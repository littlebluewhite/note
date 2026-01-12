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

Step-by-step trace / 逐步解析

We append a sentinel `0`, so we scan `extended = [2, 1, 5, 6, 2, 3, 0]`.
加入哨兵 `0`，掃描序列 `extended = [2, 1, 5, 6, 2, 3, 0]`。

- i=0, cur=2: push 0. stack = [0(2)], max=0
  / i=0, cur=2：推入 0。stack = [0(2)], max=0
- i=1, cur=1: pop 0 (h=2), left=-1, width=1, area=2 → max=2. push 1. stack = [1(1)]
  / i=1, cur=1：彈出 0 (h=2)，left=-1，width=1，area=2 → max=2。推入 1。stack = [1(1)]
- i=2, cur=5: top height 1 ≤ 5, push 2. stack = [1(1), 2(5)]
  / i=2, cur=5：頂端 1 ≤ 5，推入 2。stack = [1(1), 2(5)]
- i=3, cur=6: top height 5 ≤ 6, push 3. stack = [1(1), 2(5), 3(6)]
  / i=3, cur=6：頂端 5 ≤ 6，推入 3。stack = [1(1), 2(5), 3(6)]
- i=4, cur=2:
  - pop 3 (h=6), left=2, width=1, area=6 → max=6
  - pop 2 (h=5), left=1, width=2, area=10 → max=10
  - stop (top height 1 ≤ 2), push 4. stack = [1(1), 4(2)]
  / i=4, cur=2：
    - 彈出 3 (h=6)，left=2，width=1，area=6 → max=6
    - 彈出 2 (h=5)，left=1，width=2，area=10 → max=10
    - 停止（頂端 1 ≤ 2），推入 4。stack = [1(1), 4(2)]
- i=5, cur=3: top height 2 ≤ 3, push 5. stack = [1(1), 4(2), 5(3)]
  / i=5, cur=3：頂端 2 ≤ 3，推入 5。stack = [1(1), 4(2), 5(3)]
- i=6, cur=0 (sentinel):
  - pop 5 (h=3), left=4, width=1, area=3
  - pop 4 (h=2), left=1, width=4, area=8
  - pop 1 (h=1), left=-1, width=6, area=6
  - push 6, done. max=10
  / i=6, cur=0（哨兵）：
    - 彈出 5 (h=3)，left=4，width=1，area=3
    - 彈出 4 (h=2)，left=1，width=4，area=8
    - 彈出 1 (h=1)，left=-1，width=6，area=6
    - 推入 6，結束。max=10

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
