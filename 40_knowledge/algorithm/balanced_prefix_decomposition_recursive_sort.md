---
title: Balanced Prefix Decomposition + Recursive Descending Reorder / 平衡前綴分塊 + 遞迴降序重排
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-02-20
updated: 2026-02-20
status: active
source: knowledge
complexity_time: O(n^2 log n)
complexity_space: O(n^2)
review_interval_days: 14
next_review: 2026-03-06
---
# Balanced Prefix Decomposition + Recursive Descending Reorder / 平衡前綴分塊 + 遞迴降序重排

## Goal

Given a string that can be decomposed into balanced primitive blocks, produce the lexicographically maximum result under allowed adjacent block swaps.
對可分解為平衡 primitive 區塊的字串，在允許相鄰區塊交換下，求字典序最大結果。

## When to Use

- Input has a balance invariant (`+1/-1`, parentheses-like).
  / 輸入具備平衡不變量（如 `+1/-1`、括號結構）。
- Valid segments can be split at points where running balance returns to zero.
  / 可在前綴平衡回到 0 的位置切出合法區段。
- Objective is lexicographic optimization by reordering independent top-level blocks.
  / 目標是透過重排獨立頂層區塊做字典序最佳化。

## Core Idea

1. Scan once with `balance` to split into top-level primitive blocks.
   / 以 `balance` 一次掃描，切出頂層 primitive blocks。
2. Each block is structurally `open + inner + close`; recursively optimize `inner`.
   / 每個區塊可寫成 `open + inner + close`，對 `inner` 遞迴最佳化。
3. After all top-level blocks are individually optimized, sort them in descending lexicographic order and concatenate.
   / 本層所有區塊最佳化後做字典序降序排序再串接。
4. Recursion bottoms out at empty or minimal block.
   / 遞迴在空字串或最小區塊時結束。

Why sorting descending works:
把區塊降序排列為何正確：

- Top-level blocks are independent movable units.
  / 頂層區塊彼此獨立且可交換。
- For lexicographic maximum, place larger prefix first (exchange argument).
  / 字典序最大化的交換論證：較大的區塊應放前面。

## Steps

1. Initialize `balance = 0`, `start = 0`, `blocks = []`.
2. Iterate index `i` over string:
   - update balance (`'1'` => `+1`, `'0'` => `-1`).
   - if `balance == 0`, extract one top-level block `[start..i]`.
3. For each extracted block, recursively solve inner `[start+1..i-1]`.
4. Rebuild block as `"1" + solved_inner + "0"` and push into `blocks`.
5. Sort `blocks` descending, then `concat`.
6. Return concatenated result.

## Complexity

- Time: `O(n^2 log n)`
- Space: `O(n^2)`

Where:
`n`: input string length.

Notes:
- Sorting appears at each recursion layer; total string materialization adds another factor.
- For `n <= 50` (like LeetCode 761), this is comfortably fast.

## Pitfalls

- Splitting with wrong boundaries (e.g., not resetting `start` after `balance==0`).
  / 切塊邊界寫錯（忘記更新 `start`）。
- Sorting ascending by mistake.
  / 排序方向寫反（升序）。
- Recursive slicing on non-ASCII strings with byte indices.
  / 若字串非 ASCII，用 byte index 切片會出錯。
- Forgetting that each block includes outer `1` and `0` wrappers.
  / 忘記重建 block 時要加外層 `1`、`0`。

## Examples

Input: `s = "11011000"`

- Top-level decomposition by balance:
  - `"11011000"` is one outer block: `1 + "101100" + 0`
- Recurse into `"101100"`:
  - blocks: `"10"`, `"1100"`
  - optimize inners: both already optimal
  - sort descending: `"1100"`, `"10"`
  - merged: `"110010"`
- Rebuild outer: `"1" + "110010" + "0" = "11100100"`

## Notes

- This pattern is equivalent to operating on Dyck-path mountains: split by return-to-level events, recursively optimize each mountain, then reorder mountains.
- Implementation can be written in a readable string-recursive version or an index-driven low-allocation version.

## Related

- [q761](../leetcode/q761.md)
- [q756](../leetcode/q756.md)
