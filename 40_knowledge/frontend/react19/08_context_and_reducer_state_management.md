---
title: Context and Reducer State Management / Context 與 Reducer 狀態管理
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "08"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [07_data_fetching_client_patterns]
---
# Context and Reducer State Management / Context 與 Reducer 狀態管理

## Goal

本章目標是把跨元件共享狀態從「多層 props 傳遞」提升到「Context + Reducer」的可維護架構。

銜接上一章：你已能抓資料與處理錯誤，現在要管理多元件共同使用的狀態。

下一章預告：第 09 章會把可重用邏輯抽成 custom hooks，降低 Context 層噪音。

## Prerequisites

- 已完成第 07 章。
- 熟悉 `useState` 與 immutable update。
- 知道 action 與 reducer 基本概念。

## Core Concepts

1. Context as dependency injection channel
- 何時用：多個深層元件都需要同一份資料或 dispatch。
- 何時不用：只在兩層內傳遞 props，props 更直覺。

2. Reducer as state transition registry
- 何時用：狀態更新規則多且需要集中管理。
- 何時不用：只有單一簡單布林值切換。

3. Split contexts for performance
- 何時用：把 `state` 和 `dispatch` 分離，減少重渲染。
- 何時不用：小型 demo 可先單 context，過早優化沒有必要。

## Step-by-step

1. 建立 `TodoState`, `TodoAction` 型別。
2. 寫純函式 `todoReducer(state, action)`。
3. 建立 `TodoStateContext` 與 `TodoDispatchContext`。
4. 在 `TodoProvider` 用 `useReducer` 包裝 children。
5. 寫 `useTodoState()` 與 `useTodoDispatch()` hook。
6. 在 page 層放置 provider，避免整個 app 全域包覆。
7. 把新增/切換/刪除都改為 dispatch action。
8. 為 reducer 補 default case 與不可達檢查。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：建立 Todo Provider，完成新增與切換完成。

驗收條件：
- 可新增至少 3 筆 todo。
- 點擊可切換 `done` 狀態。
- reducer 不直接 mutate state。

### 進階任務 (Advanced)
任務：加入刪除與篩選（all/done/todo）。

驗收條件：
- 刪除後畫面即時更新。
- 篩選結果正確且不改動原資料。
- `Action` type 有清楚 discriminated union。

### 挑戰任務 (Challenge)
任務：加入 localStorage 持久化（client only）。

驗收條件：
- 重新整理後資料仍存在。
- hydrate 時不報錯。
- 載入失敗時會回退到空陣列。

## Reference Solution

```tsx
"use client";

import { createContext, useContext, useMemo, useReducer } from "react";

type Todo = { id: string; text: string; done: boolean };
type TodoState = { items: Todo[]; filter: "all" | "done" | "todo" };

type TodoAction =
  | { type: "add"; text: string }
  | { type: "toggle"; id: string }
  | { type: "remove"; id: string }
  | { type: "filter"; filter: TodoState["filter"] };

const initialState: TodoState = { items: [], filter: "all" };

function todoReducer(state: TodoState, action: TodoAction): TodoState {
  switch (action.type) {
    case "add":
      return {
        ...state,
        items: [...state.items, { id: crypto.randomUUID(), text: action.text, done: false }],
      };
    case "toggle":
      return {
        ...state,
        items: state.items.map((item) => (item.id === action.id ? { ...item, done: !item.done } : item)),
      };
    case "remove":
      return { ...state, items: state.items.filter((item) => item.id !== action.id) };
    case "filter":
      return { ...state, filter: action.filter };
    default:
      return state;
  }
}

const TodoStateContext = createContext<TodoState | null>(null);
const TodoDispatchContext = createContext<React.Dispatch<TodoAction> | null>(null);

export function TodoProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(todoReducer, initialState);
  const stableState = useMemo(() => state, [state]);
  return (
    <TodoStateContext.Provider value={stableState}>
      <TodoDispatchContext.Provider value={dispatch}>{children}</TodoDispatchContext.Provider>
    </TodoStateContext.Provider>
  );
}

export function useTodoState() {
  const ctx = useContext(TodoStateContext);
  if (!ctx) throw new Error("useTodoState must be used inside TodoProvider");
  return ctx;
}

export function useTodoDispatch() {
  const ctx = useContext(TodoDispatchContext);
  if (!ctx) throw new Error("useTodoDispatch must be used inside TodoProvider");
  return ctx;
}
```

## Common Pitfalls

- 把 `dispatch` 與 `state` 混在同 context，導致無關元件重渲染。
- reducer 裡直接 `push` 或改動既有物件。
- action payload 沒型別約束，埋下 runtime bug。
- 在 Server Component 中直接使用 Context hook，忽略 `"use client"` 邊界。

## Checklist

- [ ] `TodoAction` 使用 union type，不是 `any`。
- [ ] reducer 每個 case 都回傳新 state。
- [ ] provider 僅包覆需要共享狀態的路由區塊。
- [ ] `useTodoState` 與 `useTodoDispatch` 有錯誤保護。
- [ ] 至少完成 1 次 reload 後持久化驗證。

## Further Reading (official links only)

- [Passing Data Deeply with Context](https://react.dev/learn/passing-data-deeply-with-context)
- [Extracting State Logic into a Reducer](https://react.dev/learn/extracting-state-logic-into-a-reducer)
- [Scaling Up with Reducer and Context](https://react.dev/learn/scaling-up-with-reducer-and-context)
