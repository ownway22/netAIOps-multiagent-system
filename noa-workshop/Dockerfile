# syntax=docker/dockerfile:1.7
# ----------------------------------------------------------------------------
# NOA Workshop — Foundry Hosted Agent 容器映像檔（linux/amd64）
#
# 與 sample-code/ipm_multiagent/Dockerfile 對齊（已驗證可用的參考範本）。關鍵選擇：
#   1. 用 requirements.txt（runtime 才需要的相依）取代 `pip install .`，
#      避免 DevUI / OTLP-grpc / 開發工具進來與 agent-framework==1.2.2 +
#      agent-framework-foundry-hosting=1.0.0a* 起衝突。
#   2. 透過 PYTHONPATH=/app/src 直接執行 package，不必先 pip install wheel。
#      runtime 用到的資料就在 package 內的 `src/noa_workshop/n3_data/`，
#      只要 `COPY src ./src` 一起搬進來，
#      `Path(__file__).parents[1] / "n3_data"` 一定找得到。
#   3. Layer cache：先複製 requirements，最後才複製程式碼。
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

# 先安裝 runtime 相依套件，後面動到程式碼也不會搞壞 pip 的 layer cache。
# `--pre` 是必要的，因為 agent-framework-foundry-hosting==1.0.0a260429 是
# pre-release 版本。
COPY requirements.txt ./
RUN pip install --no-cache-dir --pre -r requirements.txt

# 複製 package 原始碼（runtime JSON / markdown 資料就在
# /app/src/noa_workshop/n3_data/，所以一次性 copy src 就夠了）。
COPY src ./src

# 不裝 wheel 也能 import：直接把 src 加進 PYTHONPATH。
ENV PYTHONPATH=/app/src

# Foundry hosted-agent 規範：Responses 通訊協定走 8088 埠。
EXPOSE 8088

CMD ["python", "-m", "noa_workshop.n6_deployment.hosted_agent"]
