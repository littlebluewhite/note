# Coupon Validation and Ordered Grouping

目標：從三個等長陣列 `code`、`business_line`、`is_active` 中，挑出同時滿足「代碼字元合法、業務分類合法且啟用」的優惠券，並依指定分類順序再依字典序輸出代碼。

## 核心想法

- 事先把允許的分類映射成固定順序索引：`electronics -> 0, grocery -> 1, pharmacy -> 2, restaurant -> 3`，便於後續排序時用第一鍵。
- 代碼合法性檢查：非空且所有字元皆為 `is_ascii_alphanumeric` 或底線 `_`；不用正規表示式即可完成。
- 篩選時同步檢查 `is_active` 與分類是否存在於映射表，合格者存成 `(order, code)`。
- 最後對 `(order, code)` 排序即可同時滿足分類優先與同分類內字典序要求。

## 步驟

1. 建立 `HashMap<&str, usize>` 儲存分類到順序的映射。
2. 逐一掃描 `code / business_line / is_active`：
   - 略過 `is_active = false`。
   - `code` 為空或含非允許字元則略過。
   - `business_line` 不在映射表中則略過。
   - 通過檢查者推入 `(order, code)`。
3. 對收集的配對排序（tuple 既有詞典序，會先比 `order` 再比 `code`），最後取出代碼字串。

## 複雜度

- 時間：O(n log n)，排序為主；掃描與檢查皆為 O(n)。
- 空間：O(n) 儲存通過篩選的配對；映射與常數狀態為 O(1)。

## 邊界注意

- 空字串直接判定無效；`is_ascii_alphanumeric` 僅涵蓋英數，不接受空白或特殊符號。
- 分類字串長度最高 100，但只需檢查是否存在於映射表，無需額外處理。
