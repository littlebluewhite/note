# Prefix Sum / 前綴和

Goal: answer range sum/count queries in `O(1)` after `O(n)` preprocessing.
目標：先處理 `O(n)` 後，區間查詢 `O(1)`。

## Definition / 定義

- `prefix[0] = 0`
- `prefix[i + 1] = prefix[i] + a[i]`
- Range sum `[l, r]` = `prefix[r + 1] - prefix[l]`
  / 區間和 `[l, r]` 的計算方式

## Worked Examples / 實作範例

### Example 1: range sum / 範例 1：區間總和

Input format / 輸入格式

```
n
x1 x2 ... xn
l r
```

Output format / 輸出格式

- Output sum of `[l, r]` (0-based, inclusive).
  / 輸出區間總和。

Example input / 範例輸入

```
4
2 1 3 4
1 3
```

Expected output / 預期輸出

```
8
```

Step-by-step / 步驟

- Step 1: build prefix: `[0,2,3,6,10]`.
  / 步驟 1：建立前綴和。
- Step 2: answer = `prefix[4] - prefix[1] = 10 - 2 = 8`.
  / 步驟 2：套用公式。

State table / 狀態表

```
i     | 0 1 2 3 4
prefix| 0 2 3 6 10
```

Rust (full program) / Rust（完整程式）

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut a = vec![0i64; n];
    for i in 0..n {
        a[i] = it.next().unwrap().parse().unwrap();
    }
    let l: usize = it.next().unwrap().parse().unwrap();
    let r: usize = it.next().unwrap().parse().unwrap();
    let mut prefix = vec![0i64; n + 1];
    for i in 0..n {
        prefix[i + 1] = prefix[i] + a[i];
    }
    let ans = prefix[r + 1] - prefix[l];
    println!("{}", ans);
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
    a := make([]int64, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &a[i])
    }
    var l, r int
    fmt.Fscan(in, &l, &r)
    prefix := make([]int64, n+1)
    for i := 0; i < n; i++ {
        prefix[i+1] = prefix[i] + a[i]
    }
    ans := prefix[r+1] - prefix[l]
    fmt.Println(ans)
}
```

### Example 2: subarray sum count / 範例 2：子陣列和計數

Input format / 輸入格式

```
n target
x1 x2 ... xn
```

Output format / 輸出格式

- Count of subarrays with sum = target.
  / 輸出子陣列數量。

Example input / 範例輸入

```
3 1
1 -1 1
```

Expected output / 預期輸出

```
3
```

Step-by-step / 步驟

- Step 1: prefix sums = `[0,1,0,1]`.
  / 步驟 1：計算前綴和。
- Step 2: use map counts; for each prefix `p`, add count of `p - target`.
  / 步驟 2：用雜湊表統計。

State table / 狀態表

```
Idx | prefix | need (p-1) | count added | total
----+--------+-------------+------------+------
0   | 0      | -1          | 0          | 0
1   | 1      | 0           | 1          | 1
2   | 0      | -1          | 0          | 1
3   | 1      | 0           | 2          | 3
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
    let target: i32 = it.next().unwrap().parse().unwrap();
    let mut nums = vec![0i32; n];
    for i in 0..n {
        nums[i] = it.next().unwrap().parse().unwrap();
    }
    let mut count: HashMap<i32, i32> = HashMap::new();
    count.insert(0, 1);
    let mut prefix = 0i32;
    let mut ans = 0i32;
    for x in nums {
        prefix += x;
        if let Some(c) = count.get(&(prefix - target)) {
            ans += c;
        }
        *count.entry(prefix).or_insert(0) += 1;
    }
    println!("{}", ans);
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
    nums := make([]int, n)
    for i := 0; i < n; i++ {
        fmt.Fscan(in, &nums[i])
    }
    count := map[int]int{0: 1}
    prefix := 0
    ans := 0
    for _, x := range nums {
        prefix += x
        ans += count[prefix-target]
        count[prefix]++
    }
    fmt.Println(ans)
}
```

## Common uses / 常見用途

- Fixed-length window sums. / 固定長度視窗。
- Many range queries. / 大量區間查詢。
- DP transitions needing range sums. / DP 轉移加速。

## Variations / 變化型

- 2D prefix sums for submatrix queries. / 二維前綴和。
- Difference array for range updates. / 差分陣列。

## Grid line prefix sums / 矩陣列、欄、對角線前綴

Use multiple 1D prefix arrays to query row/column/diagonal sums in `O(1)`.
使用多組一維前綴和，可在 `O(1)` 內查詢列、欄與對角線總和。

- Row prefix: `row[r][c + 1] = row[r][c] + grid[r][c]`.
  / 列前綴和：`row[r][c + 1] = row[r][c] + grid[r][c]`。
- Column prefix: `col[r + 1][c] = col[r][c] + grid[r][c]`.
  / 欄前綴和：`col[r + 1][c] = col[r][c] + grid[r][c]`。
- Main diagonal prefix (down-right): `diag1[r + 1][c + 1] = diag1[r][c] + grid[r][c]`.
  / 主對角線前綴（右下）：`diag1[r + 1][c + 1] = diag1[r][c] + grid[r][c]`。
- Anti-diagonal prefix (down-left): `diag2[r + 1][c] = diag2[r][c + 1] + grid[r][c]`.
  / 副對角線前綴（左下）：`diag2[r + 1][c] = diag2[r][c + 1] + grid[r][c]`。

Query sums for a `k x k` subgrid with top-left `(r, c)`:
查詢左上角 `(r, c)`、邊長 `k` 的子矩陣：

- Row sum: `row[r][c + k] - row[r][c]`.
  / 列總和：`row[r][c + k] - row[r][c]`。
- Column sum: `col[r + k][c] - col[r][c]`.
  / 欄總和：`col[r + k][c] - col[r][c]`。
- Main diagonal sum: `diag1[r + k][c + k] - diag1[r][c]`.
  / 主對角線總和：`diag1[r + k][c + k] - diag1[r][c]`。
- Anti-diagonal sum: `diag2[r + k][c] - diag2[r][c + k]`.
  / 副對角線總和：`diag2[r + k][c] - diag2[r][c + k]`。

Note: build `diag2` with columns iterating right-to-left to satisfy the dependency.
注意：`diag2` 需由右往左建立，才能使用 `diag2[r][c + 1]`。

## Pitfalls / 常見陷阱

- Off-by-one errors. / 邊界容易出錯。
- Use `i64` to avoid overflow. / 使用 `i64`。
- Normalize modulo: `(x % MOD + MOD) % MOD`. / 取模需正規化。

## Complexity / 複雜度

- Build: `O(n)` / 建立：`O(n)`
- Query: `O(1)` / 查詢：`O(1)`

## Related problems / 相關題目

- [q1895](../leetcode/q1895.md)
- [q3578](../leetcode/q3578.md)
- [q3652](../leetcode/q3652.md)
