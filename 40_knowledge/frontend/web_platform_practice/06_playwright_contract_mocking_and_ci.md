---
title: Playwright Contract Mocking and CI
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, testing, ci]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: web_platform_practice
chapter: "06"
level: intermediate
stack: Playwright + Vitest + Mock Service Worker + CI
prerequisites: [testing_basics]
---
# Playwright Contract Mocking and CI

## Goal

建立端到端與契約測試雙軌驗證，並形成 CI 失敗排查標準流程。

銜接上一章：delivery 優化。下一章預告：capstone 交付演練與 release readiness。

## Prerequisites

- 具備 Vitest 或 Jest 基礎。
- 可執行 Playwright。
- 了解 API schema 基本概念。

## Core Concepts

1. E2E 驗證核心旅程，不覆蓋所有細節。
- 何時用：關鍵流程（登入、購物、付款）。
- 何時不用：純展示頁。

2. Contract test 鎖定前後端接口一致性。
- 何時用：多團隊並行開發。
- 何時不用：單體且低變更頻率。

3. CI triage 需要標準化。
- 何時用：每日多次部署。
- 何時不用：單機手工流程。

## Step-by-step

1. 定義關鍵旅程與 P0 測試清單。
2. 建立 Playwright smoke + full 套件分層。
3. 以 mock server 或 MSW 建立 contract 驗證。
4. 在 CI 設定 fail-fast 與 artifact 上傳。
5. 建立 flaky test 重試與標記策略。
6. 建立 triage runbook（分類、owner、SLA）。

## Hands-on Lab

### Foundation
- 寫 3 個 Playwright smoke test。

### Advanced
- 建 1 個 contract test 並加入 schema 驗證。

### Challenge
- 讓 CI 失敗能在 15 分鐘內定位問題類型。

## Reference Solution

```yaml
- name: e2e
  run: npm run test:e2e -- --reporter=line
```

## Evidence

- Artifact: `playwright-report/`, `reports/contracts/`
- Command: `npm run test:e2e`, `npm run test:contract`
- CI logs: failed step + owner + recovery note

## Common Pitfalls

- 把所有測試都塞進 E2E，造成維護爆炸。
- mock 資料與真實 schema 漂移。
- 缺少 artifact，失敗後不可追溯。
- flaky test 無標記導致誤判回歸。

## Checklist

- [ ] smoke/full 分層存在。
- [ ] contract 測試有 schema 驗證。
- [ ] CI 產出 report artifact。
- [ ] triage runbook 可執行。
- [ ] flaky policy 已定義。

## Further Reading

- https://playwright.dev/
- https://testingjavascript.com/
- https://docs.github.com/actions
