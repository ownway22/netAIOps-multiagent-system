---
applyTo: '**/*.sql,**/models/**,**/entities/**,**/migrations/**,**/schema/**'
---

# 資料庫開發規範

## 結構描述設計

- 資料表名稱使用**單數形式**：`user`、`order`、`product`。
- 每張資料表必須有**主鍵** — 優先使用 `UUID` 或自動遞增的 `id`。
- 每張資料表都加上 `created_at` 與 `updated_at` 時間戳記。
- 預設套用 **NOT NULL** 約束 — 僅在語意上確實需要時才允許 `NULL`。

```sql
CREATE TABLE user (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) NOT NULL UNIQUE,
    name        VARCHAR(100) NOT NULL,
    status      VARCHAR(20)  NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);
```

## 命名慣例

| 元素          | 慣例               | 範例                  |
|---------------|--------------------|-----------------------|
| 資料表        | `snake_case`       | `order_item`          |
| 欄位          | `snake_case`       | `first_name`          |
| 索引          | `idx_資料表_欄位`  | `idx_user_email`      |
| 外鍵          | `fk_資料表_參考`   | `fk_order_user`       |

## 查詢最佳實踐

- `SELECT` 時一律指定**欄位名稱** — 避免使用 `SELECT *`。
- 在 `WHERE`、`JOIN`、`ORDER BY` 中常用的欄位建立**索引**。
- 所有結構描述變更都撰寫 **migration** — 禁止手動修改正式環境的結構描述。
- 涉及多張資料表的操作使用**交易（transaction）**。

## ORM 使用規範

- 定義的模型應精確對應資料庫結構描述。
- 使用**預先載入（eager loading）**以避免 N+1 查詢問題。
- 複雜查詢使用原生 SQL；標準 CRUD 操作使用 ORM。
