---
title: Zustand 5 Capstone State Platform Delivery
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, zustand5, capstone]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: zustand5_complete_notes
chapter: "20"
level: advanced
stack: TypeScript + React 19 + Next.js 16 + Zustand 5
prerequisites: [zustand5_ch00_ch19]
---
# Zustand 5 Capstone State Platform Delivery

## Goal

完成一個多模組狀態平台（user/session/preferences/tasks），驗證效能、一致性、韌性與交付流程。

銜接上一章：升級治理。下一章預告：跨模組 store governance 標準化。

## Prerequisites

- 完成 `00-19` 章。
- 熟悉 slices、persist、selector、SSR hydration。
- 可執行測試與 build。

## Core Concepts

1. store 契約是長期維護核心。
- 何時用：多團隊共享狀態。
- 何時不用：單頁簡單狀態。

2. 訂閱策略要受控。
- 何時用：複雜 UI 與高互動頁。
- 何時不用：小型靜態頁。

3. recoverability 是交付要求。
- 何時用：持續部署。
- 何時不用：無上線壓力。

## Step-by-step

1. 功能需求：登入態、偏好設定、任務清單、跨頁同步。
2. 非功能需求：hydrate mismatch = 0、重渲染數下降、錯誤可恢復。
3. 觀測指標：selector hit、render count、persist consistency。
4. 驗收腳本：`npm run lint && npm run test && npm run build`。
5. 回歸清單：SSR 首屏、重整持久化、錯誤注入恢復、跨頁一致性。
6. 回滾演練：版本切換與資料相容驗證。

## Hands-on Lab

### Foundation
- 完成多模組 store（至少 4 slices）。

### Advanced
- 完成 selector/perf profiling 並優化。

### Challenge
- 執行 persist corruption 演練與恢復流程。

## Reference Solution

```ts
export type AppState = {
  session: SessionSlice;
  preferences: PreferencesSlice;
  tasks: TasksSlice;
  ui: UiSlice;
};
```

## Evidence

- Demo route: `/dashboard`, `/settings`, `/tasks`
- Commands: `npm run test`, `npm run build`
- Artifacts: `reports/zustand-capstone/`

## Common Pitfalls

- store 責任混雜，action 互相耦合。
- selector 過大導致大量重渲染。
- persist schema 變更未做 migration。
- SSR/hydration path 未覆蓋測試。

## Checklist

- [ ] 功能需求模組完成。
- [ ] 非功能需求有證據。
- [ ] 驗收腳本可重跑。
- [ ] 回歸清單逐項驗證。
- [ ] rollback/migration 演練完成。

## Further Reading

- https://zustand.docs.pmnd.rs/
- https://github.com/pmndrs/zustand
- https://nextjs.org/docs
