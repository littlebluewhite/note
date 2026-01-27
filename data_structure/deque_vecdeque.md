# Deque (VecDeque) / 雙端佇列

Goal: push and pop at both ends in `O(1)` amortized time.
目標：兩端都能在 `O(1)` 攤還時間進出。

## When to use / 何時使用

- Sliding window algorithms. / 滑動視窗演算法。
- BFS variants (e.g., 0-1 BFS). / BFS 變形（如 0-1 BFS）。
- Workflows needing both front and back operations. / 需要同時操作頭尾。

## Operations (Rust) / 操作

- `push_front`, `push_back`
- `pop_front`, `pop_back`
- `front`, `back`

## Worked Examples / 實作範例

### Example 1: basic operations / 範例 1：基本操作

Input format / 輸入格式

```
q
command [value]
...
```

Commands: `push_front x`, `push_back x`, `pop_front`, `pop_back`

Output format / 輸出格式

- Print popped values line by line. / 每次 pop 輸出一行。

Example input / 範例輸入

```
4
push_back 1
push_front 2
pop_back
pop_front
```

Expected output / 預期輸出

```
1
2
```

Step-by-step / 步驟

- Step 1: start with empty deque.
  / 步驟 1：空佇列。
- Step 2: `push_back(1)`.
  / 步驟 2：從尾端加入 1。
- Step 3: `push_front(2)`.
  / 步驟 3：從頭端加入 2。
- Step 4: `pop_back()` -> 1.
  / 步驟 4：尾端移除得到 1。
- Step 5: `pop_front()` -> 2.
  / 步驟 5：頭端移除得到 2。

State table / 狀態表

```
Step | Operation     | Deque
-----+---------------+---------
0    | init          | []
1    | push_back(1)  | [1]
2    | push_front(2) | [2,1]
3    | pop_back()    | [2]
4    | pop_front()   | []
```

Rust (full program) / Rust（完整程式）

```rust
use std::collections::VecDeque;
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let q: usize = it.next().unwrap().parse().unwrap();
    let mut dq: VecDeque<i32> = VecDeque::new();
    let mut out = String::new();

    for _ in 0..q {
        let cmd = it.next().unwrap();
        match cmd {
            "push_front" => {
                let x: i32 = it.next().unwrap().parse().unwrap();
                dq.push_front(x);
            }
            "push_back" => {
                let x: i32 = it.next().unwrap().parse().unwrap();
                dq.push_back(x);
            }
            "pop_front" => {
                let v = dq.pop_front().map(|x| x.to_string()).unwrap_or("empty".to_string());
                out.push_str(&v);
                out.push('\n');
            }
            "pop_back" => {
                let v = dq.pop_back().map(|x| x.to_string()).unwrap_or("empty".to_string());
                out.push_str(&v);
                out.push('\n');
            }
            _ => {}
        }
    }
    print!("{}", out);
}
```

Go (full program) / Go（完整程式）

```go
package main

import (
    "bufio"
    "container/list"
    "fmt"
    "os"
)

func main() {
    in := bufio.NewReader(os.Stdin)
    out := bufio.NewWriter(os.Stdout)
    defer out.Flush()

    var q int
    fmt.Fscan(in, &q)
    dq := list.New()

    for i := 0; i < q; i++ {
        var cmd string
        fmt.Fscan(in, &cmd)
        switch cmd {
        case "push_front":
            var x int
            fmt.Fscan(in, &x)
            dq.PushFront(x)
        case "push_back":
            var x int
            fmt.Fscan(in, &x)
            dq.PushBack(x)
        case "pop_front":
            e := dq.Front()
            if e == nil {
                fmt.Fprintln(out, "empty")
            } else {
                fmt.Fprintln(out, e.Value.(int))
                dq.Remove(e)
            }
        case "pop_back":
            e := dq.Back()
            if e == nil {
                fmt.Fprintln(out, "empty")
            } else {
                fmt.Fprintln(out, e.Value.(int))
                dq.Remove(e)
            }
        }
    }
}
```

### Example 2: palindrome check / 範例 2：回文檢查

Input format / 輸入格式

```
s
```

Output format / 輸出格式

- Print `true` if palindrome, else `false`.
  / 回文輸出 `true`，否則 `false`。

Example input / 範例輸入

```
level
```

Expected output / 預期輸出

```
true
```

Step-by-step / 步驟

- Step 1: load chars into deque.
  / 步驟 1：將字元依序放入 deque。
- Step 2: compare front and back each round.
  / 步驟 2：每輪取頭尾比較。
- Step 3: if all equal, it is a palindrome.
  / 步驟 3：全部相等則為回文。

State table / 狀態表

```
Round | Deque        | Front | Back | Match
------+--------------+-------+------+------
1     | [l,e,v,e,l]  | l     | l    | yes
2     | [e,v,e]      | e     | e    | yes
3     | [v]          | v     | v    | yes
```

Rust (full program) / Rust（完整程式）

```rust
use std::collections::VecDeque;
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let s = input.split_whitespace().next().unwrap_or("");
    let mut dq: VecDeque<char> = s.chars().collect();
    let mut ok = true;
    while dq.len() > 1 {
        let f = dq.pop_front().unwrap();
        let b = dq.pop_back().unwrap();
        if f != b {
            ok = false;
            break;
        }
    }
    println!("{}", if ok { "true" } else { "false" });
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
    var s string
    fmt.Fscan(in, &s)
    runes := []rune(s)
    l, r := 0, len(runes)-1
    ok := true
    for l < r {
        if runes[l] != runes[r] {
            ok = false
            break
        }
        l++
        r--
    }
    if ok {
        fmt.Println("true")
    } else {
        fmt.Println("false")
    }
}
```

## Variations / 變化型

- Manual ring buffer for tighter control. / 手寫環狀陣列以控制效能。
- Use `Vec` as a stack when only one end is needed. / 只需一端時用 `Vec`。

## Pitfalls / 常見陷阱

- `Vec` + `remove(0)` is `O(n)`; use `VecDeque`. / `Vec` 刪頭是 `O(n)`。
- Indexing into `VecDeque` can be slower than `Vec`. / 直接索引效能較差。

## Complexity / 複雜度

- Push/pop front/back: `O(1)` amortized / 頭尾進出：`O(1)` 攤還
- Access front/back: `O(1)` / 讀頭尾：`O(1)`

## Related problems / 相關題目

- [q1161](../leetcode/q1161.md)
- [q1970](../leetcode/q1970.md)
- [q3578](../leetcode/q3578.md)