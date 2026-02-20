---
title: String Block Vector (Vec<String>) / 字串區塊向量
note_type: knowledge
domain: data_structure
tags: [knowledge, data_structure]
created: 2026-02-20
updated: 2026-02-20
status: active
source: knowledge
complexity_time: O(k log k + L)
complexity_space: O(k + L)
review_interval_days: 14
next_review: 2026-03-06
---
# String Block Vector (Vec<String>) / 字串區塊向量

## Purpose / 目的

Store multiple independently-constructed string blocks, then reorder and merge them efficiently.
儲存多個可獨立建構的字串區塊，最後再做重排與合併。

## Core Idea / 核心概念

- Use `Vec<String>` as a block container.
  / 以 `Vec<String>` 當區塊容器。
- Each block is built once (often with `String::with_capacity`).
  / 每個區塊只建構一次（常搭配 `String::with_capacity`）。
- Apply global ordering (`sort_unstable_by`) on block-level, then `concat`.
  / 先做區塊層級排序，再一次 `concat` 合併。

This avoids repeated front-insertions or costly incremental full-string rebuilds.
可避免大量前插與反覆整體字串重建的成本。

## Operations / 操作

- `blocks.push(block)`: amortized `O(1)`
- `blocks.sort_unstable_by(...)`: `O(k log k)`
- `blocks.concat()`: `O(L)`

Where:
`k`: number of blocks.
`L`: total output length.

## When to Use / 使用時機

- Output is naturally composed of many variable-length segments.
  / 輸出天然由多段可變長片段組成。
- You need to sort or reorder segments before final output.
  / 最終輸出前需要重排或排序片段。
- Recursive decomposition produces sibling blocks per level.
  / 遞迴分解後，每層會產生多個同層兄弟區塊。

## Worked Example / 實作範例

Problem pattern: LeetCode 761.
題型：LeetCode 761。

- Collect optimized top-level special blocks:
  - `"10"`, `"1100"`
- Sort descending:
  - `"1100"`, `"10"`
- Concat:
  - `"110010"`

Rust snippet:

```rust
let mut blocks: Vec<String> = vec!["10".to_string(), "1100".to_string()];
blocks.sort_unstable_by(|a, b| b.cmp(a));
let merged = blocks.concat();
assert_eq!(merged, "110010");
```

## Variations / 變化型

- `Vec<&str>` then one final allocation: lower allocation count when source slices live long enough.
  / 用 `Vec<&str>` 暫存切片，最後一次配置（需注意生命週期）。
- `Vec<Vec<u8>>` for byte-level operations and ASCII-only input.
  / 以 `Vec<Vec<u8>>` 進行位元組層操作（適合 ASCII）。
- `BinaryHeap<String>` when only top few blocks are needed online.
  / 若是線上取最大前幾項，可改用堆。

## Complexity / 複雜度

- Time: `O(k log k + L)`
- Space: `O(k + L)`

## Pitfalls / 常見陷阱

- Sorting references to mutable strings then mutating afterward can invalidate assumptions.
  / 排序後若又修改字串內容，可能破壞排序假設。
- Excessive cloning of large blocks increases constants.
  / 大區塊過度 clone 會放大常數成本。
- Forgetting pre-allocation when block size is predictable.
  / 可預估長度卻未預先配置容量。

## Implementation Notes / 實作細節

- Prefer `sort_unstable_by(|a, b| b.cmp(a))` for descending lexical order.
  / 降序字典序可直接使用 `sort_unstable_by(|a, b| b.cmp(a))`。
- For known wrapper length (e.g., add outer `1` and `0`), use `String::with_capacity(inner_len + 2)`.
  / 若外層固定包裝長度可預知，先 `with_capacity`。
- `concat` is usually cleaner than repeated `push_str` into an unknown-size accumulator.
  / 多塊合併時，`concat` 通常比手寫反覆 `push_str` 更簡潔。

## Related Problems / 相關題目

- [q761](../leetcode/q761.md)
- [q756](../leetcode/q756.md)
