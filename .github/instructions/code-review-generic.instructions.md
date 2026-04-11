---
description: "適用於任何專案的通用程式碼審查指引，可搭配 GitHub Copilot 使用"
applyTo: "**"
excludeAgent: ["coding-agent"]
---

# 通用程式碼審查指引

適用於 GitHub Copilot 的全面程式碼審查準則，可調整套用於任何專案。本指引遵循提示工程的最佳實務，並為程式碼品質、安全性、測試和架構審查提供結構化的方法。

## 審查語言

執行程式碼審查時，以**繁體中文**回應（或指定你偏好的語言）。

> **自訂提示**：若需變更語言，請將「繁體中文」替換為你偏好的語言，例如「English」、「日本語」等。

## 審查優先順序

執行程式碼審查時，依照以下順序排列問題的優先等級：

### 🔴 嚴重（阻擋合併）

- **安全性**：弱點、暴露的機密資訊、身分驗證/授權問題
- **正確性**：邏輯錯誤、資料毀損風險、競態條件
- **破壞性變更**：未經版本控管的 API 合約變更
- **資料遺失**：資料遺失或損毀的風險

### 🟡 重要（需要討論）

- **程式碼品質**：嚴重違反 SOLID 原則、過度重複
- **測試覆蓋率**：關鍵路徑或新功能缺少測試
- **效能**：明顯的效能瓶頸（N+1 查詢、記憶體洩漏）
- **架構**：與已確立模式的重大偏離

### 🟢 建議（不阻擋的改善）

- **可讀性**：命名不佳、可以簡化的複雜邏輯
- **最佳化**：不影響功能的效能改善
- **最佳實務**：與慣例的輕微偏差
- **文件**：缺少或不完整的註解/文件

## 一般審查原則

執行程式碼審查時，遵循以下原則：

1. **具體明確**：引用確切的行數、檔案，並提供具體範例
2. **提供脈絡**：說明為什麼某件事是問題，以及可能的影響
3. **建議解決方案**：在適用時展示修正後的程式碼，而非僅指出錯誤
4. **保持建設性**：聚焦於改善程式碼，而非批評作者
5. **肯定良好做法**：表揚寫得好的程式碼和巧妙的解決方案
6. **務實態度**：不是每個建議都需要立即實作
7. **歸納相關意見**：避免對同一主題發出多則重複的評論

## 程式碼品質標準

執行程式碼審查時，檢查以下項目：

### 整潔程式碼

- 變數、函式和類別使用具描述性且有意義的命名
- 單一職責原則：每個函式/類別只做好一件事
- DRY（不要重複自己）：沒有程式碼重複
- 函式應該小巧且聚焦（理想情況下少於 20-30 行）
- 避免過深的巢狀結構（最多 3-4 層）
- 避免魔術數字和魔術字串（使用常數）
- 程式碼應具備自我說明性；僅在必要時加入註解

### 範例

```javascript
// ❌ 不佳：命名不良且使用魔術數字
function calc(x, y) {
  if (x > 100) return y * 0.15;
  return y * 0.1;
}

// ✅ 良好：清晰命名且使用常數
const PREMIUM_THRESHOLD = 100;
const PREMIUM_DISCOUNT_RATE = 0.15;
const STANDARD_DISCOUNT_RATE = 0.1;

function calculateDiscount(orderTotal, itemPrice) {
  const isPremiumOrder = orderTotal > PREMIUM_THRESHOLD;
  const discountRate = isPremiumOrder
    ? PREMIUM_DISCOUNT_RATE
    : STANDARD_DISCOUNT_RATE;
  return itemPrice * discountRate;
}
```

### 錯誤處理

- 在適當的層級進行正確的錯誤處理
- 有意義的錯誤訊息
- 不得有靜默失敗或忽略的例外
- 快速失敗：及早驗證輸入
- 使用適當的錯誤型別/例外

### 範例

```python
# ❌ 不佳：靜默失敗和通用錯誤
def process_user(user_id):
    try:
        user = db.get(user_id)
        user.process()
    except:
        pass

# ✅ 良好：明確的錯誤處理
def process_user(user_id):
    if not user_id or user_id <= 0:
        raise ValueError(f"Invalid user_id: {user_id}")

    try:
        user = db.get(user_id)
    except UserNotFoundError:
        raise UserNotFoundError(f"User {user_id} not found in database")
    except DatabaseError as e:
        raise ProcessingError(f"Failed to retrieve user {user_id}: {e}")

    return user.process()
```

## 安全性審查

執行程式碼審查時，檢查安全性問題：

- **敏感資料**：程式碼或日誌中不得包含密碼、API 金鑰、權杖或個人識別資訊
- **輸入驗證**：所有使用者輸入皆經過驗證和清理
- **SQL 注入**：使用參數化查詢，絕不使用字串串接
- **身分驗證**：存取資源前進行適當的身分驗證檢查
- **授權**：驗證使用者是否具有執行操作的權限
- **加密**：使用成熟的函式庫，絕不自行實作加密演算法
- **相依套件安全**：檢查相依套件中的已知弱點

