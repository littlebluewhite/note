---
title: "postgres slow query triage"
category: database
tags: [database]
created: 2026-02-03
updated: 2026-02-03
difficulty: "n/a"
source: database
status: active
---
# postgres slow query triage

PostgreSQL Slow Query Triage

目的

提供一個固定順序的檢查流程，快速縮小慢查詢原因。

步驟 1: 確認問題型態

- 是單次慢（查詢本身）還是間歇慢（鎖或資源）
- 是否只在特定時間變慢（尖峰或維運）

步驟 2: 取得 EXPLAIN

EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;

- 看是否 Seq Scan / Sort / Nested Loop loops 很大
- 觀察 rows 預估與實際差距

步驟 3: 檢查索引

- 條件欄位是否有索引
- 複合索引順序是否匹配
- 是否需要表達式或部分索引

步驟 4: 檢查統計資訊

- ANALYZE 更新統計
- 觀察統計過期或偏差

步驟 5: 檢查鎖與長交易

- pg_stat_activity 是否有長交易或 idle in transaction
- 針對鎖等待先解決阻塞源

步驟 6: 檢查 I/O 與資源

- Buffers read 很高代表 I/O 壓力
- 確認磁碟或 cache 是否不足

步驟 7: 變更與驗證

- 調整索引或查詢後重新 EXPLAIN
- 對比前後實際時間與 buffers
