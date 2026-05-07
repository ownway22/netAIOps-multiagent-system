"""4 個 single agent 的工廠函式（供 DevUI 與練習使用）。

用途
----
DevUI 的 *Agent 類別* 會列出所有透過 ``agent_framework.devui.serve`` 註冊的
``AgentProtocol`` 實體。本檔把 NOA 的四位專家 agent 各自包成一個
``get_<role>()`` 工廠函式，方便：

1. ``n5_devui.devui_server`` 一次匯入並呈現給學員。
2. 學員直接 import 單一 agent 做 hello-world 互動。

關鍵設計
--------
- 全部走 ``agent_factory.make_agent()``，所以會自動套用：
  * ``.env`` 中的 ``FOUNDRY_PROJECT_ENDPOINT`` / ``AZURE_AI_MODEL_DEPLOYMENT_NAME``
  * 雙模式（``NOA_USE_HOSTED_AGENTS=true`` 走 portal Prompt Agent；否則走本地）
  * 各角色綁定的 Python ``@tool`` 函式
- FieldOps 的 ``create_dispatch_request`` 在 DevUI agent-mode chat 中無法
  序列化 ``function_approval_request``，因此本檔在 FieldOps 上覆寫成
  ``FIELD_OPS_TOOLS_AUTO_APPROVE``（自動核准版）。完整 HITL 體驗請走
  ``n4_workflows.workflow_handoff``（workflow-mode）。

如何驗證
--------
``uv run python -m noa_workshop.n5_devui.devui_server`` 能看到這 4 個 agent。
"""

from __future__ import annotations

from typing import Any

from noa_workshop.n1_agents.agent_factory import make_agent
from noa_workshop.n2_tools import FIELD_OPS_TOOLS_AUTO_APPROVE


def get_noc_manager() -> Any:
    """NOC Manager (Niobe) — 純協調者，無工具。"""
    return make_agent("noc_manager")


def get_telemetry_analyzer() -> Any:
    """Telemetry Analyzer — KPI / 告警 / 拓樸 / 歷史工單查詢。"""
    return make_agent("telemetry_analyzer")


def get_security_compliance() -> Any:
    """Security & Compliance — IOC、安全策略、SLA 與合規檢查。"""
    return make_agent("security_compliance")


def get_field_ops() -> Any:
    """Field Ops (Miles Dyson) — 派工 / 庫存 / 客戶通知。

    DevUI agent-mode 用自動核准版以避免序列化錯誤。
    """
    return make_agent(
        "field_ops",
        tools_override=FIELD_OPS_TOOLS_AUTO_APPROVE,
    )


def get_all_single_agents() -> list[Any]:
    """一次拿齊 4 個 single agent（給 DevUI launcher 用）。"""
    return [
        get_noc_manager(),
        get_telemetry_analyzer(),
        get_security_compliance(),
        get_field_ops(),
    ]
