---
title: Edit Distance DP / 編輯距離 DP
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(mn)
complexity_space: O(mn)
review_interval_days: 14
next_review: 2026-02-17
canonical: algorithm/edit_distance_dp.md
---
# Edit Distance DP / 編輯距離 DP

Goal: compute the minimum cost to transform one string into another by allowed edit operations.
目標：在允許的編輯操作下，計算將字串 A 轉成字串 B 的最小代價。

## When to use / 使用時機

- String alignment problems with cost (insert/delete/replace/keep).
  / 需要對齊兩字串並計算成本（插入/刪除/替換/保留）。
- Variants of edit distance, delete sum, or min deletions to match.
  / 編輯距離、刪除總和、最少刪除數等變形題。
- Optimal result on prefixes implies optimal result on larger prefixes.
  / 前綴的最優解可以推導更長前綴的最優解。

## State / 狀態

- Let `dp[i][j]` be the minimum cost to make `a[0..i)` and `b[0..j)` equal.
  / `dp[i][j]` 表示讓 `a[0..i)` 與 `b[0..j)` 相等的最小成本。
- Use `(m+1) x (n+1)` table to handle empty prefixes cleanly.
  / 使用 `(m+1) x (n+1)` 表格處理空前綴。

## Base cases / 初始條件

- `dp[0][0] = 0`
  / 空對空的成本為 0。
- `dp[i][0] = dp[i-1][0] + cost_delete(a[i-1])`
  / 把 `a[0..i)` 變成空字串，只能一直刪除。
- `dp[0][j] = dp[0][j-1] + cost_insert(b[j-1])`
  / 把空字串變成 `b[0..j)`，只能一直插入。

## Transition / 轉移

If `a[i-1] == b[j-1]`:

```
dp[i][j] = dp[i-1][j-1]  // keep the character
```

If `a[i-1] != b[j-1]`:

```
dp[i][j] = min(
  dp[i-1][j]   + cost_delete(a[i-1]), // delete from a
  dp[i][j-1]   + cost_insert(b[j-1]), // insert into a
  dp[i-1][j-1] + cost_replace(a[i-1], b[j-1]) // replace
)
```

只有允許部分操作時，把不允許的選項移除即可。

## Custom cost models / 成本模型調整

- Equal cost edits: standard Levenshtein distance (`cost_* = 1`).
  / 標準編輯距離，所有操作成本相同。
- ASCII delete sum (LeetCode 712): only delete allowed.
  / ASCII 刪除總和：只允許刪除。

For delete-sum:

```
if a[i-1] == b[j-1]:
  dp[i][j] = dp[i-1][j-1]
else:
  dp[i][j] = min(
    dp[i-1][j] + ascii(a[i-1]),
    dp[i][j-1] + ascii(b[j-1])
  )
```

## Order / 計算順序

- Iterate `i = 1..m`, `j = 1..n` so `dp[i-1][j]`, `dp[i][j-1]`, `dp[i-1][j-1]` are ready.
  / 只要上、左、左上已完成即可。
- Space can be compressed to `O(n)` with a rolling row.
  / 可用滾動陣列壓到 `O(n)` 空間。

## Complexity / 複雜度

- Time: `O(mn)`
  / 時間：`O(mn)`。
- Space: `O(mn)` (or `O(n)` with rolling).
  / 空間：`O(mn)`（可壓縮到 `O(n)`）。

## Pitfalls / 常見陷阱

- Off-by-one when mixing indices and prefix lengths.
  / 索引與前綴長度混用造成 off-by-one。
- Make sure costs are computed using correct character values.
  / 成本要用正確的字元值（ASCII/Unicode）。
- Large costs: pick a safe integer type.
  / 成本可能變大時要選對數值型別。

## Related problems / 相關題目

- [72. Edit Distance](https://leetcode.com/problems/edit-distance/)
- [583. Delete Operation for Two Strings](https://leetcode.com/problems/delete-operation-for-two-strings/)
- [712. Minimum ASCII Delete Sum for Two Strings](https://leetcode.com/problems/minimum-ascii-delete-sum-for-two-strings/)
- [q712](../leetcode/q712.md)