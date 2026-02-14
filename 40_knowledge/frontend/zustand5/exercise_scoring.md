---
title: Zustand 5 Exercise Scoring Guide
note_type: system
domain: frontend
tags: [system, frontend, zustand5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: system
---
# Zustand 5 Exercise Scoring Guide

## Purpose

提供每章練習的量化評分標準，確保學習者不只看懂，還能實作與排錯。

## Scoring Model

- 每章滿分：100 分。
- Foundation：30 分。
- Advanced：35 分。
- Challenge：35 分。
- 通過標準：
  - 入門合格：>= 70
  - 穩定實作：>= 85
  - 可教他人：>= 95

## Foundation (30)

- 功能正確（15）：主要 store 行為可運作。
- 型別正確（10）：state/action/selectors 有明確 type。
- 可讀性（5）：命名與檔案分層清楚。

## Advanced (35)

- 邊界處理（15）：loading/error/empty/hydration 路徑有處理。
- 架構合理（10）：store 與 UI 職責分離。
- 可測試性（10）：主要邏輯可透過測試驗證。

## Challenge (35)

- 效能與訂閱策略（15）：避免不必要重渲染。
- 品質保障（10）：有測試或完整驗收證據。
- 實戰可遷移（10）：可套用到多模組頁面。

## Self-review Template

```md
## Chapter XX score
- Foundation: __ / 30
- Advanced: __ / 35
- Challenge: __ / 35
- Total: __ / 100

### Evidence
- Demo route:
- Key files:
- Test commands:
- Screenshot/video:

### Gap and action
- What failed:
- Why:
- Fix plan:
```
