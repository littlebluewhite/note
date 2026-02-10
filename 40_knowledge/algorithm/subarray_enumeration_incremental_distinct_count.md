---
title: Subarray Enumeration with Incremental Distinct Counting / 子陣列枚舉與增量去重計數
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-10
updated: 2026-02-10
status: active
source: algorithm
complexity_time: O(n^2)
complexity_space: O(U)
review_interval_days: 14
next_review: 2026-02-24
---
# Subarray Enumeration with Incremental Distinct Counting / 子陣列枚舉與增量去重計數

## Goal

Enumerate all subarrays in `O(n^2)` while maintaining distinct-category counts incrementally, instead of recomputing sets from scratch for every `[l..r]`.
以 `O(n^2)` 枚舉所有子陣列，並用增量方式維護不同類別的去重計數，避免對每個 `[l..r]` 重新統計。

## When to Use

- `n` is around `10^3` to low `10^4`, so quadratic scan is acceptable.
  / `n` 約 `10^3` 級別，可接受平方複雜度。
- Condition is based on **distinct value counts by category** (e.g., even vs odd, color A vs color B).
  / 條件依賴「按類別分組的不同值數量」。
- Value range is bounded, so array-based marking can replace hash sets.
  / 值域可控，可用陣列標記取代雜湊集合。

## Core Idea

Fix left boundary `l`, then grow right boundary `r` from `l` to `n-1`.
Maintain:

- whether value `x` has appeared in current `[l..r]`.
- category-distinct counters (`distinct_even`, `distinct_odd`, etc.).

When extending to `r`, only handle `nums[r]` once:

- if first appearance in current left-run, increment its category counter;
- evaluate condition immediately and update answer.

This turns each `l` into one linear pass.

## Steps

1. Prepare marker structure (`seen_ver`) and global answer `ans`.
2. For each left boundary `l`:
   - start a new version/token;
   - reset category counters to zero.
3. For each `r` from `l` to `n-1`:
   - if `nums[r]` not marked in current version, mark it and update category counter;
   - check target predicate and update `ans`.
4. Return `ans`.

## Complexity

- Time: `O(n^2)`
- Space: `O(U)` (bounded value domain size)

## Pitfalls

- Forgetting to isolate state per `l` causes cross-window contamination.
  / 沒有為每個 `l` 隔離狀態會造成污染。
- Using one shared set but not clearing correctly can lead to wrong distinct counts.
  / 共用集合若未正確清空，去重數量會錯。
- If value range is large/unbounded, array marking is not suitable; switch to hash set/map.
  / 值域太大時應改用雜湊。
- Off-by-one in length update (`r - l + 1`).
  / 子陣列長度常見邊界錯誤。

## Examples

### Balanced by parity-distinct counts / 奇偶去重平衡

Condition:

- `#distinct_even([l..r]) == #distinct_odd([l..r])`

Pseudocode:

```text
ans = 0
for l in [0..n-1]:
    new_version()
    de = 0
    do = 0
    for r in [l..n-1]:
        x = nums[r]
        if first_seen_in_this_version(x):
            if x is even: de++ else do++
        if de == do:
            ans = max(ans, r-l+1)
```

## Notes

- With bounded domain, this pattern is often faster than `HashSet` due to contiguous memory.
- Versioned markers avoid `O(U)` clearing per left boundary.
- If categories are more than two, store an array of counters indexed by category id.

## Related

- [q3719](../leetcode/q3719.md)
- [timestamped_presence_array](../data_structure/timestamped_presence_array.md)
