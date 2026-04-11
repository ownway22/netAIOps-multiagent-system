---
description: "產生符合 Conventional Commits 格式的 commit message"
mode: "ask"
---

# 產生 Commit Message

請根據目前的 git diff 變更內容，產生符合 [Conventional Commits](https://www.conventionalcommits.org/) 格式的 commit message。

## 格式

```
<type>(<scope>): <subject>

<body>
```

## Type 類型
- `feat`: 新功能
- `fix`: 修復 bug
- `docs`: 文件變更
- `style`: 格式調整（不影響邏輯）
- `refactor`: 重構（非新功能或修復）
- `test`: 測試相關
- `chore`: 建置或輔助工具變更

## 規則
- subject 使用英文、小寫開頭、不加句號
- body 說明「為什麼」而非「做了什麼」
- 如有 breaking change，加上 `BREAKING CHANGE:` footer
