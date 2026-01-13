# Stack / 堆疊

Goal: support last-in-first-out (LIFO) operations in `O(1)`.
目標：以 `O(1)` 支援後進先出（LIFO）操作。

## Core idea / 核心概念

A stack only allows access to the top element.
堆疊只允許存取頂端元素。

- Push: add to top. / 推入：加入頂端。
- Pop: remove top. / 彈出：移除頂端。
- Peek: read top. / 查看：讀取頂端。

## Operations / 操作

- `push(x)` / `O(1)` (amortized for dynamic arrays)
- `pop()` / `O(1)`
- `peek()` / `O(1)`
- `is_empty()` / `O(1)`

## Typical uses / 常見用途

- Parentheses matching / 括號匹配
- Undo / Redo / 復原與重做
- DFS or recursion simulation / DFS 或遞迴模擬
- Monotonic stack problems / 單調堆疊題型

## Worked example / 實作範例

### Example: valid parentheses / 範例：括號是否合法

Input format / 輸入格式

```
s
```

Output format / 輸出格式

- `true` if valid, else `false`.
  / 若括號正確則輸出 `true`。

Example input / 範例輸入

```
([])()
```

Expected output / 預期輸出

```
true
```

Step-by-step / 步驟

- Read char:
  - Open bracket -> push.
  - Close bracket -> check top and pop.
  / 開括號推入，閉括號比對後彈出。

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let s = input.trim();
    let mut stack: Vec<char> = Vec::new();
    let mut ok = true;

    for ch in s.chars() {
        match ch {
            '(' | '[' | '{' => stack.push(ch),
            ')' | ']' | '}' => {
                let top = stack.pop();
                if top.is_none() {
                    ok = false;
                    break;
                }
                let t = top.unwrap();
                let valid = (ch == ')' && t == '(') || (ch == ']' && t == '[') || (ch == '}' && t == '{');
                if !valid {
                    ok = false;
                    break;
                }
            }
            _ => {}
        }
    }

    if !stack.is_empty() {
        ok = false;
    }
    println!("{}", ok);
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
    stack := []rune{}
    ok := true

    for _, ch := range s {
        switch ch {
        case '(', '[', '{':
            stack = append(stack, ch)
        case ')', ']', '}':
            if len(stack) == 0 {
                ok = false
                break
            }
            t := stack[len(stack)-1]
            stack = stack[:len(stack)-1]
            valid := (ch == ')' && t == '(') || (ch == ']' && t == '[') || (ch == '}' && t == '{')
            if !valid {
                ok = false
                break
            }
        }
    }

    if len(stack) != 0 {
        ok = false
    }
    fmt.Println(ok)
}
```

## Related problems / 相關題目

- `leetcode/q85.md`