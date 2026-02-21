---
title: Primality Test by Square-Root Trial Division / 根號試除質數判定
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-02-21
updated: 2026-02-21
status: active
source: knowledge
complexity_time: O(sqrt(n))
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-03-07
---
# Primality Test by Square-Root Trial Division / 根號試除質數判定

## Goal

Determine whether an integer `n` is prime using deterministic trial division up to `sqrt(n)`.
用確定性的試除法，在 `sqrt(n)` 內判斷整數 `n` 是否為質數。

## When to Use

- Need primality checks for one/few numbers.
  / 只需對少量數字做質數判定。
- Input numbers are not huge.
  / 輸入數值不大，`O(sqrt(n))` 可接受。
- Simplicity and correctness are more important than asymptotic optimum.
  / 需求偏重可讀性與正確性，不追求最極致複雜度。

## Core Idea

- A composite number has at least one factor `d <= sqrt(n)`.
  / 合數一定存在至少一個因數 `d <= sqrt(n)`。
- So it is enough to test divisibility from `2` to `floor(sqrt(n))`.
  / 因此只需測試 `2..floor(sqrt(n))` 是否可整除。
- If no divisor exists, `n` is prime.
  / 若皆不可整除，`n` 即為質數。

## Steps

1. Handle base cases: `n < 2` is not prime.
   / 基底情況：`n < 2` 不是質數。
2. If `n == 2`, return true; if even and `n > 2`, return false.
   / `n == 2` 為質數；若 `n > 2` 且為偶數，直接不是質數。
3. Try odd divisors `d = 3, 5, 7, ...` while `d * d <= n`.
   / 只試奇數除數 `d`，直到 `d * d > n`。
4. If `n % d == 0`, return false; otherwise true at end.
   / 若找到可整除因數回傳 false，否則最後回傳 true。

## Complexity

- Time: `O(sqrt(n))`
- Space: `O(1)`

## Pitfalls

- Missing edge cases: `0`, `1`, and negatives are not prime.
  / 遺漏 `0`、`1`、負數等邊界情況。
- Potential overflow in `d * d <= n` for large types.
  / `d * d` 可能溢位，必要時改成 `d <= n / d`。
- Testing all integers instead of skipping even divisors.
  / 未略過偶數除數，造成不必要常數成本。

## Examples

- `n = 19`: test `3` only (`3*3 <= 19`, `19 % 3 != 0`), then stop -> prime.
  / `n = 19`：只需檢查 `3`，不可整除，結論為質數。
- `n = 21`: `21 % 3 == 0` -> composite.
  / `n = 21`：可被 `3` 整除，為合數。

Rust snippet:

```rust
fn is_prime(n: i32) -> bool {
    if n < 2 {
        return false;
    }
    if n == 2 {
        return true;
    }
    if n % 2 == 0 {
        return false;
    }
    let mut d = 3;
    while d * d <= n {
        if n % d == 0 {
            return false;
        }
        d += 2;
    }
    true
}
```

## Notes

- If many queries share an upper bound, prefer Sieve of Eratosthenes.
  / 若要大量判定且有共同上界，改用埃式篩更合適。
- For tiny bounded domains, precomputed lookup is even faster.
  / 若值域極小，預先查表比每次試除更快。

## Related

- [q762](../leetcode/q762.md)
- [204. Count Primes](https://leetcode.com/problems/count-primes/)
- [866. Prime Palindrome](https://leetcode.com/problems/prime-palindrome/)
