---
title: Range Enumeration + Popcount Filter / 區間枚舉 + 置位數篩選
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-02-21
updated: 2026-02-21
status: active
source: knowledge
complexity_time: O(R)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-03-07
---
# Range Enumeration + Popcount Filter / 區間枚舉 + 置位數篩選

## Goal

Count or collect numbers in an integer interval `[L, R]` by filtering with their bit-count feature (`popcount`).
在整數區間 `[L, R]` 中，透過每個數字的置位數（`popcount`）做條件篩選，完成計數或收集答案。

## When to Use

- The range width `R - L` is moderate and direct scan is affordable.
  / 區間寬度 `R - L` 不大，線性掃描可接受。
- The filter can be computed in constant time with bit operations.
  / 篩選條件可用位元運算常數時間計算。
- You need deterministic and easy-to-verify logic.
  / 需要可驗證、穩定且容易實作的解法。

## Core Idea

- Enumerate every integer in the target range exactly once.
  / 對區間中每個整數完整掃描一次。
- Compute `k = popcount(x)` using intrinsic operation (`count_ones`).
  / 用內建函式（如 `count_ones`）計算 `k = popcount(x)`。
- Keep `x` if `k` satisfies a property (e.g., `k` is prime).
  / 若 `k` 符合條件（例如為質數）就保留或計數。

## Steps

1. Initialize answer container/counter.
   / 初始化答案容器或計數器。
2. For each `x` in `[L, R]`, compute `k = popcount(x)`.
   / 對每個 `x` 計算 `k = popcount(x)`。
3. Check predicate `P(k)` and keep when true.
   / 檢查條件 `P(k)`，成立則收下。
4. Return final result.
   / 回傳最終結果。

## Complexity

- Time: `O(R)` where `R = right - left + 1`.
- Space: `O(1)` (excluding output collection).

## Pitfalls

- Forgetting inclusive bounds (`left..=right`) causes off-by-one errors.
  / 忘記使用閉區間會產生 off-by-one。
- Mixing signed and unsigned bit operations without explicit casting.
  / 有號與無號位元運算混用、未轉型容易踩雷。
- Recomputing heavy predicates when a tiny lookup table is possible.
  / 若條件值域很小，卻重複做昂貴判斷會浪費常數。

## Examples

For `left = 6`, `right = 10`:
對 `left = 6`, `right = 10`：

- `6 (110)` -> `popcount = 2`
- `7 (111)` -> `popcount = 3`
- `8 (1000)` -> `popcount = 1`
- `9 (1001)` -> `popcount = 2`
- `10 (1010)` -> `popcount = 2`

If predicate is "popcount is prime", valid numbers are `6, 7, 9, 10`.
若條件是「置位數為質數」，合法數字為 `6, 7, 9, 10`。

Rust snippet:

```rust
fn count_with_popcount_filter(left: i32, right: i32, ok: impl Fn(u32) -> bool) -> i32 {
    let mut ans = 0;
    for x in left..=right {
        let k = (x as u32).count_ones();
        if ok(k) {
            ans += 1;
        }
    }
    ans
}
```

## Notes

- This is often the clean baseline before trying DP/bit-DP optimizations.
  / 這通常是進入 DP/bit-DP 前最穩定的基線方案。
- When popcount upper bound is tiny, pair with constant-time lookup.
  / 當置位數上界很小時，可搭配常數時間查表再降常數。

## Related

- [q762](../leetcode/q762.md)
- [q401](../leetcode/q401.md)
- [191. Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/)
- [338. Counting Bits](https://leetcode.com/problems/counting-bits/)
