# Longest Chain DP (Column Compatibility) / 最長鏈 DP（欄位相容）

Goal: pick the longest subsequence where every pair of consecutive elements is compatible under a custom order.
目標：在自訂的相容關係下，挑出最長的可連接子序列。

## Core idea / 核心概念

- Treat each position as a node in a DAG ordered by index.
  / 將每個位置視為 DAG 節點（依索引方向）。
- Add a directed edge `i -> j` when `i < j` and `i` can precede `j`.
  / 若 `i < j` 且相容，視為有邊 `i -> j`。
- The longest chain is the longest path in this DAG; use DP.
  / 最長鏈等同 DAG 最長路徑，可用 DP 求解。

## When to use / 使用時機

- Need a longest subsequence with a custom comparator.
  / 需要自訂比較規則的最長子序列。
- Compatibility depends on multiple rows or dimensions.
  / 相容條件來自多列或多維資料。
- Input size allows `O(m^2 * k)` transitions.
  / 資料量可接受 `O(m^2 * k)` 的轉移成本。

## State / 狀態

- `dp[j]`: longest valid chain ending at position `j`.
  / `dp[j]`：以 `j` 結尾的最長鏈長度。

## Transition / 轉移

For each `j`, try all `i < j`:
/ 對每個 `j`，枚舉所有 `i < j`：

```
if compatible(i, j) {
    dp[j] = max(dp[j], dp[i] + 1)
}
```

Compatibility example for columns:
/ 欄位相容範例：

- `compatible(i, j)` if for all rows `r`, `strs[r][i] <= strs[r][j]`.
  / 若所有列 `r` 都滿足 `strs[r][i] <= strs[r][j]`，則相容。

## Answer / 答案

- `max(dp)` gives the longest keepable chain.
  / `max(dp)` 是可保留的最長鏈。
- If deletions are allowed: `answer = m - max(dp)`.
  / 若允許刪除：`答案 = m - max(dp)`。

## Complexity / 複雜度

- Time: `O(m^2 * k)` where `k` is compatibility check cost.
  / 時間：`O(m^2 * k)`，`k` 為相容判斷成本。
- Space: `O(m)` for the DP array.
  / 空間：`O(m)`。

## Pitfalls / 常見陷阱

- Forgetting to initialize `dp[j] = 1`.
  / 忘記初始化 `dp[j] = 1`。
- Not treating equality as allowed when order is non-decreasing.
  / 需要非遞減時，別把相等排除。
- Recomputing compatibility expensively; keep checks simple.
  / 相容檢查太重；盡量簡化。

## Related problems / 相關題目

- [q960](../leetcode/q960.md)