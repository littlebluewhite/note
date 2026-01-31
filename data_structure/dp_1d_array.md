# DP 1D Array / 一維 DP 陣列

Goal: store the best value for each position with `O(1)` access.
目標：用 `O(1)` 存取每個位置的最佳值。

## Core structure / 核心結構

- `dp[i]` holds the optimal value for state `i`.
  / `dp[i]` 儲存狀態 `i` 的最佳值。
- Usually a `Vec<usize>` or `Vec<i32>`; initialized with base values.
  / 多半用 `Vec<usize>` 或 `Vec<i32>`，並先填入初始值。

## Typical operations / 常見操作

- Initialize: `dp[i] = 1` (or other base) for all `i`.
  / 初始化：`dp[i] = 1`（或其他基底）。
- Update with transitions: `dp[j] = max(dp[j], dp[i] + 1)`.
  / 用轉移更新：`dp[j] = max(dp[j], dp[i] + 1)`。
- Read final answer: `max(dp)` or `dp[last]`.
  / 讀取答案：`max(dp)` 或 `dp[last]`。

## When to use / 使用時機

- Sequence DP problems where each position depends on earlier ones.
  / 序列型 DP，狀態依賴之前位置。
- Longest chain / subsequence DP.
  / 最長鏈、最長子序列類 DP。
- Single-dimension state is enough.
  / 單一維度就能表達狀態。

## Complexity / 複雜度

- Space: `O(n)` for `n` positions.
  / 空間：`O(n)`。
- Time depends on transitions (often `O(n^2)`).
  / 時間取決於轉移成本（常見為 `O(n^2)`）。

## Pitfalls / 常見陷阱

- Wrong base values make all transitions invalid.
  / 基底設錯會導致所有轉移無效。
- Overwriting in the wrong order if transition needs old values.
  / 若需舊值，更新順序錯會污染狀態。
- Using `i32` when the value can exceed bounds.
  / 值可能超界時別用 `i32`。

## Related problems / 相關題目

- [q960](../leetcode/q960.md)
- [q2977](../leetcode/q2977.md)
