---
title: Prefix/Suffix Penalty Scan / 前後綴懲罰掃描
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-07
status: active
source: algorithm
complexity_time: O(n)
complexity_space: O(n) ~ O(1)
review_interval_days: 14
next_review: 2026-02-17
canonical: algorithm/prefix_suffix_penalty_scan.md
---
# Prefix/Suffix Penalty Scan / 前後綴懲罰掃描

## Goal

Given a sequence and a split point `j`, minimize `left_cost(j) + right_cost(j)` by scanning all splits once.
給定序列與切點 `j`，在線性掃描中最小化 `left_cost(j) + right_cost(j)`。

## When to Use

- The objective can be decomposed into independent left and right penalties.
- 題目成本可拆成左右兩側互不干擾的懲罰和。
- You need the minimum cost split (sometimes with earliest-index tie break).
- 需要找最小成本切點（有時要同分取最早）。
- Typical forms: delete/keep penalties, open/close penalties, bad-item counts.
- 常見型態：刪除成本、營業/關店懲罰、左右不良元素計數。

## Core Idea

- Define split `j` as left interval `[0, j)` and right interval `[j, n)`.
- 定義切點 `j` 對應左區間 `[0, j)`、右區間 `[j, n)`。
- Precompute:
- 預先計算：
- `prefix_bad[j]`: bad count (or penalty) in the left part.
- `prefix_bad[j]`：左側不良數（或左側懲罰）。
- `suffix_bad[j]`: bad count (or penalty) in the right part.
- `suffix_bad[j]`：右側不良數（或右側懲罰）。
- Then evaluate all splits in `O(1)` each:
- 接著每個切點可 `O(1)` 計算：
- `cost(j) = prefix_bad[j] + suffix_bad[j]`.
- `cost(j) = prefix_bad[j] + suffix_bad[j]`。

## Steps

1. Define what is "bad" on the left and on the right.
2. 定義左側與右側各自要計入的「不良」條件。
3. Build `prefix_bad` from left to right.
4. 由左到右建立 `prefix_bad`。
5. Build `suffix_bad` from right to left.
6. 由右到左建立 `suffix_bad`。
7. Scan all `j in [0, n]`, compute `cost(j)`, keep minimum (and earliest on tie if required).
8. 掃描所有切點 `j`，計算 `cost(j)`，維持最小值（若有同分規則則同步處理）。

## Complexity

- Time: `O(n)` (build + scan).
- Space: `O(n)` with prefix/suffix arrays.
- Space can be reduced to `O(1)` when the split cost can be updated incrementally.

## Pitfalls

- Off-by-one mistakes around `[0, j)` and `[j, n)`.
- Tie-breaking (earliest or latest split) is easy to miss.
- Forgetting to include boundary splits `j = 0` and `j = n`.

## Examples

Example problem: split `s = "aababbab"` to minimize deletions for form `a* b*`.
範例：將 `s = "aababbab"` 切成左右兩段，最小化刪除數使結果為 `a* b*`。

- Left bad = `'b'` in `[0, j)`.
- 左側不良 = `[0, j)` 的 `'b'`。
- Right bad = `'a'` in `[j, n)`.
- 右側不良 = `[j, n)` 的 `'a'`。
- Compute `prefixB` and `suffixA`, then find minimum of `prefixB[j] + suffixA[j]`.
- 計算 `prefixB` 與 `suffixA`，取最小 `prefixB[j] + suffixA[j]`。
- Best cost is `2`.
- 最小成本為 `2`。

## Notes

- This is a split-scan framework, not limited to strings.
- 這是通用切點掃描框架，不限字串題。
- Many problems have an equivalent `O(1)` running-score variant after algebraic simplification.
- 許多題目在代數化後可改寫成 `O(1)` 空間的滾動分數版本。

## Related

- [q2483](../leetcode/q2483.md)
- [q1653](../leetcode/q1653.md)
