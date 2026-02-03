---
title: "Pairwise Distance Enumeration / 兩兩距離枚舉"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(k^2)
complexity_space: O(k^2)
---
# Pairwise Distance Enumeration / 兩兩距離枚舉

Goal: enumerate all possible distances between any two positions in 1D.
目標：列舉一維座標中任意兩點的距離集合。

## When to use / 何時使用

- Any two lines/points can become boundaries after removals.
  / 任意兩條線或點都可能成為邊界。
- Input size is small enough for `O(k^2)` enumeration.
  / 座標數量小，能接受 `O(k^2)` 列舉。

## Pattern / 流程

1. Collect positions and add fixed boundaries if required.
   / 收集座標，必要時加入邊界。
2. Sort ascending to keep distances positive.
   / 升冪排序，距離自然為正。
3. For each `i < j`, compute `d = pos[j] - pos[i]`, store in a set.
   / 枚舉 `i < j`，計算距離放入集合。
4. Use the set for membership queries or intersection with another axis.
   / 使用集合做查找或與另一方向取交集。

## Worked Example / 實作範例

Positions: `[1, 2, 4]`
座標：`[1, 2, 4]`

- Pairwise distances: `2-1 = 1`, `4-1 = 3`, `4-2 = 2`.
  / 兩兩距離：`2-1 = 1`、`4-1 = 3`、`4-2 = 2`。
- Distance set: `{1, 2, 3}`.
  / 距離集合：`{1, 2, 3}`。

## Pitfalls / 常見陷阱

- Forgetting to include fixed boundaries like `1` and `m`.
  / 忘記加入固定邊界。
- Using `i32` when `distance^2` may overflow.
  / 距離平方可能溢位，請用 `i64`。
- `O(k^2)` space can be large when `k` grows.
  / `O(k^2)` 空間在 `k` 大時會爆。

## Complexity / 複雜度

- Time: `O(k^2)` for `k` positions.
  / 時間：`O(k^2)`。
- Space: `O(k^2)` for the distance set.
  / 空間：`O(k^2)`。

## Rust snippet / Rust 範例

```rust
use std::collections::HashSet;

fn all_distances(pos: &Vec<i64>) -> HashSet<i64> {
    let mut set = HashSet::new();
    for i in 0..pos.len() {
        for j in (i + 1)..pos.len() {
            set.insert(pos[j] - pos[i]);
        }
    }
    set
}
```

## Related problems / 相關題目

- [q2975](../leetcode/q2975.md)
