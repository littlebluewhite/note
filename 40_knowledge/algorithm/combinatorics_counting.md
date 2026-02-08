---
title: Combinatorics Counting / 組合計數
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(n)
complexity_space: O(1)
review_interval_days: 14
next_review: 2026-02-17
---
# Combinatorics Counting / 組合計數

Goal: count valid configurations using combinatorial formulas instead of enumeration.
目標：用組合公式取代暴力枚舉。

## Thought process / 思路

- Decide whether order matters. / 先判斷是否計入順序。
- Split into independent choices and multiply. / 拆成獨立選擇後相乘。
- Use algebra to avoid double loops. / 用代數化簡避免雙迴圈。

## Common formulas / 常用公式

- Factorial: `n!` / 階乘：`n!`
- Combinations: `C(n, k) = n! / (k! (n-k)!)` / 組合數
- Pair count: `C(n, 2) = n * (n - 1) / 2` / 兩兩配對
- Sum of pair products across groups:
  - `sum_{i<j} b_i * b_j = (S^2 - sum(b_i^2)) / 2`, `S = sum(b_i)`
  - 組間配對數可用平方和公式計算

## Worked Examples / 實作範例

### Example 1: pairs across groups / 範例 1：組間配對

Input format / 輸入格式

```
n
b1 b2 ... bn
```

Output format / 輸出格式

- Total number of cross-group pairs.
  / 輸出組間配對數。

Example input / 範例輸入

```
3
2 3 5
```

Expected output / 預期輸出

```
31
```

Step-by-step / 步驟

- Step 1: compute total `S = 2 + 3 + 5 = 10`.
  / 步驟 1：總數 `S = 10`。
- Step 2: compute sum of squares `4 + 9 + 25 = 38`.
  / 步驟 2：平方和 `38`。
- Step 3: apply formula `(S^2 - sumsq) / 2`.
  / 步驟 3：套用公式。

State table / 狀態表

```
Value | Result
------+--------
S     | 10
S^2   | 100
sumsq | 38
pairs | 31
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut s: i64 = 0;
    let mut sumsq: i64 = 0;
    for _ in 0..n {
        let x: i64 = it.next().unwrap().parse().unwrap();
        s += x;
        sumsq += x * x;
    }
    let pairs = (s * s - sumsq) / 2;
    println!("{}", pairs);
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
    var s int64 = 0
    var sumsq int64 = 0
    for i := 0; i < n; i++ {
        var x int64
        fmt.Fscan(in, &x)
        s += x
        sumsq += x * x
    }
    pairs := (s*s - sumsq) / 2
    fmt.Println(pairs)
}
```

### Example 2: combinations / 範例 2：組合數

Input format / 輸入格式

```
n k
```

Output format / 輸出格式

- Output `C(n,k)`.
  / 輸出組合數。

Example input / 範例輸入

```
5 3
```

Expected output / 預期輸出

```
10
```

Step-by-step / 步驟

- Step 1: `C(5,3) = 5*4*3 / (3*2*1)`.
  / 步驟 1：寫出公式。
- Step 2: numerator = 60, denominator = 6.
  / 步驟 2：分子 60、分母 6。
- Step 3: result = 10.
  / 步驟 3：答案 10。

State table / 狀態表

```
Value     | Result
----------+--------
Numerator | 60
Denom     | 6
C(5,3)    | 10
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn comb(n: i64, k: i64) -> i64 {
    let k = k.min(n - k);
    let mut num = 1i64;
    let mut den = 1i64;
    for i in 1..=k {
        num *= n - k + i;
        den *= i;
    }
    num / den
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: i64 = it.next().unwrap().parse().unwrap();
    let k: i64 = it.next().unwrap().parse().unwrap();
    println!("{}", comb(n, k));
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

func comb(n, k int64) int64 {
    if k > n-k {
        k = n - k
    }
    var num int64 = 1
    var den int64 = 1
    for i := int64(1); i <= k; i++ {
        num *= n - k + i
        den *= i
    }
    return num / den
}

func main() {
    in := bufio.NewReader(os.Stdin)
    var n, k int64
    fmt.Fscan(in, &n, &k)
    fmt.Println(comb(n, k))
}
```

### Example 3: stars and bars / 範例 3：隔板法

Input format / 輸入格式

```
balls boxes
```

Output format / 輸出格式

- Number of distributions of identical balls into boxes.
  / 輸出分配方式數。

Example input / 範例輸入

```
4 3
```

Expected output / 預期輸出

```
15
```

Step-by-step / 步驟

- Step 1: total positions = `n + k - 1 = 6`.
  / 步驟 1：位置總數 6。
- Step 2: choose `k-1 = 2` bars.
  / 步驟 2：選 2 條隔板。
- Step 3: `C(6,2) = 15`.
  / 步驟 3：答案 15。

State table / 狀態表

```
Value | Result
------+--------
Total | 6
Bars  | 2
Ways  | 15
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn comb(n: i64, k: i64) -> i64 {
    let k = k.min(n - k);
    let mut num = 1i64;
    let mut den = 1i64;
    for i in 1..=k {
        num *= n - k + i;
        den *= i;
    }
    num / den
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let balls: i64 = it.next().unwrap().parse().unwrap();
    let boxes: i64 = it.next().unwrap().parse().unwrap();
    let ways = comb(balls + boxes - 1, boxes - 1);
    println!("{}", ways);
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

func comb(n, k int64) int64 {
    if k > n-k {
        k = n - k
    }
    var num int64 = 1
    var den int64 = 1
    for i := int64(1); i <= k; i++ {
        num *= n - k + i
        den *= i
    }
    return num / den
}

func main() {
    in := bufio.NewReader(os.Stdin)
    var balls, boxes int64
    fmt.Fscan(in, &balls, &boxes)
    fmt.Println(comb(balls+boxes-1, boxes-1))
}
```

## Variations / 變化型

- Precompute factorials + inverse factorials for modulo `MOD`. / 預先計算階乘與反元素。
- "Stars and bars" for distributions. / 隔板法分配。
- Inclusion-exclusion for overcounting. / 容斥原理。

## Complexity / 複雜度

- Time: `O(n)`
- Space: `O(1)`

Where:
`n`: number of values/items.


## Pitfalls / 常見陷阱

- Overflow: use `i64` or `i128`. / 溢位需用較大整數型別。
- Division order matters. / 整除順序要正確。
- Formula must match whether order matters. / 公式要符合是否計序。

## Related problems / 相關題目

- [q2147](../leetcode/q2147.md)
- [q3577](../leetcode/q3577.md)
- [q3623](../leetcode/q3623.md)
- [q3625](../leetcode/q3625.md)