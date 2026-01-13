# Piecewise Linear Sweep / 分段線性掃描

Goal: integrate or search a monotone piecewise-linear function using slope change events.
目標：用「斜率變化事件」掃描，積分或搜尋單調的分段線性函數。

## When to Use / 使用時機

- The cumulative value is the sum of independent contributions (e.g., area below a line).
  / 累積值是多個獨立貢獻的總和（例如線下方面積）。
- Each contribution becomes active on an interval and adds a constant slope.
  / 每個貢獻只在某個區間內提供固定斜率。
- You need the earliest position where the cumulative value reaches a target.
  / 需要找最小位置使累積值達到目標。

## Key Idea / 關鍵概念

If slope changes only at event positions, then between two consecutive events the slope is constant.
因此相鄰事件之間是固定斜率的線性段。

Let:
- `slope` = current slope (sum of active contributions)
- `area` = cumulative value at `prev_y`

Then for `y` in `[prev_y, curr_y]`:
`F(y) = area + slope * (y - prev_y)`

So if `target` falls inside this segment:
`y = prev_y + (target - area) / slope`

## Steps / 流程

1. Build events `(y, delta_slope)`.
   / 建立事件 `(y, 斜率變化)`。
2. Sort events by `y`.
   / 依 `y` 排序。
3. Sweep in order:
   - Advance to next event, add `slope * dy` to `area`.
   - If `target` is within this segment, compute the exact `y`.
   - Apply all events at the current `y` to update `slope`.
   / 掃描區間，累積面積並更新斜率。

## Complexity / 複雜度

- Time: `O(n log n)` for sorting.
  / 時間：排序 `O(n log n)`。
- Space: `O(n)` for events.
  / 空間：事件陣列 `O(n)`。

## Pitfalls / 常見陷阱

- Always group events with the same `y` together.
  / 同一個 `y` 的事件要一起處理。
- If `slope == 0`, the segment is flat; only return if `target == area`.
  / `slope == 0` 代表平坦區段，只有 `target == area` 才有解。
- Use 64-bit or floating types to avoid overflow.
  / 使用 64-bit 或浮點型別避免溢位。

## Minimal Template / 簡化模板

```text
sort events
area = 0
slope = 0
prev_y = events[0].y
apply events at prev_y to slope
for each next event at curr_y:
    dy = curr_y - prev_y
    if slope > 0 and area + slope * dy >= target:
        return prev_y + (target - area) / slope
    area += slope * dy
    prev_y = curr_y
    apply events at curr_y to slope
```

## Related Problems / 相關題目

- `leetcode/q3453.md`
