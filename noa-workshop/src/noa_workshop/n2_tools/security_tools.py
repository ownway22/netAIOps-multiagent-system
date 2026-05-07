"""Security & Compliance 的工具集：IOC 查詢、策略檢查、SLA 驗證、知識庫查詢。

全部都是「只讀」工具：agent 只能查事實、不能執行任何阻擋或設定變更。
"""

from __future__ import annotations

from typing import Annotated, Any

from agent_framework import tool
from pydantic import Field

from .data_loader import load_json, load_text


@tool
def lookup_threat_intel(
    indicator: Annotated[
        str, Field(description="要查的 IP / domain / hash / 簽章 ID")
    ],
) -> dict[str, Any]:
    """拿 IOC feed 比對一個 indicator（IP / domain / hash / signature）。"""
    feed = load_json("threat_intel/ioc_feed.json")
    needle = indicator.strip().lower()
    for ind in feed["indicators"]:
        if ind["indicator"].lower() == needle:
            return {"hit": True, "type": "indicator", **ind}
    for sig in feed["signatures"]:
        if sig["sig_id"].lower() == needle:
            return {"hit": True, "type": "signature", **sig}
    return {"hit": False, "indicator": indicator, "note": "Not found in current IOC feed"}


@tool
def check_security_policy(
    action_or_config: Annotated[
        str,
        Field(description="要評估的動作或設定變更（自由文字描述）"),
    ],
) -> dict[str, Any]:
    """檢查某個動作 / 設定是否命中「阻擋樣式」或違反安全策略。"""
    policies = load_json("knowledge/policies.json")
    text = action_or_config.lower()
    matched_blocked = [p for p in policies.get("blocked_indicators", []) if p.lower() in text]
    return {
        "input": action_or_config,
        "blocked_pattern_matches": matched_blocked,
        "policies": policies["security_policies"],
        "verdict": "blocked" if matched_blocked else "needs-human-review",
    }


@tool
def validate_sla(
    region: Annotated[str, Field(description="區域 key")],
    latency_ms: Annotated[float, Field(description="觀測到的 latency（毫秒）")],
    packet_loss_pct: Annotated[float, Field(description="觀測到的封包丟失率（百分比）")],
) -> dict[str, Any]:
    """拿現職 KPI 跟區域的 SLA 表比對，回報是否違反 SLA。"""
    sla = load_json("knowledge/policies.json")["sla"].get(region)
    if sla is None:
        return {"error": f"No SLA defined for region: {region}"}
    violations = []
    if latency_ms > sla["latency_ms_max"]:
        violations.append(f"latency {latency_ms}ms > SLA {sla['latency_ms_max']}ms")
    if packet_loss_pct > sla["packet_loss_pct_max"]:
        violations.append(
            f"packet_loss {packet_loss_pct}% > SLA {sla['packet_loss_pct_max']}%"
        )
    return {"region": region, "violations": violations, "violates_sla": bool(violations)}


@tool
def list_compliance_violations(
    region: Annotated[str, Field(description="區域 key")],
) -> list[dict[str, Any]]:
    """列出一個區域目前的合規 / SLA 違反條目（從 KPI 推導）。"""
    kpi_data = load_json("telemetry/kpi_metrics.json")["regions"].get(region)
    if kpi_data is None:
        return []
    if not kpi_data["samples"]:
        return []
    latest = kpi_data["samples"][-1]
    sla = kpi_data["sla"]
    out = []
    if latest.get("packet_loss_pct", 0) > sla["packet_loss_pct_max"]:
        out.append({"type": "sla-packet-loss", "value": latest["packet_loss_pct"], "ts": latest["ts"]})
    if latest.get("latency_ms", 0) > sla["latency_ms_max"]:
        out.append({"type": "sla-latency", "value": latest["latency_ms"], "ts": latest["ts"]})
    return out


@tool
def knowledge_search(
    topic: Annotated[
        str, Field(description="二選一：fiber_cut | security_incident")
    ],
) -> str:
    """拿指定主題的 SOP markdown（給 NOC Manager / Security agent 讀）。"""
    topic = topic.lower().strip()
    mapping = {
        "fiber_cut": "knowledge/sop_fiber_cut.md",
        "security_incident": "knowledge/sop_security_incident.md",
    }
    rel = mapping.get(topic)
    if rel is None:
        return f"No SOP indexed for topic '{topic}'. Available: {list(mapping.keys())}"
    return load_text(rel)


SECURITY_TOOLS = [
    lookup_threat_intel,
    check_security_policy,
    validate_sla,
    list_compliance_violations,
    knowledge_search,
]
