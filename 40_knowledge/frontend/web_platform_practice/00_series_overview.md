---
title: Web Platform Practice Series Overview
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, web-platform]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: web_platform_practice
chapter: "00"
level: intermediate
stack: Browser APIs + TypeScript + Playwright + CI
prerequisites: [html_css_js_basics]
---
# Web Platform Practice Series Overview

## Goal

建立一條「框架能力 -> 瀏覽器與平台能力 -> 可交付品質」的實戰路徑。

銜接上一章：一般前端框架基礎（React/Svelte/Tailwind/Zustand）。下一章預告：Rendering pipeline 與 event loop 的實作診斷。

## Prerequisites

- 可操作 Node.js 專案並執行 `npm run dev`。
- 知道 bundle、hydration、cache 的基本概念。
- 了解基本 HTTP 與瀏覽器 DevTools。

## Core Concepts

1. 平台能力是產品穩定性的下限。
- 何時用：上線前要做效能、安全、交付品質治理。
- 何時不用：純概念學習或一次性 demo。

2. 量測優先於優化。
- 何時用：任何性能或穩定性問題。
- 何時不用：還沒有明確 KPI，先定義指標。

3. 自動化驗證優先於手動回歸。
- 何時用：跨頁面、跨環境、跨團隊交付。
- 何時不用：探索早期原型。

## Step-by-step

1. 建立 `web-platform-lab` 專案與 `docs/` 記錄路徑。
2. 設定測試命令：unit、e2e、build、lint。
3. 設定 `performance budget` 初始值（LCP、INP、CLS）。
4. 設定最小安全基線（CSP、CSRF、防 XSS）。
5. 設定交付基線（bundle size、cache policy、error budget）。
6. 每章完成後留下 evidence 與 gap/action。

## Hands-on Lab

### Foundation
- 建立 `docs/notes/web-platform/` 並完成章節索引。

### Advanced
- 建立 `ci/checklist.md`，列出 release gate。

### Challenge
- 選一個現有頁面做完整壓測與回滾演練。

## Reference Solution

```md
# ci/checklist.md
- [ ] npm run lint
- [ ] npm run test
- [ ] npm run build
- [ ] npm run e2e
- [ ] web-vitals thresholds pass
- [ ] security headers verified
```

## Evidence

- Demo route: `/performance-lab`, `/security-lab`
- Commands: `npm run test`, `npm run e2e`, `npm run build`
- Artifacts: `reports/lighthouse/`, `reports/playwright/`

## Common Pitfalls

- 把平台問題當成框架問題，導致診斷方向錯誤。
- 沒有先定義 budget 就直接優化。
- 只看本地結果，不做 CI gate。
- 沒有 rollback 機制就部署重大變更。

## Checklist

- [ ] 有章節索引與 evidence 路徑。
- [ ] 有明確 KPI 與 budget。
- [ ] 有 CI gate。
- [ ] 有安全檢查清單。
- [ ] 有 rollback 演練紀錄。

## Further Reading

- https://web.dev/
- https://developer.mozilla.org/
- https://w3c.github.io/web-performance/
