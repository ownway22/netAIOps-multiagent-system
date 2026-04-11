````skill
---
name: git-commit
description: '執行 git commit，搭配約定式提交訊息分析、智慧暫存及訊息產生功能。當使用者要求提交變更、建立 git commit 或提及「/commit」時使用。支援：(1) 從變更自動偵測類型與範圍，(2) 從 diff 產生約定式提交訊息，(3) 可選擇覆寫類型/範圍/描述的互動式提交，(4) 智慧檔案暫存以進行邏輯分組'
license: MIT
allowed-tools: Bash
---

# 使用約定式提交（Conventional Commits）進行 Git 提交

## 概述

使用約定式提交規範建立標準化、語意化的 git 提交。分析實際的 diff 以判斷適當的類型、範圍和訊息。

## 約定式提交格式

```
<類型>[可選的範圍]: <描述>

[可選的內文]

[可選的頁尾]
```

## 提交類型

| 類型       | 用途                           |
| ---------- | ------------------------------ |
| `feat`     | 新功能                         |
| `fix`      | 錯誤修復                       |
| `docs`     | 僅文件變更                     |
| `style`    | 格式/樣式（不影響邏輯）        |
| `refactor` | 程式碼重構（非功能/修復）      |
| `perf`     | 效能改善                       |
| `test`     | 新增/更新測試                  |
| `build`    | 建置系統/相依套件              |
| `ci`       | CI/組態變更                    |
| `chore`    | 維護/雜項                      |
| `revert`   | 還原提交                       |

## 破壞性變更

```
# 在類型/範圍後加上驚嘆號
feat!: remove deprecated endpoint

# BREAKING CHANGE 頁尾
feat: allow config to extend other configs

BREAKING CHANGE: `extends` key behavior changed
```

## 工作流程

### 1. 分析 Diff

```bash
# 如果檔案已暫存，使用暫存區的 diff
git diff --staged

# 如果沒有暫存，使用工作目錄的 diff
git diff

# 同時檢查狀態
git status --porcelain
```

### 2. 暫存檔案（如有需要）

如果沒有已暫存的檔案，或想以不同方式分組變更：

```bash
# 暫存特定檔案
git add path/to/file1 path/to/file2

# 依模式暫存
git add *.test.*
git add src/components/*

# 互動式暫存
git add -p
```

**絕對不要提交機密資訊**（.env、credentials.json、私密金鑰）。

### 3. 產生提交訊息

分析 diff 以判斷：

- **類型**：這是什麼類型的變更？
- **範圍**：影響哪個區域/模組？
- **描述**：一行摘要說明變更內容（現在式、祈使語氣、少於 72 個字元）

### 4. 執行提交

```bash
# 單行
git commit -m "<類型>[範圍]: <描述>"

# 多行（包含內文/頁尾）
git commit -m "$(cat <<'EOF'
<類型>[範圍]: <描述>

<可選的內文>

<可選的頁尾>
EOF
)"
```

## 最佳實務

- 每次提交只包含一個邏輯變更
- 使用現在式：「add」而非「added」
- 使用祈使語氣：「fix bug」而非「fixes bug」
- 引用議題：`Closes #123`、`Refs #456`
- 描述保持在 72 個字元以內

## Git 安全規範

- 絕對不要更新 git config
- 未經明確要求，絕對不要執行破壞性指令（--force、hard reset）
- 除非使用者要求，絕對不要跳過 hooks（--no-verify）
- 絕對不要 force push 到 main/master
- 如果提交因 hooks 失敗，修復後建立新的提交（不要 amend）

````
