# Copilot 指令

## 專案概述

這是一個使用 Next.js（App Router）搭配 PostgreSQL 資料庫的全端 TypeScript 應用程式。

- **前端**：React 19 + Next.js 15（App Router）+ Tailwind CSS 4
- **後端**：Next.js API Routes + Drizzle ORM
- **資料庫**：PostgreSQL 16
- **測試**：Vitest（單元測試）+ Playwright（端對端測試）
- **套件管理工具**：pnpm

## 專業技能調用規則

本專案在 `.github/skills/` 目錄下定義了特定任務的標準作業程序 (SOP)。
在執行以下任務前，請務必先參考對應的技能檔案，並遵循其中的規範。

| 技能                 | 適用時機                                                                                                                                                                                                                                               | 技能檔案路徑                               |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------ |
| **Azure DevOps CLI** | 透過 CLI 管理 Azure DevOps 資源（專案、存放庫、管線、建置、提取要求、工作項目、成品、服務端點）。當使用者提及 Azure DevOps、`az devops` 指令、DevOps 自動化或 CI/CD 時觸發。                                                                           | `.github/skills/azure-devops-cli/SKILL.md` |
| **Copilot SDK**      | 使用 GitHub Copilot SDK 建構代理式應用程式。適用於在應用程式中嵌入 AI 代理、建立自訂工具、實作串流回應、管理工作階段、連線至 MCP 伺服器或建立自訂代理。觸發關鍵字：Copilot SDK、GitHub SDK、代理式應用程式、嵌入 Copilot、可程式化代理。               | `.github/skills/copilot-sdk/SKILL.md`      |
| **GitHub CLI (gh)**  | 從命令列操作 GitHub 資源，包括存放庫、議題、提取要求、Actions、專案、發行版本、Gist、Codespace、組織及擴充功能管理。當使用者需要執行 `gh` 指令或從終端機操作 GitHub 時觸發。                                                                           | `.github/skills/gh-cli/SKILL.md`           |
| **Git Commit**       | 執行 git commit 搭配約定式提交訊息。當使用者要求提交變更、建立 git commit 或提及 `/commit` 時使用。支援：從變更自動偵測類型與範圍、從 diff 產生約定式提交訊息、智慧檔案暫存以進行邏輯分組。                                                            | `.github/skills/git-commit/SKILL.md`       |
| **Microsoft 文件**   | 查詢官方 Microsoft 文件以瞭解概念、尋找教學課程及學習服務。適用於 Azure、.NET、Microsoft 365、Windows、Power Platform 及所有 Microsoft 技術。當需要從 learn.microsoft.com 取得準確且即時的資訊（架構概覽、快速入門、組態指南、限制與最佳實務）時觸發。 | `.github/skills/microsoft-docs/SKILL.md`   |

當我提出的需求涉及上述領域時，請明確表示你已閱讀該技能檔案，並遵循其中的規範。

## 程式碼風格與慣例

### 通用規則

- 始終使用 TypeScript 嚴格模式。**絕對不要使用 `any`** — 請改用 `unknown` 搭配型別收窄（type narrowing）。
- 優先使用 `const`，其次才是 `let`。禁止使用 `var`。
- 使用具名匯出（named export），不使用預設匯出（default export）（Next.js 的頁面與佈局元件除外）。
- 單一檔案最大行數：300 行。超過請重構拆分為較小的模組。
- 使用 `@/` 別名進行絕對路徑匯入（例如 `import { Button } from "@/components/ui/button"`）。

### 命名慣例

| 項目             | 慣例            | 範例                    |
| ---------------- | --------------- | ----------------------- |
| 變數 / 函式      | camelCase       | `getUserById`           |
| 元件             | PascalCase      | `UserProfileCard`       |
| 型別 / 介面      | PascalCase      | `UserProfile`           |
| 常數             | SCREAMING_SNAKE | `MAX_RETRY_COUNT`       |
| 檔案（元件）     | kebab-case      | `user-profile-card.tsx` |
| 檔案（工具函式） | kebab-case      | `format-date.ts`        |
| 資料庫資料表     | snake_case      | `user_profiles`         |
| 環境變數         | SCREAMING_SNAKE | `DATABASE_URL`          |

