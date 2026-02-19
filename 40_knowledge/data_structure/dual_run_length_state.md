---
title: Dual Run-Length State / 雙連續段長狀態
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-19
updated: 2026-02-19
status: active
source: data_structure
complexity_time: O(1) per step
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-03-05
---
# Dual Run-Length State / 雙連續段長狀態

## Purpose / 目的

Maintain only two run lengths (`prev_run`, `curr_run`) while scanning a sequence, so boundary-based counting can be done online.
在線性掃描時只維護兩段長度（`prev_run`、`curr_run`），讓邊界型計數可即時完成。

## Core Idea / 核心概念

- `curr_run`: length of the current homogeneous block.
- `curr_run`：目前連續段長度。
- `prev_run`: length of the immediately previous block.
- `prev_run`：前一個連續段長度。
- On value change, the old current run becomes previous run, and a new current run starts at length `1`.
- 遇到值切換時，舊 `curr_run` 轉成 `prev_run`，新 `curr_run` 從 `1` 開始。

This structure avoids storing all run lengths (`Vec`) while preserving enough information for adjacent-run formulas.
這個結構不必保存整份 run-length 陣列，卻足以支撐相鄰段公式的計算。

## Operations / 操作

State variables:
狀態變數：

```text
prev_run: int
curr_run: int
ans: int
```

Process each next symbol:
每讀入下一個字元：

1. Same as previous symbol:
1. 若與前一字元相同：
   - `curr_run += 1`
2. Different from previous symbol:
2. 若與前一字元不同：
   - consume boundary contribution (e.g., `ans += min(prev_run, curr_run)`)
   - 邊界貢獻入帳（如 `ans += min(prev_run, curr_run)`）
   - `prev_run = curr_run`
   - `curr_run = 1`

Finalize once after scan:
掃描結束後再做一次收尾貢獻。

## When to Use / 使用時機

- Problems depend on adjacent segment lengths only.
- 題目只依賴相鄰段長，不需要更遠歷史。
- One-pass streaming is required.
- 需要單趟掃描與常數空間。
- Input length is large and full run-length array is unnecessary.
- 輸入很大，不想為所有段長額外配置記憶體。

## Worked Example / 實作範例

String: `00110011`
字串：`00110011`

Initial state:
初始：`prev_run=0, curr_run=1, ans=0`

- Read second `0`: `curr_run=2`
- Hit boundary (`0 -> 1`): add `min(0,2)=0`, move `prev=2`, reset `curr=1`
- Read second `1`: `curr=2`
- Hit boundary (`1 -> 0`): add `min(2,2)=2`, move `prev=2`, reset `curr=1`
- Repeat similarly for remaining part.
- End: final add `min(2,2)=2`

Total `ans = 6`.

## Variations / 變化型

- Full run-length array (`Vec<int> runs`) then adjacent combine.
- 完整 run-length 陣列後處理相鄰段。
- Keep extra aggregate fields (e.g., max run, run count) for multi-metric tasks.
- 若題目需要多指標，可額外維護最大段長、段數等欄位。

## Complexity / 複雜度

- Time: `O(1) per step`, total `O(n)`
- Space: `O(1)`

Where:
`n`: sequence length.

## Pitfalls / 常見陷阱

- Not resetting `curr_run = 1` at boundaries.
- 邊界切換後忘記把 `curr_run` 重設為 1。
- Updating `prev_run` before consuming boundary contribution.
- 邊界貢獻尚未計算就先覆蓋 `prev_run`。
- Missing final flush after loop.
- 迴圈結束後漏掉最後一次收尾計算。

## Implementation Notes / 實作細節

- In Rust, scan `s.as_bytes()` for cheap adjacent comparisons.
- Rust 可用 `as_bytes()` 做常數時間相鄰比較。
- Use signed/unsigned integer type wide enough for answer constraints.
- 答案可能較大時要用足夠位寬（如 `i64`）。
- If input may be empty in other tasks, guard initialization accordingly.
- 若題目允許空輸入，初始化要額外防呆。

## Related Problems / 相關題目

- [q696](../leetcode/q696.md)
