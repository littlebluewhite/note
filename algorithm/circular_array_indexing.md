---
title: "Circular Array Indexing / 環狀陣列索引"
category: algorithm
tags: [algorithm]
created: 2026-02-05
updated: 2026-02-05
difficulty: n/a
source: algorithm
status: active
complexity_time: O(1) per index
complexity_space: O(1)
---
# Circular Array Indexing / 環狀陣列索引

## Goal

Map any left/right movement to a valid index in a circular array.
把任意左/右移動轉成合法的環狀索引。

## When to Use

- Circular arrays, ring buffers, or wrap-around indexing.
- Moving by positive or negative steps and always staying inside `[0, n-1]`.
- Any simulation that needs “wrap” behavior without loops.

## Core Idea

Use modulo with **Euclidean remainder** so negative offsets still map into `[0, n-1]`.
用「歐幾里得餘數」處理負數，確保索引落在 `[0, n-1]`。

Formula:

- `j = (i + step) mod n`
- In Rust: `j = (i + step).rem_euclid(n)`
- In languages without `rem_euclid`: `j = ((i + step) % n + n) % n`

## Steps

1. Let `n = len`.
2. For each index `i`, compute `offset = i + step`.
3. Normalize: `j = offset.rem_euclid(n)`.
4. Use `j` as the wrapped index.

## Complexity

- Time: `O(1)` per index.
- Space: `O(1)`.

## Pitfalls

- `%` in many languages keeps the sign of the dividend; negative values must be fixed.
- Large steps still need normalization (always mod by `n`).
- `n` must be positive; handle empty arrays separately if applicable.

## Examples

Array length `n = 4`:

- `i = 1`, `step = -2` → `j = (1 - 2).rem_euclid(4) = 3`.
- `i = 3`, `step = 1` → `j = (3 + 1).rem_euclid(4) = 0`.

## Notes

- This is a building block for circular scans, rotations, and ring buffers.
- If you apply multiple steps, add them first, then mod once.

## Related problems / 相關題目

- [q3379](../leetcode/q3379.md)
