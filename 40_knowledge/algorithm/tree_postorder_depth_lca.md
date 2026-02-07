---
title: Tree Postorder Depth + LCA Merge / 後序深度合併找最深節點 LCA
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
canonical: algorithm/tree_postorder_depth_lca.md
---
# Tree Postorder Depth + LCA Merge / 後序深度合併找最深節點 LCA

Goal: find the smallest subtree that contains all deepest nodes by merging depths bottom-up.
目標：用後序合併深度，自底向上找出包含所有最深節點的最小子樹。

## When to use / 使用時機

- Need the LCA of all deepest nodes in a tree.
  / 需要找出所有最深節點的 LCA。
- Need to return the subtree root that contains all nodes at maximum depth.
  / 需要回傳包含所有最大深度節點的子樹根。

## Key idea / 核心想法

Each node returns two pieces of information:
每個節點回傳兩個資訊：

- `depth`: the maximum depth within its subtree (measured from this node).
  / `depth`：子樹內的最大深度（以當前節點為起點）。
- `ans`: the smallest subtree root that contains all deepest nodes in its subtree.
  / `ans`：包含該子樹所有最深節點的最小子樹根。

Merge rule:
合併規則：

- If left depth == right depth, current node is the LCA of deepest nodes.
  / 若左右深度相同，當前節點即為最深節點的 LCA。
- If one side is deeper, carry the deeper side's `ans` upward.
  / 若一側較深，答案沿較深一側往上帶。

## Pattern / 流程

1. Postorder DFS.
   / 後序 DFS。
2. Null node returns `(0, None)`.
   / 空節點回傳 `(0, None)`。
3. Compare left/right depths and select the answer node.
   / 比較左右深度並選擇答案節點。
4. Return `(max_depth + 1, ans)`.
   / 回傳 `(max_depth + 1, ans)`。

## Pseudocode / 偽碼

```text
function dfs(node):
    if node == null:
        return (0, null)

    (ld, lnode) = dfs(node.left)
    (rd, rnode) = dfs(node.right)

    if ld == rd:
        return (ld + 1, node)
    if ld > rd:
        return (ld + 1, lnode)
    return (rd + 1, rnode)

answer = dfs(root).node
```

## Example / 範例

Tree:

```
    1
   / \
  2   3
     / \
    4   5
```

- Deepest nodes are 4 and 5 (depth 3).
  / 最深節點為 4、5（深度 3）。
- DFS returns LCA = 3.
  / DFS 回傳 LCA = 3。

## Rust snippet / Rust 範例

```rust
use std::rc::Rc;
use std::cell::RefCell;

fn dfs(node: Option<Rc<RefCell<TreeNode>>>) -> (i32, Option<Rc<RefCell<TreeNode>>>) {
    if node.is_none() {
        return (0, None);
    }
    let rc = node.unwrap();
    let (left, right) = {
        let n = rc.borrow();
        (n.left.clone(), n.right.clone())
    };
    let (ld, lnode) = dfs(left);
    let (rd, rnode) = dfs(right);

    if ld == rd {
        (ld + 1, Some(rc))
    } else if ld > rd {
        (ld + 1, lnode)
    } else {
        (rd + 1, rnode)
    }
}
```

## Complexity / 複雜度

- Time: `O(n)`.
  / 時間：`O(n)`。
- Space: `O(h)` recursion stack, `h` is tree height.
  / 空間：`O(h)` 遞迴堆疊，`h` 為樹高。

## Pitfalls / 常見陷阱

- Depth definition must be consistent (node count vs. edge count).
  / 深度定義需一致（節點數或邊數）。
- Skewed trees can cause deep recursion.
  / 樹偏斜可能導致遞迴過深。
- With `Rc<RefCell<TreeNode>>`, clone children before recursion to avoid borrow conflicts.
  / 使用 `Rc<RefCell<TreeNode>>` 時，先 clone 子節點避免借用衝突。

## Related problems / 相關題目

- [q865](../leetcode/q865.md)