---
title: Tree Postorder Height Check (Sentinel Early Stop) / 後序高度檢查（哨兵值早停）
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-08
updated: 2026-02-08
status: active
source: algorithm
complexity_time: O(n)
complexity_space: O(h)
review_interval_days: 14
next_review: 2026-02-22
canonical: algorithm/tree_postorder_height_balance_check.md
---
# Tree Postorder Height Check (Sentinel Early Stop) / 後序高度檢查（哨兵值早停）

Goal: check tree constraints that depend on child heights (for example, balance) in one DFS pass.
目標：對「依賴左右子樹高度」的條件（例如平衡性）用一次 DFS 完成檢查。

## When to Use / 使用時機

- Need both subtree height and validity check.
  / 同時需要子樹高度與有效性判斷。
- Naive top-down solution recomputes heights repeatedly.
  / 直覺自頂向下會重複計算高度，造成 `O(n^2)`。
- Want early termination once any subtree fails.
  / 任一子樹失敗就想立刻停止。

## Core Idea / 核心概念

- Postorder DFS first solves children, then current node.
  / 後序 DFS 先解子節點，再解當前節點。
- Return a normal value for success (height), and a sentinel value for failure (`-1`).
  / 成功回傳正常值（高度），失敗回傳哨兵值（`-1`）。
- If left or right returns sentinel, bubble failure upward immediately.
  / 左右任一回傳哨兵值，立即向上層傳遞失敗。

## Steps / 步驟

1. Define `dfs(node)`:
   - return `0` if node is null.
   - return `-1` if this subtree is invalid.
   - otherwise return subtree height.
2. Recurse left and right.
3. If either side is `-1`, return `-1`.
4. Check local constraint:
   - for balance check: `abs(lh - rh) <= 1`.
5. If violated, return `-1`; else return `max(lh, rh) + 1`.
6. Final answer is `dfs(root) != -1`.

## Complexity / 複雜度

- Time: `O(n)` (each node visited once).
  / 時間：`O(n)`（每個節點一次）。
- Space: `O(h)` recursion stack.
  / 空間：`O(h)` 遞迴堆疊。

## Pitfalls / 常見陷阱

- Recomputing `height()` separately in every node check.
  / 每個節點都額外呼叫 `height()` 會重複走訪。
- Forgetting to short-circuit when sentinel appears.
  / 忘記在看到哨兵值時立刻早停。
- Mixing different height definitions (nodes vs edges).
  / 高度定義（節點數或邊數）前後不一致。

## Example / 範例

Tree:

```text
    1
   / \
  2   2
 / \
3   3
/ \
4   4
```

- Subtree rooted at the left `2` is already too deep.
  / 左子樹根 `2` 的高度差已超過 1。
- DFS returns `-1` from that subtree and propagates upward.
  / DFS 從該子樹回傳 `-1` 並一路上拋。
- Final result is unbalanced.
  / 最終判斷為不平衡。

## Rust Snippet / Rust 範例

```rust
use std::cell::RefCell;
use std::rc::Rc;

fn height_or_fail(node: Option<Rc<RefCell<TreeNode>>>) -> i32 {
    if node.is_none() {
        return 0;
    }
    let rc = node.unwrap();
    let (left, right) = {
        let n = rc.borrow();
        (n.left.clone(), n.right.clone())
    };

    let lh = height_or_fail(left);
    if lh == -1 {
        return -1;
    }
    let rh = height_or_fail(right);
    if rh == -1 {
        return -1;
    }

    if (lh - rh).abs() > 1 {
        -1
    } else {
        lh.max(rh) + 1
    }
}
```

## Notes / 補充

- This pattern generalizes to many tree checks where child results can be merged and failures can short-circuit.
  / 這個模式可泛化到許多可「合併子結果 + 失敗早停」的樹題。

## Related / 相關題目

- [q110](../leetcode/q110.md)
- [q865](../leetcode/q865.md)