### 範例

```java
// ❌ 不佳：SQL 注入弱點
String query = "SELECT * FROM users WHERE email = '" + email + "'";

// ✅ 良好：參數化查詢
PreparedStatement stmt = conn.prepareStatement(
    "SELECT * FROM users WHERE email = ?"
);
stmt.setString(1, email);
```

```javascript
// ❌ 不佳：機密資訊暴露在程式碼中
const API_KEY = "sk_live_abc123xyz789";

// ✅ 良好：使用環境變數
const API_KEY = process.env.API_KEY;
```

## 測試標準

執行程式碼審查時，驗證測試品質：

- **覆蓋率**：關鍵路徑和新功能必須有測試
- **測試名稱**：使用描述性名稱來說明正在測試什麼
- **測試結構**：清晰的 Arrange-Act-Assert 或 Given-When-Then 模式
- **獨立性**：測試不應相互依賴或依賴外部狀態
- **斷言**：使用具體的斷言，避免通用的 assertTrue/assertFalse
- **邊界情況**：測試邊界條件、null 值、空集合
- **適當模擬**：模擬外部相依，而非領域邏輯

### 範例

```typescript
// ❌ 不佳：模糊的名稱和斷言
test("test1", () => {
  const result = calc(5, 10);
  expect(result).toBeTruthy();
});

// ✅ 良好：描述性名稱和具體斷言
test("should calculate 10% discount for orders under $100", () => {
  const orderTotal = 50;
  const itemPrice = 20;

  const discount = calculateDiscount(orderTotal, itemPrice);

  expect(discount).toBe(2.0);
});
```

## 效能考量

執行程式碼審查時，檢查效能問題：

- **資料庫查詢**：避免 N+1 查詢，使用適當的索引
- **演算法**：針對使用情境選擇適當的時間/空間複雜度
- **快取**：對耗時或重複的操作使用快取
- **資源管理**：適當清理連線、檔案、串流
- **分頁**：大型結果集應進行分頁
- **延遲載入**：僅在需要時才載入資料

### 範例

```python
# ❌ 不佳：N+1 查詢問題
users = User.query.all()
for user in users:
    orders = Order.query.filter_by(user_id=user.id).all()  # N+1!

# ✅ 良好：使用 JOIN 或預先載入
users = User.query.options(joinedload(User.orders)).all()
for user in users:
    orders = user.orders
```

## 架構與設計

執行程式碼審查時，驗證架構原則：

- **關注點分離**：層級/模組之間有清晰的邊界
- **相依方向**：高階模組不依賴低階細節
- **介面隔離**：偏好小巧且聚焦的介面
- **鬆耦合**：元件應可獨立測試
- **高內聚**：相關功能歸為一組
- **一致的模式**：遵循程式碼庫中已確立的模式

## 文件標準

執行程式碼審查時，檢查文件：

- **API 文件**：公開的 API 必須加以文件化（用途、參數、回傳值）
- **複雜邏輯**：不明顯的邏輯應加上解釋性註解
- **README 更新**：新增功能或變更設定時更新 README
- **破壞性變更**：清楚記載任何破壞性變更
- **範例**：為複雜功能提供使用範例

## 評論格式範本

執行程式碼審查時，使用以下格式撰寫評論：

```markdown
**[優先等級] 類別：簡短標題**

問題或建議的詳細說明。

**為什麼這很重要：**
說明其影響或提出建議的原因。

**建議修正：**
[適用時附上程式碼範例]

**參考資料：** [相關文件或標準的連結]
```

### 評論範例

#### 嚴重問題

````markdown
**🔴 嚴重 - 安全性：SQL 注入弱點**

第 45 行的查詢將使用者輸入直接串接到 SQL 字串中，
產生了 SQL 注入弱點。

**為什麼這很重要：**
攻擊者可以操控 email 參數來執行任意 SQL 指令，
可能導致所有資料庫資料被暴露或刪除。

**建議修正：**

```sql
-- 取代原本的寫法：
query = "SELECT * FROM users WHERE email = '" + email + "'"

-- 使用：
PreparedStatement stmt = conn.prepareStatement(
    "SELECT * FROM users WHERE email = ?"
);
stmt.setString(1, email);
```

**參考資料：** OWASP SQL 注入防範速查表
````

#### 重要問題

````markdown
**🟡 重要 - 測試：關鍵路徑缺少測試覆蓋**

`processPayment()` 函式處理金融交易，但缺少退款情境的測試。

**為什麼這很重要：**
退款涉及金流異動，應徹底測試以防止
財務錯誤或資料不一致。

**建議修正：**
新增測試案例：

```javascript
test("should process full refund when order is cancelled", () => {
  const order = createOrder({ total: 100, status: "cancelled" });

  const result = processPayment(order, { type: "refund" });

  expect(result.refundAmount).toBe(100);
  expect(result.status).toBe("refunded");
});
```
````

