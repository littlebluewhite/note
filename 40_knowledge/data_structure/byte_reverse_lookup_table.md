---
title: Byte Reverse Lookup Table / 位元組反轉查表
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-16
updated: 2026-02-16
status: active
source: data_structure
complexity_time: O(1) query after O(256) preprocess
complexity_space: O(256)
review_interval_days: 14
next_review: 2026-03-02
---
# Byte Reverse Lookup Table / 位元組反轉查表

## Purpose / 目的

Store precomputed reversed bits for every `u8` value (`0..255`) so repeated bit-reversal queries can run with very small constant cost.
預先儲存每個 `u8`（`0..255`）的反轉結果，讓大量位元反轉查詢以更小常數時間完成。

## Core Idea / 核心概念

- A 32-bit integer can be split into 4 bytes.
  / 一個 32-bit 整數可拆成 4 個 byte。
- Reverse each byte by table lookup.
  / 每個 byte 透過查表取得反轉值。
- Swap byte positions when combining because full-bit reversal changes both intra-byte and inter-byte order.
  / 合併時要對調 byte 位置，因為完整位元反轉同時改變 byte 內與 byte 之間順序。

Formula (`b0` low byte ... `b3` high byte):
公式（`b0` 低位 byte，`b3` 高位 byte）：

`rev32 = LUT[b0] << 24 | LUT[b1] << 16 | LUT[b2] << 8 | LUT[b3]`

## Operations / 操作

- Build table: `O(256)` once.
  / 建表一次：`O(256)`。
- Query one 32-bit value: 4 lookups + shifts + OR, `O(1)`.
  / 查一次 32-bit：4 次查表 + 位移 + OR，`O(1)`。
- Extendable to 64-bit with 8 lookups.
  / 可擴展到 64-bit（8 次查表）。

## When to Use / 使用時機

- The same reverse-bits function is called many times.
  / 同一個反轉位元函式會被重複呼叫很多次。
- Throughput matters more than tiny one-time setup cost.
  / 吞吐量重要，且可接受小型一次性預處理成本。
- You want branchless, predictable runtime.
  / 想要更可預測、分支較少的執行成本。

## Worked Example / 實作範例

Input:
`x = 0x12345678`

1. Split bytes:
   - `b0 = 0x78`, `b1 = 0x56`, `b2 = 0x34`, `b3 = 0x12`
2. Lookup:
   - `r0 = LUT[0x78]`, `r1 = LUT[0x56]`, `r2 = LUT[0x34]`, `r3 = LUT[0x12]`
3. Combine with swapped positions:
   - `ans = (r0 << 24) | (r1 << 16) | (r2 << 8) | r3`

This equals full 32-bit bit reversal.
結果即為完整 32-bit 位元反轉。

## Variations / 變化型

- Nibble table (size 16): smaller memory, more operations per query.
  / Nibble 查表（大小 16）：記憶體更小，但單次操作較多。
- 16-bit table (size 65536): fewer operations, larger memory.
  / 16-bit 查表（大小 65536）：操作更少，但記憶體更大。
- CPU intrinsic (`reverse_bits`): depends on language/compiler/platform support.
  / CPU intrinsic（內建反轉）：依語言/編譯器/平台支援而定。

## Complexity / 複雜度

- Preprocess Time: `O(256)`
- Query Time: `O(1)`
- Space: `O(256)`

## Pitfalls / 常見陷阱

- Forgetting to reorder bytes after per-byte reversal.
  / 只做 byte 內反轉卻忘記調整 byte 位置。
- Using signed integer shifts that introduce sign extension.
  / 使用有號位移造成符號延伸。
- Rebuilding LUT on every call instead of one-time initialization.
  / 每次呼叫都重建表，失去優化效果。

## Implementation Notes / 實作細節

- In Rust, use `[u8; 256]` for compact and cache-friendly storage.
  / Rust 建議使用 `[u8; 256]`，快取友善且存取成本低。
- Build LUT with the same shift-mask algorithm for consistency.
  / 建表可沿用 shift-mask 反轉邏輯，行為一致且容易驗證。
- For thread-safe global reuse, prefer `OnceLock<[u8; 256]>` or `lazy_static`.
  / 若要全域重用且執行緒安全，可用 `OnceLock<[u8; 256]>` 或 `lazy_static`。

Rust snippet:

```rust
fn build_lut() -> [u8; 256] {
    let mut lut = [0u8; 256];
    for i in 0..256u32 {
        let mut x = i as u8;
        let mut r = 0u8;
        for _ in 0..8 {
            r = (r << 1) | (x & 1);
            x >>= 1;
        }
        lut[i as usize] = r;
    }
    lut
}
```

## Related Problems / 相關題目

- [q190](../leetcode/q190.md)
- [832. Flipping an Image](https://leetcode.com/problems/flipping-an-image/)
- [1009. Complement of Base 10 Integer](https://leetcode.com/problems/complement-of-base-10-integer/)
