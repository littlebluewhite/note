## Long/Short K Transactions with One-Day Separation

目標：股價序列 `prices`，最多進行 `k` 筆交易，每筆可做多或做空，需先開倉再平倉，且平倉當天不能立刻開新倉（至少隔一日）。求最大總獲利（可為負）。

### 狀態設計（以「已完成交易數」為維度）

- `rest[t]`：空手，已完成 `t` 筆交易。  
- `long[t]`：持有多單，已完成 `t` 筆交易。  
- `short[t]`：持有空單，已完成 `t` 筆交易。  
長度皆為 `k+1`，索引 `t` 表示已完成的交易筆數。

### 轉移推導（當日價格為 `p`）

- 平倉（交易數 +1）：  
  `rest[t+1] = max(rest[t+1], long[t] + p, short[t] - p)`  
  - 多單平倉賺 `+p`，空單平倉賺 `-p`。  
  - 只有平倉會增加交易數，符合「先開後平」。
- 開倉（交易數不變）：  
  `long[t]  = max(long[t],  rest[t] - p)`  
  `short[t] = max(short[t], rest[t] + p)`  
  - 從空手開多需付出 `p`，開空得到 `p`。

等價的轉移順序：先計算「平倉」再計算「開倉」，但都必須讀取「前一日」的狀態。

### 為何自然滿足「平倉當天不能再開倉」

更新採「舊陣列生成新陣列」的滾動方式：  
當日 `rest[t+1]`（平倉所得）不會在同一迭代被用來更新當日 `long/short`，因為 `long/short` 只讀取前一日的 `rest`。因此平倉後至少隔一日才能再開倉，無需額外標誌。

### 初始化與邊界

- `NEG = i64::MIN / 4` 作為不可能狀態，避免加減價格時溢位。  
- Day 0 之前（基準）：  
  - `rest[0] = 0`；其他 `rest` 為 `NEG`。  
  - `long`、`short` 全為 `NEG`。  
- 若 `k = 0`，直接回傳 0；轉移也不會越界。
- `NEG` 與價格/獲利量級：  
  - 最高價差約 `1e5`，最多 `k=5e2`，累積量級 `5e7`；再乘常數仍遠小於 `|i64::MIN/4|`。  
  - 使用 `i64::MIN/4` 確保 `NEG ± price` 不會溢位。

### 偽碼（單層滾動）

```
NEG = i64::MIN / 4
rest = vec![NEG; k+1]; rest[0] = 0
long = vec![NEG; k+1]
short = vec![NEG; k+1]

for p in prices:
    new_rest = rest.clone()
    new_long = long.clone()
    new_short = short.clone()

    for t in 0..=k:
        // 平倉 -> rest[t+1]
        if t + 1 <= k {
            new_rest[t+1] = max(new_rest[t+1], long[t] + p, short[t] - p)
        }
        // 開倉 -> long[t], short[t]
        new_long[t]  = max(new_long[t],  rest[t] - p)
        new_short[t] = max(new_short[t], rest[t] + p)
    }

    rest = new_rest; long = new_long; short = new_short

answer = max(rest)
```

若要節省常數，可用兩層陣列 `prev`/`curr` 並每日日末 `swap`；邏輯相同。

### 程式碼解析（核心片段）

以下對應 Rust / 類似語言的實作重點：

- 前綴常數：`let neg = i64::MIN / 4;`。  
- 狀態初始化：`rest = vec![neg; k+1]; rest[0] = 0; long = vec![neg; k+1]; short = vec![neg; k+1];`。  
- 每日更新（保持前一日與當日分離）：  
  ```rust
  let mut nr = rest.clone();
  let mut nl = long.clone();
  let mut ns = short.clone();
  for t in 0..=k {
      if t + 1 <= k {
          nr[t + 1] = nr[t + 1].max(long[t] + p).max(short[t] - p); // 平倉
      }
      nl[t] = nl[t].max(rest[t] - p);   // 開多
      ns[t] = ns[t].max(rest[t] + p);   // 開空
  }
  rest = nr; long = nl; short = ns;
  ```
- 最終答案：`rest.iter().copied().max().unwrap()`。  
- 若改用雙層陣列：  
  - `rest_cur.fill(neg); long_cur.fill(neg); ...`  
  - 用 `rest_prev` 讀取、`rest_cur` 寫入，日末 `swap(rest_prev, rest_cur)`，並重置 `*_cur` 為 `neg`。
- 若需優化常數：  
  - 可把 `for t in 0..k`，內部手動展開平倉分支，或用迭代器 `take(k)` 避免邊界判斷。  
  - 但務必確保 `t+1` 不越界，且仍讀取前一日 `rest`。

### 複雜度

- 時間：`O(n * k)`。  
- 空間：`O(k)`（使用滾動即可，若採雙層備份為 `O(k)` 常數倍）。

### 注意實作細節

- 必須使用 `i64`：價格、交易數乘積可達 `1e5 * 1e5 = 1e10`，再累積需要 64 位。  
- 迭代順序不限，但要保證使用「前一日」狀態計算「當日」狀態；用獨立新陣列最安全。  
- 若使用原地更新，需先計算平倉部分寫回 `rest_next`，開倉部分讀取的是舊 `rest`，避免同日連續操作。
- 若允許「同一天先開倉再平倉」會破壞題意；本設計因讀舊狀態而自動避免。
- 回傳時只能取 `rest`，不可取 `long/short`（未平倉不算完成）。

### 範例（prices = [1, 7, 2, 5], k = 2）

Day 0, p=1  
- 開多：`long[0] = -1`；開空：`short[0] = 1`。

Day 1, p=7  
- 平多：`rest[1] = 6`；平空：`rest[1] = max(6, 1-7=-6) = 6`。  
- 仍可從舊 `rest[0]=0` 再開倉：`short[0] = max(1, 0+7=7)`。

Day 2, p=2  
- 從前日的 `short[0]=7` 平倉：`rest[1] = max(6, 7-2=5) = 6`。  
- 從 `rest[1]=6` 開空（不能同日，需用前日值）：`short[1] = 6 + 2 = 8`。

Day 3, p=5  
- 平倉完成第 2 筆：`rest[2] = max(NEG, long[1]+5, short[1]-5) = max(NEG, NEG, 8-5=3) = 3`。  
- 也可以在 Day2 開多 `long[1]=6-2=4`，此處平倉得 `9`；`rest[2]` 取最大為 `9`。  
- 最終答案 `max(rest) = max(rest[0]=0, rest[1]=6, rest[2]=9) = 9`。

該解對應兩筆交易：  
1) Day0 多 -> Day1 平，多賺 `+6`。  
2) Day2 多 -> Day3 平，多賺 `+(5-2)=3`。合計 9。

### 自行檢查要點

- `k=1`、全上漲：應開多一次並平倉。  
- `k=1`、全下跌：可開空一次並平倉。  
- `k` 很大（大於可用交易數）：答案不變，但狀態維度仍為 `k+1`。  
- 價格長度為 1：無法平倉，`max(rest)=0`。  
- 交替價格、限制隔日開倉：確認未誤用「當日 rest」開倉。
