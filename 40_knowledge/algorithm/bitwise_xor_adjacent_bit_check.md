---
title: Adjacent-Bit Alternation Check via XOR / 以 XOR 檢查相鄰位元交替
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-18
updated: 2026-02-18
status: active
source: algorithm
complexity_time: O(w)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-03-04
---
# Adjacent-Bit Alternation Check via XOR / 以 XOR 檢查相鄰位元交替

## Goal

Determine whether a positive integer's binary representation has alternating adjacent bits.
判斷一個正整數的二進位表示是否滿足「相鄰位元交替」。

## When to Use

- Need to verify local bit transitions (`01` / `10`) across all adjacent positions.
  / 需要檢查整段位元中每一對相鄰位是否都為 `01` 或 `10`。
- Prefer branch-light bitwise checks over per-bit loops.
  / 希望用位元運算快速判斷，而不是逐位比較迴圈。
- Input is a fixed-width integer (`u32/u64`).
  / 輸入是固定寬度整數（如 `u32/u64`）。

## Core Idea

Let `x = n ^ (n >> 1)`.
令 `x = n ^ (n >> 1)`。

- XOR compares each bit of `n` with its right neighbor.
  / XOR 會比較 `n` 的每一位與其右側相鄰位。
- If all adjacent bits are different, every compared position becomes `1`.
  / 若相鄰位皆不同，所有被比較的位置都會變成 `1`。
- For positive `n`, this makes `x` a contiguous all-ones pattern: `1, 3, 7, 15, ...`.
  / 對正整數而言，`x` 會成為連續全 1 型態：`1, 3, 7, 15, ...`。

All-ones check:
全 1 判斷式：

`x & (x + 1) == 0`

Because for `x = 2^k - 1`, `x + 1` is `1000...0`, and the AND is zero.
因為 `x = 2^k - 1` 時，`x + 1` 會變成 `1000...0`，兩者 AND 必為 0。

## Steps

1. Compute `x = n ^ (n >> 1)`.
   / 計算 `x = n ^ (n >> 1)`。
2. Return whether `x & (x + 1) == 0`.
   / 回傳 `x & (x + 1) == 0` 是否成立。

## Complexity

- Time: `O(w)` in general bit-width model, `O(1)` for fixed machine word.
- Space: `O(1)`.

## Pitfalls

- Using signed right shift may introduce sign extension for negative values.
  / 使用有號右移在負數情況可能有符號延伸問題。
- This trick assumes positive input as in q693; include explicit handling if `n <= 0` is allowed.
  / 此技巧預設輸入為正數（q693 條件）；若允許 `n <= 0` 需額外處理。
- Mixing integer widths without casts can cause compile errors.
  / 混用不同整數位寬未轉型，容易導致編譯錯誤。

## Examples

- `n = 5 (101)`
  - `n >> 1 = 10`
  - `x = 101 ^ 010 = 111`
  - `x & (x + 1) = 111 & 1000 = 0` -> alternating.

- `n = 7 (111)`
  - `n >> 1 = 11`
  - `x = 111 ^ 011 = 100`
  - `x & (x + 1) = 100 & 101 = 100` -> not alternating.

## Notes

- Alternative method: iteratively compare `(n & 1)` and `((n >> 1) & 1)` for each position.
  / 另一種寫法是逐位比較 `(n & 1)` 與 `((n >> 1) & 1)`。
- XOR + all-ones check is shorter and usually easier to reason about in interviews.
  / XOR 搭配全 1 檢查式通常更精簡，面試情境也更常見。

Rust snippet:

```rust
fn has_alternating_bits(n: u32) -> bool {
    let x = n ^ (n >> 1);
    (x & (x + 1)) == 0
}
```

## Related

- [q693](../leetcode/q693.md)
- [191. Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/)
- [231. Power of Two](https://leetcode.com/problems/power-of-two/)
- [338. Counting Bits](https://leetcode.com/problems/counting-bits/)
