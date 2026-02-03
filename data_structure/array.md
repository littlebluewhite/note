---
title: "Array"
category: data_structure
tags: [data_structure]
created: 2026-02-03
updated: 2026-02-03
difficulty: "n/a"
source: data_structure
status: active
complexity_time: O(1) access
complexity_space: O(n)
---
# Array / 陣列

## Purpose / 目的

Store a sequence of elements in contiguous memory for fast indexed access.
用連續記憶體儲存一串元素，以支援快速索引存取。

## Core Idea / 核心概念

- Indexing by `i` is `O(1)`.
  / 用索引 `i` 取值是 `O(1)`。
- Great for linear scans and piecewise patterns.
  / 很適合線性掃描與分段型態判斷。

## Operations / 操作

- Read / Write by index: `O(1)`.
  / 索引讀寫：`O(1)`。
- Append (dynamic array / Vec): amortized `O(1)`.
  / 尾端追加（動態陣列/Vec）：攤銷 `O(1)`。
- Insert/delete in the middle: `O(n)` due to shifts.
  / 中間插入/刪除：需搬移元素，`O(n)`。

## Complexity / 複雜度

- Time: `O(1) access`
- Space: `O(n)`

Where:
`n`: number of elements.


## Notes / 補充

- Strict comparisons between neighbors (`a[i] < a[i+1]`) are a common building block for monotonic scans.
  / 相鄰嚴格比較（`a[i] < a[i+1]`）常用於單調段掃描。

## Related problems / 相關題目

- [q3637](../leetcode/q3637.md)