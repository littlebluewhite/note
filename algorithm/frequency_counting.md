# Frequency Counting / 次數統計

Goal: count occurrences efficiently, often with a fixed value range.
目標：快速統計出現次數。

## Thought process / 思路

- Small range: use array. / 範圍小用陣列。
- Sparse keys: use hash map. / 稀疏用雜湊。

## Pattern / 模式

- Use `freq[value]` for bounded domains.
  / 範圍固定用陣列。
- For two-sided counts, keep `left` and `right`:
  / 左右兩邊計數：
  - Initialize `right` with all counts.
  - For each index, move from `right` to `left`.

## Worked Examples / 實作範例

### Example 1: simple count / 範例 1：基本計數

Input format / 輸入格式

```
n maxVal
x1 x2 ... xn
```

Output format / 輸出格式

- For each value `v` from 0..maxVal, output `v count`.
  / 逐一輸出 0..maxVal 的次數。

Example input / 範例輸入

```
4 3
1 2 1 3
```

Expected output / 預期輸出

```
0 0
1 2
2 1
3 1
```

Step-by-step / 步驟

- Step 1: init `freq` to zeros.
  / 步驟 1：頻率陣列清零。
- Step 2: read values and increment `freq[value]`.
  / 步驟 2：讀入並累加。

State table / 狀態表

```
Step | x | freq[1] | freq[2] | freq[3]
-----+---+---------+---------+--------
0    | - | 0       | 0       | 0
1    | 1 | 1       | 0       | 0
2    | 2 | 1       | 1       | 0
3    | 1 | 2       | 1       | 0
4    | 3 | 2       | 1       | 1
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let max_val: usize = it.next().unwrap().parse().unwrap();
    let mut freq = vec![0i64; max_val + 1];
    for _ in 0..n {
        let x: usize = it.next().unwrap().parse().unwrap();
        freq[x] += 1;
    }
    for v in 0..=max_val {
        println!("{} {}", v, freq[v]);
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
    var n, maxVal int
    fmt.Fscan(in, &n, &maxVal)
    freq := make([]int, maxVal+1)
    for i := 0; i < n; i++ {
        var x int
        fmt.Fscan(in, &x)
        freq[x]++
    }
    out := bufio.NewWriter(os.Stdout)
    for v := 0; v <= maxVal; v++ {
        fmt.Fprintf(out, "%d %d\n", v, freq[v])
    }
    out.Flush()
}
```

### Example 2: left/right split / 範例 2：左右分割

Input format / 輸入格式

```
n
x1 x2 ... xn
```

Output format / 輸出格式

- For each index, output `left_count current_value right_count current_value`.
  / 每個位置輸出該值左右次數。

Example input / 範例輸入

```
3
1 2 1
```

Expected output / 預期輸出

```
1 1
1 0
2 0
```

Step-by-step / 步驟

- Step 1: right counts = {1:2, 2:1}, left empty.
  / 步驟 1：右邊計數初始化。
- Step 2: move index 0 (1) -> left {1:1}, right {1:1,2:1}.
  / 步驟 2：移動第一個 1。
- Step 3: move index 1 (2) -> left {1:1,2:1}, right {1:1}.
  / 步驟 3：移動 2。
- Step 4: move index 2 (1) -> left {1:2,2:1}, right {}.
  / 步驟 4：移動最後的 1。

State table / 狀態表

```
Idx | val | left[val] | right[val]
----+-----+-----------+-----------
0   | 1   | 1         | 1
1   | 2   | 1         | 0
2   | 1   | 2         | 0
```

Rust (full program) / Rust（完整程式）

```rust
use std::collections::HashMap;
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut nums = Vec::with_capacity(n);
    for _ in 0..n {
        let x: i32 = it.next().unwrap().parse().unwrap();
        nums.push(x);
    }

    let mut left: HashMap<i32, i32> = HashMap::new();
    let mut right: HashMap<i32, i32> = HashMap::new();
    for &x in &nums {
        *right.entry(x).or_insert(0) += 1;
    }

    for &x in &nums {
        if let Some(v) = right.get_mut(&x) {
            *v -= 1;
            if *v == 0 {
                right.remove(&x);
            }
        }
        *left.entry(x).or_insert(0) += 1;
        let l = *left.get(&x).unwrap_or(&0);
        let r = *right.get(&x).unwrap_or(&0);
        println!("{} {}", l, r);
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
    var n int
    fmt.Fscan(in, &n)
    nums := make([]int, n)
    right := map[int]int{}
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &nums[i])
        right[nums[i]]++
    }
    left := map[int]int{}
    out := bufio.NewWriter(os.Stdout)
    for i := 0; i < n; i++ {
        x := nums[i]
        right[x]--
        if right[x] == 0 {
            delete(right, x)
        }
        left[x]++
        fmt.Fprintf(out, "%d %d\n", left[x], right[x])
    }
    out.Flush()
}
```

## Variations / 變化型

- Prefix counts per value for many range queries. / 每個值做前綴計數。
- Bitset for boolean presence. / bitset 表示存在性。

## Pitfalls / 常見陷阱

- Range too large for arrays. / 範圍太大需改用雜湊。
- Use `i64` for counts to avoid overflow. / 計數用 `i64`。

## Complexity / 複雜度

- Array access: `O(1)` / 陣列存取 `O(1)`
- Full scan: `O(n)` / 掃描 `O(n)`

## Related problems / 相關題目

- `leetcode/q3583.md`