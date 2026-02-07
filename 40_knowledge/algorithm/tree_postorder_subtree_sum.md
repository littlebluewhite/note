---
title: Tree Postorder Subtree Sum / 後序子樹總和
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(n)
complexity_space: O(h)
review_interval_days: 14
next_review: 2026-02-17
canonical: algorithm/tree_postorder_subtree_sum.md
---
# Tree Postorder Subtree Sum / 後序子樹總和

Goal: compute each subtree sum with a postorder DFS.
目標：用後序 DFS 計算每個節點的子樹總和。

## When to use / 使用時機

- Need subtree sums to evaluate a global objective (e.g., split a tree).
  / 需要子樹總和來計算全域目標（例如切樹）。
- Aggregate values from children to parent.
  / 子節點資訊要往上合併。

## Pattern / 流程

1. Postorder DFS (left, right, root).
   / 後序 DFS（左、右、根）。
2. For each node: `sum = left_sum + right_sum + val`.
   / 每個節點計算 `sum = left_sum + right_sum + val`。
3. Optionally update a global metric with `sum`.
   / 可用 `sum` 更新全域答案。

## Worked Example / 實作範例

Tree:

```
    1
   / \
  2   3
```

Subtree sums:

- Node 2 -> 2
  / 節點 2 -> 2
- Node 3 -> 3
  / 節點 3 -> 3
- Node 1 -> 1 + 2 + 3 = 6
  / 節點 1 -> 1 + 2 + 3 = 6

If total sum is 6 and you cut at a subtree:
若總和為 6，切在某個子樹時：

- Cut at node 2: `2 * (6 - 2) = 8`
  / 切在節點 2：`2 * (6 - 2) = 8`
- Cut at node 3: `3 * (6 - 3) = 9`
  / 切在節點 3：`3 * (6 - 3) = 9`

## Rust snippet / Rust 範例

LeetCode style binary tree:

```rust
use std::rc::Rc;
use std::cell::RefCell;

fn subtree_sum(node: &Option<Rc<RefCell<TreeNode>>>) -> i64 {
    if let Some(rc) = node {
        let (left, right, val) = {
            let n = rc.borrow();
            (n.left.clone(), n.right.clone(), n.val as i64)
        };
        val + subtree_sum(&left) + subtree_sum(&right)
    } else {
        0
    }
}
```

## Complexity / 複雜度

- Time: `O(n)`
  / 時間：`O(n)`
- Space: `O(h)` recursion stack, `h` is tree height
  / 空間：`O(h)` 遞迴堆疊，`h` 為樹高

## Pitfalls / 常見陷阱

- Skewed trees can cause deep recursion; consider iterative DFS if needed.
  / 樹過度偏斜會造成遞迴過深，必要時改用迭代 DFS。
- Product may overflow 64-bit; use `i128` for intermediate products.
  / 乘積可能超過 64-bit，改用 `i128` 中間值。
- With `Rc<RefCell<TreeNode>>`, clone child `Rc` before recursion to avoid borrow conflicts.
  / 使用 `Rc<RefCell<TreeNode>>` 時，先 clone 子節點避免借用衝突。

## Related problems / 相關題目

- [q1339](../leetcode/q1339.md)