---
title: Fixed-Width Bitmask Integer / 固定寬度位元遮罩整數
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-17
updated: 2026-02-17
status: active
source: data_structure
complexity_time: O(1) per bit op
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-03-03
---
# Fixed-Width Bitmask Integer / 固定寬度位元遮罩整數

## Purpose / 目的

Represent a small set of binary states inside one integer (`u8/u16/u32/u64`) for compact storage and fast bitwise operations.
將一組 0/1 狀態壓在單一整數（`u8/u16/u32/u64`）中，以更緊湊的記憶體與更快的位元操作處理問題。

## Core Idea / 核心概念

- Bit position `i` corresponds to state/flag `i`.
  / 第 `i` 位代表第 `i` 個狀態或旗標。
- `0` means off/absent, `1` means on/present.
  / 位元 `0` 表示關閉或不存在，`1` 表示開啟或存在。
- One integer can hold many boolean values.
  / 一個整數可以同時承載多個布林狀態。

Example (10 LEDs in Binary Watch):
範例（Binary Watch 共 10 顆 LED）：

- Higher 4 bits can represent hour LEDs.
- Lower 6 bits can represent minute LEDs.

## Operations / 操作

- Test bit `i`: `(x >> i) & 1` / 讀取第 `i` 位。
- Set bit `i`: `x | (1 << i)` / 設為 1。
- Clear bit `i`: `x & !(1 << i)` / 清為 0。
- Toggle bit `i`: `x ^ (1 << i)` / 翻轉。
- Count 1s: `x.count_ones()` / 計算亮燈數（popcount）。

## When to Use / 使用時機

- Number of flags is small and fixed.
  / 狀態數量小且固定。
- Need frequent membership/feature count checks.
  / 需要高頻查詢狀態與計數。
- Want branch-light, constant-time primitive ops.
  / 需要常數時間且分支少的底層操作。

## Worked Example / 實作範例

Binary Watch check:
Binary Watch 判斷：

- `hour = 5` (`0101`), `minute = 18` (`010010`)
- `hour.count_ones() = 2`, `minute.count_ones() = 2`
- Total LEDs on = `4`

If `turnedOn == 4`, then `"5:18"` is valid.
若 `turnedOn == 4`，則 `"5:18"` 為合法時間。

Rust snippet:

```rust
fn leds_on(hour: u32, minute: u32) -> u32 {
    hour.count_ones() + minute.count_ones()
}
```

## Variations / 變化型

- `u8/u16/u32/u64`: choose by required bit width.
  / 依狀態數選擇不同位寬。
- Multi-word bitset (`Vec<u64>`): for larger state spaces.
  / 狀態很多時可改為多字 bitset。
- Language intrinsics (`count_ones`, `leading_zeros`) for hardware-accelerated bit queries.
  / 使用語言內建函式以取得硬體加速的位元查詢。

## Complexity / 複雜度

- Time: `O(1) per bit op`
- Space: `O(1)`

## Pitfalls / 常見陷阱

- Shifting beyond type width is undefined/panicking behavior (depends on language/mode).
  / 位移超過型別寬度可能導致未定義行為或 panic。
- Using signed integers can trigger arithmetic right shift surprises.
  / 用有號整數右移可能出現符號延伸問題。
- Forgetting display formatting requirements even when bit logic is correct.
  / 位元邏輯正確但輸出格式錯誤（如分鐘未補零）。

## Implementation Notes / 實作細節

- Prefer unsigned integers for bit manipulation (`u32`, `u64`).
  / 位元運算建議使用無號整數。
- Keep masks explicit and named when semantics matter.
  / 遮罩建議命名清楚，避免 magic number。
- For readability, isolate bit-logic helper functions.
  / 可將位元判斷封裝成小函式提升可讀性。

## Related Problems / 相關題目

- [q401](../leetcode/q401.md)
- [q190](../leetcode/q190.md)
- [191. Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/)
- [338. Counting Bits](https://leetcode.com/problems/counting-bits/)
