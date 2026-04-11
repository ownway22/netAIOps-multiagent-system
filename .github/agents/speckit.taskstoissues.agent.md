---
description: 根據可用的設計產出文件，將現有任務轉換為可執行、相依性排序的 GitHub issues。
tools: ['github/github-mcp-server/issue_write']
---

## 使用者輸入

```text
$ARGUMENTS
```

您**必須**在繼續之前考慮使用者輸入（如果非空）。

## 大綱

1. 從儲存庫根目錄執行 `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`，並解析 FEATURE_DIR 和 AVAILABLE_DOCS 清單。所有路徑必須是絕對路徑。對於參數中的單引號如 "I'm Groot"，使用跳脫語法：例如 'I'\''m Groot'（或盡可能使用雙引號："I'm Groot"）。
1. 從執行的腳本中，提取 **tasks** 的路徑。
1. 執行以下命令取得 Git 遠端：

```bash
git config --get remote.origin.url
```

> [!CAUTION]
> 僅當遠端是 GITHUB URL 時才繼續執行下一步驟

1. 對於清單中的每個任務，使用 GitHub MCP 伺服器在代表 Git 遠端的儲存庫中建立新的 issue。

> [!CAUTION]
> 在任何情況下都絕對不要在與遠端 URL 不符的儲存庫中建立 issues
