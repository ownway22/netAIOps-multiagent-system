````skill
---
name: microsoft-docs
description: 查詢官方 Microsoft 文件以瞭解概念、尋找教學課程，以及學習服務的運作方式。適用於 Azure、.NET、Microsoft 365、Windows、Power Platform 及所有 Microsoft 技術。從 learn.microsoft.com 及其他官方 Microsoft 網站取得準確且即時的資訊——包括架構概覽、快速入門、組態指南、限制與最佳實務。
compatibility: 需要 Microsoft Learn MCP 伺服器 (https://learn.microsoft.com/api/mcp)
---

# Microsoft 文件

## 工具

| 工具                    | 用途                                                       |
| ----------------------- | ---------------------------------------------------------- |
| `microsoft_docs_search` | 搜尋文件——概念、指南、教學課程、組態設定                     |
| `microsoft_docs_fetch`  | 取得完整頁面內容（當搜尋摘錄不足時）                        |

## 何時使用

- **瞭解概念** — 「Cosmos DB 的分割區如何運作？」
- **學習服務** — 「Azure Functions 概覽」、「Container Apps 架構」
- **尋找教學課程** — 「快速入門」、「入門指南」、「逐步教學」
- **組態選項** — 「App Service 組態設定」
- **限制與配額** — 「Azure OpenAI 速率限制」、「Service Bus 配額」
- **最佳實務** — 「Azure 安全性最佳實務」

## 查詢效果

好的查詢要具體明確：

```
# ❌ 太廣泛
"Azure Functions"

# ✅ 具體明確
"Azure Functions Python v2 programming model"
"Cosmos DB partition key design best practices"
"Container Apps scaling rules KEDA"
```

包含相關上下文：

- **版本**：如有相關（`.NET 8`、`EF Core 8`）
- **任務意圖**：（`quickstart`、`tutorial`、`overview`、`limits`）
- **平台**：適用於多平台文件（`Linux`、`Windows`）

## 何時擷取完整頁面

搜尋後在以下情況擷取：

- **教學課程** — 需要完整的逐步操作說明
- **組態指南** — 需要列出所有選項
- **深入探討** — 使用者需要全面的內容涵蓋
- **搜尋摘錄被截斷** — 需要完整上下文

## 為何使用此工具

- **準確性** — 即時文件，而非可能過時的訓練資料
- **完整性** — 教學課程包含所有步驟，而非片段
- **權威性** — 官方 Microsoft 文件

````