#### 建議

````markdown
**🟢 建議 - 可讀性：簡化巢狀條件判斷**

第 30-40 行的巢狀 if 語句使邏輯難以閱讀。

**為什麼這很重要：**
更簡潔的程式碼更容易維護、除錯和測試。

**建議修正：**

```javascript
// 取代巢狀 if：
if (user) {
  if (user.isActive) {
    if (user.hasPermission("write")) {
      // 執行某些操作
    }
  }
}

// 考慮使用守衛子句：
if (!user || !user.isActive || !user.hasPermission("write")) {
  return;
}
// 執行某些操作
```
````

## 審查清單

執行程式碼審查時，系統性地驗證：

### 程式碼品質

- [ ] 程式碼遵循一致的風格和慣例
- [ ] 命名具描述性且遵循命名慣例
- [ ] 函式/方法小巧且聚焦
- [ ] 沒有程式碼重複
- [ ] 複雜邏輯已拆分為更簡單的部分
- [ ] 錯誤處理是適當的
- [ ] 沒有被註解掉的程式碼或未附工單的 TODO

### 安全性

- [ ] 程式碼或日誌中沒有敏感資料
- [ ] 所有使用者輸入皆有輸入驗證
- [ ] 沒有 SQL 注入弱點
- [ ] 身分驗證和授權已正確實作
- [ ] 相依套件是最新且安全的

### 測試

- [ ] 新程式碼有適當的測試覆蓋率
- [ ] 測試命名良好且聚焦
- [ ] 測試涵蓋邊界情況和錯誤情境
- [ ] 測試獨立且具確定性
- [ ] 沒有永遠通過或被註解掉的測試

### 效能

- [ ] 沒有明顯的效能問題（N+1、記憶體洩漏）
- [ ] 適當使用快取
- [ ] 高效的演算法和資料結構
- [ ] 適當的資源清理

### 架構

- [ ] 遵循已確立的模式和慣例
- [ ] 適當的關注點分離
- [ ] 沒有架構違規
- [ ] 相依方向正確

### 文件

- [ ] 公開的 API 已加以文件化
- [ ] 複雜邏輯有解釋性註解
- [ ] README 已視需要更新
- [ ] 破壞性變更已記載

## 專案特定的自訂設定

若要為你的專案自訂此範本，請新增以下章節：

1. **語言/框架專屬檢查**
   - 範例：「執行程式碼審查時，驗證 React hooks 是否遵循 hooks 的規則」
   - 範例：「執行程式碼審查時，檢查 Spring Boot 控制器是否使用適當的註解」

2. **建置與部署**
   - 範例：「執行程式碼審查時，驗證 CI/CD 管線設定是否正確」
   - 範例：「執行程式碼審查時，檢查資料庫遷移是否可逆」

3. **商業邏輯規則**
   - 範例：「執行程式碼審查時，驗證定價計算是否包含所有適用稅額」
   - 範例：「執行程式碼審查時，檢查在資料處理前是否已取得使用者同意」

4. **團隊慣例**
   - 範例：「執行程式碼審查時，驗證提交訊息是否遵循約定式提交格式」
   - 範例：「執行程式碼審查時，檢查分支名稱是否遵循格式：type/ticket-description」

## 額外資源

有關有效程式碼審查和 GitHub Copilot 自訂的更多資訊：

- [GitHub Copilot 提示工程](https://docs.github.com/en/copilot/concepts/prompting/prompt-engineering)
- [GitHub Copilot 自訂指令](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [Awesome GitHub Copilot 儲存庫](https://github.com/github/awesome-copilot)
- [GitHub 程式碼審查指南](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests)
- [Google 工程實務 - 程式碼審查](https://google.github.io/eng-practices/review/)
- [OWASP 安全性指南](https://owasp.org/)

## 提示工程技巧

執行程式碼審查時，套用以下來自 [GitHub Copilot 文件](https://docs.github.com/en/copilot/concepts/prompting/prompt-engineering)的提示工程原則：

1. **從一般到具體**：先從整體架構審查開始，再深入實作細節
2. **提供範例**：在建議變更時，引用程式碼庫中類似的模式
3. **拆解複雜任務**：依照邏輯區塊審查大型 PR（安全性 → 測試 → 邏輯 → 風格）
4. **避免模糊性**：具體指出你正在處理的檔案、行數和問題
5. **指出相關程式碼**：引用可能受變更影響的相關程式碼
6. **實驗與迭代**：若初次審查遺漏了某些內容，以聚焦的問題再次審查

## 專案脈絡資訊

這是一份通用範本。請使用你的專案特定資訊自訂本章節：

- **技術堆疊**：[例如：Java 17、Spring Boot 3.x、PostgreSQL]
- **架構**：[例如：六角形/整潔架構、微服務]
- **建置工具**：[例如：Gradle、Maven、npm、pip]
- **測試**：[例如：JUnit 5、Jest、pytest]
- **程式碼風格**：[例如：遵循 Google 風格指南]
