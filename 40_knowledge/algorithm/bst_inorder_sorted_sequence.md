---
title: BST Inorder Produces Sorted Sequence / BST 中序遍歷產生遞增序列
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-02-09
updated: 2026-02-09
status: active
source: algorithm
complexity_time: O(n)
complexity_space: O(h)
review_interval_days: 14
next_review: 2026-02-23
---
# BST Inorder Produces Sorted Sequence / BST 中序遍歷產生遞增序列

## Goal

Use inorder traversal on a Binary Search Tree (BST) to obtain a non-decreasing sequence of values.
在二元搜尋樹（BST）上使用中序遍歷，取得非遞減（遞增可含重複）序列。

## When to Use

- Need sorted values from a BST without extra sorting.
- 想從 BST 直接拿到排序後的值，避免額外排序成本。
- Need rank-based operations like k-th smallest, predecessor, successor.
- 需要做第 k 小、前驅、後繼等次序型操作。
- Need to rebuild or rebalance a BST from its node values.
- 需要先抽出節點值，再重建或平衡 BST。

## Core Idea

- BST property: `left < root < right` (or non-strict variants by problem definition).
- BST 性質：`左 < 根 < 右`（是否允許等號依題目定義）。
- Inorder order is `left -> root -> right`, so output follows key order.
- 中序順序是 `左 -> 根 -> 右`，輸出自然符合大小順序。

## Steps

1. Initialize an empty array `vals`.
2. 建立空陣列 `vals`。
3. DFS inorder:
4. 以 DFS 做中序遍歷：
5. Traverse left subtree.
6. 先走左子樹。
7. Append current node value to `vals`.
8. 把當前節點值加入 `vals`。
9. Traverse right subtree.
10. 再走右子樹。
11. Return `vals`.
12. 回傳 `vals`。

## Complexity

- Time: `O(n)` (visit each node once)
- Space: `O(h)` recursion stack, plus `O(n)` output array if collected

## Pitfalls

- Applying this to a non-BST tree does not guarantee sorted order.
- 非 BST 上做中序遍歷不會保證排序。
- Deep skewed BST may hit recursion depth limits.
- 極端偏斜 BST 可能造成遞迴過深，可改迭代堆疊版。
- Duplicate handling must match BST definition used by the problem.
- 若存在重複值，要先確認題目對 BST 的重複值規則。

## Examples

BST:

```text
    4
   / \
  2   6
 / \ / \
1  3 5  7
```

Inorder output: `[1, 2, 3, 4, 5, 6, 7]`
中序輸出：`[1, 2, 3, 4, 5, 6, 7]`

## Notes

- This is often the first half of a two-stage pattern:
- 常和「兩階段流程」一起出現：
- Stage A: inorder to get sorted values.
- 階段 A：中序取出排序序列。
- Stage B: build a balanced BST from sorted values.
- 階段 B：由排序序列建平衡 BST。

## Related

- [q94](../leetcode/q94.md)
- [q98](../leetcode/q98.md)
- [q230](../leetcode/q230.md)
- [q1382](../leetcode/q1382.md)
