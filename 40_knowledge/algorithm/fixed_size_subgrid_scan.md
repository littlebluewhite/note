---
title: Fixed-Size Subgrid Scan / 固定尺寸子矩陣掃描
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O((rows-k+1)*(cols-k+1)*k^2)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-02-17
canonical: algorithm/fixed_size_subgrid_scan.md
---
# Fixed-Size Subgrid Scan / 固定尺寸子矩陣掃描

Goal: enumerate every `k x k` subgrid in a matrix and validate or compute a property.
目標：枚舉矩陣中所有 `k x k` 子矩陣並檢查條件或計算結果。

## Core idea / 核心想法

- Slide a fixed window by moving the top-left corner.
  / 固定大小視窗，以左上角位置滑動。
- For each window, run a bounded `k*k` check.
  / 每個視窗只做 `k*k` 次的檢查。

## Template / 範本

```
for r in 0..=rows-k:
    for c in 0..=cols-k:
        process subgrid [r..r+k), [c..c+k)
```

## When to use / 使用時機

- `k` is small and fixed (e.g., 2x2, 3x3, 5x5).
  / `k` 固定且小。
- Need to validate a local pattern in every window.
  / 要檢查每個區塊的局部性條件。

## Variations / 變化型

- Scan multiple sizes by looping `k` from large to small and early-exit when found.
  / 需要最大尺寸時可從大到小掃描，找到就提前結束。
- Combine with prefix sums to validate row/column/diagonal sums in `O(1)`.
  / 搭配前綴和可 `O(1)` 計算列/欄/對角線總和。

## Worked Example / 範例

Problem: count `3 x 3` magic squares.
題目：計算 `3 x 3` 魔術方陣數量。

- Iterate all `r` in `0..=rows-3` and `c` in `0..=cols-3`.
  / 掃過所有可能的左上角。
- For each window, verify digits and row/column/diagonal sums.
  / 每個視窗檢查數字合法性與各列/欄/對角線總和。

## Complexity / 複雜度

- Time: `O((rows-k+1)*(cols-k+1)*k^2)`
- Space: `O(1)`

Where:
`rows`: number of rows.
`cols`: number of columns.
`k`: window size.


- Windows: `(rows-k+1) * (cols-k+1)`
  / 視窗數量。
- Each window: `O(k*k)`
  / 每個視窗檢查成本。
- Total: `O((rows-k+1)*(cols-k+1)*k*k)`
  / 總時間複雜度。
  / 額外空間 `O(1)`。

## Pitfalls / 常見陷阱

- Forgetting to handle grids smaller than `k`.
  / 忘了處理尺寸不足的情況。
- Off-by-one on the last valid top-left index.
  / 左上角索引容易 off-by-one。
- Recomputing heavy aggregates unnecessarily (use local checks if `k` is tiny).
  / `k` 小時不需要複雜前綴加速。

## Related problems / 相關題目

- [q1895](../leetcode/q1895.md)
- [q840](../leetcode/q840.md)