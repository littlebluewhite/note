PostgreSQL EXPLAIN / ANALYZE Guide

目的

快速判讀查詢計畫，找出慢的原因與索引機會。

常用指令

EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;

重點欄位

- actual time: 實際耗時
- rows: 實際輸出筆數
- loops: 節點被執行次數
- Buffers: shared hit/read/dirtied

Plan Node 字典

掃描節點

- Seq Scan: 全表掃描
- Index Scan: 走索引，回表取資料
- Index Only Scan: 索引覆蓋查詢，不回表
- Bitmap Index Scan: 用索引產生 bitmap
- Bitmap Heap Scan: 用 bitmap 回表取資料
- Tid Scan: 依 tuple ID 讀取特定列

排序與聚合

- Sort: 需要排序
- Incremental Sort: 只有部分排序
- GroupAggregate: 先排序再聚合
- HashAggregate: 先 hash 再聚合

Join 節點

- Nested Loop: 小表或有索引時快
- Hash Join: 中大型表常見
- Merge Join: 兩邊已排序或可排序

其他常見節點

- Limit: 限制輸出筆數
- Unique: 去重
- Append: 合併多個子計畫
- Gather/Gather Merge: 平行查詢彙整
- Result: 產生常數或計算結果

診斷技巧

- 預估 rows 與實際差距大：統計過期或資料分布異常
- Sort 節點昂貴：考慮索引順序或增加 work_mem
- Loop 次數很大：Nested Loop 可能不適合
- Buffers read 很高：I/O 成本高，考慮索引或 cache
- Index Only Scan 需要 visibility map，VACUUM 可幫助
- Hash Join 需要足夠 work_mem

常見改善方向

- 新增或調整索引（含複合、部分、表達式）
- ANALYZE 更新統計
- 調整查詢條件與排序
- 大批量查詢用批次或分頁降低峰值

慢查詢速查流程

1) 先跑 EXPLAIN (ANALYZE, BUFFERS)\n2) 看是否 Seq Scan / Sort / Nested Loop loops 過大\n3) 檢查索引與索引順序是否命中\n4) rows 預估偏差大就先 ANALYZE\n5) 檢查鎖等待或長交易（pg_stat_activity）\n6) 調整後再次驗證
