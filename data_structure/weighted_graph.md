# Weighted Graph / 加權圖

Goal: model graphs where each edge has a cost, distance, time, or risk.
目標：用「邊權」表示成本、距離、時間或風險。

## Core idea / 核心概念

- Each edge has a weight `w` (non-negative or negative).
  / 每條邊都有權重 `w`（可正可負）。
- Path cost is the sum of edge weights along the path.
  / 路徑成本是邊權總和。
- Directed vs undirected edges follow the same concept.
  / 有向、無向圖都能使用邊權。

## When to use / 何時使用

- Shortest path problems (distance, time, cost).
  / 最短路徑（距離、時間、成本）。
- Minimum cost flow / routing models.
  / 成本流與路由模型。
- Any model that needs edge-specific penalties.
  / 需要邊特定代價的情境。

## Representation / 表示方式

- Adjacency list (sparse graphs): `Vec<Vec<(usize, i64)>>`
  / 鄰接表（稀疏圖）常用。
- Adjacency matrix (dense graphs): `n x n`, `INF` for no edge.
  / 鄰接矩陣（稠密圖）。

Directed edge (u -> v, w):
有向邊：

```
adj[u].push((v, w))
```

Undirected edge (u <-> v, w):
無向邊：

```
adj[u].push((v, w))
adj[v].push((u, w))
```

## Worked example / 範例

Input (directed weighted):
輸入（有向加權）：

```
n m
0 1 2
0 2 5
1 2 1
1 3 2
```

Adjacency list:
鄰接表：

```
0: (1,2), (2,5)
1: (2,1), (3,2)
2: -
3: -
```

## Pitfalls / 常見陷阱

- Negative edges break Dijkstra; use Bellman-Ford instead.
  / 有負權時不能用 Dijkstra。
- Multiple edges between the same pair may exist.
  / 可能存在多重邊。
- Choose `INF` large enough to avoid overflow.
  / `INF` 太小會溢位。

## Related / 相關

- [adjacency_list](adjacency_list.md)
- [dijkstra_shortest_path](../algorithm/dijkstra_shortest_path.md)
