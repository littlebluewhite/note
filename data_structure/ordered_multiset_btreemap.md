# Ordered Multiset with BTreeMap / 有序多重集合 (BTreeMap)

Goal: support ordered insert/delete and min/max queries with duplicates.
目標：支援有序插入/刪除與最小/最大查詢，且可重複。

## Why BTreeMap / 為什麼用 BTreeMap

- `BTreeMap` keeps keys sorted and supports `O(log n)` insert/delete.
  / `BTreeMap` 會維持 key 有序，插入/刪除為 `O(log n)`。
- By storing counts, it becomes a multiset.
  / 透過「值 -> 次數」即可成為 multiset。

## Core operations / 核心操作

### Insert / 插入

```rust
*map.entry(x).or_insert(0) += 1;
```

### Remove one occurrence / 刪除一次

```rust
if let Some(c) = map.get_mut(&x) {
    *c -= 1;
    if *c == 0 { map.remove(&x); }
}
```

### Get min / 取最小值

```rust
let min_key = map.keys().next().copied();
```

### Get max / 取最大值

```rust
let max_key = map.keys().next_back().copied();
```

## Patterns / 常用型態

- Two-multiset split: maintain smallest `k` in one, rest in another.
  / 雙 multiset 分割：一個放最小 `k` 個，其餘放另一個。
- Lazy deletion with counts for sliding windows.
  / 滑動視窗中用計數實作延遲刪除。

## Complexity / 複雜度

- Insert/delete/min/max: `O(log n)`.
- Space: `O(n)`.

## Pitfalls / 注意事項

- Always update counts; remove key when count hits zero.
  / 次數歸零必須刪 key。
- Use `i64` for sum if values can be large.
  / 若元素值大，總和請用 `i64`。

## Related problems / 相關題目

- [3013. Divide an Array Into Subarrays With Minimum Cost II](../leetcode/q3013.md)
- [480. Sliding Window Median](https://leetcode.com/problems/sliding-window-median/)
