---
title: Earliest Index State Hash Map / 最早索引狀態雜湊表
note_type: knowledge
domain: data_structure
tags: [knowledge, data_structure]
created: 2026-02-13
updated: 2026-02-13
status: active
source: knowledge
complexity_time: O(1) avg per operation
complexity_space: O(m)
review_interval_days: 14
next_review: 2026-02-27
---
# Earliest Index State Hash Map / 最早索引狀態雜湊表

## Purpose / 目的

Store the first index where each prefix-state signature appears, so repeated signatures immediately yield maximum candidate interval lengths.
儲存每個前綴狀態 signature 首次出現的位置，讓同狀態再次出現時可立刻算出候選最長區間。

## Core Idea / 核心概念

- Key: state signature (e.g., tuple of prefix differences).
  / 鍵：狀態 signature（例如前綴差分 tuple）。
- Value: earliest index where this key was seen.
  / 值：該狀態最早出現索引。
- On each index `i`:
  - if key exists at `j`, interval length candidate is `i - j`;
  - if key not exists, insert `(key, i)`.

## Operations / 操作

- Initialize with empty-prefix state: `map[init_state] = 0`.
  / 先放入空前綴狀態。
- Query existing earliest index:
  - Rust: `if let Some(&j) = map.get(&key) { ... }`
- Insert only once (first occurrence):
  - Rust: `map.entry(key).or_insert(i)`
- Do not overwrite existing value.
  / 不可覆蓋已存在的最早索引。

## When to Use / 使用時機

- Need longest subarray/substring where validity is determined by equal prefix-state signatures.
  / 合法性可轉為前綴狀態相等，且目標是最長區間。
- State domain is large/sparse, not suitable for direct array indexing.
  / 狀態空間稀疏，難以用陣列直接索引。

## Worked Example / 實作範例

Given prefix states sequence:

`[S0, S1, S2, S1, S3, S2]` at indices `[0,1,2,3,4,5]`

Process:

- `S0` first seen at 0.
- `S1` first seen at 1.
- `S2` first seen at 2.
- index 3 sees `S1` again -> length `3 - 1 = 2`.
- index 5 sees `S2` again -> length `5 - 2 = 3` (better).

Earliest-index policy guarantees maximal distance for each repeated state.

## Variations / 變化型

- Single map for one constraint family.
- Multiple maps in parallel for multiple state transforms.
- Key as tuple/struct/packed integer depending on dimension and value range.

## Complexity / 複雜度
- Time: `O(1)` average per `get/insert`, overall `O(n)` for one-pass scan
- Space: `O(m)` where `m` is number of distinct states

## Pitfalls / 常見陷阱

- Missing empty-prefix initialization.
  / 漏掉初始狀態。
- Updating existing key with later index.
  / 用較晚索引覆蓋最早索引。
- Inconsistent key construction across positions.
  / 不同位置 key 建構規則不一致。
- Assuming worst-case collision-free behavior in strict proofs.
  / 嚴格理論上雜湊有碰撞風險，實務通常接受平均複雜度。

## Implementation Notes / 實作細節

Rust snippet:

```rust
use std::collections::HashMap;

let mut first: HashMap<(i32, i32), usize> = HashMap::new();
first.insert((0, 0), 0); // empty prefix

for i in 1..=n {
    let key = build_key(i);
    if let Some(&j) = first.get(&key) {
        ans = ans.max((i - j) as i32);
    } else {
        first.insert(key, i);
    }
}
```

## Related Problems / 相關題目

- [q3714](../leetcode/q3714.md)
- [prefix_difference_state_matching](../algorithm/prefix_difference_state_matching.md)
- [hash_map_set](./hash_map_set.md)
