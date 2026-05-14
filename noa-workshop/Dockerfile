# syntax=docker/dockerfile:1.7
# ----------------------------------------------------------------------------
# NOA Workshop — Foundry Hosted Agent container (linux/amd64)
#
# Aligned with sample-code/ipm_multiagent/Dockerfile (a verified-working
# reference). Key choices:
#   1. Use requirements.txt (runtime-only deps) instead of `pip install .`
#      to avoid pulling in DevUI / OTLP-grpc / dev tooling that conflicted
#      with agent-framework==1.2.2 + agent-framework-foundry-hosting=1.0.0a*.
#   2. Run the package via PYTHONPATH=/app/src — no wheel install needed.
#      The runtime data lives inside the package at
#      `src/noa_workshop/n3_data/`, so it ships with `COPY src ./src`
#      and `Path(__file__).parents[1] / "n3_data"` always resolves.
#   3. Layer cache: requirements first, code last.
# ----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install runtime dependencies first so subsequent code changes don't bust
# the pip layer cache. `--pre` is required because
# agent-framework-foundry-hosting==1.0.0a260429 is a pre-release tag.
COPY requirements.txt ./
RUN pip install --no-cache-dir --pre -r requirements.txt

# Copy package source (the runtime JSON/markdown data lives at
# /app/src/noa_workshop/n3_data/, so a single src copy is enough).
COPY src ./src

# Make the source tree importable without installing a wheel.
ENV PYTHONPATH=/app/src

# Foundry hosted-agent contract — Responses protocol on 8088.
EXPOSE 8088

CMD ["python", "-m", "noa_workshop.n6_deployment.hosted_agent_server"]
