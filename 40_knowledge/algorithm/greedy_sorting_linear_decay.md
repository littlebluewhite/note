---
title: Greedy Sorting with Linear Decay / 遞減回合的貪婪排序
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(n log n + k)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-02-17
canonical: algorithm/greedy_sorting_linear_decay.md
---
# Greedy Sorting with Linear Decay / 遞減回合的貪婪排序

## Problem Pattern / 題型特徵

- You must pick `k` items over `k` turns.
  / 必須在 `k` 回合內挑出 `k` 個物件。
- After each pick, all unpicked items decrease by `1` (or a fixed amount).
  / 每回合未被選到的物件都會減 `1`（或固定量）。
- Each item’s gain depends on its pick time.
  / 每個物件的收益會受「被選的回合」影響。

## Key Idea / 核心觀念

If an item starts with value `h`, then choosing it at turn `t` yields:

```
gain = max(h - t, 0)
```

因此要讓總和最大，應該把「較大」的 `h` 放在「較早」的回合。

## Algorithm / 演算法

1. Sort values in **descending** order.
   / 依數值由大到小排序。
2. For `i = 0..k-1`, add `max(values[i] - i, 0)`.
   / 對前 `k` 個元素，累加 `max(values[i] - i, 0)`。

## Correctness Sketch / 正當性簡述

- Exchange argument: for any two items `a >= b`,
  picking `a` earlier and `b` later never decreases the total.
- Therefore, the optimal order is non-increasing by initial value.
- Sorting plus the formula gives the optimal sum.

交換論證：若 `a >= b`，把 `a` 放在更早的回合不會使總和變小，因此排序後依序選取最優。

## Complexity / 複雜度

- Time: `O(n log n + k)`
- Space: `O(1)`

Where:
`n`: number of items.
`k`: number of picks/turns.


- Sorting: `O(n log n)`
- Summation: `O(k)`
- Extra space: `O(1)` (in-place sort)

## Pitfalls / 常見陷阱

- Use `i64` (or 64-bit) for the sum to avoid overflow.
  / 總和請用 64 位整數避免溢位。
- Stop at `max(x, 0)` since values cannot be negative.
  / 需要取 `max(x, 0)`，快樂值不會為負。

## Rust Snippet / Rust 範例

```rust
values.sort_unstable_by(|a, b| b.cmp(a));
let mut total: i64 = 0;
for i in 0..k {
    let gain = values[i] as i64 - i as i64;
    if gain > 0 {
        total += gain;
    }
}
```

## Related Problems / 相關題目

- [q3075](../leetcode/q3075.md)