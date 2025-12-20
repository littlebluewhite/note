# Monotonic Queue / 單調隊列

Goal: maintain window min/max in `O(1)` amortized time.
目標：在滑動視窗中維持最小/最大值。

## Core idea / 核心概念

Use a deque of indices and keep it monotonic.
用雙端佇列存索引並保持單調性。

- Max: keep values decreasing. / 最大值：遞減。
- Min: keep values increasing. / 最小值：遞增。

Each index enters and leaves once.
每個索引只進出一次。

## Steps (max queue) / 步驟（最大值）

1. Pop from back while `a[back] <= a[r]`.
2. Push `r`.
3. Pop front if outside window.
4. Front is current maximum.

## Worked Examples / 實作範例

### Example 1: max in window / 範例 1：視窗最大值

Input format / 輸入格式

```
n k
x1 x2 ... xn
```

Output format / 輸出格式

- Window maximums separated by spaces.
  / 以空白輸出每個視窗最大值。

Example input / 範例輸入

```
4 2
1 3 2 5
```

Expected output / 預期輸出

```
3 3 5
```

Step-by-step / 步驟

- Step 1: r=0 -> deque [0].
  / 步驟 1：加入 index 0。
- Step 2: r=1 -> pop 0 (1<=3), deque [1].
  / 步驟 2：維持遞減。
- Step 3: r=2 -> deque [1,2], window [1,2] max=3.
  / 步驟 3：更新視窗。
- Step 4: r=3 -> pop 2 and 1, deque [3], max=5.
  / 步驟 4：最大值為 5。

State table / 狀態表

```
 r | deque(idx) | window | max
---+------------+--------+-----
 0 | [0]        | [0,0]  | 1
 1 | [1]        | [0,1]  | 3
 2 | [1,2]      | [1,2]  | 3
 3 | [3]        | [2,3]  | 5
```

Rust (full program) / Rust（完整程式）

```rust
use std::collections::VecDeque;
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

    let mut dq: VecDeque<usize> = VecDeque::new();
    let mut res: Vec<i32> = Vec::new();
    for r in 0..n {
        while let Some(&back) = dq.back() {
            if a[back] <= a[r] {
                dq.pop_back();
            } else {
                break;
            }
        }
        dq.push_back(r);
        if let Some(&front) = dq.front() {
            if front + k <= r {
                dq.pop_front();
            }
        }
        if r + 1 >= k {
            res.push(a[*dq.front().unwrap()]);
        }
    }

    let mut out = String::new();
    for (i, v) in res.iter().enumerate() {
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

func main() {
    in := bufio.NewReader(os.Stdin)
    var n, k int
    fmt.Fscan(in, &n, &k)
    a := make([]int, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &a[i])
    }
    dq := []int{}
    res := []int{}
    for r := 0; r < n; r++ {
        for len(dq) > 0 && a[dq[len(dq)-1]] <= a[r] {
            dq = dq[:len(dq)-1]
        }
        dq = append(dq, r)
        if dq[0]+k <= r {
            dq = dq[1:]
        }
        if r+1 >= k {
            res = append(res, a[dq[0]])
        }
    }
    out := bufio.NewWriter(os.Stdout)
    for i, v := range res {
        if i > 0 {
            fmt.Fprint(out, " ")
        }
        fmt.Fprint(out, v)
    }
    fmt.Fprintln(out)
    out.Flush()
}
```

### Example 2: min in window / 範例 2：視窗最小值

Input format / 輸入格式

```
n k
x1 x2 ... xn
```

Output format / 輸出格式

- Window minimums separated by spaces.
  / 以空白輸出每個視窗最小值。

Example input / 範例輸入

```
4 3
4 2 2 6
```

Expected output / 預期輸出

```
2 2
```

Step-by-step / 步驟

- Step 1: r=0 -> deque [0].
  / 步驟 1：加入 index 0。
- Step 2: r=1 -> pop 0 (4>=2), deque [1].
  / 步驟 2：維持遞增。
- Step 3: r=2 -> deque [1,2], min=2.
  / 步驟 3：視窗最小值 2。
- Step 4: r=3 -> remove out-of-window, min=2.
  / 步驟 4：最小值仍為 2。

State table / 狀態表

```
 r | deque(idx) | window | min
---+------------+--------+-----
 0 | [0]        | [0,0]  | 4
 1 | [1]        | [0,1]  | 2
 2 | [1,2]      | [0,2]  | 2
 3 | [1,2,3]    | [1,3]  | 2
```

Rust (full program) / Rust（完整程式）

```rust
use std::collections::VecDeque;
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

    let mut dq: VecDeque<usize> = VecDeque::new();
    let mut res: Vec<i32> = Vec::new();
    for r in 0..n {
        while let Some(&back) = dq.back() {
            if a[back] >= a[r] {
                dq.pop_back();
            } else {
                break;
            }
        }
        dq.push_back(r);
        if let Some(&front) = dq.front() {
            if front + k <= r {
                dq.pop_front();
            }
        }
        if r + 1 >= k {
            res.push(a[*dq.front().unwrap()]);
        }
    }

    let mut out = String::new();
    for (i, v) in res.iter().enumerate() {
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

func main() {
    in := bufio.NewReader(os.Stdin)
    var n, k int
    fmt.Fscan(in, &n, &k)
    a := make([]int, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &a[i])
    }
    dq := []int{}
    res := []int{}
    for r := 0; r < n; r++ {
        for len(dq) > 0 && a[dq[len(dq)-1]] >= a[r] {
            dq = dq[:len(dq)-1]
        }
        dq = append(dq, r)
        if dq[0]+k <= r {
            dq = dq[1:]
        }
        if r+1 >= k {
            res = append(res, a[dq[0]])
        }
    }
    out := bufio.NewWriter(os.Stdout)
    for i, v := range res {
        if i > 0 {
            fmt.Fprint(out, " ")
        }
        fmt.Fprint(out, v)
    }
    fmt.Fprintln(out)
    out.Flush()
}
```

## Variations / 變化型

- Reverse comparisons for min queue. / 反向比較得到最小值。
- Two queues to keep both min and max. / 同時維護最小與最大。

## Pitfalls / 常見陷阱

- Store indices, not values. / 存索引以判斷過期。
- Off-by-one on window size. / 視窗大小錯誤。

## Complexity / 複雜度

- Total `O(n)` / 總時間 `O(n)`

## Related problems / 相關題目

- `leetcode/q3578.md`
