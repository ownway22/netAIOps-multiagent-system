"""把 M3 Handoff 多-agent 團隊部署為 Foundry hosted agent。

這個腳本實作官方 Python SDK 的部署流程，詳見
https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent。

步驟：
    1. 從本專案 Dockerfile 裣出 ``linux/amd64`` 容器映像。
    2. 推到 Foundry 端的 ACR（預設 ``crazc475mssqyvc.azurecr.io``）。
    3. 呼叫 ``AIProjectClient.agents.create_version(...)`` 註冊一個 hosted
       agent 版本，平台會自動幫你布建基礎設施。
    4. 輪詢該版本，直到 ``status == 'active'``。
    5. 透過 ``project.get_openai_client(agent_name=...).responses.create(...)``
       走 Responses 協議做一次 smoke test。

跳起來::

    cd noa-workshop
    uv run python -m noa_workshop.n6_deployment.hosted_agent_deployer

可選的環境變數覆寫（預設值都是對 workshop 專案評估過的合理值）：

* ``ACR_LOGIN_SERVER``—ACR 登入伺服器（預設 ``crazc475mssqyvc.azurecr.io``）
* ``IMAGE_REPO``       —映像倉儲名稱（預設 ``noa-multiagent-hosted``）
* ``IMAGE_TAG``        —映像 tag（預設 ``v$(date +%s)``）
* ``HOSTED_AGENT_NAME``—hosted agent 名稱（預設 ``noa-multiagent-hosted``）
* ``SKIP_BUILD``       —有設時跳過 build/push（映像必須已存在）
* ``SKIP_DEPLOY``      —有設時跳過 create_version（只跱驗證）
"""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentProtocol,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from noa_workshop.n1_agents.orchestration_handoff import SCENARIO_A_PROMPT

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOCKERFILE = PROJECT_ROOT / "Dockerfile"


def _run(cmd: list[str], *, check: bool = True, env: dict[str, str] | None = None) -> None:
    print(f"\n$ {' '.join(shlex.quote(c) for c in cmd)}")
    subprocess.run(cmd, check=check, env=env)


