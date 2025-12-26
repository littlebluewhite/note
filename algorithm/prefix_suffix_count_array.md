# Prefix/Suffix Count Array / 前後綴計數陣列

Goal: store counts for prefixes and suffixes so split queries are `O(1)`.
目標：保存前後綴計數，讓切點查詢維持 `O(1)`。

## Core structure / 核心結構

- `prefix[0] = 0`, `prefix[i + 1] = prefix[i] + is_left_bad(a[i])`.
  / `prefix[0] = 0`，`prefix[i + 1] = prefix[i] + 判斷函式`。
- `suffix[n] = 0`, `suffix[i] = suffix[i + 1] + is_right_bad(a[i])`.
  / `suffix[n] = 0`，`suffix[i] = suffix[i + 1] + 判斷函式`。
- Arrays are length `n + 1` to keep the base values.
  / 陣列長度 `n + 1` 以保留基底值。

## Typical operations / 常見操作

- Prefix count up to `j` (exclusive): `prefix[j]`.
  / 取得長度 `j` 的前綴計數。
- Suffix count from `j` (inclusive): `suffix[j]`.
  / 取得從 `j` 開始的後綴計數。
- Split cost: `prefix[j] + suffix[j]`.
  / 切點成本 = `prefix[j] + suffix[j]`。

## Example / 範例

String: `Y N Y N` (index 0..3)

- `prefixN` counts `N` in `[0, j)`: `[0, 0, 1, 1, 2]`
- `suffixY` counts `Y` in `[j, n)`: `[2, 1, 1, 0, 0]`

Closing at `j = 2` -> penalty `prefixN[2] + suffixY[2] = 1 + 1 = 2`.

## When to use / 使用時機

- Any "choose a split point" problem with additive left/right costs.
  / 任何需要切點且成本可拆成左右相加的問題。
- Counting "bad" items on both sides of a boundary.
  / 計算邊界左右兩側的不良項目數。

## Complexity / 複雜度

- Build time: `O(n)`.
  / 建表時間：`O(n)`。
- Query time: `O(1)` per split.
  / 每個切點查詢 `O(1)`。
- Space: `O(n)`.
  / 空間：`O(n)`。

## Pitfalls / 常見陷阱

- Mixing inclusive/exclusive ranges causes off-by-one errors.
  / 前後綴範圍定義不一致容易出錯。
- Do not forget the base slots at `0` and `n`.
  / 記得保留 `0` 與 `n` 的基底位置。

## Related problems / 相關題目

- `leetcode/q2483.md`
