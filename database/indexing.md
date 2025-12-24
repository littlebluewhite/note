Indexing Basics

目的

索引用額外空間換取查詢速度，尤其是搜尋、排序、分組與 JOIN。

本文以 PostgreSQL 為主。

核心概念

- 常見索引為 B-Tree，適合範圍查詢與排序
- 複合索引遵守 leftmost prefix 規則
- 索引能加速讀取，但會增加寫入成本

什麼情況該建立索引

- WHERE 條件常使用的欄位
- JOIN 的連接鍵
- ORDER BY / GROUP BY 常用欄位
- 高查詢頻率且表資料量大

什麼情況不適合

- 低選擇性欄位（例如布林值）
- 高寫入頻率且很少被查詢
- 很小的表（全表掃描更快）

索引類型速覽（通用概念）

- Single-column: 單一欄位索引
- Composite: 多欄位索引，順序很重要
- Unique: 保證唯一性，同時可加速查詢
- Covering: 查詢欄位完全被索引覆蓋，可避免回表
- Partial/Filtered: 只索引符合條件的資料（部分引擎支援）

PostgreSQL 常見索引型別

- B-Tree: 預設，適合等值與範圍查詢、排序
- GIN: array、jsonb、全文檢索常用
- GiST: range type、空間資料
- BRIN: 超大表且資料自然排序時效果佳
- Hash: 只適合等值查詢，較少使用

複合索引順序設計

- 先放等值查詢欄位，再放範圍查詢欄位
- 常見組合：WHERE a = ? AND b = ? ORDER BY c
- 查詢若只使用後段欄位，索引通常無法利用

範例（PostgreSQL）

-- 查詢使用者 email
CREATE INDEX idx_users_email ON users (email);

-- 複合索引（tenant_id 等值，created_at 範圍）
CREATE INDEX idx_orders_tenant_created_at
ON orders (tenant_id, created_at);

-- 唯一索引
CREATE UNIQUE INDEX idx_users_email_unique ON users (email);

-- 表達式索引（大小寫不敏感查詢）
CREATE INDEX idx_users_email_lower ON users (lower(email));

-- 部分索引（只索引活躍資料）
CREATE INDEX idx_users_active ON users (email) WHERE is_active = true;

-- 覆蓋索引（Postgres 的 INCLUDE）
CREATE INDEX idx_orders_lookup
ON orders (tenant_id, created_at) INCLUDE (status, total);

常見問題

- 函式或運算套在索引欄位上，可能導致無法用索引
- ORDER BY 欄位順序與索引順序不一致，可能無法利用
- 過多索引會拖慢寫入與批次更新

檢查與驗證

- 使用 EXPLAIN / EXPLAIN ANALYZE 看是否走索引
- 觀察慢查詢與最常出現的 WHERE/JOIN
- 定期檢視未使用或重複的索引

PostgreSQL 實務補充

- 建索引避免長時間鎖表，可用 CONCURRENTLY（不可在交易中）
  CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
- 用 EXPLAIN (ANALYZE, BUFFERS) 觀察是否走 index scan 或 bitmap scan
- 表膨脹或大量更新後可考慮 REINDEX 或定期 VACUUM

EXPLAIN / ANALYZE 範例

1) 等值查詢應命中索引

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM users WHERE email = 'a@example.com';

重點觀察

- Index Scan 或 Index Only Scan
- rows=1 預估與實際差距不要太大

2) 範圍查詢 + 排序 + LIMIT

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
WHERE tenant_id = 't1' AND created_at >= now() - interval '7 days'
ORDER BY created_at DESC
LIMIT 50;

對應索引

CREATE INDEX idx_orders_tenant_created_at
ON orders (tenant_id, created_at DESC);

重點觀察

- Index Scan Backward 或 Index Scan
- 避免 Sort 節點（代表索引順序沒有被利用）

3) JSONB 搜尋（GIN）

CREATE INDEX idx_events_payload_gin ON events USING GIN (payload jsonb_path_ops);

EXPLAIN (ANALYZE, BUFFERS)
SELECT id FROM events
WHERE payload @> '{"type":"signup"}';

重點觀察

- Bitmap Index Scan + Bitmap Heap Scan 常見

4) 部分索引（活躍資料）

CREATE INDEX idx_users_active_email
ON users (email)
WHERE is_active = true;

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM users WHERE is_active = true AND email = 'a@example.com';

重點觀察

- 使用 idx_users_active_email
- 條件要包含 is_active = true 才能使用部分索引

診斷提示

- Seq Scan 常見原因：選擇性太低、統計過期、索引不足
- Rows Removed by Filter 很高：索引不精準或需要複合索引
- Index Only Scan 需要 visibility map，可能先 VACUUM

設計檢查清單

- 查詢條件是否有高選擇性
- 索引順序是否對應查詢模式
- 是否需要覆蓋索引以減少回表
- 寫入成本能否接受
