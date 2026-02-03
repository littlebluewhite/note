---
title: "DP / Dynamic Programming (動態規劃)"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(S * T)
complexity_space: O(S)
---
# DP / Dynamic Programming (動態規劃)

Goal: solve problems with optimal substructure + overlapping subproblems by avoiding recomputation.
目標：利用「最佳子結構 + 重疊子問題」，避免重複計算。

## When to consider DP / 何時考慮 DP

- Need max/min/count results. / 需求是最大、最小或計數。
- Problem can be split into smaller subproblems. / 可拆成更小子問題。
- Subproblems repeat. / 子問題會重複。

## Standard workflow (5 steps) / 標準流程（五步）

1. Define state: what does `dp[state]` mean?
   / 定義狀態：`dp[state]` 代表什麼。
2. Transition: how to derive from smaller states?
   / 轉移方程怎麼來。
3. Base cases: minimal subproblem answers.
   / 初始條件。
4. Order: ensure dependencies are ready.
   / 計算順序。
5. Answer location: which state is final?
   / 最終答案位置。

## Quick intuition / 思路小抄

- Decide dimensions: time/position/choices.
  / 先決定維度：時間、位置、選擇數等。
- Find the "last step" or split point.
  / 找「最後一步」或「分割點」。
- Consider space compression if order allows.
  / 若依賴順序允許，可做空間壓縮。

## Worked Examples / 實作範例

### Example 1: House Robber / 範例 1：打家劫舍

Input format / 輸入格式

```
n
a1 a2 ... an
```

Output format / 輸出格式

- Maximum sum without adjacent picks.
  / 不可相鄰的最大總和。

Example input / 範例輸入

```
5
2 7 9 3 1
```

Expected output / 預期輸出

```
12
```

State / 狀態

- `dp[i]` = max money from first `i` houses.
  / `dp[i]` 表示前 `i` 間房子的最大金額。

Transition / 轉移

- `dp[i] = max(dp[i-1], dp[i-2] + a[i-1])`
  / 不偷第 i 間或偷第 i 間。

Step-by-step / 步驟

- Step 1: base `dp[0]=0`, `dp[1]=2`.
  / 步驟 1：基底。
- Step 2: `dp[2]=max(2,0+7)=7`.
  / 步驟 2：計算 dp[2]。
- Step 3: `dp[3]=max(7,2+9)=11`.
  / 步驟 3：計算 dp[3]。
- Step 4: `dp[4]=max(11,7+3)=11`.
  / 步驟 4：計算 dp[4]。
- Step 5: `dp[5]=max(11,11+1)=12`.
  / 步驟 5：計算 dp[5]。

State table / 狀態表

```
i  | 0  1  2  3  4  5
---+----------------
a  | -  2  7  9  3  1
dp | 0  2  7 11 11 12
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut a = vec![0i32; n];
    for i in 0..n {
        a[i] = it.next().unwrap().parse().unwrap();
    }
    let mut dp = vec![0i32; n + 1];
    if n >= 1 {
        dp[1] = a[0];
    }
    for i in 2..=n {
        dp[i] = dp[i - 1].max(dp[i - 2] + a[i - 1]);
    }
    println!("{}", dp[n]);
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
    var n int
    fmt.Fscan(in, &n)
    a := make([]int, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &a[i])
    }
    dp := make([]int, n+1)
    if n >= 1 {
        dp[1] = a[0]
    }
    for i := 2; i <= n; i++ {
        take := dp[i-2] + a[i-1]
        skip := dp[i-1]
        if take > skip {
            dp[i] = take
        } else {
            dp[i] = skip
        }
    }
    fmt.Println(dp[n])
}
```

### Example 2: Fibonacci / 範例 2：費波那契

Input format / 輸入格式

```
n
```

Output format / 輸出格式

- Output `F[n]`.
  / 輸出第 n 項。

Example input / 範例輸入

```
5
```

Expected output / 預期輸出

```
5
```

State / 狀態

- `F[i] = F[i-1] + F[i-2]` with `F[0]=0`, `F[1]=1`.
  / 基本定義。

Step-by-step / 步驟

- Step 1: F[0]=0, F[1]=1.
  / 步驟 1：基底。
- Step 2: F[2]=1, F[3]=2, F[4]=3, F[5]=5.
  / 步驟 2：依序計算。

State table / 狀態表

```
i  | 0 1 2 3 4 5
---+------------
F  | 0 1 1 2 3 5
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let n: usize = input.split_whitespace().next().unwrap().parse().unwrap();
    let mut f = vec![0i64; n + 1];
    if n >= 1 {
        f[1] = 1;
    }
    for i in 2..=n {
        f[i] = f[i - 1] + f[i - 2];
    }
    println!("{}", f[n]);
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
    var n int
    fmt.Fscan(in, &n)
    f := make([]int64, n+1)
    if n >= 1 {
        f[1] = 1
    }
    for i := 2; i <= n; i++ {
        f[i] = f[i-1] + f[i-2]
    }
    fmt.Println(f[n])
}
```

### Example 3: Grid paths / 範例 3：網格路徑數

Input format / 輸入格式

```
rows cols
```

Output format / 輸出格式

- Number of paths from (0,0) to (r-1,c-1).
  / 輸出路徑數。

Example input / 範例輸入

```
3 3
```

Expected output / 預期輸出

```
6
```

State / 狀態

- `dp[r][c] = dp[r-1][c] + dp[r][c-1]` with first row/col = 1.
  / 每格由上與左相加。

