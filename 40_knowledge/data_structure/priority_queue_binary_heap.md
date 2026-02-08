---
title: Priority Queue (Binary Heap) / 優先佇列（二元堆）
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: data_structure
complexity_time: O(log n) push/pop, O(1) peek
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-02-17
---
# Priority Queue (Binary Heap) / 優先佇列（二元堆）

Goal: get the min or max element with `O(log n)` updates.
目標：以 `O(log n)` 維護最大或最小元素。

## Core idea / 核心概念

A binary heap keeps a partial order so the top is always accessible.
二元堆維持局部有序，堆頂永遠是最大或最小。

- Max-heap: parent >= children / 最大堆：父 >= 子
- Min-heap: parent <= children / 最小堆：父 <= 子

## Operations / 操作

- Push: `O(log n)` / 插入：`O(log n)`
- Pop top: `O(log n)` / 取出堆頂：`O(log n)`
- Peek top: `O(1)` / 查看堆頂：`O(1)`

## Typical uses / 常見用途

- Top-k elements. / 取前 k 大或小。
- Dijkstra / A* (min-heap by distance). / 最短路徑。
- Scheduling by priority. / 依優先序排程。

## Worked Examples / 實作範例

### Example 1: top-k largest / 範例 1：取前 k 大

Input format / 輸入格式

```
n k
x1 x2 ... xn
```

Output format / 輸出格式

- Print the k largest values in pop order (descending).
  / 依彈出順序輸出。

Example input / 範例輸入

```
5 2
5 1 4 2 9
```

Expected output / 預期輸出

```
9 5
```

Step-by-step / 步驟

- Step 1: push all numbers into max-heap.
  / 步驟 1：全部推入最大堆。
- Step 2: pop k times.
  / 步驟 2：彈出 k 次。

State table / 狀態表

```
Step | Operation | Heap top | Popped
-----+-----------+----------+--------
1    | push 5    | 5        | -
2    | push 1    | 5        | -
3    | push 4    | 5        | -
4    | push 2    | 5        | -
5    | push 9    | 9        | -
6    | pop       | 5        | 9
7    | pop       | 4        | 5
```

Rust (full program) / Rust（完整程式）

```rust
use std::collections::BinaryHeap;
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let k: usize = it.next().unwrap().parse().unwrap();
    let mut heap = BinaryHeap::new();
    for _ in 0..n {
        let x: i32 = it.next().unwrap().parse().unwrap();
        heap.push(x);
    }
    let mut out = String::new();
    for i in 0..k {
        if let Some(v) = heap.pop() {
            if i > 0 {
                out.push(' ');
            }
            out.push_str(&v.to_string());
        }
    }
    println!("{}", out);
}
```

Go (full program) / Go（完整程式）

```go
package main

import (
    "bufio"
    "container/heap"
    "fmt"
    "os"
)

type MaxHeap []int

func (h MaxHeap) Len() int           { return len(h) }
func (h MaxHeap) Less(i, j int) bool { return h[i] > h[j] }
func (h MaxHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *MaxHeap) Push(x interface{}) { *h = append(*h, x.(int)) }
func (h *MaxHeap) Pop() interface{} {
    old := *h
    n := len(old)
    v := old[n-1]
    *h = old[:n-1]
    return v
}

func main() {
    in := bufio.NewReader(os.Stdin)
    var n, k int
    fmt.Fscan(in, &n, &k)
    h := &MaxHeap{}
    heap.Init(h)
    for i := 0; i < n; i++ {
        var x int
        fmt.Fscan(in, &x)
        heap.Push(h, x)
    }
    out := bufio.NewWriter(os.Stdout)
    for i := 0; i < k; i++ {
        v := heap.Pop(h).(int)
        if i > 0 {
            fmt.Fprint(out, " ")
        }
        fmt.Fprint(out, v)
    }
    fmt.Fprintln(out)
    out.Flush()
}
```

### Example 2: min-heap scheduling / 範例 2：最早完成排程

Input format / 輸入格式

