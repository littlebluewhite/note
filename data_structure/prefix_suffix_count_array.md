---
title: "Prefix/Suffix Count Array / 前後綴計數陣列"
category: data_structure
tags: [data_structure]
created: 2026-02-03
updated: 2026-02-07
difficulty: "n/a"
source: data_structure
status: active
complexity_time: O(n)
complexity_space: O(n)
---
# Prefix/Suffix Count Array / 前後綴計數陣列

## Purpose / 目的

Store cumulative counts from both directions so each split-point query can be answered in `O(1)`.
同時保存前綴與後綴累積計數，讓每個切點查詢可在 `O(1)` 完成。

## Core Idea / 核心概念

- `prefix[i]` stores the count for interval `[0, i)`.
- `prefix[i]` 儲存區間 `[0, i)` 的累積值。
- `suffix[i]` stores the count for interval `[i, n)`.
- `suffix[i]` 儲存區間 `[i, n)` 的累積值。
- Use length `n + 1` arrays so boundaries `0` and `n` are naturally represented.
- 使用長度 `n + 1` 的陣列可自然涵蓋邊界 `0` 與 `n`。

## Operations / 操作

Build prefix:
建立前綴：

```text
prefix[0] = 0
for i in 0..n-1:
  prefix[i + 1] = prefix[i] + left_bad(a[i])
```

Build suffix:
建立後綴：

```text
suffix[n] = 0
for i in (n-1..0):
  suffix[i] = suffix[i + 1] + right_bad(a[i])
```

Evaluate split `j`:
計算切點 `j`：

```text
cost(j) = prefix[j] + suffix[j]
```

## When to Use / 使用時機

- Need repeated evaluations across all split points.
- 需要對所有切點反覆計算成本。
- Total cost is additive from left and right intervals.
- 總成本可拆成左右區間相加。
- Common in string deletions, shop closing time, and partition penalty problems.
- 常見於字串刪除、關店時機、分割懲罰題型。

## Worked Example / 實作範例

Problem shape: make `s = "aababbab"` balanced (`a* b*`).
題型：讓 `s = "aababbab"` 變為 balanced（`a* b*`）。

- `prefixB[j]`: count `'b'` in `[0, j)`.
- `suffixA[j]`: count `'a'` in `[j, n)`.
- `cost(j) = prefixB[j] + suffixA[j]`.

Computed arrays:
計算結果：

- `prefixB = [0, 0, 0, 1, 1, 2, 3, 3, 4]`
- `suffixA = [4, 3, 2, 2, 1, 1, 1, 0, 0]`

The minimum value over all `j` is `2`.
所有 `j` 中最小值為 `2`。

## Variations / 變化型

- Replace counts with weighted costs.
- 將計數改成加權成本。
- Keep one directional array and derive the other side with running totals.
- 只保留單向陣列，另一側用滾動總和推導。
- Use `i64` when cumulative values may exceed `i32`.
- 累積值可能超過 `i32` 時改用 `i64`。

## Complexity / 複雜度

- Build time: `O(n)`
- Query time per split: `O(1)`
- Full split scan: `O(n)`
- Space: `O(n)`

## Pitfalls / 常見陷阱

- Mixing inclusive/exclusive interval definitions.
- 把 `[0, j)` 與 `[j, n)` 的定義寫混。
- Forgetting boundary splits `j = 0` and `j = n`.
- 漏掉邊界切點 `j = 0` 與 `j = n`。
- Using length `n` arrays instead of `n + 1`.
- 陣列長度只開 `n` 容易造成邊界錯誤。

## Implementation Notes / 實作細節

- In Rust, `Vec<i32>` is sufficient for count-only tasks up to `1e5`.
- Rust 在 `1e5` 規模的純計數題通常用 `Vec<i32>` 即可。
- Build suffix by reverse iteration: `for i in (0..n).rev()`.
- 後綴建表可用反向迴圈：`for i in (0..n).rev()`。
- Use explicit names (`prefix_b`, `suffix_a`) to reduce semantic bugs.
- 用明確命名（如 `prefix_b`、`suffix_a`）降低語意混淆。

## Related Problems / 相關題目

- [q2483](../leetcode/q2483.md)
- [q1653](../leetcode/q1653.md)
