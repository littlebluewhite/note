---
title: Props, State, and One-way Data Flow / Props、State 與單向資料流
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "03"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [02_jsx_and_component_basics]
---
# Props, State, and One-way Data Flow / Props、State 與單向資料流

## Goal

理解父子元件資料流方向，並能用 `useState` 管理互動狀態。

## Prerequisites

- 已完成第 02 章。
- 能建立基本 component。

## Core Concepts

- `props` 由父元件傳入，子元件不可直接修改。
- `state` 屬於 component 自己，透過 setter 觸發重渲染。
- React 採單向資料流，事件回呼用來向上回傳意圖。

## Step-by-step

1. 父元件維護 `count` state。
2. 子元件顯示數值與按鈕。
3. 由父元件傳遞 `onIncrement` callback。
4. 子元件點擊後通知父元件更新 state。

範例：

```tsx
import { useState } from "react";

function CounterView({ count, onIncrement }: { count: number; onIncrement: () => void }) {
  return (
    <section>
      <p>Count: {count}</p>
      <button onClick={onIncrement}>+1</button>
    </section>
  );
}

export default function CounterPage() {
  const [count, setCount] = useState(0);
  return <CounterView count={count} onIncrement={() => setCount((c) => c + 1)} />;
}
```

## Hands-on Lab

任務：製作「購物車項目計數器」。

- 父元件維護 `items` 與 `quantity`。
- 子元件顯示目前數量與 `+/-` 按鈕。
- 數量不能小於 0。

驗收清單：

- 所有 state 在父元件集中管理。
- 子元件只透過 props + callback 互動。
- 點擊後畫面即時更新。

## Reference Solution

```tsx
import { useState } from "react";

type QuantityProps = {
  quantity: number;
  onInc: () => void;
  onDec: () => void;
};

function QuantityControl({ quantity, onInc, onDec }: QuantityProps) {
  return (
    <div>
      <button onClick={onDec}>-</button>
      <span>{quantity}</span>
      <button onClick={onInc}>+</button>
    </div>
  );
}

export default function CartCounter() {
  const [quantity, setQuantity] = useState(0);
  return (
    <QuantityControl
      quantity={quantity}
      onInc={() => setQuantity((q) => q + 1)}
      onDec={() => setQuantity((q) => Math.max(0, q - 1))}
    />
  );
}
```

## Common Pitfalls

- 直接修改 props 或 state 物件。
- 把可由 props 計算出的值又存一份 state，造成不同步。
- callback 命名不清楚（如 `handle`, `do`, `run`）導致閱讀成本高。

## Checklist

- [ ] 能解釋 props 與 state 差異。
- [ ] 能實作父傳子、子回呼父。
- [ ] 知道何時不該新增 state。
- [ ] 能用函式型更新 `setState`。

## Further Reading (official links only)

- [State: A Component's Memory](https://react.dev/learn/state-a-components-memory)
- [Sharing State Between Components](https://react.dev/learn/sharing-state-between-components)
- [Responding to Events](https://react.dev/learn/responding-to-events)