```
n
time name
...
```

Output format / 輸出格式

- One line per task in completion order: `time name`.
  / 每行輸出完成順序。

Example input / 範例輸入

```
3
1 A
3 B
2 C
```

Expected output / 預期輸出

```
1 A
2 C
3 B
```

Step-by-step / 步驟

- Step 1: push tasks into min-heap by time.
  / 步驟 1：依時間推入最小堆。
- Step 2: pop all tasks in order.
  / 步驟 2：依序彈出。

State table / 狀態表

```
Step | Operation  | Heap top | Popped
-----+------------+----------+--------
1    | push (1,A) | (1,A)    | -
2    | push (3,B) | (1,A)    | -
3    | push (2,C) | (1,A)    | -
4    | pop        | (2,C)    | (1,A)
5    | pop        | (3,B)    | (2,C)
6    | pop        | -        | (3,B)
```

Rust (full program) / Rust（完整程式）

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut heap: BinaryHeap<Reverse<(i32, String)>> = BinaryHeap::new();
    for _ in 0..n {
        let t: i32 = it.next().unwrap().parse().unwrap();
        let name = it.next().unwrap().to_string();
        heap.push(Reverse((t, name)));
    }
    while let Some(Reverse((t, name))) = heap.pop() {
        println!("{} {}", t, name);
    }
}
```

Go (full program) / Go（完整程式）

```go
package main

import (
    "bufio"
    "container/heap"
    "fmt"
    "os"
)

type Task struct {
    t int
    name string
}

type MinHeap []Task

func (h MinHeap) Len() int           { return len(h) }
func (h MinHeap) Less(i, j int) bool { return h[i].t < h[j].t }
func (h MinHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *MinHeap) Push(x interface{}) { *h = append(*h, x.(Task)) }
func (h *MinHeap) Pop() interface{} {
    old := *h
    n := len(old)
    v := old[n-1]
    *h = old[:n-1]
    return v
}

func main() {
    in := bufio.NewReader(os.Stdin)
    out := bufio.NewWriter(os.Stdout)
    defer out.Flush()

    var n int
    fmt.Fscan(in, &n)
    h := &MinHeap{}
    heap.Init(h)
    for i := 0; i < n; i++ {
        var t int
        var name string
        fmt.Fscan(in, &t, &name)
        heap.Push(h, Task{t: t, name: name})
    }
    for h.Len() > 0 {
        task := heap.Pop(h).(Task)
        fmt.Fprintf(out, "%d %s\n", task.t, task.name)
    }
}
```

## Variations / 變化型

- Store `(priority, value)` tuples. / 存 `(priority, value)`。
- Tie-break with tuple ordering, e.g. `(end_time, room_id)` for earliest finish then smallest id.
  / 用 tuple 排序做 tie-break，例如 `(end_time, room_id)` 先看結束時間再看編號。
- Use `Reverse` or custom `Ord` for min-heap. / 用 `Reverse` 或自訂排序。
- Lazy deletion for "decrease-key" workflows. / 懶刪除取代原地更新。

## Complexity / 複雜度

- Time: `O(log n) push/pop, O(1) peek`
- Space: `O(n)`

Where:
`n`: number of elements in the heap.


## Pitfalls / 常見陷阱

- Updating priorities in-place is not supported. / 不能直接更新權重。
- Comparisons must be total order; handle ties. / 比較需具備全序。

## Notes (Rust) / 註記

- `BinaryHeap` is max-heap by default. / `BinaryHeap` 預設為最大堆。
- Use `Reverse` to simulate min-heap. / 使用 `Reverse` 模擬最小堆。
- `BinaryHeap<Reverse<(i64, usize)>>` provides a min-heap with tuple tie-breaking.
  / `BinaryHeap<Reverse<(i64, usize)>>` 可做最小堆並依 tuple 進行 tie-break。

## Related problems / 相關題目

- [q2402](../leetcode/q2402.md)
- [q3433](../leetcode/q3433.md)
- [q3650](../leetcode/q3650.md)