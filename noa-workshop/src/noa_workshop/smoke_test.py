"""M1 — Hello Agent smoke test.

Builds the telemetry_analyzer agent (which has tools) and asks it a question
that should trigger a tool call. Use this to verify your .env, az login, and
model deployment are wired up correctly before tackling M2-M4.

Run::

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
