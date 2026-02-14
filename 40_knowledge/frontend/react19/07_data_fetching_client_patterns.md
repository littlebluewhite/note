---
title: Data Fetching Client Patterns / Client 端資料抓取模式
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "07"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [06_effects_and_common_side_effect_patterns]
---
# Data Fetching Client Patterns / Client 端資料抓取模式

## Goal

本章目標是建立 client fetching 的標準骨架：`loading/error/data`、取消請求、重試機制，讓畫面對網路波動有韌性。

銜接上一章：你已知道 effect 的正確用法，現在把它用在真實資料抓取流程。

下一章預告：第 08 章會將資料與狀態管理推進到跨元件共享（Context + Reducer）。

## Prerequisites

- 已完成第 06 章。
- 了解 Promise 與 `async/await`。
- 了解基本 TypeScript 型別宣告。

## Core Concepts

1. Async state triad
- 何時用：任何非同步資料來源都應明確表示 loading/error/data。
- 何時不用：同步常數資料不需要 triad。

2. Request cancellation
- 何時用：component unmount、查詢條件快速切換時。
- 何時不用：一次性短流程且不會切換路由時可簡化，但仍建議保留。

3. Client fetch vs Server fetch
- 何時用：需要瀏覽器即時互動（搜尋輸入、即時篩選）。
- 何時不用：初始頁面內容可由 Next.js Server Component 直接取資料。

## Step-by-step

1. 建立 `User` type 與 API 回傳型別。
2. 在 `src/app/users/page.tsx` 建立 client 頁面。
3. 寫 `useUsers(keyword)` hook 管理 triad。
4. 使用 `AbortController` 在 cleanup 中中止請求。
5. 加入 `retry()`，讓使用者可重試失敗請求。
6. 把 API 解析錯誤與網路錯誤分開處理。
7. 在 UI 區分三種狀態並加上空列表訊息。
8. 透過 `keyword` 變動驗證 race condition 是否被消除。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：做 `/users` 頁，顯示使用者列表。

驗收條件：
- 初次進入顯示 loading。
- 成功後顯示列表。
- 失敗後顯示 retry 按鈕。

### 進階任務 (Advanced)
任務：加入搜尋 keyword，輸入會重新抓取。

驗收條件：
- 快速輸入時舊請求會被取消。
- 只顯示最新 keyword 的結果。
- 空結果顯示 `No users found`。

### 挑戰任務 (Challenge)
任務：加入快取層（以 `Map<string, User[]>` 做記憶）。

驗收條件：
- 同 keyword 重查優先讀快取。
- 手動 refresh 可強制略過快取。
- 快取命中時畫面不閃爍 loading。

## Reference Solution

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";

type User = { id: string; name: string; email: string };

type FetchState = {
  loading: boolean;
  error: string;
  data: User[];
};

function useUsers(keyword: string) {
  const [state, setState] = useState<FetchState>({ loading: true, error: "", data: [] });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    const query = keyword.trim();

    setState((prev) => ({ ...prev, loading: true, error: "" }));

    fetch(`/api/users?keyword=${encodeURIComponent(query)}`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json() as Promise<User[]>;
      })
      .then((users) => setState({ loading: false, error: "", data: users }))
      .catch((error: Error) => {
        if (error.name === "AbortError") return;
        setState({ loading: false, error: error.message, data: [] });
      });

    return () => controller.abort();
  }, [keyword, reloadKey]);

  const retry = useCallback(() => setReloadKey((n) => n + 1), []);
  return { ...state, retry };
}

export default function UsersPage() {
  const [keyword, setKeyword] = useState("");
  const { loading, error, data, retry } = useUsers(keyword);

  return (
    <main>
      <h1>Users</h1>
      <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="Search users" />

      {loading ? <p>Loading...</p> : null}
      {error ? <button onClick={retry}>Retry ({error})</button> : null}
      {!loading && !error && data.length === 0 ? <p>No users found.</p> : null}

      <ul>
        {data.map((user) => (
          <li key={user.id}>{user.name} ({user.email})</li>
        ))}
      </ul>
    </main>
  );
}
```

## Common Pitfalls

- 把 loading 和 data 寫在不同 state，造成瞬間不一致。
- 沒處理 HTTP 非 2xx，錯誤被當成成功資料。
- 忘記 abort 舊請求，快速輸入時結果跳回舊 keyword。
- 在 Next.js Server Component 直接使用 browser fetch 流程與互動 state，邊界混亂。

## Checklist

- [ ] `useUsers` hook 具備 `loading/error/data/retry`。
- [ ] keyword 快速切換不會出現舊資料覆蓋新資料。
- [ ] API 500 時能顯示錯誤且可重試。
- [ ] 空資料狀態有明確文案。
- [ ] 至少一個型別（`User` 或 `FetchState`）被完整使用。

## Further Reading (official links only)

- [Lifecycle of Reactive Effects](https://react.dev/learn/lifecycle-of-reactive-effects)
- [Fetching Data](https://nextjs.org/docs/app/building-your-application/data-fetching)
- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
