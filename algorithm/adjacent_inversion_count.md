---
title: "Adjacent Inversion Count / 相鄰逆序計數"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(1) per update
complexity_space: O(1)
---
# Adjacent Inversion Count / 相鄰逆序計數

Goal: quickly know if an array is non-decreasing after local edits.
目標：在局部更新後快速判斷陣列是否非遞減。

## Core idea / 核心概念

Define a counter over adjacent pairs:
定義相鄰逆序計數：

```
bad(i) = 1 if a[i] > a[i+1], else 0
count = sum(bad(i))
```

The array is non-decreasing iff `count == 0`.
當 `count == 0` 時，整體即為非遞減。

## Local update rule / 區域更新規則

Only adjacent pairs touching the modified positions can change.
只有「被修改位置的相鄰對」會影響計數。

Example: merge adjacent `(u, v)` into `u`:
範例：合併相鄰 `(u, v)` 到 `u`：

- Old pairs that may change: `(prev(u), u)`, `(u, v)`, `(v, next(v))`
  / 可能變動的舊對：`(prev(u), u)`、`(u, v)`、`(v, next(v))`
- Subtract their old contributions from `count`.
  / 先扣掉舊貢獻。
- Perform the merge.
  / 合併更新值與連結。
- New pairs that may change: `(prev(u), u)`, `(u, next(v))`
  / 新的可能變動對：`(prev(u), u)`、`(u, next(v))`
- Add their new contributions to `count`.
  / 再加回新貢獻。

Each merge updates `count` in `O(1)`.
每次合併可在 `O(1)` 更新。

## Why it works / 為什麼可行

Global monotonicity is fully determined by local adjacent comparisons.
整體單調性完全由相鄰元素大小關係決定。

## Complexity / 複雜度

- Time: `O(1) per update`
- Space: `O(1)`

- Update per local change: `O(1)`.
  / 每次局部更新：`O(1)`。
- Extra space: `O(1)` besides the array.
  / 其餘空間：`O(1)`。

## Related problems / 相關題目

- [3507. Minimum Pair Removal to Sort Array I](https://leetcode.com/problems/minimum-pair-removal-to-sort-array-i/)
- [3510. Minimum Pair Removal to Sort Array II](https://leetcode.com/problems/minimum-pair-removal-to-sort-array-ii/)