Step-by-step / 步驟

- Step 1: initialize first row/col to 1.
  / 步驟 1：第一行與第一列為 1。
- Step 2: fill remaining cells by transition.
  / 步驟 2：依序填表。

State table / 狀態表

```
1 1 1
1 2 3
1 3 6
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let m: usize = it.next().unwrap().parse().unwrap();
    let mut dp = vec![vec![1i64; m]; n];
    for i in 1..n {
        for j in 1..m {
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1];
        }
    }
    println!("{}", dp[n - 1][m - 1]);
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
    dp := make([][]int64, n)
    for i := 0; i < n; i++ {
        dp[i] = make([]int64, m)
        for j := 0; j < m; j++ {
            dp[i][j] = 1
        }
    }
    for i := 1; i < n; i++ {
        for j := 1; j < m; j++ {
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
        }
    }
    fmt.Println(dp[n-1][m-1])
}
```

## Diagram & Visual Explanation / 圖示與視覺化說明

Example array / 範例陣列：`a = [2, 7, 9, 3, 1]`

```
i:   0  1  2  3  4  5
 a:  -  2  7  9  3  1
 dp: 0  2  7 11 11 12
```

Each `dp[i]` depends only on `dp[i-1]` and `dp[i-2]`.
每個狀態只依賴前兩格，因此可以壓縮空間。

## Pattern-based Row DP (Fixed-Width Grid) / 固定寬度的列狀態 DP

Goal: handle `n x m` grids with small `m` by enumerating row states and transitions.
目標：當欄數 `m` 很小時，用列狀態枚舉與列間轉移處理 `n x m` 網格。

### Core idea / 核心想法

- Treat each row as a state (colors/choices). / 以「一列」作為狀態。
- Filter row states by horizontal constraints. / 先保留橫向合法狀態。
- Transition only between vertically compatible states. / 只在縱向相容的狀態間轉移。
- Group symmetric states by pattern to shrink transitions. / 用型態分組縮小轉移表。

### Workflow / 流程

1. Enumerate all row states (`k^m`) and keep those valid within the row.
   / 枚舉所有列狀態並保留橫向合法者。
2. Precompute transitions between states that satisfy vertical constraints.
   / 預先計算縱向相容的轉移。
3. DP by rows: `next[s2] += cur[s1]`.
   / 逐列做 DP 累加。
4. Apply modulo and optional space compression.
   / 取模並視情況壓縮空間。

### Mini example (3 colors, width 3) / 小範例（三色、寬度 3）

- Valid rows fall into two patterns: `ABA` (two colors) and `ABC` (three distinct).
  / 合法列可分成 `ABA` 與 `ABC` 兩種型態。
- Transition counts depend only on pattern: `ABC -> ABC` 2, `ABC -> ABA` 2, `ABA -> ABC` 2, `ABA -> ABA` 3.
  / 轉移數只與型態有關：2、2、2、3。
- So DP can be reduced to two counters.
  / 因此可壓縮成兩個計數器。

### Complexity / 複雜度

- Time: `O(S * T)`
- Space: `O(S)`

Where:
`S`: number of states.
`T`: transition cost per state.


- States: `O(k^m)`, transitions: `O(S^2)`, DP: `O(n * transitions)`.
  / 狀態數與欄數 `m` 指數相關，`m` 小時可行。

## Top-down vs Bottom-up / 自上而下 vs 自下而上

- Top-down: recursion + memoization; easy but watch depth.
  / 遞迴 + 記憶化，需注意遞迴深度。
- Bottom-up: iterative table filling; stable and compressible.
  / 迴圈填表，效能穩定易壓縮。

## Common DP types / 常見 DP 類型

- 1D sequence DP. / 一維序列 DP。
- 2D grid DP. / 二維網格 DP。
- Interval DP. / 區間 DP。
- Knapsack DP. / 背包 DP。
- Tree DP. / 樹 DP。
- Bitmask DP. / 位元壓 DP。
- DAG DP. / DAG 上 DP。

## Optimizations / 常見優化

- Prefix sums or differences. / 前綴和或差分。
- Monotonic queues. / 單調隊列。
- Divide and conquer DP. / 分治 DP。
- Convex hull trick. / 斜率優化。

## Update order hints / 更新順序要點

- 0/1 knapsack: iterate capacity high to low.
  / 0/1 背包容量由大到小。
- Complete knapsack: iterate low to high.
  / 完全背包容量由小到大。
- Multi-state DP: use `next_*` to avoid contamination.
  / 多狀態用 `next_*` 避免污染。

## Pitfalls / 常見陷阱

- Missing base states (e.g., `dp[0]=1`). / 初值缺失。
- Wrong iteration order. / 迭代順序錯誤。
- Overflow or negative modulo. / 溢位或負數取模。
- State too large. / 狀態空間過大。

## Complexity intuition / 複雜度心法

- Count states first, then multiply by transition cost.
  / 先估狀態數，再乘轉移成本。
- Compress space only if dependency order is safe.
  / 確認依賴順序後再壓縮。

## Related problems / 相關題目

- [q712](../leetcode/q712.md)
- [q1411](../leetcode/q1411.md)
- [q1458](../leetcode/q1458.md)
- [q2110](../leetcode/q2110.md)
- [q2147](../leetcode/q2147.md)
- [q2977](../leetcode/q2977.md)
- [q3562](../leetcode/q3562.md)
- [q3573](../leetcode/q3573.md)
- [q3578](../leetcode/q3578.md)
- [q3651](../leetcode/q3651.md)