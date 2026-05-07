"""雙模式 agent factory：本地模式與 Foundry hosted 模式共用一個入口。

用途
----
讓 workshop 的所有地方都用 ``make_agent(role)`` 拿 agent，
不用關心現在是本地還是 hosted。

關鍵設計
--------
- ``NOA_USE_HOSTED_AGENTS=false``（預設）：用 ``FoundryChatClient`` + ``Agent``，
  從 ``instructions/<role>.md`` 讀 system prompt，在 Python 端插入 ``@tool``。
- ``NOA_USE_HOSTED_AGENTS=true``：用 ``FoundryAgent`` 接 portal 上已建好的 prompt agent，
  instructions 與 tools 都由 portal 端負責。

兩種模式皆回傳符合 ``AgentProtocol`` 的物件，上層 workflow 程式一模一樣。

如何驗證
--------
``smoke_test`` 與 DevUI 都走這個 factory，只要這兩個能跑就代表 factory 沒問題。
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from agent_framework import Agent
from agent_framework.foundry import FoundryAgent, FoundryChatClient
from azure.identity import DefaultAzureCredential

from noa_workshop.n2_tools import FIELD_OPS_TOOLS, SECURITY_TOOLS, TELEMETRY_TOOLS

_INSTRUCTIONS_DIR = Path(__file__).resolve().parent / "instructions"

# 角色註冊表：邏輯 role 名稱 → (instructions 檔、hosted agent_name env、工具清單)
_ROLE_REGISTRY: dict[str, dict[str, Any]] = {
    "noc_manager": {
        "filename": "noc_manager.md",
        "agent_name_env": "NOA_NOC_MANAGER_AGENT_NAME",
        "default_agent_name": "noc-manager",
        "display_name": "NOCManager",
        # NOC manager 是協調者，不需要自己呼叫工具，所以預設空清單。
        "tools": [],
    },
    "telemetry_analyzer": {
        "filename": "telemetry_analyzer.md",
        "agent_name_env": "NOA_TELEMETRY_AGENT_NAME",
        "default_agent_name": "telemetry-analyzer",
        "display_name": "TelemetryAnalyzer",
        "tools": TELEMETRY_TOOLS,
    },
    "security_compliance": {
        "filename": "security_compliance.md",
        "agent_name_env": "NOA_SECURITY_AGENT_NAME",
        "default_agent_name": "security-compliance",
        "display_name": "SecurityCompliance",
        "tools": SECURITY_TOOLS,
    },
    "field_ops": {
        "filename": "field_ops.md",
        "agent_name_env": "NOA_FIELD_OPS_AGENT_NAME",
        "default_agent_name": "field-ops",
        "display_name": "FieldOps",
        "tools": FIELD_OPS_TOOLS,
    },
}


def _read_instructions(filename: str) -> str:
    path = _INSTRUCTIONS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Instructions file not found: {path}")
    return path.read_text(encoding="utf-8")


def _is_hosted_mode() -> bool:
    return os.getenv("NOA_USE_HOSTED_AGENTS", "false").strip().lower() == "true"


def _project_endpoint() -> str:
    # Foundry hosted 容器內部保留了 ``FOUNDRY_*`` / ``AGENT_*`` 這些環境變數前綴，
    # 部署腳本無法直接設 ``FOUNDRY_PROJECT_ENDPOINT``。
    # 為了讓本檔在本機與 hosted 容器內都能跑，這裡接受兩個名字：
    # - 本機：在 .env 裡填 ``FOUNDRY_PROJECT_ENDPOINT``
    # - 容器內：平台會注入 ``AZURE_AI_PROJECT_ENDPOINT``
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT") or os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        raise RuntimeError(
            "Neither FOUNDRY_PROJECT_ENDPOINT nor AZURE_AI_PROJECT_ENDPOINT is set."
            " Copy .env.example to .env and fill it in."
        )
    return endpoint


def _model() -> str:
    model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    if not model:
        raise RuntimeError(
            "AZURE_AI_MODEL_DEPLOYMENT_NAME is not set. Set it to your Foundry chat model deployment."
        )
    return model


@lru_cache(maxsize=1)
def _shared_credential() -> Any:
    # 本機與容器內共用一份 ``DefaultAzureCredential``。
    # DAC 的 chain 會自動判斷：在容器內選 managed identity，本機選你 az login 的身分。
    return DefaultAzureCredential()


@lru_cache(maxsize=1)
def shared_chat_client() -> FoundryChatClient:
    """回傳程序內共用的 FoundryChatClient（本地模式 agent 與 Magentic manager 都走這個）。"""
    return FoundryChatClient(
        project_endpoint=_project_endpoint(),
        model=_model(),
        credential=_shared_credential(),
    )


def make_agent(
    role: str,
    *,
    extra_tools: Iterable[Any] | None = None,
    tools_override: Iterable[Any] | None = None,
    name_override: str | None = None,
) -> Any:
    """建一個指定角色的 agent。

    Parameters
    ----------
    role : ``noc_manager`` / ``telemetry_analyzer`` / ``security_compliance`` / ``field_ops`` 之一。
    extra_tools : 可選。本地模式下要多掛的工具。
    tools_override : 可選。完全取代預設工具清單（只適用本地模式）。
        用於某些 runtime 無法序列化預設工具的狀況 — 例如 DevUI 的 agent-mode chat
        與 hosted Responses 皆不支援 ``function_approval_request``，需把 FieldOps 的 HITL
        ``create_dispatch_request`` 換成自動核准的 ``create_dispatch_request_auto``。
    name_override : 可選。覆寫 display_name（同一角色在不同 workflow 裡演 manager / participant 時有用）。
    """
    spec = _ROLE_REGISTRY.get(role)
    if spec is None:
        raise ValueError(f"Unknown role: {role}. Valid: {list(_ROLE_REGISTRY)}")

    display_name = name_override or spec["display_name"]

    if _is_hosted_mode():
        agent_name = os.getenv(spec["agent_name_env"], spec["default_agent_name"])
        version = os.getenv("NOA_AGENT_VERSION") or None
        kwargs: dict[str, Any] = {
            "project_endpoint": _project_endpoint(),
            "agent_name": agent_name,
            "credential": _shared_credential(),
        }
        if version:
            kwargs["agent_version"] = version
        return FoundryAgent(**kwargs)

    # 本地模式
    instructions = _read_instructions(spec["filename"])
    if tools_override is not None:
        tools: list[Any] = list(tools_override)
    else:
        tools = list(spec["tools"])
    if extra_tools:
        tools.extend(extra_tools)

    return Agent(
        client=shared_chat_client(),
        name=display_name,
        instructions=instructions,
        tools=tools,
        # HandoffBuilder 需要這個旗標，讓本地對話歷史與服務端同步，不會被 handoff tool-call 跳過。
        # 其他 orchestration 加了也不影響，為了一致一律開。
        require_per_service_call_history_persistence=True,
    )


def make_all_specialists() -> dict[str, Any]:
    """一次拿三位專家 agent（不含 NOC Manager）。"""
    return {
        "telemetry_analyzer": make_agent("telemetry_analyzer"),
        "security_compliance": make_agent("security_compliance"),
        "field_ops": make_agent("field_ops"),
    }
