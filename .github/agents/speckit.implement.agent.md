---
description: 透過處理和執行 tasks.md 中定義的所有任務來執行實作計畫
---

## 使用者輸入

```text
$ARGUMENTS
```

在繼續之前，您**必須**考慮使用者輸入（如果不為空）。

## 大綱

1. 從儲存庫根目錄執行 `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` 並解析 FEATURE_DIR 和 AVAILABLE_DOCS 列表。所有路徑必須是絕對路徑。對於參數中的單引號，如 "I'm Groot"，使用跳脫語法：例如 'I'\''m Groot'（或如果可以的話使用雙引號："I'm Groot"）。

2. **檢查檢核清單狀態**（如果 FEATURE_DIR/checklists/ 存在）：
   - 掃描 checklists/ 目錄中的所有檢核清單檔案
   - 對於每個檢核清單，計算：
     - 總項目數：所有符合 `- [ ]` 或 `- [X]` 或 `- [x]` 的行
     - 已完成項目：符合 `- [X]` 或 `- [x]` 的行
     - 未完成項目：符合 `- [ ]` 的行
   - 建立狀態表：

     ```text
     | 檢核清單 | 總計 | 已完成 | 未完成 | 狀態 |
     |----------|------|--------|--------|------|
     | ux.md     | 12    | 12        | 0          | ✓ 通過 |
     | test.md   | 8     | 5         | 3          | ✗ 失敗 |
     | security.md | 6   | 6         | 0          | ✓ 通過 |
     ```

   - 計算整體狀態：
     - **通過 (PASS)**：所有檢核清單都有 0 個未完成項目
     - **失敗 (FAIL)**：一個或多個檢核清單有未完成項目

   - **如果任何檢核清單未完成**：
     - 顯示包含未完成項目計數的表格
     - **停止**並詢問：「部分檢核清單未完成。您是否仍要繼續實作？（yes/no）」
     - 等待使用者回應後再繼續
     - 如果使用者說「no」或「wait」或「stop」，則停止執行
     - 如果使用者說「yes」或「proceed」或「continue」，則繼續執行步驟 3

   - **如果所有檢核清單都已完成**：
     - 顯示所有檢核清單都通過的表格
     - 自動繼續執行步驟 3

3. 載入並分析實作情境：
   - **必要**：讀取 tasks.md 以取得完整的任務清單和執行計畫
   - **必要**：讀取 plan.md 以取得技術堆疊、架構和檔案結構
   - **如果存在**：讀取 data-model.md 以取得實體和關係
   - **如果存在**：讀取 contracts/ 以取得 API 規格和測試需求
   - **如果存在**：讀取 research.md 以取得技術決策和約束條件
   - **如果存在**：讀取 quickstart.md 以取得整合情境

