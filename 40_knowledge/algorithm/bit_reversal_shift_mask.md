---
title: Bit Reversal by Shift and Mask / 以位移與遮罩反轉位元
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-16
updated: 2026-02-16
status: active
source: algorithm
complexity_time: O(w)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-03-02
---
# Bit Reversal by Shift and Mask / 以位移與遮罩反轉位元

## Goal

Reverse the bit order of a fixed-width integer (e.g., 32-bit).
將固定寬度整數（例如 32-bit）的位元順序完全反轉。

## When to Use

- Need exact bit-order reversal for encoding, hashing, or bit-level transforms.
  / 需要做精確的位元順序反轉（編碼、雜湊、低階位元轉換）。
- Width is fixed and small (`8/16/32/64`), so a direct loop is simple and reliable.
  / 位寬固定且不大（`8/16/32/64`），直接迴圈實作最直觀穩定。
- Interview/LeetCode bit manipulation tasks.
  / 面試與 LeetCode 的位元操作題型。

## Core Idea

- Read source bits from least-significant to most-significant.
  / 從來源數字的最低位一路讀到最高位。
- Build result from left to right: shift result left, then append extracted low bit.
  / 目標值每回合先左移，再把取出的最低位補進去。
- Repeat exactly `w` times (`w` = bit width), guaranteeing all bits are handled.
  / 固定做 `w` 次（`w` 為位寬），確保每個位元都被處理。

Recurrence:
遞推式：

`ans = (ans << 1) | (x & 1)` and `x >>= 1`

## Steps

1. Initialize `ans = 0`.
   / 初始化 `ans = 0`。
2. For `i` in `0..w`:
   / 對 `i` 從 `0` 到 `w-1`：
   - Extract low bit: `b = x & 1`.
     / 取最低位：`b = x & 1`。
   - Shift target: `ans <<= 1`.
     / 目標左移一位：`ans <<= 1`。
   - Append bit: `ans |= b`.
     / 補上此 bit：`ans |= b`。
   - Consume source bit: `x >>= 1`.
     / 來源右移一位：`x >>= 1`。
3. Return `ans`.
   / 回傳 `ans`。

## Complexity

- Time: `O(w)` (for 32-bit, this is constant `O(1)`).
- Space: `O(1)`.

## Pitfalls

- Using signed right shift accidentally (`i32 >>`) can introduce sign bits.
  / 不小心用有號型別右移會發生符號延伸，造成高位污染。
- Looping fewer than `w` times drops leading zeros in the reversed result.
  / 若迴圈次數少於 `w`，反轉後的前導 0 會被錯誤遺失。
- Mixing integer widths (`u32` with `u64`) without explicit casts.
  / 混用不同位寬整數未轉型，可能造成編譯錯誤或隱性 bug。

## Examples

Example (`w = 8`):
範例（`w = 8`）：

`x = 00010110` (22)

- step1: `ans=00000000`, low bit `0` -> `ans=00000000`
- step2: low bit `1` -> `ans=00000001`
- step3: low bit `1` -> `ans=00000011`
- ...
- final: `ans=01101000` (104)

## Notes

- For high-frequency calls, combine with byte-level lookup table to reduce per-call operations.
  / 若函式會被大量重複呼叫，可改用 byte 查表降低單次常數成本。
- Native intrinsics (if available) may outperform manual loops in systems code.
  / 在系統程式中可考慮平台內建 intrinsic 取得更好常數。

Rust snippet:

```rust
fn reverse_bits_u32(mut x: u32) -> u32 {
    let mut ans = 0u32;
    for _ in 0..32 {
        ans = (ans << 1) | (x & 1);
        x >>= 1;
    }
    ans
}
```

## Related

- [q190](../leetcode/q190.md)
- [191. Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/)
- [338. Counting Bits](https://leetcode.com/problems/counting-bits/)
