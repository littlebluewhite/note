---
title: Dynamic Array (Vec) / 動態陣列
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(1) amortized push/pop, O(n) insert
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
---
# Dynamic Array (Vec) / 動態陣列

## Definition / 定義

A dynamic array stores elements in contiguous memory and grows as needed.
動態陣列以連續記憶體存放元素，容量不足時自動擴張。

## Operations / 操作與複雜度

- Time: `O(1) amortized push/pop, O(n) insert`
- Space: `O(n)`

Where:
`n`: number of elements.


- Indexing `v[i]`: `O(1)` / 直接索引為 `O(1)`
- Push/Pop at end: amortized `O(1)` / 尾端新增或刪除為均攤 `O(1)`
- Insert/Delete in middle: `O(n)` / 中間插入或刪除為 `O(n)`
- Iteration: `O(n)` / 走訪為 `O(n)`

## When to Use / 使用時機

- Need fast random access and iteration.
  / 需要快速隨機存取與遍歷。
- Want to sort values in place.
  / 需要原地排序。

## Rust Notes / Rust 注意事項

- `Vec<T>` is the standard dynamic array.
  / `Vec<T>` 是 Rust 的標準動態陣列。
- `sort_unstable()` or `sort_unstable_by(...)` sorts in place.
  / `sort_unstable()` 可原地排序，通常更快且省記憶體。
- Use `i64` when summing many `i32` values.
  / 多個 `i32` 加總時，建議轉為 `i64` 避免溢位。

## Example / 範例

```rust
let mut v = vec![3, 1, 2];
v.sort_unstable();
let first = v[0];
```

## Pitfalls / 常見陷阱

- Repeated insertions at the front are expensive (`O(n)`).
  / 反覆在前端插入會很慢。
- Sorting changes element order; keep a copy if original order matters.
  / 排序會改變順序，必要時先備份。

## Related Problems / 相關題目

- [q66](../leetcode/q66.md)
- [q3075](../leetcode/q3075.md)
- [q3453](../leetcode/q3453.md)