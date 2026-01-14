# Scanline + Segment Tree Union Area / 掃描線 + 線段樹求聯集面積

Goal: compute the union area of axis-aligned rectangles/squares where overlaps are counted once.
目標：計算軸對齊矩形/正方形的聯集面積，重疊只算一次。

## When to Use / 使用時機

- Overlapping rectangles/squares must be merged into a single covered region.
  / 需要合併重疊矩形/正方形的覆蓋面積。
- The coverage changes only at rectangle edges (event positions).
  / 覆蓋只會在矩形邊界的事件位置改變。

## Key Idea / 關鍵概念

Sweep a horizontal line by increasing `y`. Between two consecutive event `y` values, the active
intervals on `x` do not change, so the covered width is constant.
用掃描線沿 `y` 方向上移。相鄰事件 `y` 之間，活躍的 `x` 區間不變，因此水平覆蓋寬度固定。

Use coordinate compression on all `x` boundaries, and maintain the union length of active `x`
intervals with a segment tree that supports range add.
把所有 `x` 邊界離散化，用線段樹做區間加法，維護活躍區間的聯集長度。

## Events / 事件

For each rectangle/square:
- bottom edge: `(y, x1, x2, +1)`
- top edge: `(y2, x1, x2, -1)`
每個矩形/正方形產生兩個事件：底邊 `+1`、頂邊 `-1`。

## Steps / 流程

1. Build events and collect all `x` endpoints.
   / 建立事件並收集所有 `x` 端點。
2. Sort unique `x` and build a segment tree on compressed indices.
   / 排序去重 `x`，建立線段樹。
3. Sort events by `y`.
   / 依 `y` 排序事件。
4. Sweep in order:
   - `width = tree.query()` gives union length on `x`.
   - `area += width * (cur_y - prev_y)`.
   - Apply all events at `cur_y` to the tree.
   / 取目前寬度累積面積，處理同一 `y` 的事件更新。

## Optional: Record Segments / 可選：記錄區間

If you need the earliest `y` where area reaches a target (e.g., half the total area), record each
strip as `(y_start, y_end, start_area, width)` during the sweep, then locate the target segment and
interpolate.
若需要找最小 `y` 使面積達到目標（例如總面積一半），可在掃描時記錄 `(y_start, y_end, start_area, width)`，
再定位區間並線性插值。

## Complexity / 複雜度

- Time: `O(n log n)` for sorting and segment tree updates.
  / 時間：`O(n log n)`。
- Space: `O(n)` for events and the segment tree.
  / 空間：`O(n)`。

## Pitfalls / 常見陷阱

- Use half-open intervals `[x1, x2)` to avoid double counting.
  / 使用半開區間 `[x1, x2)` 避免重複計算。
- Always add area **before** applying events at the current `y`.
  / 面積要先累積，再處理當前 `y` 的事件。
- Coordinate compression is required for large coordinates.
  / 大座標需做離散化。
- Use 64-bit or floating types for area.
  / 面積請用 64-bit 或浮點型別。

## Minimal Template / 簡化模板

```text
events = [(y, x1, x2, +1/-1) ...]
xs = sorted unique x endpoints
build segment tree on xs
sort events by y
prev_y = events[0].y
area = 0
for each group at cur_y:
    width = tree.query()
    area += width * (cur_y - prev_y)
    apply all events at cur_y (range add)
    prev_y = cur_y
```

## Related problems / 相關題目

- `leetcode/q3454.md`
- `leetcode/q850.md`
