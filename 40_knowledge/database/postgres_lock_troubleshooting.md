---
title: postgres lock troubleshooting
note_type: knowledge
domain: database
tags: [database, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: database
canonical: database/postgres_lock_troubleshooting.md
---
# postgres lock troubleshooting

PostgreSQL Lock Troubleshooting

目的

快速定位鎖等待、死鎖與長交易造成的效能問題。

常見症狀

- 查詢卡住不回應
- 大量 session 處於 active 但無法前進
- 交易長時間未提交

常用查詢

-- 觀察等待鎖的查詢
SELECT pid, usename, state, wait_event_type, wait_event, now() - xact_start AS xact_age, query
FROM pg_stat_activity
WHERE wait_event_type = 'Lock'
ORDER BY xact_age DESC;

-- 找出阻塞者與被阻塞者
SELECT blocked.pid AS blocked_pid,
       blocked.query AS blocked_query,
       blocker.pid AS blocker_pid,
       blocker.query AS blocker_query,
       now() - blocker.xact_start AS blocker_age
FROM pg_stat_activity blocked
JOIN pg_locks blocked_locks ON blocked.pid = blocked_locks.pid
JOIN pg_locks blocker_locks
  ON blocker_locks.locktype = blocked_locks.locktype
 AND blocker_locks.database IS NOT DISTINCT FROM blocked_locks.database
 AND blocker_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
 AND blocker_locks.page IS NOT DISTINCT FROM blocked_locks.page
 AND blocker_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
 AND blocker_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
 AND blocker_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
 AND blocker_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
 AND blocker_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
 AND blocker_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
 AND blocker_locks.pid != blocked_locks.pid
JOIN pg_stat_activity blocker ON blocker.pid = blocker_locks.pid
WHERE NOT blocked_locks.granted;

-- 檢查長交易
SELECT pid, usename, state, now() - xact_start AS xact_age, query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_age DESC
LIMIT 20;

常見鎖與對策

- Row-level lock（FOR UPDATE）: 避免長交易，縮短鎖持有時間
- AccessExclusiveLock（DDL）: 盡量離峰執行，避免與大量讀寫衝突
- 長交易阻擋 autovacuum: 排查 idle in transaction

鎖類型速覽（常用）

- Row-level: SELECT ... FOR UPDATE/SHARE
- RowExclusiveLock: 一般 DML（INSERT/UPDATE/DELETE）
- ShareLock: 某些維護操作（較少見）
- AccessShareLock: 普通 SELECT
- AccessExclusiveLock: DDL（ALTER TABLE 等）

鎖類型範例

- Row-level
  SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
- RowExclusiveLock
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
- AccessShareLock
  SELECT * FROM accounts WHERE id = 1;
- AccessExclusiveLock
  ALTER TABLE accounts ADD COLUMN note text;

pg_locks 常見 lock mode 對照

- AccessShareLock: SELECT
- RowShareLock: SELECT ... FOR UPDATE/SHARE
- RowExclusiveLock: INSERT/UPDATE/DELETE
- ShareLock: CREATE INDEX（非 CONCURRENTLY）
- ShareUpdateExclusiveLock: VACUUM (ANALYZE) / CREATE INDEX CONCURRENTLY
- AccessExclusiveLock: ALTER TABLE / DROP TABLE / TRUNCATE

鎖衝突矩陣（簡化）

僅列出常用 lock mode，未包含 ShareRowExclusive 與 Exclusive。

| Mode \\ Conflicts | AccessShare | RowShare | RowExclusive | ShareUpdateExclusive | Share | AccessExclusive |
|---|---|---|---|---|---|---|
| AccessShare | - | - | - | - | - | Y |
| RowShare | - | - | - | - | - | Y |
| RowExclusive | - | - | - | Y | Y | Y |
| ShareUpdateExclusive | - | - | Y | Y | Y | Y |
| Share | - | - | Y | Y | - | Y |
| AccessExclusive | Y | Y | Y | Y | Y | Y |

pg_locks 判讀要點

- granted = false 表示正在等待鎖
- granted = true 但仍被阻塞，通常是等待別的資源（例如 IO）
- 同一 resource 上有多個鎖模式時，注意衝突矩陣

阻塞鏈查詢（延伸）

-- 找出阻塞鏈路（需要 pg_blocking_pids）
SELECT pid, usename, now() - xact_start AS xact_age, query,
       pg_blocking_pids(pid) AS blocking_pids
FROM pg_stat_activity
WHERE array_length(pg_blocking_pids(pid), 1) > 0
ORDER BY xact_age DESC;

常見死鎖模式與避免方式

- 兩個交易以不同順序更新同一批資料
  解法：固定更新順序
- SELECT ... FOR UPDATE 與 UPDATE 交錯
  解法：統一使用 FOR UPDATE 或統一更新流程
- 批次更新與線上寫入衝突
  解法：分批處理或離峰執行

避免與緩解

- 統一寫入順序，降低死鎖
- 對可重試錯誤實作 retry
- 使用 NOWAIT 或 SKIP LOCKED 降低等待
- 設定 lock_timeout / statement_timeout

  SET lock_timeout = '2s';
  SET statement_timeout = '30s';

- 設定 idle_in_transaction_session_timeout 避免閒置交易

  SET idle_in_transaction_session_timeout = '1min';

安全終止阻塞者（pg_terminate_backend）

- 優先使用 pg_cancel_backend(pid) 取消單一查詢
  SELECT pg_cancel_backend(12345);
- 若無法解除，才使用 pg_terminate_backend(pid) 終止連線（會 rollback 交易）
  SELECT pg_terminate_backend(12345);
- 先確認 pid 是否為真正的 blocker，避免殺錯重要交易
- 終止後觀察應用層是否有重試或錯誤處理
