---
title: "Floyd-Warshall All-Pairs Shortest Path / Floyd-Warshall 全點對最短路徑"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(n^3)
complexity_space: O(n^2)
---
# Floyd-Warshall All-Pairs Shortest Path / Floyd-Warshall 全點對最短路徑

Goal: compute the shortest distance between **every pair** of nodes in a weighted graph.
目標：計算加權圖中 **任兩點** 的最短距離。

## Prerequisites / 先備知識

- Weighted graph: [weighted_graph](../data_structure/weighted_graph.md)
  / 加權圖。
- 2D array / matrix: [dp_2d_array](../data_structure/dp_2d_array.md)
  / 二維陣列（距離矩陣）。

## Core idea / 核心概念

- Dynamic programming over intermediate nodes.
  / 對「中繼節點」做動態規劃。
- Let `dist[i][j]` be the best cost from `i` to `j` using only nodes `{0..k}` as intermediates.
  / `dist[i][j]` 表示允許中繼節點在 `{0..k}` 的最短距離。
- Transition:
  / 轉移式：

```
for k in 0..n-1:
  for i in 0..n-1:
    for j in 0..n-1:
      dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

## Why it covers multi-step paths / 為什麼不會漏掉多段路徑

DP invariant:
DP 不變量：

- After finishing iteration `k`, `dist[i][j]` is the shortest path from `i` to `j`
  using only intermediates in `{0..k}`.
- 做完第 `k` 輪後，`dist[i][j]` 表示只允許中繼節點在 `{0..k}` 的最短距離。

Why the recurrence is complete:
為什麼轉移式不會漏：

1. Any valid path with intermediates in `{0..k}` falls into exactly one case:
   任一路徑（中繼節點在 `{0..k}`）只會落在兩種情況之一：
   - it does **not** go through `k` -> already covered by `dist` from `k-1`
     / **不經過** `k` -> 已被 `k-1` 的 `dist` 覆蓋
   - it **does** go through `k` -> split at the **first** occurrence of `k`
     / **經過** `k` -> 以「**第一次**經過 `k`」為切點分成兩段
2. The two subpaths are `i -> k` and `k -> j`.
   Both subpaths only use intermediates in `{0..k-1}`.
   / 兩段分別為 `i -> k` 與 `k -> j`，其內部中繼節點都只在 `{0..k-1}`。
3. Therefore the best path through `k` is exactly
   `dist[i][k] + dist[k][j]`, and we take the min.
   / 因此經過 `k` 的最佳路徑正是 `dist[i][k] + dist[k][j]`，取最小即可。

Key intuition:
直覺重點：

- "Many steps" just means "many intermediates".
  / 「很多步」其實只是「很多中繼節點」。
- Floyd-Warshall grows the allowed intermediate set one node at a time,
  so long paths are gradually composed across iterations.
  / 允許的中繼集合逐步擴大，長路徑會在不同輪次被逐步拼接出來。

## When to use / 何時使用

- Need all-pairs shortest path (APSP).
  / 需要全點對最短路徑。
- Graph is **small or dense**, or node count is fixed (e.g., 26 letters).
  / 圖很小或很稠密，或節點數固定（如 26 個字母）。
- Need to answer many shortest-path queries after a one-time precompute.
  / 要一次預處理後回答多次查詢。

## Pattern / 流程

1. Initialize `dist` as `n x n` matrix:
   / 初始化 `dist`：
   - `dist[i][i] = 0`
   - `dist[u][v] = min(dist[u][v], w)` for each edge `(u, v, w)`
   - no edge → `INF`
2. Run the triple loop with `k` as the outermost loop.
   / 以 `k` 為最外層跑三層迴圈更新。
3. `dist[i][j]` is the minimum cost from `i` to `j`.
   / 最終 `dist[i][j]` 即為最短距離。

## Step-by-step example / 逐步範例

Graph (directed):
圖（有向）：

```
0 -> 1 (5)
1 -> 2 (2)
0 -> 2 (10)
```

Initialization:
初始化：

```
 dist =
 [0, 5, 10]
 [INF, 0, 2]
 [INF, INF, 0]
```

Use `k = 1` as intermediate:
使用 `k = 1` 當中繼：

- `dist[0][2] = min(10, dist[0][1] + dist[1][2]) = min(10, 5 + 2) = 7`

Final:
最終：

```
 dist =
 [0, 5, 7]
 [INF, 0, 2]
 [INF, INF, 0]
