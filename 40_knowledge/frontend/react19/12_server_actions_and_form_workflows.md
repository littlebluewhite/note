---
title: Server Actions and Form Workflows / Server Actions 與表單工作流
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "12"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [11_server_components_and_client_boundaries]
---
# Server Actions and Form Workflows / Server Actions 與表單工作流

## Goal

本章目標是建立「表單提交直達 server」的工作流，讓驗證、寫入、回饋在同一條可追蹤流程中完成。

銜接上一章：你已分清 server/client 邊界，現在把資料變更行為放回 server 端。

下一章預告：第 13 章會用 Suspense + Streaming 改善等待體驗，讓提交後頁面更流暢。

## Prerequisites

- 已完成第 11 章。
- 了解 HTML form 基本語義。
- 知道 server 端是最終驗證邊界。

## Core Concepts

1. Server Actions as mutation boundary
- 何時用：新增、更新、刪除等資料變更操作。
- 何時不用：純 client UI 切換與短暫狀態。

2. `useActionState` for submission result
- 何時用：你需要把 server 回傳錯誤/成功狀態映射到 UI。
- 何時不用：完全無回饋的背景操作。

3. Progressive enhancement with forms
- 何時用：保留原生 form 能力，JS 可用時再增強互動。
- 何時不用：把提交完全綁死在自定義 click handler。

## Step-by-step

1. 在 `src/app/todos/actions.ts` 宣告 `"use server"` action。
2. action 內解析 `FormData` 並做最終驗證。
3. 寫入資料層（先用 mock，後續可換 DB）。
4. 回傳 `{ ok, message, fieldErrors }` 結構。
5. 在 client form 使用 `useActionState` 綁定 action。
6. 根據 state 顯示欄位錯誤與全域訊息。
7. 送出中禁用按鈕，避免 double submit。
8. 成功後清空表單並刷新列表。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：完成新增 todo 的 server action。

驗收條件：
- 空白文字提交被拒絕。
- 成功提交後列表可見新項目。
- 送出中按鈕被禁用。

### 進階任務 (Advanced)
任務：加入欄位層級錯誤（text 長度上限）。

驗收條件：
- 錯誤可對應到正確欄位。
- 錯誤後不清空使用者輸入。
- 修正後可立即再次提交。

### 挑戰任務 (Challenge)
任務：加入 idempotency token，避免重複提交寫入。

驗收條件：
- 同 token 重送不會新增重複資料。
- 伺服端可辨識重送請求。
- UI 顯示「already processed」結果。

## Reference Solution

```tsx
// src/app/todos/actions.ts
"use server";

type ActionState = {
  ok: boolean;
  message: string;
  fieldErrors: { text?: string };
};

export async function createTodoAction(_: ActionState, formData: FormData): Promise<ActionState> {
  const text = String(formData.get("text") ?? "").trim();

  if (!text) {
    return { ok: false, message: "Validation failed.", fieldErrors: { text: "Text is required." } };
  }
  if (text.length > 120) {
    return { ok: false, message: "Validation failed.", fieldErrors: { text: "Text must be <= 120 chars." } };
  }

  // TODO: write to DB here
  return { ok: true, message: "Todo created.", fieldErrors: {} };
}

// src/components/TodoForm.tsx
"use client";

import { useActionState } from "react";
import { createTodoAction } from "@/app/todos/actions";

const initialState = { ok: false, message: "", fieldErrors: {} };

export function TodoForm() {
  const [state, action, pending] = useActionState(createTodoAction, initialState);

  return (
    <form action={action}>
      <input name="text" placeholder="Add todo" disabled={pending} />
      {state.fieldErrors.text ? <p role="alert">{state.fieldErrors.text}</p> : null}
      <button type="submit" disabled={pending}>{pending ? "Submitting..." : "Add"}</button>
      {state.message ? <p>{state.message}</p> : null}
    </form>
  );
}
```

## Common Pitfalls

- 把商業驗證只放 client，server action 未覆核。
- 回傳錯誤格式不一致，UI 難處理。
- 忽略 pending 狀態，使用者可重複提交。
- 在 client 檔案誤寫 `"use server"` 或混用 server-only 模組。

## Checklist

- [ ] `actions.ts` 含 `"use server"` 且無 client API 呼叫。
- [ ] form 有 pending、success、error 三種視覺狀態。
- [ ] 欄位錯誤與全域錯誤可同時呈現。
- [ ] 重複提交可被阻擋或去重。
- [ ] 程式碼保留清楚 action 回傳型別。

## Further Reading (official links only)

- [React useActionState](https://react.dev/reference/react/useActionState)
- [Next.js Server Actions](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions)
- [Forms](https://nextjs.org/docs/app/guides/forms)
