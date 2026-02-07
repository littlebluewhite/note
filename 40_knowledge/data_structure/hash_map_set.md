---
title: Hash Map / Hash Set / 雜湊表與集合
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: data_structure
complexity_time: O(1) avg per op
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
canonical: data_structure/hash_map_set.md
---
# Hash Map / Hash Set / 雜湊表與集合

Goal: store keys for fast lookup and aggregation.
目標：快速查詢與統計鍵值。

## When to use / 何時使用

- Need average `O(1)` insert/lookup. / 需要平均 `O(1)` 查詢與插入。
- Keys are sparse or not suitable for array indexing. / 鍵值稀疏，不適合用陣列。

## HashMap / 雜湊表

- Key -> value mapping. / 鍵值對映。
- Common for counts, min/max, sums, grouping. / 常用於計數、最值、總和、分組。

## HashSet / 雜湊集合

- Store unique keys. / 儲存唯一鍵值。
- Useful for membership tests and deduplication. / 適合判斷存在與去重。

## Worked Examples / 實作範例

### Example 1: frequency count / 範例 1：次數統計

Input format / 輸入格式

```
n
x1 x2 ... xn
```

Output format / 輸出格式

- One line per key: `key count`, keys in ascending order.
  / 每行一個鍵值，依序輸出。

Example input / 範例輸入

```
4
1 2 1 3
```

Expected output / 預期輸出

```
1 2
2 1
3 1
```

Step-by-step / 步驟

- Step 1: start with empty map.
  / 步驟 1：空的計數表。
- Step 2: read 1 -> count[1]=1.
  / 步驟 2：讀到 1。
- Step 3: read 2 -> count[2]=1.
  / 步驟 3：讀到 2。
- Step 4: read 1 -> count[1]=2.
  / 步驟 4：再讀到 1。
- Step 5: read 3 -> count[3]=1.
  / 步驟 5：讀到 3。

State table / 狀態表

```
Step | x | count[1] | count[2] | count[3]
-----+---+----------+----------+---------
0    | - | 0        | 0        | 0
1    | 1 | 1        | 0        | 0
2    | 2 | 1        | 1        | 0
3    | 1 | 2        | 1        | 0
4    | 3 | 2        | 1        | 1
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
    let mut cnt: HashMap<i32, i32> = HashMap::new();
    for _ in 0..n {
        let x: i32 = it.next().unwrap().parse().unwrap();
        *cnt.entry(x).or_insert(0) += 1;
    }
    let mut keys: Vec<i32> = cnt.keys().cloned().collect();
    keys.sort();
    for k in keys {
        println!("{} {}", k, cnt[&k]);
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
    cnt := map[int]int{}
    for i := 0; i < n; i++ {
        var x int
        fmt.Fscan(in, &x)
        cnt[x]++
    }
    keys := make([]int, 0, len(cnt))
    for k := range cnt {
        keys = append(keys, k)
    }
    sort.Ints(keys)
    out := bufio.NewWriter(os.Stdout)
    for _, k := range keys {
        fmt.Fprintf(out, "%d %d\n", k, cnt[k])
    }
    out.Flush()
}
```

### Example 2: group sums / 範例 2：分組加總

Input format / 輸入格式

```
n
key value
...
```

Output format / 輸出格式

- One line per key: `key sum`, keys sorted lexicographically.
  / 每行一個鍵值，字典序輸出。

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

### Example 3: membership test / 範例 3：存在性判斷

Input format / 輸入格式

```
n
set elements...
q
queries...
```

Output format / 輸出格式

- Print `true`/`false` per query.
  / 每個查詢輸出一行。

Example input / 範例輸入

```
3
2 5 7
2
5 4
```

Expected output / 預期輸出

```
true
false
```

Step-by-step / 步驟

- Step 1: insert 2, 5, 7 into set.
  / 步驟 1：插入 2、5、7。
- Step 2: query 5 -> found.
  / 步驟 2：查詢 5 -> 存在。
- Step 3: query 4 -> not found.
  / 步驟 3：查詢 4 -> 不存在。

State table / 狀態表

```
Query | In set?
------+--------
5     | yes
4     | no
```

Rust (full program) / Rust（完整程式）

```rust
use std::collections::HashSet;
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut set: HashSet<i32> = HashSet::new();
    for _ in 0..n {
        let x: i32 = it.next().unwrap().parse().unwrap();
        set.insert(x);
    }
    let q: usize = it.next().unwrap().parse().unwrap();
    for _ in 0..q {
        let x: i32 = it.next().unwrap().parse().unwrap();
        println!("{}", if set.contains(&x) { "true" } else { "false" });
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
    set := map[int]bool{}
    for i := 0; i < n; i++ {
        var x int
        fmt.Fscan(in, &x)
        set[x] = true
    }
    var q int
    fmt.Fscan(in, &q)
    out := bufio.NewWriter(os.Stdout)
    for i := 0; i < q; i++ {
        var x int
        fmt.Fscan(in, &x)
        if set[x] {
            fmt.Fprintln(out, "true")
        } else {
            fmt.Fprintln(out, "false")
        }
    }
    out.Flush()
}
```

## Variations / 變化型

- `BTreeMap` / `BTreeSet` for ordered keys. / 有序鍵值改用樹狀結構。
- Use counts to simulate a multiset. / 用計數模擬多重集合。
- Pre-allocate with `with_capacity` if size is known. / 已知大小可預先配置。

## Pitfalls / 常見陷阱

- Hashing floats is unreliable due to NaN/precision. / 浮點數有 NaN 與精度問題。
- Worst-case can degrade; consider ordered maps if needed. / 最壞情況退化。
- Large keys can be expensive to clone. / 大型鍵值複製成本高。

## Complexity / 複雜度

- Time: `O(1) avg per op`
- Space: `O(n)`

Where:
`n`: number of stored keys.


- Average insert/lookup: `O(1)` / 平均：`O(1)`
- Worst-case: `O(n)` / 最壞：`O(n)`

## Related problems / 相關題目

- [q756](../leetcode/q756.md)
- [q2092](../leetcode/q2092.md)
- [q2977](../leetcode/q2977.md)
- [q3531](../leetcode/q3531.md)
- [q3606](../leetcode/q3606.md)
- [q3623](../leetcode/q3623.md)
- [q3625](../leetcode/q3625.md)