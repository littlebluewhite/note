---
title: Upgrade, Security, and Monthly Update Playbook / 升級、安全與每月更新手冊
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, zustand5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: zustand5_complete_notes
chapter: "19"
level: beginner
stack: "TypeScript + React 19 + Next.js 16 App Router + Zustand 5.0.11"
prerequisites: [18_deployment_observability_and_runtime_debug_workflow]
---
# Upgrade, Security, and Monthly Update Playbook / 升級、安全與每月更新手冊

## Goal

本章目標是完成「制度化 Zustand/React/Next 升級決策」，並把 v5 API 正確性與 persist 一致性檢核納入每月流程。

- 銜接上一章：`18_deployment_observability_and_runtime_debug_workflow`。
- 下一章預告：`series_complete`。

## Prerequisites

- 已完成 `18_deployment_observability_and_runtime_debug_workflow`。
- 熟悉 TypeScript 基本語法與 React function component。
- 可執行 `npm run dev` 並觀察畫面狀態變化。

## Core Concepts

1. Patch-first with evidence
- 何時用：有 patch 更新或安全修補時，先升級再以測試佐證。
- 何時不用：長期累積 patch，一次跨多版本升級。

2. v5 API correctness gate
- 何時用：每月檢查是否仍存在舊寫法（例如 `useStore(selector, shallow)`）。
- 何時不用：只看功能可跑，忽略 API 教學與實作偏差。

3. Persist consistency gate
- 何時用：有 `persist` store 時，固定驗證 rapid updates 後 storage/in-memory 一致。
- 何時不用：只跑單次 happy path，不驗證高頻更新。

## Step-by-step

1. 每月固定日期檢查 `zustand` / `react` / `next` 最新版本與發布日期。
2. 比對 current vs latest，標記 patch/minor/major 差異。
3. 先做 v5 API 掃描：`useShallow`、`createWithEqualityFn` 是否到位。
4. 檢查 `persist` store 是否具備 `version` + `migrate` + 一致性驗收。
5. 若有 patch/security 修補，建立升級分支並更新依賴。
6. 執行 `lint/test/build + smoke test`，重點驗證 hydration、client boundary。
7. 執行 rapid updates 一致性檢查並記錄結果。
8. 更新月檢紀錄：版本日期、風險等級、決策、截止日、驗證證據。

截至 2026-02-14 的基準快照：

- Zustand 最新 stable：`5.0.11`（2026-02-01）。
- React 最新 patch：`19.2.4`（2026-01-26）。
- Next.js 實作基準：`16.x App Router`。

## Hands-on Lab

### Foundation
任務：完成一次 `zustand/react/next` 月檢記錄。

驗收條件：
- 記錄 current vs latest 與發布日期。
- 有風險等級與升級決策。
- 有明確截止日與 owner。

### Advanced
任務：完成 v5 API 正確性掃描與修正。

驗收條件：
- 不再以舊 equality 用法作為預設範例。
- 至少一處改為 `useShallow` 或 `createWithEqualityFn`。
- 行為與效能結果可驗證。

### Challenge
任務：為 persist store 建立 rapid updates 一致性檢核。

驗收條件：
- 高頻更新後 storage 與 in-memory 一致。
- 有可重現步驟或測試。
- 將結果寫入 monthly log。

## Reference Solution

```md
## 2026-02 monthly update

### Version status
- Current: zustand 5.0.10 / react 19.2.2 / next 16.0.0
- Latest: zustand 5.0.11 (2026-02-01) / react 19.2.4 (2026-01-26) / next 16.0.1
- Delta: patch updates available

### Risk status
- Breaking change risk: low
- Security advisories: none critical this month
- API compatibility: old equality usage found in 2 files
- Persist consistency: rapid updates check passed

### Decision
- Action: patch now
- Reason: low risk and aligns with v5 correctness baseline
- Deadline: 2026-02-20

### Validation
- npm run lint: pass
- npm run test: pass
- npm run build: pass
- smoke routes: /, /dashboard, /settings pass
- persist rapid updates check: pass

### Follow-ups
- Replace remaining legacy equality patterns
- Update chapter 16 and chapter 19 notes
- Owner: frontend team
```

## Common Pitfalls

- 只看版本號，不看發布日期與修補背景。
- 保留舊 equality 寫法卻當作 v5 正確示範。
- `persist` 只測重整，不測 rapid updates 一致性。
- 沒有 deadline/owner，導致月檢變成無效紀錄。

## Checklist

- [ ] 版本比較含發布日期。
- [ ] 有風險等級、決策、截止日、owner。
- [ ] v5 API 正確性檢查已完成（`useShallow` / `createWithEqualityFn`）。
- [ ] `persist` 一致性檢查已完成（rapid updates）。
- [ ] 有完整 lint/test/build + smoke 證據。

## Further Reading (official links only)

- [Zustand Releases](https://github.com/pmndrs/zustand/releases)
- [Migrate to v5](https://zustand.docs.pmnd.rs/migrations/migrating-to-v5)
- [Persist Middleware](https://zustand.docs.pmnd.rs/middlewares/persist)
- [React Security Update Note](https://react.dev/blog/2025/12/11/react-19-upgrade-guide#updates-since-the-release-of-react-19)
