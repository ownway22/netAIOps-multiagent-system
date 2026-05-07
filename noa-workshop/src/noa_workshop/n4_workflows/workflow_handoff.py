"""重寫為 DevUI 可視覺化 graph 的 handoff workflow。

最早是用 ``HandoffBuilder`` 寫的（詳見 ``orchestration_handoff``），
這裡改用 ``WorkflowBuilder`` + 明式 ``add_edge`` 重寫，讓整個 topology 能
在 ``agent_framework.devui`` 中以靜態 graph 的方式呈現（與
``sample-code/agent-framework-devui/workflow.py`` 同一個套路）。

協作主軸跟 HandoffBuilder 版本完全一樣：

    NOC Manager 先做一次事件分流 → 0~3 位專家
    (telemetry / security / field_ops) 條件式參與 → finalize 收斂為摘要

關鍵差異 (vs. ``HandoffBuilder`` 版)：
- 路由由 NOC Manager 一次決定 (透過 Pydantic ``response_format=RoutingPlan``)，
  不再依賴執行時的多輪 handoff，因此 graph 可以被靜態繪製。
- 每位專家有對應的 ``submit_<role>`` / ``record_<role>`` / ``skip_<role>``
  輔助 executor，組合成 fan-in/fan-out 的條件邊。
- field_ops 的 ``create_dispatch_request`` 仍維持
  ``approval_mode='always_require'``，所以 DevUI / CLI 仍會在派工前發出
  ``function_approval_request`` HITL 事件。

Run::

    # CLI 端到端執行
    uv run python -m noa_workshop.n4_workflows.workflow_handoff

    # DevUI 圖形化呈現
    uv run python -m noa_workshop.n5_devui.devui_server
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Literal, cast

from agent_framework import (
    Agent,
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    Content,
    Message,
    Workflow,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing_extensions import Never

from noa_workshop.n1_agents import make_agent, shared_chat_client
from noa_workshop.n1_agents.agent_factory import _read_instructions

SCENARIO_A_PROMPT = (
    "緊急通報：台灣北部區域在 09:25 後出現 P1 link_down 告警，RTR-N1↔RTR-N2 鏈路中斷，用戶大量回報延遲。請協調團隊處理，若需派工請走完正式流程。"
)


SpecialistRole = Literal["telemetry", "security", "field_ops"]


class RoutingPlan(BaseModel):
    """NOC Manager 對單一事件的分流決定。"""

    specialists: list[SpecialistRole] = Field(
        ...,
        description="本次需要參與的專家子集，至少一位",
    )
    rationale: str = Field(..., description="挑選這些專家的理由")
    summary_for_handoff: str = Field(
        ..., description="給專家看的交辦說明 (繁體中文)"
    )


# --------------------------------------------------------------------------- #
# NOC Manager (with structured output for routing)
# --------------------------------------------------------------------------- #


def _build_manager() -> Agent:
    """NOC Manager 改造版：強制以 ``RoutingPlan`` JSON 回覆。"""
    base_instructions = _read_instructions("noc_manager.md")
    routing_addendum = (
        "\n\n=== M3 Workflow 額外規則 ===\n"
        "你正在執行事件分流 (incident triage)。當你收到事件描述後，請挑選下列專家中"
        "需要參與的子集 (至少一位)：\n"
        " - telemetry：需要進一步確認 KPI / 告警 / 拓樸事實時加入。\n"
        " - security：可能涉及 IOC、安全簽章、合規風險時加入。\n"
        " - field_ops：需要派工 / 檢查現場硬體 / 協調備品時加入。\n"
        "請只輸出 JSON，欄位包含：specialists (string list)、rationale、"
        "summary_for_handoff (繁體中文交辦說明)。"
    )
    return Agent(
        client=shared_chat_client(),
        name="NOCManager",
        instructions=base_instructions + routing_addendum,
        # ChatOptions 是 TypedDict；Foundry chat client 雖然沒把 response_format
        # 列為正規 kwarg，但透過 default_options 傳进去仍然有效。
        default_options={"response_format": RoutingPlan},
        require_per_service_call_history_persistence=True,
    )


# --------------------------------------------------------------------------- #
# Workflow executors
# --------------------------------------------------------------------------- #


@executor(id="start_dispatch")
async def start_dispatch(
    prompt: str, ctx: WorkflowContext[AgentExecutorRequest]
) -> None:
    """Workflow 入口：把 prompt 記錄到 state，轉手給 NOC Manager。"""
    ctx.set_state("incident_prompt", prompt)
    ctx.set_state("findings", {})
    await ctx.send_message(
        AgentExecutorRequest(
            messages=[Message("user", [prompt])],
            should_respond=True,
        )
    )


@executor(id="parse_plan")
async def parse_plan(
    response: AgentExecutorResponse, ctx: WorkflowContext[RoutingPlan]
) -> None:
    """把 manager 的結構化回覆轉成 ``RoutingPlan``。"""
    plan = cast("RoutingPlan | None", response.agent_response.value)
    if plan is None:
        # 防護措施：模型不小心沒輸出合法 JSON 時，預設先讓 telemetry 接手。
        plan = RoutingPlan(
            specialists=["telemetry"],
            rationale="manager 未回傳結構化計畫，預設先請 telemetry 做事實確認。",
            summary_for_handoff=response.agent_response.text or "",
        )
    ctx.set_state("plan", plan.model_dump())
    ctx.set_state("manager_text", response.agent_response.text or "")
    await ctx.send_message(plan)


def _make_submit(role: SpecialistRole, executor_id: str):
    """產生一個 ``submit_<role>`` executor，負責將事件交給指定專家。"""

    @executor(id=executor_id)
    async def _submit(
        plan: RoutingPlan, ctx: WorkflowContext[AgentExecutorRequest]
    ) -> None:
        prompt = ctx.get_state("incident_prompt") or ""
        message_text = (
            f"NOC Manager 已將案件交給 {role}。\n\n"
            f"【原始通報】\n{prompt}\n\n"
            f"【主管交辦】\n{plan.summary_for_handoff}\n\n"
            f"【挑選原因】\n{plan.rationale}\n\n"
            "請依你的職責給出分析；如需呼叫工具取得最新事實請直接使用。"
        )
        await ctx.send_message(
            AgentExecutorRequest(
                messages=[Message("user", [message_text])],
                should_respond=True,
            )
        )

    return _submit


def _make_record(role: SpecialistRole, executor_id: str):
    """產生一個 ``record_<role>`` executor，把專家的回覆存進 state。"""

    @executor(id=executor_id)
    async def _record(
        response: AgentExecutorResponse,
        ctx: WorkflowContext[RoutingPlan],
    ) -> None:
        findings: dict[str, str] = ctx.get_state("findings") or {}
        findings[role] = response.agent_response.text or ""
        ctx.set_state("findings", findings)
        plan_dict = ctx.get_state("plan") or {}
        await ctx.send_message(RoutingPlan(**plan_dict))

    return _record


def _make_skip(role: SpecialistRole, executor_id: str):
    """產生一個 ``skip_<role>`` 直通 executor（該角色本輪不需參與時用）。"""
    del role  # 只是為了讓呼叫者讀到名字時看出是哪個角色、內部不使用

    @executor(id=executor_id)
    async def _skip(
        plan: RoutingPlan, ctx: WorkflowContext[RoutingPlan]
    ) -> None:
        await ctx.send_message(plan)

    return _skip


submit_telemetry = _make_submit("telemetry", "submit_telemetry")
record_telemetry = _make_record("telemetry", "record_telemetry")
skip_telemetry = _make_skip("telemetry", "skip_telemetry")

submit_security = _make_submit("security", "submit_security")
record_security = _make_record("security", "record_security")
skip_security = _make_skip("security", "skip_security")

submit_field_ops = _make_submit("field_ops", "submit_field_ops")
record_field_ops = _make_record("field_ops", "record_field_ops")
skip_field_ops = _make_skip("field_ops", "skip_field_ops")


@executor(id="finalize")
async def finalize(plan: RoutingPlan, ctx: WorkflowContext[Never, str]) -> None:
    """拼出 NOC 結案摘要，作為整個 workflow 的最終輸出。"""
    findings: dict[str, str] = ctx.get_state("findings") or {}
    incident: str = ctx.get_state("incident_prompt") or ""
    manager_text: str = ctx.get_state("manager_text") or ""

    parts: list[str] = [
        "=== NOA M3 Workflow 結案摘要 ===",
        f"原始通報：{incident}",
        "",
        f"NOC Manager 路由計畫：{plan.specialists}",
        f"主管說明：{manager_text}",
        "",
    ]
    for role in ("telemetry", "security", "field_ops"):
        if role in findings:
            parts.append(f"--- {role} ---")
            parts.append(findings[role])
            parts.append("")
        else:
            parts.append(f"--- {role} (本次未啟用) ---")
            parts.append("")
    await ctx.yield_output("\n".join(parts))


# --------------------------------------------------------------------------- #
# Workflow builder
# --------------------------------------------------------------------------- #


def _wants(role: SpecialistRole):
    def _cond(plan: RoutingPlan) -> bool:
        return role in plan.specialists

    return _cond


def _skips(role: SpecialistRole):
    def _cond(plan: RoutingPlan) -> bool:
        return role not in plan.specialists

    return _cond


def get_workflow() -> Workflow:
    """拼出可在 DevUI 視覺化的 M3 workflow graph。

    拓樸（由左至右）::

        start_dispatch
            → noc_manager (AgentExecutor, response_format=RoutingPlan)
            → parse_plan
            → [stage 1：telemetry]
                ├── submit_telemetry → telemetry_agent → record_telemetry
                └── skip_telemetry
            → [stage 2：security]
                ├── submit_security  → security_agent  → record_security
                └── skip_security
            → [stage 3：field_ops]
                ├── submit_field_ops → field_ops_agent → record_field_ops
                └── skip_field_ops
            → finalize → yield_output
    """
    if os.getenv("NOA_USE_HOSTED_AGENTS", "false").strip().lower() == "true":
        # 這個帶「結構化輸出」的 manager 是寫在程式裡，不是 Foundry portal
        # 上的 prompt agent，所以這個 graph 只能在 local 模式跱。Hosted 模式請
        # 繼續使用 M5 裡的 SequentialBuilder（deployment/host_server.py）。
        raise RuntimeError(
            "M3 graph workflow requires NOA_USE_HOSTED_AGENTS=false "
            "(local mode)."
        )

    manager = AgentExecutor(_build_manager(), id="noc_manager")
    telemetry = AgentExecutor(
        make_agent("telemetry_analyzer"), id="telemetry_agent"
    )
    security = AgentExecutor(
        make_agent("security_compliance"), id="security_agent"
    )
    field_ops = AgentExecutor(make_agent("field_ops"), id="field_ops_agent")

    builder = (
        WorkflowBuilder(
            name="Workflow_Handoff",
            description=(
                "NOC Manager 一次性路由 → telemetry / security / field_ops "
                "條件式參與 → finalize 收斂"
            ),
            start_executor=start_dispatch,
        )
        .add_edge(start_dispatch, manager)
        .add_edge(manager, parse_plan)
        # Stage 1：telemetry
        .add_edge(parse_plan, submit_telemetry, condition=_wants("telemetry"))
        .add_edge(parse_plan, skip_telemetry, condition=_skips("telemetry"))
        .add_edge(submit_telemetry, telemetry)
        .add_edge(telemetry, record_telemetry)
        # Stage 2：security
        .add_edge(record_telemetry, submit_security, condition=_wants("security"))
        .add_edge(record_telemetry, skip_security, condition=_skips("security"))
        .add_edge(skip_telemetry, submit_security, condition=_wants("security"))
        .add_edge(skip_telemetry, skip_security, condition=_skips("security"))
        .add_edge(submit_security, security)
        .add_edge(security, record_security)
        # Stage 3：field_ops
        .add_edge(record_security, submit_field_ops, condition=_wants("field_ops"))
        .add_edge(record_security, skip_field_ops, condition=_skips("field_ops"))
        .add_edge(skip_security, submit_field_ops, condition=_wants("field_ops"))
        .add_edge(skip_security, skip_field_ops, condition=_skips("field_ops"))
        .add_edge(submit_field_ops, field_ops)
        .add_edge(field_ops, record_field_ops)
        # 收斂
        .add_edge(record_field_ops, finalize)
        .add_edge(skip_field_ops, finalize)
    )
    return builder.build()


# --------------------------------------------------------------------------- #
# CLI runner—不走 DevUI 也能端到端跱完 M3
# --------------------------------------------------------------------------- #


def _print_run(result: Any) -> None:
    """以人類友善的方式印出一次非 streaming workflow run 的事件。"""
    for event in result:
        executor_id = getattr(event, "executor_id", "") or ""
        if event.type == "data":
            text = getattr(event.data, "text", str(event.data))
            print(f"\n[{executor_id}] {text}")
        elif event.type == "output":
            print(f"\n=== Output from {executor_id} ===")
            print(event.data)


async def _resolve_request(req_event: Any) -> Any:
    """處理 HITL ``function_approval_request`` 事件（CLI 上詢問使用者是否同意）。"""
    data = req_event.data
    if isinstance(data, Content) and data.type == "function_approval_request":
        func_call = data.function_call
        args = func_call.parse_arguments() or {}
        print("\n=========================================")
        print("[HITL] Tool approval requested")
        print(f"    function: {func_call.name}")
        print(f"    args    : {args}")
        print("=========================================")
        if os.getenv("NOA_AUTO_APPROVE", "true").strip().lower() == "true":
            approved = True
            print("[HITL] AUTO-APPROVED (NOA_AUTO_APPROVE=true)")
        else:
            answer = await asyncio.to_thread(input, "Approve dispatch? (y/n): ")
            approved = answer.strip().lower() == "y"
        return data.to_function_approval_response(approved=approved)

    raise RuntimeError(f"Unhandled request_info event: {req_event!r}")


async def main() -> None:
    load_dotenv()

    workflow = get_workflow()

    print("\n=== Handoff Workflow (graph) ===")
    print(f"[User] {SCENARIO_A_PROMPT}\n")

    result = await workflow.run(SCENARIO_A_PROMPT)
    _print_run(result)
    pending = result.get_request_info_events()

    rounds = 0
    while pending and rounds < 8:
        rounds += 1
        responses: dict[str, Any] = {}
        for req in pending:
            responses[req.request_id] = await _resolve_request(req)
        result = await workflow.run(responses=responses)
        _print_run(result)
        pending = result.get_request_info_events()


if __name__ == "__main__":
    asyncio.run(main())
