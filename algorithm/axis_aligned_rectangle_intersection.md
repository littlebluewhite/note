---
title: "Axis-Aligned Rectangle Intersection / 軸對齊矩形交集"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(n^2)
complexity_space: O(1)
---
# Axis-Aligned Rectangle Intersection / 軸對齊矩形交集

Goal: compute the intersection of two axis-aligned rectangles and use it to derive area or maximum inscribed square.
目標：計算兩個軸對齊矩形的交集，並據此求面積或交集內可放的最大正方形。

## When to use / 使用時機

- Need overlap width/height between two rectangles.
  / 需要快速判斷兩矩形重疊與交集尺寸。
- Need to maximize a value over all rectangle pairs (e.g., max overlap area).
  / 需要在所有矩形對中找最大交集相關值。

## Key formula / 核心公式

For rectangle A `(ax1, ay1)` to `(ax2, ay2)` and B `(bx1, by1)` to `(bx2, by2)`:
對矩形 A `(ax1, ay1)` 到 `(ax2, ay2)` 與 B `(bx1, by1)` 到 `(bx2, by2)`：

- `left = max(ax1, bx1)`, `right = min(ax2, bx2)`
- `bottom = max(ay1, by1)`, `top = min(ay2, by2)`
- `width = right - left`, `height = top - bottom`
- Intersection exists iff `width > 0` and `height > 0`.
  / 當 `width > 0` 且 `height > 0` 時才有交集。

If you need the largest square inside the intersection:
若要交集內最大正方形：

- `side = min(width, height)`
- `area = side * side`

## Pattern / 流程

1. Enumerate all rectangle pairs `(i, j)`.
   / 枚舉所有矩形對 `(i, j)`。
2. Compute intersection width/height via the formula.
   / 用公式算交集寬高。
3. If intersecting, compute target value (area, square, etc.) and update the maximum.
   / 若相交，計算目標值並更新最大值。

## Worked Example / 範例

Rect A: `(1, 1)` to `(4, 5)`, Rect B: `(2, 3)` to `(6, 4)`
矩形 A：`(1, 1)` 到 `(4, 5)`，矩形 B：`(2, 3)` 到 `(6, 4)`

- `left = max(1, 2) = 2`, `right = min(4, 6) = 4`
- `bottom = max(1, 3) = 3`, `top = min(5, 4) = 4`
- `width = 2`, `height = 1` → intersection exists.
  / `width = 2`、`height = 1` → 有交集。
- Largest square side is `min(2, 1) = 1`, area `= 1`.
  / 最大正方形邊長 `1`，面積 `1`。

## Pitfalls / 常見陷阱

- Using `>= 0` instead of `> 0` (touching edges has zero area).
  / 用 `>= 0` 會把只接觸邊界的情況當成相交。
- Area can exceed `i32` when coordinates are large; use `i64`.
  / 座標大時面積可能超出 `i32`，用 `i64`。
- Forgetting that the max over intersections of 2+ rectangles is covered by some pair.
  / 忘了「多矩形交集」必然是某個矩形對交集的子集合。

## Complexity / 複雜度

- Time: `O(n^2)` for `n` rectangles (pairwise enumeration).
  / 時間：`O(n^2)`。
- Space: `O(1)` extra.
  / 空間：`O(1)`。

## Rust snippet / Rust 範例

```rust
fn max_square_area(bottom_left: &Vec<Vec<i32>>, top_right: &Vec<Vec<i32>>) -> i64 {
    let n = bottom_left.len();
    let mut best: i64 = 0;
    for i in 0..n {
        for j in (i + 1)..n {
            let left = bottom_left[i][0].max(bottom_left[j][0]) as i64;
            let right = top_right[i][0].min(top_right[j][0]) as i64;
            let bottom = bottom_left[i][1].max(bottom_left[j][1]) as i64;
            let top = top_right[i][1].min(top_right[j][1]) as i64;

            let w = right - left;
            let h = top - bottom;
            if w > 0 && h > 0 {
                let side = if w < h { w } else { h };
                best = best.max(side * side);
            }
        }
    }
    best
}
```

## Related problems / 相關題目

- [q3047](../leetcode/q3047.md)
- [q3453](../leetcode/q3453.md)
- [q3454](../leetcode/q3454.md)
