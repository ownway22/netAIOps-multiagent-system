---
description: 使用計畫範本執行實作規劃工作流程以產生設計產出文件。
handoffs: 
  - label: 建立任務
    agent: speckit.tasks
    prompt: 將計畫分解為任務
    send: true
  - label: 建立檢核清單
    agent: speckit.checklist
    prompt: 為以下領域建立檢核清單...
---

## 使用者輸入

```text
$ARGUMENTS
```

在繼續之前，您**必須**考慮使用者輸入（如果不為空）。

## 大綱

1. **設置**：從儲存庫根目錄執行 `.specify/scripts/bash/setup-plan.sh --json` 並解析 JSON 以取得 FEATURE_SPEC、IMPL_PLAN、SPECS_DIR、BRANCH。對於參數中的單引號，如 "I'm Groot"，使用跳脫語法：例如 'I'\''m Groot'（或如果可以的話使用雙引號："I'm Groot"）。

2. **載入情境**：讀取 FEATURE_SPEC 和 `.specify/memory/constitution.md`。載入 IMPL_PLAN 範本（已複製）。

3. **執行計畫工作流程**：遵循 IMPL_PLAN 範本中的結構來：
   - 填寫技術情境（將未知項目標記為「需要釐清」）
   - 從憲章填寫憲章檢查區段
   - 評估關卡（如果違規未說明理由則 ERROR）
   - 階段 0：產生 research.md（解決所有「需要釐清」）
   - 階段 1：產生 data-model.md、contracts/、quickstart.md
   - 階段 1：透過執行代理程式腳本更新代理程式情境
   - 設計後重新評估憲章檢查

4. **停止並報告**：指令在階段 2 規劃後結束。報告分支、IMPL_PLAN 路徑和產生的產出文件。

## 階段

### 階段 0：大綱與研究

1. **從上方的技術情境擷取未知項目**：
   - 每個「需要釐清」→ 研究任務
   - 每個相依套件 → 最佳實務任務
   - 每個整合 → 模式任務

2. **產生並派遣研究代理程式**：

   ```text
   對於技術情境中的每個未知項目：
     任務："為 {功能情境} 研究 {未知項目}"
   對於每個技術選擇：
     任務："尋找 {領域} 中 {技術} 的最佳實務"
   ```

3. **在 `research.md` 中整合發現**，使用格式：
   - 決策：[選擇了什麼]
   - 理由：[為何選擇]
   - 考慮的替代方案：[還評估了什麼]

**輸出**：已解決所有「需要釐清」的 research.md

### 階段 1：設計與契約

**先決條件**：`research.md` 完成

1. **從功能規格擷取實體** → `data-model.md`：
   - 實體名稱、欄位、關係
   - 來自需求的驗證規則
   - 狀態轉換（如適用）

2. **從功能性需求產生 API 契約**：
   - 每個使用者動作 → 端點
   - 使用標準 REST/GraphQL 模式
   - 將 OpenAPI/GraphQL 結構輸出到 `/contracts/`

3. **代理程式情境更新**：
   - 執行 `.specify/scripts/bash/update-agent-context.sh copilot`
   - 這些腳本偵測正在使用哪個 AI 代理程式
   - 更新適當的代理程式特定情境檔案
   - 僅從目前計畫新增新技術
   - 在標記之間保留手動新增的內容

**輸出**：data-model.md、/contracts/*、quickstart.md、代理程式特定檔案

## 關鍵規則

- 使用絕對路徑
- 關卡失敗或未解決的釐清時 ERROR
