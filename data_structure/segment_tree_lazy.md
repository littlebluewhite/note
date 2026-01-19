# Segment Tree (Range Add + Covered Length) / 線段樹（區間加 + 覆蓋長度）

Goal: support range add/remove on intervals and query the union length of covered ranges.
目標：支援區間加/減，並查詢覆蓋區間的聯集長度。

## Core Idea / 核心概念

Each node stores:
- `count`: how many active intervals fully cover this node.
- `len`: total covered length in this node.
每個節點維護「覆蓋次數 count」與「覆蓋長度 len」。

Update rule:
- If `count > 0`, the whole node is covered, so `len = xs[r] - xs[l]`.
- Else if leaf, `len = 0`.
- Else, `len = len(left) + len(right)`.
更新規則：若 `count > 0` 代表整段被覆蓋；否則由子節點加總。

Why `count` matters:
- Removing one interval does not necessarily uncover the segment if others still cover it.
- `count > 0` means "covered by at least one interval", so we can skip looking at children.
為什麼需要 `count`：移除一個區間後，可能仍被其他區間覆蓋；只要 `count > 0` 就是完全覆蓋。

## Comparison / 比較

- Typical lazy tree pushes numeric tags to children and aggregates sums/min/max.
- This coverage tree treats `count` as a lazy tag, but the answer is `len`, not `count`.
- Merge rule is conditional: `count > 0` overrides children, otherwise sum children.
和一般 lazy / RMQ 線段樹相比：傳統樹只合併子節點；覆蓋樹先看 `count`，
`count > 0` 直接覆蓋整段，`count == 0` 才合併子節點。

## Correctness / 正確性

Why this is correct (short proof idea):
- Any point in a segment is covered iff its path has some node with `count > 0`.
- If a node has `count > 0`, its entire interval is covered, so `len = interval length`.
- If `count == 0`, coverage depends on children; summing `len(left)+len(right)` is exact.
正確性要點：任一點若沿路遇到 `count > 0` 則被覆蓋；節點 `count > 0` 代表整段覆蓋，
`count == 0` 時需由子節點合併，因此 `len` 的遞迴定義正確。
記憶口訣：`count > 0 -> 全覆蓋；count = 0 -> 看孩子`。

## Update Steps / 更新步驟

How update works (range add):
1. If update range does not intersect, return.
2. If fully covered, add `delta` to `count`.
3. Otherwise, recurse to children.
4. Recompute `len` using the update rule.
更新流程：不相交跳過；完全涵蓋就改 `count`；否則往下遞迴，最後依規則重算 `len`。

## Coordinate Compression / 座標離散化

Store all `x` endpoints in a sorted unique array `xs`.
Segments correspond to half-open intervals `[xs[i], xs[i+1])`.
用排序去重的 `xs` 建立區間，線段樹用索引表示 `[xs[i], xs[i+1])`。

## Operations / 操作

- `update(ql, qr, delta)`: add `delta` to coverage count for `[ql, qr)`.
  / 對 `[ql, qr)` 做覆蓋次數加減。
- `query()`: return the total covered length (`tree[1]`).
  / 回傳總覆蓋長度。

## Complexity / 複雜度

- Update: `O(log n)`.
  / 更新：`O(log n)`。
- Query: `O(1)` (root length).
  / 查詢：`O(1)`。

## Pitfalls / 常見錯誤

- Use half-open intervals `[x1, x2)` to avoid double counting.
  / 使用半開區間避免重複計算。
- The tree index range is `[0, xs.len() - 1)`.
  / 線段樹索引範圍是 `[0, xs.len() - 1)`。
- Always compute `len` after updating children or `count`.
  / 更新後要重新計算 `len`。
- Treating `count` as the answer instead of `len`.
- Using `[x1, x2]` and over-counting shared boundaries.
- Allocating too small a tree array (not using `4 * n`).

## Minimal Rust Skeleton / Rust 簡化骨架

