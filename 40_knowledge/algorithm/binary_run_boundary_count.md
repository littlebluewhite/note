---
title: Binary Run Boundary Count / 二元連續段邊界計數
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-19
updated: 2026-02-19
status: active
source: algorithm
complexity_time: O(n)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-03-05
---
# Binary Run Boundary Count / 二元連續段邊界計數

## Goal

Count valid substrings/subarrays formed by two adjacent runs in a binary sequence without enumerating all substrings.
在二元序列中，不枚舉所有子字串，直接計算由相鄰兩個連續段形成的合法子字串數量。

## When to Use

- Input is binary-like (two categories), and valid answers are built from two adjacent homogeneous runs.
- 題目是二元分類，且合法答案由相鄰兩段同值區塊組成。
- A candidate interval must have balanced counts from both sides of a boundary.
- 合法區間要在邊界兩側達到數量平衡。
- Need `O(n)` one-pass counting with constant extra memory.
- 需要單趟 `O(n)` 且額外空間 `O(1)`。

## Core Idea

Let run lengths be `g0, g1, g2, ...`.
令連續段長為 `g0, g1, g2, ...`。

For each adjacent pair `(gi, g{i+1})`, the number of valid intervals crossing their boundary is:
對每對相鄰段 `(gi, g{i+1})`，跨越該邊界的合法區間數為：

`min(gi, g{i+1})`

Total answer:
總答案：

`sum(min(gi, g{i+1}))`

This can be streamed with two counters: previous run length and current run length.
這個公式可以用兩個計數器串流計算：前一段長度與目前段長度。

## Steps

1. Initialize `prev_run = 0`, `curr_run = 1`, `ans = 0`.
2. Scan from index `1` to `n - 1`.
3. If `s[i] == s[i-1]`, extend current run: `curr_run += 1`.
4. Else boundary reached:
   - add `min(prev_run, curr_run)` to `ans`.
   - shift runs: `prev_run = curr_run`, `curr_run = 1`.
5. After loop, add final `min(prev_run, curr_run)`.

Pseudo-code:

```text
prev = 0
curr = 1
ans = 0
for i in [1..n-1]:
  if s[i] == s[i-1]:
    curr += 1
  else:
    ans += min(prev, curr)
    prev = curr
    curr = 1
ans += min(prev, curr)
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

Where:
`n`: sequence length.

## Pitfalls

- Forgetting the final add after loop (`ans += min(prev, curr)`).
- 漏掉掃描結束後最後一組邊界貢獻。
- Misunderstanding the valid pattern: intervals must be exactly two grouped runs, not multi-switch segments.
- 把多次切換（如 `00110011`）誤當成單一合法區間。
- Initializing `curr_run` incorrectly when `n >= 1`.
- 初始化段長時 off-by-one。

## Examples

Input `s = "00110011"`.
輸入 `s = "00110011"`。

Run lengths are `[2, 2, 2, 2]`.
連續段長為 `[2, 2, 2, 2]`。

Answer is:
答案：

`min(2,2) + min(2,2) + min(2,2) = 6`

Input `s = "10101"` has run lengths `[1,1,1,1,1]`, answer `4`.
輸入 `s = "10101"` 的段長為 `[1,1,1,1,1]`，答案為 `4`。

## Notes

- Equivalent implementation: build full run-length array then sum adjacent minimums.
- 等價寫法是先建 run-length 陣列，再做相鄰最小值加總。
- The two-counter streaming form is usually preferred for interviews and large input.
- 面試與大輸入通常優先採用雙計數器串流版本。

## Related

- [q696](../leetcode/q696.md)
