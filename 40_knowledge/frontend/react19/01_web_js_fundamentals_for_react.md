---
title: Web + JavaScript Fundamentals for React / React 前的 Web 與 JS 基礎
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "01"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [00_series_overview]
---
# Web + JavaScript Fundamentals for React / React 前的 Web 與 JS 基礎

## Goal

在接觸 component 前，先掌握 React 最常用的 JavaScript 思維：不可變資料、函式組合、陣列轉換與事件流程。

## Prerequisites

- 已完成 `00_series_overview`。
- 可執行 Node.js 指令。

## Core Concepts

- Value vs Reference：物件/陣列複製要避免直接 mutate。
- 常用陣列 API：`map`, `filter`, `find`, `reduce`。
- Arrow function 與解構賦值是 JSX 常態語法。
- Promise/async 是 client data fetching 與 Server Actions 的基礎。

## Step-by-step

1. 用 TypeScript 寫出不可變更新模式。
2. 練習把 imperative loop 改寫成 declarative 陣列操作。
3. 理解事件 callback 為何通常傳 function reference。
4. 理解 `null`、`undefined` 與條件渲染關係。

範例：不可變更新。

```ts
type Todo = { id: number; text: string; done: boolean };

const todos: Todo[] = [
  { id: 1, text: "read", done: false },
  { id: 2, text: "code", done: false },
];

const next = todos.map((t) => (t.id === 2 ? { ...t, done: true } : t));
```

## Hands-on Lab

任務：在 `learning-log.md` 旁新增 `js-drills.ts`，完成以下函式。

- `toggleById(items, id)`：回傳新陣列，不可 mutate 原陣列。
- `completedCount(items)`：回傳 `done === true` 的數量。
- `visibleItems(items, keyword)`：文字過濾。

驗收清單：

- 原始 `items` 內容不被改寫。
- 三個函式可獨立執行。
- 有最少 3 組測試資料。

## Reference Solution

```ts
type Item = { id: number; text: string; done: boolean };

export function toggleById(items: Item[], id: number): Item[] {
  return items.map((item) => (item.id === id ? { ...item, done: !item.done } : item));
}

export function completedCount(items: Item[]): number {
  return items.filter((item) => item.done).length;
}

export function visibleItems(items: Item[], keyword: string): Item[] {
  const k = keyword.trim().toLowerCase();
  if (!k) return items;
  return items.filter((item) => item.text.toLowerCase().includes(k));
}
```

## Common Pitfalls

- 用 `push/splice` 改動 state 來源，造成 React 不重渲染或行為錯誤。
- 在 `map` 裡忘記 `return`。
- 把 async function 直接塞到不該 async 的 callback，導致錯誤難追。

## Checklist

- [ ] 知道何時要用 immutable update。
- [ ] 熟悉 `map/filter/reduce`。
- [ ] 能寫出基本 `async/await`。
- [ ] 能讀懂 TS 型別註記。

## Further Reading (official links only)

- [Learn JavaScript for React](https://react.dev/learn/javascript-in-jsx-with-curly-braces)
- [Describing the UI](https://react.dev/learn/describing-the-ui)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
