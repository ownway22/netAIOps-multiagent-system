---
applyTo: '**/*.java'
---

# Java 程式碼規範

## 風格

- 遵循 **Google Java Style Guide**。
- 方法與變數使用 `camelCase`，類別使用 `PascalCase`，常數使用 `UPPER_SNAKE_CASE`。
- 每行最大長度：**120 字元**。
- `if`/`for`/`while` 一律使用**大括號**，即使只有單行內容。

## 結構

- 每個檔案只放一個公開類別，檔案不超過 **300 行**。
- 套件結構遵循領域驅動設計（DDD）：`com.project.domain.feature`。
- 使用 **record** 定義不可變的資料傳輸物件（Java 16+）。

## 最佳實踐

- 型別明確的區域變數優先使用 **`var`**（Java 10+）。
- 使用 **Optional** 取代回傳 `null`。
- 集合轉換優先使用 **Stream API**。
- 採用**依賴注入** — 服務類別避免直接使用 `new`。
- 為所有公開方法撰寫 **Javadoc**。

```java
public record UserResponse(String id, String name, String email) {}

public Optional<UserResponse> findUserById(String id) {
    return userRepository.findById(id)
            .map(user -> new UserResponse(user.getId(), user.getName(), user.getEmail()));
}
```

## 測試

- 使用 **JUnit 5** 並搭配描述性的 `@DisplayName` 標註。
- 遵循**準備 → 執行 → 驗證（Arrange → Act → Assert）**模式。
- 使用 **Mockito** 模擬依賴元件。
