# Two Pointers / 雙指標

Goal: scan from both ends or maintain a moving range in linear time.
目標：用兩個指標線性掃描。

## Common patterns / 常見模式

- Trim invalid prefix/suffix. / 修剪無效前後段。
- Maintain a moving window `[l, r]`. / 維持可變視窗。
- Two-sum on sorted arrays. / 排序後找兩數和。

## Worked Examples / 實作範例

### Example 1: two-sum in sorted array / 範例 1：排序陣列找兩數和

Input format / 輸入格式

```
n target
x1 x2 ... xn
```

Output format / 輸出格式

- If found, output the pair values `a b`, else `not found`.
  / 有解輸出兩數，否則輸出 `not found`。

Example input / 範例輸入

```
5 8
1 2 4 6 10
```

Expected output / 預期輸出

```
2 6
```

Step-by-step / 步驟

- Step 1: l=0, r=4 -> sum=11 > 8, move r.
  / 步驟 1：太大，右指標左移。
- Step 2: l=0, r=3 -> sum=7 < 8, move l.
  / 步驟 2：太小，左指標右移。
- Step 3: l=1, r=3 -> sum=8 found.
  / 步驟 3：找到答案。

State table / 狀態表

```
 l | r | a[l] | a[r] | sum | action
---+---+------+------|-----+--------
 0 | 4 | 1    | 10   | 11  | r--
 0 | 3 | 1    | 6    | 7   | l++
 1 | 3 | 2    | 6    | 8   | found
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let target: i32 = it.next().unwrap().parse().unwrap();
    let mut a = vec![0i32; n];
    for i in 0..n {
        a[i] = it.next().unwrap().parse().unwrap();
    }
    let mut l = 0usize;
    let mut r = n.saturating_sub(1);
    let mut found = false;
    while l < r {
        let sum = a[l] + a[r];
        if sum == target {
            println!("{} {}", a[l], a[r]);
            found = true;
            break;
        } else if sum < target {
            l += 1;
        } else {
            r -= 1;
        }
    }
    if !found {
        println!("not found");
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

func main() {
    in := bufio.NewReader(os.Stdin)
    var n, target int
    fmt.Fscan(in, &n, &target)
    a := make([]int, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &a[i])
    }
    l, r := 0, n-1
    found := false
    for l < r {
        sum := a[l] + a[r]
        if sum == target {
            fmt.Printf("%d %d\n", a[l], a[r])
            found = true
            break
        } else if sum < target {
            l++
        } else {
            r--
        }
    }
    if !found {
        fmt.Println("not found")
    }
}
```

### Example 2: remove duplicates in-place / 範例 2：原地去重

Input format / 輸入格式

```
n
x1 x2 ... xn
```

Output format / 輸出格式

- First line: new length.
- Second line: unique prefix values.
  / 第一行輸出長度，第二行輸出結果。

Example input / 範例輸入

```
5
1 1 2 2 3
```

Expected output / 預期輸出

```
3
1 2 3
```

Step-by-step / 步驟

- Step 1: slow=0, fast scans.
  / 步驟 1：慢指標記錄位置。
- Step 2: when a[fast] != a[slow], advance slow and copy.
  / 步驟 2：遇到新值就寫入。

State table / 狀態表

```
fast | slow | array prefix
-----+------+-------------
0    | 0    | [1]
1    | 0    | [1]
2    | 1    | [1,2]
3    | 1    | [1,2]
4    | 2    | [1,2,3]
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
    if n == 0 {
        println!("0");
        println!();
        return;
    }
    let mut slow = 0usize;
    for fast in 1..n {
        if a[fast] != a[slow] {
            slow += 1;
            a[slow] = a[fast];
        }
    }
    let new_len = slow + 1;
    println!("{}", new_len);
    let mut out = String::new();
    for i in 0..new_len {
        if i > 0 {
            out.push(' ');
        }
        out.push_str(&a[i].to_string());
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
    var n int
    fmt.Fscan(in, &n)
    a := make([]int, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &a[i])
    }
    if n == 0 {
        fmt.Println(0)
        fmt.Println()
        return
    }
    slow := 0
    for fast := 1; fast < n; fast++ {
        if a[fast] != a[slow] {
            slow++
            a[slow] = a[fast]
        }
    }
    newLen := slow + 1
    fmt.Println(newLen)
    out := bufio.NewWriter(os.Stdout)
    for i := 0; i < newLen; i++ {
        if i > 0 {
            fmt.Fprint(out, " ")
        }
        fmt.Fprint(out, a[i])
    }
    fmt.Fprintln(out)
    out.Flush()
}
```

## Variations / 變化型

- Fast/slow pointers to detect cycles. / 快慢指標判環。
- Merge-like scan across two sorted arrays. / 合併式雙指標。

## Pitfalls / 常見陷阱

- Ensure each pointer moves to avoid infinite loops. / 指標必須前進。
- Be explicit about inclusive/exclusive boundaries. / 邊界要明確。

## Complexity / 複雜度

- Each pointer moves at most `n` steps: `O(n)`.
  / 總時間 `O(n)`。

## Related problems / 相關題目

- `leetcode/q2211.md`
