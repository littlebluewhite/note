---
title: "Graph BFS (Queue) / 圖遍歷 BFS（佇列）"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(V + E)
complexity_space: O(V)
---
# Graph BFS (Queue) / 圖遍歷 BFS（佇列）

Goal: explore a graph level by level and find shortest paths in unweighted graphs.
目標：以層級方式探索圖，並在無權圖中找到最短路徑。

## Core idea / 核心概念

- Use a queue to expand nodes in the order they are discovered.
  / 使用佇列依照發現順序擴展節點。
- The first time you visit a node is the shortest path in an unweighted graph.
  / 在無權圖中第一次到達某節點即為最短路徑。
- Mark `visited` when enqueuing to avoid duplicates.
  / 入隊時就標記 `visited`，避免重複入隊。

## When to use / 何時使用

- Shortest path on unweighted graphs or grids.
  / 無權圖或網格的最短路徑。
- Multi-source expansion (e.g., spread, infection, flooding).
  / 多源擴散（感染、擴散、淹水）。
- Level-order traversal or connectivity checks.
  / 層級遍歷或連通性檢查。

## Pattern / 流程

1. Initialize queue with start node(s); mark them visited.
   / 初始化佇列並標記起點（可多源）。
2. While queue not empty:
   / 佇列不空時重複：
   - Pop front, visit node.
     / 取出佇列頭節點。
   - For each neighbor not visited, mark and enqueue.
     / 對未訪問鄰居標記並入隊。
3. Optional: track distance/levels by storing depth or using size-based layers.
   / 可用深度或每層大小追蹤距離。

## Grid BFS / 網格 BFS

- Convert `(r, c)` to index `r * col + c` for arrays.
  / 用 `r * col + c` 映射成一維索引。
- 4-direction moves: up, down, left, right.
  / 4 向移動：上、下、左、右。

## Rust snippet / Rust 範例

```rust
use std::collections::VecDeque;

fn bfs_grid(row: usize, col: usize, blocked: &Vec<bool>) -> bool {
    let total = row * col;
    let mut visited = vec![false; total];
    let mut q: VecDeque<(usize, usize)> = VecDeque::new();

    for c in 0..col {
        if !blocked[c] {
            visited[c] = true;
            q.push_back((0, c));
        }
    }

    let dirs = [(1_i32, 0_i32), (-1, 0), (0, 1), (0, -1)];
    while let Some((r, c)) = q.pop_front() {
        if r == row - 1 {
            return true;
        }
        for (dr, dc) in dirs.iter() {
            let nr = r as i32 + dr;
            let nc = c as i32 + dc;
            if nr < 0 || nc < 0 {
                continue;
            }
            let nr = nr as usize;
            let nc = nc as usize;
            if nr >= row || nc >= col {
                continue;
            }
            let idx = nr * col + nc;
            if blocked[idx] || visited[idx] {
                continue;
            }
            visited[idx] = true;
            q.push_back((nr, nc));
        }
    }

    false
}
```

## Pitfalls / 常見陷阱

- Marking `visited` only when popped -> duplicates and slow.
  / 出隊時才標記會重複入隊，效能變差。
- Using `Vec` with `remove(0)` -> `O(n)` each pop.
  / 用 `Vec` 刪頭會是 `O(n)`。
- Forgetting bounds checks in grid traversal.
  / 網格 BFS 忘記邊界檢查。

## Complexity / 複雜度

- Time: `O(V + E)` for graph, `O(row * col)` for grid.
  / 時間：圖為 `O(V + E)`，網格為 `O(row * col)`。
- Space: `O(V)` for queue + visited.
  / 空間：佇列與 visited 為 `O(V)`。

## Related problems / 相關題目

- [q1970](../leetcode/q1970.md)