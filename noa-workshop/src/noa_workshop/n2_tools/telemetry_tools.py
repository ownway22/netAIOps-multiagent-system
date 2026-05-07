"""Telemetry Analyzer 的工具集：KPI 查詢、告警、拓樸、baseline 比對、歷史工單搜尋。

所有函式都用 ``@tool`` 裝飾，讓 ``Agent`` 可以自動推論參數類型與描述。
``Annotated[..., Field(description=...)]`` 是推薦寫法，描述文字會被送進 LLM 的 tool schema。
"""

from __future__ import annotations

import statistics
from typing import Annotated, Any

from agent_framework import tool
from pydantic import Field

from .data_loader import load_json


@tool
def query_kpi_metrics(
    region: Annotated[str, Field(description="區域 key，例如 'north-transport-ring'")],
    metric: Annotated[
        str, Field(description="三選一：packet_loss_pct、latency_ms、throughput_gbps")
    ],
    time_window_minutes: Annotated[
        int, Field(description="回看視窗（分鐘），預設 30", ge=1, le=240)
    ] = 30,
) -> dict[str, Any]:
    """拿指定區域在視窗內的 KPI 樣本與統計摘要。"""
    data = load_json("telemetry/kpi_metrics.json")
    region_block = data["regions"].get(region)
    if region_block is None:
        return {"error": f"Unknown region: {region}", "valid_regions": list(data["regions"].keys())}
    samples = region_block.get("samples", [])
    # fixture 裡每個樣本間隔 5 分鐘，所以隨視窗取最近 N 個
    n = max(1, time_window_minutes // 5)
    selected = samples[-n:]
    values = [s[metric] for s in selected if metric in s]
    return {
        "region": region,
        "metric": metric,
        "samples": [{"ts": s["ts"], "value": s.get(metric)} for s in selected],
        "summary": {
            "count": len(values),
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "mean": round(statistics.fmean(values), 3) if values else None,
        },
        "baseline": region_block["baseline"].get(metric),
    }


@tool
def get_active_alarms(
    min_severity: Annotated[
        str, Field(description="最低四棟度：P1 | P2 | P3 | P4")
    ] = "P3",
) -> list[dict[str, Any]]:
    """列出低於或等於指定四棟度的告警（P1 最高）。"""
    order = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
    threshold = order.get(min_severity.upper(), 3)
    alarms = load_json("telemetry/alarms.json")["alarms"]
    return [a for a in alarms if order.get(a["severity"], 9) <= threshold]


@tool
def get_topology(
    scope: Annotated[
        str, Field(description="區域 key 或 'all'．指定 'all' 會拿到全部拓樸")
    ] = "all",
) -> dict[str, Any]:
    """拿區域節點與鏈路的拓樸關係，用來將告警轉換為 cable_id 與站點。"""
    topo = load_json("telemetry/topology.json")
    if scope == "all":
        return topo
    region_block = topo["regions"].get(scope)
    if region_block is None:
        return {"error": f"Unknown region: {scope}", "valid_regions": list(topo["regions"].keys())}
    return {scope: region_block}


@tool
def run_baseline_comparison(
    region: Annotated[str, Field(description="區域 key")],
    metric: Annotated[str, Field(description="KPI metric 名稱")],
) -> dict[str, Any]:
    """拿最新一筆 KPI 跟 baseline 與 SLA 門檻比對。"""
    data = load_json("telemetry/kpi_metrics.json")
    region_block = data["regions"].get(region)
    if region_block is None:
        return {"error": f"Unknown region: {region}"}
    samples = region_block.get("samples", [])
    if not samples:
        return {"error": "No samples available"}
    latest = samples[-1]
    baseline = region_block["baseline"].get(metric)
    sla = region_block["sla"].get(f"{metric}_max")
    current = latest.get(metric)
    if baseline is None or current is None:
        return {"error": f"Metric {metric} not available for {region}"}
    delta_ratio = round((current - baseline) / max(baseline, 1e-6), 2)
    return {
        "region": region,
        "metric": metric,
        "current": current,
        "baseline": baseline,
        "sla_threshold": sla,
        "delta_vs_baseline_x": delta_ratio,
        "violates_sla": (sla is not None and current > sla),
        "ts": latest["ts"],
    }


@tool
def search_historical_tickets(
    keyword: Annotated[str, Field(description="關鍵詞（自由文字），例如 'fiber'、'security'")],
) -> list[dict[str, Any]]:
    """以關鍵詞在過去工單的標題、root_cause、tags 中搜尋。"""
    tickets = load_json("tickets/historical_tickets.json")["tickets"]
    kw = keyword.lower()
    matches = []
    for t in tickets:
        haystack = " ".join([t.get("title", ""), t.get("root_cause", ""), " ".join(t.get("tags", []))]).lower()
        if kw in haystack:
            matches.append(
                {
                    "ticket_id": t["ticket_id"],
                    "title": t["title"],
                    "severity": t["severity"],
                    "mttr_minutes": t.get("mttr_minutes"),
                    "root_cause": t.get("root_cause"),
                    "tags": t.get("tags", []),
                }
            )
    return matches


TELEMETRY_TOOLS = [
    query_kpi_metrics,
    get_active_alarms,
    get_topology,
    run_baseline_comparison,
    search_historical_tickets,
]
