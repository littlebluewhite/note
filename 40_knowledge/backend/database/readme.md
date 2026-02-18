---
title: README
note_type: knowledge
domain: backend
category: database
tags: [database, backend, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: knowledge
---
# README

Database 筆記索引

這裡整理資料庫相關主題，作為資料庫筆記的入口。

主索引

- INDEX.md

主題導覽

- alembic/README.md: Alembic migrations 與常用操作
- indexing.md: 索引基礎與常見陷阱
- transactions.md: 交易與 ACID 概念
- isolation_levels.md: 隔離等級速覽
- postgres_gotchas.md: PostgreSQL 常見陷阱與維運注意事項
- postgres_explain_guide.md: PostgreSQL EXPLAIN/ANALYZE 指南
- postgres_explain_examples.md: PostgreSQL EXPLAIN 範例與解讀
- postgres_index_join_guide.md: 索引與 Join 策略快速判斷
- postgres_lock_troubleshooting.md: 鎖等待與死鎖排查
- postgres_slow_query_triage.md: 慢查詢排查流程

## Cross-references（後端系列）

- transactions.md <-> [Saga 分散式交易](../distributed_systems/13_saga_pattern.md)
- postgres_lock_troubleshooting.md <-> [分散式鎖](../distributed_systems/15_distributed_locking.md)
- isolation_levels.md <-> [CAP 定理與一致性模型](../distributed_systems/12_cap_consistency_models.md)
- indexing.md <-> [快取與 Redis 模式](../infrastructure/21_caching_redis_patterns.md)
- postgres_slow_query_triage.md <-> [連線池管理](../engineering/38_connection_pooling.md)
- indexing.md <-> [分片與分區](../distributed_systems/43_sharding_partitioning.md)
- transactions.md <-> [資料庫複製](../distributed_systems/44_database_replication.md)
- isolation_levels.md <-> [NoSQL 選型指南](../system_design/45_nosql_selection_guide.md)
- postgres_lock_troubleshooting.md <-> [零停機 Schema 遷移](../engineering/55_zero_downtime_schema_migration.md)
