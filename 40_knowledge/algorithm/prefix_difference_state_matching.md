---
title: Prefix Difference State Matching / 前綴差分狀態匹配
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-02-13
updated: 2026-02-13
status: active
source: knowledge
complexity_time: O(k n)
complexity_space: O(k n)
review_interval_days: 14
next_review: 2026-02-27
---
# Prefix Difference State Matching / 前綴差分狀態匹配

## Goal

Transform substring constraints of the form "multiple counters are equal / unchanged" into prefix-state equality, so longest-valid-substring can be found in one pass.
把「多個計數要相等／某些計數要不變」的子字串條件，轉成「前綴狀態相同」，用單次掃描找最長合法子字串。

## When to Use

- Substring validity can be expressed as linear equalities over counts.
  / 子字串合法條件可寫成計數的線性等式。
- Need longest interval under those equalities.
  / 目標是最長區間。
- Alphabet / category count is small, so the number of state-forms is small (`k` forms).
  / 類別數不大，狀態形式數量 `k` 可控。

## Core Idea

Let prefix counts at position `i` be `P(i)`.
If substring `(l, r]` must satisfy some relation `F(P(r) - P(l)) = 0`, rewrite it into:

`G(P(r)) == G(P(l))`

Then for each transformed state `state = G(P(i))`:

- first time seen -> store earliest index.
- seen before -> candidate length is `i - earliest[state]`.

For multiple constraint families, run the same logic with multiple transforms `G1..Gk` and take max.

## Steps

1. Define one or more prefix-state transforms `G` that are equivalent to validity.
2. Initialize hash map(s) with empty prefix (`i=0`) state.
3. Scan string/array once, update raw counts.
4. Compute transformed state(s) at each prefix index `i`.
5. For each state:
   - if existed: update answer by distance to earliest index;
   - else: record earliest index.

## Complexity
- Time: `O(k n)`
- Space: `O(k n)`

## Pitfalls

- Forgetting to insert empty-prefix state (`i = 0`) causes missing answers starting at index 0.
  / 漏掉空前綴會錯過從起點開始的合法區間。
- Overwriting earliest index breaks maximal-length guarantee.
  / 不能覆蓋最早位置，否則最長答案會變短。
- Wrong index convention (`prefix index` vs `array index`) causes off-by-one errors.
  / 前綴索引與原陣列索引混用容易錯一位。
- State transform must be mathematically equivalent to original constraints.
  / 狀態轉換若不等價會得到錯誤答案。

## Examples

For `s` over `a/b/c`, suppose we need substring with equal counts of `a,b,c`:

- Prefix counts at `i`: `(A, B, C)`.
- Valid `(l, r]` iff `A_r - A_l = B_r - B_l = C_r - C_l`.
- Equivalent transformed state:
  - `(A - B, A - C)` equal at both ends.

So longest valid substring reduces to longest distance between equal `(A-B, A-C)` prefix states.

## Notes

- This is a "prefix-hash state" pattern; it generalizes `0/1 equal count` and multi-category equal-count problems.
  / 這是前綴狀態雜湊技巧，可泛化到兩類與多類等量問題。
- If `k` is constant and small, linear-time performance is practical.
  / 當 `k` 為小常數時，實務上可視為 `O(n)`。

## Related

- [q3714](../leetcode/q3714.md)
- [q3713](../leetcode/q3713.md)
- [earliest_index_state_hash_map](../data_structure/earliest_index_state_hash_map.md)
