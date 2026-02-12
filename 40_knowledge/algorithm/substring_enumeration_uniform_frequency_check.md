---
title: Substring Enumeration with Uniform Frequency Check / 子字串枚舉與等頻檢查
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-02-12
updated: 2026-02-12
status: active
source: knowledge
complexity_time: O(n^2)
complexity_space: O(A)
review_interval_days: 14
next_review: 2026-02-26
---
# Substring Enumeration with Uniform Frequency Check / 子字串枚舉與等頻檢查

## Goal

Find the longest substring where all distinct symbols appear the same number of times, using incremental updates instead of recomputing full frequency histograms each time.
在不重算完整頻率分布的前提下，找出「所有不同字元出現次數相同」的最長子字串。

## When to Use

- String or array length is around `10^3` and `O(n^2)` is acceptable.
  / 長度約 `10^3`，可接受平方時間。
- Alphabet/value domain is small and fixed (`A` small, e.g., 26 lowercase letters).
  / 值域固定且小（例如 26 個小寫字母）。
- Need exact longest valid substring, not approximate.
  / 需要精確最長答案。

## Core Idea

Fix left boundary `l`, extend right boundary `r` one step at a time, and maintain:

- `freq[x]`: occurrence count of symbol `x` in current window.
- `distinct`: number of symbols with positive frequency.
- `max_freq`: maximum frequency among symbols in window.

Let `len = r - l + 1`. The window is balanced iff:

`len == distinct * max_freq`

Why this works:

- For all present symbols, `freq_i <= max_freq`.
- Summing gives `len = sum(freq_i) <= distinct * max_freq`.
- Equality holds only when every present symbol has frequency exactly `max_freq`.

So we can test balance in `O(1)` per expansion.

## Steps

1. Initialize answer `ans = 0`.
2. For each left boundary `l` from `0..n-1`:
   - reset `freq`, `distinct`, `max_freq`.
3. For each right boundary `r` from `l..n-1`:
   - update `freq[s[r]]`;
   - if it becomes first occurrence, increase `distinct`;
   - update `max_freq`;
   - compute `len`, and if `len == distinct * max_freq`, update `ans`.
4. Return `ans`.

## Complexity
- Time: `O(n^2)` (each pair `(l, r)` processed once)
- Space: `O(A)` (`A` = alphabet size)

## Pitfalls

- Forgetting to reset `freq/distinct/max_freq` when `l` moves.
  / 左端點改變時沒重設狀態會污染答案。
- Using this directly when alphabet is huge can make memory/time constants poor.
  / 字元集合過大時常數會變差。
- Off-by-one in substring length (`r - l + 1`).
  / 常見長度邊界錯誤。
- If symbols can be outside expected domain, add mapping or bounds checks first.
  / 若值不在固定域內，需先做映射。

## Examples

Given `s = "abbac"`:

- `l = 0`, extend `r`:
  - `r = 0` -> `"a"`: `len=1, distinct=1, max=1`, valid.
  - `r = 1` -> `"ab"`: `len=2, distinct=2, max=1`, valid.
  - `r = 2` -> `"abb"`: `len=3, distinct=2, max=2`, invalid.
  - `r = 3` -> `"abba"`: `len=4, distinct=2, max=2`, valid (best = 4).

## Notes

- This pattern is often faster than checking all non-zero frequencies each step.
  / 比起每步掃描全部字元次數，常數更小。
- For lowercase letters, using `[usize; 26]` is cache-friendly and allocation-free.
  / 使用固定長度陣列可避免雜湊開銷。

## Related

- [fixed_alphabet_frequency_array](../data_structure/fixed_alphabet_frequency_array.md)
- [q3713](../leetcode/q3713.md)