4. **專案設置驗證**：
   - **必要**：根據實際專案設置建立/驗證忽略檔案：

   **偵測與建立邏輯**：
   - 檢查以下指令是否成功以判斷儲存庫是否為 git 儲存庫（如果是則建立/驗證 .gitignore）：

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - 檢查 Dockerfile* 是否存在或 plan.md 中有 Docker → 建立/驗證 .dockerignore
   - 檢查 .eslintrc* 是否存在 → 建立/驗證 .eslintignore
   - 檢查 eslint.config.* 是否存在 → 確保設定的 `ignores` 項目涵蓋所需模式
   - 檢查 .prettierrc* 是否存在 → 建立/驗證 .prettierignore
   - 檢查 .npmrc 或 package.json 是否存在 → 建立/驗證 .npmignore（如果發布）
   - 檢查 terraform 檔案 (*.tf) 是否存在 → 建立/驗證 .terraformignore
   - 檢查是否需要 .helmignore（存在 helm charts）→ 建立/驗證 .helmignore

   **如果忽略檔案已存在**：驗證它包含必要模式，僅附加缺少的關鍵模式
   **如果忽略檔案遺失**：使用偵測到技術的完整模式集建立

   **依技術的常見模式**（來自 plan.md 技術堆疊）：
   - **Node.js/JavaScript/TypeScript**：`node_modules/`、`dist/`、`build/`、`*.log`、`.env*`
   - **Python**：`__pycache__/`、`*.pyc`、`.venv/`、`venv/`、`dist/`、`*.egg-info/`
   - **Java**：`target/`、`*.class`、`*.jar`、`.gradle/`、`build/`
   - **C#/.NET**：`bin/`、`obj/`、`*.user`、`*.suo`、`packages/`
   - **Go**：`*.exe`、`*.test`、`vendor/`、`*.out`
   - **Ruby**：`.bundle/`、`log/`、`tmp/`、`*.gem`、`vendor/bundle/`
   - **PHP**：`vendor/`、`*.log`、`*.cache`、`*.env`
   - **Rust**：`target/`、`debug/`、`release/`、`*.rs.bk`、`*.rlib`、`*.prof*`、`.idea/`、`*.log`、`.env*`
   - **Kotlin**：`build/`、`out/`、`.gradle/`、`.idea/`、`*.class`、`*.jar`、`*.iml`、`*.log`、`.env*`
   - **C++**：`build/`、`bin/`、`obj/`、`out/`、`*.o`、`*.so`、`*.a`、`*.exe`、`*.dll`、`.idea/`、`*.log`、`.env*`
   - **C**：`build/`、`bin/`、`obj/`、`out/`、`*.o`、`*.a`、`*.so`、`*.exe`、`Makefile`、`config.log`、`.idea/`、`*.log`、`.env*`
   - **Swift**：`.build/`、`DerivedData/`、`*.swiftpm/`、`Packages/`
   - **R**：`.Rproj.user/`、`.Rhistory`、`.RData`、`.Ruserdata`、`*.Rproj`、`packrat/`、`renv/`
   - **通用**：`.DS_Store`、`Thumbs.db`、`*.tmp`、`*.swp`、`.vscode/`、`.idea/`

   **工具特定模式**：
   - **Docker**：`node_modules/`、`.git/`、`Dockerfile*`、`.dockerignore`、`*.log*`、`.env*`、`coverage/`
   - **ESLint**：`node_modules/`、`dist/`、`build/`、`coverage/`、`*.min.js`
   - **Prettier**：`node_modules/`、`dist/`、`build/`、`coverage/`、`package-lock.json`、`yarn.lock`、`pnpm-lock.yaml`
   - **Terraform**：`.terraform/`、`*.tfstate*`、`*.tfvars`、`.terraform.lock.hcl`
   - **Kubernetes/k8s**：`*.secret.yaml`、`secrets/`、`.kube/`、`kubeconfig*`、`*.key`、`*.crt`

5. 解析 tasks.md 結構並擷取：
   - **任務階段**：設置、測試、核心、整合、收尾
   - **任務相依性**：循序 vs 平行執行規則
   - **任務細節**：ID、描述、檔案路徑、平行標記 [P]
   - **執行流程**：順序和相依性需求

6. 依任務計畫執行實作：
   - **逐階段執行**：在移至下一階段前完成每個階段
   - **尊重相依性**：依序執行循序任務，平行任務 [P] 可同時執行  
   - **遵循測試驅動開發 (TDD) 方法**：在對應的實作任務之前執行測試任務
   - **基於檔案的協調**：影響相同檔案的任務必須循序執行
   - **驗證檢查點**：在繼續之前驗證每個階段完成

7. 實作執行規則：
   - **設置優先**：初始化專案結構、相依套件、設定
   - **程式碼前先測試**：如果需要為契約、實體和整合情境撰寫測試
   - **核心開發**：實作模型、服務、命令列介面 (CLI) 指令、端點
   - **整合工作**：資料庫連線、中介軟體、日誌記錄、外部服務
   - **收尾和驗證**：單元測試、效能最佳化、文件

8. 進度追蹤和錯誤處理：
   - 每個完成的任務後報告進度
   - 如果任何非平行任務失敗則停止執行
   - 對於平行任務 [P]，繼續執行成功的任務，報告失敗的任務
   - 提供包含除錯情境的清楚錯誤訊息
   - 如果實作無法繼續則建議後續步驟
   - **重要** 對於已完成的任務，確保在 tasks 檔案中將任務標記為 [X]。

9. 完成驗證：
   - 驗證所有必要任務已完成
   - 檢查實作的功能是否符合原始規格
   - 驗證測試通過且涵蓋率符合需求
   - 確認實作遵循技術計畫
   - 報告最終狀態與已完成工作的摘要

備註：此指令假設 tasks.md 中存在完整的任務分解。如果任務不完整或遺失，建議先執行 `/speckit.tasks` 重新產生任務清單。
