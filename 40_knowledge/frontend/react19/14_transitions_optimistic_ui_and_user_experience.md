---
title: Transitions, Optimistic UI, and User Experience / Transition、樂觀更新與體驗
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "14"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [13_suspense_streaming_and_loading_ui]
---
# Transitions, Optimistic UI, and User Experience / Transition、樂觀更新與體驗

## Goal

本章目標是讓操作延遲時仍保持流暢互動，並學會在「先顯示結果」與「正確回滾」之間取得平衡。

銜接上一章：你已能分段載入內容，現在進一步優化使用者操作中的等待體驗。

下一章預告：第 15 章會處理失敗路徑，讓 optimistic 與 transition 錯誤能被妥善復原。

## Prerequisites

- 已完成第 13 章。
- 了解非同步請求與錯誤處理。
- 知道 `useState` 與 `useMemo`。

## Core Concepts

1. `startTransition` for non-urgent updates
- 何時用：大量列表篩選、搜尋結果切換等可延後更新。
- 何時不用：輸入框游標、按鍵回饋等必須即時更新。

2. `useOptimistic` for perceived speed
- 何時用：發送留言、按讚、加入收藏等高頻簡單操作。
- 何時不用：涉及高風險不可逆操作（付款、庫存扣減）應先確認後再顯示。

3. Rollback strategy
- 何時用：server 失敗時要清楚撤回 optimistic 狀態。
- 何時不用：只做樂觀顯示卻沒失敗策略。

## Step-by-step

1. 選擇一個提交延遲明顯的互動（例如留言發送）。
2. 用 `useOptimistic` 在送出瞬間先加上 `pending` 項目。
3. 送出後等待 server 回傳真實 id。
4. 成功時以真實資料取代暫存資料。
5. 失敗時刪除暫存資料並顯示錯誤。
6. 對重排序或篩選使用 `startTransition`。
7. 在 UI 區分 urgent（輸入）與 transition（結果）。
8. 驗證慢網路下輸入不會卡頓。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：實作留言板 optimistic 新增。

驗收條件：
- 點送出後留言立即出現在列表。
- pending 留言有視覺標記。
- 成功後 pending 狀態會移除。

### 進階任務 (Advanced)
任務：加入 `startTransition` 到搜尋過濾。

驗收條件：
- 輸入框保持順暢。
- 大列表重算不阻塞輸入。
- transition 中有提示文字。

### 挑戰任務 (Challenge)
任務：加入錯誤回滾與重試。

驗收條件：
- 失敗後 optimistic 項目正確移除。
- UI 顯示錯誤與 retry。
- 重試成功後資料一致。

## Reference Solution

```tsx
"use client";

import { startTransition, useOptimistic, useState } from "react";

type Comment = { id: string; text: string; pending?: boolean };

export function CommentComposer({ initial }: { initial: Comment[] }) {
  const [comments, setComments] = useState<Comment[]>(initial);
  const [optimisticComments, addOptimistic] = useOptimistic(comments, (state, text: string) => [
    ...state,
    { id: `temp-${Date.now()}`, text, pending: true },
  ]);

  async function submit(text: string) {
    addOptimistic(text);
    try {
      const res = await fetch("/api/comments", { method: "POST", body: JSON.stringify({ text }) });
      if (!res.ok) throw new Error("Create comment failed");
      const saved = (await res.json()) as Comment;
      setComments((prev) => [...prev, saved]);
    } catch {
      setComments((prev) => prev);
    }
  }

  function onFilter(keyword: string) {
    startTransition(() => {
      setComments((prev) => prev.filter((c) => c.text.toLowerCase().includes(keyword.toLowerCase())));
    });
  }

  return (
    <section>
      <button onClick={() => submit("hello")}>Send demo comment</button>
      <button onClick={() => onFilter("hello")}>Filter hello</button>
      <ul>
        {optimisticComments.map((c) => (
          <li key={c.id}>{c.text} {c.pending ? "(pending)" : ""}</li>
        ))}
      </ul>
    </section>
  );
}
```

## Common Pitfalls

- transition 包住輸入 state，反而造成輸入延遲。
- optimistic 項目沒有唯一臨時 id，導致 merge 混亂。
- 失敗時未 rollback，畫面與後端資料不一致。
- 在 Next.js server-only 路由嘗試直接使用 client hook，邊界錯誤。

## Checklist

- [ ] optimistic 項目可辨識（pending 標記）。
- [ ] 失敗回滾行為有實測。
- [ ] transition 只包非緊急更新。
- [ ] 輸入過程在慢資料下仍順暢。
- [ ] 最終資料與 server 回傳一致。

## Further Reading (official links only)

- [React startTransition](https://react.dev/reference/react/startTransition)
- [React useOptimistic](https://react.dev/reference/react/useOptimistic)
- [Queueing a Series of State Updates](https://react.dev/learn/queueing-a-series-of-state-updates)
