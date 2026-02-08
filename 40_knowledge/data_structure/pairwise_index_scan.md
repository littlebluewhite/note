---
title: Pairwise Index Scan / 陣列兩兩掃描
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: data_structure
complexity_time: O(n^2)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-02-17
---
# Pairwise Index Scan / 陣列兩兩掃描

Goal: enumerate all unordered pairs in a flat array using indices for pairwise computations.
目標：用索引在扁平陣列中枚舉所有無序兩兩組合以進行成對計算。

## Core structure / 核心結構

- Store items in a contiguous array, each item identified by its index.
  / 將元素放在連續陣列中，用索引唯一標識。
- Use two indices with `i < j` to cover each pair exactly once.
  / 使用 `i < j` 的雙迴圈確保每一對只被計算一次。

## Typical operations / 常見操作

- Pairwise scan:
  / 兩兩掃描：

```
for i in 0..n-1:
    for j in i+1..n-1:
        process(a[i], a[j])
```

## Example / 範例

Problem: max square area inside the intersection of any two rectangles.
題目：任意兩矩形交集內可放最大正方形面積。

- Store rectangles in arrays.
  / 先把矩形存成陣列。
- For each pair `(i, j)`, compute intersection and update the best area.
  / 對每一對 `(i, j)` 計算交集並更新最大面積。

## Complexity / 複雜度

- Time: `O(n^2)` for `n` items.
  / 時間：`O(n^2)`。
- Space: `O(1)` extra.
  / 空間：`O(1)`。

## Pitfalls / 常見陷阱

- Starting `j` from `0` causes double counting; always use `j = i + 1`.
  / `j` 從 `0` 開始會重複計算，請用 `j = i + 1`。
- `O(n^2)` is only feasible for small `n` (e.g., `n <= 10^3`).
  / `O(n^2)` 只能用在小規模輸入。
- Pairwise computations like area can overflow `i32`; use `i64`.
  / 面積類計算可能溢位 `i32`，請改用 `i64`。

## Related problems / 相關題目

- [q3047](../leetcode/q3047.md)
- [q2975](../leetcode/q2975.md)
