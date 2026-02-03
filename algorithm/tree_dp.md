---
title: "Tree DP / 樹上動態規劃"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(n)
complexity_space: O(n)
---
# Tree DP / 樹上動態規劃

Goal: solve problems on trees by combining results from children.
目標：用子樹資訊合併求解。

## Pattern / 流程

1. Choose a root. / 選根。
2. Run DFS in postorder. / 後序 DFS。
3. Compute DP state from children. / 由子節點合併。

## Worked Examples / 實作範例

### Example 1: maximum independent set / 範例 1：最大獨立集

Input format / 輸入格式

```
n
val0 val1 ... val(n-1)
(n-1) lines of edges: u v
```

Output format / 輸出格式

- Maximum independent set value.
  / 輸出最大值。

Example input / 範例輸入

```
4
3 2 4 1
0 1
0 2
2 3
```

Expected output / 預期輸出

```
6
```

Tree:

```
    0
   / \
  1   2
     /
    3
```

Values: `val = [3, 2, 4, 1]`

State / 狀態

- `dp[u][0]`: max value if `u` not chosen.
  / `u` 不選時子樹最大值。
- `dp[u][1]`: max value if `u` chosen.
  / `u` 被選時子樹最大值。

Transition / 轉移

- `dp[u][1] = val[u] + sum(dp[v][0])`
- `dp[u][0] = sum(max(dp[v][0], dp[v][1]))`

Step-by-step / 步驟

- Step 1: compute leaves (1,3).
  / 步驟 1：先處理葉節點。
- Step 2: compute node 2 from child 3.
  / 步驟 2：合併子節點。
- Step 3: compute node 0 from children 1 and 2.
  / 步驟 3：合併根節點。

State table / 狀態表

```
Node | dp0 | dp1
-----+-----+-----
1    | 0   | 2
3    | 0   | 1
2    | 1   | 4
0    | 6   | 4
```

