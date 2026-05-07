"""用 ``SequentialBuilder`` 做的順序 multi-agent orchestration。

用途
----
與 ``n4_workflows.workflow_sequential`` 同一個教學情境（Telemetry → Security → FieldOps
的線性管線），但這裡用高階的 ``SequentialBuilder`` 一行拼裝，
而不是手寫的 ``WorkflowBuilder`` graph。最後用 ``Workflow.as_agent`` 包成
一個 chat 介面的 agent，顯示在 DevUI 的 **Agent** 類別。

關鍵設計
--------
- ``SequentialBuilder`` 來自 ``agent_framework.orchestrations``，它象黑盒一樣幫
  你接好所有 executor，是拼「固定順序」管線的推薦寫法。
- ``WorkflowBuilder`` 的版本保留在 ``workflow_sequential`` 是刷為了對比：
  顯式 graph（可視化、可分支） vs. 宣告式 orchestration（一行搮定，但只能線性）。
- ``FIELD_OPS_TOOLS_AUTO_APPROVE``：DevUI agent-mode chat 無法序列化
  ``function_approval_request``，這裡換上自動核准版。

如何驗證
--------
- DevUI：``Orchestration_Sequential`` 會出現在 entity 清單，交談查看訓令依序走 telemetry
  → security → field_ops。
- CLI::

      uv run python -m noa_workshop.n1_agents.orchestration_sequential
"""

from __future__ import annotations

import asyncio

from agent_framework import WorkflowAgent
from agent_framework.orchestrations import SequentialBuilder
from dotenv import load_dotenv

from noa_workshop.n1_agents import make_agent
from noa_workshop.n2_tools import FIELD_OPS_TOOLS_AUTO_APPROVE

# 一律用與 WorkflowBuilder 版本相同的 prompt，教學時講話的腳本能對齊。
SCENARIO_A_PROMPT = (
    "台灣北部區域出現 P1 告警 (ALM-2026050501)，用戶投訴連線品質劣化。請依序：(1) 確認 KPI 與告警事實、(2) 判斷是否為安全事件、(3) 若需派工請草擬派工建議。"
)


# DevUI 用這個名字顯示 entity。
AGENT_NAME = "Orchestration_Sequential"
AGENT_DESCRIPTION = (
    "NOA Sequential orchestration：TelemetryAnalyzer → "
    "SecurityCompliance → FieldOps（由 SequentialBuilder 拼裝）。"
)


def get_agent() -> WorkflowAgent:
    """建一條順序管線並包成 chat-ready agent。

    每次呼叫都回傳全新的 ``WorkflowAgent``；``make_agent`` 在建立時才讀 env vars，
    所以 DevUI auto-reload 能看到你中間改 ``.env`` 的結果。
    """

    load_dotenv()

    telemetry = make_agent("telemetry_analyzer")
    security = make_agent("security_compliance")
    # DevUI agent-mode chat 無法序列化 ``function_approval_request`` 內容
    # （按 Approve 後會冒 "Object of type Content is not JSON serializable" 與
    # "Unexpected content type while awaiting request info responses"），
    # 所以這裡把 FieldOps 的 HITL 派工工具換成自動核准版。
    # 完整的 HITL 教學仍保留在 ``Workflow_Handoff``（DevUI workflow-mode）。
    field_ops = make_agent(
        "field_ops", tools_override=FIELD_OPS_TOOLS_AUTO_APPROVE
    )

    # SequentialBuilder 幫你接好：_InputToConversation → telemetry → security → field_ops，
    # 並設 field_ops 為 output executor，最後的 message list 就是 workflow output。
    workflow = SequentialBuilder(
        participants=[telemetry, security, field_ops],
    ).build()

    # ``as_agent`` 會讓 workflow 變成 ``WorkflowAgent``（實作 SupportsAgentRun）。
    # DevUI 以是否有 ``executors`` / ``get_executors_list`` 判斷是 Agent 還是 Workflow；
    # 這個包裝讓它落在 Agent 類別。
    return workflow.as_agent(
        name=AGENT_NAME,
        description=AGENT_DESCRIPTION,
    )


async def _main() -> None:
    """從 CLI 全程跑一次這個 orchestration。"""

    agent = get_agent()

    print(f"\n=== {AGENT_NAME} (SequentialBuilder edition) ===")
    print(f"[User] {SCENARIO_A_PROMPT}\n")

    response = await agent.run(SCENARIO_A_PROMPT)
    print(response.text)


if __name__ == "__main__":
    asyncio.run(_main())
