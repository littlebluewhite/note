---
title: Events, Forms, and Controlled Inputs / 事件、表單與受控輸入
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "05"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [04_rendering_lists_conditions_and_keys]
---
# Events, Forms, and Controlled Inputs / 事件、表單與受控輸入

## Goal

本章目標是把「使用者輸入 -> 驗證 -> 提交 -> 回饋」做成可預期流程，避免畫面狀態和資料狀態不同步。

銜接上一章：你已經會渲染清單與條件，現在要把互動資料輸入進狀態系統。

下一章預告：第 06 章會把表單外的副作用（監聽、計時器、同步外部系統）抽成正確的 `useEffect` 模式。

## Prerequisites

- 已完成第 04 章。
- 了解 `useState` 與事件綁定。
- 專案已可執行 `npm run dev`。

## Core Concepts

1. Controlled Inputs
- 何時用：需要即時驗證、條件禁用按鈕、顯示輸入狀態。
- 何時不用：大型檔案上傳或極少互動的欄位可先用非受控模式再讀值。

2. Form Submit Pipeline
- 何時用：你要統一處理提交邏輯（驗證、送 API、顯示錯誤）。
- 何時不用：只有單一按鈕切換、沒有提交語義時。

3. Validation Boundary
- 何時用：client 做使用者體驗型檢查，server 做最終合法性檢查。
- 何時不用：把安全驗證只留在 client 是錯誤作法。

## Step-by-step

1. 在 `src/app/login/page.tsx` 建立 client component（含 `"use client"`）。
2. 用單一 `form` state 物件管理 `email`、`password`、`remember`。
3. 將每個 input 變成 controlled：綁 `value/checked` 與 `onChange`。
4. 寫 `validate(form)` 回傳欄位錯誤 map，避免把驗證分散在 JSX。
5. 在 `onSubmit` 先 `preventDefault()`，再跑 `validate`。
6. 若驗證失敗，更新 `errors` 並 `return`。
7. 若驗證成功，設定 `isSubmitting=true`，模擬 API，最後復原狀態。
8. 在 UI 呈現三種狀態：idle、submitting、error/success。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：完成登入表單（email/password）與最小驗證。

驗收條件：
- email 不合法時顯示欄位錯誤。
- password 小於 8 碼不能提交。
- submit 按鈕在提交中顯示 `Signing in...`。

### 進階任務 (Advanced)
任務：新增 `remember me` checkbox 與錯誤摘要區塊。

驗收條件：
- checkbox 為 controlled input。
- 錯誤摘要顯示所有欄位錯誤。
- 使用者修正欄位後，該欄位錯誤可即時消失。

### 挑戰任務 (Challenge)
任務：加上提交防抖與重複點擊防護。

驗收條件：
- 連續點擊 submit 只會送出一次。
- 提交中禁用所有欄位。
- API 失敗後可重新提交，且舊錯誤不殘留。

## Reference Solution

```tsx
"use client";

import { FormEvent, useMemo, useState } from "react";

type LoginForm = {
  email: string;
  password: string;
  remember: boolean;
};

type LoginErrors = Partial<Record<keyof LoginForm, string>>;

function validate(form: LoginForm): LoginErrors {
  const errors: LoginErrors = {};
  if (!form.email.includes("@")) errors.email = "Email format is invalid.";
  if (form.password.length < 8) errors.password = "Password must be at least 8 chars.";
  return errors;
}

export default function LoginPage() {
  const [form, setForm] = useState<LoginForm>({ email: "", password: "", remember: false });
  const [errors, setErrors] = useState<LoginErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  const hasError = useMemo(() => Object.keys(errors).length > 0, [errors]);

  function update<K extends keyof LoginForm>(key: K, value: LoginForm[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isSubmitting) return;

    const nextErrors = validate(form);
    setErrors(nextErrors);
    setMessage("");
    if (Object.keys(nextErrors).length > 0) return;

    try {
      setIsSubmitting(true);
      await new Promise((resolve) => setTimeout(resolve, 600));
      setMessage("Login success.");
    } catch {
      setMessage("Login failed. Please retry.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main>
      <h1>Sign in</h1>
      {hasError ? <p role="alert">Please fix input errors.</p> : null}
      {message ? <p>{message}</p> : null}

      <form onSubmit={onSubmit}>
        <label>
          Email
          <input
            type="email"
            value={form.email}
            disabled={isSubmitting}
            onChange={(e) => update("email", e.target.value)}
          />
        </label>
        {errors.email ? <p role="alert">{errors.email}</p> : null}

        <label>
          Password
          <input
            type="password"
            value={form.password}
            disabled={isSubmitting}
            onChange={(e) => update("password", e.target.value)}
          />
        </label>
        {errors.password ? <p role="alert">{errors.password}</p> : null}

        <label>
          <input
            type="checkbox"
            checked={form.remember}
            disabled={isSubmitting}
            onChange={(e) => update("remember", e.target.checked)}
          />
          Remember me
        </label>

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}
```

## Common Pitfalls

- 把 `value` 綁定了卻忘記 `onChange`，造成 input 無法輸入。
- 每個欄位都用獨立 state，後續重置與驗證難維護。
- client 驗證通過就當成安全，忽略 server 最終驗證。
- Next.js App Router 中忘記 `"use client"` 卻使用事件 handler，導致編譯錯誤。

## Checklist

- [ ] `src/app/login/page.tsx` 能在瀏覽器正常輸入並提交。
- [ ] 空密碼或短密碼會顯示具體錯誤文案。
- [ ] 提交中按鈕文案會變化且不可重複點擊。
- [ ] 失敗後可重試，錯誤訊息不會永久殘留。
- [ ] 程式碼中有 `LoginForm` 與 `LoginErrors` 型別。

## Further Reading (official links only)

- [Responding to Events](https://react.dev/learn/responding-to-events)
- [Reacting to Input with State](https://react.dev/learn/reacting-to-input-with-state)
- [Managing State](https://react.dev/learn/managing-state)
