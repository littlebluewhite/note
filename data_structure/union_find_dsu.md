# Union-Find (DSU) / 並查集

Goal: maintain disjoint sets with fast union and find operations.
目標：快速合併集合並查詢元素所屬集合。

## Core idea / 核心概念

Each set is a tree. The root is the representative.
每個集合是一棵樹，根節點為代表。

## Operations / 操作

- `find(x)`: return the representative. / 回傳集合代表。
- `union(a, b)`: merge two sets. / 合併兩個集合。
- `same(a, b)`: check if in same set. / 判斷是否同集合。

## Diagram & Visual Explanation / 圖示與視覺化說明

Before union / 合併前：

```
0   1   2   3   4
|   |   |   |   |
0   1   2   3   4
```

After `union(0,1)`, `union(1,2)`, `union(3,4)` / 合併後：

```
0       3
|       |
1       4
|
2
```

Path compression flattens trees, making future `find` faster.
路徑壓縮會把節點直接接到根，之後查找更快。

## Worked Examples / 實作範例

### Example 1: connectivity queries / 範例 1：連通性查詢

Input format / 輸入格式

```
n m q
u1 v1
...
um vm
x1 y1
...
q queries
```

Output format / 輸出格式

- One line per query: `true`/`false`.
  / 每個查詢輸出一行。

Example input / 範例輸入

```
5 3 2
0 1
1 2
3 4
0 2
0 4
```

Expected output / 預期輸出

```
true
false
```

Step-by-step / 步驟

- Step 1: each node is its own parent.
  / 步驟 1：每個節點自成一集合。
- Step 2: union(0,1) -> parent[1]=0.
  / 步驟 2：合併 0 與 1。
- Step 3: union(1,2) -> parent[2]=0.
  / 步驟 3：合併 1 與 2。
- Step 4: union(3,4) -> parent[4]=3.
  / 步驟 4：合併 3 與 4。

State table / 狀態表

```
Step | parent[0..4]
-----+-----------------
0    | [0,1,2,3,4]
1    | [0,0,2,3,4]
2    | [0,0,0,3,4]
3    | [0,0,0,3,3]
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

struct DSU {
    parent: Vec<usize>,
}

impl DSU {
    fn new(n: usize) -> Self {
        let mut parent = Vec::with_capacity(n);
        for i in 0..n {
            parent.push(i);
        }
        Self { parent }
    }

    fn find(&mut self, x: usize) -> usize {
        if self.parent[x] != x {
            let root = self.find(self.parent[x]);
            self.parent[x] = root;
        }
        self.parent[x]
    }

    fn union(&mut self, a: usize, b: usize) {
        let ra = self.find(a);
        let rb = self.find(b);
        if ra != rb {
            self.parent[rb] = ra;
        }
    }

    fn same(&mut self, a: usize, b: usize) -> bool {
        self.find(a) == self.find(b)
    }
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let m: usize = it.next().unwrap().parse().unwrap();
    let q: usize = it.next().unwrap().parse().unwrap();
    let mut dsu = DSU::new(n);
    for _ in 0..m {
        let a: usize = it.next().unwrap().parse().unwrap();
        let b: usize = it.next().unwrap().parse().unwrap();
        dsu.union(a, b);
    }
    for _ in 0..q {
        let a: usize = it.next().unwrap().parse().unwrap();
        let b: usize = it.next().unwrap().parse().unwrap();
        println!("{}", if dsu.same(a, b) { "true" } else { "false" });
    }
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

type DSU struct {
    parent []int
}

func NewDSU(n int) *DSU {
    p := make([]int, n)
    for i := 0; i < n; i++ {
        p[i] = i
    }
    return &DSU{parent: p}
}

func (d *DSU) Find(x int) int {
    if d.parent[x] != x {
        d.parent[x] = d.Find(d.parent[x])
    }
    return d.parent[x]
}

func (d *DSU) Union(a, b int) {
    ra, rb := d.Find(a), d.Find(b)
    if ra != rb {
        d.parent[rb] = ra
    }
}

func (d *DSU) Same(a, b int) bool {
    return d.Find(a) == d.Find(b)
}

func main() {
    in := bufio.NewReader(os.Stdin)
    out := bufio.NewWriter(os.Stdout)
    defer out.Flush()

    var n, m, q int
    fmt.Fscan(in, &n, &m, &q)
    dsu := NewDSU(n)
    for i := 0; i < m; i++ {
        var a, b int
        fmt.Fscan(in, &a, &b)
        dsu.Union(a, b)
    }
    for i := 0; i < q; i++ {
        var a, b int
        fmt.Fscan(in, &a, &b)
        if dsu.Same(a, b) {
            fmt.Fprintln(out, "true")
        } else {
            fmt.Fprintln(out, "false")
        }
    }
}
```

### Example 2: component size / 範例 2：查詢集合大小

Input format / 輸入格式

