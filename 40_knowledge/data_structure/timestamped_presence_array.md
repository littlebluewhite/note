---
title: Timestamped Presence Array / 版本標記出現陣列
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-10
updated: 2026-02-10
status: active
source: data_structure
complexity_time: O(1) per check/mark
complexity_space: O(U)
review_interval_days: 14
next_review: 2026-02-24
---
# Timestamped Presence Array / 版本標記出現陣列

## Purpose / 目的

Track whether a value has appeared in the **current round/window** without clearing the entire array each round.
在每一輪/每個視窗中追蹤值是否出現過，且不用每輪都清空整個陣列。

## Core Idea / 核心概念

Use an integer array `seen_ver[value]` and a global `version` counter:

- value `x` is considered present in current round iff `seen_ver[x] == version`.
- to mark present: `seen_ver[x] = version`.
- to reset all marks logically: `version += 1`.

這種作法把「清空整個 `seen` 陣列」轉成「遞增版本號」，避免 `O(U)` 全量重設。

## Operations / 操作

- Check present:
  - `seen_ver[x] == version`
- Mark present:
  - `seen_ver[x] = version`
- Logical clear all:
  - `version += 1`

All above are `O(1)`.

## When to Use / 使用時機

- Need repeated rounds of membership checks with the same bounded value domain.
  / 多輪重複查詢，且值域固定。
- Clearing a boolean array each round would be too costly.
  / 每輪清空布林陣列成本高。
- Example patterns: per-left-boundary subarray scans, BFS layer-local marks, batched dedup.
  / 例如每個左端點的子陣列掃描、分層去重。

## Worked Example / 實作範例

Task: for each left boundary `l`, count distinct values while expanding `r`.

```text
seen_ver[0..U] = 0
version = 0
for l in 0..n-1:
    version += 1
    distinct = 0
    for r in l..n-1:
        x = nums[r]
        if seen_ver[x] != version:
            seen_ver[x] = version
            distinct += 1
```

Compared with naive clear:

- naive: each `l` clears `O(U)` + scan `O(n)`
- versioned: each `l` only does scan `O(n)`

## Variations / 變化型

- `u16/u32/i32` versions depending on round count.
- Multi-state tracking:
  - store small enums or bitmasks instead of only presence.
- Two-domain markers:
  - maintain separate arrays for two categories if needed.

## Complexity / 複雜度

- Time: `O(1) per check/mark`
- Space: `O(U)`

Where:

- `U` = value domain size.

## Pitfalls / 常見陷阱

- Version overflow in extremely many rounds.
  / 輪數極大時要注意版本號溢位。
- Input values must be validated within `[0, U]` before indexing.
  / 先確認值在索引範圍內。
- If `U` is huge and sparse, hash set/map is better.
  / 值域過大且稀疏時改用雜湊。

## Implementation Notes / 實作細節

- Typical initialization:
  - `let mut seen_ver = vec![0i32; U + 1];`
  - `let mut version = 0i32;`
- In competitive coding constraints, this often yields lower constants than `HashSet`.
- If overflow risk exists, periodically clear array and reset `version` to 1.

## Related Problems / 相關題目

- [q3719](../leetcode/q3719.md)
