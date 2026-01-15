# Sorted Array / 排序陣列

Goal: keep elements in non-decreasing order for fast scanning and binary search.
目標：維持排序以便進行快速掃描與二分查詢。

## Core structure / 核心結構

- A contiguous array sorted in ascending order.
  / 以升冪排序的連續陣列。
- Typically built once by sorting the input.
  / 通常由輸入排序後一次建立。

## Typical operations / 常見操作

- Build: `sort(a)` in `O(n log n)`.
  / 建立：排序成本 `O(n log n)`。
- Binary search: `O(log n)`.
  / 二分查詢 `O(log n)`。
- Linear scan for runs or aggregates: `O(n)`.
  / 線性掃描連續段或彙總 `O(n)`。
- Insert/delete: `O(n)` due to shifting.
  / 插入與刪除因位移為 `O(n)`。

## Example / 範例

Problem: longest consecutive run.
題目：最長連續段。

```
sort(a)
cur = 1
best = 1
for i in 1..n-1:
    if a[i] == a[i-1] + 1:
        cur += 1
    else:
        cur = 1
    best = max(best, cur)
```

## Complexity / 複雜度

- Space: `O(n)` for the array itself.
  / 空間：陣列本體 `O(n)`。
- Extra space: `O(1)` if sorting in place.
  / 額外空間：就地排序為 `O(1)`。

## Pitfalls / 常見陷阱

- Forgetting to sort before scanning.
  / 忘記先排序導致連續段判斷錯誤。
- Duplicates may need special handling.
  / 有重複值時需明確定義如何處理。
- Frequent insertions degrade performance.
  / 頻繁插入會造成效能下降。

## Related problems / 相關題目

- `leetcode/q2943.md`
