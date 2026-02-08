---
title: Value-Sorted Prefix Min Sweep / 依值排序的前綴最小掃描
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
---
# Value-Sorted Prefix Min Sweep / 依值排序的前綴最小掃描

Goal: quickly answer `min(dp[x])` over all items with `value[x] <= value[i]`.
目標：快速取得所有滿足 `value[x] <= value[i]` 的狀態最小值。

## When to use / 何時使用

- You need transitions like `dp[i] = min(dp[x])` for all `value[x] <= value[i]`.
  / 轉移形式為 `dp[i] = min(dp[x])`，且 `value[x] <= value[i]`。
- Direct scanning is too slow (quadratic on `n`).
  / 直接掃描會是平方等級。
- The threshold is monotonic in `value` (e.g., `<=`).
  / 門檻是單調關係（如 `<=`）。

## Core idea / 核心概念

1. Sort all items by `value` ascending.
   / 依 `value` 升冪排序所有項目。
2. Scan in order while maintaining a running minimum `minCost`.
   / 依序掃描並維護前綴最小值 `minCost`。
3. For items with the same `value`, update in a batch to avoid contamination.
   / 對相同 `value` 的項目分批更新，避免同輪互相污染。

## Template / 模板

Given arrays `value[i]` and `dp[i]` (previous layer):
給定 `value[i]` 與前一層 `dp[i]`：

```
items = indices sorted by value
minCost = +inf
for each block [l..r] with same value:
    for i in l..r:
        minCost = min(minCost, dp[items[i]])
    for i in l..r:
        dp_next[items[i]] = minCost
```

- If you update `dp` in place, use the two-phase block update above.
  / 若原地更新，一定要採用「先掃描、後寫回」的區塊更新。

## Example / 範例

Values and costs:
值與成本：

```
value: [3, 1, 3, 2]
cost : [8, 5, 6, 7]
```

Sorted indices by value: `[1 (1), 3 (2), 0 (3), 2 (3)]`

Scan:
- value=1 block: minCost=min(5)=5 => dp_next for idx 1 is 5
- value=2 block: minCost=min(5,7)=5 => dp_next for idx 3 is 5
- value=3 block: minCost=min(5,8,6)=5 => dp_next for idx 0,2 are 5

So all positions with value >= 1 get prefix min 5.
符合 `value[x] <= value[i]` 的最小值皆為 5。

## Complexity / 複雜度

- Time: `O(n log n)`
- Space: `O(n)`

Where:
`n`: number of items.


- Sorting: `O(n log n)`.
  / 排序 `O(n log n)`。
- Scan: `O(n)` per layer.
  / 每一層掃描 `O(n)`。

## Pitfalls / 常見陷阱

- Forgetting to batch-update equal values causes using updated values in the same round.
  / 忘記對相同值分批更新會污染本輪結果。
- Mixing different layers of DP without a clear previous/next separation.
  / 沒區分前一層/下一層 DP。

## Related problems / 相關題目

- [q3651](../leetcode/q3651.md)