---
title: Bounded Enumeration + Popcount Filter / 有界枚舉 + 位元計數篩選
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-17
updated: 2026-02-17
status: active
source: algorithm
complexity_time: O(|A|*|B|)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-03-03
---
# Bounded Enumeration + Popcount Filter / 有界枚舉 + 位元計數篩選

## Goal

Enumerate all candidates in a small bounded search space, then keep only those whose bit-count feature matches a target.
在「範圍小且固定」的搜尋空間中完整枚舉，再用位元 1 的個數（popcount）作為條件篩選。

## When to Use

- Candidate space is small enough to brute-force directly.
  / 候選空間夠小，暴力枚舉成本可接受。
- Constraint can be computed quickly by bit operations.
  / 篩選條件可透過位元運算快速計算。
- You need all valid outputs, not just one optimum.
  / 目標是收集所有合法解，而非只找最佳解。

## Core Idea

- Split the domain into bounded ranges (e.g., hour `0..11`, minute `0..59`).
  / 將問題拆成有限區間（例如小時 `0..11`、分鐘 `0..59`）。
- For each candidate, compute `popcount(part1) + popcount(part2)`.
  / 對每個候選值計算 `popcount(part1) + popcount(part2)`。
- Keep candidate iff the sum equals target.
  / 僅保留總和等於目標值的候選。

## Steps

1. Define bounded domains `A` and `B`.
   / 定義有限搜尋域 `A` 與 `B`。
2. Loop over every pair `(a, b)`.
   / 枚舉所有 `(a, b)`。
3. Compute `score = popcount(a) + popcount(b)`.
   / 計算 `score = popcount(a) + popcount(b)`。
4. If `score == target`, serialize/record the answer.
   / 若 `score == target`，就格式化並收集答案。
5. Return all collected results.
   / 回傳結果集合。

## Complexity

- Time: `O(|A|*|B|)`
- Space: `O(1)` (excluding output)

For Binary Watch:
對 Binary Watch 而言：

- `|A|=12`, `|B|=60`, so `12*60=720` checks.
- 屬固定常數，因此實務與理論上都可視為 `O(1)`。

## Pitfalls

- Over-optimizing with DFS/backtracking when brute force is already tiny.
  / 空間很小時硬上回溯，反而增加複雜度。
- Wrong output formatting (`hour` no leading zero, `minute` must be two digits).
  / 格式化錯誤（小時不可補零、分鐘必須兩位）。
- Mixing signed/unsigned bit operations causing unnecessary casts.
  / 有號/無號混用造成不必要轉型與 bug 風險。

## Examples

Binary Watch (`turnedOn = 1`):
Binary Watch（`turnedOn = 1`）：

- Candidate `0:01` -> `popcount(0)=0`, `popcount(1)=1`, total `1` -> keep.
- Candidate `1:00` -> `1 + 0 = 1` -> keep.
- Candidate `3:00` -> `2 + 0 = 2` -> discard.

Rust snippet:

```rust
fn read_binary_watch(turned_on: i32) -> Vec<String> {
    let mut ans = Vec::new();
    let target = turned_on as u32;
    for h in 0..12u32 {
        for m in 0..60u32 {
            if h.count_ones() + m.count_ones() == target {
                ans.push(format!("{}:{:02}", h, m));
            }
        }
    }
    ans
}
```

## Notes

- This pattern is a practical "enumerate then filter" baseline.
  / 這是「先枚舉、再過濾」的實用基線策略。
- If range grows large, move to combinatorics, DP, or bitset acceleration.
  / 若搜尋域變大，應考慮組合計數、DP 或 bitset 加速。

## Related

- [q401](../leetcode/q401.md)
- [q190](../leetcode/q190.md)
- [191. Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/)
- [338. Counting Bits](https://leetcode.com/problems/counting-bits/)
