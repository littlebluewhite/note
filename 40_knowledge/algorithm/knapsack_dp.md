---
title: Knapsack DP / 背包動態規劃
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(n * B)
complexity_space: O(B)
review_interval_days: 14
next_review: 2026-02-17
---
# Knapsack DP / 背包動態規劃

Goal: maximize value (or count ways) under a cost/weight limit.
目標：在容量限制內取得最大價值（或計數方式）。

## 0/1 Knapsack / 0/1 背包

- `dp[c] = max value with total cost exactly c`
  / `dp[c]` 表示總成本剛好為 `c` 的最大價值
- Initialize `dp[0] = 0`, others to `NEG`.
  / 初始化。
- For each item `(cost, value)`, iterate `c` from high to low.
  / 迭代容量由大到小。

## Complete Knapsack / 完全背包

- Each item can be used multiple times.
  / 每個物品可重複使用。
- Iterate `c` from low to high.
  / 容量由小到大。

## Bounded Knapsack / 有限背包

- Each item has limited count.
  / 每個物品有數量上限。
- Use binary splitting to convert to 0/1 items.
  / 二進位拆分。

## Worked Examples / 實作範例

### Example 1: 0/1 maximize value / 範例 1：0/1 最大價值

Input format / 輸入格式

```
n B
cost1 value1
...
costn valuen
```

Output format / 輸出格式

- Maximum value.
  / 輸出最大價值。

Example input / 範例輸入

```
2 5
2 3
3 4
```

Expected output / 預期輸出

```
7
```

Step-by-step / 步驟

- Step 1: dp[0]=0, others = -INF.
  / 步驟 1：初始化 dp。
- Step 2: process item (2,3), update from c=5..2.
  / 步驟 2：處理第一個物品。
- Step 3: process item (3,4), update from c=5..3.
  / 步驟 3：處理第二個物品。

State table / 狀態表

```
After item (2,3):
 c: 0 1 2 3 4 5
 dp:0 - 3 - - -

After item (3,4):
 c: 0 1 2 3 4 5
 dp:0 - 3 4 - 7
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let b: usize = it.next().unwrap().parse().unwrap();
    let mut items = Vec::with_capacity(n);
    for _ in 0..n {
        let c: usize = it.next().unwrap().parse().unwrap();
        let v: i32 = it.next().unwrap().parse().unwrap();
        items.push((c, v));
    }
    let mut dp = vec![i32::MIN / 4; b + 1];
    dp[0] = 0;
    for (cost, val) in items {
        for c in (cost..=b).rev() {
            dp[c] = dp[c].max(dp[c - cost] + val);
        }
    }
    let ans = dp.iter().cloned().max().unwrap();
    println!("{}", ans);
}
```

Go (full program) / Go（完整程式）

```go
package main

import (
    "bufio"
    "fmt"
    "math"
    "os"
)

func main() {
    in := bufio.NewReader(os.Stdin)
    var n, b int
    fmt.Fscan(in, &n, &b)
    items := make([][2]int, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &items[i][0], &items[i][1])
    }
    dp := make([]int, b+1)
    for i := range dp {
        dp[i] = math.MinInt / 4
    }
    dp[0] = 0
    for _, it := range items {
        cost, val := it[0], it[1]
        for c := b; c >= cost; c-- {
            if dp[c-cost]+val > dp[c] {
                dp[c] = dp[c-cost] + val
            }
        }
    }
    best := dp[0]
    for _, v := range dp {
        if v > best {
            best = v
        }
    }
    fmt.Println(best)
}
```

### Example 2: complete knapsack (coin change) / 範例 2：完全背包（換錢）

Input format / 輸入格式

```
target m
c1 c2 ... cm
```

Output format / 輸出格式

- Number of ways.
  / 輸出方式數。

Example input / 範例輸入

```
4 2
1 3
```

Expected output / 預期輸出

```
2
```

Step-by-step / 步驟

- Step 1: dp[0]=1.
  / 步驟 1：dp[0]=1。
- Step 2: coin=1, fill dp from low to high.
  / 步驟 2：用硬幣 1。
- Step 3: coin=3, update dp from low to high.
  / 步驟 3：用硬幣 3。

State table / 狀態表

