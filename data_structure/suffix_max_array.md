---
title: "Suffix Max Array / 後綴最大值陣列"
category: data_structure
tags: [data_structure]
created: 2026-02-03
updated: 2026-02-03
difficulty: "n/a"
source: data_structure
status: active
complexity_time: O(n) build, O(1) query
complexity_space: O(n)
---
# Suffix Max Array / 後綴最大值陣列

Goal: answer "maximum value in suffix `[i, n)`" in `O(1)`.
目標：用 `O(1)` 查詢區間 `[i, n)` 的最大值。

## Core idea / 核心概念

- Precompute from right to left:
  / 從右往左預先計算：
  - `suffix_max[i] = max(arr[i], suffix_max[i + 1])`
  - `suffix_max[n] = base` (often `0` or `-INF`)
    / `suffix_max[n]` 為基底值（常用 `0` 或 `-INF`）

## Pattern / 流程

1. Allocate `suffix_max` with length `n + 1`.
   / 建立長度 `n + 1` 的陣列。
2. Set base value at `suffix_max[n]`.
   / 設定基底值。
3. Iterate `i` from `n - 1` down to `0`:
   / 由右往左更新。

## Example / 範例

Array: `[2, 5, 1, 4]`

- `suffix_max[4] = 0`
- `suffix_max[3] = max(4, 0) = 4`
- `suffix_max[2] = max(1, 4) = 4`
- `suffix_max[1] = max(5, 4) = 5`
- `suffix_max[0] = max(2, 5) = 5`

Query: max from index 2 -> `suffix_max[2] = 4`.

## Rust snippet / Rust 範例

```rust
fn build_suffix_max(arr: &Vec<i32>) -> Vec<i32> {
    let n = arr.len();
    let mut suffix_max = vec![0; n + 1];
    for i in (0..n).rev() {
        let v = arr[i];
        suffix_max[i] = if suffix_max[i + 1] > v { suffix_max[i + 1] } else { v };
    }
    suffix_max
}
```

## When to use / 使用時機

- Offline queries for max in suffix ranges.
  / 需要多次查詢後綴最大值。
- Combine with binary search for interval scheduling.
  / 搭配二分搜尋做區間選擇。

## Pitfalls / 常見陷阱

- Base value must respect value range (use `-INF` if negatives exist).
  / 若可能有負值，基底要用 `-INF`。
- Forgetting `n + 1` length leads to bounds error.
  / 忘了 `n + 1` 容易越界。

## Complexity / 複雜度

- Time: `O(n) build, O(1) query`
- Space: `O(n)`

Where:
`n`: number of elements.


- Build time: `O(n)`
  / 建表時間：`O(n)`
- Query time: `O(1)`
  / 查詢時間：`O(1)`
  / 空間：`O(n)`

## Related problems / 相關題目

- [q2054](../leetcode/q2054.md)