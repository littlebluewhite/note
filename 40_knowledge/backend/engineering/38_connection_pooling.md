---
title: "Connection Pooling / 連線池管理"
note_type: knowledge
domain: backend
category: engineering
tags: [backend, engineering, go, rust, connection-pooling]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "38"
level: intermediate
review_interval_days: 14
next_review: 2026-03-03
---

# Connection Pooling / 連線池管理

## Purpose / 目的

連線池（Connection Pool）的核心目標是**有效管理資料庫與外部服務的連線資源**，避免資源耗盡。每次建立 TCP 連線（尤其是 TLS 握手）的成本極高，連線池透過重複使用已建立的連線來降低延遲、控制資源用量，並防止後端服務因連線數失控而癱瘓。

本指南涵蓋 PostgreSQL、Redis 的連線池診斷與調校，以 Rust（sqlx、redis-rs）和 Go（database/sql、go-redis）為範例語言。

## Symptoms / 常見症狀

| 症狀 | 表現 | 影響程度 |
|------|------|----------|
| Connection timeout | 應用程式等待連線逾時，回傳 `connection pool timed out` | 嚴重 |
| Too many connections | 資料庫端回報 `FATAL: too many connections for role` | 嚴重 |
| Connection leak | 連線池可用連線數隨時間持續下降，最終耗盡 | 嚴重 |
| 高延遲（連線建立開銷） | 每次請求都重新建立連線，P99 延遲飆升 | 中等 |
| Idle connection eviction | 閒置連線被伺服器端或池端驅逐，下次請求遭遇 cold start | 輕微 |

日誌中出現以下關鍵字時應立即診斷：`pool exhausted`、`connection pool timed out`、`too many connections`、`remaining connection slots are reserved`、`broken pipe`、`connection reset by peer`。

## Diagnostic Steps / 診斷步驟

1. **確認連線池指標** — 收集 active / idle / waiting 連線數，判斷池是否飽和。
2. **比對 pool size 與 DB max_connections** — 確認 `實例數 * pool_size` 未超過資料庫的 `max_connections`。
3. **檢查連線洩漏** — 觀察 active 連線是否只增不減。常見原因：忘記歸還連線（Go 未呼叫 `rows.Close()`、Rust 中連線未被 drop）。
4. **檢視連線存活時間與健康檢查** — 確認是否設定 `max_lifetime`、`idle_timeout`、`test_before_acquire`，避免使用已失效的連線。

## Detection Commands / 偵測指令

### PostgreSQL 連線狀態

```sql
-- 查看所有活躍連線，依狀態分組
SELECT state, usename, datname, COUNT(*)
FROM pg_stat_activity
GROUP BY state, usename, datname
ORDER BY count DESC;

-- 查看等待中的連線（可能是鎖或池飽和導致）
SELECT pid, state, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY backend_start;

-- 確認資料庫最大連線數設定
SHOW max_connections;
```

### Redis 連線狀態

```bash
# 列出所有客戶端連線
redis-cli CLIENT LIST

# 查看連線統計資訊
redis-cli INFO clients
# 關注 connected_clients、blocked_clients、tracking_clients
```

### Go：database/sql 連線池統計

```go
stats := db.Stats()
log.Printf(
    "OpenConns=%d InUse=%d Idle=%d WaitCount=%d WaitDuration=%v",
    stats.OpenConnections,
    stats.InUse,
    stats.Idle,
    stats.WaitCount,
    stats.WaitDuration,
)
```

### Rust：sqlx 連線池統計

```rust
let pool: PgPool = PgPoolOptions::new()
    .max_connections(20)
    .connect(&database_url)
    .await?;

// 取得池狀態
let size = pool.size();          // 目前池中的連線總數
let idle = pool.num_idle();      // 閒置連線數
// active = size - idle
println!("pool: size={size}, idle={idle}, active={}", size - idle as u32);
```

## Common Causes & Resolutions / 常見原因與解法

### 1. Pool 太小

**原因：** 預設的 pool size 過小，無法應付並發請求量。

**公式參考（HikariCP 建議）：**
```
pool_size = (CPU cores * 2) + effective_spindle_count
```

對於 SSD 環境，`effective_spindle_count` 通常設為 1，因此 4 核心機器建議 pool_size = 9~10。

**Rust sqlx 設定：**

```rust
use sqlx::postgres::PgPoolOptions;
use std::time::Duration;

let pool = PgPoolOptions::new()
    .max_connections(10)                       // 最大連線數
    .min_connections(2)                        // 最小閒置連線數
    .acquire_timeout(Duration::from_secs(3))   // 等待連線的逾時
    .max_lifetime(Duration::from_mins(30))     // 連線最大存活時間
    .idle_timeout(Duration::from_mins(10))     // 閒置連線逾時
    .test_before_acquire(true)                 // 取用前健康檢查
    .connect(&database_url)
    .await?;
```

**Go database/sql 設定：**

