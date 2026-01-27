# Longest Consecutive Run in Sorted List / 排序後最長連續段

Goal: find the longest length of consecutive integers by sorting and scanning once.
目標：先排序再線性掃描，找出最長連續整數段長度。

## Core idea / 核心想法

- Sort ascending, then scan and count `prev + 1` runs.
  / 先升冪排序，掃描時遇到 `prev + 1` 就延長連續段。
- Reset the run length when the sequence breaks.
  / 一旦不連續就重設當前長度。
- Track the maximum run length.
  / 全程維護最大值。

## Template / 範本

```
sort(a)
best = 0
cur = 0
for i in 0..n:
    if i == 0 or a[i] != a[i-1] + 1:
        cur = 1
    else:
        cur += 1
    best = max(best, cur)
```

## Worked Example / 範例

Input array / 輸入陣列：

```
[4, 2, 3, 7, 10, 9]
```

After sorting / 排序後：

```
[2, 3, 4, 7, 9, 10]
```

Scan result / 掃描結果：

- `2,3,4` is a run of length 3.
  / `2,3,4` 連續段長度為 3。
- `7` starts a new run of length 1.
  / `7` 重新開始，長度 1。
- `9,10` is a run of length 2.
  / `9,10` 連續段長度為 2。

Maximum run length = 3.
最大連續段長度 = 3。

## Complexity / 複雜度

- Sorting: `O(n log n)`
  / 排序時間 `O(n log n)`。
- Scan: `O(n)`
  / 掃描時間 `O(n)`。
- Extra space: `O(1)` if sorting in place.
  / 額外空間 `O(1)`（就地排序）。

## Pitfalls / 常見陷阱

- Duplicates: decide whether to ignore `a[i] == a[i-1]` or reset the run.
  / 重複值：要決定是否忽略 `a[i] == a[i-1]` 或視為斷開。
- Empty list: return 0 instead of 1.
  / 空陣列需回傳 0。
- Off-by-one when initializing the first run length.
  / 第一段初始化容易 off-by-one。

## Related problems / 相關題目

- [q2943](../leetcode/q2943.md)
