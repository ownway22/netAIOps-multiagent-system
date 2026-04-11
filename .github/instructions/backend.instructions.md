---
applyTo: '**/api/**,**/server.*,**/routes/**,**/controllers/**,**/services/**,**/middleware/**'
---

# 後端開發規範

## 架構

- 遵循**分層架構**：路由（Routes）→ 控制器（Controllers）→ 服務層（Services）→ 資料存取層（Repositories）。
- 控制器保持精簡 — 商業邏輯應放在**服務層**。
- 每個檔案單一職責，檔案不超過 **250 行**。

## API 設計

- 遵循 **RESTful** 慣例，資源命名保持一致。
- 使用適當的 HTTP 方法與狀態碼：

| 方法     | 用途           | 成功狀態碼   |
|----------|----------------|--------------|
| `GET`    | 查詢           | `200`        |
| `POST`   | 新增           | `201`        |
| `PUT`    | 完整更新       | `200`        |
| `PATCH`  | 部分更新       | `200`        |
| `DELETE` | 刪除           | `204`        |

- 回傳一致的 JSON 回應格式：

```json
{
  "data": { },
  "message": "Success",
  "timestamp": "2026-01-01T00:00:00Z"
}
```

## 錯誤處理

- 使用**集中式錯誤處理器** — 禁止讓原始例外直接暴露給用戶端。
- 回傳結構化的錯誤物件：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": []
  }
}
```

## 安全性

- 在邊界層**驗證並清理**所有輸入。
- 使用**參數化查詢** — 禁止直接拼接 SQL 字串。
- 實施速率限制、CORS 政策，以及安全標頭（如 helmet）。
- 禁止記錄敏感資料（密碼、權杖、個人識別資訊）。
