---
title: "Bitwise OR With Next Integer / 與下一個整數的位元 OR"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(bit-length)
complexity_space: O(1)
---
# Bitwise OR With Next Integer / 與下一個整數的位元 OR

Goal: reason about `x OR (x + 1)` and invert it for the minimum `x`.
目標：分析 `x OR (x + 1)`，並反推最小的 `x`。

## Observation / 性質

- Let `k` be the index of the least significant `0` in `x` (bits `0..k-1` are `1` and bit `k` is `0`).
  / 設 `x` 的最低位 `0` 在第 `k` 位（`0..k-1` 都是 `1`，第 `k` 位是 `0`）。
- `x + 1` flips the lower `1`s to `0` and turns bit `k` to `1`.
  / `x + 1` 會把低位的連續 `1` 變成 `0`，並把第 `k` 位變成 `1`。
- Therefore `x OR (x + 1)` keeps higher bits unchanged, sets bit `k` to `1`, and forces bits `0..k-1` to `1`.
  / 因此 `x OR (x + 1)` 的高位不變，第 `k` 位變 `1`，更低位全部變 `1`。
- The result always ends with a suffix of `1`s, so it is always odd.
  / 結果一定以一段連續 `1` 結尾，因此必為奇數。

## Inversion: minimum `x` for target `y` / 反推最小 `x`

- If `y` is even, no solution exists.
  / `y` 為偶數時無解。
- Let `L` be the length of trailing `1`s in `y`.
  / 令 `L` 為 `y` 尾端連續 `1` 的長度。
- Any valid `x` equals `y` with one bit within that trailing-`1` suffix cleared to `0`.
  / 任一可行 `x` 都是把這段尾端 `1` 中的某一位清成 `0`。
- To minimize `x`, clear the most significant bit in that suffix:
  / 要使 `x` 最小，應清掉這段連續 `1` 中最高位：

```
x = y - 2^(L-1)
```

## Procedure / 流程

1. If `y` is even, return `-1`.
   / `y` 為偶數直接回傳 `-1`。
2. Count trailing `1`s to get `L`.
   / 計算尾端連續 `1` 的長度 `L`。
3. Return `y - 2^(L-1)`.
   / 回傳 `y - 2^(L-1)`。

## Worked Examples / 範例

`y = 13 (1101b)`

- trailing `1`s: `L = 1`
- `x = 13 - 2^0 = 12`
- `12 OR 13 = 13`

`y = 7 (111b)`

- trailing `1`s: `L = 3`
- `x = 7 - 2^2 = 3`
- `3 OR 4 = 7`

## Complexity / 複雜度

- Time: `O(bit-length)` per number.
  / 每個數 `O(bit-length)`。
- Space: `O(1)`.
  / 空間 `O(1)`。

## Pitfalls / 常見陷阱

- `y` must be odd, otherwise there is no valid `x`.
  / `y` 必須為奇數，偶數無解。
- `L >= 1` for odd `y`, so avoid shifting by a negative count.
  / 奇數 `y` 的 `L >= 1`，避免位移負值。
- Use an unsigned shift count in code.
  / 位移次數用無號型別。

## Rust snippet / Rust 範例

```rust
fn min_x(y: i32) -> i32 {
    if y & 1 == 0 {
        return -1;
    }
    let mut t = y;
    let mut len: u32 = 0;
    while t & 1 == 1 {
        len += 1;
        t >>= 1;
    }
    y - (1i32 << (len - 1))
}
```

## Related problems / 相關題目

- [q3314](../leetcode/q3314.md)
