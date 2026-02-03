---
title: "Dijkstra Shortest Path / Dijkstra 最短路徑"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(n + m)
complexity_space: O(n + m)
---
# Dijkstra Shortest Path / Dijkstra 最短路徑

Goal: compute the shortest distance from a source in graphs with **non-negative** edge weights.
目標：在邊權皆為**非負**的圖中，求從起點到各節點的最短距離。

## Prerequisites / 先備知識

- Weighted graph: [weighted_graph](../data_structure/weighted_graph.md)
  / 加權圖。
- Adjacency list: [adjacency_list](../data_structure/adjacency_list.md)
  / 鄰接表。
- Priority queue (min-heap): [priority_queue_binary_heap](../data_structure/priority_queue_binary_heap.md)
  / 優先佇列（最小堆）。
- Relaxation concept: [relaxation](relaxation.md)
  / 鬆弛（relaxation）的概念。

## Core idea / 核心概念

- Always expand the node with the smallest tentative distance.
  / 每次擴展目前距離最小的節點。
- Use a min-heap (priority queue) to fetch that node quickly.
  / 用最小堆快速取出最小距離節點。
- Relax edges: if `dist[u] + w < dist[v]`, update `dist[v]`.
  / 進行鬆弛：若 `dist[u] + w < dist[v]`，就更新 `dist[v]`。

## When to use / 何時使用

- Shortest path on weighted graphs with non-negative edges.
  / 權重非負圖的最短路徑。
- Multi-source shortest path (add a super source).
  / 多源最短路徑（加入超級起點）。
- Problems that can be modeled as shortest path after **state expansion**.
  / 透過**狀態擴張**可轉成最短路徑的題目。

## Pattern / 流程

1. Build adjacency list.
   / 建立鄰接表。
2. Initialize `dist` to INF; set `dist[src] = 0`.
   / `dist` 初始化為 INF，起點為 0。
3. Push `(0, src)` into min-heap.
   / 推入 `(0, src)` 到最小堆。
4. While heap not empty:
   / 迭代直到堆為空：
   - Pop `(d, u)`. If `d != dist[u]`, skip (outdated).
     / 取出 `(d, u)`；若 `d != dist[u]` 則略過（過期）。
   - For each edge `(u, v, w)`, relax `dist[v]`.
     / 對每條邊 `(u, v, w)` 做鬆弛更新。

## Step-by-step walkthrough / 逐步教學

We will use this directed graph (non-negative weights):
以下用一個有向圖示範（權重皆非負）：

```
0 -> 1 (2), 0 -> 2 (4)
1 -> 2 (1), 1 -> 3 (7)
2 -> 3 (3)
```

Goal: shortest distances from source `0`.
目標：求起點 `0` 到各點最短距離。

Initialization:
初始化：

- `dist = [0, INF, INF, INF]`
- heap = `(0, 0)`

Step 1:
步驟 1：

- Pop `(0, 0)` → relax neighbors of `0`:
  - to `1`: `0 + 2 = 2` → update `dist[1]=2`
  - to `2`: `0 + 4 = 4` → update `dist[2]=4`
- heap now: `(2,1), (4,2)`

Step 2:
步驟 2：

- Pop `(2, 1)` → relax neighbors of `1`:
  - to `2`: `2 + 1 = 3` → update `dist[2]=3` (better than 4)
  - to `3`: `2 + 7 = 9` → update `dist[3]=9`
- heap now: `(3,2), (4,2), (9,3)`
  - `(4,2)` is outdated later.

Step 3:
步驟 3：

- Pop `(3, 2)` → relax neighbors of `2`:
  - to `3`: `3 + 3 = 6` → update `dist[3]=6` (better than 9)
- heap now: `(4,2), (6,3), (9,3)`

Step 4:
步驟 4：

- Pop `(4, 2)` → outdated because `dist[2]=3`, skip.
- Pop `(6, 3)` → relax neighbors (none).
- Pop `(9, 3)` → outdated, skip.

Final:
最終答案：

- `dist = [0, 2, 3, 6]`

Key observation:
關鍵觀察：

When a node `u` is popped with `d == dist[u]`, that distance is finalized.
節點 `u` 被取出且 `d == dist[u]` 時，`dist[u]` 已是最短距離。

## Larger walkthrough with table / 更大範例 + 表格追蹤

Graph:
圖：

```
0 -> 1 (2), 0 -> 2 (5)
1 -> 2 (1), 1 -> 3 (2)
2 -> 3 (3), 2 -> 4 (5)
3 -> 4 (1)
```

Goal: shortest distances from source `0`.
目標：求起點 `0` 到各點最短距離。

Legend:
說明：

- Heap shows candidates as `(dist, node)`; outdated entries may exist.
  / 堆中可能包含過期項。
- `parent[v]` stores the predecessor for path reconstruction.
  / `parent[v]` 用於還原路徑。

