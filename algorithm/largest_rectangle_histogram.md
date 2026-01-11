# Largest Rectangle in Histogram (Monotonic Stack) / 直方圖最大矩形（單調堆疊）

Goal: find the maximum rectangle area formed by consecutive bars.
目標：在直方圖中找出由連續柱子形成的最大矩形面積。

## Core idea / 核心概念

Maintain a monotonic increasing stack of indices.
維持「遞增高度」的索引堆疊。

When the current height is smaller than the stack top, the top bar's right boundary is fixed at the current index, and the left boundary is the new stack top after popping.
當前高度比堆疊頂端小時，堆疊頂端柱子的右界就是當前索引，左界是彈出後的新堆疊頂端。

Each bar is pushed and popped once.
每個柱子只進出堆疊各一次。

## Steps / 步驟

1. Append a sentinel `0` to the end of `heights` to flush the stack.
2. Iterate `i` from `0..=n`:
   - While stack not empty and `heights[stack.top] > heights[i]`:
     - Pop `top`, let `h = heights[top]`.
     - Let `left = stack.top` after popping (or `-1` if empty).
     - Width is `i - left - 1`, area is `h * width`.
   - Push `i`.

1. 在 `heights` 結尾加上哨兵 `0`，確保堆疊完整清空。
2. 由左到右掃描 `i`：
   - 當堆疊不空且 `heights[top] > heights[i]`：
     - 彈出 `top`，記錄高度 `h`。
     - 左界為彈出後的新堆疊頂端（若空則視為 `-1`）。
     - 寬度為 `i - left - 1`，面積為 `h * width`。
   - 將 `i` 推入堆疊。

## Why it works / 為何正確

When a bar is popped, the nearest smaller bar on the right is the current index, and the nearest smaller bar on the left is the new stack top. This uniquely determines the widest rectangle with that bar as the minimum height.
當柱子被彈出時，它右側第一個更小的柱子是當前索引，左側第一個更小的柱子是新的堆疊頂端，能唯一決定以該柱為最小高度的最大寬度。

## Complexity / 時間與空間

- Time: `O(n)` / 時間：`O(n)`
- Space: `O(n)` / 空間：`O(n)`

## Typical uses / 常見用途

- Maximal rectangle in a binary matrix (row heights).
  / 二元矩陣最大矩形（逐列維護高度）。
- Largest rectangle in skyline / 直方圖最大矩形。
- Range expansion by nearest smaller element / 最近更小元素擴張。

## Worked example / 實作範例

Input / 輸入

```
heights = [2, 1, 5, 6, 2, 3]
```

Output / 輸出

```
10
```

Explanation / 說明

The best rectangle uses heights `5` and `6` with width `2` (area `10`).
最佳矩形包含高度 `5` 與 `6`，寬度為 `2`，面積 `10`。

Rust (function) / Rust（函式）

```rust
fn largest_rectangle_histogram(heights: &Vec<i32>) -> i32 {
    let mut stack: Vec<usize> = Vec::new();
    let mut max_area = 0i32;
    let mut extended = heights.clone();
    extended.push(0);

    for i in 0..extended.len() {
        let cur = extended[i];
        while let Some(&top) = stack.last() {
            if extended[top] <= cur {
                break;
            }
            let h = extended[top];
            stack.pop();
            let width = match stack.last() {
                Some(&left) => i - left - 1,
                None => i,
            };
            let area = h * width as i32;
            if area > max_area {
                max_area = area;
            }
        }
        stack.push(i);
    }
    max_area
}
```
