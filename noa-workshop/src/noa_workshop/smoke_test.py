"""Smoke test：驗證環境是否就緒。

用途
----
建立一個帶工具的 telemetry agent，問它一個會觸發 tool call 的問題。
看到表格化回覆代表 `.env` / `az login` / model deployment 都通了。

關鍵設計
--------
- 用 `make_agent("telemetry_analyzer")` 直接拿到綁好工具的 agent。
- 問題用繁中提問，agent 應該會呼叫 `query_kpi_metrics` 並用 baseline 比對。

如何驗證
--------
::

    uv run python -m noa_workshop.smoke_test
"""

from __future__ import annotations

import asyncio

from dotenv import load_dotenv

from noa_workshop.n1_agents import make_agent


async def main() -> None:
    load_dotenv()

    agent = make_agent("telemetry_analyzer")
    query = (
        "請查 north-transport-ring 區域過去 30 分鐘的 packet_loss_pct，"
        "並用 baseline 比對結果告訴我是否異常。"
    )
    print(f"\n[Q] {query}\n")
    result = await agent.run(query)
    print(f"[Agent] {result.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
