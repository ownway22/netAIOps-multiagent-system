---
applyTo: '**/*.css,**/*.scss,**/*.html,**/*.jsx,**/*.tsx,**/*.vue,**/components/**'
---

# 前端開發規範

## UI 原則

- 採用**行動優先（Mobile-first）**的響應式設計 — 從最小斷點開始。
- 遵循**語意化 HTML** — 適當使用 `<nav>`、`<main>`、`<article>`、`<section>` 等標籤。
- 確保符合 **WCAG 2.1 AA** 無障礙標準：替代文字、ARIA 標籤、鍵盤導覽、色彩對比。

## CSS / 樣式

- 使用**工具優先（utility-first）**方式（如 Tailwind）或 **CSS Modules** 進行樣式隔離。
- 避免過度巢狀選擇器 — 最多 **3 層**。
- 使用 **CSS 自訂屬性**（`--color-primary`）實現主題切換。
- 透過 `prefers-color-scheme` 或主題切換機制支援**深色模式**。

```css
:root {
  --color-primary: #3b82f6;
  --color-bg: #ffffff;
  --color-text: #1f2937;
}

[data-theme='dark'] {
  --color-bg: #111827;
  --color-text: #f9fafb;
}
```

## 效能

- 延遲載入圖片與非關鍵元件。
- 減少 DOM 深度 — 避免不必要的包裹元素。
- 圖片使用 `loading="lazy"`，關鍵資源使用 `<link rel="preload">`。

## 狀態管理

- 盡可能將 UI 狀態保持在元件**區域範圍內**。
- 僅在兄弟元件需要共享時才提升狀態。
- 全域 store 僅用於**真正全域**的狀態（驗證、主題、語系）。
