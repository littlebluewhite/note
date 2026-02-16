---
title: Svelte 5 Capstone Product Delivery
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5, capstone]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "26"
level: advanced
stack: TypeScript + SvelteKit 2.51.x + Svelte 5.50.x
prerequisites: [svelte5_ch00_ch25]
---
# Svelte 5 Capstone Product Delivery

## Goal

以 SvelteKit 完成一個可上線的「多角色任務系統」模組，涵蓋 form actions、load、錯誤恢復、部署觀測。

銜接上一章：Advanced TypeScript。下一章預告：跨專案複用的 SvelteKit release template。

## Prerequisites

- 完成 `00-25` 章。
- 熟悉 `+page.server.ts`、`+layout.ts`、form actions。
- 可執行 `npm run check/test/build`。

## Core Concepts

1. runes + SvelteKit server boundary 要明確。
- 何時用：涉及資料更新與授權流程。
- 何時不用：純靜態展示頁。

2. 觀測與回滾是部署必要條件。
- 何時用：所有 production release。
- 何時不用：本地 demo。

3. 測試分層（component/integration/e2e）。
- 何時用：多模組功能。
- 何時不用：一次性原型。

## Step-by-step

1. 功能需求：角色登入、任務 CRUD、權限可見範圍。
2. 非功能需求：LCP <= 2.5s、error rate < 1%、500 response < 0.5%。
3. 觀測指標：load/action latency、4xx/5xx ratio、hydrate mismatch count。
4. 驗收腳本：`npm run lint && npm run check && npm run test && npm run build`。
5. 回歸清單：SSR 頁、表單提交流程、權限路徑、錯誤頁。
6. 做 rollback 演練並更新 runbook。

## Hands-on Lab

### Foundation
- 完成角色任務流程（至少 admin/member）。

### Advanced
- 加入 observability hook 與錯誤分類。

### Challenge
- 跑一次完整 release rehearsal（含 rollback）。

## Reference Solution

```ts
export const slo = {
  lcpMs: 2500,
  errorRate: 0.01,
  server5xxRate: 0.005,
} as const;
```

## Evidence

- Demo route: `/app/tasks`, `/app/admin`
- Commands: `npm run test`, `npm run build`
- Artifacts: `reports/svelte5-capstone/`

## Common Pitfalls

- server-only 程式碼誤放 client。
- form actions 成功/失敗分支未完整覆蓋。
- hydration 問題沒有保留追蹤資料。
- rollback 手冊存在但未演練。

## Checklist

- [ ] 功能需求可操作。
- [ ] 非功能指標有數據。
- [ ] 驗收腳本可重跑。
- [ ] 回歸清單可追蹤。
- [ ] rollback 演練已完成。

## Further Reading

- https://svelte.dev/docs
- https://kit.svelte.dev/docs
- https://playwright.dev/
