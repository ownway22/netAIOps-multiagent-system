---
applyTo: "**"
---

# Copilot 全域指引

## 專案資訊
- 專案名稱：{{PROJECT_NAME}}

## 程式碼風格
- 使用清晰、有意義的變數與函式命名
- 優先使用組合（composition）而非繼承（inheritance）
- 遵循 DRY（Don't Repeat Yourself）原則
- 保持函式短小，每個函式只做一件事

## 回應語言
- 使用繁體中文回應
- 程式碼中的註解使用英文
- commit message 使用英文，遵循 Conventional Commits 格式

## 安全性
- 不在程式碼中硬編碼任何密鑰、密碼或敏感資訊
- 使用環境變數或密鑰管理工具存放敏感設定
- 遵循 OWASP Top 10 安全最佳實踐

## 測試
- 為新功能撰寫對應的單元測試
- 測試命名格式：`test_<功能描述>_<預期結果>`
