---
title: "Sliding Window: sum of k smallest / 滑動視窗：維護視窗內 k 個最小值的總和"
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(n log n)
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
canonical: algorithm/sliding_window_k_smallest_sum.md
---
# Sliding Window: sum of k smallest / 滑動視窗：維護視窗內 k 個最小值的總和

## Problem pattern / 題型

Given a sliding window over an array, maintain **the sum of the smallest `m` values** in the current window.
在陣列的滑動視窗中，維護「視窗內最小 `m` 個值的總和」。

This shows up in:
常見於：
- k-smallest in window / 視窗內取 k 小
- sliding window median variants / 480 類型的延伸
- problems requiring min-cost picking under moving range constraints / 需要在移動範圍中挑最小成本

In LeetCode 3013 (Daily 2026-02-02), we need `m = k-2` smallest values in a window determined by `dist`.
在 LeetCode 3013 中，我們要在每一步維護視窗內 `m = k-2` 的最小值總和。

---

## Approach A: Two heaps + lazy deletion (fast) / 兩個 heap + 延遲刪除（快、但容易寫錯）

Maintain:
- `small`: **max-heap** of chosen `m` smallest values (top is the largest among chosen)
- `large`: **min-heap** of the remaining values
- `sum_small`: sum of values currently in `small`
- `del_small`, `del_large`: HashMap counters for lazy deletions

維護：
- `small`：選中的 `m` 個最小值，用 **max-heap** 存（堆頂是被選中集合中的最大值）
- `large`：其餘元素，用 **min-heap** 存
- `sum_small`：`small` 的總和
- `del_*`：用 HashMap 記錄被「應該刪除」但還在 heap 裡的元素次數（lazy deletion）

Operations:
1) insert(x): put into `small` first, then move top to `large` if size too big
2) erase(x): mark for deletion in the heap where it belongs (often inferred by comparing to `small.top`), then prune
3) rebalance: ensure `small.len == m` by moving between heaps, pruning invalid tops

時間複雜度：每步 amortized `O(log n)`。

Notes:
- In Rust, `BinaryHeap` is max-heap; implement min-heap via `Reverse<T>`.
- Lazy deletion is tricky when duplicates exist; always count multiplicities.

參考：
- [[40_knowledge/algorithm/lazy_deletion_priority_queue.md]]
- [[40_knowledge/data_structure/priority_queue_binary_heap.md]]

---

## Approach B: Two multisets (ordered sets) with sum (stable) / 兩個 multiset（最穩）

Use an ordered multiset implementation (in Rust, `BTreeMap<value, count>`):
- `st1`: holds the smallest `m` values
- `st2`: holds the rest
- `sum1`: sum of all values in `st1`

用有序 multiset（Rust 用 `BTreeMap<值, 次數>`）：
- `st1`：存最小的 `m` 個值
- `st2`：存剩下的值
- `sum1`：`st1` 的總和

### Invariant / 不變量

`|st1| == m` (by element count, not distinct keys) and every value in `st1` <= every value in `st2`.
`st1` 的「元素數量」固定是 `m`，且 `st1` 內的值都 <= `st2` 內的值。

### How to rebalance / 如何 rebalance

After each add/remove:
- while `st1_size < m`: move the smallest key from `st2` → `st1` and add to `sum1`
- while `st1_size > m`: move the largest key from `st1` → `st2` and subtract from `sum1`

每次 add/remove 後：
- `st1` 不足 `m`：把 `st2` 的最小值搬到 `st1`
- `st1` 超過 `m`：把 `st1` 的最大值搬到 `st2`

Time complexity: each move is `O(log n)`, so overall `O(n log n)`.

Rust multiset details: [[40_knowledge/data_structure/ordered_multiset_btreemap.md]]

---

## Complexity / 複雜度

- Time: `O(n log n)`
- Space: `O(n)`

Where:
`n`: number of elements.


## Related problems / 相關題

- 480. Sliding Window Median
- 3013. Divide an Array Into Subarrays With Minimum Cost II