---
title: "Divisor Enumeration by Square Root / 根號枚舉因數"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(sqrt(n))
complexity_space: O(1)
---
# Divisor Enumeration by Square Root / 根號枚舉因數

Goal: enumerate, count, or sum divisors of `n` in `O(sqrt(n))`.
目標：用 `O(sqrt(n))` 枚舉、計數或加總 `n` 的所有因數。

## Thought process / 思路

- Every divisor `d` pairs with `n / d`.
  / 每個因數 `d` 都有對應的配對 `n / d`。
- If `d <= sqrt(n)`, then `n / d >= sqrt(n)`. So we only scan up to `sqrt(n)`.
  / 只要掃到 `sqrt(n)`，就能涵蓋所有配對。

## Pattern / 模式

For `i` from `1` to `floor(sqrt(n))`:
若 `i` 從 `1` 掃到 `floor(sqrt(n))`：

1. If `n % i == 0`, then `i` and `n / i` are divisors.
   / 若 `n % i == 0`，則 `i` 與 `n / i` 都是因數。
2. If `i == n / i`, count once; otherwise count both.
   / 若 `i == n / i` 只算一次，否則算兩個。
3. Optional early exit if divisor count exceeds a limit.
   / 若需要固定個數因數，可超過即提前停止。

## Worked Example / 實作範例

### Example: enumerate divisors of 36 / 範例：枚舉 36 的因數

Pairs found / 配對如下：

- `1 * 36`
- `2 * 18`
- `3 * 12`
- `4 * 9`
- `6 * 6` (square root pair)

Divisors / 因數集合：
`{1, 2, 3, 4, 6, 9, 12, 18, 36}`

### Example: check exactly four divisors / 範例：是否恰好四個因數

`n = 21`:

- `1, 21`
- `3, 7`

Total 4 divisors, sum = `1 + 3 + 7 + 21 = 32`.
總共 4 個因數，總和 `32`。

## Rust snippet / Rust 範例

```rust
fn sum_if_four_divisors(n: i32) -> i32 {
    let n = n as i64;
    let mut count = 0;
    let mut sum = 0i64;
    let mut i = 1i64;
    while i * i <= n {
        if n % i == 0 {
            let j = n / i;
            if i == j {
                count += 1;
                sum += i;
            } else {
                count += 2;
                sum += i + j;
            }
            if count > 4 {
                return 0;
            }
        }
        i += 1;
    }
    if count == 4 { sum as i32 } else { 0 }
}
```

## Variations / 變化型

- Count divisors only: keep `count`, skip `sum`.
  / 只計數因數：保留 `count` 即可。
- Primality test: `n` is prime if no divisor in `[2, sqrt(n)]`.
  / 質數判定：`[2, sqrt(n)]` 無因數則為質數。
- Perfect square detection: check if `i * i == n`.
  / 判斷完全平方數：檢查 `i * i == n`。

## Pitfalls / 常見陷阱

- Overflow: use `i <= n / i` when `n` can be large.
  / 避免溢位：`n` 很大時用 `i <= n / i`。
- `n = 1` has only one divisor.
  / `n = 1` 只有 1 個因數。
- Double counting when `i == n / i`.
  / `i == n / i` 只能算一次。

## Complexity / 複雜度

- Time: `O(sqrt(n))`
- Space: `O(1)`

## Related problems / 相關題目

- [q1390](../leetcode/q1390.md)