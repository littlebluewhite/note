---
title: Tailwind CSS 4 Exercise Scoring Guide
note_type: system
domain: frontend
tags: [system, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: system
---
# Tailwind CSS 4 Exercise Scoring Guide

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

- 視覺正確性（15）：元素樣式與規格相符，顏色、間距、字型正確呈現。
- 類別使用正確（10）：utility class 語法無誤，無多餘或衝突 class。
- 可讀性（5）：HTML 結構清楚，class 排列有邏輯順序。

## Advanced (35)

- 響應式設計（15）：使用 breakpoint 變體，在 mobile/tablet/desktop 正確呈現。
- 架構合理（10）：元件拆分明確，utility 與自訂 @theme token 使用得當。
- 狀態互動（10）：hover/focus/active 等狀態變體正確應用。

## Challenge (35)

- 效能/體驗（15）：動畫流暢、Layout Shift 最小、深色模式完整。
- 品質保障（10）：有螢幕截圖或明確驗收步驟佐證。
- 實戰可遷移（10）：可套用到不同頁面或設計系統。

## Self-review Template

```md
## Chapter XX score
- Foundation: __ / 30
- Advanced: __ / 35
- Challenge: __ / 35
- Total: __ / 100

### Evidence
- Demo page URL:
- Key files:
- Breakpoints tested: sm / md / lg / xl / 2xl
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
