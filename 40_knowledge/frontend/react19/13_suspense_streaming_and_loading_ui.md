---
title: Suspense, Streaming, and Loading UI / Suspense、串流與 Loading UI
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "13"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [12_server_actions_and_form_workflows]
---
# Suspense, Streaming, and Loading UI / Suspense、串流與 Loading UI

## Goal

本章目標是透過 Suspense 與 Streaming 讓頁面「先快顯示骨架，再分段補齊內容」，提升體感速度。

銜接上一章：你已能提交資料與回饋，現在要優化等待過程的 UX。

下一章預告：第 14 章會進一步處理互動中的優先級與 optimistic 更新。

## Prerequisites

- 已完成第 12 章。
- 理解 server/client 邊界。
- 了解 loading UI 基本概念。

## Core Concepts

1. Suspense boundary design
- 何時用：某區塊資料慢、但頁面其他區塊可先顯示。
- 何時不用：整頁都放同一 boundary，失去分段渲染價值。

2. Streaming response
- 何時用：server 可先送初始框架，再送慢區塊內容。
- 何時不用：非常小且瞬間完成的頁面。

3. Fallback quality
- 何時用：fallback 應盡量貼近最終布局，減少 layout shift。
- 何時不用：用與最終版面差異過大的 placeholder。

## Step-by-step

1. 選定慢區塊（例如報表 table）與快區塊（標題/摘要）。
2. 將慢區塊抽成獨立 server component。
3. 在父頁面使用 `<Suspense fallback={...}>` 包覆。
4. 設計尺寸接近的 fallback skeleton。
5. 在 route 層新增 `loading.tsx` 作為全局 loading。
6. 觀察初始回應是否先顯示快區塊。
7. 量測 LCP 與互動可見時間。
8. 依觀察調整 boundary 粒度。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：在 dashboard 中把 `ReportTable` 包成 suspense 區塊。

驗收條件：
- 首屏能先顯示標題與摘要。
- 慢資料區塊顯示 fallback。
- 資料完成後自動替換 fallback。

### 進階任務 (Advanced)
任務：實作兩層 boundary（summary、table）。

驗收條件：
- summary 較快完成，table 可稍後出現。
- 任一區塊失敗不拖累整頁。
- loading 文案區分區塊責任。

### 挑戰任務 (Challenge)
任務：對慢 API 模擬 1.5s 延遲，優化 fallback 視覺穩定性。

驗收條件：
- layout shift 可明顯下降。
- fallback 尺寸接近實際內容。
- 使用者可理解目前等待的是哪個區塊。

## Reference Solution

```tsx
// src/app/dashboard/page.tsx
import { Suspense } from "react";
import { DashboardSummary } from "@/components/dashboard-summary";
import { ReportTable } from "@/components/report-table";

export default function DashboardPage() {
  return (
    <main>
      <h1>Dashboard</h1>

      <Suspense fallback={<p>Loading summary...</p>}>
        <DashboardSummary />
      </Suspense>

      <Suspense fallback={<TableSkeleton />}>
        <ReportTable />
      </Suspense>
    </main>
  );
}

function TableSkeleton() {
  return (
    <div aria-busy="true">
      <p>Loading report table...</p>
      <div style={{ height: 220, background: "#f2f2f2" }} />
    </div>
  );
}
```

## Common Pitfalls

- fallback 過於簡化，導致內容載入時版面跳動。
- 把所有慢區塊包在同一個 suspense，無法分段呈現。
- loading.tsx 與局部 fallback 責任重疊。
- 在 client-only 區塊過度依賴 Suspense，忽略 Next.js server streaming 優勢。

## Checklist

- [ ] 至少有 1 個 route-level loading 與 1 個 component-level suspense。
- [ ] fallback 高度與最終內容接近。
- [ ] 首屏可先看到非慢區塊內容。
- [ ] 模擬慢網路下仍可讀出頁面主結構。
- [ ] 無大量 layout shift 主觀閃爍問題。

## Further Reading (official links only)

- [React Suspense](https://react.dev/reference/react/Suspense)
- [Next.js Loading UI and Streaming](https://nextjs.org/docs/app/building-your-application/routing/loading-ui-and-streaming)
- [Streaming](https://nextjs.org/docs/app/building-your-application/routing/loading-ui-and-streaming#streaming-with-suspense)
