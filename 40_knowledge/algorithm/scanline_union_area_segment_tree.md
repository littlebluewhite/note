---
title: Scanline + Segment Tree Union Area / 掃描線 + 線段樹求聯集面積
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(n log n)
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
canonical: algorithm/scanline_union_area_segment_tree.md
---
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

## Coordinate Compression Example / 離散化例子

離散化做法：
- 收集所有矩形/正方形的 `x1`、`x2`，排序去重成 `xs`。
- 線段樹葉子對應 `[xs[i], xs[i+1])`，覆蓋只會在端點變化。

例如兩個區間 `[-1, 2)` 與 `[1, 5)`，端點集合是 `{-1, 1, 2, 5}`，
離散化後切成三段 `[-1, 1)`, `[1, 2)`, `[2, 5)`，每段只需記錄覆蓋次數。
ASCII 示意：
```
原始區間:
[-1, 2)  **********
   [1, 5)      ***************
端點:  -1   1   2       5
切段:  [-1,1) [1,2) [2,5)
```
若把兩個區間都加進去，覆蓋次數分別是：
`[-1,1)`=1, `[1,2)`=2, `[2,5)`=1；聯集長度就是三段的長度總和。
口訣：`count > 0 -> 全覆蓋；count = 0 -> 看孩子`。

## Example / 範例

小例子（兩個正方形）：
```
A: x:[0,2) y:[0,2)
B: x:[1,3) y:[1,3)
事件:
y=0 add [0,2)
y=1 add [1,3)
y=2 remove [0,2)
y=3 remove [1,3)
xs = [0,1,2,3] -> 切段: [0,1) [1,2) [2,3)
```
掃描過程（prev_y 從 0 開始）：
```
y=0: area += 0*(0-0)=0
覆蓋次數: [0,1)=1 [1,2)=1 [2,3)=0 -> width=2

y=1: area += 2*(1-0)=2
覆蓋次數: [0,1)=1 [1,2)=2 [2,3)=1 -> width=3

y=2: area += 3*(2-1)=3 (累計 5)
覆蓋次數: [0,1)=0 [1,2)=1 [2,3)=1 -> width=2

y=3: area += 2*(3-2)=2 (累計 7)
覆蓋次數: [0,1)=0 [1,2)=0 [2,3)=0 -> width=0
```
總面積 = 7（=4+4-1），示範 `y` 事件決定高度段，線段樹維護 x 聯集寬度。

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

## Pitfalls / 常見錯誤

- Use half-open intervals `[x1, x2)` to avoid double counting.
  / 使用半開區間 `[x1, x2)` 避免重複計算。
- Always add area **before** applying events at the current `y`.
  / 面積要先累積，再處理當前 `y` 的事件。
- Group events with the same `y` to keep each strip width constant.
  / 同一個 `y` 的事件要一起處理，條帶寬度才不會被切碎。
- Sort + dedup `xs` to avoid zero-length segments.
  / `xs` 要排序去重，避免零長度區間。
- Use 64-bit or floating types for area.
  / 面積請用 64-bit 或浮點型別。

## Order Details / 次序重點

Between two consecutive distinct `y` values, the x-coverage is constant.
So the strip `(prev_y, cur_y)` must use the *old* coverage before applying
events at `cur_y`, and all events at the same `y` should be grouped.

相鄰事件高度之間，x 覆蓋固定，所以 `prev_y ~ cur_y` 應使用更新前的寬度；
同一個 `y` 的事件要一起處理，否則會把同一條帶錯切成多段。

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

Template Explanation / 模板逐行說明
- `events`: 每個矩形產生兩個事件，`+1` 表示進入覆蓋，`-1` 表示退出覆蓋。
- `xs`: 收集所有 `x1/x2` 端點做離散化，線段樹用索引維護 `[xs[i], xs[i+1])`。
- `build segment tree`: 節點儲存 `count` 與 `len`，`len` 是該區間的聯集長度。
- `sort events by y`: 掃描線自下而上，事件高度決定覆蓋集合何時改變。
- `prev_y`: 上一次事件高度，`cur_y - prev_y` 就是當前高度條帶厚度。
- `width = tree.query()`: 查詢 x 聯集寬度，代表這個高度條帶的固定寬度。
- `area += width * (cur_y - prev_y)`: 累積此高度條帶的面積。
- `apply all events at cur_y`: 更新線段樹覆蓋次數，再往上掃描。

## Related problems / 相關題目

- [q3454](../leetcode/q3454.md)
- [q850](../leetcode/q850.md)