```
After coin 1:
 dp: [1,1,1,1,1]
After coin 3:
 dp: [1,1,1,2,2]
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let target: usize = it.next().unwrap().parse().unwrap();
    let m: usize = it.next().unwrap().parse().unwrap();
    let mut coins = Vec::with_capacity(m);
    for _ in 0..m {
        let c: usize = it.next().unwrap().parse().unwrap();
        coins.push(c);
    }
    let mut dp = vec![0i64; target + 1];
    dp[0] = 1;
    for c in coins {
        for s in c..=target {
            dp[s] += dp[s - c];
        }
    }
    println!("{}", dp[target]);
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
    var target, m int
    fmt.Fscan(in, &target, &m)
    coins := make([]int, m)
    for i := 0; i < m; i++ {
        fmt.Fscan(in, &coins[i])
    }
    dp := make([]int64, target+1)
    dp[0] = 1
    for _, c := range coins {
        for s := c; s <= target; s++ {
            dp[s] += dp[s-c]
        }
    }
    fmt.Println(dp[target])
}
```

### Example 3: bounded knapsack / 範例 3：有限背包

Input format / 輸入格式

```
B
cost value count
```

Output format / 輸出格式

- Maximum value.
  / 輸出最大價值。

Example input / 範例輸入

```
6
2 3 3
```

Expected output / 預期輸出

```
9
```

Step-by-step / 步驟

- Step 1: split count 3 into 1 + 2.
  / 步驟 1：二進位拆分為 1 與 2。
- Step 2: items become (2,3) and (4,6).
  / 步驟 2：轉成 0/1 物品。
- Step 3: run 0/1 knapsack on split items.
  / 步驟 3：套用 0/1 背包。

State table / 狀態表

```
count=3 -> 1 + 2
items: (2,3), (4,6)
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let b: usize = it.next().unwrap().parse().unwrap();
    let cost: usize = it.next().unwrap().parse().unwrap();
    let value: i32 = it.next().unwrap().parse().unwrap();
    let mut count: usize = it.next().unwrap().parse().unwrap();

    let mut items = Vec::new();
    let mut k = 1usize;
    while count > 0 {
        let take = k.min(count);
        items.push((cost * take, value * take as i32));
        count -= take;
        k <<= 1;
    }

    let mut dp = vec![i32::MIN / 4; b + 1];
    dp[0] = 0;
    for (c, v) in items {
        for s in (c..=b).rev() {
            dp[s] = dp[s].max(dp[s - c] + v);
        }
    }
    let ans = dp.iter().cloned().max().unwrap();
    println!("{}", ans);
}
```

Go (full program) / Go（完整程式）

```go
package main

import (
    "bufio"
    "fmt"
    "math"
    "os"
)

func main() {
    in := bufio.NewReader(os.Stdin)
    var b, cost, value, count int
    fmt.Fscan(in, &b)
    fmt.Fscan(in, &cost, &value, &count)

    items := [][2]int{}
    k := 1
    for count > 0 {
        take := k
        if take > count {
            take = count
        }
        items = append(items, [2]int{cost * take, value * take})
        count -= take
        k <<= 1
    }

    dp := make([]int, b+1)
    for i := range dp {
        dp[i] = math.MinInt / 4
    }
    dp[0] = 0
    for _, it := range items {
        c, v := it[0], it[1]
        for s := b; s >= c; s-- {
            if dp[s-c]+v > dp[s] {
                dp[s] = dp[s-c] + v
            }
        }
    }
    best := dp[0]
    for _, v := range dp {
        if v > best {
            best = v
        }
    }
    fmt.Println(best)
}
```

## Variations / 變化型

- Count ways: replace max with `+` and use modulo.
  / 改成計數題。
- Multi-dimensional knapsack. / 多維背包。
- Tree knapsack: merge child arrays. / 樹上背包合併。

## Pitfalls / 常見陷阱

- Wrong iteration order (0/1 vs complete). / 迭代方向錯誤。
- Using `-INF` too small and causing overflow. / `-INF` 太小。
- Unclear definition: "exactly" vs "at most". / 定義不清。

## Complexity / 複雜度

- Time: `O(n * B)` / 時間：`O(n * B)`
- Space: `O(B)` / 空間：`O(B)`

## Related problems / 相關題目

- [q3562](../leetcode/q3562.md)