---
title: Effects and Common Side-effect Patterns / Effect 與常見副作用模式
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "06"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [05_events_forms_and_controlled_inputs]
---
# Effects and Common Side-effect Patterns / Effect 與常見副作用模式

## Goal

本章目標是把「需要和外部系統同步」的邏輯放在 `useEffect`，同時避免把純運算誤塞進 effect。

銜接上一章：你已能處理表單事件，現在要處理事件之外的副作用（訂閱、計時器、網路同步）。

下一章預告：第 07 章會將 effect 應用在資料抓取，並補上取消請求與 race condition。

## Prerequisites

- 已完成第 05 章。
- 能分辨 state 更新與事件處理。
- 了解 `cleanup` 函式概念。

## Core Concepts

1. Effect is for external sync
- 何時用：要同步 DOM API、browser event、timer、websocket。
- 何時不用：可在 render 直接算出的值，不要放 effect。

2. Dependency array as contract
- 何時用：明確描述 effect 依賴哪些 reactive 值。
- 何時不用：用空依賴陣列硬壓警告，通常會導致 stale data。

3. Cleanup to prevent stale subscriptions
- 何時用：有 add/remove、start/stop、subscribe/unsubscribe 成對操作時。
- 何時不用：沒有副作用時不需要寫空 cleanup。

## Step-by-step

1. 在 `src/app/online-status/page.tsx` 建立 client component。
2. 先實作 `useOnlineStatus`，訂閱 `online/offline`。
3. 在 effect 中回傳 cleanup 移除事件監聽。
4. 顯示 `online` 狀態與最後變更時間。
5. 再新增 `useWindowWidth`，觀察 resize 監聽模式。
6. 比較「直接 render 計算」與「effect 計算」的差異。
7. 刪除不必要 effect，保持最小副作用面積。
8. 使用 React DevTools 檢查不必要 re-render。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：實作 `useOnlineStatus` 與 UI 指示。

驗收條件：
- 切換網路後畫面文字會更新。
- 重新整理頁面不會重複綁定監聽。
- cleanup 存在且可正常執行。

### 進階任務 (Advanced)
任務：實作 `useDocumentTitle`，根據表單狀態更新頁面標題。

驗收條件：
- `title` 變動與 state 同步。
- 離開頁面時還原預設標題。
- 無 eslint effect dependency 警告。

### 挑戰任務 (Challenge)
任務：合併 `useOnlineStatus` + `useWindowWidth`，做一個環境資訊面板。

驗收條件：
- 在窄螢幕且離線時顯示明確警示。
- 任一 hook 拆除後不影響另一個 hook。
- 無 memory leak（多次切換 route 仍正常）。

## Reference Solution

```tsx
"use client";

import { useEffect, useMemo, useState } from "react";

function useOnlineStatus(): boolean {
  const [online, setOnline] = useState(
    typeof navigator === "undefined" ? true : navigator.onLine,
  );

  useEffect(() => {
    const onOnline = () => setOnline(true);
    const onOffline = () => setOnline(false);

    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  return online;
}

function useWindowWidth(): number {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const update = () => setWidth(window.innerWidth);
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  return width;
}

export default function OnlineStatusPage() {
  const online = useOnlineStatus();
  const width = useWindowWidth();
  const message = useMemo(() => {
    if (!online) return "Offline mode";
    if (width < 768) return "Online on small screen";
    return "Online on desktop";
  }, [online, width]);

  return (
    <main>
      <h1>Environment status</h1>
      <p>{message}</p>
      <p>Width: {width}px</p>
    </main>
  );
}
```

## Common Pitfalls

- 把 `filteredItems` 這類純計算結果放 effect 再 setState。
- 依賴陣列漏掉函式或 state，導致 stale closure。
- effect 內直接改 mutable 全域變數，難以除錯。
- 在 Next.js Server Component 誤用 `useEffect`，忘記 `"use client"` 邊界。

## Checklist

- [ ] `useOnlineStatus` 有 add/remove 成對處理。
- [ ] effect dependency 警告皆已解決而非忽略。
- [ ] 可指出至少一段「本來有 effect，後來移除」的改善。
- [ ] route 切換 10 次後功能仍正常（無重複監聽現象）。
- [ ] 所有自訂 hook 有明確回傳型別。

## Further Reading (official links only)

- [Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects)
- [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)
- [Lifecycle of Reactive Effects](https://react.dev/learn/lifecycle-of-reactive-effects)
