## Best Time to Buy and Sell Stock using Strategy — Prefix Window Delta

### 問題類型

長度固定子陣列的最佳修改；需要以 O(1) 取得區間求和並掃描全部起點。

### 關鍵轉換

- 修改長度 `k`、前半設 0 後半設 1。區間起點為 `l` 時，利潤變化：
  - 前半：原值為 `s*p`，改為 0，增益 `-s*p`。
  - 後半：原值為 `s*p`，改為 `p`，增益 `p - s*p`。
- 合併後 `delta(l) = -Σ_{window}(s*p) + Σ_{second half}(p)`，只依賴兩個區間求和。

### 演算法

1. 建前綴和：
   - `prefix_sp[i] = Σ_{0..i-1} strategy[j]*price[j]`
   - `prefix_p[i]  = Σ_{0..i-1} price[j]`
2. 對每個起點 `l` (0-based，`l + k <= n`)：
   - `sum_sp   = prefix_sp[l+k] - prefix_sp[l]`
   - `sum_p2   = prefix_p[l+k] - prefix_p[l + k/2]`
   - `delta    = -sum_sp + sum_p2`
   - 保留最大值 `max_delta`。
3. 原始利潤 `base = Σ strategy[i]*price[i]`，答案 `base + max(0, max_delta)`（可選擇不修改）。

### 複雜度

- 時間：O(n) 建前綴與單次掃描。
- 空間：O(n) 儲存前綴和。

### 注意事項

- 需以 64 位整數避免 `10^5 * 10^5` 累積溢位。
- `k` 為偶數，後半起點為 `l + k/2`，包含 `k/2` 個元素。
