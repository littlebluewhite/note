---
title: "Monotonic Three-Phase Scan (Inc→Dec→Inc) / 三段單調掃描"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: "n/a"
source: algorithm
status: active
complexity_time: O(n)
complexity_space: O(1)
---
# Monotonic Three-Phase Scan (Inc→Dec→Inc) / 三段單調掃描

## Goal
Detect whether an array can be split into **three non-empty monotonic segments**:
strictly increasing → strictly decreasing → strictly increasing.

目標：判斷陣列是否能切成 **三段皆非空** 的單調片段：
嚴格遞增 → 嚴格遞減 → 嚴格遞增。

## Core Idea / 核心概念
Use a **state machine** (phase = 0/1/2) and scan from left to right.

- Phase 0: consume the longest strictly increasing prefix.
- Phase 1: consume the longest strictly decreasing middle.
- Phase 2: consume the longest strictly increasing suffix.

At the end, succeed only if:
- you made progress in each phase (each segment length ≥ 2), and
- the scan ends exactly at the last element.

核心想法：用「狀態機」一次掃描。
- 第 0 段吃完最長嚴格遞增。
- 第 1 段吃完最長嚴格遞減。
- 第 2 段吃完最長嚴格遞增。
最後必須三段都有實際前進（每段至少 2 個元素），且剛好走到陣列尾端。

## Template / 模板
Let `i` be the current index.

1) `while i+1 < n && a[i] < a[i+1] { i++ }`  → `p = i`
2) `while i+1 < n && a[i] > a[i+1] { i++ }`  → `q = i`
3) `while i+1 < n && a[i] < a[i+1] { i++ }`

Validation:
- `p > 0` (first segment non-empty)
- `q > p` (second segment non-empty)
- `q < n-1` (third segment non-empty)
- `i == n-1` (consumed to the end)

## Complexity
- Time: `O(n)` / 時間：`O(n)`
- Space: `O(1)` / 空間：`O(1)`

## Pitfalls / 常見坑
- Allowing equal adjacent values (must be **strict**).
  / 相等不算單調（必須嚴格）。
- Forgetting to ensure each segment is non-empty.
  / 忘了檢查三段都要有長度。
- Returning true after finishing phase 1 (need phase 2 and must end exactly).
  / 做完遞減就回 true（不行，還要第三段且走到尾端）。

## Related Problems / 相關題
- [q3637](../leetcode/q3637.md)
- [q3640](../leetcode/q3640.md)
