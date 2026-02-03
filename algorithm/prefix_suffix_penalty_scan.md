---
title: "Prefix/Suffix Penalty Scan / 前後綴懲罰掃描"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(n)
complexity_space: O(n)
---
# Prefix/Suffix Penalty Scan / 前後綴懲罰掃描

Goal: find the earliest split index that minimizes total penalty computed from left and right sides.
目標：找出使左右兩側懲罰總和最小且最早的切點。

## Key idea / 核心想法

- When a cost decomposes into "left part + right part", precompute both sides and scan all split points.
  / 當成本可拆成「左側 + 右側」時，先計算兩側，再掃描所有切點。
- For split `j`, total penalty = `left_bad[0..j)` + `right_bad[j..n)`.
  / 切點 `j` 的總懲罰 = 左側不良數 + 右側不良數。

## Pattern / 流程

1. Build prefix counts for the left-side penalty.
   / 建立左側前綴計數。
2. Build suffix counts for the right-side penalty.
   / 建立右側後綴計數。
3. Scan `j = 0..=n`, compute `penalty = prefix[j] + suffix[j]`, keep the smallest; on ties keep the earliest.
   / 掃描所有 `j`，計算懲罰並維持最小值，若同分保留最早切點。

## Why it works / 正確性直覺

- Each position contributes to exactly one side of the split, so the total penalty is the sum of two independent counts.
  / 每個位置只會落在其中一側，因此懲罰可拆成兩個獨立計數相加。

## Complexity / 複雜度

- Time: `O(n)` build + `O(n)` scan.
  / 時間：`O(n)`。
- Space: `O(n)` for two count arrays (can be reduced to `O(1)` with a running score).
  / 空間：`O(n)`，也可用滾動更新降為 `O(1)`。

## Pitfalls / 常見陷阱

- Off-by-one: a split at `j` means `[0, j)` on the left and `[j, n)` on the right.
  / 切點 `j` 表示左側 `[0, j)`、右側 `[j, n)`。
- If multiple `j` share the same minimum, keep the earliest.
  / 多個最小值時要選最早的 `j`。

## Related problems / 相關題目

- [q2483](../leetcode/q2483.md)