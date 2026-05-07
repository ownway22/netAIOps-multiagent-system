"""用明式 graph edge 重寫的 sequential workflow。

為什麼要寫這個版本？
- 上一個 ``orchestration_sequential``（用 ``SequentialBuilder``）教的是同一件事：
  TelemetryAnalyzer → SecurityCompliance → FieldOps。
- 這裡改用 ``WorkflowBuilder.add_edge`` 明式蒙出所有 edge，這樣才能
  **在 DevUI 裡看到視覺化 graph**（Microsoft Agent Framework Developer UI）。
- 我們另外加了 **一條條件分枝**，讓 graph 看起來不兩段子就走完：
  當 SecurityCompliance agent 回報 ``是否為安全事件：是`` 時，就不走 FieldOps，
  而是走到 escalation 終點。

CLI 跳起來跑一輪::

    uv run python -m noa_workshop.n4_workflows.workflow_sequential

在 DevUI 裡打開（CLI 會自動搜尋 ``noa-workshop/devui/``）::

    cd noa-workshop
    uv run devui ./devui --port 8090
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from agent_framework import (
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    Message,
    Workflow,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from dotenv import load_dotenv
from typing_extensions import Never

from noa_workshop.n1_agents import make_agent

SCENARIO_A_PROMPT = (
    "台灣北部區域出現 P1 告警 (ALM-2026050501)，用戶投訴連線品質劣化。請依序：(1) 確認 KPI 與告警事實、(2) 判斷是否為安全事件、(3) 若需派工請草擬派工建議。"
)


# ---------------------------------------------------------------------------
# Routing payload
# ---------------------------------------------------------------------------


@dataclass
class SecurityVerdict:
    """由安全判定節點傳給下游分枝的決定包。

    這裡順便把對話一起帶下去，三個分枝各自都能獨立運作：
    escalation 終點可以直接把它 yield 為最終輸出，FieldOps bridge 也
    能重新包裝成 ``AgentExecutorRequest``。
    """

    is_security_event: bool
    verdict_text: str
    conversation: list[Message]


def _looks_like_security_event(text: str) -> bool:
    """對 SecurityCompliance 回覆的自由文字做一個含糊判斷。

    它的 system prompt 有規定一定要寫 ``是否為安全事件：是 / 否 / 待確認``，
    所以這裡看到 ``：是`` 才走 escalation；``否`` / ``待確認`` / 沒講 /
    看不懂都當「不是安全事件」，繼續往 FieldOps 走。
    """

    norm = text.replace(" ", "").replace("\u3000", "")
    if "是否為安全事件：是" in norm:
        return True
    if "非安全事件" in norm:
        return False
    if "是否為安全事件：否" in norm or "是否為安全事件：待確認" in norm:
        return False
    return False


# ---------------------------------------------------------------------------
# Glue executors（讓 graph 中的各個 agent 能接上、轉換訊息的小節點）
# ---------------------------------------------------------------------------


@executor(id="prepare_input")
async def prepare_input(
    user_prompt: str, ctx: WorkflowContext[AgentExecutorRequest]
) -> None:
    """把 user prompt 包成起始對話，丟給 telemetry。"""

    initial = [Message("user", contents=[user_prompt])]
    await ctx.send_message(
        AgentExecutorRequest(messages=initial, should_respond=True)
    )


@executor(id="forward_to_security")
async def forward_to_security(
    response: AgentExecutorResponse,
    ctx: WorkflowContext[AgentExecutorRequest],
) -> None:
    """把目前完整對話（包含 telemetry 的回覆）丟給 security。"""

    await ctx.send_message(
        AgentExecutorRequest(
            messages=list(response.full_conversation),
            should_respond=True,
        )
    )


@executor(id="classify_security")
async def classify_security(
    response: AgentExecutorResponse,
    ctx: WorkflowContext[SecurityVerdict],
) -> None:
    """讀 security 的裁決文字，轉成型別明確的路由決定。"""

    verdict_text = response.agent_response.text or ""
    await ctx.send_message(
        SecurityVerdict(
            is_security_event=_looks_like_security_event(verdict_text),
            verdict_text=verdict_text,
            conversation=list(response.full_conversation),
        )
    )


@executor(id="route_to_field_ops")
async def route_to_field_ops(
    verdict: SecurityVerdict,
    ctx: WorkflowContext[AgentExecutorRequest],
) -> None:
    """把對話接手給 FieldOps，請它給出派工計畫。"""

    await ctx.send_message(
        AgentExecutorRequest(
            messages=verdict.conversation,
            should_respond=True,
        )
    )


@executor(id="security_escalation")
async def security_escalation(
    verdict: SecurityVerdict,
    ctx: WorkflowContext[Never, list[Message]],
) -> None:
    """当 security 判為真安全事件時所走到的終點。"""

    note = Message(
        "assistant",
        contents=[
            "[Workflow] Security 判定為安全事件，已停在 escalation 節點；"
            "請通知 NOC Manager 與資安主管接手 incident response，"
            "暫停 field-ops 派工。"
        ],
        author_name="WorkflowRouter",
    )
    await ctx.yield_output(verdict.conversation + [note])


@executor(id="finalize_field_ops")
async def finalize_field_ops(
    response: AgentExecutorResponse,
    ctx: WorkflowContext[Never, list[Message]],
) -> None:
    """FieldOps 給出計畫後，以完整對話紀錄作為最終輸出。"""

    await ctx.yield_output(list(response.full_conversation))


# ---------------------------------------------------------------------------
# Workflow factory
# ---------------------------------------------------------------------------


def get_workflow() -> Workflow:
    """拼出 M2 的 graph workflow。

    用 factory 函式提供是為了讓 DevUI 自動搜尋與單元測試都能拿到一個
    總讀進最新 ``.env`` 的新實例。
    """

    load_dotenv()

    telemetry_executor = AgentExecutor(
        make_agent("telemetry_analyzer"), id="telemetry_analyzer"
    )
    security_executor = AgentExecutor(
        make_agent("security_compliance"), id="security_compliance"
    )
    field_ops_executor = AgentExecutor(make_agent("field_ops"), id="field_ops")

    return (
        WorkflowBuilder(
            name="Workflow_Sequential",
            description=(
                "NOA Sequential graph：Telemetry → Security → FieldOps"
                "（線性 pipeline + 安全事件 escalation 分枝）。"
            ),
            start_executor=prepare_input,
        )
        .add_edge(prepare_input, telemetry_executor)
        .add_edge(telemetry_executor, forward_to_security)
        .add_edge(forward_to_security, security_executor)
        .add_edge(security_executor, classify_security)
        .add_edge(
            classify_security,
            route_to_field_ops,
            condition=lambda v: not v.is_security_event,
        )
        .add_edge(
            classify_security,
            security_escalation,
            condition=lambda v: v.is_security_event,
        )
        .add_edge(route_to_field_ops, field_ops_executor)
        .add_edge(field_ops_executor, finalize_field_ops)
        .build()
    )


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


async def main() -> None:
    workflow = get_workflow()

    print("\n=== Sequential Workflow (graph edition) ===")
    print(f"[User] {SCENARIO_A_PROMPT}\n")

    result = await workflow.run(SCENARIO_A_PROMPT)

    for output in result.get_outputs():
        if isinstance(output, list):
            for idx, message in enumerate(output, 1):
                role = getattr(message, "role", "?")
                author = getattr(message, "author_name", None) or "system"
                text = getattr(message, "text", str(message))
                print(f"\n--- Turn {idx} | role={role} | author={author} ---")
                print(text)
        else:
            print("\n[Final Output]")
            print(output)


if __name__ == "__main__":
    asyncio.run(main())
