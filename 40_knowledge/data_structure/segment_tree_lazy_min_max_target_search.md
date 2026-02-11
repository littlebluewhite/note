---
title: Segment Tree (Lazy Range Add + Min/Max + Rightmost Target Search) / 線段樹（Lazy 區間加 + 最小最大值 + 最右目標搜尋）
note_type: knowledge
domain: data_structure
tags: [knowledge, data_structure]
created: 2026-02-11
updated: 2026-02-11
status: active
source: knowledge
complexity_time: O(log n) per update/query
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-25
---
# Segment Tree (Lazy Range Add + Min/Max + Rightmost Target Search) / 線段樹（Lazy 區間加 + 最小最大值 + 最右目標搜尋）

## Purpose / 目的

Maintain an array under range-add updates and quickly find the rightmost index in a range whose value equals a target (often `0`).
在可做區間加的陣列上，快速找到某區間內值等於目標值（常見是 `0`）的最右位置。

## Core Idea / 核心概念

Each node stores:

- `min_val`: minimum value in segment
- `max_val`: maximum value in segment
- `lazy_add`: pending range add tag

Range add updates both `min_val` and `max_val` by the same delta, and accumulates lazy tag.

For "find rightmost target":

1. If segment does not intersect query range: prune.
2. If `target < min_val` or `target > max_val`: prune.
3. Recurse right child first, then left child.
4. First found leaf is the answer.

This prune is especially strong when values are prefix sums with bounded adjacent difference.

## Operations / 操作

- `range_add(l, r, delta)`:
  - add `delta` to every value in `[l, r]`
- `find_last_value(start, target)`:
  - search in `[start, n]` for rightmost index where value is `target`

## When to Use / 使用時機

- Need frequent range adds and point-value existence search by interval.
- Need rightmost/leftmost target index, not just aggregate statistics.
- Prefix-sum style problems where each step changes by small discrete increments.

## Worked Example / 實作範例

Array (prefix values): `[1, 0, 0, -1, 0]`

Task: find rightmost `0` from index `2`.

- root min/max contains `0`, continue
- right child range contains `0`, recurse right first
- keep descending until leaf at index `5` found

Now apply `range_add(2, 4, +1)`:

- values become `[1, 1, 1, 0, 0]`
- querying rightmost `0` from index `2` still returns index `5`

## Variations / 變化型

- Find leftmost target: recurse left child first.
- Target interval query (`[lo, hi]`) instead of exact target.
- Store additional fields (`sum`, `count`, `argmin`) when needed.

## Complexity / 複雜度

- Time: `O(log n)` per `range_add` and search query (typical)
- Space: `O(n)`

## Pitfalls / 常見陷阱

- Forgetting to `push_down` before descending causes stale child ranges.
- Mixing `0-based` and `1-based` tree indices.
- Using min/max prune without checking query-range intersection.
- Assuming `target in [min,max]` always implies existence in arbitrary arrays; this is safe only with additional structure assumptions.

## Implementation Notes / 實作細節

- Allocate `4 * n + 5` nodes for safe array-based segment tree.
- Keep `apply(idx, delta)` as a single helper to avoid duplicated logic.
- For rightmost search, always recurse right first and return immediately when found.
- In prefix-sum tasks, pair this structure with lazy propagation to support sliding-left-boundary corrections.

## Related Problems / 相關題目

- [q3721](../leetcode/q3721.md)
