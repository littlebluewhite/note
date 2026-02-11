---
title: Prefix Sum Dynamic Balance Transform / 前綴和動態平衡轉換
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-02-11
updated: 2026-02-11
status: active
source: knowledge
complexity_time: O(n log n)
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-25
---
# Prefix Sum Dynamic Balance Transform / 前綴和動態平衡轉換

## Goal

Convert "distinct category counts are equal" problems into a zero-sum prefix problem that still works while the left boundary slides.
把「兩類去重數量相等」轉成「區間和為 0」的前綴和問題，且可在左邊界移動時持續維護。

## When to Use

- Objective is based on equality of two distinct-category counts (e.g., distinct even vs distinct odd).
- Need longest/maximum interval under that equality condition.
- Brute force over all left boundaries is too slow (`n` around `10^5`).
- Can support range-adjustment after moving left boundary (usually with lazy segment tree).

## Core Idea

For a fixed left boundary `l`, define contribution per value occurrence:

- first occurrence of an even value in current window contributes `+1`
- first occurrence of an odd value contributes `-1`
- repeated occurrences contribute `0`

Then for any right boundary `r`:

- `balanced(l, r)` iff `sum(contrib[l..r]) == 0`

So the task becomes "find farthest `r` such that transformed prefix at `r` equals 0".

When left boundary moves from `l` to `l+1`, only the removed value `x = nums[l]` changes contributions:

- if next occurrence of `x` is at `next`, then removing `x` affects transformed prefix on `[l+1, next-1]`
- this is a range add update

Hence the full approach is:

- prefix transform + dynamic range updates + farthest target-value query

## Steps

1. Build initial transformed prefix for `l = 0`.
2. Record all occurrence positions for each value in queues.
3. Build a structure over prefix values that supports:
   - range add
   - rightmost position with target value (usually `0`)
4. Iterate left boundary `l`:
   - query best right boundary `r >= l + current_best`
   - pop current occurrence of `nums[l]`
   - apply range update on `[l+1, next-1]`
5. Keep global maximum length.

## Complexity

- Time: `O(n log n)`
- Space: `O(n)`

## Pitfalls

- Off-by-one between array index (`0-based`) and prefix structure index (`1-based`).
- Wrong update interval when removing left boundary element; correct interval is `[l+1, next-1]`.
- Forgetting duplicates contribute `0` in transformed array.
- Querying from `l` instead of `l + current_best` loses pruning and slows down in practice.

## Examples

### Example: `nums = [3,2,2,5,4]`

- Initial (`l=0`) transformed contributions by first-seen rule:
  - `3 -> -1`, `2 -> +1`, second `2 -> 0`, `5 -> -1`, `4 -> +1`
- Prefix becomes `[-1, 0, 0, -1, 0]`
- Rightmost `0` gives full length `5`
- Moving `l` forward updates only a contiguous prefix range determined by next position of removed value

## Notes

- Correctness relies on contribution being local to first occurrence and on exact range-adjustment while left boundary advances.
- "target in [min, max]" pruning for segment tree search additionally relies on prefix differences being stepwise (discrete intermediate-value property).

## Related

- [q3721](../leetcode/q3721.md)
- [segment_tree_lazy_min_max_target_search](../data_structure/segment_tree_lazy_min_max_target_search.md)
- [hashmap_vecdeque_occurrence_queue](../data_structure/hashmap_vecdeque_occurrence_queue.md)
