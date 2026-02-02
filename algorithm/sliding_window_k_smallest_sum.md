# Sliding Window: Sum of K Smallest / 滑動視窗取最小 K 個和

Goal: maintain the sum of the smallest `k` values inside a sliding window.
目標：在滑動視窗中維持「最小 `k` 個值的總和」。

## When to use / 使用時機

- Window slides by one step; need the smallest `k` elements each time.
  / 視窗每次只移動一格，且每一步都要拿出最小 `k` 個元素。
- Typical in problems like “pick `k-2` smallest in a range” or “window median variants.”
  / 常見於「區間內挑最小 `k-2` 個」或「滑窗中位數變形題」。

## Core idea / 核心概念

Maintain two ordered multisets:
維護兩個有序 multiset：

- `st1`: the smallest `k` elements (track their sum).
  / `st1`：目前視窗中最小的 `k` 個元素（維護其總和）。
- `st2`: the remaining elements.
  / `st2`：其餘元素。

Invariant:
不變量：

- `st1` always has exactly `k` elements.
  / `st1` 的元素數量永遠為 `k`。
- All elements in `st1` are `<=` all elements in `st2`.
  / `st1` 內任一元素 `<= st2` 內任一元素。

## Operations / 操作

### Add x / 新增元素

1. If `st2` is not empty and `x >= min(st2)`, insert into `st2`.
2. Else insert into `st1` and add to sum.
3. Rebalance to restore size invariant.

加入 `x`：
1. 若 `st2` 非空且 `x >= min(st2)`，丟進 `st2`。
2. 否則進 `st1` 並累加 sum。
3. 重新平衡。

### Remove x / 移除元素

1. Try to remove from `st1`; if removed, subtract from sum.
2. Else remove from `st2`.
3. Rebalance.

移除 `x`：
1. 優先從 `st1` 刪；刪到就更新 sum。
2. 否則從 `st2` 刪。
3. 重新平衡。

### Rebalance / 平衡

- If `st1` has fewer than `k`, move the smallest from `st2` to `st1`.
- If `st1` has more than `k`, move the largest from `st1` to `st2`.

若 `st1` 太小，就從 `st2` 取最小補回；
若 `st1` 太大，就把 `st1` 最大值移到 `st2`。

## Complexity / 複雜度

- Each add/remove/rebalance: `O(log n)`.
- Total for sliding window over `n`: `O(n log n)`.

## Pitfalls / 注意事項

- Must support duplicates: use multiset (value -> count).
  / 必須支援重複值，需用 multiset（值 -> 次數）。
- Rebalance after every update to keep `st1` size correct.
  / 每次更新後都要平衡，確保 `st1` 大小正確。
- When window size is smaller than `k`, define behavior (usually not used).
  / 視窗大小小於 `k` 時需要明確定義（多數題目不會用到）。

## Template (Rust, BTreeMap multiset) / 模板（Rust）

```rust
use std::collections::BTreeMap;

struct KSmallestSum {
    k: usize,
    st1: BTreeMap<i32, i32>,
    st2: BTreeMap<i32, i32>,
    sum: i64,
    s1: usize,
    s2: usize,
}

impl KSmallestSum {
    fn new(k: usize) -> Self {
        Self { k, st1: BTreeMap::new(), st2: BTreeMap::new(), sum: 0, s1: 0, s2: 0 }
    }

    fn add_one(map: &mut BTreeMap<i32, i32>, key: i32) {
        *map.entry(key).or_insert(0) += 1;
    }

    fn remove_one(map: &mut BTreeMap<i32, i32>, key: i32) -> bool {
        if let Some(c) = map.get_mut(&key) {
            *c -= 1;
            if *c == 0 { map.remove(&key); }
            true
        } else { false }
    }

    fn first_key(map: &BTreeMap<i32, i32>) -> Option<i32> {
        map.keys().next().copied()
    }

    fn last_key(map: &BTreeMap<i32, i32>) -> Option<i32> {
        map.keys().next_back().copied()
    }

    fn rebalance(&mut self) {
        while self.s1 < self.k && !self.st2.is_empty() {
            if let Some(x) = Self::first_key(&self.st2) {
                Self::add_one(&mut self.st1, x);
                Self::remove_one(&mut self.st2, x);
                self.sum += x as i64;
                self.s1 += 1;
                self.s2 -= 1;
            }
        }
        while self.s1 > self.k {
            if let Some(x) = Self::last_key(&self.st1) {
                Self::add_one(&mut self.st2, x);
                Self::remove_one(&mut self.st1, x);
                self.sum -= x as i64;
                self.s1 -= 1;
                self.s2 += 1;
            }
        }
    }

    fn add(&mut self, x: i32) {
        if !self.st2.is_empty() && x >= *self.st2.keys().next().unwrap() {
            Self::add_one(&mut self.st2, x);
            self.s2 += 1;
        } else {
            Self::add_one(&mut self.st1, x);
            self.sum += x as i64;
            self.s1 += 1;
        }
        self.rebalance();
    }

    fn erase(&mut self, x: i32) {
        if Self::remove_one(&mut self.st1, x) {
            self.sum -= x as i64;
            self.s1 -= 1;
        } else if Self::remove_one(&mut self.st2, x) {
            self.s2 -= 1;
        }
        self.rebalance();
    }

    fn sum(&self) -> i64 { self.sum }
}
```

## Related problems / 相關題目

- [3013. Divide an Array Into Subarrays With Minimum Cost II](../leetcode/q3013.md)
- [480. Sliding Window Median](https://leetcode.com/problems/sliding-window-median/)
