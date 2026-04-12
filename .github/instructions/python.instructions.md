---
applyTo: "**/*.py"
---

# Python 程式碼規範

## 風格

- 遵循 **PEP 8** 規範，所有函式簽章皆須加上 **型別提示（type hints）**。
- 變數與函式使用 `snake_case`，類別使用 `PascalCase`。
- 優先使用 **f-string**，避免 `.format()` 或 `%` 格式化。
- 每行最大長度：**88 字元**（Black 格式化工具預設值）。

## 結構

- 盡量每個檔案只放一個類別，檔案不超過 **300 行**。
- 使用 `dataclasses` 或 `Pydantic` 模型定義資料結構 — 避免使用原始字典。
- 匯入順序：標準函式庫 → 第三方套件 → 本地模組，各群組間以空行分隔。

## 最佳實踐

- 使用 `uv` 管理 Python 套件與執行環境：
  - 使用 `uv run` 執行 Python 程式碼（不使用 `python` 或 `.venv/bin/python`）
  - 使用 `uv sync` 同步虛擬環境
  - 使用 `uv add <package>` 安裝套件（不使用 `pip install`）
  - 使用 `uv remove <package>` 移除套件
  - 禁止直接使用 `pip`、`pip install` 或 `.venv/bin/python`
- 使用**情境管理器**（`with`）處理資源（檔案、連線）。
- 使用**串列推導式**取代 `map()`/`filter()`，以提升可讀性。
- 明確處理例外 — 禁止使用空的 `except:`。
- 為所有公開函式與類別撰寫 **docstring**（Google 風格）。

```python
def calculate_total(items: list[Item], tax_rate: float = 0.1) -> float:
    """計算含稅總金額。

    Args:
        items: 要加總的項目清單。
        tax_rate: 稅率（小數表示），預設為 0.1。

    Returns:
        含稅後的總金額。
    """
    subtotal = sum(item.price for item in items)
    return subtotal * (1 + tax_rate)
```
