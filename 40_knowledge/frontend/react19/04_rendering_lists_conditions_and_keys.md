---
title: Rendering Lists, Conditions, and Keys / 清單渲染、條件渲染與 Key
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "04"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [03_props_state_and_one_way_data_flow]
---
# Rendering Lists, Conditions, and Keys / 清單渲染、條件渲染與 Key

## Goal

掌握 React 最常見的畫面控制技術：`map` 渲染清單、條件判斷、穩定 key。

## Prerequisites

- 已完成第 03 章。
- 熟悉陣列 `map`。

## Core Concepts

- 清單渲染使用 `array.map` 產生 JSX。
- 條件渲染可用 `if`, `?:`, `&&`。
- `key` 用於辨識清單項目的身份，應使用穩定唯一 id。

## Step-by-step

1. 建立 `TaskList` component 接收 task 陣列。
2. 透過 `map` 轉成 `<li>`。
3. 用 `task.done` 控制顯示狀態。
4. 使用 `task.id` 作為 key。

範例：

```tsx
type Task = { id: string; text: string; done: boolean };

export function TaskList({ tasks }: { tasks: Task[] }) {
  if (tasks.length === 0) return <p>No tasks yet.</p>;

  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.id}>{task.done ? "[Done]" : "[Todo]"} {task.text}</li>
      ))}
    </ul>
  );
}
```

## Hands-on Lab

任務：建立可篩選的待辦清單。

- `filter = all | done | todo`。
- 依條件渲染不同項目。
- 空資料時顯示提示。

驗收清單：

- 每個清單項目使用穩定 key。
- 切換 filter 時畫面正確。
- 空狀態文案清楚。

## Reference Solution

```tsx
type Filter = "all" | "done" | "todo";
type Task = { id: string; text: string; done: boolean };

export function getVisible(tasks: Task[], filter: Filter): Task[] {
  if (filter === "done") return tasks.filter((t) => t.done);
  if (filter === "todo") return tasks.filter((t) => !t.done);
  return tasks;
}

export function TodoList({ tasks, filter }: { tasks: Task[]; filter: Filter }) {
  const visible = getVisible(tasks, filter);
  if (visible.length === 0) return <p>Nothing here.</p>;

  return (
    <ul>
      {visible.map((task) => (
        <li key={task.id}>{task.text}</li>
      ))}
    </ul>
  );
}
```

## Common Pitfalls

- 用陣列 index 當 key，導致重排後狀態錯置。
- `&&` 條件渲染遇到 `0` 時意外顯示 `0`。
- 在 render 階段做高成本運算而不抽離。

## Checklist

- [ ] 會寫清單渲染。
- [ ] 會寫基本條件渲染。
- [ ] 知道 key 要用穩定 id。
- [ ] 會處理空狀態。

## Further Reading (official links only)

- [Rendering Lists](https://react.dev/learn/rendering-lists)
- [Conditional Rendering](https://react.dev/learn/conditional-rendering)
- [Keeping List Items in Order with key](https://react.dev/learn/rendering-lists#keeping-list-items-in-order-with-key)
