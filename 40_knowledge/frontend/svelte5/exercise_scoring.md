---
title: Svelte 5 Exercise Scoring Guide
note_type: system
domain: frontend
tags: [system, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: system
---
# Svelte 5 Exercise Scoring Guide

## Purpose

提供每章練習的可量化評分標準，讓學習者能自評「是否真的會用」。

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

- 功能正確（15）：主要功能可運作。
- 型別基本正確（10）：核心資料有 type。
- 可讀性（5）：命名與結構清楚。

## Advanced (35)

- 邊界處理（15）：空資料、錯誤路徑、loading 有處理。
- 架構合理（10）：責任拆分明確，沒有過度耦合。
- 可測試性（10）：主要邏輯可獨立驗證。

## Challenge (35)

- 效能/體驗（15）：有 transition、fine-grained reactivity 或避免不必要 DOM 更新。
- 品質保障（10）：有測試或明確驗收步驟。
- 實戰可遷移（10）：可套用到不同路由或模組。

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

## Coaching Rules

- 若總分 < 70：先回到 Foundation，不進下一章。
- 若 70-84：可進下一章，但需補至少 1 個 Advanced 缺口。
- 若 >= 85：可直接進下一章，並保留 Challenge 的改進記錄。
