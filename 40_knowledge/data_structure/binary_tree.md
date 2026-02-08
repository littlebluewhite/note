---
title: Binary Tree / 二元樹
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: data_structure
complexity_time: O(n) traversal
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
---
# Binary Tree / 二元樹

Goal: represent hierarchical data where each node has at most two children.
目標：表示階層式結構，每個節點最多有兩個子節點。

## Terminology / 術語

- Root: the top node with no parent. / 根節點：最上層、沒有父節點。
- Parent / Child: direct connection between nodes. / 父節點／子節點：直接相連關係。
- Leaf: node with no children. / 葉節點：沒有子節點的節點。
- Depth: distance from root (edges). / 深度：與根節點的邊數距離。
- Level: 1-based depth (root is level 1). / 層級：從 1 開始計算深度（根為第 1 層）。
- Height: maximum depth in the tree. / 高度：樹的最大深度。

## Structure / 結構

- Each node stores a value and two optional children (`left`, `right`).
  / 每個節點包含值與兩個可選子節點。
- Common representations:
  / 常見表示法：
  - Pointer-based nodes (general binary tree).
    / 指標節點（一般二元樹）。
  - Array-based indexing for complete trees (heaps).
    / 完全二元樹可用陣列索引（堆）。

## Traversals / 走訪方式

- Preorder: `root -> left -> right`.
  / 前序：根 -> 左 -> 右。
- Inorder: `left -> root -> right`.
  / 中序：左 -> 根 -> 右。
- Postorder: `left -> right -> root`.
  / 後序：左 -> 右 -> 根。
- Level-order (BFS): by levels from top to bottom.
  / 層序：從上到下逐層。

## Worked example / 範例

Tree:

```
    1
   / \
  2   3
 / \
4  5
```

Traversal outputs:

- Preorder: `1 2 4 5 3`
  / 前序：`1 2 4 5 3`
- Inorder: `4 2 5 1 3`
  / 中序：`4 2 5 1 3`
- Postorder: `4 5 2 3 1`
  / 後序：`4 5 2 3 1`
- Level-order: `1 2 3 4 5`
  / 層序：`1 2 3 4 5`

## Rust representation / Rust 表示法

LeetCode style (shared ownership with interior mutability):

```rust
use std::rc::Rc;
use std::cell::RefCell;

#[derive(Debug, PartialEq, Eq)]
pub struct TreeNode {
    pub val: i32,
    pub left: Option<Rc<RefCell<TreeNode>>>,
    pub right: Option<Rc<RefCell<TreeNode>>>,
}

impl TreeNode {
    #[inline]
    pub fn new(val: i32) -> Self {
        TreeNode { val, left: None, right: None }
    }
}
```

Pointer-based owned tree (no sharing):

```rust
#[derive(Debug)]
pub struct Node {
    pub val: i32,
    pub left: Option<Box<Node>>,
    pub right: Option<Box<Node>>,
}
```

## Operations & Complexity / 操作與複雜度

- Time: `O(n) traversal`
- Space: `O(n)`

Where:
`n`: number of nodes.


- Full traversal: `O(n)` time.
  / 全遍歷時間：`O(n)`。
- DFS stack space: `O(h)` where `h` is height.
  / DFS 堆疊空間：`O(h)`，`h` 為高度。
- BFS queue space: `O(w)` where `w` is maximum width.
  / BFS 佇列空間：`O(w)`，`w` 為最大寬度。

## Pitfalls / 常見陷阱

- Skewed trees can cause deep recursion; prefer iterative traversal if needed.
  / 極度偏斜的樹會造成遞迴太深，必要時改用迭代。
- Mixing 0-based depth and 1-based level definitions.
  / 容易混淆深度（0-based）與層級（1-based）。
- Forgetting to handle `None` children in traversal.
  / 走訪時忘記處理空子節點。

## Related problems / 相關題目

- [q110](../leetcode/q110.md)
- [q865](../leetcode/q865.md)
- [q1161](../leetcode/q1161.md)
- [q1339](../leetcode/q1339.md)