def _shell_capture(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")

    project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model_deployment = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    acr_login_server = os.environ.get("ACR_LOGIN_SERVER", "crazc475mssqyvc.azurecr.io")
    acr_name = acr_login_server.split(".", 1)[0]
    image_repo = os.environ.get("IMAGE_REPO", "noa-multiagent-hosted")
    image_tag = os.environ.get("IMAGE_TAG", f"v{int(time.time())}")
    image_uri = f"{acr_login_server}/{image_repo}:{image_tag}"

    hosted_agent_name = os.environ.get("HOSTED_AGENT_NAME", "noa-multiagent-hosted")

    print("=== Foundry hosted-agent 部署（M3 Handoff）===")
    print(f"專案 endpoint   ：{project_endpoint}")
    print(f"模型部署名稱  ：{model_deployment}")
    print(f"ACR             ：{acr_login_server}")
    print(f"映像            ：{image_uri}")
    print(f"Hosted agent    ：{hosted_agent_name}")

    # ------------------------------------------------------------------
    # 1. 建立 & 推送容器映像（SKIP_BUILD=1 可跳過）
    # ------------------------------------------------------------------
    if os.environ.get("SKIP_BUILD"):
        print("\nSKIP_BUILD 已設——假設映像已經存在 ACR。")
    else:
        # ``az acr build`` 使用 ACR Tasks 在雲端建映像，不需要本地 docker daemon，
        # 並且不管開發者机器是什麼架構都能保證內部是 linux/amd64。
        # ``--no-logs`` 避免 Windows 上 colorama 遭遇 cp1252 讀不懂 UTF-8
        # build log 的崩潰。我們仍然能從 API 拿到 run ID 與最終狀態。
        _run(
            [
                "az",
                "acr",
                "build",
                "--registry",
                acr_name,
                "--image",
                f"{image_repo}:{image_tag}",
                "--platform",
                "linux",
                "--file",
                str(DOCKERFILE),
                "--no-logs",
                str(PROJECT_ROOT),
            ]
        )

    # ------------------------------------------------------------------
    # 2. 註冊 / 更新 hosted agent 版本
    # ------------------------------------------------------------------
    credential = AzureCliCredential()
    project = AIProjectClient(
        endpoint=project_endpoint,
        credential=credential,
        allow_preview=True,
    )

    if os.environ.get("SKIP_DEPLOY"):
        print("\nSKIP_DEPLOY 已設——跳過 create_version，直接走驗證。")
        latest_version = _resolve_latest_active_version(project, hosted_agent_name)
    else:
        latest_version = _create_or_update_agent(
            project=project,
            agent_name=hosted_agent_name,
            image_uri=image_uri,
            model_deployment=model_deployment,
        )
        _wait_for_active(project, hosted_agent_name, latest_version)

    # ------------------------------------------------------------------
    # 3. 透過 Responses API 驗證
    # ------------------------------------------------------------------
    print("\n=== 驗證 Responses API ===")
    openai_client = project.get_openai_client(agent_name=hosted_agent_name)

    # 預熱：先送一個微型請求 trigger 最小副本上線，不要讓正式場景去燒掛
    # gateway 大約 360 秒的時間預算。Hosted agent 遇到第一次 /responses 才會
    # 自動從 0 跳到 1 個副本。
    print("\n--- 預熱記 ping ---")
    prewarm = openai_client.responses.create(
        input="ping. reply with the single word OK.",
        timeout=300,
    )
    print(prewarm.output_text)

    print("\n--- M3 SCENARIO_A_PROMPT ---")
    print(SCENARIO_A_PROMPT)
    response = openai_client.responses.create(
        input=SCENARIO_A_PROMPT,
        timeout=600,
    )
    print("\n--- Hosted agent 裁決 ---")
    print(response.output_text)
    print("\n部署與 Responses API 驗證都已完成。")
    return 0


def _create_or_update_agent(
    *,
    project: AIProjectClient,
    agent_name: str,
    image_uri: str,
    model_deployment: str,
) -> str:
    """第一次部署時創建 agent，之後每次重跱則推一個新版本。"""

    # NOTE：Foundry hosted-agent runtime 保留 ``FOUNDRY_*`` 與 ``AGENT_*`` 這些
    # env-var prefix—這裡如果傳 ``FOUNDRY_PROJECT_ENDPOINT`` 進去會被拒為
    # ``invalid_payload``。改用沒被保留的 ``AZURE_AI_PROJECT_ENDPOINT``
    # （agent_factory._project_endpoint() 會當備援讀它）—這也與
    # sample-code/ipm_multiagent 參考作法一致。
    # ``AZURE_AI_MODEL_DEPLOYMENT_NAME`` 是 agent_factory._model() 的必需項。
    # ``NOA_USE_HOSTED_AGENTS=false`` 讓 Handoff team 仍以進程內
    # Agent + FoundryChatClient 的方式跱。
    project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    definition = HostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="1.0.0"),
        ],
        cpu="1",
        memory="2Gi",
        image=image_uri,
        environment_variables={
            "AZURE_AI_PROJECT_ENDPOINT": project_endpoint,
            "AZURE_AI_MODEL_DEPLOYMENT_NAME": model_deployment,
            "NOA_USE_HOSTED_AGENTS": "false",
        },
    )

    try:
        existing = project.agents.get(agent_name=agent_name)
    except Exception:  # noqa: BLE001 — SDK 可能丟 ResourceNotFound 或 HttpResponseError
        existing = None

    if existing is None:
        print(f"\n創建 hosted agent '{agent_name}'（同時也會創建 version 1）...")
        result = project.agents.create_version(agent_name=agent_name, definition=definition)
    else:
        print(f"\nAgent '{agent_name}' 已存在——推一個新版本...")
        result = project.agents.create_version(agent_name=agent_name, definition=definition)

    version = getattr(result, "version", None) or result["version"]
    print(f"已請求 version {version}。")
    return str(version)


def _wait_for_active(project: AIProjectClient, agent_name: str, version: str, *, timeout_s: int = 600) -> None:
    print(f"等待 version {version} 進入 active 狀態（限時 {timeout_s} 秒）...")
    start = time.time()
    while True:
        info = project.agents.get_version(agent_name=agent_name, agent_version=version)
        # SDK 回一個 model 物件；這裡轉為 dict-style 存取以增加適應性。
        status = getattr(info, "status", None) or info["status"]
        elapsed = int(time.time() - start)
        print(f"  [{elapsed}s] status={status}")
        if status == "active":
            print("Hosted agent 已進入 active。")
            return
        if status == "failed":
            error = getattr(info, "error", None) or info.get("error")
            print(f"佈建失敗：{error}", file=sys.stderr)
            raise RuntimeError(f"Hosted agent provisioning failed: {error}")
        if elapsed > timeout_s:
            raise TimeoutError(f"Hosted agent did not reach 'active' within {timeout_s}s")
        time.sleep(10)


def _resolve_latest_active_version(project: AIProjectClient, agent_name: str) -> str:
    versions = list(project.agents.list_versions(agent_name=agent_name))
    if not versions:
        raise RuntimeError(f"No versions found for agent '{agent_name}'.")
    # 挪出最新的 active 版本。
    actives = [v for v in versions if (getattr(v, "status", None) or v["status"]) == "active"]
    if not actives:
        raise RuntimeError(f"No active versions for '{agent_name}'.")
    latest = max(actives, key=lambda v: getattr(v, "version", None) or v["version"])
    return str(getattr(latest, "version", None) or latest["version"])


if __name__ == "__main__":
    raise SystemExit(main())
