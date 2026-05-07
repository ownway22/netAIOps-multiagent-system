"""M3 Handoff—把動態 handoff 多-agent 團隊包裝為 Foundry hosted agent。

這個模組將 M3 Handoff workflow（NOC Manager 透過 ``HandoffBuilder`` 動態分派
給 telemetry / security / field_ops）包起來為一個 ``ResponsesHostServer``，
這樣就能以單一 hosted agent 的身份部署到 Microsoft Foundry，對外暴露
 OpenAI 相容的 Responses 協議。

本地驗證::

    uv run python -m noa_workshop.n6_deployment.hosted_agent
    # 另一個終端機：
    curl -s -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"input": "north-transport-ring 09:25 P1 link_down 怎麼辦？", "stream": false}' \\
        | python3 -m json.tool

部署註記
--------

* 容器一定要監聽 ``8088``股（Foundry hosted-agent 規範）。
* Foundry runtime 會自動注入 ``FOUNDRY_PROJECT_ENDPOINT`` 與
  ``AZURE_AI_MODEL_DEPLOYMENT_NAME``，我們在 ``noa_workshop.n1_agents.agent_factory``
  裡讀儲。
* ``ResponsesHostServer`` 同時接受一般 agent 與 ``WorkflowAgent``；
  ``Workflow.as_agent(name=...)`` 會回一個 ``WorkflowAgent``，這樣 Handoff team
  以單一 agent 身份對外提供服務。
* FieldOps 改用 ``FIELD_OPS_TOOLS_AUTO_APPROVE``，因為 hosted Responses API
  在這裡沒有人可以處理 ``function_approval_request``。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from agent_framework import Agent
from agent_framework.orchestrations import HandoffBuilder
from agent_framework_foundry_hosting import ResponsesHostServer
from agent_framework_foundry_hosting import _responses as _afh_responses
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from noa_workshop.n1_agents import make_agent
from noa_workshop.n1_agents.orchestration_handoff import (
    AGENT_DESCRIPTION,
    _terminate_when_manager_summarises,
)
from noa_workshop.n2_tools import FIELD_OPS_TOOLS_AUTO_APPROVE


# ---------------------------------------------------------------------------
# Foundry hosting 跟 HandoffBuilder 的相容性 patch
# ---------------------------------------------------------------------------
# ``agent_framework_foundry_hosting._responses._arguments_to_str`` 宣告輸入是
# ``str | Mapping | None``並直接丟給 ``json.dumps``。當內部的 workflow 是
# HandoffBuilder 時，系統生成的 ``handoff`` 工具會被帶一個
# ``HandoffAgentUserRequest``（Pydantic-style）物件作為參數送進去，
# ``json.dumps`` 就會舍並丟：
#
#   TypeError: Object of type HandoffAgentUserRequest is not JSON serializable
#
# 造成 Responses 資料流在 ``response.created`` 之後中斷，對呼叫者顯示為 500
# ``server_error``。這裡補上一個減火 patch：遇到非 mapping 物件時走
# ``model_dump()`` / ``__dict__`` 備援，讓 handoff 事件能完整來回。該 patch 只
# 局限於本模組；str / Mapping / None 輸入仍與原函式一致。
def _patch_arguments_to_str() -> None:
    def _arguments_to_str(arguments: Any) -> str:
        if arguments is None:
            return ""
        if isinstance(arguments, str):
            return arguments
        # 先試 pydantic-style，因為有些 agent_framework model class
        # （例如 HandoffAgentUserRequest）也被註為 Mapping，但 ``json.dumps`` 不能直接丟。
        if hasattr(arguments, "model_dump"):
            return json.dumps(arguments.model_dump(), default=str)
        if isinstance(arguments, Mapping):
            return json.dumps(arguments, default=str)
        if hasattr(arguments, "__dict__"):
            return json.dumps(vars(arguments), default=str)
        return json.dumps(arguments, default=str)

    _afh_responses._arguments_to_str = _arguments_to_str


_patch_arguments_to_str()


# 本地開發便利：若 repo 裡有 .env 就載進來。部署到 Foundry 容器裡時這個檔案
# 不存在，Foundry 會自己注入環境變數，所以這裡自動成為 no-op。
def _maybe_load_dotenv() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        return
    repo_root = Path(__file__).resolve().parents[3]
    env_path = repo_root / ".env"
    if env_path.is_file():
        load_dotenv(env_path)


_maybe_load_dotenv()


# Foundry 上的 hosted agent 名稱（要跟部署腳本裡的 HOSTED_AGENT_NAME
# 跟 agent.manifest.yaml 裡的 ``name:`` 保持一致）。
HOSTED_AGENT_NAME = "noa-multiagent-hosted"


def _disable_service_history(agent: Agent) -> Agent:
    """強制設 ``store=False``，避免 FoundryChatClient 重複記錄對話歷史。

    Handoff 迴圈每一輪都會裝豐富的 `Message` 歷史並重播給 manager 與專家。
    同時上並保留 ``store=True``（Foundry 預設）時，Responses 後端也會把這些
    實例記錄下來，下一輪就會跟本地重播的歷史撞車，Foundry 會回
    ``Duplicate item found with id fc_...``。hosted-agent 的官方建議就是關掉
    伺服器端儲存，讓 framework 自己採儲存歷史。
    """

    if agent.default_options is None:
        agent.default_options = {"store": False}
    else:
        agent.default_options["store"] = False
    return agent


def build_workflow():
    """拼出與 ``orchestration_handoff.get_agent`` 一模一樣的 Handoff team。

    Hosted-mode 重點：
      - 本地 ``@tool`` Python 函式仍會在容器裡跱，所以專家仍保有 telemetry /
        security / field-ops 各自的工具集。
      - 所有帶 chat client 的 Agent 都被強制 ``store=False``，因為 Foundry hosting
        runtime 才是對話歷史的拥有者（詳見
        https://learn.microsoft.com/agent-framework/hosting/foundry-hosted-agent）。
      - FieldOps 改用 ``FIELD_OPS_TOOLS_AUTO_APPROVE``，所以 hosted Responses API
        不會被 ``function_approval_request`` 卡住（那個事件需要人類處理）。
    """

    noc_manager = _disable_service_history(make_agent("noc_manager"))
    telemetry = _disable_service_history(make_agent("telemetry_analyzer"))
    security = _disable_service_history(make_agent("security_compliance"))
    field_ops = _disable_service_history(
        make_agent("field_ops", tools_override=FIELD_OPS_TOOLS_AUTO_APPROVE)
    )

    return (
        HandoffBuilder(
            name=HOSTED_AGENT_NAME,
            description=AGENT_DESCRIPTION,
            participants=[noc_manager, telemetry, security, field_ops],
            termination_condition=_terminate_when_manager_summarises,
        )
        .with_start_agent(noc_manager)
        .add_handoff(noc_manager, [telemetry, security, field_ops])
        .add_handoff(telemetry, [noc_manager])
        .add_handoff(security, [noc_manager, field_ops])
        .add_handoff(field_ops, [noc_manager])
        .build()
    )


def _wrap_clear_stale_pending_requests(agent: Any) -> None:
    """新一輪使用者對話出現時，清除残留的 ``_pending_requests``。

    ``WorkflowAgent`` 會在實例上記 ``_pending_requests``，以支援內容為
    ``function_approval_response`` / ``function_result`` 的 HITL 輪次。但
    HandoffBuilder、我們的終止條件、field-ops 派工流都可能在 workflow 完成時
    （例如主管已出結案摘要、但還有 ``request_info`` 邁邁未送交）讓這個 dict
    轉為非空狀態。

    下一次使用者在 portal 裡送一句純文字時，
    ``_extract_function_responses`` 就會丟
    ``AgentInvalidResponseException("Unexpected content type while awaiting
    request info responses.")``，gateway 就會回「An internal server error
    occurred.」這種泛用錯誤訊息。

    這裡對 ``_run_core`` 裝一層裝飾、當這一輪輸入沒有 function-response
    內容時就清掃舊條目—那是「這是一個全新使用者輪」的明確訊號。
    """

    original_run_core = agent._run_core  # bound method

    async def _run_core_with_reset(
        input_messages,
        checkpoint_id,
        checkpoint_storage,
        streaming,
        function_invocation_kwargs=None,
        client_kwargs=None,
    ):
        if agent._pending_requests:
            has_function_response = any(
                getattr(c, "type", None)
                in ("function_approval_response", "function_result")
                for m in input_messages
                for c in getattr(m, "contents", [])
            )
            if not has_function_response:
                agent._pending_requests.clear()

        async for event in original_run_core(
            input_messages,
            checkpoint_id,
            checkpoint_storage,
            streaming,
            function_invocation_kwargs=function_invocation_kwargs,
            client_kwargs=client_kwargs,
        ):
            yield event

    agent._run_core = _run_core_with_reset


def make_server() -> ResponsesHostServer:
    """把 Handoff workflow 包裝為 Foundry hosted Responses server。"""

    workflow = build_workflow()
    workflow_agent = workflow.as_agent(name=HOSTED_AGENT_NAME)
    _wrap_clear_stale_pending_requests(workflow_agent)
    server = ResponsesHostServer(workflow_agent)

    # Foundry hosted-agent 平台同時探測 ``GET /readiness`` 與 ``GET /liveness``。
    # ``azure-ai-agentserver-core`` 只註冊 ``/readiness``（在 2.0.0b3 驗證），
    # 所以 liveness 探測會 404，平台就會把容器標記為 Unhealthy → ActivationFailed。
    # 這裡手動在底層的 Starlette router 上增一個 200-OK 的 ``/liveness`` 路由，
    # 讓探測能成功。
    async def _liveness(_request: Request) -> PlainTextResponse:
        return PlainTextResponse("OK")

    server.router.routes.append(  # type: ignore[attr-defined]
        Route("/liveness", _liveness, methods=["GET"], name="liveness"),
    )
    return server


if __name__ == "__main__":
    # 跟 sample-code/ipm_multiagent/main.py 保持一致：讓 ResponsesHostServer 自己
    # 選 host / port 預設值，這樣才能跟 Foundry hosted-agent 規範走。
    make_server().run()
