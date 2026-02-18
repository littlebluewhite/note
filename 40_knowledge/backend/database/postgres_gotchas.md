---
title: postgres gotchas
note_type: knowledge
domain: backend
category: database
tags: [database, backend, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: knowledge
---
# postgres gotchas

PostgreSQL Gotchas

這份筆記整理容易被忽略的行為與維運風險，作為查詢與排錯用。

VACUUM 與 Autovacuum

- MVCC 會留下 dead tuples，需要 VACUUM 清理
- 長交易會阻擋 VACUUM 回收空間
- Autovacuum 太慢時會造成 bloat 與查詢變慢
- 大表可考慮調整 autovacuum_vacuum_scale_factor

Table Bloat

- 大量 UPDATE/DELETE 會讓表膨脹
- 症狀：表大小暴增、Index Scan 變慢
- 解法：VACUUM (FULL) 或重建索引/表（需停機或鎖表）

Statistics 與 Query Planner

- 統計資訊過期會導致錯誤的執行計畫
- ANALYZE 可更新統計資訊
- 常見徵兆：預估 rows 與實際差異極大

Transaction ID Wraparound

- PostgreSQL 需要定期 freeze，避免 XID wraparound
- Autovacuum 若被長交易阻塞，會有風險警告
- 監控 autovacuum 進度與 freeze age

長交易與連線池

- 閒置交易 (idle in transaction) 會阻擋 vacuum 並持有鎖
- 在應用層設定 statement_timeout 與 idle_in_transaction_session_timeout

索引維護

- REINDEX 可修復索引膨脹或損壞
- 觀察 pg_stat_user_indexes 判斷未使用索引
- 重要索引變更多時，記得更新統計

常用監控查詢

-- 檢查長交易與 idle in transaction
SELECT pid, usename, state, now() - xact_start AS xact_age, query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_age DESC
LIMIT 20;

-- 找出膨脹或更新多的表（粗略）
SELECT relname, n_dead_tup, n_live_tup,
       round(n_dead_tup::numeric / NULLIF(n_live_tup, 0), 2) AS dead_ratio
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;

-- 找出未使用索引
SELECT relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC
LIMIT 20;

-- 檢查 autovacuum 最近執行情況
SELECT relname, last_autovacuum, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY last_autovacuum NULLS FIRST
LIMIT 20;