```
Step | Pop      | Heap after relax                 | dist[0..4]        | parent[0..4]
-----+----------+----------------------------------+-------------------+---------------
0    | -        | (0,0)                            | [0,INF,INF,INF,INF] | [-,-,-,-,-]
1    | (0,0)    | (2,1),(5,2)                      | [0,2,5,INF,INF]   | [-,0,0,-,-]
2    | (2,1)    | (3,2),(4,3),(5,2)                | [0,2,3,4,INF]     | [-,0,1,1,-]
3    | (3,2)    | (4,3),(5,2),(8,4)                | [0,2,3,4,8]       | [-,0,1,1,2]
4    | (4,3)    | (5,2),(5,4),(8,4)                | [0,2,3,4,5]       | [-,0,1,1,3]
5    | (5,2)    | (5,4),(8,4)                      | [0,2,3,4,5]       | [-,0,1,1,3]
6    | (5,4)    | (8,4)                            | [0,2,3,4,5]       | [-,0,1,1,3]
7    | (8,4)    | -                                | [0,2,3,4,5]       | [-,0,1,1,3]
```

Notes:
補充：

- Step 5 pops `(5,2)`, but `dist[2]=3`, so it is outdated and skipped.
  / 第 5 步 `(5,2)` 過期，直接略過。

Detailed log:
逐行追蹤：

```
Step 0 (init):
dist = [0, INF, INF, INF, INF]
parent = [-, -, -, -, -]
heap = [(0,0)]

Step 1 pop (0,0):
relax 0->1 (2): dist[1]=2, parent[1]=0, push (2,1)
relax 0->2 (5): dist[2]=5, parent[2]=0, push (5,2)
heap = [(2,1),(5,2)]

Step 2 pop (2,1):
relax 1->2 (1): dist[2]=3, parent[2]=1, push (3,2)
relax 1->3 (2): dist[3]=4, parent[3]=1, push (4,3)
heap = [(3,2),(4,3),(5,2)]

Step 3 pop (3,2):
relax 2->3 (3): nd=6 > dist[3]=4, no update
relax 2->4 (5): dist[4]=8, parent[4]=2, push (8,4)
heap = [(4,3),(5,2),(8,4)]

Step 4 pop (4,3):
relax 3->4 (1): dist[4]=5, parent[4]=3, push (5,4)
heap = [(5,2),(5,4),(8,4)]

Step 5 pop (5,2):
outdated (dist[2]=3), skip
heap = [(5,4),(8,4)]

Step 6 pop (5,4):
no neighbors
heap = [(8,4)]

Step 7 pop (8,4):
outdated (dist[4]=5), skip
heap = []
```

## Pseudocode / 偽代碼

```
dist[*] = INF
dist[src] = 0
heap.push((0, src))

while heap not empty:
    (d, u) = heap.pop_min()
    if d != dist[u]: continue
    for (v, w) in adj[u]:
        if d + w < dist[v]:
            dist[v] = d + w
            parent[v] = u
            heap.push((dist[v], v))
```

## Reconstruct path / 還原最短路徑

To get the actual path (not just distance), store `parent[v] = u` when relaxing.
若要找出最短路徑本身，在更新 `dist[v]` 時記錄 `parent[v] = u`。

Then, for any target `t`:
對任一目標點 `t`：

1. Start from `t`, repeatedly follow `parent`.
   / 從 `t` 開始沿著 `parent` 往回走。
2. Reverse the collected nodes.
   / 反轉節點序列即為最短路徑。

## Practice problems + solutions / 練習題與解法

### A) Single-source shortest path + path reconstruction

Problem:
題目：

Given a directed graph with non-negative weights, source `s` and target `t`.
Output the shortest distance and one shortest path.
給定非負權有向圖與起點 `s`、終點 `t`，輸出最短距離與一條最短路徑。

Sample:
範例：

```
Nodes: 0..4, s=0, t=4
Edges:
0->1(2), 0->2(5)
1->2(1), 1->3(2)
2->3(3), 2->4(5)
3->4(1)
```

Solution idea:
解法：

- Run Dijkstra from `s`, maintain `parent[v]`.
- Reconstruct path from `t`.

Answer:
答案：

- shortest distance = `5`
- one shortest path = `0 -> 1 -> 3 -> 4`

### B) Multi-source shortest path

Problem:
題目：

Given `k` sources, find distance to the nearest source for every node.
給定多個起點，對每個節點求距離最近起點的距離。

Solution idea:
解法：

- Initialize all `dist[source]=0`, push all sources to the heap.
- Run Dijkstra once.

Mini example:
小例子：

```
Sources: {0, 3}
Edges: 0->1(2), 1->2(2), 3->2(1)
```

Answer:
答案：

- dist[0]=0, dist[1]=2, dist[2]=1, dist[3]=0

### C) Grid shortest path (non-negative weights)

Problem:
題目：

Each cell has a cost to enter (>=0). Find minimum total cost from top-left to bottom-right (including the start cell cost).
每格有進入成本（>=0），求左上到右下最小成本（包含起點成本）。

Solution idea:
解法：