```

## Full-matrix walkthrough / 完整矩陣走查

Goal path: `1 -> 5 -> 3 -> 2 -> 4` (total cost = 8).
目標路徑：`1 -> 5 -> 3 -> 2 -> 4`（總成本 = 8）。

Graph (directed) edges:
圖（有向）邊：

- 1 -> 5 (2)
- 5 -> 3 (2)
- 3 -> 2 (2)
- 2 -> 4 (2)
- 1 -> 4 (20)
- All other missing edges are treated as `INF`.
  / 其餘缺邊視為 `INF`。

Matrix order: nodes `1..5`.
矩陣順序：節點 `1..5`。

`k = 0` (initial, direct edges only):
`k = 0`（初始，只允許直接邊）：

```
      1   2   3   4   5
1:    0  INF INF  20   2
2:   INF  0  INF  2  INF
3:   INF  2   0  INF INF
4:   INF INF INF  0  INF
5:   INF INF  2  INF  0
```

`k = 1`:

```
      1   2   3   4   5
1:    0  INF INF  20   2
2:   INF  0  INF  2  INF
3:   INF  2   0  INF INF
4:   INF INF INF  0  INF
5:   INF INF  2  INF  0
```

`k = 2` (updates `dist[3][4]` via 3->2->4):
`k = 2`（更新 `dist[3][4]`，走 3->2->4）：

```
      1   2   3   4   5
1:    0  INF INF  20   2
2:   INF  0  INF  2  INF
3:   INF  2   0   4  INF
4:   INF INF INF  0  INF
5:   INF INF  2  INF  0
```

`k = 3` (updates `dist[5][4]` via 5->3->2->4):
`k = 3`（更新 `dist[5][4]`，走 5->3->2->4）：

```
      1   2   3   4   5
1:    0  INF INF  20   2
2:   INF  0  INF  2  INF
3:   INF  2   0   4  INF
4:   INF INF INF  0  INF
5:   INF  4   2   6  0
```

`k = 4`:

```
      1   2   3   4   5
1:    0  INF INF  20   2
2:   INF  0  INF  2  INF
3:   INF  2   0   4  INF
4:   INF INF INF  0  INF
5:   INF  4   2   6  0
```

`k = 5` (updates `dist[1][4]` via 1->5->3->2->4):
`k = 5`（更新 `dist[1][4]`，走 1->5->3->2->4）：

```
      1   2   3   4   5
1:    0   6   4   8   2
2:   INF  0  INF  2  INF
3:   INF  2   0   4  INF
4:   INF INF INF  0  INF
5:   INF  4   2   6  0
```

Key buildup:
重點累積過程：

- `k = 2`: `dist[3][4] = 4` from `3 -> 2 -> 4`
- `k = 3`: `dist[5][4] = 6` from `5 -> 3 -> 2 -> 4`
- `k = 5`: `dist[1][4] = 8` from `1 -> 5 -> 3 -> 2 -> 4`

## Pitfalls / 常見陷阱

- Overflow: use a safe `INF`, and skip when `dist[i][k]` or `dist[k][j]` is `INF`.
  / 溢位：`INF` 要夠大，且遇到 `INF` 先跳過。
- Multiple edges between the same pair: keep the **minimum** edge cost.
  / 多重邊要保留最小成本。
- `O(n^3)` is too slow for large `n` (e.g., `n > 500`).
  / 大 `n` 時三層迴圈過慢。
- Negative cycles: if `dist[i][i] < 0`, a negative cycle exists.
  / 若 `dist[i][i] < 0` 代表存在負環。

## Variations / 變化型

- Transitive closure: use boolean matrix and replace `+` with `AND`, `min` with `OR`.
  / 可用布林矩陣做可達性閉包。
- Path reconstruction: keep `next[i][j]` to rebuild paths.
  / 加 `next` 矩陣可重建路徑。
- Min-plus matrix multiplication view.
  / 視為 min-plus 矩陣乘法。

## Complexity / 複雜度

- Time: `O(n^3)`.
  / 時間：`O(n^3)`。
- Space: `O(n^2)`.
  / 空間：`O(n^2)`。

## Related problems / 相關題目

- [q2976](../leetcode/q2976.md)
- [q2977](../leetcode/q2977.md)
