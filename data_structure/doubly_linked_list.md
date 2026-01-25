# Doubly Linked List / 雙向鏈結串列

Goal: support `O(1)` removal and neighbor queries in a sequence.
目標：在序列中提供 `O(1)` 刪除與前後鄰居查詢。

## Core idea / 核心概念

Each node keeps `prev` and `next` pointers.
每個節點保存 `prev` 與 `next` 指標。

- Remove a node by linking its neighbors together.
  / 刪除節點時，把前後節點接起來。
- Access neighbors in `O(1)`.
  / 前後鄰居查詢 `O(1)`。

## Array-based representation / 陣列化實作

When nodes are fixed indices, store pointers in arrays:
當節點索引固定時，可用陣列存指標：

```
prev[i] = index of previous node (or -1)
next[i] = index of next node (or -1)
removed[i] = whether i is deleted
```

This keeps merges/removals fast without allocations.
這樣可快速合併/刪除且避免動態配置。

## Operations / 操作

- **Remove i**: `next[prev[i]] = next[i]`, `prev[next[i]] = prev[i]`.
  / 移除 i：更新前後節點的連結。
- **Merge (u, v)**: keep `u`, delete `v`, and rewire `u` to `next[v]`.
  / 合併 (u, v)：保留 u、刪除 v、接上 `next[v]`。

## Example / 範例

Sequence `0 <-> 1 <-> 2`:
序列 `0 <-> 1 <-> 2`：

- Remove `1` -> `0 <-> 2`
  / 刪除 `1` 後變成 `0 <-> 2`。

## Complexity / 複雜度

- Remove / merge: `O(1)`.
  / 刪除或合併：`O(1)`。
- Space: `O(n)` for `prev/next` arrays.
  / 空間：`O(n)`。

## Related problems / 相關題目

- [3507. Minimum Pair Removal to Sort Array I](https://leetcode.com/problems/minimum-pair-removal-to-sort-array-i/)
- [3510. Minimum Pair Removal to Sort Array II](https://leetcode.com/problems/minimum-pair-removal-to-sort-array-ii/)
