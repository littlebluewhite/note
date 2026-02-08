---
title: transactions
note_type: knowledge
domain: database
tags: [database, knowledge]
created: 2023-01-01
updated: 2026-02-03
status: active
source: database
---
# transactions

Transactions Basics

目的

交易確保多個操作要嘛全部成功，要嘛全部失敗，避免資料不一致。

本文以 PostgreSQL 為主。

ACID 摘要

- Atomicity: 全有或全無
- Consistency: 遵守資料規則與約束
- Isolation: 交易之間互不干擾
- Durability: 提交後持久化

基本語法

BEGIN;
-- 多筆寫入或讀寫
COMMIT;

-- 失敗時
ROLLBACK;

PostgreSQL 行為重點

- 預設隔離等級為 Read Committed
- Read Uncommitted 在 Postgres 會視同 Read Committed
- 可用 SET TRANSACTION 設定單筆交易隔離等級

  BEGIN;
  SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
  -- work
  COMMIT;

自動提交（Autocommit）

- 多數驅動預設每個 statement 自成交易
- 需要跨多筆操作時，必須手動開始交易

常見模式

1) Read-Modify-Write

BEGIN;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

2) 需要回滾的批次更新

BEGIN;
UPDATE orders SET status = 'archived' WHERE created_at < '2023-01-01';
COMMIT;

3) Savepoint（局部回滾）

BEGIN;
SAVEPOINT s1;
-- 嘗試性操作
ROLLBACK TO SAVEPOINT s1;
COMMIT;

鎖定與併發控制（PostgreSQL）

- SELECT ... FOR UPDATE 會鎖住列，避免競爭更新
- NOWAIT 立即失敗，避免長時間等待
- SKIP LOCKED 常用在佇列式任務

  SELECT * FROM jobs
  WHERE status = 'pending'
  FOR UPDATE SKIP LOCKED
  LIMIT 10;

交易設計原則

- 交易越短越好，避免鎖表與阻塞
- 寫入操作使用一致順序，降低死鎖
- 對可重試的錯誤（deadlock/serialization failure）實作 retry
- 讀寫混合時，用 FOR UPDATE 或一致的隔離等級

錯誤處理建議（PostgreSQL）

- deadlock_detected (40P01) 需重試
- serialization_failure (40001) 需重試
- 交易失敗必須 rollback
- 需要 idempotency 時，加入唯一鍵或防重機制

與隔離等級的關係

- 隔離等級影響讀到的資料一致性與可併發度
- 需要一致讀取時提高隔離等級，但可能降低吞吐
- 參考：database/isolation_levels.md