### React 與 Next.js

- 使用函式元件搭配 Hooks。**禁止使用 class 元件。**
- 預設使用伺服器元件（Server Components）。只有在需要互動、瀏覽器 API 或 `useState` / `useEffect` 等 Hooks 時，才加上 `"use client"`。
- 表單處理請使用 `useActionState`（不要使用已棄用的 `useFormState`）。
- 元件檔案就近放置：`components/user-card/user-card.tsx`、`components/user-card/user-card.test.tsx`。
- 可重複使用的邏輯請抽取為自訂 Hook，放在 `src/hooks/` 目錄下。

### API 與資料取得

- 所有 API 呼叫一律透過 `src/lib/api-client.ts` 中的用戶端發送。**禁止直接使用原生 `fetch`。**
- 使用 `zod` 驗證所有請求與回應的結構描述（schema）。Schema 檔案放在 `src/schemas/` 目錄。
- 資料庫查詢放在 `src/db/queries/`，每個領域實體一個檔案（例如 `users.ts`、`orders.ts`）。
- Server Actions 放在對應功能資料夾中的 `actions.ts` 檔案內。

### 錯誤處理

- 所有應用程式錯誤一律使用 `src/lib/errors.ts` 中的自訂 `AppError` 類別。
- 務必明確處理錯誤 — 禁止空的 `catch` 區塊。
- API 路由必須回傳統一的錯誤格式：`{ error: { code: string, message: string } }`。
- 使用 `src/lib/logger.ts` 進行結構化日誌記錄。

### 測試

- 單元測試與整合測試使用 Vitest。
- 遵循 AAA 模式：**準備（Arrange）→ 執行（Act）→ 斷言（Assert）**。
- 測試檔案命名：`*.test.ts` 或 `*.test.tsx`，與原始碼就近放置。
- 模擬（mock）外部相依套件，但不要模擬內部商業邏輯。
- 最低覆蓋率目標：`src/lib/` 與 `src/db/queries/` 中的商業邏輯達 80%。

### 樣式

- 使用 Tailwind CSS 工具類別。**除非萬不得已，否則不要撰寫自訂 CSS。**
- 遵循行動裝置優先（mobile-first）的響應式設計：先寫基本樣式，再依序加上 `sm:`、`md:`、`lg:` 中斷點。
- 使用 `tailwind.config.ts` 中定義的設計代碼（design tokens），包括顏色、間距、字型。避免使用任意值如 `text-[13px]` — 請改為擴充設定檔。

### Git 提交訊息

使用約定式提交（Conventional Commits）格式：

```
<類型>(<範圍>): <描述>

# 範例：
feat(auth): 新增 Google OAuth 登入流程
fix(orders): 修復結帳時的競態條件
refactor(db): 從 Prisma 遷移至 Drizzle ORM
docs(readme): 更新本機開發環境設定說明
```

類型：`feat`、`fix`、`refactor`、`docs`、`test`、`chore`、`perf`、`ci`

### 資安

- 絕對不要在程式碼中寫死密鑰或 API 金鑰。請透過 `src/lib/env.ts`（使用 `zod` 驗證）存取環境變數。
- 在伺服器端清理（sanitize）所有使用者輸入。
- 使用參數化查詢（Drizzle 已內建支援）— 絕對不要用字串串接組合 SQL。
- `"use server"` 指令僅放在 Server Action 檔案的最頂端，不要在函式內部行內使用。

### 禁止事項

- 安裝新套件前，先確認現有套件是否已能滿足需求。
- 不要使用 `// @ts-ignore` 或 `// @ts-expect-error`，除非附上註解說明原因。
- 禁止在已提交的程式碼中使用 `console.log` 除錯 — 請使用 logger。
- 不要把商業邏輯寫在 React 元件中 — 請抽取至 `src/lib/` 或 `src/services/`。
- 不要使用 `useEffect` 來取得資料 — 請改用伺服器元件或 React Query。
