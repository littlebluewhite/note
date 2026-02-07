---
title: Ordered Multiset via BTreeMap / 用 BTreeMap 實作有序 Multiset
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: data_structure
complexity_time: O(log n) per op
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
canonical: data_structure/ordered_multiset_btreemap.md
---
# Ordered Multiset via BTreeMap / 用 BTreeMap 實作有序 Multiset

Rust 沒有內建 multiset（像 C++ `multiset`），但我們可以用：

- `BTreeMap<T, i32>`：key 是值、value 是出現次數
- 另外自己維護：`size`（元素總數，含重複）與 `sum`（可選）

適用場景：
- 需要 ordered set + duplicates
- 需要取最小/最大（`first_key_value` / `last_key_value`）
- 需要插入、刪除、搬移元素並維持順序

---

## Core ops / 核心操作

### Insert one / 插入一個

```rust
fn insert_one(map: &mut BTreeMap<i32, i32>, key: i32) {
    *map.entry(key).or_insert(0) += 1;
}
```

### Remove one / 刪除一個（若不存在回傳 false）

```rust
fn remove_one(map: &mut BTreeMap<i32, i32>, key: i32) -> bool {
    if let Some(cnt) = map.get_mut(&key) {
        *cnt -= 1;
        if *cnt == 0 {
            map.remove(&key);
        }
        true
    } else {
        false
    }
}
```

### Pop min / 取出最小值（一次）

```rust
fn pop_min(map: &mut BTreeMap<i32, i32>) -> Option<i32> {
    let key = *map.first_key_value()?.0;
    remove_one(map, key);
    Some(key)
}
```

### Pop max / 取出最大值（一次）

```rust
fn pop_max(map: &mut BTreeMap<i32, i32>) -> Option<i32> {
    let key = *map.last_key_value()?.0;
    remove_one(map, key);
    Some(key)
}
```

---

## Pattern: two multisets + sum of k smallest

常用在「維護視窗內最小 k 個元素的總和」：

- `st1`: k 個最小（維護 sum1）
- `st2`: 其餘

不變量：
- `st1_size == k`
- `max(st1) <= min(st2)`

每次 insert/remove 後呼叫 `rebalance()`：
- st1 不足：st2 的 min → st1
- st1 過多：st1 的 max → st2

LeetCode 3013 就是這個模板。
## Complexity / 複雜度

- Time: `O(log n) per op`
- Space: `O(n)`

Where:
`n`: number of elements.
