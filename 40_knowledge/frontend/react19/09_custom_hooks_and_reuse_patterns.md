---
title: Custom Hooks and Reuse Patterns / 自訂 Hook 與重用模式
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "09"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [08_context_and_reducer_state_management]
---
# Custom Hooks and Reuse Patterns / 自訂 Hook 與重用模式

## Goal

本章目標是把重複的狀態邏輯抽成 custom hook，讓 component 專注在 UI，邏輯專注在可測試函式。

銜接上一章：你已能用 Context + Reducer 管理共享狀態，現在要整理重複邏輯並降低元件複雜度。

下一章預告：第 10 章會正式進入 Next.js App Router，將前面 hook 與狀態管理帶到框架環境。

## Prerequisites

- 已完成第 08 章。
- 知道 hooks 規則（top-level call）。
- 熟悉 `useEffect` 與 `useMemo`。

## Core Concepts

1. Hook extracts behavior, not markup
- 何時用：多個 component 重複同一段 stateful logic。
- 何時不用：只在單一元件且很短的邏輯，不必過度抽象。

2. API design first
- 何時用：先定義 hook 輸入/輸出，減少後續 breaking change。
- 何時不用：邊寫邊猜介面，容易形成難用 hook。

3. Composition over monolith
- 何時用：拆成小 hook 組合（例如 debounce + fetch）。
- 何時不用：一個 hook 包太多責任，難測且難重用。

## Step-by-step

1. 找出重複邏輯（例如搜尋輸入防抖）。
2. 設計 `useDebouncedValue<T>(value, delay)` API。
3. 實作 effect + cleanup 處理計時器。
4. 補上泛型回傳型別。
5. 在兩個不同 component 套用同一 hook。
6. 再設計 `useAsyncTask` 管理 loading/error/result。
7. 把 UI 從 hook 中完全移除，保持無 JSX。
8. 為 hook 寫最小行為測試（可在第 17 章擴充）。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：完成 `useDebouncedValue` 並用在搜尋框。

驗收條件：
- 快速輸入時請求不會每字觸發。
- 停止輸入後延遲 300ms 才更新。
- unmount 後不會 setState。

### 進階任務 (Advanced)
任務：做 `useAsyncTask` 以統一非同步流程。

驗收條件：
- 有 `run`, `loading`, `error`, `result`。
- 連續觸發時前次結果不覆蓋新請求。
- 錯誤訊息可被上層 UI 顯示。

### 挑戰任務 (Challenge)
任務：把 `useDebouncedValue + useAsyncTask` 組成 `useDebouncedSearch`。

驗收條件：
- API 介面保持簡單（輸入 keyword，輸出 triad）。
- 支援可配置 delay。
- 型別可推斷結果資料形狀。

## Reference Solution

```tsx
"use client";

import { useEffect, useState } from "react";

export function useDebouncedValue<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState<T>(value);

  useEffect(() => {
    const id = window.setTimeout(() => setDebounced(value), delay);
    return () => window.clearTimeout(id);
  }, [value, delay]);

  return debounced;
}

type AsyncState<T> = { loading: boolean; error: string; result: T | null };

export function useAsyncTask<T>() {
  const [state, setState] = useState<AsyncState<T>>({ loading: false, error: "", result: null });

  async function run(task: () => Promise<T>) {
    setState((prev) => ({ ...prev, loading: true, error: "" }));
    try {
      const result = await task();
      setState({ loading: false, error: "", result });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setState({ loading: false, error: message, result: null });
    }
  }

  return { ...state, run };
}
```

## Common Pitfalls

- 在 hook 內寫 JSX，讓重用性下降。
- hook 命名不含 `use`，破壞規則與可讀性。
- 參數過多且含 UI 細節，導致 hook 難以抽換。
- 在 Next.js server 檔案匯入需要 browser API 的 hook，造成邊界錯誤。

## Checklist

- [ ] 至少抽出 2 個 custom hooks。
- [ ] 每個 hook 都有明確輸入與輸出型別。
- [ ] hook 檔案不包含 JSX。
- [ ] 至少 1 個 hook 被兩個元件重用。
- [ ] 路由切換與重整後不出現計時器殘留錯誤。

## Further Reading (official links only)

- [Reusing Logic with Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [Rules of Hooks](https://react.dev/reference/rules/rules-of-hooks)
- [Removing Effect Dependencies](https://react.dev/learn/removing-effect-dependencies)
