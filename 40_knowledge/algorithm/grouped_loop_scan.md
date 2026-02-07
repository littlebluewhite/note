---
title: Grouped Loop Scan / 分組迴圈掃描
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-04
updated: 2026-02-04
status: active
source: algorithm
complexity_time: O(n)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-02-18
canonical: algorithm/grouped_loop_scan.md
---
# Grouped Loop Scan / 分組迴圈掃描

## Goal

Iterate an array by **maximal groups/segments** in linear time, without re-scanning elements.
用線性時間枚舉「最大化」的段落或群組，避免重複掃描。

## When to Use

- Need to process runs/segments (monotonic, equal values, pattern phases).
- When the next valid start is deterministically related to the current segment boundary.
- To avoid nested loops while still enumerating all maximal groups.

## Core Idea

Use two indices:

- `i` = start of current group.
- `j` = scan forward to find the end of the maximal group.

After processing the group `[i, j-1]`, move `i` to the next possible start (often `j` or `j-1`).
Each index advances monotonically, so total time is `O(n)`.

## Steps

1. Initialize `i = 0`.
2. Set `j = i + 1`.
3. Advance `j` while the group property holds.
4. Process the maximal group `[i, j-1]`.
5. Set `i` to the next start (e.g., `i = j` or `i = j-1`).
6. Repeat until `i >= n`.

## Complexity

- Time: `O(n)`
- Space: `O(1)`

## Pitfalls

- Off-by-one boundaries (`j` is the first index that breaks the property).
- Forgetting to ensure progress (must move `i` forward every iteration).
- Picking the wrong next start can skip valid groups or cause duplicates.
- Strict vs non-strict comparisons matter for monotonic segments.

## Examples

- Monotonic run enumeration (increasing or decreasing segments).
- Trionic subarray scanning: consume maximal inc → dec → inc, then jump to the start of the last segment.

## Notes

- If overlap is needed, move `i` to a boundary inside the group (e.g., `j-1`).
- If groups are disjoint, move `i` directly to `j`.

## Related

- [q3640](../leetcode/q3640.md)
