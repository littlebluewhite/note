# DP 2D Array / 二維 DP 陣列

Goal: store DP states for two indices with `O(1)` access.
目標：以 `O(1)` 存取兩個維度的 DP 狀態。

## Core structure / 核心結構

- `dp[i][j]` stores the best value for state `(i, j)`.
  / `dp[i][j]` 儲存狀態 `(i, j)` 的最佳值。
- Common type: `Vec<Vec<i32>>` or `Vec<Vec<i64>>`.
  / 常用型別：`Vec<Vec<i32>>` 或 `Vec<Vec<i64>>`。

## Initialization / 初始化

- Allocate with a base value:
  / 以基底值配置：

```
let mut dp = vec![vec![init; n]; m];
```

- Use a safe negative sentinel when results can be negative.
  / 若可能為負值，請用安全的負無窮哨兵。

## Indexing tips / 索引技巧

- For easier boundary handling, some problems add an extra row/column as padding.
  / 有些題目會加一列或一欄當作 padding，方便處理邊界。
- Be consistent about 0-based or 1-based indexing.
  / 請一致使用 0-based 或 1-based 索引。

## Update order / 更新順序

- If transitions use `dp[i-1][j]`, `dp[i][j-1]`, `dp[i-1][j-1]`, iterate row-major or column-major.
  / 若依賴三個方向，使用行優先或列優先即可。
- For rolling arrays, keep the previous row and update left-to-right.
  / 若用滾動陣列，保留上一列並由左到右更新。

## Complexity / 複雜度

- Space: `O(mn)` for `m x n` states.
  / 空間：`O(mn)`。
- Access/update: `O(1)` per state.
  / 單次存取或更新：`O(1)`。

## Pitfalls / 常見陷阱

- Memory can be large for big `m, n`; consider compression.
  / `m, n` 很大時注意記憶體，可做壓縮。
- Mixing in empty-state values can break non-empty constraints.
  / 若有非空限制，別讓空狀態值混入。

## Related problems / 相關題目

- `leetcode/q1458.md`
- [62. Unique Paths](https://leetcode.com/problems/unique-paths/)
- [64. Minimum Path Sum](https://leetcode.com/problems/minimum-path-sum/)
- [1143. Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/)
