# Special Triplets via Prefix/Suffix Counts

目標：計算索引三元組 `(i, j, k)`，使 `i < j < k` 且 `nums[i] = nums[k] = 2 * nums[j]`。

## 核心想法

- 以 `j` 為中心，把條件化成「左邊有幾個值等於 `2 * nums[j]`、右邊有幾個值等於同一值」，答案累加兩者乘積。
- 線性掃描 `j`：維護左、右兩側的頻率陣列（或雜湊）。處理當前 `j` 前，先把 `nums[j]` 從右側扣掉，避免重複使用；計算 `target = 2 * nums[j]`；答案加上 `left[target] * right[target]`；最後把 `nums[j]` 放進左側。
- 本題 `nums[i] <= 10^5`，目標值只到 `2 * 10^5`，用固定長度陣列即可 O(1) 查詢與更新。

## 演算法步驟

1. 準備大小 `MAX = 200000` 的 `left`、`right` 計數陣列（i64）。先把整個 `nums` 填入 `right`。
2. 逐一枚舉 `j`：  
   - `right[nums[j]]--`。  
   - `t = 2 * nums[j]`；若 `t <= MAX`，答案累加 `left[t] * right[t]`。  
   - `left[nums[j]]++`。
3. 最後取模回傳。

## 複雜度

- 時間：O(n)，每個元素只被讀寫常數次。
- 空間：O(U)，`U = 2 * 10^5 + 1` 的計數陣列。

## 為何「先扣再算」

- 如果不先把 `nums[j]` 從 `right` 扣掉，當 `nums[j] * 2 == nums[j]`（例如 `nums[j] = 0`）時，會把自己錯算為右側的可選元素，導致多計數。先扣除即可避免。
