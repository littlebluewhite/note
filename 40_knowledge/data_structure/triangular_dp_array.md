---
title: Triangular DP Array / 三角形 DP 陣列
note_type: knowledge
domain: data_structure
tags: [knowledge, data_structure]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
complexity_time: O(1) per access
complexity_space: O(R^2)
review_interval_days: 14
next_review: 2026-02-28
---
# Triangular DP Array / 三角形 DP 陣列

## Purpose / 目的

用於儲存「第 `r` 層有 `r+1` 個狀態」的分層問題，讓 `dp[r][c]` 可以 `O(1)` 存取並直接做鄰接層轉移。

## Core Idea / 核心概念

- 狀態佈局是三角形：第 0 層 1 個、第 1 層 2 個、...、第 `R` 層 `R+1` 個。
- 雖然邏輯上是三角形，實作常用矩形陣列（例如 `(R+2) x (R+2)`）承載，換取簡單索引與邊界安全。
- 典型索引：`dp[row][col]`，其中 `0 <= col <= row`。

## Operations / 操作

- 初始化：
  - `let mut dp = vec![vec![0.0; r + 2]; r + 2];`
- 讀取狀態：
  - `let x = dp[row][col];`
- 更新下一層：
  - `dp[row + 1][col] += v;`
  - `dp[row + 1][col + 1] += v;`
- 逐層迭代：
  - `for row in 0..=R { for col in 0..=row { ... } }`

## When to Use / 使用時機

- 問題天然是三角層級（如塔狀分流、三角路徑、Pascal 類問題）。
- 每層節點只依賴同層或上一層的局部鄰居。
- 需要可讀性與除錯便利，願意接受 `O(R^2)` 記憶體。

## Worked Example / 實作範例

以香檳塔（`poured = 2`）為例：

1. `dp[0][0] = 2.0`
2. 在 `(0,0)` 溢流 `1.0`，下一層各加 `0.5`
3. 得到第 1 層：`dp[1][0] = 0.5`、`dp[1][1] = 0.5`

狀態表：

```text
row 0: [2.0]
row 1: [0.5, 0.5]
```

## Variations / 變化型

- 省記憶體版本：滾動陣列 `Vec<f64>`，每次只保留當前層與下一層，空間 `O(R)`。
- 精準索引版本：每列長度只配置 `row + 1`，節省常數空間但邏輯較繁瑣。
- 整數型版本：若轉移不涉及小數，可用 `i64`／`u64`。

## Complexity / 複雜度

- 單次狀態讀寫：`O(1)`
- 若處理到第 `R` 層：
  - Time: `O(R^2)`
  - Space: `O(R^2)`（完整三角狀態）

## Pitfalls / 常見陷阱

- `col` 有效範圍是 `0..=row`，誤用固定欄範圍會讀到無效狀態。
- 忘記預留 `+1` 邊界，更新到 `col + 1` 時越界。
- 浮點累積誤差在深層可能放大，輸出比較時建議允許誤差或做截斷。

## Implementation Notes / 實作細節

- Rust 常用 `vec![vec![init; cols]; rows]`，對三角 DP 足夠直觀。
- 若只查單列單點，模擬深度只需到目標列，不必建到最大上限層。
- 對有容量上限的問題，最終值通常要做 `min(capacity, value)`。

## Related Problems / 相關題目

- [q799](../leetcode/q799.md)
