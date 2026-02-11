---
title: HashMap + VecDeque Occurrence Queue / HashMap + VecDeque 出現位置佇列
note_type: knowledge
domain: data_structure
tags: [knowledge, data_structure]
created: 2026-02-11
updated: 2026-02-11
status: active
source: knowledge
complexity_time: O(1) average per operation
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-25
---
# HashMap + VecDeque Occurrence Queue / HashMap + VecDeque 出現位置佇列

## Purpose / 目的

Track each value's future occurrence positions so that after removing a left boundary element, we can immediately know its next occurrence.
追蹤每個值後續出現的位置，讓左邊界移動時可立即得到該值下一次出現位置。

## Core Idea / 核心概念

Use:

- `HashMap<Value, VecDeque<Index>>`

For each value `x`, the deque stores all occurrence indices in increasing order.

During left-boundary sweep:

1. pop current index from front
2. new front (if exists) is next occurrence
3. if empty, treat next occurrence as sentinel (`n + 1` or `n + 2`)

This supports constant-time transition from "current occurrence" to "next occurrence".

## Operations / 操作

- Build:
  - scan array once, `push_back(index)` into value queue
- Advance left boundary at value `x`:
  - `queue.pop_front()`
  - `next = queue.front().copied()`

## When to Use / 使用時機

- Sliding left boundary algorithms need each value's next position.
- Need ordered occurrence access, mostly from the front.
- Total operations should be linear over all occurrences.

## Worked Example / 實作範例

`nums = [3, 2, 2, 5, 4]` (1-based index)

- map after preprocessing:
  - `3 -> [1]`
  - `2 -> [2, 3]`
  - `5 -> [4]`
  - `4 -> [5]`

Move left from `1` to `2`:

- value is `3`
- pop front of `3`: queue becomes `[]`
- next occurrence does not exist, use sentinel

Move left from `2` to `3`:

- value is `2`
- pop front of `2`: queue becomes `[3]`
- next occurrence is `3`

## Variations / 變化型

- Use `Vec<Vec<usize>> + pointer` when value range is compact and fixed.
- Store zero-based indices if all consumers use zero-based indexing.
- Use `BTreeMap` when ordered key iteration is also required.

## Complexity / 複雜度

- Time: `O(1)` average per pop/front lookup, `O(n)` total preprocessing
- Space: `O(n)`

## Pitfalls / 常見陷阱

- Forgetting to pop current index first leads to wrong "next occurrence".
- Mixing 0-based and 1-based indexing in interval formulas.
- Using a wrong sentinel can break range calculations (`next - 1`).
- Assuming map entry always exists without guarding edge cases.

## Implementation Notes / 實作細節

- Rust common pattern:
  - `map.entry(x).or_insert_with(VecDeque::new).push_back(pos);`
  - on advance: `q.pop_front(); let next = q.front().copied();`
- This structure is ideal when each index is consumed exactly once in left-to-right order.
- Often paired with segment tree / Fenwick / difference-array updates driven by next occurrence.

## Related Problems / 相關題目

- [q3721](../leetcode/q3721.md)
