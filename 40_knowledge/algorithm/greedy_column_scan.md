---
title: Greedy Column Scan for Lexicographic Order / 欄位貪心掃描
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(n * m)
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
canonical: algorithm/greedy_column_scan.md
---
# Greedy Column Scan for Lexicographic Order / 欄位貪心掃描

Goal: minimize the number of deleted columns so row strings become nondecreasing lexicographically.
目標：最少刪除欄位，使每一列字串按字典序非遞減。

## Key idea / 核心想法

- Scan columns left to right and decide keep/delete immediately.
  / 由左到右掃描欄位，當下決定保留或刪除。
- Keep a state array for adjacent rows that are already strictly ordered.
  / 用狀態陣列記錄相鄰列是否已被前面欄位嚴格決定順序。

## Pattern / 流程

1. Initialize `sorted[i] = false` for each adjacent pair `(i, i+1)`.
   / 初始化相鄰列狀態。
2. For each column `c` from left to right:
   / 逐欄掃描：
   - If any unresolved pair has `row[i][c] > row[i+1][c]`, delete column `c`.
     / 若尚未確定順序的相鄰列出現逆序，必須刪除該欄。
   - Otherwise keep the column and mark pairs with `row[i][c] < row[i+1][c]` as resolved.
     / 否則保留該欄並標記嚴格遞增的相鄰列。
3. Count deletions.
   / 統計刪除數。

## Why it works / 正確性直覺

- For unresolved pairs, all previous columns are equal. A decrease at the current column can never be fixed by future columns, so deletion is forced.
  / 未確定的相鄰列在此前欄位都相等，若當前欄位逆序，後面欄位無法補救，只能刪除。
- If no decrease exists, keeping the column is safe and can only resolve more pairs.
  / 若沒有逆序，保留此欄不會破壞可行性，且能確定更多相鄰列順序。

## When to use / 使用時機

- Multiple equal-length strings, need minimal deletions of shared positions to keep rows lexicographically sorted.
  / 多個等長字串，需刪除共同欄位以保持行字典序。

## Complexity / 複雜度

- Time: `O(n * m)` for `n` rows and `m` columns.
  / 時間：`O(n * m)`。
- Space: `O(n)` for the state array.
  / 空間：`O(n)`。

## Pitfalls / 常見陷阱

- Update resolved pairs only when the column is kept.
  / 只有在欄位被保留時才更新狀態。
- Equality does not resolve order; only strict `<` does.
  / 相等不算確定順序，必須嚴格遞增才可標記。
- Do not compare pairs already resolved.
  / 已確定的相鄰列不需再比較。

## Related problems / 相關題目

- [q955](../leetcode/q955.md)