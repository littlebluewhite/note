---
title: isolation levels
note_type: knowledge
domain: database
tags: [database, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: database
---
# isolation levels

Isolation Levels

目的

隔離等級定義交易之間可見的資料範圍，影響一致性與併發性。

本文以 PostgreSQL 為主。

常見異常

- Dirty Read: 讀到未提交資料
- Non-Repeatable Read: 同一交易內兩次讀取結果不同
- Phantom Read: 同一交易內查詢集合結果改變
- Write Skew: 兩個交易互相讀取後寫入，導致規則被破壞

PostgreSQL 隔離等級

Read Uncommitted
- 在 Postgres 會視同 Read Committed

Read Committed（預設）
- 每個 statement 看到當下已提交的快照
- 避免 dirty read
- 仍可能 non-repeatable read / phantom read

Repeatable Read
- 交易開始時取得一致快照
- 同一交易內重複讀取結果固定
- 仍可能發生 write skew
- 若與並行更新衝突，可能被中止需重試

Serializable
- 以 SSI (Serializable Snapshot Isolation) 達成序列化效果
- 會偵測危險衝突並中止交易
- 需要處理 serialization_failure (40001) 重試

使用方式

BEGIN ISOLATION LEVEL REPEATABLE READ;
-- work
COMMIT;

或

BEGIN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- work
COMMIT;

如何選擇

- 一般業務：Read Committed
- 需要一致快照：Repeatable Read
- 嚴格一致性：Serializable（搭配 retry）

常見實務建議

- 不要全域提高隔離等級，僅在需要時提升
- 關鍵邏輯可用 SELECT ... FOR UPDATE 加強一致性
- 交易失敗後必須 rollback 再重試
