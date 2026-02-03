---
title: "Relaxation / 鬆弛"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(E)
complexity_space: O(V)
---
# Relaxation / 鬆弛

Goal: update a best-known value when a better path is found.
目標：當找到更好的路徑時，更新「目前最優解」。

## Core idea / 核心概念

`dist[x]` means the current best-known cost from the source to node `x`.
`dist[x]` 代表「從起點到節點 `x` 的目前已知最小成本」。

The source (start node) is the node you choose as the starting point of the path query.
起點（source/start node）就是你要從哪個節點出發來計算路徑的那個節點。

Typical choices:
常見選法：

- Single-source shortest path: the given `s` in the problem statement.
  / 單一起點：題目指定的 `s`。
- Multi-source shortest path: add a super source or push multiple sources with `dist=0`.
  / 多起點：加入超級起點或把多個起點的 `dist` 設為 0。
- Grid problems: top-left cell `(0,0)` (or the specified start).
  / 格子圖：左上角 `(0,0)` 或題目指定起點。

Example meanings:
語意範例：

- `dist[u] = 3` means there is a path from the source to `u` with total cost 3,
  and no better path has been found so far.
  / `dist[u] = 3` 表示目前已知從起點到 `u` 的最小成本是 3（可能還有更短的路徑尚未被發現）。
- `dist[v] = INF` means `v` is not reachable yet (or unknown).
  / `dist[v] = INF` 表示 `v` 目前不可達或尚未被探索到。

For edge `(u -> v, w)`:
對於邊 `(u -> v, w)`：

```
if dist[u] + w < dist[v]:
    dist[v] = dist[u] + w
    parent[v] = u
```

This is called relaxation.
這個更新動作就叫「鬆弛」。

## When to use / 何時使用

- Shortest paths: Dijkstra, Bellman-Ford, SPFA.
  / 最短路徑演算法。
- Dynamic programming transitions with better cost.
  / 任何「取更小成本」的 DP 轉移。

## Worked example / 範例

Given `dist[u]=3`, edge `u->v` with `w=4`, and `dist[v]=10`:
已知 `dist[u]=3`，邊 `u->v` 權重 `4`，`dist[v]=10`：

- `dist[u] + w = 7 < 10`, so update:
  / `7 < 10`，更新：

```
dist[v] = 7
parent[v] = u
```

## Typical pattern / 常見流程

1. Initialize `dist` to `INF`, set source to `0`.
   / `dist` 初始化為 `INF`，起點為 `0`。
2. Iterate edges (or pop from heap) and relax.
   / 迭代邊並執行鬆弛。
3. Optionally track `parent` to reconstruct paths.
   / 記錄 `parent` 以還原路徑。

## Complexity / 複雜度

- Time: `O(E)`
- Space: `O(V)`

Where:
`V`: number of vertices.
`E`: number of edges.


## Pitfalls / 常見陷阱

- Forgetting `INF` guard may overflow: check `dist[u]` is valid.
  / 未檢查 `INF` 可能溢位。
- Negative edges invalidate Dijkstra's correctness.
  / Dijkstra 不適用負權。
- Not storing `parent` makes path reconstruction impossible.
  / 未記錄 `parent` 無法還原路徑。

## Related / 相關

- [dijkstra_shortest_path](dijkstra_shortest_path.md)
- [priority_queue_binary_heap](../data_structure/priority_queue_binary_heap.md)