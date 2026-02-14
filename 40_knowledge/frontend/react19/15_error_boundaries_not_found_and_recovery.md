---
title: Error Boundaries, Not Found, and Recovery / 錯誤邊界、404 與復原策略
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "15"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [14_transitions_optimistic_ui_and_user_experience]
---
# Error Boundaries, Not Found, and Recovery / 錯誤邊界、404 與復原策略

## Goal

本章目標是建立「錯誤可隔離、可引導、可恢復」的頁面策略，避免單點失敗拖垮整頁。

銜接上一章：你已處理 optimistic 操作，現在要補上失敗路徑與可復原機制。

下一章預告：第 16 章會在正確性穩定後，進入可量測的效能優化。

## Prerequisites

- 已完成第 14 章。
- 了解錯誤與例外基本概念。
- 了解 Next.js route file conventions。

## Core Concepts

1. Error boundary scope
- 何時用：可能噴錯的局部區塊應有自己的 boundary。
- 何時不用：所有錯誤都回到全站單一錯誤頁。

2. Not Found as business outcome
- 何時用：資源不存在（404）是可預期結果，不是程式錯誤。
- 何時不用：把 404 當 500 顯示「系統故障」。

3. Recovery-first UI
- 何時用：提供 retry、返回、重置條件。
- 何時不用：只顯示錯誤訊息卻沒有下一步操作。

## Step-by-step

1. 在目標 route 新增 `error.tsx`。
2. 設計錯誤訊息與 `Try again` 按鈕。
3. 新增 `not-found.tsx` 處理不存在資源。
4. 在 page 的資料查詢中適時呼叫 `notFound()`。
5. 區分 4xx 與 5xx 類型訊息。
6. 記錄錯誤 id（便於追蹤）。
7. 將可重試操作包裝成明確流程。
8. 在 staging 模擬 API fail 與 404。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：為 `/products/[id]` 增加 `not-found.tsx`。

驗收條件：
- 不存在 id 會導向 not-found 畫面。
- 畫面有返回產品列表按鈕。
- 文案可區分「不存在」而非「系統錯誤」。

### 進階任務 (Advanced)
任務：新增 route-level `error.tsx` 與 retry。

驗收條件：
- API 臨時失敗時顯示 retry。
- retry 後成功可回到正常內容。
- 錯誤邊界不影響其他 route。

### 挑戰任務 (Challenge)
任務：把錯誤分級成 recoverable/unrecoverable 並顯示不同 CTA。

驗收條件：
- recoverable 有 retry。
- unrecoverable 有 support link 或回首頁。
- 每種錯誤都有可觀測訊息（error id）。

## Reference Solution

```tsx
// src/app/products/[id]/page.tsx
import { notFound } from "next/navigation";

type Product = { id: string; name: string };

async function getProduct(id: string): Promise<Product | null> {
  const res = await fetch(`https://example.com/api/products/${id}`, { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Product API failed: ${res.status}`);
  return res.json() as Promise<Product>;
}

export default async function ProductDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await getProduct(id);
  if (!product) notFound();

  return (
    <main>
      <h1>{product.name}</h1>
      <p>ID: {product.id}</p>
    </main>
  );
}

// src/app/products/[id]/error.tsx
"use client";

export default function ErrorPage({ reset }: { error: Error; reset: () => void }) {
  return (
    <main>
      <h2>Something went wrong.</h2>
      <button onClick={reset}>Try again</button>
    </main>
  );
}
```

## Common Pitfalls

- 404 與 500 混為一談，使用者無法判斷問題性質。
- retry 只重畫畫面，沒有重新請求。
- error UI 沒有返回路徑，使用者卡死。
- 在 server component 直接依賴 client-only error hooks，Next 邊界不清。

## Checklist

- [ ] `not-found.tsx` 與 `error.tsx` 都已建立。
- [ ] 404 與 500 文案不同。
- [ ] 至少 1 個錯誤流程可重試成功。
- [ ] 發生錯誤時有可追蹤資訊（timestamp 或 error id）。
- [ ] 正常流程不受錯誤頁影響。

## Further Reading (official links only)

- [React Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [Next.js Error Handling](https://nextjs.org/docs/app/building-your-application/routing/error-handling)
- [notFound](https://nextjs.org/docs/app/api-reference/functions/not-found)
