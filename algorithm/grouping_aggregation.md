# Grouping and Aggregation / 分組與彙總

Goal: aggregate values by key (count, min, max, sum) in one pass.
目標：以單次掃描完成分組統計。

## Pattern / 流程

1. Use a map from `key -> aggregate`.
   / 使用 `key -> aggregate` 的對映。
2. Update aggregate while scanning.
   / 掃描時更新統計值。
3. Optionally do a second pass using aggregates.
   / 需要時再做第二次掃描。

## Worked Examples / 實作範例

### Example 1: group sums / 範例 1：分組加總

Input format / 輸入格式

```
n
key value
...
```

Output format / 輸出格式

- One line per key: `key sum`, keys sorted.
  / 每行輸出分組總和。

Example input / 範例輸入

```
3
a 3
b 2
a 5
```

Expected output / 預期輸出

```
a 8
b 2
```

Step-by-step / 步驟

- Step 1: sum map is empty.
  / 步驟 1：空的加總表。
- Step 2: add (a,3) -> sum[a]=3.
  / 步驟 2：加入 (a,3)。
- Step 3: add (b,2) -> sum[b]=2.
  / 步驟 3：加入 (b,2)。
- Step 4: add (a,5) -> sum[a]=8.
  / 步驟 4：加入 (a,5)。

State table / 狀態表

```
Step | item   | sum[a] | sum[b]
-----+--------+--------+-------
0    | init   | 0      | 0
1    | (a,3)  | 3      | 0
2    | (b,2)  | 3      | 2
3    | (a,5)  | 8      | 2
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
    let mut sum: HashMap<String, i32> = HashMap::new();
    for _ in 0..n {
        let k = it.next().unwrap().to_string();
        let v: i32 = it.next().unwrap().parse().unwrap();
        *sum.entry(k).or_insert(0) += v;
    }
    let mut keys: Vec<String> = sum.keys().cloned().collect();
    keys.sort();
    for k in keys {
        println!("{} {}", k, sum[&k]);
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
    "sort"
)

func main() {
    in := bufio.NewReader(os.Stdin)
    var n int
    fmt.Fscan(in, &n)
    sum := map[string]int{}
    for i := 0; i < n; i++ {
        var k string
        var v int
        fmt.Fscan(in, &k, &v)
        sum[k] += v
    }
    keys := make([]string, 0, len(sum))
    for k := range sum {
        keys = append(keys, k)
    }
    sort.Strings(keys)
    out := bufio.NewWriter(os.Stdout)
    for _, k := range keys {
        fmt.Fprintf(out, "%s %d\n", k, sum[k])
    }
    out.Flush()
}
```

### Example 2: min/max per group / 範例 2：分組最小最大

Input format / 輸入格式

```
n
key value
...
```

Output format / 輸出格式

- One line per key: `key min max`, keys sorted.
  / 每行輸出最小與最大。

Example input / 範例輸入

```
3
x 4
x 1
y 5
```

Expected output / 預期輸出

```
x 1 4
y 5 5
```

Step-by-step / 步驟

- Step 1: start with empty min/max maps.
  / 步驟 1：空的 min/max。
- Step 2: read (x,4) -> min[x]=4, max[x]=4.
  / 步驟 2：初始化 x。
- Step 3: read (x,1) -> min[x]=1, max[x]=4.
  / 步驟 3：更新 x。
- Step 4: read (y,5) -> min[y]=5, max[y]=5.
  / 步驟 4：初始化 y。

State table / 狀態表

```
Step | item   | min[x] | max[x] | min[y] | max[y]
-----+--------+--------+--------+--------+-------
0    | init   | -      | -      | -      | -
1    | (x,4)  | 4      | 4      | -      | -
2    | (x,1)  | 1      | 4      | -      | -
3    | (y,5)  | 1      | 4      | 5      | 5
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
    let mut minv: HashMap<String, i32> = HashMap::new();
    let mut maxv: HashMap<String, i32> = HashMap::new();
    for _ in 0..n {
        let k = it.next().unwrap().to_string();
        let v: i32 = it.next().unwrap().parse().unwrap();
        let entry_min = minv.entry(k.clone()).or_insert(v);
        if v < *entry_min {
            *entry_min = v;
        }
        let entry_max = maxv.entry(k).or_insert(v);
        if v > *entry_max {
            *entry_max = v;
        }
    }
    let mut keys: Vec<String> = minv.keys().cloned().collect();
    keys.sort();
    for k in keys {
        println!("{} {} {}", k, minv[&k], maxv[&k]);
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
    "sort"
)

func main() {
    in := bufio.NewReader(os.Stdin)
    var n int
    fmt.Fscan(in, &n)
    minv := map[string]int{}
    maxv := map[string]int{}
    for i := 0; i < n; i++ {
        var k string
        var v int
        fmt.Fscan(in, &k, &v)
        mv, ok := minv[k]
        if !ok || v < mv {
            minv[k] = v
        }
        xv, ok := maxv[k]
        if !ok || v > xv {
            maxv[k] = v
        }
    }
    keys := make([]string, 0, len(minv))
    for k := range minv {
        keys = append(keys, k)
    }
    sort.Strings(keys)
    out := bufio.NewWriter(os.Stdout)
    for _, k := range keys {
        fmt.Fprintf(out, "%s %d %d\n", k, minv[k], maxv[k])
    }
    out.Flush()
}
```

## Typical aggregates / 常見彙總

- Count: `cnt[key] += 1` / 計數
- Min/Max: update bounds / 更新最小最大
- Sum: `sum[key] += value` / 累加總和

## Variations / 變化型

- Use arrays if key range is small. / 小範圍用陣列。
- Keep multiple aggregates per key. / 同時維護多種統計。
- Group by computed buckets. / 依規則分桶。

## Pitfalls / 常見陷阱

- Expensive key cloning; prefer references. / 鍵值複製成本高。
- Incorrect initialization for min/max. / 最小最大初始化錯誤。

## Related problems / 相關題目

- [q3531](../leetcode/q3531.md)
- [q3623](../leetcode/q3623.md)