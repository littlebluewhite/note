---
title: Monotonic Segment Scan
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(n)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-02-17
---
# Monotonic Segment Scan / 單調段掃描

## Goal

Detect whether an array can be partitioned (by indices) into consecutive monotonic segments.
用線性掃描判斷陣列能否用索引切成連續的單調段（遞增/遞減）。

## When to Use

- Pattern checking like: increasing → decreasing → increasing.
  / 檢查形狀：遞增 → 遞減 → 遞增。
- Validate piecewise monotonic constraints with strict inequalities.
  / 驗證分段單調且「嚴格不等式」的限制。

## Core Idea / 核心想法

Treat the scan as a small state machine:
把掃描當作簡單狀態機：

1. Consume as long as the current monotonic relation holds.
   / 只要目前關係成立就一直前進。
2. Record the boundary index.
   / 記下段落邊界。
3. Switch to next expected relation and continue.
   / 切換到下一段預期關係並繼續。

Strict vs non-strict matters:
- Strictly increasing uses `<`.
- Strictly decreasing uses `>`.

## Template / 範本

Example: inc → dec → inc

```text
i = 0
while i+1<n and a[i] < a[i+1]: i++
require i >= 1   // first segment length >= 2

while i+1<n and a[i] > a[i+1]: i++
require middle segment advanced at least once
require i <= n-2 // so last segment has length >= 2

while i+1<n and a[i] < a[i+1]: i++
return i == n-1
```

## Pitfalls / 常見陷阱

- Segment length constraints (`p>0`, `q<n-1`) are easy to miss.
  / 容易漏掉段長限制（例如 `p>0`, `q<n-1`）。
- Equal adjacent values break strict monotonicity.
  / 相鄰相等會破壞「嚴格」單調。
- `n` might be too small to contain all segments.
  / `n` 太小時不可能切成多段。

## Related problems / 相關題目

- [q3637](../leetcode/q3637.md) — Trionic Array I
