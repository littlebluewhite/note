# Adjacency List / 鄰接表

Goal: represent graphs or trees efficiently, especially when the graph is sparse.
目標：高效表示稀疏圖或樹。

## When to use / 何時使用

- Frequent neighbor iteration is needed. / 常需要遍歷鄰居。
- Edge count `m` is close to node count `n`. / 邊數 `m` 接近節點數 `n`。
- You will run BFS/DFS or tree DP. / 會進行 BFS/DFS 或樹上 DP。

## Structure / 結構

- Unweighted: `Vec<Vec<usize>>` / 無權圖：`Vec<Vec<usize>>`
- Weighted: `Vec<Vec<(usize, i64)>>` / 有權圖：`Vec<Vec<(usize, i64)>>`
- Space: `O(n + m)` / 空間：`O(n + m)`

## Build / 建立方式

- Undirected: push both `u -> v` and `v -> u`. / 無向圖：加入兩個方向。
- Directed: push only `u -> v`. / 有向圖：只加入單向。

## Worked Examples / 實作範例

### Example 1: undirected graph / 範例 1：無向圖

Input format / 輸入格式

```
n m
u1 v1
u2 v2
...
um vm
```

Output format / 輸出格式

```
0: neighbors...
1: neighbors...
...
```

Example input / 範例輸入

```
4 3
0 1
1 2
1 3
```

Expected output / 預期輸出

```
0: 1
1: 0 2 3
2: 1
3: 1
```

Step-by-step / 步驟

- Step 1: initialize `adj` with empty lists.
  / 步驟 1：建立空的鄰接表。
- Step 2: add edge (0,1) -> append 1 to `adj[0]`, 0 to `adj[1]`.
  / 步驟 2：加入邊 (0,1)。
- Step 3: add edge (1,2) -> append 2 to `adj[1]`, 1 to `adj[2]`.
  / 步驟 3：加入邊 (1,2)。
- Step 4: add edge (1,3) -> append 3 to `adj[1]`, 1 to `adj[3]`.
  / 步驟 4：加入邊 (1,3)。

State table / 狀態表

```
Step | Edge  | adj[0] | adj[1]   | adj[2] | adj[3]
-----+-------+--------+----------+--------+--------
0    | init  | []     | []       | []     | []
1    | 0-1   | [1]    | [0]      | []     | []
2    | 1-2   | [1]    | [0,2]    | [1]    | []
3    | 1-3   | [1]    | [0,2,3]  | [1]    | [1]
```

Transition / 轉移

- Undirected edge (u,v): `adj[u].push(v)`, `adj[v].push(u)`.
  / 無向邊 (u,v)：兩邊都加入。

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};
use std::fmt::Write;

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let m: usize = it.next().unwrap().parse().unwrap();
    let mut adj = vec![Vec::<usize>::new(); n];
    for _ in 0..m {
        let u: usize = it.next().unwrap().parse().unwrap();
        let v: usize = it.next().unwrap().parse().unwrap();
        adj[u].push(v);
        adj[v].push(u);
    }

    let mut out = String::new();
    for i in 0..n {
        let _ = write!(&mut out, "{}:", i);
        for (idx, v) in adj[i].iter().enumerate() {
            if idx == 0 {
                let _ = write!(&mut out, " {}", v);
            } else {
                let _ = write!(&mut out, " {}", v);
            }
        }
        let _ = writeln!(&mut out);
    }
    print!("{}", out);
}
```

Go (full program) / Go（完整程式）

```go
package main

import (
    "bufio"
    "fmt"
    "os"
)

