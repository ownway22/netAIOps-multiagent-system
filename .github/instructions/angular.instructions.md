---
applyTo: '**/*.ts,**/*.component.html'
---

# Angular 程式碼規範

## 風格

- 遵循 **Angular 官方風格指南**。
- 屬性與方法使用 `camelCase`，類別與介面使用 `PascalCase`。
- 介面命名以語境為前綴，而非 `I` — 例如用 `UserProfile` 而非 `IUserProfile`。
- 在 `tsconfig.json` 中啟用**嚴格模式**，禁止使用 `any`。

## 元件設計

- 每個檔案只放一個元件，元件不超過 **200 行**。
- 使用**獨立元件（standalone components）**（Angular 15+）— 新程式碼避免使用 NgModules。
- 優先使用 **signals** 進行響應式狀態管理（Angular 16+）。
- 預設使用 `OnPush` 變更偵測策略。

```typescript
@Component({
  selector: 'app-user-card',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './user-card.component.html',
})
export class UserCardComponent {
  readonly user = input.required<User>();
  readonly isActive = computed(() => this.user().status === 'active');
}
```

## 最佳實踐

- 優先使用**響應式表單（reactive forms）**，而非範本驅動表單。
- 透過 `inject()` 函式注入服務，取代建構子注入。
- 在範本中使用 **`async` pipe** 處理 observables — 避免手動訂閱。
- 依**功能模組**組織程式碼，而非依檔案類型分類。

## 檔案命名

| 類型        | 命名慣例                         |
|-------------|----------------------------------|
| 元件        | `user-card.component.ts`         |
| 服務        | `user.service.ts`                |
| 指令        | `highlight.directive.ts`         |
| 管道        | `currency-format.pipe.ts`        |
| 守衛        | `auth.guard.ts`                  |
