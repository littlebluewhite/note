---
title: "Grouped Loop (Maximal Segment Enumeration) / 分組迴圈（最大段枚舉）"
category: algorithm
tags: [algorithm]
created: 2026-02-04
updated: 2026-02-04
difficulty: n/a
source: algorithm
status: active
complexity_time: O(n)
complexity_space: O(1)
---
# Grouped Loop (Maximal Segment Enumeration) / 分組迴圈（最大段枚舉）

## Goal

Enumerate **maximal** segments/patterns in an array in overall `O(n)` by moving the scan pointer to the **start of the next group**.

用一次掃描（`O(n)`）列舉陣列中符合某種模式的「最大化片段」（maximal segment），並且每次直接跳到下一段可能的起點。

## When to Use

- The pattern is composed of a few monotonic phases (inc/dec/inc, etc.).
- Once you finish one maximal pattern, you know the **earliest** possible start of the next pattern.

典型場景：
- 由多段單調段組成的模式（例如 inc→dec→inc）
- 完成一個 maximal pattern 後，可以推得下一個 pattern 的最早起點（因此不需要回頭）

## Core Idea / 核心概念

Instead of trying all starts `l`, we do:

1. Starting from `i`, greedily extend phase 1.
2. Then greedily extend phase 2.
3. Then greedily extend phase 3.
4. This yields one **maximal** pattern.
5. Set `i` to a boundary inside the current pattern that is guaranteed to be the earliest start of the next pattern.

在 `i` 位置開始：
- 吃完第一段的最長單調
- 接著吃第二段的最長單調
- 接著吃第三段的最長單調
得到一個 maximal pattern。
然後把 `i` 跳到「下一個 pattern 可能開始的位置」（常見是第三段的起點），保證整體只走過每個元素常數次。

## Example Pattern: Inc → Dec → Inc

This is exactly what LeetCode **Trionic Array** 系列會用到。

Pseudo:

- `i` is current start candidate
- extend `inc` while `a[j] < a[j+1]`
- extend `dec` while `a[j] > a[j+1]`
- extend `inc` while `a[j] < a[j+1]`

If any phase is empty, no valid pattern starting at `i`.
Otherwise you get one maximal triple-phase segment.

## Complexity

- Time: `O(n)` (each index advances monotonically)
- Space: `O(1)`

## Related Problems / 相關題

- [q3637](../leetcode/q3637.md)
- [q3640](../leetcode/q3640.md)
