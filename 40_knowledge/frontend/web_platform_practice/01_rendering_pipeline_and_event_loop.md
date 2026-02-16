---
title: Rendering Pipeline and Event Loop
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, web-performance]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: web_platform_practice
chapter: "01"
level: intermediate
stack: Browser rendering + JS runtime
prerequisites: [dom_cssom_js_basics]
---
# Rendering Pipeline and Event Loop

## Goal

學會定位主執行緒阻塞、長任務、layout thrashing，並建立可重現診斷流程。

銜接上一章：系列導讀。下一章預告：多執行緒、儲存策略與離線快取。

## Prerequisites

- 熟悉 DevTools Performance 面板。
- 了解 repaint/reflow 基本概念。
- 可在程式中加入 `performance.mark`。

## Core Concepts

1. Rendering pipeline（style -> layout -> paint -> composite）。
- 何時用：畫面卡頓、scroll 掉幀。
- 何時不用：純後端 API 延遲。

2. Event loop（task/microtask/render）。
- 何時用：輸入延遲、事件回應慢。
- 何時不用：單純網路慢但主執行緒空閒。

3. 長任務切分。
- 何時用：單次 JS > 50ms。
- 何時不用：已在 worker 背景執行。

## Step-by-step

1. 用 DevTools 錄製慢頁面互動。
2. 找出 `Long Task`、重複 layout 與 forced sync layout。
3. 用 `performance.mark/measure` 標記關鍵流程。
4. 將重計算拆到 `requestIdleCallback` 或 worker。
5. 改善 DOM 讀寫順序，避免交錯讀寫。
6. 重錄性能曲線並比對 before/after。

## Hands-on Lab

### Foundation
- 建立一個輸入篩選頁，故意加入同步重計算。

### Advanced
- 將重計算移到 worker 或 idle callback。

### Challenge
- 將 INP 改善 30% 以上並提供證據。

## Reference Solution

```ts
performance.mark('filter-start');
const result = expensiveFilter(data, keyword);
performance.mark('filter-end');
performance.measure('filter', 'filter-start', 'filter-end');
```

## Evidence

- Command: `npm run dev`
- Report: DevTools Performance trace before/after
- Metric: INP, scripting time, dropped frames

## Common Pitfalls

- 只看 FPS，不看 main-thread 長任務來源。
- 在 render 階段做同步排序與格式化。
- 忽略第三方 script 造成的阻塞。
- 誤把網路延遲當成 event loop 問題。

## Checklist

- [ ] 有 before/after trace。
- [ ] 有 `performance.measure` 紀錄。
- [ ] 有明確 bottleneck 行。
- [ ] 有修正策略與回歸驗證。
- [ ] 有可重跑步驟。

## Further Reading

- https://developer.mozilla.org/en-US/docs/Web/Performance
- https://web.dev/articles/optimize-long-tasks
