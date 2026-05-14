"""Deploy the M3 Handoff multi-agent team as a Foundry hosted agent.

This script implements the official Python-SDK deployment path documented at
https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent.

Steps:
    1. Build the container image for ``linux/amd64`` from the project Dockerfile.
    2. Push it to the Foundry-side ACR (``crazc475mssqyvc.azurecr.io`` by default).
    3. Call ``AIProjectClient.agents.create_version(...)`` to register a hosted
       agent version. The platform provisions infrastructure automatically.
    4. Poll the version endpoint until ``status == 'active'``.
    5. Smoke-test the deployed agent through the Responses protocol via
       ``project.get_openai_client(agent_name=...).responses.create(...)``.

Run::

    cd noa-workshop
    uv run python -m noa_workshop.n6_deployment.hosted_agent_deployer

Optional environment overrides (defaults are sensible for the workshop project):

* ``ACR_LOGIN_SERVER`` – ACR login server (default ``crazc475mssqyvc.azurecr.io``)
* ``IMAGE_REPO``        – Image repository name (default ``noa-multiagent-hosted``)
* ``IMAGE_TAG``         – Image tag (default: ``v$(date +%s)``)
* ``HOSTED_AGENT_NAME`` – Hosted agent name (default ``noa-multiagent-hosted``)
* ``SKIP_BUILD``        – If set, skip docker build/push (image must already exist)
* ``SKIP_DEPLOY``       – If set, skip create_version (only run validation)
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

from noa_workshop.n1_agents.multi_agent_handoff import SCENARIO_A_PROMPT

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

    print("=== Foundry hosted-agent deployment (M3 Handoff) ===")
    print(f"Project endpoint : {project_endpoint}")
    print(f"Model deployment : {model_deployment}")
    print(f"ACR              : {acr_login_server}")
    print(f"Image            : {image_uri}")
    print(f"Hosted agent     : {hosted_agent_name}")

    # ------------------------------------------------------------------
    # 1. Build & push container image (skip with SKIP_BUILD=1)
    # ------------------------------------------------------------------
    if os.environ.get("SKIP_BUILD"):
        print("\nSKIP_BUILD set — assuming the image already exists in ACR.")
    else:
        # ``az acr build`` builds the image in ACR Tasks (cloud-side) so no
        # local Docker daemon is required, and the linux/amd64 platform is
        # guaranteed regardless of the developer machine's architecture.
        # ``--no-logs`` avoids the Windows-side colorama crash that hits when
        # the ``az.exe`` invoked from WSL streams UTF-8 build output through
        # cp1252; we still get the run ID + final status from the API.
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
    # 2. Register / update the hosted agent version
    # ------------------------------------------------------------------
    credential = AzureCliCredential()
    project = AIProjectClient(
        endpoint=project_endpoint,
        credential=credential,
        allow_preview=True,
    )

    if os.environ.get("SKIP_DEPLOY"):
        print("\nSKIP_DEPLOY set — skipping create_version, going straight to validation.")
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
    # 3. Validate via the Responses API
    # ------------------------------------------------------------------
    print("\n=== Validating Responses API ===")
    openai_client = project.get_openai_client(agent_name=hosted_agent_name)

    # Pre-warm: a tiny request to trigger min-replica scale-up before the
    # full scenario, so we don't burn the gateway's ~360s budget on cold
    # start. The hosted agent auto-scales from 0→1 on first /responses hit.
    print("\n--- Pre-warm ping ---")
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
    print("\n--- Hosted agent verdict ---")
    print(response.output_text)
    print("\nDeployment + Responses-API validation complete.")
    return 0


def _create_or_update_agent(
    *,
    project: AIProjectClient,
    agent_name: str,
    image_uri: str,
    model_deployment: str,
) -> str:
    """Create the agent the first time, or push a new version on subsequent runs."""

    # NOTE: The Foundry hosted-agent runtime reserves the ``FOUNDRY_*`` and
    # ``AGENT_*`` env-var prefixes — passing ``FOUNDRY_PROJECT_ENDPOINT`` here
    # is rejected with ``invalid_payload``. Use the non-reserved
    # ``AZURE_AI_PROJECT_ENDPOINT`` (which factory._project_endpoint() reads
    # as a fallback) — this matches the sample-code/ipm_multiagent reference.
    # ``AZURE_AI_MODEL_DEPLOYMENT_NAME`` is required by factory._model().
    # ``NOA_USE_HOSTED_AGENTS=false`` keeps the Handoff team running as
    # in-process Agent + FoundryChatClient.
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
    except Exception:  # noqa: BLE001 — SDK raises ResourceNotFound or HttpResponseError
        existing = None

    if existing is None:
        print(f"\nCreating hosted agent '{agent_name}' (this also creates version 1)...")
        result = project.agents.create_version(agent_name=agent_name, definition=definition)
    else:
        print(f"\nAgent '{agent_name}' exists — creating a new version...")
        result = project.agents.create_version(agent_name=agent_name, definition=definition)

    version = getattr(result, "version", None) or result["version"]
    print(f"Version {version} requested.")
    return str(version)


def _wait_for_active(project: AIProjectClient, agent_name: str, version: str, *, timeout_s: int = 600) -> None:
    print(f"Waiting for version {version} to become active (timeout {timeout_s}s)...")
    start = time.time()
    while True:
        info = project.agents.get_version(agent_name=agent_name, agent_version=version)
        # The SDK returns a model object; convert to dict-style access for resilience.
        status = getattr(info, "status", None) or info["status"]
        elapsed = int(time.time() - start)
        print(f"  [{elapsed}s] status={status}")
        if status == "active":
            print("Hosted agent is active.")
            return
        if status == "failed":
            error = getattr(info, "error", None) or info.get("error")
            print(f"Provisioning failed: {error}", file=sys.stderr)
            raise RuntimeError(f"Hosted agent provisioning failed: {error}")
        if elapsed > timeout_s:
            raise TimeoutError(f"Hosted agent did not reach 'active' within {timeout_s}s")
        time.sleep(10)


def _resolve_latest_active_version(project: AIProjectClient, agent_name: str) -> str:
    versions = list(project.agents.list_versions(agent_name=agent_name))
    if not versions:
        raise RuntimeError(f"No versions found for agent '{agent_name}'.")
    # Pick the newest active one.
    actives = [v for v in versions if (getattr(v, "status", None) or v["status"]) == "active"]
    if not actives:
        raise RuntimeError(f"No active versions for '{agent_name}'.")
    latest = max(actives, key=lambda v: getattr(v, "version", None) or v["version"])
    return str(getattr(latest, "version", None) or latest["version"])


if __name__ == "__main__":
    raise SystemExit(main())
