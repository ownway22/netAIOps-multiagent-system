"""用 ``MagenticBuilder`` 做的動態規劃 multi-agent orchestration（NOA Mark-2 動態 planning）。

用途
----
用於「情境 C：安全事件」。這裡的 manager 本身也是一個 agent，它會看著所有對話、動態決定讓誰
下一個發言，索引到 NOA Mark-2 的 dynamic-planning 模式。

關鍵設計
--------
- ``security_compliance`` 負責提供 IOC + 策略事實，``telemetry_analyzer`` 負責提供網路證據，
  manager 一輪一輪迴圈到拿到足夠信心的結論。
- ``MagenticBuilder`` 是高階拼裝器，不需要手寫 routing graph，動態控制流由 LLM 推論。

如何驗證
--------
- DevUI：``Orchestration_Magentic`` 出現在 entity 清單，送一句安全事件就會看到
  manager 交替讓 telemetry / security 發言。
- CLI::

      uv run python -m noa_workshop.n1_agents.orchestration_magentic
"""

from __future__ import annotations

import asyncio

from agent_framework import Agent, WorkflowAgent
from agent_framework.orchestrations import MagenticBuilder
from dotenv import load_dotenv

from noa_workshop.n1_agents import make_agent, shared_chat_client

SCENARIO_C_PROMPT = (
    "緊急通報：台灣中央核心 POP 節點 在 14:10 出現異常南向流量（egress +85%），同時偵測到簽章 SIG-BOT-2104 告警。請判斷：這是不是安全事件？若是請給出建議的 mitigation；若否請給出原因。"
)


MANAGER_INSTRUCTIONS = (
    "你是 NOC 多 agent 協調者。你會看到 telemetry 與 security 兩位專家的對話。"
    "請依下列原則決定誰下一個發言："
    " 1. 優先讓 security 做 IOC / 策略判斷。"
    " 2. 若 security 需要更多 KPI 證據，請 telemetry 補資料。"
    " 3. 兩位都給出明確結論後，自行收斂為一份對主管可讀的事件摘要，"
    "    一定要包含：是否為安全事件、信心等級、建議下一步、是否需要人類批准。"
    " 4. 全程使用繁體中文。"
)


AGENT_NAME = "Orchestration_Magentic"
AGENT_DESCRIPTION = (
    "NOA Magentic orchestration：manager agent 動態選握下一位發言者（telemetry 或 security），"
    "直到拿到明確的結論。"
)


def _build_workflow():
    """拼出 Magentic workflow（telemetry + security + manager）。"""

    telemetry = make_agent("telemetry_analyzer")
    security = make_agent("security_compliance")

    # 在 agent_framework v0.5+中，Magentic manager 本身就是一個 ``Agent``。
    # 這裡給它一個不掛工具的腦，與其他 agent 共用同一個 FoundryChatClient。
    manager = Agent(
        client=shared_chat_client(),
        name="MagenticManager",
        instructions=MANAGER_INSTRUCTIONS,
    )

    return MagenticBuilder(
        participants=[telemetry, security],
        manager_agent=manager,
        max_round_count=8,
        max_stall_count=2,
        max_reset_count=1,
        intermediate_outputs=True,
    ).build()


def get_agent() -> WorkflowAgent:
    """把 Magentic workflow 包成 chat-ready agent，讓 DevUI 可以直接對話。"""

    load_dotenv()
    workflow = _build_workflow()
    return workflow.as_agent(
        name=AGENT_NAME,
        description=AGENT_DESCRIPTION,
    )


async def main() -> None:
    load_dotenv()
    workflow = _build_workflow()

    print(f"\n=== {AGENT_NAME} (MagenticBuilder edition) ===")
    print(f"[User] {SCENARIO_C_PROMPT}\n")

    # 預設不使用 streaming，workshop 輸出較易讀。想看逐 token 演進可改為 stream=True。
    result = await workflow.run(SCENARIO_C_PROMPT)

    for event in result:
        executor = event.executor_id or ""
        if event.type == "data":
            text = getattr(event.data, "text", str(event.data))
            print(f"\n[{executor}] {text}")

    print("\n=== Final Magentic verdict ===")
    for output in result.get_outputs():
        print(output)


if __name__ == "__main__":
    asyncio.run(main())
