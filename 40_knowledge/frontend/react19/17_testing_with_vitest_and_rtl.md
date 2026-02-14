---
title: Testing with Vitest and RTL / 使用 Vitest 與 RTL 測試 React
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "17"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [16_performance_memoization_and_react_compiler]
---
# Testing with Vitest and RTL / 使用 Vitest 與 RTL 測試 React

## Goal

本章目標是建立可維護測試基線：以使用者行為為中心，覆蓋表單、非同步、錯誤路徑，避免脆弱測試。

銜接上一章：你已做效能優化，現在要用測試鎖住行為，避免後續優化破壞功能。

下一章預告：第 18 章會把測試帶入交付流程（CI/CD、監控、除錯）。

## Prerequisites

- 已完成第 16 章。
- 熟悉基本 DOM 查詢與事件概念。
- 專案可執行 `npm run test`。

## Core Concepts

1. Test behavior, not implementation
- 何時用：驗證使用者看得到、操作得到的結果。
- 何時不用：直接驗 state 內部值或 className 細節。

2. Async-safe assertions
- 何時用：提交、抓資料、延遲渲染等非同步流程。
- 何時不用：用同步斷言檢查尚未完成的 UI 變更。

3. Testing pyramid for frontend
- 何時用：component test 作為主力，E2E 作少量關鍵流程。
- 何時不用：把所有情境都堆在昂貴 E2E。

## Step-by-step

1. 安裝 `vitest`, `@testing-library/react`, `@testing-library/user-event`。
2. 設定 `vitest.config.ts` 與 `test/setup.ts`。
3. 為 `LoginForm` 寫第一個 smoke test。
4. 補錯誤輸入測試（email/password invalid）。
5. 補成功提交測試（模擬 API success）。
6. 補失敗提交測試（模擬 API error）。
7. 對 async 流程使用 `findByRole`、`waitFor`。
8. 將測試加入 CI 命令。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：為登入表單建立 3 個基本測試。

驗收條件：
- 初始渲染正常。
- 錯誤輸入會顯示警示。
- 成功提交顯示成功訊息。

### 進階任務 (Advanced)
任務：為 `useUsers` 頁面建立 loading/error/retry 測試。

驗收條件：
- loading 文案可被找到。
- API fail 時顯示 retry。
- 點 retry 後可恢復成功路徑。

### 挑戰任務 (Challenge)
任務：建立自動化測試矩陣（form + fetch + optimistic）。

驗收條件：
- 至少 10 個測試案例。
- 測試執行時間可接受（例如 < 10 秒）。
- 無 flaky 測試（連跑 5 次穩定通過）。

## Reference Solution

```tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginForm } from "@/components/login-form";

it("shows validation errors for invalid input", async () => {
  const user = userEvent.setup();
  render(<LoginForm />);

  await user.type(screen.getByLabelText(/email/i), "bad-mail");
  await user.type(screen.getByLabelText(/password/i), "123");
  await user.click(screen.getByRole("button", { name: /sign in/i }));

  expect(await screen.findByText(/email format is invalid/i)).toBeInTheDocument();
  expect(await screen.findByText(/at least 8 chars/i)).toBeInTheDocument();
});

it("shows success message after submit", async () => {
  const user = userEvent.setup();
  render(<LoginForm />);

  await user.type(screen.getByLabelText(/email/i), "a@b.com");
  await user.type(screen.getByLabelText(/password/i), "12345678");
  await user.click(screen.getByRole("button", { name: /sign in/i }));

  await waitFor(() => {
    expect(screen.getByText(/login success/i)).toBeInTheDocument();
  });
});
```

## Common Pitfalls

- 測試只驗 className，遇到重構就大量失敗。
- 非同步流程使用 `getBy` 導致偶發失敗。
- 共用 mutable mock 狀態造成測試互相污染。
- 在 Next.js 專案中忽略 `jsdom` 設定，導致 client component 測試異常。

## Checklist

- [ ] `vitest.config.ts` 與 `test/setup.ts` 已存在。
- [ ] 至少 1 個表單成功路徑 + 1 個失敗路徑測試。
- [ ] 至少 1 個非同步等待測試使用 `findBy` 或 `waitFor`。
- [ ] 測試可在本機連跑 3 次通過。
- [ ] CI 腳本包含測試步驟。

## Further Reading (official links only)

- [Vitest Docs](https://vitest.dev/guide/)
- [Testing Library React](https://testing-library.com/docs/react-testing-library/intro/)
- [Next.js Testing](https://nextjs.org/docs/app/building-your-application/testing)
- [React Testing Recipes](https://react.dev/learn/testing)
