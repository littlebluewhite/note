---
title: Performance, Memoization, and React Compiler / 效能、記憶化與 React Compiler
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "16"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [15_error_boundaries_not_found_and_recovery]
---
# Performance, Memoization, and React Compiler / 效能、記憶化與 React Compiler

## Goal

本章目標是建立「先量測、後優化」流程，避免盲目加 memo，並理解 React Compiler 在新版本中的角色。

銜接上一章：你已把錯誤流程穩定，現在可以安全地處理效能問題。

下一章預告：第 17 章會把這些關鍵互動寫成測試，避免優化後回歸。

## Prerequisites

- 已完成第 15 章。
- 了解 `memo`, `useMemo`, `useCallback` 基本語法。
- 能使用 React DevTools。

## Core Concepts

1. Measure before optimize
- 何時用：任何效能優化前都要先拿 profiler 證據。
- 何時不用：憑感覺到處 memo。

2. Memoization cost model
- 何時用：昂貴計算或頻繁重渲染熱點。
- 何時不用：簡單運算與低頻 component。

3. React Compiler mindset
- 何時用：以可分析、純函式、穩定資料流撰碼，讓編譯器更容易優化。
- 何時不用：期待 compiler 自動修正所有架構問題。

4. React 19.2 delta-aware optimization
- 何時用：需要把新 API（Activity、`useEffectEvent`、`cacheSignal`、`prerender/resume`）納入性能決策。
- 何時不用：沿用舊版心智模型，不檢查 runtime/static 渲染新能力。

## Step-by-step

1. 定義效能目標（例如輸入延遲 < 50ms）。
2. 用 React Profiler 記錄 baseline。
3. 找出熱點 component 與重渲染原因。
4. 對昂貴衍生資料加 `useMemo`。
5. 對 callback 傳遞熱點加 `useCallback`。
6. 以 `memo` 包覆純展示元件。
7. 再量測並比較前後差異。
8. 記錄哪些優化保留、哪些回退。

## React 19.2 Delta (as of 2026-02-14)

- `Activity API`
  - 用途：將不在前景的 UI 樹降載，保留狀態但降低背景工作成本。
  - 何時考慮：大型分頁/側邊欄切換，需保留 state 又不想持續高頻更新。
- `useEffectEvent`
  - 用途：把 effect 內事件回呼與依賴管理拆開，降低 stale closure 與過度重跑。
  - 何時考慮：effect 中有 callback 註冊（socket、event bus、timer）且依賴頻繁變動。
- `cacheSignal`
  - 用途：在 cache 流程中傳遞中止訊號，減少無效計算與浪費資源。
  - 何時考慮：server 端有可取消的昂貴計算或資料準備流程。
- `react-dom/static` 的 `prerender` / `resume`
  - 用途：先預渲染再恢復，優化靜態輸出與回復流程。
  - 何時考慮：靜態站點輸出、預計算內容、需要更細緻控制 render pipeline 的場景。
- 章節連動：
  - 與第 13 章（Suspense/Streaming）一起評估 loading 策略。
  - 與第 11 章（Server/Client 邊界）一起評估 server-side 成本。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：優化 1,000 筆列表的搜尋輸入體驗。

驗收條件：
- 輸入不卡頓。
- 搜尋結果正確。
- profiler 顯示主要熱點下降。

### 進階任務 (Advanced)
任務：拆分熱點 component 並加 memo。

驗收條件：
- 無關 state 更新不再重渲染列表。
- callback 穩定，不反覆產生新引用。
- 優化前後有數據對比。

### 挑戰任務 (Challenge)
任務：建立 performance note，記錄 compiler-ready coding rules。

驗收條件：
- 列出 5 條可執行規則。
- 每條規則有正反例。
- 團隊可據此做 code review。

## Reference Solution

```tsx
"use client";

import { memo, useCallback, useMemo, useState } from "react";

type Item = { id: string; name: string };

const ItemRow = memo(function ItemRow({ item, onSelect }: { item: Item; onSelect: (id: string) => void }) {
  return <li onClick={() => onSelect(item.id)}>{item.name}</li>;
});

export default function ItemSearch({ items }: { items: Item[] }) {
  const [keyword, setKeyword] = useState("");
  const [selected, setSelected] = useState<string | null>(null);

  const visible = useMemo(() => {
    const k = keyword.trim().toLowerCase();
    if (!k) return items;
    return items.filter((item) => item.name.toLowerCase().includes(k));
  }, [items, keyword]);

  const onSelect = useCallback((id: string) => {
    setSelected(id);
  }, []);

  return (
    <section>
      <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="Search" />
      <p>Selected: {selected ?? "none"}</p>
      <ul>
        {visible.map((item) => (
          <ItemRow key={item.id} item={item} onSelect={onSelect} />
        ))}
      </ul>
    </section>
  );
}
```

```tsx
"use client";

import { useEffect, useEffectEvent } from "react";

type Props = { roomId: string; onConnected: (roomId: string) => void };
declare function createConnection(roomId: string): {
  on: (event: "connected", handler: () => void) => void;
  connect: () => void;
  disconnect: () => void;
};

export function ChatConnection({ roomId, onConnected }: Props) {
  const onConnectedEvent = useEffectEvent(() => {
    onConnected(roomId);
  });

  useEffect(() => {
    const connection = createConnection(roomId);
    connection.on("connected", onConnectedEvent);
    connection.connect();
    return () => connection.disconnect();
  }, [roomId, onConnectedEvent]);

  return null;
}
```

## Common Pitfalls

- 無 profiler 證據就加 `memo`，程式更難讀卻無效益。
- `useCallback` 依賴錯誤導致舊資料閉包。
- `useMemo` 包非常便宜計算，反增心智負擔。
- 在 Next.js server/client 邊界中錯置優化邏輯，導致 bundle 反而變大。

## Checklist

- [ ] 已保存一份優化前 profiler 截圖或數據。
- [ ] 已保存一份優化後 profiler 截圖或數據。
- [ ] 至少移除 1 個無效 memo。
- [ ] 熱點 component re-render 次數下降。
- [ ] 有一份簡短 performance note 記錄決策。

## Further Reading (official links only)

- [React memo](https://react.dev/reference/react/memo)
- [React useMemo](https://react.dev/reference/react/useMemo)
- [React Compiler v1](https://react.dev/blog/2025/10/07/react-compiler-1)
- [React 19.2](https://react.dev/blog/2025/10/01/react-19-2)
- [React useEffectEvent](https://react.dev/reference/react/useEffectEvent)