Answer = max(dp0, dp1) at root = 6.
答案為 6。

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn dfs(u: usize, p: usize, adj: &Vec<Vec<usize>>, val: &Vec<i64>, dp0: &mut Vec<i64>, dp1: &mut Vec<i64>) {
    dp0[u] = 0;
    dp1[u] = val[u];
    for &v in &adj[u] {
        if v == p {
            continue;
        }
        dfs(v, u, adj, val, dp0, dp1);
        dp0[u] += dp0[v].max(dp1[v]);
        dp1[u] += dp0[v];
    }
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut val = vec![0i64; n];
    for i in 0..n {
        val[i] = it.next().unwrap().parse().unwrap();
    }
    let mut adj = vec![Vec::<usize>::new(); n];
    for _ in 0..(n - 1) {
        let u: usize = it.next().unwrap().parse().unwrap();
        let v: usize = it.next().unwrap().parse().unwrap();
        adj[u].push(v);
        adj[v].push(u);
    }
    let mut dp0 = vec![0i64; n];
    let mut dp1 = vec![0i64; n];
    dfs(0, n, &adj, &val, &mut dp0, &mut dp1);
    let ans = dp0[0].max(dp1[0]);
    println!("{}", ans);
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

func dfs(u, p int, adj [][]int, val []int, dp0, dp1 []int) {
    dp0[u] = 0
    dp1[u] = val[u]
    for _, v := range adj[u] {
        if v == p {
            continue
        }
        dfs(v, u, adj, val, dp0, dp1)
        if dp0[v] > dp1[v] {
            dp0[u] += dp0[v]
        } else {
            dp0[u] += dp1[v]
        }
        dp1[u] += dp0[v]
    }
}

func main() {
    in := bufio.NewReader(os.Stdin)
    var n int
    fmt.Fscan(in, &n)
    val := make([]int, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &val[i])
    }
    adj := make([][]int, n)
    for i := 0; i < n-1; i++ {
        var u, v int
        fmt.Fscan(in, &u, &v)
        adj[u] = append(adj[u], v)
        adj[v] = append(adj[v], u)
    }
    dp0 := make([]int, n)
    dp1 := make([]int, n)
    dfs(0, -1, adj, val, dp0, dp1)
    ans := dp0[0]
    if dp1[0] > ans {
        ans = dp1[0]
    }
    fmt.Println(ans)
}
```

### Example 2: subtree sum / 範例 2：子樹總和

Input format / 輸入格式

```
n
val0 val1 ... val(n-1)
(n-1) lines of edges: u v
```

Output format / 輸出格式

- Print `sub[0..n-1]` in one line.
  / 一行輸出子樹和。

Example input / 範例輸入

```
4
3 2 4 1
0 1
0 2
2 3
```

Expected output / 預期輸出

```
8 2 5 1
```

Step-by-step / 步驟

- Step 1: compute leaves' sub sum = val.
  / 步驟 1：葉節點子樹和 = 自身值。
- Step 2: propagate upward by postorder.
  / 步驟 2：後序合併。

State table / 狀態表

```
Node | sub
-----+----
1    | 2
3    | 1
2    | 5
0    | 8
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn dfs(u: usize, p: usize, adj: &Vec<Vec<usize>>, val: &Vec<i64>, sub: &mut Vec<i64>) {
    sub[u] = val[u];
    for &v in &adj[u] {
        if v == p {
            continue;
        }
        dfs(v, u, adj, val, sub);
        sub[u] += sub[v];
    }
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut val = vec![0i64; n];
    for i in 0..n {
        val[i] = it.next().unwrap().parse().unwrap();
    }
    let mut adj = vec![Vec::<usize>::new(); n];
    for _ in 0..(n - 1) {
        let u: usize = it.next().unwrap().parse().unwrap();
        let v: usize = it.next().unwrap().parse().unwrap();
        adj[u].push(v);
        adj[v].push(u);
    }
    let mut sub = vec![0i64; n];
    dfs(0, n, &adj, &val, &mut sub);
    let mut out = String::new();
    for (i, v) in sub.iter().enumerate() {
        if i > 0 {
            out.push(' ');
        }
        out.push_str(&v.to_string());
    }
    println!("{}", out);
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

func dfs(u, p int, adj [][]int, val []int, sub []int) {
    sub[u] = val[u]
    for _, v := range adj[u] {
        if v == p {
            continue
        }
        dfs(v, u, adj, val, sub)
        sub[u] += sub[v]
    }
}

func main() {
    in := bufio.NewReader(os.Stdin)
    var n int
    fmt.Fscan(in, &n)
    val := make([]int, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &val[i])
    }
    adj := make([][]int, n)
    for i := 0; i < n-1; i++ {
        var u, v int
        fmt.Fscan(in, &u, &v)
        adj[u] = append(adj[u], v)
        adj[v] = append(adj[v], u)
    }
    sub := make([]int, n)
    dfs(0, -1, adj, val, sub)
    out := bufio.NewWriter(os.Stdout)
    for i, v := range sub {
        if i > 0 {
            fmt.Fprint(out, " ")
        }
        fmt.Fprint(out, v)
    }
    fmt.Fprintln(out)
    out.Flush()
}
```

## Diagram & Visual Explanation / 圖示與視覺化說明

```
    0
   / \
  1   2
     /
    3
```

For each node `u`, we compute two numbers. / 每個節點 `u` 都計算兩個狀態。
- pick `u` (use children state 0) / 選 `u`（子節點只能用 0 狀態）
- skip `u` (use max of children) / 不選 `u`（子節點取最大）

## Variations / 變化型

- Tree knapsack: merge child arrays. / 樹上背包合併。
- Rerooting DP: compute answers for all roots. / 換根 DP。
- Multiple states per node. / 多狀態 DP。

## Pitfalls / 常見陷阱

- Recursion depth may be large; consider iterative DFS. / 遞迴過深。
- Remember to skip parent when iterating children. / 走訪時跳過父節點。

## Complexity / 複雜度

- Time: `O(n)`
- Space: `O(n)`

Where:
`n`: number of nodes.


- Typical: `O(n)` for constant-size states. / 常見 `O(n)`。
- Tree knapsack can be `O(n * B^2)`. / 樹上背包更高。

## Related problems / 相關題目

- [q3562](../leetcode/q3562.md)