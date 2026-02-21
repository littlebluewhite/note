---
title: Small Prime Lookup Table / 小範圍質數查表
note_type: knowledge
domain: data_structure
tags: [knowledge, data_structure]
created: 2026-02-21
updated: 2026-02-21
status: active
source: knowledge
complexity_time: O(1) per lookup
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-03-07
---
# Small Prime Lookup Table / 小範圍質數查表

## Purpose / 目的

Store primality for a tiny fixed integer range (e.g., `0..20`) and answer `is_prime(k)` in constant time.
針對很小且固定的整數範圍（例如 `0..20`）預存質數資訊，以常數時間完成 `is_prime(k)` 查詢。

## Core Idea / 核心概念

- When query domain is tiny, use precomputed membership instead of runtime trial division.
  / 當查詢值域很小時，用預先建好的成員查表，取代每次動態試除。
- Two common representations:
  / 常見表示法有兩種：
  - Boolean array: `prime[k]`.
  - Bitmask integer: bit `k` means whether `k` is prime.

## Operations / 操作

- Build (constant literals for small range):
  / 建立（小範圍可直接寫常數）：
  - Array: `let prime = [false, false, true, true, ...];`
  - Bitmask: `mask |= 1 << p` for each prime `p`.
- Query:
  / 查詢：
  - Array: `prime[k as usize]`
  - Bitmask: `((mask >> k) & 1) == 1`

## When to Use / 使用時機

- Query values are guaranteed inside a tiny bound.
  / 查詢值有明確且很小的上界。
- Same lookup happens many times in loops.
  / 迴圈內需重複做大量相同查詢。
- You want branch-light and cache-friendly checks.
  / 需要分支少、常數低的判斷。

## Worked Example / 實作範例

For LeetCode 762 (`right <= 10^6`), `popcount(x)` is at most `20`.
在 LeetCode 762（`right <= 10^6`）中，`popcount(x)` 最大只到 `20`。

Primes in `0..20` are:
`0..20` 的質數為：

`2, 3, 5, 7, 11, 13, 17, 19`

Bitmask approach in Rust:

```rust
const PRIME_MASK: i32 = (1 << 2)
    | (1 << 3)
    | (1 << 5)
    | (1 << 7)
    | (1 << 11)
    | (1 << 13)
    | (1 << 17)
    | (1 << 19);

fn is_prime_small(k: i32) -> bool {
    ((PRIME_MASK >> k) & 1) == 1
}
```

## Variations / 變化型

- `bool` array for readability.
  / 用布林陣列提升可讀性。
- Bitmask for compact constant and low overhead.
  / 用 bitmask 壓縮空間並降低常數。
- Hash set (usually unnecessary for tiny contiguous domains).
  / HashSet（通常只在非連續或不規則值域才有意義）。

## Complexity / 複雜度

- Time: `O(1) per lookup`
- Space: `O(1)` for fixed tiny domains

## Pitfalls / 常見陷阱

- Shifting with wrong integer width/type.
  / 位移型別錯誤（例如 signed/unsigned 混用）。
- Forgetting to prove upper bound before hardcoding table.
  / 未先證明查詢上界就硬編碼常數。
- Using table index out of range.
  / 查表索引可能越界。

## Implementation Notes / 實作細節

- Document how the bound is derived (e.g., max popcount).
  / 註明上界來源（例如最大置位數推導）。
- Prefer constants for deterministic behavior in interviews/contests.
  / 面試/競賽情境建議用常數，行為可預期。
- If bounds change, regenerate table rather than patching manually.
  / 若上界改動，應重建整張表而不是手改零碎項目。

## Related Problems / 相關題目

- [q762](../leetcode/q762.md)
- [q401](../leetcode/q401.md)
- [191. Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/)
- [204. Count Primes](https://leetcode.com/problems/count-primes/)