- Treat each cell `(r,c)` as a node.
- Edge to 4 neighbors with weight = neighbor's cost.
- Run Dijkstra from `(0,0)`.

Mini example:
小例子：

```
Grid costs:
1 3 1
1 5 1
4 2 1
```

Answer:
答案：

- minimum cost = `7` (path: right, right, down, down with costs 1+3+1+1+1)

## Undirected graphs / 無向圖

If the graph is undirected, add edges in both directions:
若是無向圖，對每條邊 `(u, v, w)` 加入兩條：

- `u -> v (w)` and `v -> u (w)`
  / 同時加入 `u -> v (w)` 與 `v -> u (w)`。

Dijkstra logic is unchanged.
其餘流程不變。

## 0-1 BFS vs Dijkstra / 0-1 BFS 對照

When all edge weights are only `0` or `1`, use 0-1 BFS:
當邊權只有 `0/1` 時，可用 0-1 BFS 取代 Dijkstra：

- Time: `O(n + m)` (faster than `O((n+m)log n)`).
  / 時間更快。
- Use a deque: push front if weight is `0`, push back if weight is `1`.
  / 用 deque，權重為 0 放前端、為 1 放後端。

Pseudocode:
偽代碼：

```
dist[*] = INF
dist[src] = 0
deque.push_front(src)

while deque not empty:
    u = deque.pop_front()
    for (v, w) in adj[u]:
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
            if w == 0: deque.push_front(v)
            else: deque.push_back(v)
```

## State expansion / 狀態擴張

If a node has extra conditions (remaining steps, parity, switch, etc.), create new states like `(node, state)` and run Dijkstra on the expanded graph.
若節點有額外條件（剩餘步數、奇偶、開關等），可將狀態擴成 `(node, state)`，在擴充後的圖上跑 Dijkstra。

Example: if an edge `u → v` (cost `w`) can be reversed once at `v` with cost `2w`, add both `u → v (w)` and `v → u (2w)`.
範例：若 `u → v`（成本 `w`）可在 `v` 反轉一次並以 `2w` 成本走回 `u`，就加入 `u → v (w)` 與 `v → u (2w)`。

## Rust full example / Rust 完整範例

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;
use std::io::{self, Read};

fn dijkstra(n: usize, adj: &[Vec<(usize, i64)>], src: usize) -> (Vec<i64>, Vec<Option<usize>>) {
    let inf = i64::MAX / 4;
    let mut dist = vec![inf; n];
    let mut parent = vec![None; n];
    dist[src] = 0;
    let mut heap = BinaryHeap::new();
    heap.push((Reverse(0_i64), src));

    while let Some((Reverse(d), u)) = heap.pop() {
        if d != dist[u] {
            continue;
        }
        for &(v, w) in &adj[u] {
            let nd = d + w;
            if nd < dist[v] {
                dist[v] = nd;
                parent[v] = Some(u);
                heap.push((Reverse(nd), v));
            }
        }
    }

    (dist, parent)
}

fn build_path(parent: &[Option<usize>], target: usize) -> Vec<usize> {
    let mut path = Vec::new();
    let mut cur = Some(target);
    while let Some(v) = cur {
        path.push(v);
        cur = parent[v];
    }
    path.reverse();
    path
}

fn main() {
    // Input format:
    // n m
    // u v w  (m lines, 0-indexed, directed)
    // s t
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let m: usize = it.next().unwrap().parse().unwrap();

    let mut adj = vec![Vec::new(); n];
    for _ in 0..m {
        let u: usize = it.next().unwrap().parse().unwrap();
        let v: usize = it.next().unwrap().parse().unwrap();
        let w: i64 = it.next().unwrap().parse().unwrap();
        adj[u].push((v, w));
    }
    let s: usize = it.next().unwrap().parse().unwrap();
    let t: usize = it.next().unwrap().parse().unwrap();

    let (dist, parent) = dijkstra(n, &adj, s);
    if dist[t] >= i64::MAX / 8 {
        println!("unreachable");
        return;
    }

    let path = build_path(&parent, t);
    println!("dist = {}", dist[t]);
    println!("path = {:?}", path);
}
```

## Pitfalls / 常見陷阱

- Negative edges break Dijkstra; use Bellman-Ford or SPFA instead.
  / 有負權邊不能用 Dijkstra，改用 Bellman-Ford 或 SPFA。
- Not skipping outdated heap entries causes extra work.
  / 未跳過過期堆元素會造成額外工作。
- Using too-small `INF` may overflow when adding edges.
  / `INF` 太小可能在加權時溢位。
- Graph too large: consider 0-1 BFS or Dial's algorithm if weights are small integers.
  / 若邊權很小（如 0/1 或小整數），可考慮 0-1 BFS 或 Dial 演算法。

## Complexity / 複雜度

- Time: `O((n + m) log n)` with a binary heap.
  / 時間：`O((n + m) log n)`。
- Space: `O(n + m)` for graph + heap + dist.
  / 空間：`O(n + m)`。

## Related problems / 相關題目

- [q3650](../leetcode/q3650.md)
