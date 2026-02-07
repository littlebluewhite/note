---
title: Lazy Deletion in Priority Queue / 優先佇列延遲刪除
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(k log n)
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
canonical: algorithm/lazy_deletion_priority_queue.md
---
# Lazy Deletion in Priority Queue / 優先佇列延遲刪除

Goal: keep a heap of candidates when deletions are frequent but direct removal is expensive.
目標：當候選項頻繁失效且無法在堆內快速刪除時，用延遲刪除維持正確性。

## Core idea / 核心概念

Push everything into the heap; validate only when popping.
所有候選都先推入堆，真正取出時才做有效性檢查。

- If a popped item is stale, discard and pop again.
  / 若資料已失效，直接丟棄再彈下一個。
- This avoids `O(n)` deletions inside a binary heap.
  / 避免在二元堆內做 `O(n)` 的刪除。

## Staleness checks / 失效判定

Common ways to detect stale items:
常見失效判定方法：

- **Removed flag**: a node was deleted/merged. / 用 `removed` 標記節點已被刪除或合併。
- **Adjacency check**: `next[u] == v` for a pair. / 用相鄰關係判斷是否仍為鄰居。
- **Value/version match**: stored key equals current recomputed key.
  / 比對紀錄的 key 與目前值是否一致。

## Steps / 步驟

1. Initialize the heap with all candidates, store auxiliary arrays for validity checks.
2. Loop: pop the top; if stale, continue.
3. Use the valid item, apply the update, and push new candidates that arise.
4. Mark removed or updated nodes so future pops can detect staleness.

## Example / 範例

Minimum adjacent pair merge:
最小相鄰對合併：

- Heap stores `(sum, left_index)`.
  / 堆存 `(sum, left_index)`。
- After merging `(u, v)`, old pairs `(prev, u)` and `(v, next)` become stale.
  / 合併 `(u, v)` 後，舊的 `(prev, u)`、`(v, next)` 都變成失效資料。
- We do **not** delete them from heap; we skip them when popped.
  / 不從堆中刪除，只在彈出時略過。

## Complexity / 複雜度

- Time: `O(k log n)`
- Space: `O(n)`

Where:
`k`: number of heap pushes (candidates).
`n`: active elements in the heap.

- Each candidate is pushed once per creation and popped at most once.
  / 每個候選只會被建立一次、彈出最多一次。
- Total time `O(k log n)` where `k` is the number of pushes.
  / 總時間 `O(k log n)`。

## Pitfalls / 注意事項

- Staleness checks must cover **all** invalid conditions (removed, non-adjacent, changed key).
  / 失效檢查要涵蓋「被移除、非相鄰、key 改變」等情況。
- Tie-breaking must be encoded in the heap key if the problem requires leftmost/rightmost.
  / 若題目要求最左/最右，需在 key 中加入索引作 tie-break。

## Related problems / 相關題目

- [3507. Minimum Pair Removal to Sort Array I](https://leetcode.com/problems/minimum-pair-removal-to-sort-array-i/)
- [3510. Minimum Pair Removal to Sort Array II](https://leetcode.com/problems/minimum-pair-removal-to-sort-array-ii/)
