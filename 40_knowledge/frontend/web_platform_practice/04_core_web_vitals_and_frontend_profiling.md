---
title: Core Web Vitals and Frontend Profiling
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, core-web-vitals]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: web_platform_practice
chapter: "04"
level: intermediate
stack: Lighthouse + Web Vitals + DevTools
prerequisites: [rendering_pipeline_basics]
---
# Core Web Vitals and Frontend Profiling

## Goal

建立可操作的指標治理流程，將 LCP/INP/CLS 直接轉換為開發任務與 release gate。

銜接上一章：安全基線。下一章預告：bundle、圖片字型、快取與交付策略。

## Prerequisites

- 知道 CWV 三大指標。
- 可執行 Lighthouse。
- 可讀 DevTools flame chart。

## Core Concepts

1. Field data 優先，Lab data 輔助。
- 何時用：上線流量分析。
- 何時不用：尚未上線，可先用 lab。

2. Budget-driven optimization。
- 何時用：需要跨團隊一致標準。
- 何時不用：探索階段。

3. 回歸防線比一次優化更重要。
- 何時用：持續交付。
- 何時不用：一次性活動頁。

## Step-by-step

1. 設定 baseline：LCP/INP/CLS 預算。
2. 建立 lab profile（Lighthouse + trace）。
3. 標記主要 bottleneck（script/layout/network）。
4. 對應優化任務並估算收益。
5. 實作後重跑 profile。
6. 將 budget check 接入 CI。

## Hands-on Lab

### Foundation
- 跑一份 Lighthouse baseline 報告。

### Advanced
- 至少改善一個指標 20%。

### Challenge
- 建立 PR template 的 perf section。

## Reference Solution

```json
{
  "lcp_ms": 2500,
  "inp_ms": 200,
  "cls": 0.1
}
```

## Evidence

- Artifact: `reports/lighthouse/before.json`, `after.json`
- Command: `npm run perf:lighthouse`
- CI: perf budget job log

## Common Pitfalls

- 只看單次跑分，不看趨勢。
- 忽略 third-party script 影響。
- 沒有設備與網路條件一致化。
- 只調整 code，不調整資源交付策略。

## Checklist

- [ ] budget 已定義。
- [ ] before/after 報告存在。
- [ ] bottleneck 有對應任務。
- [ ] CI 有閾值檢查。
- [ ] 回歸策略已記錄。

## Further Reading

- https://web.dev/vitals/
- https://developer.chrome.com/docs/devtools/performance
