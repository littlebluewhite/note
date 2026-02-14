---
title: Layered Overflow DP Simulation / 分層溢流 DP 模擬
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
complexity_time: O(L^2)
complexity_space: O(L^2)
review_interval_days: 14
next_review: 2026-02-28
---
# Layered Overflow DP Simulation / 分層溢流 DP 模擬

## Goal

在「分層結構 + 容量上限 + 溢流分配」的問題中，精準模擬資源如何由上層傳到下層，求某個目標節點的最終值。

## When to Use

- 結構是分層 DAG（例如金字塔、三角網格），邊只往下一層。
- 每個節點有容量上限（例如最多裝 `1` 單位），超出的部分要傳遞。
- 傳遞規則固定且局部（例如平均分給兩個子節點）。
- 查詢目標只在前 `L` 層內，無需模擬整個無限過程。

## Core Idea

- 定義狀態 `dp[row][col]`：到達該節點的總量（可大於容量）。
- 每個節點只做一件事：保留容量內部分，把超量往下一層傳。
- 由上到下處理，因為下一層只依賴上一層，符合 DP 拓樸順序。

對香檳塔類型問題（容量 `cap = 1`、左右平分）可寫成：

```text
overflow = max(0, dp[row][col] - 1)
dp[row + 1][col]     += overflow / 2
dp[row + 1][col + 1] += overflow / 2
```

## Steps

1. 決定需要模擬的最深層 `L`（通常是查詢列 `query_row`）。
2. 配置三角形 DP 陣列 `dp`，大小至少 `(L + 2) x (L + 2)`。
3. 設定來源節點初值（例如 `dp[0][0] = poured`）。
4. 逐層掃描：
   - 計算每個節點的超量 `overflow`。
   - 依規則把 `overflow` 分配到下一層節點。
5. 讀取答案，若節點有容量上限，回傳 `min(cap, dp[target])`。

## Complexity

- Time: `O(L^2)`，因為總共處理約 `1 + 2 + ... + (L + 1)` 個狀態。
- Space: `O(L^2)`，儲存完整分層狀態。

## Pitfalls

- 忘記只傳「超量」而不是全部流量，會造成結果過大。
- 陣列尺寸沒預留 `+1` 邊界，更新 `row + 1`、`col + 1` 時會越界。
- 輸出值需被容量上限截斷（如 `min(1.0, x)`），否則與題意不符。
- 使用整數運算處理等比分流會遺失精度，應改用 `f64`。

## Examples

以 `poured = 4`、查詢到第 `2` 列為例：

- 第 0 列：`[4.0]`
  - 超量 `3.0`，分給下一列左右各 `1.5`
- 第 1 列：`[1.5, 1.5]`
  - 兩杯各超量 `0.5`，往下一列分流各 `0.25`
- 第 2 列：`[0.25, 0.5, 0.25]`

若問第 2 列中間杯，答案是 `0.5`。

## Notes

- 這是「圖上 DP」的一種特化：節點依層有天然拓樸序。
- 可用滾動陣列把空間降到 `O(L)`，但完整二維較易除錯與說明。
- 若分配比例不是 1/2 與 1/2，只要替換轉移係數即可沿用。

## Related

- [q799](../leetcode/q799.md)
