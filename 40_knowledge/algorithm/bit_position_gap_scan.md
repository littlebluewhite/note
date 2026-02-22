---
title: Bit Position Gap Scan / 位元位置間距掃描
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-02-22
updated: 2026-02-22
status: active
source: knowledge
complexity_time: O(w)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-03-08
---
# Bit Position Gap Scan / 位元位置間距掃描

## Goal

Scan a binary representation once and compute distances between consecutive set bits (`1`), usually to get the maximum gap.
單次掃描二進位位元，計算相鄰 `1` 的距離，常用於求最大間距。

## When to Use

- Need distances between consecutive marked positions in a bit sequence.
  / 需要計算位元序列中相鄰標記位置（`1`）的距離。
- Input is an integer and bit operations are preferred over string conversion.
  / 輸入是整數，偏好位元運算而非轉字串。
- Only local adjacency is needed, not all pairwise distances.
  / 只關心相鄰關係，不需要所有配對距離。

## Core Idea

- Keep a running bit index `pos` while shifting `x` right.
  / 用 `pos` 記錄目前掃描位元索引，並持續右移 `x`。
- Maintain `last_one`: the most recent position where bit is `1`.
  / 維護最近一次看到 `1` 的位置 `last_one`。
- On each new `1`, distance to previous adjacent `1` is `pos - last_one`.
  / 每遇到新 `1`，和前一個相鄰 `1` 的距離就是 `pos - last_one`。
- Update global answer (max/min depending on problem goal).
  / 依題目需求更新全域答案（常見是最大值）。

## Steps

1. Initialize `x = n`, `pos = 0`, `last_one = None`, `ans = 0`.
   / 初始化 `x = n`、`pos = 0`、`last_one = None`、`ans = 0`。
2. While `x > 0`:
   / 當 `x > 0` 時重複：
   - If `(x & 1) == 1`, then:
     / 若最低位是 `1`：
     - If `last_one` exists, compute `gap = pos - last_one` and update `ans`.
       / 若 `last_one` 已存在，計算 `gap = pos - last_one` 並更新答案。
     - Set `last_one = pos`.
       / 設定 `last_one = pos`。
   - Shift right: `x >>= 1`.
     / 右移一位：`x >>= 1`。
   - Move index: `pos += 1`.
     / 位元索引加一：`pos += 1`。
3. Return `ans`.
   / 回傳 `ans`。

## Complexity
- Time: `O(w)` where `w` is the number of scanned bits (`O(log n)` for value-based bound).
- Space: `O(1)`.

## Pitfalls

- Forgetting to update `last_one` after processing a `1`.
  / 遇到 `1` 後忘記更新 `last_one` 會導致後續距離錯誤。
- Using signed shifts carelessly for negative values.
  / 對有號負數做位移可能引入符號延伸；通常用 `u32/u64` 較安全。
- Confusing "adjacent ones" with "any two ones".
  / 把「相鄰 `1`」誤解成「任意兩個 `1`」會得到錯誤答案。

## Examples

Example: `n = 22`, binary `10110`
範例：`n = 22`，二進位 `10110`

Bit scan (LSB -> MSB):
逐位掃描（低位到高位）：

```
pos | bit | last_one(before) | gap | ans
----+-----+-------------------+-----+----
0   | 0   | -                 | -   | 0
1   | 1   | None              | -   | 0
2   | 1   | 1                 | 1   | 1
3   | 0   | 2                 | -   | 1
4   | 1   | 2                 | 2   | 2
```

Return `2`.
回傳 `2`。

Rust snippet:

```rust
fn binary_gap(mut x: u32) -> i32 {
    let mut pos = 0i32;
    let mut last_one: Option<i32> = None;
    let mut ans = 0i32;
    while x > 0 {
        if (x & 1) == 1 {
            if let Some(prev) = last_one {
                ans = ans.max(pos - prev);
            }
            last_one = Some(pos);
        }
        x >>= 1;
        pos += 1;
    }
    ans
}
```

## Notes

- If the integer width is fixed (e.g., 32-bit), runtime is effectively constant.
  / 若整數位寬固定（如 32-bit），實務上可視為常數時間。
- This pattern generalizes to any "distance between consecutive markers" stream scan.
  / 這個模式可泛化到所有「相鄰標記距離」的串流掃描題。

## Related

- [q868](../leetcode/q868.md)
- [q693](../leetcode/q693.md)
- [191. Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/)
