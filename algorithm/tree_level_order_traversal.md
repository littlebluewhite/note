# Tree Level-Order Traversal (BFS) / 樹的層序遍歷（BFS）

Goal: traverse a tree level by level to compute per-level aggregates like sums, counts, or maxima.
目標：逐層遍歷樹，用於計算每一層的總和、數量或最大值等彙總資訊。

## Core idea / 核心概念

- Use a queue and process nodes in layers.
  / 使用佇列，按層次處理節點。
- Snapshot the queue length to lock the current level.
  / 先固定佇列長度，鎖定當層範圍。
- After processing a level, update answer and move to the next level.
  / 當層處理完後更新答案，進入下一層。

## When to use / 何時使用

- Need the sum/avg/max of each level.
  / 需要每層的總和、平均或最大值。
- Find the smallest level that satisfies a condition.
  / 找出滿足條件的最小層級。
- Compute tree height or maximum width.
  / 計算樹高或最大寬度。

## Pattern / 流程

1. If root is empty, return.
   / 若 root 為空，直接回傳。
2. Push root into a queue, set `level = 1`.
   / root 入隊，設定 `level = 1`。
3. While queue not empty:
   / 佇列不空時重複：
   - `size = queue.len()` to lock current level.
     / 用 `size = queue.len()` 固定當層節點數。
   - Loop `size` times: pop node, add to sum, push children.
     / 連續 `size` 次出隊，累加值並加入子節點。
   - Update answer for this level; `level += 1`.
     / 更新本層答案後，`level += 1`。

## Rust snippet / Rust 範例

```rust
use std::collections::VecDeque;
use std::rc::Rc;
use std::cell::RefCell;

fn level_sums(root: Option<Rc<RefCell<TreeNode>>>) -> Vec<i64> {
    let mut sums = Vec::new();
    if root.is_none() {
        return sums;
    }

    let mut q: VecDeque<Rc<RefCell<TreeNode>>> = VecDeque::new();
    q.push_back(root.unwrap());

    while !q.is_empty() {
        let size = q.len();
        let mut sum: i64 = 0;
        for _ in 0..size {
            let node_rc = q.pop_front().unwrap();
            let (val, left, right) = {
                let node = node_rc.borrow();
                (node.val, node.left.clone(), node.right.clone())
            };
            sum += val as i64;
            if let Some(left) = left {
                q.push_back(left);
            }
            if let Some(right) = right {
                q.push_back(right);
            }
        }
        sums.push(sum);
    }

    sums
}
```

## Pitfalls / 常見陷阱

- Forgetting to snapshot `queue.len()` -> mixes multiple levels.
  / 沒固定當層長度會混到下一層。
- Updating result on `>=` when the smallest level is required.
  / 需要最小層級時，不能用 `>=` 更新。
- Using `i32` for sums when values can accumulate large totals.
  / 總和可能放不下 `i32`，需用 `i64`。

## Complexity / 複雜度

- Time: `O(n)` where `n` is number of nodes.
  / 時間：`O(n)`，`n` 為節點數。
- Space: `O(w)` where `w` is maximum width.
  / 空間：`O(w)`，`w` 為最大寬度。

## Related problems / 相關題目

- [q1161](../leetcode/q1161.md)