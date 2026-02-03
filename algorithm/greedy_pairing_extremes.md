---
title: "Greedy Pairing Extremes / 極值配對貪婪"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(n log n)
complexity_space: O(1)
---
# Greedy Pairing Extremes / 極值配對貪婪

Goal: pair elements to minimize the maximum pair sum (or pair cost by sum).
目標：將元素兩兩配對，使最大配對和（或以加總定義的配對成本）最小。

## Key Idea / 核心觀念

- After sorting, always pair the smallest with the largest.
  / 排序後，最小值配最大值。
- The largest element must belong to some pair, and the smallest partner gives the smallest possible sum for that pair.
  / 最大值一定要配對，配最小值可讓該配對和最小。
- Apply the same argument recursively to the remaining elements.
  / 對剩餘元素重複相同推理即可。

## Algorithm / 演算法

1. Sort the array in ascending order.
   / 將陣列由小到大排序。
2. Use two pointers `l=0`, `r=n-1`, track `ans`.
   / 用雙指標從兩端往內，維護最大配對和 `ans`。
3. While `l < r`, update `ans = max(ans, a[l] + a[r])`, then `l++`, `r--`.
   / 每次計算 `a[l] + a[r]` 更新最大值，再收縮區間。
4. Return `ans`.
   / 回傳 `ans`。

## Correctness Sketch / 正當性簡述

Let the sorted array be `a0 <= a1 <= ... <= a(n-1)`.
設排序後為 `a0 <= a1 <= ... <= a(n-1)`。

- The largest element `a(n-1)` must be paired with some `ai`.
  / 最大值 `a(n-1)` 必須與某個 `ai` 配對。
- The smallest possible sum for a pair containing `a(n-1)` is `a0 + a(n-1)`.
  / 包含 `a(n-1)` 的最小配對和是 `a0 + a(n-1)`。
- Pairing `a(n-1)` with any `ai > a0` yields a sum `>= a0 + a(n-1)`, so it cannot reduce the maximum.
  / 若配到 `ai > a0`，該配對和只會更大，無法降低最大值。
- Therefore, there exists an optimal solution pairing `a0` with `a(n-1)`. Remove them and repeat by induction.
  / 因此一定存在最優解把 `a0` 與 `a(n-1)` 配在一起，移除後對剩餘元素歸納成立。

## Worked Example / 範例

Array: `[3, 5, 2, 3]` -> sorted `[2, 3, 3, 5]`
陣列 `[3, 5, 2, 3]` 排序後為 `[2, 3, 3, 5]`。

- Pair `(2, 5)` sum = 7, pair `(3, 3)` sum = 6.
  / 配 `(2, 5)` 得 7，配 `(3, 3)` 得 6。
- Maximum pair sum is `7`.
  / 最大配對和為 `7`。

## Complexity / 複雜度

- Time: `O(n log n)` for sorting + `O(n)` scan.
  / 時間：排序 `O(n log n)`，掃描 `O(n)`。
- Space: `O(1)` extra if sorting in place.
  / 空間：就地排序為 `O(1)` 額外空間。

## Pitfalls / 常見陷阱

- `n` must be even; every element is paired once.
  / `n` 必須為偶數，元素只能配對一次。
- Use 64-bit when values can overflow 32-bit on addition.
  / 若數值範圍較大，配對和可能溢位，需用 64 位整數。
- The greedy pairing is based on sorted order; skipping sort breaks correctness.
  / 必須先排序，否則貪婪配對不成立。

## Rust Snippet / Rust 範例

```rust
pub fn min_pair_sum(mut nums: Vec<i32>) -> i32 {
    nums.sort_unstable();
    let mut l = 0usize;
    let mut r = nums.len() - 1;
    let mut ans = 0i32;
    while l < r {
        let sum = nums[l] + nums[r];
        if sum > ans {
            ans = sum;
        }
        l += 1;
        r -= 1;
    }
    ans
}
```

## Related Problems / 相關題目

- [q1877](../leetcode/q1877.md)
- [q881](../leetcode/q881.md)
- [q2491](../leetcode/q2491.md)