```
n m q
u1 v1
...
um vm
x1
...
xq
```

Output format / 輸出格式

- One line per query: size of component containing x.
  / 每個查詢輸出集合大小。

Example input / 範例輸入

```
4 3 2
0 1
2 3
0 2
0
3
```

Expected output / 預期輸出

```
4
4
```

Step-by-step / 步驟

- Step 1: each node has size 1.
  / 步驟 1：每個集合大小為 1。
- Step 2: union(0,1) -> size[root]=2.
  / 步驟 2：合併 0 與 1。
- Step 3: union(2,3) -> size[root]=2.
  / 步驟 3：合併 2 與 3。
- Step 4: union(0,2) -> size[root]=4.
  / 步驟 4：合併兩個大小為 2 的集合。

State table / 狀態表

```
Step | parent[0..3] | size[0..3]
-----+--------------+------------
0    | [0,1,2,3]    | [1,1,1,1]
1    | [0,0,2,3]    | [2,1,1,1]
2    | [0,0,2,2]    | [2,1,2,1]
3    | [0,0,0,2]    | [4,1,2,1]
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

struct DSU {
    parent: Vec<usize>,
    size: Vec<usize>,
}

impl DSU {
    fn new(n: usize) -> Self {
        let mut parent = Vec::with_capacity(n);
        for i in 0..n {
            parent.push(i);
        }
        Self { parent, size: vec![1; n] }
    }

    fn find(&mut self, x: usize) -> usize {
        if self.parent[x] != x {
            let root = self.find(self.parent[x]);
            self.parent[x] = root;
        }
        self.parent[x]
    }

    fn union(&mut self, a: usize, b: usize) {
        let mut ra = self.find(a);
        let mut rb = self.find(b);
        if ra == rb {
            return;
        }
        if self.size[ra] < self.size[rb] {
            std::mem::swap(&mut ra, &mut rb);
        }
        self.parent[rb] = ra;
        self.size[ra] += self.size[rb];
    }

    fn size_of(&mut self, x: usize) -> usize {
        let r = self.find(x);
        self.size[r]
    }
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let m: usize = it.next().unwrap().parse().unwrap();
    let q: usize = it.next().unwrap().parse().unwrap();
    let mut dsu = DSU::new(n);
    for _ in 0..m {
        let a: usize = it.next().unwrap().parse().unwrap();
        let b: usize = it.next().unwrap().parse().unwrap();
        dsu.union(a, b);
    }
    for _ in 0..q {
        let x: usize = it.next().unwrap().parse().unwrap();
        println!("{}", dsu.size_of(x));
    }
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

type DSU struct {
    parent []int
    size   []int
}

func NewDSU(n int) *DSU {
    p := make([]int, n)
    s := make([]int, n)
    for i := 0; i < n; i++ {
        p[i] = i
        s[i] = 1
    }
    return &DSU{parent: p, size: s}
}

func (d *DSU) Find(x int) int {
    if d.parent[x] != x {
        d.parent[x] = d.Find(d.parent[x])
    }
    return d.parent[x]
}

func (d *DSU) Union(a, b int) {
    ra, rb := d.Find(a), d.Find(b)
    if ra == rb {
        return
    }
    if d.size[ra] < d.size[rb] {
        ra, rb = rb, ra
    }
    d.parent[rb] = ra
    d.size[ra] += d.size[rb]
}

func (d *DSU) SizeOf(x int) int {
    r := d.Find(x)
    return d.size[r]
}

func main() {
    in := bufio.NewReader(os.Stdin)
    out := bufio.NewWriter(os.Stdout)
    defer out.Flush()

    var n, m, q int
    fmt.Fscan(in, &n, &m, &q)
    dsu := NewDSU(n)
    for i := 0; i < m; i++ {
        var a, b int
        fmt.Fscan(in, &a, &b)
        dsu.Union(a, b)
    }
    for i := 0; i < q; i++ {
        var x int
        fmt.Fscan(in, &x)
        fmt.Fprintln(out, dsu.SizeOf(x))
    }
}
```

## Optimizations / 優化

- Path compression. / 路徑壓縮。
- Union by size/rank. / 依大小或秩合併。

With both, operations are effectively `O(alpha(n))`.
兩者同時使用時近似 `O(alpha(n))`。

## Variations / 變化型

- Keep component size for size queries. / 維護集合大小。
- Rollback DSU for offline dynamic connectivity. / 可回滾 DSU。
- Map-based DSU for non-0..n-1 nodes. / 非連續節點用 `HashMap`。

## Pitfalls / 常見陷阱

- `find` should be mutable to apply compression. / `find` 需可變以壓縮。
- For rollback, avoid compression or log changes. / 回滾時需記錄修改。
- Be consistent with indexing. / 索引基準要一致。

## Complexity / 複雜度

- Amortized: `O(alpha(n))` / 攤還：`O(alpha(n))`

## Related problems / 相關題目

- `leetcode/q2092.md`