func main() {
    in := bufio.NewReader(os.Stdin)
    var n, m int
    fmt.Fscan(in, &n, &m)
    adj := make([][]int, n)
    for i := 0; i < m; i++ {
        var u, v int
        fmt.Fscan(in, &u, &v)
        adj[u] = append(adj[u], v)
        adj[v] = append(adj[v], u)
    }
    out := bufio.NewWriter(os.Stdout)
    for i := 0; i < n; i++ {
        fmt.Fprintf(out, "%d:", i)
        for _, v := range adj[i] {
            fmt.Fprintf(out, " %d", v)
        }
        fmt.Fprintln(out)
    }
    out.Flush()
}
```

### Example 2: directed weighted graph / 範例 2：有向加權圖

Input format / 輸入格式

```
n m
u1 v1 w1
u2 v2 w2
...
um vm wm
```

Output format / 輸出格式

```
0: (v,w) (v,w)
1:
...
```

Example input / 範例輸入

```
4 3
0 1 5
0 2 2
2 3 7
```

Expected output / 預期輸出

```
0: (1,5) (2,2)
1:
2: (3,7)
3:
```

Step-by-step / 步驟

- Step 1: initialize `adj` with empty lists.
  / 步驟 1：建立空的鄰接表。
- Step 2: add edge 0->1 (w=5) to `adj[0]`.
  / 步驟 2：加入 0->1（權重 5）。
- Step 3: add edge 0->2 (w=2) to `adj[0]`.
  / 步驟 3：加入 0->2（權重 2）。
- Step 4: add edge 2->3 (w=7) to `adj[2]`.
  / 步驟 4：加入 2->3（權重 7）。

State table / 狀態表

```
Step | Edge     | adj[0]         | adj[1] | adj[2]      | adj[3]
-----+----------+----------------+--------+-------------+--------
0    | init     | []             | []     | []          | []
1    | 0->1 (5) | [(1,5)]        | []     | []          | []
2    | 0->2 (2) | [(1,5),(2,2)]  | []     | []          | []
3    | 2->3 (7) | [(1,5),(2,2)]  | []     | [(3,7)]     | []
```

Transition / 轉移

- Directed edge (u,v,w): `adj[u].push((v,w))` only.
  / 有向邊只加入單向。

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};
use std::fmt::Write;

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let m: usize = it.next().unwrap().parse().unwrap();
    let mut adj = vec![Vec::<(usize, i64)>::new(); n];
    for _ in 0..m {
        let u: usize = it.next().unwrap().parse().unwrap();
        let v: usize = it.next().unwrap().parse().unwrap();
        let w: i64 = it.next().unwrap().parse().unwrap();
        adj[u].push((v, w));
    }

    let mut out = String::new();
    for i in 0..n {
        let _ = write!(&mut out, "{}:", i);
        for (v, w) in &adj[i] {
            let _ = write!(&mut out, " ({},{})", v, w);
        }
        let _ = writeln!(&mut out);
    }
    print!("{}", out);
}
```

Go (full program) / Go（完整程式）

```go
package main

import (
    "bufio"
    "fmt"
    "os"
)

type Edge struct {
    to int
    w  int
}

func main() {
    in := bufio.NewReader(os.Stdin)
    var n, m int
    fmt.Fscan(in, &n, &m)
    adj := make([][]Edge, n)
    for i := 0; i < m; i++ {
        var u, v, w int
        fmt.Fscan(in, &u, &v, &w)
        adj[u] = append(adj[u], Edge{to: v, w: w})
    }
    out := bufio.NewWriter(os.Stdout)
    for i := 0; i < n; i++ {
        fmt.Fprintf(out, "%d:", i)
        for _, e := range adj[i] {
            fmt.Fprintf(out, " (%d,%d)", e.to, e.w)
        }
        fmt.Fprintln(out)
    }
    out.Flush()
}
```

## Diagram & Visual Explanation / 圖示與視覺化說明

Graph / 圖：

```
0 -- 1 -- 2
     |
     3
```

Adjacency list (undirected) / 鄰接表（無向）：

```
0: [1]
1: [0, 2, 3]
2: [1]
3: [1]
```

Intuition: each node stores only its neighbors, so we can iterate edges quickly.
直覺：每個節點只存鄰居，遍歷邊時很快。

## Thought process / 思路

- If queries are "who are the neighbors of u?", adjacency list is ideal.
  / 若常問「u 的鄰居有哪些？」，鄰接表最合適。
- If queries are "is there an edge u-v?", adjacency matrix can be faster.
  / 若常問「u-v 是否有邊？」，鄰接矩陣更快。

## Variations / 變化型

- Store edge id or extra data: `Vec<Vec<(usize, edge_id)>>`.
  / 儲存邊編號或額外資訊。
- Allow duplicates for multigraphs. / 多重邊允許重複。
- Rooted tree: keep `parent[u]` or store children only.
  / 根樹：保留 `parent[u]` 或只存孩子。

## Pitfalls / 常見陷阱

- Mixing 0-based and 1-based indices. / 0-based 與 1-based 混用。
- Forgetting both directions in undirected graphs. / 無向圖忘記加雙向。
- Deep recursion may overflow; consider iterative DFS. / 遞迴過深可改用迭代 DFS。

## Complexity / 複雜度

- Build: `O(n + m)` / 建立：`O(n + m)`
- Iterate neighbors: `O(deg(u))` / 走訪鄰居：`O(deg(u))`
- BFS/DFS: `O(n + m)` / BFS/DFS：`O(n + m)`

## Related problems / 相關題目

- [q3562](../leetcode/q3562.md)
- [q3650](../leetcode/q3650.md)
