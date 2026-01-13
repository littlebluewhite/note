# Two-Sequence DP / 雙序列 DP

Goal: optimize answers across two sequences by building a 2D DP over their prefixes.
目標：在兩個序列的前綴上建立二維 DP，計算最佳解。

## When to use / 使用時機

- Problems pairing or aligning two sequences (LCS, edit distance, max dot product).
  / 需要對齊兩個序列（LCS、編輯距離、最大內積）。
- You can choose to skip elements from either sequence.
  / 可以選擇跳過任一序列的元素。
- The optimal answer for prefixes leads to the optimal answer for larger prefixes.
  / 前綴的最佳解可推到更大前綴的最佳解。

## State / 狀態

- `dp[i][j]` = best answer using `a[0..i]` and `b[0..j]`.
  / `dp[i][j]` 表示使用 `a[0..i]` 與 `b[0..j]` 的最佳答案。
- For non-empty constraints, the state always represents a non-empty choice.
  / 若題目要求非空，狀態須維持「非空」定義。

State variants / 狀態變體

- Prefix DP (most common): `dp[i][j]` covers any valid subsequence in the prefixes.
  / 前綴 DP（最常用）：`dp[i][j]` 覆蓋前綴中的任意合法子序列。
- Ending DP: `end[i][j]` must use `a[i]` and `b[j]` as the last pair.
  / 結尾 DP：`end[i][j]` 必須以 `(i, j)` 作為最後配對。

## Transitions / 轉移

Typical choices:

- Skip `a[i]`: use `dp[i-1][j]`.
  / 跳過 `a[i]`：取 `dp[i-1][j]`。
- Skip `b[j]`: use `dp[i][j-1]`.
  / 跳過 `b[j]`：取 `dp[i][j-1]`。
- Pair `a[i]` with `b[j]` (start or extend).
  / 配對 `a[i]` 與 `b[j]`（可當作開始或延伸）。

Example (max dot product of non-empty subsequences):

```
prod = a[i] * b[j]
dp[i][j] = max(
  dp[i-1][j],
  dp[i][j-1],
  prod,
  prod + dp[i-1][j-1]
)
```

## Base cases / 初始條件

- `dp[0][0]` is the direct pairing of the first elements.
  / `dp[0][0]` 直接用第一對元素配對。
- The first row/column only uses previous prefix or direct pairing.
  / 首列或首欄只能從前一格或直接配對取得。

## Answer location / 答案位置

- Prefix DP: answer is usually `dp[m-1][n-1]`.
  / 前綴 DP：答案通常在 `dp[m-1][n-1]`。
- Ending DP: answer is often `max(end[i][j])`.
  / 結尾 DP：答案常是所有 `end[i][j]` 的最大值。

## Order / 計算順序

- Row-major or column-major as long as `dp[i-1][j]`, `dp[i][j-1]`, `dp[i-1][j-1]` are ready.
  / 只要依賴的三個方向已計算完成，行優先或列優先皆可。

## Complexity / 複雜度

- Time: `O(mn)`.
  / 時間：`O(mn)`。
- Space: `O(mn)`, can be reduced to `O(n)` with rolling arrays.
  / 空間：`O(mn)`，可用滾動陣列壓到 `O(n)`。

## Pitfalls / 常見陷阱

- Non-empty requirement: do not allow empty subsequences to contribute `0`.
  / 非空限制：避免空序列用 `0` 混入比較。
- Negative values: keep the single-pair candidate.
  / 全為負時要保留「只選一對」的候選。
- Overflow: use a safe sentinel if you need `-inf`.
  / 若需 `-inf`，請用安全範圍避免溢位。

## Related problems / 相關題目

- `leetcode/q1458.md`
- [1143. Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/)
- [1035. Uncrossed Lines](https://leetcode.com/problems/uncrossed-lines/)
- [72. Edit Distance](https://leetcode.com/problems/edit-distance/)