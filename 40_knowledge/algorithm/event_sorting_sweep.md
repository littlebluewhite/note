---
title: Event Sorting Sweep / 事件排序掃描
note_type: knowledge
domain: algorithm
tags: [algorithm, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: algorithm
complexity_time: O(n log n)
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
---
# Event Sorting Sweep / 事件排序掃描

Goal: process time-based events in the correct order with explicit tie-breaking.
目標：依時間排序並明確處理同時事件。

## Pattern / 流程

1. Convert each item to an event `(time, type, payload)`.
   / 將資料轉成事件。
2. Sort by `time`; define tie-breakers.
   / 依時間排序，並設定同時間的優先序。
3. Sweep in order and update state.
   / 依序掃描更新狀態。

## Worked Examples / 實作範例

### Example 1: interval overlap count / 範例 1：區間重疊數

Input format / 輸入格式

```
n
l1 r1
...
ln rn
```

Output format / 輸出格式

- Maximum number of overlapping intervals.
  / 最大重疊數。

Example input / 範例輸入

```
2
1 3
2 4
```

Expected output / 預期輸出

```
2
```

Step-by-step / 步驟

- Step 1: events -> (1,+1), (3,-1), (2,+1), (4,-1).
  / 步驟 1：建立事件。
- Step 2: sort by time, tie: +1 before -1 (closed interval).
  / 步驟 2：同時先進後出。
- Step 3: sweep and track active count.
  / 步驟 3：掃描統計活躍數。

State table / 狀態表

```
Time | Event | Active
-----+-------+--------
1    | +1    | 1
2    | +1    | 2
3    | -1    | 1
4    | -1    | 0
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut events: Vec<(i32, i32)> = Vec::with_capacity(2 * n);
    for _ in 0..n {
        let l: i32 = it.next().unwrap().parse().unwrap();
        let r: i32 = it.next().unwrap().parse().unwrap();
        events.push((l, 1));
        events.push((r, -1));
    }
    events.sort_by(|a, b| if a.0 == b.0 { b.1.cmp(&a.1) } else { a.0.cmp(&b.0) });
    let mut active = 0;
    let mut max_active = 0;
    for (_t, delta) in events {
        active += delta;
        if active > max_active {
            max_active = active;
        }
    }
    println!("{}", max_active);
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

type Event struct {
    t int
    delta int
}

func main() {
    in := bufio.NewReader(os.Stdin)
    var n int
    fmt.Fscan(in, &n)
    events := make([]Event, 0, 2*n)
    for i := 0; i < n; i++ {
        var l, r int
        fmt.Fscan(in, &l, &r)
        events = append(events, Event{l, 1}, Event{r, -1})
    }
    sort.Slice(events, func(i, j int) bool {
        if events[i].t == events[j].t {
            return events[i].delta > events[j].delta
        }
        return events[i].t < events[j].t
    })
    active := 0
    maxActive := 0
    for _, e := range events {
        active += e.delta
        if active > maxActive {
            maxActive = active
        }
    }
    fmt.Println(maxActive)
}
```

### Example 2: meeting rooms / 範例 2：會議室數量

Input format / 輸入格式

```
n
l1 r1
...
ln rn
```

Output format / 輸出格式

- Minimum rooms required.
  / 所需最少會議室數。

Example input / 範例輸入

```
3
1 4
2 3
3 5
```

Expected output / 預期輸出

```
2
```

Step-by-step / 步驟

- Step 1: events -> (1,+1), (4,-1), (2,+1), (3,-1), (3,+1), (5,-1).
  / 步驟 1：建立事件。
- Step 2: tie-break end before start for open intervals.
  / 步驟 2：同時先離開後進入。
- Step 3: sweep to get max active rooms.
  / 步驟 3：掃描取最大值。

State table / 狀態表

```
Time | Event | Active
-----+-------+--------
1    | +1    | 1
2    | +1    | 2
3    | -1    | 1
3    | +1    | 2
4    | -1    | 1
5    | -1    | 0
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut events: Vec<(i32, i32)> = Vec::with_capacity(2 * n);
    for _ in 0..n {
        let l: i32 = it.next().unwrap().parse().unwrap();
        let r: i32 = it.next().unwrap().parse().unwrap();
        events.push((l, 1));
        events.push((r, -1));
    }
    events.sort_by(|a, b| if a.0 == b.0 { a.1.cmp(&b.1) } else { a.0.cmp(&b.0) });
    let mut active = 0;
    let mut max_active = 0;
    for (_t, delta) in events {
        active += delta;
        if active > max_active {
            max_active = active;
        }
    }
    println!("{}", max_active);
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

type Event struct {
    t int
    delta int
}

func main() {
    in := bufio.NewReader(os.Stdin)
    var n int
    fmt.Fscan(in, &n)
    events := make([]Event, 0, 2*n)
    for i := 0; i < n; i++ {
        var l, r int
        fmt.Fscan(in, &l, &r)
        events = append(events, Event{l, 1}, Event{r, -1})
    }
    sort.Slice(events, func(i, j int) bool {
        if events[i].t == events[j].t {
            return events[i].delta < events[j].delta
        }
        return events[i].t < events[j].t
    })
    active := 0
    maxActive := 0
    for _, e := range events {
        active += e.delta
        if active > maxActive {
            maxActive = active
        }
    }
    fmt.Println(maxActive)
}
```

## Variations / 變化型

- Use a min-heap for delayed actions. / 用最小堆排程延遲事件。
- Two-level ordering: `(time, priority, id)`.
  / 多層排序鍵。
- Coordinate compression for large times. / 座標壓縮。

## Pitfalls / 常見陷阱

- Tie-breaking changes answers. / 同時事件順序會影響答案。
- Closed vs open interval off-by-one. / 區間閉開易錯。
- Mixing event types without clear order. / 事件類型順序不清。

## Complexity / 複雜度

- Time: `O(n log n)`
- Space: `O(n)`

Where:
`n`: number of events/intervals.


- Sorting: `O(m log m)` / 排序：`O(m log m)`
- Sweep: `O(m)` or `O(m log m)` with heap. / 掃描：`O(m)` 或 `O(m log m)`

## Related problems / 相關題目

- [q2092](../leetcode/q2092.md)
- [q3433](../leetcode/q3433.md)
- [q3453](../leetcode/q3453.md)
- [q3454](../leetcode/q3454.md)