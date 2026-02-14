---
title: Deployment, Observability, and Debug Workflow / 部署、可觀測性與除錯流程
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "18"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [17_testing_with_vitest_and_rtl]
---
# Deployment, Observability, and Debug Workflow / 部署、可觀測性與除錯流程

## Goal

本章目標是建立「可發布、可觀測、可回滾」的交付流程，讓線上問題可快速定位與修復。

銜接上一章：你已具備測試保護網，現在把它整合到部署與線上維運流程。

下一章預告：第 19 章會把版本升級與安全檢查制度化，完成長期維護閉環。

## Prerequisites

- 已完成第 17 章。
- 了解 CI/CD 基本概念。
- 能閱讀部署日誌與錯誤訊息。

## Core Concepts

1. Release gates
- 何時用：部署前固定經過 lint/test/build/smoke gates。
- 何時不用：直接手動上線且無可追蹤紀錄。

2. Observability triad
- 何時用：error tracking、performance metrics、request logs 同時具備。
- 何時不用：只看 build 成功就當作線上健康。

3. Debug playbook
- 何時用：問題發生時走重現 -> 定位 -> 修復 -> 驗證 -> 回顧。
- 何時不用：每次 incident 都臨場 improvisation。

## Step-by-step

1. 建立 CI pipeline：`lint -> test -> build`。
2. 設定 staging 環境與 smoke test 路由。
3. 新增 runtime error tracking（client + server）。
4. 記錄 web vitals（LCP/INP/CLS）基線。
5. 定義 deploy checklist 與 rollback 條件。
6. 演練一次故障回滾流程。
7. 寫 incident template（時間線、根因、修復）。
8. 每次發版後 30 分鐘監控關鍵指標。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：建立一份可執行 release checklist。

驗收條件：
- 包含 lint/test/build/smoke 四項。
- 每項有 pass/fail 記錄欄位。
- checklist 可被他人重複執行。

### 進階任務 (Advanced)
任務：定義 3 個可觀測指標與警戒值。

驗收條件：
- 至少包含 error rate 與一個 web vitals。
- 指標異常時有明確處理步驟。
- 有 dashboard 或記錄位置。

### 挑戰任務 (Challenge)
任務：做一次故障演練（模擬 API 500）。

驗收條件：
- 能在 15 分鐘內定位問題範圍。
- 有回滾或 hotfix 決策紀錄。
- 產出一份 incident report。

## Reference Solution

```md
Release Checklist
- [ ] npm run lint
- [ ] npm run test
- [ ] npm run build
- [ ] smoke test: /, /dashboard, /products
- [ ] compare key metrics with baseline
- [ ] rollback plan validated

Incident Template
- Start time:
- Detection method:
- Impacted route:
- Suspected root cause:
- Mitigation action:
- Final fix:
- Follow-up tasks:
```

## Common Pitfalls

- 發版只看 CI 綠燈，不看線上指標。
- 監控告警太多噪音，真正異常被淹沒。
- 缺 rollback 預案，故障時只能硬修。
- Next.js route cache 與 revalidate 設定不清，造成「已修復但線上仍舊版」。

## Checklist

- [ ] CI 具備 lint/test/build 三個 gate。
- [ ] staging smoke test 至少覆蓋 3 條關鍵路由。
- [ ] 線上至少監控 3 個指標（含 error rate）。
- [ ] 已完成一次故障演練並留存報告。
- [ ] deploy 後 30 分鐘監控流程有明確負責人。

## Further Reading (official links only)

- [Next.js Deploying](https://nextjs.org/docs/app/building-your-application/deploying)
- [Next.js Analytics](https://nextjs.org/docs/app/building-your-application/optimizing/analytics)
- [Instrumentation](https://nextjs.org/docs/app/building-your-application/optimizing/instrumentation)
