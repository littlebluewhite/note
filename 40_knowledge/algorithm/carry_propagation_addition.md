---
title: Carry Propagation Addition / 進位傳播加法
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-15
status: active
source: algorithm
complexity_time: O(max(n, m))
complexity_space: O(1) extra (excluding output)
review_interval_days: 14
next_review: 2026-03-01
---
# Carry Propagation Addition / 進位傳播加法

## Goal

Compute the sum of two large numbers represented as digit sequences (array/string) without converting to built-in integer types.
在不轉成內建整數型別的前提下，計算兩個以位數序列（陣列/字串）表示的大數加總。

## When to Use

- Input size can exceed native integer ranges.
  / 輸入長度可能超過內建整數可表示範圍。
- Numbers are provided as strings or digit arrays.
  / 數字以字串或位數陣列形式提供。
- Need deterministic `O(n)` simulation close to manual column addition.
  / 需要與手算直式一致、可線性處理的流程。

## Core Idea

- Process from least-significant digit to most-significant digit.
  / 從最低位往最高位逐位處理。
- At each position in base `B`:
  - `sum = x + y + carry`
  - `digit = sum % B`
  - `carry = sum / B`
- Binary addition is the same pattern with `B = 2`; decimal is `B = 10`.
  / 二進位加法是 `B = 2`，十進位加法是 `B = 10`，規則完全一致。

## Steps

1. Initialize pointers at the end of both sequences and set `carry = 0`.
2. While any pointer is valid or `carry > 0`:
   - Read current digit from each side (or `0` if exhausted).
   - Compute `sum` and append `sum % base` to output.
   - Update `carry = sum / base`.
   - Move pointers left.
3. If output was built from low to high digits, reverse once at the end.
4. Convert output to required format (string or digit array).

## Complexity

- Time: `O(max(n, m))`
- Space:
  - `O(1)` extra when mutating in place and output reuse is allowed.
  - `O(max(n, m))` when building a new result container.

## Pitfalls

- Forgetting the final carry (e.g., `1 + 1 -> 10`).
  / 漏掉最後進位會造成答案長度少一位。
- Mixing character codes and numeric digits incorrectly.
  / 字元與數值轉換錯誤常導致 off-by-one。
- Building result from right to left but forgetting to reverse.
  / 從低位累積結果後忘記反轉。
- Assuming equal lengths without zero-padding logic.
  / 忽略長度不同情況會漏算高位。

## Examples

Binary (`base = 2`):
`a = "1010"`, `b = "1011"` -> `"10101"`.

Decimal (`base = 10`):
`[9, 9, 9] + [1]` -> `[1, 0, 0, 0]`.

## Notes

- This is a reusable primitive for:
  - plus-one style updates,
  - big integer string addition,
  - arbitrary-base positional arithmetic.
- Many "string math" problems can be reduced to this exact state machine:
  - two moving pointers,
  - one carry state,
  - one output buffer.

## Related Problems / 相關題目

- [q66](../leetcode/q66.md)
- [q67](../leetcode/q67.md)
