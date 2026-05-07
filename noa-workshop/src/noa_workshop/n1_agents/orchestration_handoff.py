"""用 ``HandoffBuilder`` 做的 handoff multi-agent orchestration。

用途
----
與 ``n4_workflows.workflow_handoff`` 同一個教學情境（NOC Manager 動態路由給
三位專家），但這裡用高階的 ``HandoffBuilder`` 拼裝，不手寫 graph
也不寫 structured-output 的路由 schema。

關鍵設計
--------
- HandoffBuilder 會自動註入一個虛擬的 ``handoff`` 工具到每个 participant，
  讓 LLM 自己決定下一位要跟誰請教。
- ``_terminate_when_manager_summarises`` 是一個教學用的防護條件：
  避免 HandoffBuilder 在 demo 裡無限迴圈，當 NOC Manager 說出結案關鍵詞就結束。
- ``FIELD_OPS_TOOLS_AUTO_APPROVE``：DevUI agent-mode chat 無法序列化
  ``function_approval_request``，這裡換上自動核准版。

如何驗證
--------
- DevUI：``Orchestration_Handoff`` 出現在 entity 清單，送一句話會看到
  NOC Manager 起頭、依需求 dispatch 給專家。
- CLI::

      uv run python -m noa_workshop.n1_agents.orchestration_handoff
"""

from __future__ import annotations

import asyncio

from agent_framework import WorkflowAgent
from agent_framework.orchestrations import HandoffBuilder
from dotenv import load_dotenv

from noa_workshop.n1_agents import make_agent
from noa_workshop.n2_tools import FIELD_OPS_TOOLS_AUTO_APPROVE

# 與 WorkflowBuilder 版本同一個 prompt，方便對比 graph vs. orchestration 兩種寫法。
SCENARIO_A_PROMPT = (
    "緊急通報：台灣北部區域在 09:25 後出現 P1 link_down 告警，RTR-N1↔RTR-N2 鏈路中斷，用戶大量回報延遲。請協調團隊處理，若需派工請走完正式流程。"
)


AGENT_NAME = "Orchestration_Handoff"
AGENT_DESCRIPTION = (
    "NOA Handoff orchestration：NOC Manager 透過 HandoffBuilder 動態分派任務給 "
    "telemetry / security / field_ops。"
)


def _terminate_when_manager_summarises(messages: list) -> bool:
    """當 NOC Manager 說出「結案」關鍵詞就終止 handoff 迴圈。

    HandoffBuilder 預設會一直在 manager 與 specialist 之間循環，直到 LLM 呼叫
    隱含的 ``end`` 工具為止。在 workshop demo 裡這個迴圈可能跳不出來，
    所以這裡加一個防護條件：只要 manager 最近一輪出現「事件處理完畢」、
    「事件已結案」、「結案摘要」或 ``incident closed``，就當作處理完成。
    """

    closing_markers = (
        "事件處理完畢",
        "事件已結案",
        "結案摘要",
        "incident closed",
    )
    for message in reversed(messages):
        if getattr(message, "role", None) != "assistant":
            continue
        author = getattr(message, "author_name", None)
        if author and author != "NOCManager":
            continue
        text = (getattr(message, "text", "") or "").lower()
        return any(marker.lower() in text for marker in closing_markers)
    return False


def get_agent() -> WorkflowAgent:
    """拼出這個 handoff orchestration，並包成 chat-ready agent。

    拓樸（NOC Manager + 3 位專家，完整 handoff 迴圈）：

    - NOC Manager 是起點 agent，可以 handoff 給任何專家。
    - Telemetry 查完事實後只能回給 manager。
    - Security 可以回 manager、也可以直接交給 field_ops（比如確認非安全事件但需要派工）。
    - Field Ops 草完派工後回給 manager。
    """

    load_dotenv()

    # NOC Manager 不需要工具，它只負責協調，預設註冊表的 tools=[] 就是我們要的。
    noc_manager = make_agent("noc_manager")
    telemetry = make_agent("telemetry_analyzer")
    security = make_agent("security_compliance")
    # DevUI agent-mode chat 無法序列化 ``function_approval_request`` 內容，
    # 這裡把 FieldOps 的 HITL 派工工具換成自動核准版。
    # 完整 HITL 教學仍保留在 ``Workflow_Handoff``（DevUI workflow-mode）。
    field_ops = make_agent(
        "field_ops", tools_override=FIELD_OPS_TOOLS_AUTO_APPROVE
    )

    workflow = (
        HandoffBuilder(
            name=AGENT_NAME,
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

    return workflow.as_agent(
        name=AGENT_NAME,
        description=AGENT_DESCRIPTION,
    )


async def _main() -> None:
    """從 CLI 全程跑一次這個 handoff orchestration。"""

    agent = get_agent()

    print(f"\n=== {AGENT_NAME} (HandoffBuilder edition) ===")
    print(f"[User] {SCENARIO_A_PROMPT}\n")

    response = await agent.run(SCENARIO_A_PROMPT)
    print(response.text)


if __name__ == "__main__":
    asyncio.run(_main())
