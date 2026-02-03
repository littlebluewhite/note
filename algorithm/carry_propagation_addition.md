---
title: "Digit Carry Addition / 數字進位加法"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(n)
complexity_space: O(1)
---
# Digit Carry Addition / 數字進位加法

## Definition / 定義

Add numbers represented as digit arrays by processing from the least significant digit and propagating carry.
將數字表示成陣列時，從最低位開始逐位相加並傳遞進位。

## When to Use / 使用時機

- The number is too large to fit in native integer types.
  / 數值太大無法用內建整數表示。
- Input is given as an array of digits, most-significant to least-significant.
  / 輸入以「最高位在前」的數字陣列表示。

## Pattern / 流程

1. Initialize `carry = 1` (for "+1") or from addition of two digits.
   / 初始化 `carry = 1`（加一）或由兩數相加產生。
2. Traverse digits from the end to the start.
   / 從尾端往前走訪。
3. For each digit: `sum = digit + carry`, set `digit = sum % 10`, `carry = sum / 10`.
   / 每位做 `sum = digit + carry`，更新 `digit = sum % 10`、`carry = sum / 10`。
4. If `carry` remains after the loop, prepend it to the array.
   / 迴圈結束仍有 `carry`，在最前方補上一位。

## Why it Works / 正確性直覺

- Each digit is updated exactly once with the incoming carry, matching manual column addition.
  / 每一位只處理一次並帶入進位，等同手算直式加法。
- Propagating `carry` ensures higher digits reflect overflow from lower digits.
  / 進位向高位傳遞，保證結果正確。

## Complexity / 複雜度

- Time: `O(n)` for `n` digits.
  / 時間：`O(n)`。
- Space: `O(1)` extra if in-place; `O(n)` if a new leading digit is needed.
  / 空間：原地為 `O(1)` 額外空間；需要補位時為 `O(n)`。

## Pitfalls / 常見陷阱

- All digits are `9` → result length increases by 1.
  / 全是 `9` 時結果長度會 +1。
- Input order is most-significant first; must iterate from the end.
  / 輸入是「最高位在前」，必須從尾端開始。
- Avoid leading zeros after the operation.
  / 結果不應有前導零。

## Example / 範例

`[1, 2, 9] + 1 → [1, 3, 0]`

## Related Problems / 相關題目

- [q66](../leetcode/q66.md)