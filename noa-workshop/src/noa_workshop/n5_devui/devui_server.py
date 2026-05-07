"""本地 DevUI 啟動器：一次載入本 workshop 的 9 個 entity。

跳起 ``agent_framework.devui`` 除錯 UI，並同時註冊 9 個 entity，讓學員
能並排比較所有層次的 orchestration：

Agent 類別（可直接對話）：
- ``n1_agents.single_agents`` 下的 4 個單一 agent：
  ``NOCManager``、``TelemetryAnalyzer``、``SecurityCompliance``、``FieldOps``。
- ``n1_agents`` 下的 3 個多-agent orchestration：
  ``Orchestration_Sequential``（SequentialBuilder）、
  ``Orchestration_Handoff``（HandoffBuilder）、
  ``Orchestration_Magentic``（MagenticBuilder）。

Workflow 類別（圖示檢視）：
- ``Workflow_Sequential``：用 ``WorkflowBuilder`` 拼出的 Telemetry → Security →
  FieldOps 線性 pipeline，附帶一條安全事件 escalation 分枝。
- ``Workflow_Handoff``：NOC Manager 以結構化輸出路由到
  telemetry / security / field_ops，並保留派工的 HITL 審核。

如何跱起來::

    uv run python -m noa_workshop.n5_devui.devui_server

跳起來後請開啟 http://localhost:8080（請使用 ``localhost``——內建前端是
寫死這個 origin 的，改用 127.0.0.1 會遇到 CORS 問題）。

先決條件：
- ``.env`` 裡要有 ``FOUNDRY_PROJECT_ENDPOINT`` 與 ``AZURE_AI_MODEL_DEPLOYMENT_NAME``。
- 已執行過 ``az login``（DefaultAzureCredential / AzureCliCredential）。
- ``NOA_USE_HOSTED_AGENTS`` 保持為 ``false``（``Workflow_Handoff`` 裡的
  結構化輸出 NOC Manager 只能跱在 local 模式）。
"""

from __future__ import annotations

import os

from agent_framework.devui import serve
from dotenv import load_dotenv

from noa_workshop.n1_agents.orchestration_handoff import (
    get_agent as get_multi_handoff_agent,
)
from noa_workshop.n1_agents.orchestration_magentic import (
    get_agent as get_multi_magentic_agent,
)
from noa_workshop.n1_agents.orchestration_sequential import (
    get_agent as get_multi_sequential_agent,
)
from noa_workshop.n1_agents.single_agents import get_all_single_agents
from noa_workshop.n4_workflows.workflow_handoff import (
    get_workflow as get_handoff_workflow,
)
from noa_workshop.n4_workflows.workflow_sequential import (
    get_workflow as get_sequential_workflow,
)


def main() -> None:
    load_dotenv()

    entities = [
        # 單一 agent（對話檢視）。
        *get_all_single_agents(),
        # 多-agent orchestration（對話檢視）。
        get_multi_sequential_agent(),
        get_multi_handoff_agent(),
        get_multi_magentic_agent(),
        # Workflow 實體（圖示檢視）。
        get_sequential_workflow(),
        get_handoff_workflow(),
    ]

    host = os.getenv("NOA_DEVUI_HOST", "localhost")
    port = int(os.getenv("NOA_DEVUI_PORT", "8080"))

    serve(
        entities=entities,
        host=host,
        port=port,
        auto_open=False,
    )


if __name__ == "__main__":
    main()
