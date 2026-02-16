---
title: Web Workers Storage Cache and Offline
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, web-platform]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: web_platform_practice
chapter: "02"
level: intermediate
stack: Worker + Storage + Cache API + Service Worker
prerequisites: [event_loop_http_cache_basics]
---
# Web Workers Storage Cache and Offline

## Goal

建立「計算隔離 + 資料持久化 + 離線可用」的最小生產級策略。

銜接上一章：render/event loop。下一章預告：前端安全基線（CSP/CORS/CSRF/XSS）。

## Prerequisites

- 了解 localStorage 與 IndexedDB 差異。
- 可註冊 Service Worker。
- 熟悉 fetch/cache headers。

## Core Concepts

1. Worker 隔離 CPU 密集任務。
- 何時用：主執行緒超載。
- 何時不用：輕量操作，搬移成本高於收益。

2. 儲存分層（memory/IndexedDB/Cache API）。
- 何時用：需要離線或跨 session 保留。
- 何時不用：短生命週期 transient state。

3. 離線策略（network-first/cache-first/stale-while-revalidate）。
- 何時用：多網路品質場景。
- 何時不用：資料強一致性要求極高且不可離線。

## Step-by-step

1. 定義可離線資料範圍（UI shell/靜態資源/可快取 API）。
2. 把重計算移入 worker。
3. 用 IndexedDB 儲存關鍵草稿或佇列。
4. 用 Service Worker 管理 cache 策略。
5. 實作 offline fallback 頁。
6. 驗證離線、慢網路、恢復連線三種路徑。

## Hands-on Lab

### Foundation
- 設定 worker 計算與主執行緒通訊。

### Advanced
- 新增 Service Worker 的 `stale-while-revalidate`。

### Challenge
- 支援離線新增草稿，連線恢復後自動同步。

## Reference Solution

```js
self.addEventListener('fetch', (event) => {
  event.respondWith(caches.match(event.request).then((hit) => hit || fetch(event.request)));
});
```

## Evidence

- Command: `npm run dev`
- Network simulation: Chrome offline/Slow 3G
- Artifact: offline screenshot + sync logs

## Common Pitfalls

- 把敏感資料存 localStorage。
- cache key/version 沒管理造成髒資料。
- worker 傳輸大量資料未使用 transferables。
- service worker 更新流程沒有 `skipWaiting` 策略。

## Checklist

- [ ] worker 任務可獨立驗證。
- [ ] IndexedDB 有 schema/version 管理。
- [ ] 離線 fallback 可觸發。
- [ ] 連線恢復同步可驗證。
- [ ] cache invalidation 規則清楚。

## Further Reading

- https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API
- https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps
