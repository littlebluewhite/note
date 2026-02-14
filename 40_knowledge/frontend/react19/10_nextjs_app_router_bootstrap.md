---
title: Next.js App Router Bootstrap / Next.js App Router 起手式
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "10"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [09_custom_hooks_and_reuse_patterns]
---
# Next.js App Router Bootstrap / Next.js App Router 起手式

## Goal

本章目標是把前面 React 基礎遷移到 Next.js 16 App Router，建立可持續擴充的專案骨架。

銜接上一章：你已能抽象 hook，現在要把這些邏輯放進 framework 的路由與渲染模型。

下一章預告：第 11 章會深入 server/client 邊界，避免把整個 app 都變成 client component。

## Prerequisites

- 已完成第 09 章。
- 可使用 `create-next-app` 建立專案。
- 理解 layout 與 page 的角色。

## Core Concepts

1. App Router file conventions
- 何時用：你使用 Next.js 13+ 的 `app/` 架構。
- 何時不用：舊專案在 `pages/` 可先維持，但新專案不建議。

2. Server-first rendering model
- 何時用：初始資料與 SEO 內容適合放 server component。
- 何時不用：需要瀏覽器事件與即時互動的區塊。

3. Route groups and layout composition
- 何時用：不同區塊共用不同 layout（marketing vs dashboard）。
- 何時不用：只有單頁 demo，過度分組會增加結構噪音。

## Step-by-step

1. 用 `create-next-app` 建立 `react19-lab`。
2. 清理預設首頁內容，保留最小可讀結構。
3. 建立 `src/app/(marketing)/page.tsx`。
4. 建立 `src/app/dashboard/page.tsx`。
5. 在 `src/app/layout.tsx` 放全域框架與 metadata。
6. 新增 `src/components/nav.tsx` 做共用導覽。
7. 為 dashboard 子路由建立專屬 layout。
8. 驗證 route、layout、metadata 三者都正常。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：建立 `about`、`dashboard`、`settings` 三個頁面。

驗收條件：
- 三條路由可訪問。
- 每頁有唯一 `<h1>`。
- `npm run dev` 無 routing 錯誤。

### 進階任務 (Advanced)
任務：建立 `(marketing)` 與 `(app)` route groups。

驗收條件：
- marketing 與 app 使用不同 layout 樣式。
- app 區塊有導覽列與側邊欄。
- route group 不影響 URL 路徑。

### 挑戰任務 (Challenge)
任務：在 dashboard 加入 server-rendered summary 區塊與 client filter 控制。

驗收條件：
- summary 由 server component 渲染。
- filter 為 client component 且只影響局部。
- 無不必要 `"use client"` 汙染。

## Reference Solution

```tsx
// src/app/layout.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "React 19 Lab",
  description: "TypeScript + Next.js 16 + React 19.2.x",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header>
          <a href="/">Home</a> | <a href="/dashboard">Dashboard</a> | <a href="/about">About</a>
        </header>
        {children}
      </body>
    </html>
  );
}

// src/app/dashboard/page.tsx
export default async function DashboardPage() {
  return (
    <main>
      <h1>Dashboard</h1>
      <p>Server-rendered summary area.</p>
    </main>
  );
}
```

## Common Pitfalls

- 見到互動就整頁加 `"use client"`，導致 server 優勢消失。
- route group 命名不清，後續維護困難。
- 將資料抓取都丟到 client，造成首屏負擔。
- 在 Server Component 直接使用 `window` 或 DOM API，違反邊界。

## Checklist

- [ ] 至少建立 3 條可訪問路由。
- [ ] `layout.tsx` 已定義 `metadata`。
- [ ] marketing/app 區塊能用不同 layout 呈現。
- [ ] dashboard 首屏可在無 JS 互動下顯示基本內容。
- [ ] 程式碼中 `"use client"` 僅出現在互動元件。

## Further Reading (official links only)

- [App Router](https://nextjs.org/docs/app)
- [Pages and Layouts](https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts)
- [Server and Client Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
