---
title: Binary Search Tree (BST) / 二元搜尋樹
note_type: knowledge
domain: data_structure
tags: [knowledge, data_structure]
created: 2026-02-09
updated: 2026-02-09
status: active
source: data_structure
complexity_time: O(h) operations
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-23
---
# Binary Search Tree (BST) / 二元搜尋樹

## Purpose / 目的

Store ordered keys in a binary tree to support search, insertion, deletion, and order queries.
以二元樹保存有序鍵值，支援查詢、插入、刪除與順序相關操作。

## Core Idea / 核心概念

- For each node: all keys in left subtree are smaller, and all keys in right subtree are larger.
  / 對每個節點而言：左子樹鍵值都較小，右子樹鍵值都較大。
- This property allows directional decisions at every step, similar to binary search on a tree.
  / 這個性質讓每一步都能像二分搜尋一樣決定往左或往右。
- Inorder traversal of a BST yields sorted keys.
  / BST 的中序遍歷會得到排序序列。

## Operations / 操作

- Search key: `O(h)`.
  / 查找鍵值：`O(h)`。
- Insert key: `O(h)`.
  / 插入鍵值：`O(h)`。
- Delete key: `O(h)` (handle 0/1/2-child cases).
  / 刪除鍵值：`O(h)`（需處理 0/1/2 子節點情況）。
- Find min/max: `O(h)` by walking to leftmost/rightmost.
  / 取最小/最大值：`O(h)`，走到最左/最右節點。
- Inorder traversal: `O(n)`.
  / 中序遍歷：`O(n)`。

## When to Use / 使用時機

- Need dynamic ordered set/map behavior.
  / 需要動態維護有序集合或映射。
- Need range queries or predecessor/successor operations.
  / 需要區間查詢、前驅/後繼查詢。
- Data arrives incrementally and order matters.
  / 資料逐步進來且順序性很重要。

## Worked Example / 實作範例

Insert keys in order: `4, 2, 6, 1, 3, 5, 7`
依序插入：`4, 2, 6, 1, 3, 5, 7`

Resulting BST:

```text
    4
   / \
  2   6
 / \ / \
1  3 5  7
```

Search `5`:

- `5 > 4` -> go right
- `5 < 6` -> go left
- hit node `5`

## Variations / 變化型

- Self-balancing BSTs: AVL tree, Red-Black tree, Treap.
  / 自平衡 BST：AVL、紅黑樹、Treap。
- Ordered map/set implementations in many languages are balanced BST variants.
  / 多數語言的有序 map/set 底層常是平衡 BST 變體。
- BST with duplicates: store count or define one-sided duplicate rule.
  / 含重複值時可加計數，或固定重複值放單側。

## Complexity / 複雜度

- Time: `O(h) operations`
- Space: `O(n)`

Where:
`n`: number of nodes.
`h`: tree height.

- Balanced BST: `h = O(log n)`, so operations are `O(log n)`.
  / 平衡 BST 時操作可達 `O(log n)`。
- Worst case (skewed): `h = O(n)`, operations degrade to `O(n)`.
  / 最壞情況（偏斜）會退化成 `O(n)`。

## Pitfalls / 常見陷阱

- Confusing BST with generic binary tree.
  / 把一般二元樹誤當 BST 使用。
- Forgetting deletion details when node has two children.
  / 刪除兩子節點情況時忘記用前驅/後繼替換。
- Ignoring balancing can cause severe performance degradation.
  / 不做平衡控制會導致效能大幅退化。

## Implementation Notes / 實作細節

- In Rust LeetCode, tree nodes are usually `Option<Rc<RefCell<TreeNode>>>`.
  / Rust LeetCode 常用 `Option<Rc<RefCell<TreeNode>>>` 表示節點。
- For interview clarity, explicitly state duplicate policy and balancing assumption.
  / 面試時要明講重複值規則與是否假設平衡。

## Related Problems / 相關題目

- [q98](../leetcode/q98.md)
- [q108](../leetcode/q108.md)
- [q230](../leetcode/q230.md)
- [q1382](../leetcode/q1382.md)
