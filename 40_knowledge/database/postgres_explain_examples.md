---
title: postgres explain examples
note_type: knowledge
domain: database
tags: [database, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: database
canonical: database/postgres_explain_examples.md
---
# postgres explain examples

PostgreSQL EXPLAIN Examples

目的

用幾個常見計畫示例，快速對照節點含意與改善方向。

例 1: Index Only Scan

Query

SELECT id FROM users WHERE email = 'a@example.com';

Plan (示意)

Index Only Scan using idx_users_email on users  (cost=0.29..8.31 rows=1 width=8)
  Index Cond: (email = 'a@example.com'::text)
  Heap Fetches: 0

解讀

- Index Only Scan: 查詢欄位已被索引覆蓋
- Heap Fetches: 0 表示不需要回表
- 若 Heap Fetches 高，可能需要 VACUUM 讓 visibility map 更新

例 2: Bitmap Index Scan + Bitmap Heap Scan

Query

SELECT id FROM orders WHERE tenant_id = 't1' AND status = 'paid';

Plan (示意)

Bitmap Heap Scan on orders  (cost=12.00..120.00 rows=500 width=8)
  Recheck Cond: ((tenant_id = 't1'::text) AND (status = 'paid'::text))
  ->  Bitmap Index Scan on idx_orders_tenant_status  (cost=0.00..11.50 rows=500 width=0)
        Index Cond: ((tenant_id = 't1'::text) AND (status = 'paid'::text))

解讀

- Bitmap Index Scan: 先用索引找出候選
- Bitmap Heap Scan: 回表取資料
- 若 rows 很大，可能需要更精準索引或調整條件

例 3: Sort + Seq Scan

Query

SELECT * FROM events ORDER BY created_at DESC LIMIT 50;

Plan (示意)

Limit  (cost=1200.00..1200.12 rows=50 width=64)
  ->  Sort  (cost=1200.00..1300.00 rows=40000 width=64)
        Sort Key: created_at DESC
        ->  Seq Scan on events  (cost=0.00..800.00 rows=40000 width=64)

解讀

- Seq Scan + Sort 代表沒能用索引排序
- 可建立索引 (created_at DESC) 以避免排序

例 4: Nested Loop vs Hash Join

Query

SELECT o.id, u.email
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.tenant_id = 't1';

Plan A (示意, Nested Loop)

Nested Loop  (cost=0.70..200.00 rows=1000 width=48)
  ->  Index Scan using idx_orders_tenant on orders o  (cost=0.42..50.00 rows=1000 width=16)
        Index Cond: (tenant_id = 't1'::text)
  ->  Index Scan using users_pkey on users u  (cost=0.28..0.30 rows=1 width=32)
        Index Cond: (id = o.user_id)

Plan B (示意, Hash Join)

Hash Join  (cost=120.00..300.00 rows=1000 width=48)
  Hash Cond: (o.user_id = u.id)
  ->  Seq Scan on orders o  (cost=0.00..150.00 rows=1000 width=16)
        Filter: (tenant_id = 't1'::text)
  ->  Hash  (cost=80.00..80.00 rows=5000 width=32)
        ->  Seq Scan on users u  (cost=0.00..80.00 rows=5000 width=32)

解讀

- Nested Loop 適合外層結果小且有索引
- Hash Join 適合中大型資料量、索引不足時
- 若 Nested Loop 很慢，可能是外層 rows 太大或缺索引
