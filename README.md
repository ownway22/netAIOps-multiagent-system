# NOA Multi-Agent Workshop

> 我們把 Microsoft NOA 簡化成 **4 個專業 agent x 3 種 orchestration 模式**，做一套擬真電信網路 incident 的 multi-agent 系統。
> 並透過 **3 個網路維運場景 x 10 個擬真資料集**，學習 Micrososft NOA 的核心精神。
> 最後把整個 multi-agent 系統的執行環境 host 在 **Microsoft Foundry** 服務中，並發布至 **Microsoft Teams** 頻道，以協助一般使用者解決網路維運相關的技術問題。

---

## 📖 目錄

- [實作要點](#實作要點)
- [前置需求](#前置需求)
- [概念地圖](#概念地圖)
  - [Agents ↔ Tools ↔ Data 三層結構](#agents--tools--data-三層結構)
  - [4 個 agent 的角色設定](#4-個-agent-的角色設定)
  - [4 個 agent 的 RACI](#4-個-agent-的-raci)
  - [10 個擬真資料集](#10-擬真資料集)
- [專案結構](#專案結構)
- [操作流程](#操作流程)
  - [Step 1 — 建立 agents](#step-1--建立-agents)
  - [Step 2 — Agent framework](#step-2--agent-framework)
  - [Step 3 — multiagent 協作](#step-3--multiagent-協作)
  - [Step 4 — 部署到 Foundry](#step-4--部署到-foundry)
  - [Step 5 — 發布到 Teams](#step-5--發布到-teams)
- [快速上手](#快速上手)
- [參考資料](#參考資料)

---

## 實作要點

| 主題                  | 內容                                                                                       |
| --------------------- | ------------------------------------------------------------------------------------------ |
| **Agent 設計**        | 4 個 agent 的 system prompt 拆分原則：NOC Manager + Telemetry / Security / Field Ops       |
| **Tool 設計**         | 各 agent 用 Python `@tool` 綁定的工具集（含 HITL `approval_mode="always_require"`）        |
| **Orchestration**     | Sequential / Handoff / Magentic 三種多 agent 協作模式對比                                  |
| **DevUI**             | 用 `agent_framework.devui` 在瀏覽器互動觀察 agent 與 workflow                              |
| **Foundry portal**    | 在 Foundry portal 建立 4 個 Prompt Agent，切換到 hosted 模式                               |
| **Hosted Agent 部署** | 把 Handoff multi-agent 包成容器，用 `AIProjectClient.agents.create_version` 部署到 Foundry |

---

## 前置需求

1. **Python 3.10+**（建議 3.11）與 [`uv`](https://docs.astral.sh/uv/)
2. **Azure CLI** 並登入：`az login`
3. **Microsoft Foundry project**，內含一個已部署的 chat 模型（建議 `gpt-4o`）
4. **Docker / Azure CLI ACR 擴充**（只有 Step 5 部署 hosted agent 需要）
5. **Clone 本專案到本機**：

   ```bash
   git clone https://github.com/ownway22/netAIOps-multiagent-system
   ```

---

## 概念地圖

### Agents ↔ Tools ↔ Data 三層結構

下圖只給三層結構的鳥瞰；每個 agent 對應的工具與資料檔的詳細名稱，請看下方 [4 個 agent 的角色設定](#4-個-agent-的角色設定)。

```mermaid
flowchart LR
    User([👤 使用者 / NOC 主管])

    subgraph Agents["Agents（n1_agents/instructions/）"]
        direction TB
        NOC["🧭 <b>NOC Manager</b><br/><i>協調者，無工具</i>"]
        TEL["📊 <b>Telemetry Analyzer<br/>Agent</b>"]
        SEC["🛡️ <b>Security & Compliance<br/>Agent</b>"]
        FOP["🔧 <b>Field Ops Agent</b>"]
    end

    subgraph Tools["Tools（n2_tools/，@tool）"]
        direction TB
        TEL_T["<b>TELEMETRY_TOOLS</b><br/>5 個工具"]
        SEC_T["<b>SECURITY_TOOLS</b><br/>5 個工具"]
        FOP_T["<b>FIELD_OPS_TOOLS</b><br/>4 個工具（含 HITL）"]
    end

    subgraph Data["Data（n3_data/）"]
        direction TB
        D_TEL["telemetry / tickets"]
        D_KNW["knowledge / threat_intel"]
        D_FOP["field_ops"]
    end

    User -->|提問 / incident| NOC
    NOC -.handoff.-> TEL
    NOC -.handoff.-> SEC
    NOC -.handoff.-> FOP
    NOC -->|彙整摘要| User

    TEL --> TEL_T --> D_TEL
    SEC --> SEC_T --> D_KNW
    FOP --> FOP_T --> D_FOP

    classDef agent fill:#E3F2FD,stroke:#1565C0,color:#0D47A1
    classDef tool fill:#FFF8E1,stroke:#F9A825,color:#5D4037
    classDef data fill:#E8F5E9,stroke:#2E7D32,color:#1B5E20
    class NOC,TEL,SEC,FOP agent
    class TEL_T,SEC_T,FOP_T tool
    class D_TEL,D_KNW,D_FOP data
```

### 4 個 agent 的角色設定

|      | **NOC Manager**                            | **Telemetry Analyzer<br/>Agent**                                           | **Security & Compliance<br/>Agent**                                                                         | **Field Ops<br/>Agent**                                                       |
| ---- | ------------------------------------------ | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 角色 | **NOC 的協調者**。                         | **網路遙測分析師**。                                                       | **網路安全與合規驗證員**。                                                                                  | **現場維運協調員**。                                                          |
| 指令 | `noc_manager.md`                           | `telemetry_analyzer.md`                                                    | `security_compliance.md`                                                                                    | `field_ops.md`                                                                |
| 工具 | _(無 — 純協調，把任務 handoff 給三位專家)_ | `TELEMETRY_TOOLS`<br/>(`telemetry_tools.py`)                               | `SECURITY_TOOLS`<br/>(`security_tools.py`)                                                                  | `FIELD_OPS_TOOLS`<br/>(`field_ops_tools.py`)                                  |
| 資料 | _(無)_                                     | `n3_data/telemetry/*.json`、<br/>`n3_data/tickets/historical_tickets.json` | `n3_data/threat_intel/ioc_feed.json`、<br/>`n3_data/knowledge/*`、<br/>`n3_data/telemetry/kpi_metrics.json` | `n3_data/field_ops/technicians.json`、<br/>`n3_data/field_ops/inventory.json` |

### 4 個 agent 的 RACI

| 動作           | NOC Manager | Telemetry | Security | Field Ops        |
| -------------- | ----------- | --------- | -------- | ---------------- |
| 接收使用者問題 | **R/A**     | I         | I        | I                |
| 查 KPI / 告警  | C           | **R/A**   | I        | I                |
| IOC / 策略判斷 | C           | I         | **R/A**  | I                |
| 派工 / 通知    | A           | I         | I        | **R**（需 HITL） |
| 對主管彙整摘要 | **R/A**     | C         | C        | C                |

> R=Responsible / A=Accountable / C=Consulted / I=Informed

### 10 個擬真資料集

`n3_data/` 下的 10 份檔案，對應到一個典型電信／網路維運中心的資料來源系統與負責部門，剛好覆蓋一次完整的事件處理迴路：**告警 → 佐證 → 定位 → 知識比對 → 派工 → 留檔**。

| 層級             | 檔案                              | 對應 OSS/BSS 模組／來源系統                                                         | 主要負責部門               |
| ---------------- | --------------------------------- | ----------------------------------------------------------------------------------- | -------------------------- |
| **觀測層**       | `alarms.json`、`kpi_metrics.json` | FM（Fault Mgmt）+ PM（Performance Mgmt）／NMS、EMS、Streaming Telemetry、Prometheus | NOC                        |
| **拓撲／資產層** | `topology.json`、`inventory.json` | Inventory／CMDB（Netbox、ServiceNow CMDB）、IP/Optical Planning、WMS                | Network Planning + 倉管    |
| **人力／作業層** | `technicians.json`                | WFM／FSM（ServiceNow FSM、Salesforce FSL）                                          | 區網維運 / 外勤派工中心    |
| **知識／政策層** | `policies.json`、`sop_*.md`       | Policy Engine、Knowledge Base（Confluence、ServiceNow KB）、SLA 管理平台            | NOC + Network Architecture |
| **安全層**       | `ioc_feed.json`                   | TIP（MISP、Anomali、Recorded Future）、SIEM（Splunk、Sentinel）                     | SOC / Threat Intel         |
| **歷史／回饋層** | `historical_tickets.json`         | TTS / ITSM（ServiceNow ITSM、BMC Remedy、TM Forum TMF621）                          | NOC + SRE                  |

> 提供 **擬真電信資料集**（KPI 時序、告警、topology、SOP、ticket、IOC、技師排班）。

---

## 專案結構

```
noa-workshop/
├── README.md                       ← 你現在看的這份
├── pyproject.toml                  ← 套件相依
├── .env.example                    ← 環境變數範本
├── Dockerfile                      ← Step 5 hosted-agent 容器
├── agent.manifest.yaml             ← Step 5 azd 部署 manifest
├── src/noa_workshop/
│   ├── smoke_test.py               ← Quick Start: hello agent + 1 tool
│   ├── n1_agents/
│   │   ├── instructions/                ← 4 份繁中 system prompt（markdown）
│   │   ├── agent_factory.py             ← 雙模式 agent factory
│   │   ├── single_agents.py             ← 4 個 single agent + get_all_single_agents()
│   │   ├── orchestration_sequential.py  ← SequentialBuilder
│   │   ├── orchestration_handoff.py     ← HandoffBuilder
│   │   └── orchestration_magentic.py    ← MagenticBuilder
│   ├── n2_tools/
│   │   ├── telemetry_tools.py
│   │   ├── security_tools.py
│   │   ├── field_ops_tools.py      ← 含 HITL approval_mode 與 _AUTO 兩版
│   │   └── data_loader.py          ← data loader、incident memory
│   ├── n3_data/                    ← 8 份擬真 sample data
│   │   ├── telemetry/              ← kpi_metrics / alarms / topology
│   │   ├── tickets/                ← historical_tickets
│   │   ├── knowledge/              ← policies、SOP markdown
│   │   ├── threat_intel/           ← ioc_feed
│   │   └── field_ops/              ← technicians、inventory
│   ├── n4_workflows/
│   │   ├── workflow_sequential.py  ← 顯式 graph (DevUI 可視化)
│   │   └── workflow_handoff.py     ← 顯式 graph + HITL approval
│   ├── n5_devui/
│   │   └── devui_server.py           ← 一次載入 9 個 entity 的 DevUI launcher
│   └── n6_deployment/
│       ├── hosted_agent.py           ← ResponsesHostServer（Step 5 容器入口）
│       └── hosted_agent_deployer.py  ← build + push + create_version 腳本
└── uv.lock
```

---

## 操作流程

下面 5 步是 **workshop 學員的主要動線**：Step 1 在 Foundry portal 手動建 4 個 Prompt Agent；
Step 2–3 在本機 DevUI 體驗 single agent 與 multi-agent 協作；Step 4 把整個 Handoff workflow 部署回 Foundry；
Step 5 把 hosted agent 進一步發布到 Microsoft Teams 頻道，讓 NOC 主管直接在 Teams 內提問。

### Step 1 — 建立 agents

> 這一步在 Foundry portal 上手動建立 4 個 Prompt Agent，把每個 agent「看到」一次，理解什麼是「server-managed agent」。
> 建好後同一份 workshop 程式可切到 hosted 模式（`NOA_USE_HOSTED_AGENTS=true`），
> 用同一份 instructions 而完全不改 client 端 code。

#### 為什麼要在 portal 建 agent？

1. **看見**：在 portal 把每個 agent「看到」一次，理解「server-managed agent」的概念。
2. **未來把更多動作搬上雲**：portal 的 Prompt Agent 可以直接掛 OpenAPI、知識庫、code interpreter，不用寫 Python。
3. **驗證 endpoint 通路**：完成 portal → SDK 的連通流程，往後做 production agent 都會用到。

#### 一步一步來（每個 agent 重複 4 次）

1. 進 [Foundry portal](https://ai.azure.com/) → 你的 project → 左側 **Agents**。
2. 按 **+ New agent**，type 選 **Prompt Agent**。
3. **Name** 欄填下表對應名稱（要跟 `.env` 對齊）。
4. **Model deployment** 選你 project 內的 chat model（建議 `gpt-4o`）。
5. **Instructions** 欄打開 [`src/noa_workshop/n1_agents/instructions/`](noa-workshop/src/noa_workshop/n1_agents/instructions/) 內對應的 markdown，全選整段貼進去。
6. **Tools** 欄留空（本 workshop 的 tool 由 Python 端注入；portal 不需要設）。
7. 按 **Create**。

| 順序 | Portal Agent Name     | 對應 instructions 檔     | `.env` 變數                  |
| ---- | --------------------- | ------------------------ | ---------------------------- |
| 1    | `noc-manager`         | `noc_manager.md`         | `NOA_NOC_MANAGER_AGENT_NAME` |
| 2    | `telemetry-analyzer`  | `telemetry_analyzer.md`  | `NOA_TELEMETRY_AGENT_NAME`   |
| 3    | `security-compliance` | `security_compliance.md` | `NOA_SECURITY_AGENT_NAME`    |
| 4    | `field-ops`           | `field_ops.md`           | `NOA_FIELD_OPS_AGENT_NAME`   |

#### 切換 SDK 到 hosted 模式（選用，本 workshop Step 2–3 不需要切）

```bash
# 在 .env 內把這行改成 true
NOA_USE_HOSTED_AGENTS=true
```

`agent_factory.py` 偵測到 `NOA_USE_HOSTED_AGENTS=true` 就會用 `FoundryAgent` 連到 portal 上你建好的 agent，
而不是用 markdown + Python tool 在本地組裝。

#### Hosted 模式注意事項

- **Hosted 模式下，Python `@tool` 不會被 portal agent 自動使用。** Portal agent 只看自己的 instructions。
- 因此 hosted 模式比較適合用來示範「endpoint 真的通」。完整的 tool-driven 體驗請留在 local 模式。
- DevUI 的 `Workflow_Handoff` 用了 structured-output（`response_format=RoutingPlan`），目前**只支援 local 模式**，請不要在 hosted 模式下跑它。

### Step 2 — Agent framework

> 這一步啟動本機 DevUI，跟 4 個 single agent 直接對話，理解 Microsoft Agent Framework 怎麼把 system prompt + Python `@tool` 組裝成可呼叫工具的 agent。

#### 啟動 DevUI

DevUI 是 Microsoft Agent Framework 內建的本機除錯介面，在瀏覽器看每個 agent / workflow 的執行軌跡、訊息流、節點圖。

```bash
cd noa-workshop
uv run python -m noa_workshop.n5_devui.devui_server
```

啟動後在瀏覽器開 **<http://localhost:8080>**。

> ⚠️ 一定要打 `localhost`，不是 `127.0.0.1`。DevUI 前端 bundle 的 fetch origin hardcode 了 `localhost:8080`，
> 用 IP 會吃 CORS。

啟動成功後左側 Entities 清單會看到 **9 個 entity**（Step 2 先用前 4 個 single agent；其餘 5 個 multi-agent 與 workflow 留到 Step 3）：

| 類別     | 名稱                       | 來源                                                                        |
| -------- | -------------------------- | --------------------------------------------------------------------------- |
| Agent    | `NOCManager`               | `n1_agents/single_agents.py`                                                |
| Agent    | `TelemetryAnalyzer`        | `n1_agents/single_agents.py`                                                |
| Agent    | `SecurityCompliance`       | `n1_agents/single_agents.py`                                                |
| Agent    | `FieldOps`                 | `n1_agents/single_agents.py`                                                |
| Agent    | `Orchestration_Sequential` | `n1_agents/orchestration_sequential.py`（`SequentialBuilder` → `as_agent`） |
| Agent    | `Orchestration_Handoff`    | `n1_agents/orchestration_handoff.py`（`HandoffBuilder` → `as_agent`）       |
| Agent    | `Orchestration_Magentic`   | `n1_agents/orchestration_magentic.py`（`MagenticBuilder` → `as_agent`）     |
| Workflow | `Workflow_Sequential`      | `n4_workflows/workflow_sequential.py`（顯式 `add_edge` graph）              |
| Workflow | `Workflow_Handoff`         | `n4_workflows/workflow_handoff.py`（顯式 graph + HITL approval）            |

#### 與 4 個 single agent 互動（理解每個 agent 的 RACI）

從 DevUI Entities 清單選下面任何一個 agent，輸入訊息開始對話。

| Agent                | 試試這樣問                                                                       |
| -------------------- | -------------------------------------------------------------------------------- |
| `NOCManager`         | 「north-transport-ring 出現 P1，請幫我規劃處理流程」（純協調，不會自己查資料）   |
| `TelemetryAnalyzer`  | 「north-transport-ring 區域過去 30 分鐘 packet_loss_pct 跟 baseline 比怎麼樣？」 |
| `SecurityCompliance` | 「14:10 出現的 SIG-BOT-2104 簽章是什麼來頭？」                                   |
| `FieldOps`           | 「north-transport-ring 附近有沒有可派的光纖技師？」                              |

> 💡 在 DevUI 內可以同時開多個分頁分別跟 4 個 single agent 對話，自己手動模擬一輪 multi-agent 協作；
> 接著進到 Step 3，看 framework 怎麼幫你把它們自動串起來——這對理解 orchestration 的價值很有感。

### Step 3 — multiagent 協作

> 把 Step 2 的 4 個 single agent 串起來，比較 Microsoft Agent Framework 三種 orchestration 模式（Sequential / Handoff / Magentic）跟兩種顯式 Workflow（含 HITL approval）的差異。

#### 試 3 個 multi-agent orchestration（觀察協作）

從 DevUI Entities 清單選下面任一 orchestration agent，觀察 NOC Manager 怎麼把任務分派給 3 位專家、最後再彙整摘要。

| 模式                       | 試試這樣問                                                                                      |
| -------------------------- | ----------------------------------------------------------------------------------------------- |
| `Orchestration_Sequential` | 「north-transport-ring 出現 P1 告警，請依序確認 KPI、判斷是否安全事件、需要派工就草擬派工建議」 |
| `Orchestration_Handoff`    | 同上。NOC Manager 會挑要呼叫哪些專家，跑完才總結                                                |
| `Orchestration_Magentic`   | 切換到場景 C：「CORE-POP1-EDGE 14:10 出現異常南向流量 + SIG-BOT-2104，這是不是安全事件？」      |

#### 在 Workflow 類別觀察 graph 與 HITL

DevUI Workflow 類別與 Agent 類別最大的差別：**會畫出 workflow 的 graph 拓樸**，可以一邊跑、一邊看訊息在哪個 executor、走哪條 edge。

| Workflow              | 觀察重點                                                                                                                                                                                    |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Workflow_Sequential` | Telemetry → Security → FieldOps 線性管線；當 Security 判定「是安全事件」時走 escalation 分支終止，否則才走到 FieldOps。觀察條件 edge 的綠 / 紅顏色                                          |
| `Workflow_Handoff`    | NOC Manager 一次性 routing → 條件式 fan-out / fan-in；**最重要的是 HITL 審批**：FieldOps 呼叫 `create_dispatch_request` 時 workflow 會凍結，DevUI 跳出 approval 提示，按 **Approve** 才繼續 |

> 💡 HITL 是**安全網**而非阻礙。只在「不可逆的真實世界動作」上加 approval（派工、出單、寫資料庫）。
> 如要看 NOC manager 在被拒絕後會怎麼回，按 **Reject** 觀察它怎麼放棄派工、改寫摘要。

### Step 4 — 部署到 Foundry

> 把 Step 3 玩過的 `Orchestration_Handoff` 包成容器，用 Foundry hosted agent 部署到雲上，
> 之後外部 app 就能用標準 OpenAI Responses 協定打它。

部署的三個關鍵檔：

| 檔案                                                                                                                              | 角色                                                                             |
| --------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| [`Dockerfile`](noa-workshop/Dockerfile)                                                                                           | 把 workshop 包成 `linux/amd64` 容器，`CMD` 啟動 `hosted_agent`                   |
| [`agent.manifest.yaml`](noa-workshop/agent.manifest.yaml)                                                                         | `azd` / Foundry hosted-agent 部署清單，宣告 entrypoint 與環境變數                |
| [`src/noa_workshop/n6_deployment/hosted_agent_deployer.py`](noa-workshop/src/noa_workshop/n6_deployment/hosted_agent_deployer.py) | 一行命令完成「build → ACR push → `create_version` → 等到 `active` → smoke test」 |

#### 一鍵部署

```bash
cd noa-workshop
uv run python -m noa_workshop.n6_deployment.hosted_agent_deployer
```

腳本會做這些事（依序）：

1. `az acr build`（cloud-side build）把 image 推到 Foundry 配對的 ACR
2. `AIProjectClient.agents.create_version(...)` 註冊一個 hosted agent 版本
3. 輪詢直到 `status == 'active'`
4. 用 `project.get_openai_client(agent_name=...)` 對它呼一次 Responses API 做 smoke test（送 `SCENARIO_A_PROMPT`）

部署成功後，整個 multi-agent Handoff workflow 變成 Foundry 上**一個 hosted agent**，
可以在 portal 直接呼叫，也可以從外部 app 用 OpenAI Responses 協定打。

### Step 5 — 發布到 Teams

> 把 Step 4 部署的 Foundry hosted agent 透過 portal 發布到 Microsoft Teams 頻道，
> NOC 主管之後就能直接在 Teams 內 @ 它問問題，不必再進 portal 或本機 DevUI。

> 📝 整體做法：在 Foundry portal 打開 Step 4 部署的 hosted agent → 設定 Microsoft Teams channel → 授權 Teams 連線並選擇要發布的 Team / Channel → 回到 Teams 對應頻道 @ agent，輸入跟 DevUI 同樣的問題（例如 `SCENARIO_A_PROMPT`），驗證回覆與本機一致。

---

## 快速上手

跑這四步，你會得到一個能呼叫工具、回應 KPI 異常的 telemetry agent，代表整個環境就緒。

```bash
# 1. 進入專案資料夾並安裝相依套件
cd noa-workshop
uv sync

# 2. 複製並編輯環境變數
cp .env.example .env
# 編輯 .env：填入 FOUNDRY_PROJECT_ENDPOINT 與 AZURE_AI_MODEL_DEPLOYMENT_NAME

# 3. 確認 Azure CLI 已登入
az login
az account show

# 4. 跑 smoke test：驗證 endpoint 通路 + 第一個 agent + tool 能跑
uv run python -m noa_workshop.smoke_test
```

`smoke_test.py` 會建一個綁了 `query_kpi_metrics` 的 telemetry agent，問它「north-transport-ring 過去 30 分鐘的 packet_loss_pct 是不是異常？」，看到表格化回覆代表全部就緒。

---

## 參考資料

### 🧭 入門概念：NOA 是什麼

1. [Microsoft NOA Framework v1](https://techcommunity.microsoft.com/blog/telecommunications-industry-blog/introducing-microsoft%E2%80%99s-network-operations-agent-%E2%80%93-a-telco-framework-for-autonom/4471185) — NOA 框架首發介紹
2. [Microsoft NOA Framework v2 演進](https://techcommunity.microsoft.com/blog/telecommunications-industry-blog/evolving-the-network-operations-agent-framework-driving-the-next-wave-of-autonom/4496607) — v2 的最新演進

### 🛠️ 技術基礎：Microsoft Agent Framework

1. [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) — Multi-agent 開源框架（OpenTelemetry / MCP / A2A）
2. [Microsoft Agent Framework SDK (Python) 總覽](https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-python) — 框架入口
3. [Microsoft Agent Framework — Workflows](https://learn.microsoft.com/agent-framework/workflows/) — Workflow 概念與用法

### 🔀 進階：三種 Orchestration 模式

1. [Sequential Orchestration (Python)](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/sequential?pivots=programming-language-python) — 線性串接
2. [Handoff Orchestration (Python)](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/handoff?pivots=programming-language-python) — 由協調者分派
3. [Magentic Orchestration (Python)](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/magentic?pivots=programming-language-python) — 動態規劃

### ☁️ 部署：Microsoft Foundry Hosted Agent

1. [Microsoft Foundry Agents 總覽](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) — Foundry agent 服務介紹
2. [Foundry Hosted Agents（概念）](https://learn.microsoft.com/agent-framework/hosting/foundry-hosted-agent) — Hosted agent 架構
3. [Foundry Quickstart: Hosted Agent (azd)](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-hosted-agent?pivots=azd) — 用 `azd` 快速部署

### 💻 範例程式碼（GitHub）

1. [Agent Framework sample: DevUI](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/devui) — DevUI 官方範例
2. [Agent Framework sample: foundry-hosted-agents](https://github.com/microsoft/agent-framework/tree/main/python/samples/04-hosting/foundry-hosted-agents) — Hosted agent 官方範例

---

Happy coding 💜