```rust
struct SegmentTree {
    n: usize,
    tree: Vec<f64>,
    count: Vec<i32>,
    xs: Vec<i64>,
}

impl SegmentTree {
    fn new(xs: Vec<i64>) -> Self {
        let n = xs.len() - 1;
        // 4 * n is a safe upper bound for a binary segment tree array.
        let size = 4 * xs.len().max(1);
        SegmentTree { n, tree: vec![0.0; size], count: vec![0; size], xs }
    }

    fn update(&mut self, idx: usize, l: usize, r: usize, ql: usize, qr: usize, delta: i32) {
        if qr <= l || ql >= r {
            return;
        }
        if ql <= l && r <= qr {
            self.count[idx] += delta;
        } else {
            let mid = (l + r) / 2;
            self.update(idx * 2, l, mid, ql, qr, delta);
            self.update(idx * 2 + 1, mid, r, ql, qr, delta);
        }

        if self.count[idx] > 0 {
            self.tree[idx] = (self.xs[r] - self.xs[l]) as f64;
        } else if r - l == 1 {
            self.tree[idx] = 0.0;
        } else {
            self.tree[idx] = self.tree[idx * 2] + self.tree[idx * 2 + 1];
        }
    }

    fn query(&self) -> f64 {
        self.tree[1]
    }
}
```

## Debug Print / 除錯印樹

Print each node's range, count, and len for a quick sanity check.
用來看每個節點的區間、count、len。

```rust
impl SegmentTree {
    fn debug_print(&self) {
        self.debug_dfs(1, 0, self.n);
    }

    fn debug_dfs(&self, idx: usize, l: usize, r: usize) {
        // Only print nodes that cover at least one segment.
        if l >= r {
            return;
        }
        println!(
            "idx={} [{}, {}) count={} len={}",
            idx, l, r, self.count[idx], self.tree[idx]
        );
        if r - l == 1 {
            return;
        }
        let mid = (l + r) / 2;
        self.debug_dfs(idx * 2, l, mid);
        self.debug_dfs(idx * 2 + 1, mid, r);
    }
}
```

Usage:
```rust
seg.update(1, 0, n, ql, qr, +1);
seg.debug_print();
```

## Code Walkthrough / 程式詳解
- Fields: `xs` is the compressed coordinate list, `n = xs.len()-1` is segment count, `count` stores cover times per node, `tree` stores covered length per node.
- `new`: `size = 4 * xs.len()` allocates enough nodes for a full binary tree; `tree` and `count` start at zero.
- `update(idx, l, r, ql, qr, delta)`:
  - `[l, r)` is the node range in index space, `[ql, qr)` is the update range.
  - If no overlap, return; if fully covered, add `delta` to `count[idx]`.
  - Otherwise recurse to children, then recompute `tree[idx]` from `count` and children.
- `query`: root `tree[1]` is the total covered length across all segments.

## Small Example / 小例子

Given `xs = [0,1,2,3]`, segments are `[0,1) [1,2) [2,3)`.
步驟：add `[0,2)` → add `[1,3)` → remove `[0,2)`。
重疊段 `[1,2)` 在第二步 `count=2`，移除一次後仍保留。

逐步表格：
```
Segments: [0,1) [1,2) [2,3)
Step 1 add [0,2): count = 1, 1, 0 | len = 1, 1, 0 | total = 2
Step 2 add [1,3): count = 1, 2, 1 | len = 1, 1, 1 | total = 3
Step 3 rm  [0,2): count = 0, 1, 1 | len = 0, 1, 1 | total = 2
```

線段樹節點視角（區間對應）：
```
node1 [0,3)
├─ node2 [0,1)
├─ node3 [1,3)
   ├─ node6 [1,2)
   └─ node7 [2,3)
```
每個節點存 `count` 與 `len`，根節點 `len` 就是整體覆蓋長度。

更新時沿路重算（自底向上）：
```
update [1,3)
      node1 [0,3)
           |
        node3 [1,3)  (count += 1)
         /     \
  node6 [1,2) node7 [2,3)
         ↑     ↑
    recompute len at node3, then node1
```

## Related problems / 相關題目

- `leetcode/q3454.md`
- `leetcode/q850.md`
