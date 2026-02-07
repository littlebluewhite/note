---
title: Presence Array / 出現標記陣列
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: data_structure
complexity_time: O(1) per op
complexity_space: O(R)
review_interval_days: 14
next_review: 2026-02-17
canonical: data_structure/presence_array.md
---
# Presence Array / 出現標記陣列

Goal: track whether each value in a small fixed range has appeared.
目標：在小範圍值域內，快速標記是否出現過。

## Core structure / 核心結構

- A fixed-size boolean array `seen[value]`.
  / 固定長度布林陣列 `seen[value]`。
- For counts, store integers instead of booleans.
  / 若要次數，改用整數陣列。

## Typical operations / 常見操作

- Check: `if seen[x] { ... }`
  / 查詢是否已出現。
- Mark: `seen[x] = true`
  / 標記出現。
- Reset: reinitialize the array if needed.
  / 需要時整體重設。

## Example / 範例

Problem: validate that a `3 x 3` grid contains distinct digits 1..9.
題目：檢查 `3 x 3` 是否含有互異的 1..9。

```
seen = [false; 10]
for each value v in window:
    if v < 1 or v > 9: invalid
    if seen[v]: duplicate -> invalid
    seen[v] = true
```

## Complexity / 複雜度

- Time: `O(1) per op`
- Space: `O(R)`

Where:
`R`: value range size.

- Access/update: `O(1)`
  / 每次查詢與更新 `O(1)`。
  / 空間 `O(R)`，`R` 為值域大小。

## Pitfalls / 常見陷阱

- Ensure indices are within range before indexing.
  / 先檢查範圍再索引。
- Reusing the array without clearing it.
  / 忘了重設造成殘留狀態。

## Related problems / 相關題目

- [q840](../leetcode/q840.md)
