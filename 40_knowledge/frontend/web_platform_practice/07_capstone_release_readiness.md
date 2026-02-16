---
title: Capstone Release Readiness
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, capstone]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: web_platform_practice
chapter: "07"
level: advanced
stack: Product delivery end-to-end
prerequisites: [chapter_01_to_06]
---
# Capstone Release Readiness

## Goal

完成一個可部署的前端功能模組，並以 release gate 驗證性能、安全、測試、可回滾性。

銜接上一章：E2E/contract/CI。下一章預告：回到各框架系列執行對應 capstone。

## Prerequisites

- 完成 `01-06` 章。
- 有一個可執行的真實功能頁面。
- 可操作 CI pipeline。

## Core Concepts

1. 功能完成不等於可上線。
- 何時用：任何 production release。
- 何時不用：臨時 demo。

2. 非功能需求需可量化。
- 何時用：性能、安全、可用性需求。
- 何時不用：沒有上線計畫。

3. 回滾是交付的一部分。
- 何時用：每次部署。
- 何時不用：不可回滾架構（需先重構）。

## Step-by-step

1. 明確功能需求與 user flow。
2. 定義非功能需求（CWV、安全、錯誤率）。
3. 建 release checklist 與 owner。
4. 執行 smoke/full/contract/perf/security 測試。
5. 驗證監控與告警。
6. 演練 rollback 並保留紀錄。

## Hands-on Lab

### Foundation
- 完成一條端到端功能流。

### Advanced
- 讓 CI gate 全部通過。

### Challenge
- 完成一次故障演練與回滾，並更新 runbook。

## Reference Solution

```md
## Release gate
- Functional: pass
- Performance: LCP <= 2.5s, INP <= 200ms, CLS <= 0.1
- Security: CSP/CORS/CSRF checks pass
- Test: unit/e2e/contract pass
- Rollback: verified within 10 minutes
```

## Evidence

- Artifacts: CI run URL, perf report, security check log
- Commands: `npm run test && npm run test:e2e && npm run build`
- Regression notes: `reports/release/regression-YYYYMMDD.md`

## Common Pitfalls

- 只驗證 happy path。
- 沒有定義 owner 導致問題無人收斂。
- release gate 與實際監控指標不一致。
- rollback 流程僅文件化，未實際演練。

## Checklist

- [ ] 功能需求完整。
- [ ] 非功能需求量化。
- [ ] 監控與告警配置完成。
- [ ] CI gate 可重跑。
- [ ] rollback 演練有證據。

## Further Reading

- https://sre.google/sre-book/service-level-objectives/
- https://web.dev/vitals/
- https://owasp.org/