```go
db, err := sql.Open("postgres", connStr)
if err != nil {
    return fmt.Errorf("open db: %w", err)
}
db.SetMaxOpenConns(10)                  // 最大連線數
db.SetMaxIdleConns(5)                   // 最大閒置連線數
db.SetConnMaxLifetime(30 * time.Minute) // 連線最大存活時間
db.SetConnMaxIdleTime(10 * time.Minute) // 閒置連線逾時
```

### 2. Connection Leak（連線洩漏）

**原因：** 程式取得連線後未正確歸還，常見於錯誤處理路徑未關閉連線。

**Go 修復 — 務必 defer Close：**

```go
rows, err := db.QueryContext(ctx, "SELECT id, name FROM users")
if err != nil {
    return err
}
defer rows.Close() // 關鍵：確保連線歸還至池

for rows.Next() {
    var id int
    var name string
    if err := rows.Scan(&id, &name); err != nil {
        return err
    }
    // ...
}
return rows.Err()
```

**Rust 修復 — 利用 RAII 確保連線 drop：**

```rust
// sqlx 的查詢函數會自動管理連線生命週期
// 避免手動 acquire 後忘記歸還
let users = sqlx::query_as::<_, User>("SELECT id, name FROM users")
    .fetch_all(&pool)  // 自動從池中取用並歸還
    .await?;

// 若需手動取得連線，確保 scope 結束時 drop
{
    let mut conn = pool.acquire().await?;
    sqlx::query("UPDATE counter SET val = val + 1")
        .execute(&mut *conn)
        .await?;
} // conn 在此自動歸還至池
```

### 3. Idle Timeout 過於激進

**原因：** `idle_timeout` 設得太短，連線頻繁被回收再重建，造成不必要的延遲。

**解法：** 設定 `min_connections` 確保池中保有基本連線數，`idle_timeout` 建議 5~10 分鐘。

### 4. 缺少健康檢查

**原因：** 池中存在已被伺服器端關閉的死連線（如 `idle_in_transaction_session_timeout` 觸發、網路瞬斷）。

**解法：** 啟用 `test_before_acquire`（sqlx）或設定較短的 `ConnMaxLifetime`（Go）。

### 5. 多實例部署導致連線數爆炸

**原因：** 每個服務實例各自持有一個連線池，實例擴展後總連線數超過資料庫限制。

**計算公式：**
```
總連線數 = 實例數 * max_pool_size_per_instance
必須滿足：總連線數 < DB max_connections - 預留管理連線 (5~10)
```

**解法：** 在應用程式與資料庫之間加入連線代理（PgBouncer）：

```ini
# pgbouncer.ini
[databases]
mydb = host=127.0.0.1 port=5432 dbname=mydb
[pgbouncer]
pool_mode = transaction        ; 交易結束即歸還連線
max_client_conn = 1000         ; 最大客戶端連線數
default_pool_size = 20         ; 每個 user/db 的池大小
reserve_pool_size = 5          ; 備用連線
server_idle_timeout = 600      ; 伺服器端閒置逾時（秒）
```

## Prevention Checklist / 預防清單

- [ ] **連線數上限檢查**：確認 `instances * pool_size < DB max_connections - reserved`
- [ ] **設定 idle timeout**：建議 5~10 分鐘，搭配 `min_connections` 避免池完全清空
- [ ] **設定 max lifetime**：建議 30 分鐘，避免長時間佔用同一條連線
- [ ] **啟用健康檢查**：sqlx 的 `test_before_acquire(true)` 或 Go 搭配 `ConnMaxLifetime`
- [ ] **監控連線池指標**：將 active / idle / waiting / wait_duration 送至監控系統（Prometheus / Grafana）
- [ ] **多實例環境使用連線代理**：超過 5 個實例時考慮引入 PgBouncer 或 AWS RDS Proxy
- [ ] **Redis 連線池同步配置**：go-redis 與 redis-rs 預設池行為不同，需明確設定 `pool_size`
- [ ] **負載測試驗證**：上線前以預期流量的 1.5 倍進行負載測試，觀察連線池行為
- [ ] **告警設定**：pool wait_duration > 1s 或 active connections > 80% pool_size 時觸發告警

## References / 參考資料

- [sqlx PgPoolOptions 文件](https://docs.rs/sqlx/latest/sqlx/postgres/struct.PgPoolOptions.html)
- [Go database/sql 官方教學](https://go.dev/doc/database/)
- [HikariCP Pool Sizing 指南](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing)
- [PgBouncer 官方文件](https://www.pgbouncer.org/config.html)
- [PostgreSQL max_connections 調校](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [redis-rs 連線管理](https://docs.rs/redis/latest/redis/#connection-handling)
- [go-redis Options 設定](https://pkg.go.dev/github.com/redis/go-redis/v9#Options)

## Cross-references / 交叉引用

- [[../database/postgres_slow_query_triage.md|PostgreSQL 慢查詢分診]] — 連線池飽和時常伴隨慢查詢，需交叉診斷是池不夠還是查詢太慢
