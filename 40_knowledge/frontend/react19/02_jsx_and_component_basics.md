---
title: JSX and Component Basics / JSX 與元件基礎
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "02"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [01_web_js_fundamentals_for_react]
---
# JSX and Component Basics / JSX 與元件基礎

## Goal

理解 JSX 如何描述 UI，並能拆出可重用 component。

## Prerequisites

- 已完成第 01 章。
- 知道函式與物件基本語法。

## Core Concepts

- JSX 是 JavaScript 語法擴充，不是模板字串。
- Component 本質是「輸入 props，輸出 UI」。
- 組件命名用 PascalCase，HTML tag 用小寫。
- Component 拆分重點：職責單一、可測試、可重用。

## Step-by-step

1. 在 Next.js `src/app/page.tsx` 建立第一個 component。
2. 新增 `src/components/ProfileCard.tsx`。
3. 用 props 控制內容與樣式 class。
4. 在 page 組合多個 `ProfileCard`。

範例：

```tsx
type ProfileCardProps = {
  name: string;
  role: string;
};

export function ProfileCard({ name, role }: ProfileCardProps) {
  return (
    <article>
      <h2>{name}</h2>
      <p>{role}</p>
    </article>
  );
}
```

## Hands-on Lab

任務：做一個 `FeatureList` 與 `FeatureItem`。

- `FeatureItem` 接收 `title` 與 `desc`。
- `FeatureList` 接收陣列並渲染多個 `FeatureItem`。
- 在首頁顯示 3 個特色項目。

驗收清單：

- props 型別完整。
- component 檔案位置清楚（`src/components`）。
- UI 能正確顯示 3 個項目。

## Reference Solution

```tsx
type Feature = { id: number; title: string; desc: string };

function FeatureItem({ title, desc }: Omit<Feature, "id">) {
  return (
    <li>
      <h3>{title}</h3>
      <p>{desc}</p>
    </li>
  );
}

export function FeatureList({ items }: { items: Feature[] }) {
  return (
    <ul>
      {items.map((item) => (
        <FeatureItem key={item.id} title={item.title} desc={item.desc} />
      ))}
    </ul>
  );
}
```

## Common Pitfalls

- 在 JSX 中使用 `class` 而非 `className`。
- 忘記最外層單一節點或 fragment。
- 將過多邏輯塞在同一個 component，難維護。

## Checklist

- [ ] 知道 JSX 與 HTML 差異。
- [ ] 會拆分基礎 component。
- [ ] 會定義 props 型別。
- [ ] 能在頁面組合多個 component。

## Further Reading (official links only)

- [Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx)
- [Your First Component](https://react.dev/learn/your-first-component)
- [Passing Props to a Component](https://react.dev/learn/passing-props-to-a-component)
