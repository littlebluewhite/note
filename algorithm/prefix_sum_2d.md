# 2D Prefix Sum / 二維前綴和

Goal: answer any submatrix sum query in `O(1)` after `O(mn)` preprocessing.
目標：先做 `O(mn)` 預處理後，任意子矩陣和可在 `O(1)` 查詢。

## Definition / 定義

Let `pref` be `(m + 1) x (n + 1)` with a zero top row and left column.
`pref` 為 `(m + 1) x (n + 1)`，最上列與最左欄為 0。

- `pref[r + 1][c + 1] = mat[r][c] + pref[r][c + 1] + pref[r + 1][c] - pref[r][c]`
- Sum of rectangle `[r1, r2) x [c1, c2)`:
  `pref[r2][c2] - pref[r1][c2] - pref[r2][c1] + pref[r1][c1]`

## Why it works / 為什麼可行

Each `pref[r + 1][c + 1]` stores the sum of the rectangle from `(0,0)` to `(r,c)`.
When querying a sub-rectangle, we add the full prefix, subtract two overlaps, and add back the double-subtracted corner.
`pref[r + 1][c + 1]` 代表從 `(0,0)` 到 `(r,c)` 的總和。
查子矩形時，加上完整前綴、扣掉兩塊重疊，再補回被扣兩次的角落。

## Example / 範例

Matrix:

```
2 1 3
4 0 2
```

Build `pref` (size `3 x 4`):

```
0 0 0 0
0 2 3 6
0 6 7 12
```

Sum of rectangle rows `[0,2)`, cols `[1,3)` (values `1,3,0,2`) =
`pref[2][3] - pref[0][3] - pref[2][1] + pref[0][1] = 12 - 0 - 6 + 0 = 6`.

## Implementation notes / 實作提醒

- Use `i64` if values or areas can overflow `i32`.
  / 若數值或面積較大，請用 `i64`。
- Always allocate with `m + 1` and `n + 1` to simplify boundaries.
  / 建議多一列一欄，邊界更好處理。
- Be explicit about half-open intervals `[r1, r2)` to avoid off-by-one.
  / 用半開區間可避免 off-by-one。

## Complexity / 複雜度

- Preprocessing: `O(mn)`
- Query: `O(1)`
- Space: `O(mn)`

## Related problems / 相關題目

- `leetcode/q1292.md`
