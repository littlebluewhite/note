# Binary Search Lower Bound / 二分搜尋下界

Goal: find the first index where `arr[i] >= target` in a sorted array.
目標：在已排序陣列中找到第一個 `arr[i] >= target` 的位置。

## Preconditions / 前置條件

- Array must be sorted in non-decreasing order.
  / 陣列必須是非遞減排序。
- Use a half-open range `[l, r)` to avoid off-by-one.
  / 使用半開區間 `[l, r)` 可減少邊界錯誤。

## Pattern / 流程

1. Initialize `l = 0`, `r = n` (search in `[l, r)`).
   / 初始化 `l = 0`, `r = n`。
2. While `l < r`, compute `m = l + (r - l) / 2`.
   / 當 `l < r` 時計算中點。
3. If `arr[m] < target`, move left bound up: `l = m + 1`.
   / 若 `arr[m] < target`，左界右移。
4. Else move right bound down: `r = m`.
   / 否則右界左移。
5. Return `l` as the insertion point and lower bound.
   / 回傳 `l` 作為插入點與下界。

## Example / 範例

Array: `[1, 3, 3, 7]`, target = `4`

- Step 1: `l=0, r=4, m=2`, `arr[2]=3 < 4` -> `l=3`
- Step 2: `l=3, r=4, m=3`, `arr[3]=7 >= 4` -> `r=3`
- Stop: `l=3` is the first index with value `>= 4`.

## Rust snippet / Rust 範例

```rust
fn lower_bound(arr: &Vec<i32>, target: i32) -> usize {
    let mut l = 0usize;
    let mut r = arr.len();
    while l < r {
        let m = l + (r - l) / 2;
        if arr[m] < target {
            l = m + 1;
        } else {
            r = m;
        }
    }
    l
}
```

## When to use / 使用時機

- Find the earliest valid index by threshold.
  / 找到第一個符合門檻的位置。
- Find insertion point while keeping order.
  / 找到維持排序的插入點。
- Combine with suffix/prefix arrays for fast queries.
  / 搭配前後綴陣列快速查詢。

## Pitfalls / 常見陷阱

- Using unsorted input -> incorrect result.
  / 未排序輸入會出錯。
- Off-by-one with closed intervals.
  / 使用閉區間容易邊界錯。
- Overflow in `m = (l + r) / 2`; use `l + (r - l) / 2`.
  / 中點計算需避免溢位。

## Complexity / 複雜度

- Time: `O(log n)`
  / 時間：`O(log n)`
- Space: `O(1)`
  / 空間：`O(1)`

## Related problems / 相關題目

- `leetcode/q1292.md`
- `leetcode/q1970.md`
- `leetcode/q2054.md`
