---
title: Two-Event Interval Scheduling / 兩個不重疊區間最大和
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
canonical: algorithm/interval_scheduling_two_events.md
---
# Two-Event Interval Scheduling / 兩個不重疊區間最大和

Goal: select at most two non-overlapping intervals to maximize total value.
目標：最多選兩個不重疊區間，使價值總和最大。

## Core idea / 核心概念

- Sort intervals by start time.
  / 依開始時間排序。
- For each interval as the first pick, find the earliest non-overlapping second interval.
  / 固定第一個區間後，找能接續的第二個區間。
- Use `suffix_max` to get the best value among all valid second intervals.
  / 用 `suffix_max` 快速取得後續最大價值。

## Pattern / 流程

1. Sort by `start`.
   / 依 `start` 排序。
2. Build `starts` array and `suffix_max` of values.
   / 建 `starts` 與 `suffix_max`。
3. For each interval `(s, e, v)`:
   / 對每個區間：
   - Find `j = lower_bound(starts, e + 1)`.
     / 用二分搜尋找第一個 `start >= e + 1`。
   - Candidate = `v + suffix_max[j]` (or just `v` if `j == n`).
     / 候選答案為 `v + suffix_max[j]`，若沒有則只取 `v`。
4. Take maximum candidate.
   / 取最大值。

## Example / 範例

Events: `[ [1,3,2], [2,4,3], [4,5,2] ]`

- Sorted by start: same order.
- `suffix_max` of values: `[3, 3, 2, 0]`.
- For event `[1,3,2]`, `e + 1 = 4`, `j = 2`, candidate = `2 + 2 = 4`.
- Best answer is `4`.

## Pitfalls / 常見陷阱

- Inclusive end time: the next start must satisfy `start >= end + 1`.
  / 區間為閉區間，下一個必須從 `end + 1` 開始。
- Sorting by end time breaks the lower_bound on starts.
  / 若不是按 start 排序，二分搜尋會失效。
- Missing the case of taking only one interval.
  / 忘了只選一個區間也可能是最優。

## Complexity / 複雜度

- Time: `O(n log n)`
- Space: `O(n)`

Where:
`n`: number of intervals.


- Sorting: `O(n log n)`
  / 排序：`O(n log n)`
- Per interval binary search: `O(log n)`
  / 每個區間二分：`O(log n)`
- Total: `O(n log n)` time, `O(n)` space.
  / 總計：時間 `O(n log n)`，空間 `O(n)`。

## Related problems / 相關題目

- [q2054](../leetcode/q2054.md)