# Sorting by Custom Order / 自訂排序

Goal: sort items by a custom priority and then by a secondary key.
目標：先依自訂優先序，再用次要鍵排序。

## Pattern / 流程

1. Map each category to a rank.
   / 將類別對映到排名。
2. Sort by `(rank, key)` using tuple comparator.
   / 用 `(rank, key)` 排序。

## Worked Examples / 實作範例

### Example 1: category ranking / 範例 1：類別排序

Input format / 輸入格式

```
m
order1 order2 ... orderm
n
cat1 score1
...
catn scoren
```

Output format / 輸出格式

- Sorted items, one per line: `cat score`.
  / 輸出排序後結果。

Example input / 範例輸入

```
3
gold silver bronze
3
silver 2
gold 5
bronze 1
```

Expected output / 預期輸出

```
gold 5
silver 2
bronze 1
```

Step-by-step / 步驟

- Step 1: rank map: gold->0, silver->1, bronze->2.
  / 步驟 1：建立排名表。
- Step 2: map items to `(rank, score)`.
  / 步驟 2：轉成排序鍵。
- Step 3: sort by `(rank, score)`.
  / 步驟 3：排序。

State table / 狀態表

```
Item          | Rank | Key
--------------+------+--------
(silver,2)    | 1    | (1,2)
(gold,5)      | 0    | (0,5)
(bronze,1)    | 2    | (2,1)
Sorted order: (gold,5), (silver,2), (bronze,1)
```

Rust (full program) / Rust（完整程式）

```rust
use std::collections::HashMap;
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let m: usize = it.next().unwrap().parse().unwrap();
    let mut rank: HashMap<String, i32> = HashMap::new();
    for i in 0..m {
        let s = it.next().unwrap().to_string();
        rank.insert(s, i as i32);
    }
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut items: Vec<(String, i32)> = Vec::with_capacity(n);
    for _ in 0..n {
        let cat = it.next().unwrap().to_string();
        let score: i32 = it.next().unwrap().parse().unwrap();
        items.push((cat, score));
    }
    items.sort_by_key(|(cat, score)| (rank[cat], *score));
    for (cat, score) in items {
        println!("{} {}", cat, score);
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

type Item struct {
    cat string
    score int
}

func main() {
    in := bufio.NewReader(os.Stdin)
    var m int
    fmt.Fscan(in, &m)
    rank := map[string]int{}
    for i := 0; i < m; i++ {
        var s string
        fmt.Fscan(in, &s)
        rank[s] = i
    }
    var n int
    fmt.Fscan(in, &n)
    items := make([]Item, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &items[i].cat, &items[i].score)
    }
    sort.Slice(items, func(i, j int) bool {
        if rank[items[i].cat] == rank[items[j].cat] {
            return items[i].score < items[j].score
        }
        return rank[items[i].cat] < rank[items[j].cat]
    })
    out := bufio.NewWriter(os.Stdout)
    for _, it := range items {
        fmt.Fprintf(out, "%s %d\n", it.cat, it.score)
    }
    out.Flush()
}
```

### Example 2: custom string order / 範例 2：字元自訂序

Input format / 輸入格式

```
order
s
```

Output format / 輸出格式

- Sorted string.
  / 輸出排序後字串。

Example input / 範例輸入

```
cba
abcd
```

Expected output / 預期輸出

```
cbad
```

Step-by-step / 步驟

- Step 1: rank: c->0, b->1, a->2, others->3.
  / 步驟 1：建立字元順位。
- Step 2: sort characters by rank.
  / 步驟 2：依排名排序。
- Step 3: result: "cbad".
  / 步驟 3：排序後字串。

State table / 狀態表

```
Char | Rank
-----+-----
a    | 2
b    | 1
c    | 0
d    | 3
```

Rust (full program) / Rust（完整程式）

```rust
use std::collections::HashMap;
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let order = it.next().unwrap();
    let s = it.next().unwrap_or("");
    let mut rank: HashMap<char, i32> = HashMap::new();
    for (i, ch) in order.chars().enumerate() {
        rank.insert(ch, i as i32);
    }
    let mut chars: Vec<char> = s.chars().collect();
    let default_rank = order.len() as i32 + 1;
    chars.sort_by_key(|c| *rank.get(c).unwrap_or(&default_rank));
    let result: String = chars.into_iter().collect();
    println!("{}", result);
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
    var order, s string
    fmt.Fscan(in, &order)
    fmt.Fscan(in, &s)
    rank := map[rune]int{}
    for i, ch := range order {
        rank[ch] = i
    }
    chars := []rune(s)
    defaultRank := len(order) + 1
    sort.Slice(chars, func(i, j int) bool {
        ri, ok := rank[chars[i]]
        if !ok {
            ri = defaultRank
        }
        rj, ok := rank[chars[j]]
        if !ok {
            rj = defaultRank
        }
        return ri < rj
    })
    fmt.Println(string(chars))
}
```

## Variations / 變化型

- Stable sort to preserve original order for ties.
  / 同分需保留原順序時用穩定排序。
- Small rank set can be an array or match. / 小集合可用陣列或 match。

## Pitfalls / 常見陷阱

- Missing rank for a category; define default rank. / 缺排名需給預設。
- Non-transitive comparator causes unstable results. / 比較器需具傳遞性。

## Complexity / 複雜度

- Sorting: `O(n log n)` / 排序：`O(n log n)`
- Rank lookup: `O(1)` / 查排名：`O(1)`

## Related problems / 相關題目

- `leetcode/q3606.md`
