---
title: React 19 Capstone Product Delivery
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19, capstone]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: react19_complete_notes
chapter: "20"
level: advanced
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [react19_ch00_ch19]
---
# React 19 Capstone Product Delivery

## Goal

以 React 19 + Next.js App Router 完成一個可上線的「任務協作看板」功能模組，涵蓋 server actions、RSC 邊界、錯誤恢復與觀測。

銜接上一章：升級治理與安全維護。下一章預告：可直接複用到實際產品的交付模板。

## Prerequisites

- 完成 `00-19` 章。
- 能操作 Next.js App Router 與 server action。
- 可執行 lint/test/build/e2e 命令。

## Core Concepts

1. 功能需求與非功能需求同等重要。
- 何時用：正式上線功能。
- 何時不用：一次性 POC。

2. 觀測指標是 release gate 的一部分。
- 何時用：持續交付環境。
- 何時不用：無部署計畫的本地實驗。

3. 回歸清單要可重跑。
- 何時用：每次釋出。
- 何時不用：沒有版本管理的臨時頁。

## Step-by-step

1. 功能需求：建立/編輯/完成/刪除任務，支援 optimistic UI。
2. 非功能需求：LCP <= 2.5s、INP <= 200ms、CLS <= 0.1、error rate < 1%。
3. 觀測指標：action latency、error boundary hit、API failure ratio。
4. 驗收腳本：`npm run lint && npm run test && npm run build && npm run test:e2e`。
5. 回歸清單：核心路由、表單提交流程、錯誤恢復、資料一致性。
6. 執行 rollback drill，驗證可在 10 分鐘內回退。

## Hands-on Lab

### Foundation
- 完成功能需求中的 CRUD + optimistic UI。

### Advanced
- 加入錯誤邊界與可觀測事件（log/metric）。

### Challenge
- 完成一次 release + rollback 演練並產出報告。

## Reference Solution

```ts
export const releaseBudget = {
  lcpMs: 2500,
  inpMs: 200,
  cls: 0.1,
  errorRate: 0.01,
} as const;
```

## Evidence

- Demo route: `/tasks`, `/tasks/[id]`
- Commands: `npm run test:e2e`, `npm run build`
- Artifacts: `reports/react19-capstone/`（含 Lighthouse、Playwright、error log）

## Common Pitfalls

- 在 client component 放過多 server logic，邊界不清。
- 沒有 failure injection，導致錯誤路徑未驗證。
- optimistic UI 與 server state 無對帳。
- 指標監控存在但未連動 release gate。

## Checklist

- [ ] 功能需求 100% 覆蓋。
- [ ] 非功能需求有量測結果。
- [ ] 驗收腳本可重跑。
- [ ] 回歸清單逐項打勾。
- [ ] rollback drill 有時間與結果紀錄。

## Further Reading

- https://react.dev/
- https://nextjs.org/docs
- https://playwright.dev/
