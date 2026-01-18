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

- For prefix DP, use `(m+1) x (n+1)` to represent empty prefixes.
  / 前綴 DP 常用 `(m+1) x (n+1)` 代表空前綴，邊界更好處理。
- Use a safe negative sentinel when results can be negative.
  / 若可能為負值，請用安全的負無窮哨兵。

## Indexing tips / 索引技巧

- For easier boundary handling, some problems add an extra row/column as padding.
  / 有些題目會加一列或一欄當作 padding，方便處理邊界。
- Be consistent about 0-based or 1-based indexing.
  / 請一致使用 0-based 或 1-based 索引。

## Example pattern / 常見範式

Two-string DP (edit distance / delete sum):

```
let mut dp = vec![vec![0i32; n + 1]; m + 1];
for i in 1..=m {
    dp[i][0] = dp[i - 1][0] + cost_a[i - 1];
}
for j in 1..=n {
    dp[0][j] = dp[0][j - 1] + cost_b[j - 1];
}
```

## Prefix arrays / 前綴陣列

- 2D arrays are also used for row/column/diagonal prefix sums in grids.
  / 二維陣列也常用來存放列/欄/對角線前綴和。

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

## Memory sizing / 記憶體估算

- Roughly `m * n * sizeof(T)`; for `i32`, that's `4 * m * n` bytes.
  / 大約 `m * n * sizeof(T)`；若用 `i32`，約 `4 * m * n` bytes。
- Consider rolling array if `m` and `n` are near constraints.
  / 若 `m`、`n` 接近上限，請考慮滾動陣列。

## Pitfalls / 常見陷阱

- Memory can be large for big `m, n`; consider compression.
  / `m, n` 很大時注意記憶體，可做壓縮。
- Mixing in empty-state values can break non-empty constraints.
  / 若有非空限制，別讓空狀態值混入。

## Related problems / 相關題目

- `leetcode/q1895.md`
- `leetcode/q712.md`
- `leetcode/q1458.md`
