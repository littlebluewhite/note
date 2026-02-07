---
title: Geometry Line Grouping / 幾何直線分組
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(n^2)
complexity_space: O(n^2)
review_interval_days: 14
next_review: 2026-02-17
canonical: algorithm/geometry_line_grouping.md
---
# Geometry Line Grouping / 幾何直線分組

Goal: group points by line or midpoint to count geometric structures.
目標：用直線或中點分組以計數幾何結構。

## Slope normalization / 斜率正規化

Represent slope as a reduced pair `(dx, dy)`:
用約分後的 `(dx, dy)` 表示斜率。

- `dx = x2 - x1`, `dy = y2 - y1`
- Divide by `g = gcd(|dx|, |dy|)` / 除以最大公因數
- Normalize sign for uniqueness / 統一正負號

## Line identification / 直線辨識

Use invariant:

`c = dy * x - dx * y`

Points on the same line share `(dx, dy, c)`.
同一直線會有相同 `(dx, dy, c)`。

## Midpoint grouping / 中點分組

For points `(x1, y1)`, `(x2, y2)`:

`mid = (x1 + x2, y1 + y2)`

Pairs with same midpoint can form parallelograms.
中點相同的點對可組成平行四邊形。

## Worked Examples / 實作範例

### Example 1: collinear points / 範例 1：共線點

Input format / 輸入格式

```
3
x1 y1
x2 y2
x3 y3
```

Output format / 輸出格式

- Print `true` if collinear, else `false`.
  / 共線輸出 `true`。

Example input / 範例輸入

```
3
0 0
1 1
2 2
```

Expected output / 預期輸出

```
true
```

Step-by-step / 步驟

- Step 1: slope from p0 to p1 -> (1,1).
  / 步驟 1：斜率 (1,1)。
- Step 2: slope from p0 to p2 -> reduce to (1,1).
  / 步驟 2：約分後相同。
- Step 3: same slope and same invariant -> collinear.
  / 步驟 3：判定共線。

State table / 狀態表

```
Pair        | dx | dy | gcd | slope
------------+----+----+-----+-------
(0,0)-(1,1) | 1  | 1  | 1   | (1,1)
(0,0)-(2,2) | 2  | 2  | 2   | (1,1)
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn gcd(mut a: i64, mut b: i64) -> i64 {
    while b != 0 {
        let t = a % b;
        a = b;
        b = t;
    }
    a.abs()
}

fn norm(dx: i64, dy: i64) -> (i64, i64) {
    let g = gcd(dx.abs(), dy.abs());
    let mut dx = dx / g;
    let mut dy = dy / g;
    if dx < 0 || (dx == 0 && dy < 0) {
        dx = -dx;
        dy = -dy;
    }
    (dx, dy)
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let _n: usize = it.next().unwrap().parse().unwrap();
    let x0: i64 = it.next().unwrap().parse().unwrap();
    let y0: i64 = it.next().unwrap().parse().unwrap();
    let x1: i64 = it.next().unwrap().parse().unwrap();
    let y1: i64 = it.next().unwrap().parse().unwrap();
    let x2: i64 = it.next().unwrap().parse().unwrap();
    let y2: i64 = it.next().unwrap().parse().unwrap();
    let s1 = norm(x1 - x0, y1 - y0);
    let s2 = norm(x2 - x0, y2 - y0);
    println!("{}", if s1 == s2 { "true" } else { "false" });
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

func gcd(a, b int64) int64 {
    for b != 0 {
        a, b = b, a%b
    }
    if a < 0 {
        return -a
    }
    return a
}

func abs(x int64) int64 {
    if x < 0 {
        return -x
    }
    return x
}

func norm(dx, dy int64) (int64, int64) {
    g := gcd(abs(dx), abs(dy))
    dx /= g
    dy /= g
    if dx < 0 || (dx == 0 && dy < 0) {
        dx = -dx
        dy = -dy
    }
    return dx, dy
}

func main() {
    in := bufio.NewReader(os.Stdin)
    var n int
    fmt.Fscan(in, &n)
    var x0, y0, x1, y1, x2, y2 int64
    fmt.Fscan(in, &x0, &y0)
    fmt.Fscan(in, &x1, &y1)
    fmt.Fscan(in, &x2, &y2)
    s1x, s1y := norm(x1-x0, y1-y0)
    s2x, s2y := norm(x2-x0, y2-y0)
    if s1x == s2x && s1y == s2y {
        fmt.Println("true")
    } else {
        fmt.Println("false")
    }
}
```

### Example 2: midpoint grouping / 範例 2：中點分組

Input format / 輸入格式

```
4
x1 y1
x2 y2
x3 y3
x4 y4
```

Output format / 輸出格式

- Print `true` if the midpoints of (1,2) and (3,4) are equal.
  / 中點相同輸出 `true`。

Example input / 範例輸入

```
4
0 0
2 0
1 1
1 -1
```

Expected output / 預期輸出

```
true
```

Step-by-step / 步驟

- Step 1: mid(A,B) = (0+2, 0+0) = (2,0).
  / 步驟 1：計算 AB 中點。
- Step 2: mid(C,D) = (1+1, 1-1) = (2,0).
  / 步驟 2：計算 CD 中點。
- Step 3: same midpoint -> can form parallelogram.
  / 步驟 3：中點相同。

State table / 狀態表

```
Pair | midpoint
-----+----------
1-2  | (2,0)
3-4  | (2,0)
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let _n: usize = it.next().unwrap().parse().unwrap();
    let x1: i64 = it.next().unwrap().parse().unwrap();
    let y1: i64 = it.next().unwrap().parse().unwrap();
    let x2: i64 = it.next().unwrap().parse().unwrap();
    let y2: i64 = it.next().unwrap().parse().unwrap();
    let x3: i64 = it.next().unwrap().parse().unwrap();
    let y3: i64 = it.next().unwrap().parse().unwrap();
    let x4: i64 = it.next().unwrap().parse().unwrap();
    let y4: i64 = it.next().unwrap().parse().unwrap();
    let mid12 = (x1 + x2, y1 + y2);
    let mid34 = (x3 + x4, y3 + y4);
    println!("{}", if mid12 == mid34 { "true" } else { "false" });
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
    var x1, y1, x2, y2, x3, y3, x4, y4 int64
    fmt.Fscan(in, &x1, &y1)
    fmt.Fscan(in, &x2, &y2)
    fmt.Fscan(in, &x3, &y3)
    fmt.Fscan(in, &x4, &y4)
    mid12x, mid12y := x1+x2, y1+y2
    mid34x, mid34y := x3+x4, y3+y4
    if mid12x == mid34x && mid12y == mid34y {
        fmt.Println("true")
    } else {
        fmt.Println("false")
    }
}
```

## Variations / 變化型

- Use tuple key `(dx, dy, c)` in hash map. / 用 tuple 當鍵值。
- Use `(x1 + x2, y1 + y2)` to avoid fractions. / 中點避免分數。
- Use `i128` for large coordinates. / 大座標用 `i128`。

## Complexity / 複雜度

- Time: `O(n^2)`
- Space: `O(n^2)`

Where:
`n`: number of points.


## Pitfalls / 常見陷阱

- Always normalize signs consistently. / 正負號必須一致。
- Avoid floating-point slopes. / 避免浮點斜率。
- Overflow in multiplications. / 乘法可能溢位。

## Related problems / 相關題目

- [q3625](../leetcode/q3625.md)