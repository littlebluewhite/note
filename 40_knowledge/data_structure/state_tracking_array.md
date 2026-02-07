---
title: State Tracking Array / 狀態追蹤陣列
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: data_structure
complexity_time: O(1) per update
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
canonical: data_structure/state_tracking_array.md
---
# State Tracking Array / 狀態追蹤陣列

Goal: maintain a lightweight per-item status while scanning data left-to-right or over time.
目標：以低成本追蹤每個項目的狀態，支援線性掃描或時間序列處理。

## Core structure / 核心結構

- A fixed-length array `state[i]` (often `bool`) that marks whether item `i` is resolved, active, or valid.
  / 以固定長度陣列記錄每個項目的狀態（常用 `bool`）。
- Access and update in `O(1)` per item.
  / 每個項目 `O(1)` 更新與查詢。

## Typical operations / 常見操作

- Check only unresolved items: `if !state[i] { ... }`.
  / 只處理未解決項目。
- Mark resolved when a decisive condition is met.
  / 條件成立時標記完成。
- Never revert if the property is monotonic.
  / 若狀態具單調性，標記後不回退。

## Use cases / 使用時機

- Adjacent pair ordering in lexicographic scans.
  / 字典序掃描中追蹤相鄰列順序是否已確定。
- Streaming validation where decisions become final.
  / 串流驗證、決策一旦確定就不再改變的情境。
- Incremental algorithms with "resolved vs unresolved" sets.
  / 增量式演算法需要區分已解與未解集合。

## Example / 範例

- `state[i] = true` means rows `i` and `i+1` are already strictly ordered, so later columns can skip this pair.
  / `state[i] = true` 代表相鄰列已嚴格排序，之後欄位可略過該對。

## Complexity / 複雜度

- Time: `O(1) per update`
- Space: `O(n)`

Where:
`n`: number of items.


- Time per update: `O(1)`; total `O(k)` for `k` updates.
  / 每次更新 `O(1)`。
  / 空間：`O(n)`。

## Pitfalls / 常見陷阱

- Do not mark resolved on equality if strict order is required.
  / 若需嚴格順序，相等時不可標記完成。
- Make sure the index meaning stays consistent.
  / 注意索引語意一致（例如 `i` 對應 `i` 與 `i+1`）。

## Related problems / 相關題目

- [q955](../leetcode/q955.md)