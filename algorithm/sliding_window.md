---
title: "Sliding Window / 滑動視窗"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(n)
complexity_space: O(1)
---
# Sliding Window / 滑動視窗

Goal: scan a contiguous subarray with two pointers in linear time.
目標：用雙指標線性掃描連續區間。

## Two patterns / 兩種模式

- Fixed length: move both ends each step. / 固定長度視窗。
- Variable length: expand `r`, shrink `l` when invalid. / 可變長度。

## Typical loop / 常見模板

```
l = 0
for r in 0..n:
    add(a[r])
    while !valid():
        remove(a[l]); l += 1
    update_answer()
```

## Worked Examples / 實作範例

### Example 1: shortest subarray with sum >= S / 範例 1：最短滿足總和

Input format / 輸入格式

```
n S
x1 x2 ... xn
```

Output format / 輸出格式

- Minimum length (assume a solution exists).
  / 輸出最短長度。

Example input / 範例輸入

```
6 7
2 3 1 2 4 3
```

Expected output / 預期輸出

```
2
```

Step-by-step / 步驟

- Step 1: expand `r` and add values until sum >= S.
  / 步驟 1：右指標擴張。
- Step 2: shrink from left to minimize length while valid.
  / 步驟 2：左指標縮小。

State table / 狀態表

```
 r | l | sum | window      | best
---+---+-----+-------------+-----
 0 | 0 | 2   | [2]         | inf
 1 | 0 | 5   | [2,3]       | inf
 2 | 0 | 6   | [2,3,1]     | inf
 3 | 0 | 8   | [2,3,1,2]   | 4
 3 | 1 | 6   | [3,1,2]     | 4
 4 | 1 | 10  | [3,1,2,4]   | 4
 4 | 2 | 7   | [1,2,4]     | 3
 4 | 3 | 6   | [2,4]       | 3
 5 | 3 | 9   | [2,4,3]     | 3
 5 | 4 | 7   | [4,3]       | 2
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let s: i32 = it.next().unwrap().parse().unwrap();
    let mut a = vec![0i32; n];
    for i in 0..n {
        a[i] = it.next().unwrap().parse().unwrap();
    }
    let mut l = 0usize;
    let mut sum = 0i32;
    let mut best = i32::MAX;
    for r in 0..n {
        sum += a[r];
        while sum >= s {
            let len = (r - l + 1) as i32;
            if len < best {
                best = len;
            }
            sum -= a[l];
            l += 1;
        }
    }
    println!("{}", best);
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
    var n, s int
    fmt.Fscan(in, &n, &s)
    a := make([]int, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &a[i])
    }
    l := 0
    sum := 0
    best := 1<<31 - 1
    for r := 0; r < n; r++ {
        sum += a[r]
        for sum >= s {
            if r-l+1 < best {
                best = r - l + 1
            }
            sum -= a[l]
            l++
        }
    }
    fmt.Println(best)
}
```

### Example 2: max sum of length k / 範例 2：固定長度最大和

Input format / 輸入格式

```
n k
x1 x2 ... xn
```

Output format / 輸出格式

- Maximum window sum.
  / 輸出最大和。

Example input / 範例輸入

```
5 3
2 1 5 1 3
```

Expected output / 預期輸出

```
9
```

Step-by-step / 步驟

- Step 1: compute sum of first k elements.
  / 步驟 1：先算第一個視窗。
- Step 2: slide by removing left, adding right.
  / 步驟 2：滑動視窗更新。

State table / 狀態表

```
Window | Sum
-------+----
[2,1,5] | 8
[1,5,1] | 7
[5,1,3] | 9
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let k: usize = it.next().unwrap().parse().unwrap();
    let mut a = vec![0i32; n];
    for i in 0..n {
        a[i] = it.next().unwrap().parse().unwrap();
    }
    let mut sum: i32 = a[0..k].iter().sum();
    let mut best = sum;
    for i in k..n {
        sum += a[i] - a[i - k];
        if sum > best {
            best = sum;
        }
    }
    println!("{}", best);
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
    var n, k int
    fmt.Fscan(in, &n, &k)
    a := make([]int, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &a[i])
    }
    sum := 0
    for i := 0; i < k; i++ {
        sum += a[i]
    }
    best := sum
    for i := k; i < n; i++ {
        sum += a[i] - a[i-k]
        if sum > best {
            best = sum
        }
    }
    fmt.Println(best)
}
```

### Example 3: minimum range after sorting / 範例 3：排序後固定長度最小範圍

Problem: pick `k` elements so that max-min is minimized.
題目：選 `k` 個元素，使最大值減最小值最小。

Core steps / 核心步驟

- Sort the array, then scan every length-`k` window.
  / 先排序，再掃描每個長度為 `k` 的視窗。
- Range of a window is `a[i+k-1] - a[i]`.
  / 視窗範圍為 `a[i+k-1] - a[i]`。

Template / 範本

```
sort(a)
best = +inf
for i in 0..=n-k:
    best = min(best, a[i+k-1] - a[i])
```

## Variations / 變化型

- Combine with monotonic queue for min/max constraints.
  / 搭配單調隊列。
- Two pointers on sorted arrays. / 排序後雙指標。

## Pitfalls / 常見陷阱

- Define validity condition clearly. / 規則不清會出錯。
- Forgetting to remove `a[l]` when moving `l`. / 移動左邊忘了移除。
- Infinite loops if pointers do not move. / 指標不前進。

## Complexity / 複雜度

- Time: `O(n)`
- Space: `O(1)`

Where:
`n`: number of elements.

- Each pointer moves at most `n` steps: `O(n)`.
  / 總時間 `O(n)`。

## Related problems / 相關題目

- [q3578](../leetcode/q3578.md)
- [q3652](../leetcode/q3652.md)
- [q1984](../leetcode/q1984.md)
- [q3634](../leetcode/q3634.md)
