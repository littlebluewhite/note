---
title: Room Allocation with Two Heaps / 兩堆資源排程
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(m log m + m log n)
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
canonical: algorithm/room_allocation_two_heaps.md
---
# Room Allocation with Two Heaps / 兩堆資源排程

Goal: assign time intervals to fixed rooms, delaying when all rooms are busy, while always choosing the smallest room id.
目標：固定房間數下做會議排程，房間全滿時延後會議，並永遠選擇最小編號房間。

## Core idea / 核心概念

- Sort meetings by original start time.
  / 依原始開始時間排序。
- Maintain two min-heaps:
  / 維護兩個最小堆：
  - `available`: room ids that are free (min by id).
    / `available`：空房間編號最小堆。
  - `busy`: `(end_time, room_id)` for occupied rooms (min by end, tie by id).
    / `busy`：已占用房間的 `(結束時間, 編號)` 最小堆。
- For each meeting, release all rooms with `end_time <= start`, then either assign a free room or delay to the earliest end time.
  / 每場會議先釋放 `end_time <= start` 的房間，再分配空房間或延後到最早結束時間。

## Pattern / 流程

1. Sort meetings by `start`.
   / 依 `start` 排序。
2. Initialize `available` with all room ids, `busy` empty.
   / 將所有房間放入 `available`，`busy` 為空。
3. For each meeting `(s, e)`:
   / 對每場會議 `(s, e)`：
   - While `busy.top.end <= s`, move that room to `available`.
     / 釋放所有 `end <= s` 的房間。
   - If `available` not empty: take smallest room id, schedule `[s, e)`.
     / 若有空房間，取最小編號直接排 `[s, e)`。
   - Else: pop earliest `(end, room)`, delay meeting to `[end, end + (e - s))`.
     / 若無空房間，取最早結束房間並延後到 `[end, end + (e - s))`。
   - Record meeting count for that room.
     / 累加該房間的會議次數。
4. Return the room id with the highest count (tie by smallest id).
   / 回傳次數最多的房間，若同分選最小編號。

## Example / 範例

Rooms: `n = 2`, meetings: `[[1,4],[2,3],[3,5]]`

- Start `[1,4]`: assign room 0, busy -> `(4,0)`.
- Start `[2,3]`: assign room 1, busy -> `(3,1),(4,0)`.
- Start `[3,5]`: release room 1 (end=3), assign room 1.

## Pitfalls / 常見陷阱

- Use 64-bit for time because delays can exceed original bounds.
  / 延後累積可能很大，時間要用 64-bit。
- `busy` heap must tie-break by room id when end times equal.
  / `busy` 堆在同一結束時間要按房間編號排序。
- Always release all `end <= start` before allocating.
  / 分配前一定要先釋放所有 `end <= start` 的房間。

## Complexity / 複雜度

- Time: `O(m log m + m log n)`
- Space: `O(n)`

Where:
`m`: number of meetings.
`n`: number of rooms.


- Sorting: `O(m log m)` where `m = meetings.length`.
  / 排序：`O(m log m)`。
- Heap operations per meeting: `O(log n)`.
  / 每場會議堆操作：`O(log n)`。
- Total: `O(m log n)` time, `O(n)` space.
  / 總計：時間 `O(m log n)`，空間 `O(n)`。

## Related problems / 相關題目

- [q2402](../leetcode/q2402.md)