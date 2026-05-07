"""Field Ops 的工具集：工程師檢索、庫存查詢、派工單（HITL 人工審核）、通知信草稿。

``create_dispatch_request`` 是重點示範：裝上 ``approval_mode="always_require"``，
代表「一定要等人顯式按同意才能執行」。
``create_dispatch_request_auto`` 是同語意但不加審核的版本，提供給未支援
``function_approval_request`` 內容型別的 runtime（DevUI agent-mode、M5 hosted Responses server）。
"""

from __future__ import annotations

from typing import Annotated, Any

from agent_framework import tool
from pydantic import Field

from .data_loader import load_json


def _site_to_region(site: str) -> str:
    if site.startswith("TPE-"):
        return "north-transport-ring"
    if site.startswith("TYO-"):
        return "central-core-pop-1"
    return "unknown"


@tool
def find_nearest_technician(
    location: Annotated[
        str, Field(description="站點代碼（例如 TPE-Banqiao）或區域 key")
    ],
    required_skill: Annotated[
        str, Field(description="技能關鍵詞：fiber-splicing | hardware-swap | rf-tuning | data-center | console-debug | tower-climbing")
    ],
) -> list[dict[str, Any]]:
    """以「站點符合度 + 可調度」排序，回傳最多 3 名候選工程師。"""
    techs = load_json("field_ops/technicians.json")["technicians"]
    skill = required_skill.lower()
    target_region = _site_to_region(location) if "-" in location else location

    def score(t: dict[str, Any]) -> int:
        s = 0
        if skill in [x.lower() for x in t["skills"]]:
            s += 10
        if t["base_site"].lower() == location.lower():
            s += 5
        if _site_to_region(t["base_site"]) == target_region:
            s += 3
        if t["status"] == "available":
            s += 2
        elif t["status"] == "on-shift":
            s += 1
        return s

    ranked = sorted(techs, key=score, reverse=True)
    return [
        {
            "id": t["id"],
            "name": t["name"],
            "base_site": t["base_site"],
            "skills": t["skills"],
            "status": t["status"],
            "phone": t["phone"],
            "match_score": score(t),
        }
        for t in ranked[:3]
        if score(t) > 0
    ]


@tool
def check_inventory(
    part_id: Annotated[str, Field(description="零件 ID（例如 FIBER-SPLICE-KIT-A）")],
) -> dict[str, Any]:
    """查某個零件的倉儲庫存狀態。"""
    parts = load_json("field_ops/inventory.json")["parts"]
    for p in parts:
        if p["part_id"].lower() == part_id.lower():
            return {"available": p["stock"] > 0, **p}
    return {"available": False, "part_id": part_id, "note": "Part not found in inventory"}


@tool(approval_mode="always_require")
def create_dispatch_request(
    technician_id: Annotated[str, Field(description="被派遣的工程師 ID")],
    incident_id: Annotated[str, Field(description="事件或工單 ID")],
    site: Annotated[str, Field(description="目標站點代碼")],
    cable_or_component: Annotated[
        str, Field(description="要修復 / 更換的 cable_id 或元件")
    ],
    eta_minutes: Annotated[int, Field(description="預計抵達現場所需分鐘", ge=10, le=480)],
    parts: Annotated[
        list[str], Field(description="作業需要的 part_id 清單")
    ],
) -> dict[str, Any]:
    """建立一張派工單．需要人工審核同意才會被記錄。

    這是本 workshop 的 HITL（Human-in-the-Loop）示範：裝了
    ``approval_mode="always_require"`` 後，Agent 只要呼叫這個工具，
    runtime 就會發出 ``function_approval_request`` 事件、挀住執行，
    等人類輸入 approve / reject 後才會出現「動作」。
    """
    return {
        "dispatch_id": f"DISP-{incident_id}-{technician_id}",
        "technician_id": technician_id,
        "incident_id": incident_id,
        "site": site,
        "target": cable_or_component,
        "eta_minutes": eta_minutes,
        "parts": parts,
        "status": "approved-and-recorded",
    }


@tool
def create_dispatch_request_auto(
    technician_id: Annotated[str, Field(description="被派遣的工程師 ID")],
    incident_id: Annotated[str, Field(description="事件或工單 ID")],
    site: Annotated[str, Field(description="目標站點代碼")],
    cable_or_component: Annotated[
        str, Field(description="要修復 / 更換的 cable_id 或元件")
    ],
    eta_minutes: Annotated[int, Field(description="預計抵達現場所需分鐘", ge=10, le=480)],
    parts: Annotated[list[str], Field(description="作業需要的 part_id 清單")],
) -> dict[str, Any]:
    """自動同意版本的派工單（沒有 HITL 門）。

    輸入 / 輸出與 ``create_dispatch_request`` 完全一樣，只是不會發出
    ``function_approval_request`` 內容。設計這個版本是為了送給還不能序列化
    該內容型別的 runtime，主要是：

    - DevUI 的 *agent-mode* 對話（``Orchestration_Sequential``、
      ``Orchestration_Handoff``、``Orchestration_Magentic``），一下有 approval
      request 就會跳 ``Object of type Content is not JSON serializable``。
    - hosted-agent 部署使用的 ``agent_framework_foundry_hosting`` Responses 協議。

    HITL 本身可以在原本的 ``Workflow_Handoff`` graph（DevUI workflow-mode）裡
    正常看到 end-to-end 示範，所以 workshop 課程內容仍完整保留。
    """

    return {
        "dispatch_id": f"DISP-{incident_id}-{technician_id}",
        "technician_id": technician_id,
        "incident_id": incident_id,
        "site": site,
        "target": cable_or_component,
        "eta_minutes": eta_minutes,
        "parts": parts,
        "status": "auto-approved-and-recorded",
        "note": "Auto-approval path. M3 graph workflow demonstrates the HITL gate.",
    }


@tool
def draft_notification_email(
    audience: Annotated[
        str, Field(description="收件對象群組：'noc-team' | 'leadership' | 'customer-success'")
    ],
    subject: Annotated[str, Field(description="信件主旨")],
    body: Annotated[str, Field(description="信件內文（純文本，可多段）")],
) -> dict[str, Any]:
    """起草一封通知信（不會實際寄出），回傳一個結構化信封讓人類審閱。"""
    routing = {
        "noc-team": "noc-team@example.com",
        "leadership": "network-leadership@example.com",
        "customer-success": "cs-ops@example.com",
    }
    return {
        "to": routing.get(audience, audience),
        "subject": subject,
        "body": body,
        "status": "drafted",
        "note": "This email has NOT been sent. Forward to your mail client to send.",
    }


FIELD_OPS_TOOLS = [
    find_nearest_technician,
    check_inventory,
    create_dispatch_request,
    draft_notification_email,
]


# 該 list 給還不能序列化 ``function_approval_request`` 的 runtime 使用。
# 主要是：DevUI agent-mode 對話、M5 Foundry hosted Responses server。
# 詳見 ``create_dispatch_request_auto`` 的說明。
FIELD_OPS_TOOLS_AUTO_APPROVE = [
    find_nearest_technician,
    check_inventory,
    create_dispatch_request_auto,
    draft_notification_email,
]
