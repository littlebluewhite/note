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

## Pitfalls / 常見陷阱

- Use half-open intervals `[x1, x2)` to avoid double counting.
  / 使用半開區間避免重複計算。
- The tree index range is `[0, xs.len() - 1)`.
  / 線段樹索引範圍是 `[0, xs.len() - 1)`。
- Always compute `len` after updating children or `count`.
  / 更新後要重新計算 `len`。

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

## Related problems / 相關題目

- `leetcode/q3454.md`
- `leetcode/q850.md`
