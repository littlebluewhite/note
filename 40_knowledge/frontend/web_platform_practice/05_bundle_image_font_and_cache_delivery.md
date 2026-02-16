---
title: Bundle Image Font and Cache Delivery
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, delivery]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: web_platform_practice
chapter: "05"
level: intermediate
stack: Build tools + CDN + caching headers
prerequisites: [http_cache_basics]
---
# Bundle Image Font and Cache Delivery

## Goal

建立交付層優化策略：bundle 分析、圖片/字型策略、HTTP 快取規則與失效流程。

銜接上一章：CWV profiling。下一章預告：E2E、contract test、mocking 與 CI 失敗排查。

## Prerequisites

- 可執行 bundle analyzer。
- 了解 HTTP cache-control。
- 知道圖片格式與 preload 基本概念。

## Core Concepts

1. Bundle size 是症狀，chunk strategy 是根因。
- 何時用：JS payload 過大。
- 何時不用：主要瓶頸在後端 latency。

2. 圖片與字型優化直接影響 LCP/CLS。
- 何時用：首頁視覺資源多。
- 何時不用：純文字頁面。

3. Cache policy 要配合版本化。
- 何時用：靜態資源長快取。
- 何時不用：動態 API 回應。

## Step-by-step

1. 產出 bundle report 並找 top modules。
2. 調整 route-level/code-split。
3. 圖片改用現代格式與 responsive sources。
4. 字型使用 subset + preload + fallback。
5. 設定 cache-control（immutable + version hash）。
6. 驗證 cache hit ratio 與回滾可行性。

## Hands-on Lab

### Foundation
- 匯出 bundle analyzer 報表。

### Advanced
- 降低 JS 初始包體 20%。

### Challenge
- 讓首頁 LCP 改善且無 CLS 回歸。

## Reference Solution

```http
Cache-Control: public, max-age=31536000, immutable
```

## Evidence

- Artifact: `reports/bundle/`, `reports/images/`
- Command: `npm run analyze`, `npm run build`
- Metric: bundle KB, LCP, CLS

## Common Pitfalls

- 用 gzip 後大小判斷錯誤來源。
- preload 過量導致網路競爭。
- 字型 fallback 缺失造成 CLS。
- 靜態資源未版本化導致 cache 汙染。

## Checklist

- [ ] bundle top offenders 已列出。
- [ ] code split 策略有紀錄。
- [ ] 圖片策略符合 responsive。
- [ ] 字型策略有 fallback。
- [ ] cache policy 可回滾。

## Further Reading

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
- https://web.dev/learn/performance/
