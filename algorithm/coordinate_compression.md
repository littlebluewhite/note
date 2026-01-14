# Coordinate Compression / 座標壓縮

Goal: map large/sparse coordinates to a compact index range while preserving order.
目標：把大而稀疏的座標映射成小範圍索引，同時保留排序關係。

## When to Use / 使用時機

- Coordinates up to `1e9` or `1e18`, but only `n` unique values matter.
  / 座標很大但只有 `n` 個實際出現的值。
- Data structures need dense indices (segment tree, BIT, array DP).
  / 需要密集索引的資料結構（線段樹、BIT、陣列 DP）。

## Steps / 流程

1. Collect all coordinates that appear in queries or intervals.
   / 收集所有會用到的座標。
2. Sort and deduplicate to form `xs`.
   / 排序並去重，得到 `xs`。
3. Use binary search to map each coordinate to its index in `xs`.
   / 用二分搜尋找到每個座標的索引。

## Half-Open Interval / 半開區間

For interval problems, use `[x1, x2)` so adjacent edges do not overlap.
區間問題建議用 `[x1, x2)`，避免邊界重複計算。

If you store segments between coordinates, there are `xs.len() - 1` segments:
`[xs[i], xs[i+1])`.
若用座標端點建立區間，段數為 `xs.len() - 1`。

## Pitfalls / 常見陷阱

- Forgetting to include both ends of an interval.
  / 忘了把區間兩端都加入壓縮列表。
- Using compressed indices directly as coordinates.
  / 把壓縮後的索引當原座標使用。
- Mixing inclusive/exclusive boundaries.
  / 混用閉區間與半開區間造成重複或漏算。

## Minimal Rust Example / Rust 簡化範例

```rust
fn compress(mut coords: Vec<i64>) -> Vec<i64> {
    coords.sort();
    coords.dedup();
    coords
}

fn idx_of(xs: &[i64], x: i64) -> usize {
    xs.binary_search(&x).unwrap()
}
```

## Related problems / 相關題目

- `leetcode/q3454.md`
