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
