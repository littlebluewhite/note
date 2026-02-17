---
title: "Multi-level Cache & Invalidation / 多層快取與失效"
note_type: knowledge
domain: backend
category: infrastructure
tags: [backend, infrastructure, go, rust, cache-invalidation]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "22"
level: advanced
review_interval_days: 14
next_review: 2026-03-03
---

# Multi-level Cache & Invalidation / 多層快取與失效

## Purpose / 目的

本指南用於診斷與解決多層快取架構（L1 in-process / L2 distributed / L3 origin）中的快取一致性問題。涵蓋失效傳播失敗、TTL 設定錯誤、快取雪崩（stampede）以及刪除後幽靈讀取等場景的排查流程與修復方案。

## Symptoms / 常見症狀

| 症狀 | 影響層級 | 嚴重程度 |
|------|---------|---------|
| 資料更新後仍讀到舊值（stale reads） | L1 / L2 | High |
| 快取到期時大量請求穿透到 origin（cache stampede） | L2 / L3 | Critical |
| L1 與 L2 之間資料不一致 | L1 ↔ L2 | High |
| 刪除紀錄後仍可讀取（ghost reads） | L1 / L2 | Medium |
| 快取命中率突然下降 | 全層級 | Medium |
| 寫入後立即讀取得到舊值（read-your-writes violation） | L1 | High |

## Diagnostic Steps / 診斷步驟

**Step 1 — 確認各層 TTL 設定：** 驗證 TTL 階層是否遵守 `L1 TTL < L2 TTL < L3 TTL` 原則。TTL 倒掛是最常見的一致性問題根源。

**Step 2 — 驗證失效事件傳播：** 追蹤一次寫入操作，確認失效事件是否成功從寫入點傳播到所有快取層。檢查 pub/sub channel 的訂閱數量與訊息投遞狀態。

**Step 3 — 檢查各層快取命中率：** 命中率異常下降表示失效策略過於激進或 TTL 過短；異常升高則可能代表失效訊息遺失。

**Step 4 — 追蹤請求路徑：** 對單一請求進行全路徑追蹤，記錄每層的 hit/miss 狀態與回應時間，找出不一致發生的具體層級。

**Step 5 — 比對各層快取內容：** 直接讀取 L1 與 L2 中同一 key 的值與版本號，不一致時比對最後更新時間戳。

## Detection Commands / 偵測指令

### Redis CLI 診斷

```bash
# 檢查特定 key 的剩餘 TTL
redis-cli TTL cache:user:1001
# 檢查 key 的內部編碼與閒置時間
redis-cli DEBUG OBJECT cache:user:1001
# 查看快取命中率統計
redis-cli INFO stats | grep keyspace
# 監控即時失效事件
redis-cli SUBSCRIBE __keyevent@0__:expired
# 檢查 pub/sub 頻道的訂閱者數量
redis-cli PUBSUB NUMSUB cache:invalidation
# 批次檢查特定 prefix 下的 key 數量
redis-cli --scan --pattern "cache:user:*" | wc -l
```

### Application Metrics / Log

```bash
# Prometheus: 各層快取命中率
curl -s 'http://localhost:9090/api/v1/query?query=cache_hit_total/(cache_hit_total+cache_miss_total)'
# 快取失效事件延遲（p99）
curl -s 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.99,cache_invalidation_delay_seconds_bucket)'
# 搜尋失效事件傳播失敗
grep -E "invalidation.*(fail|timeout|error)" /var/log/app/cache.log
# 搜尋 cache stampede 徵兆
grep "cache_miss" /var/log/app/cache.log | awk '{print $5}' | sort | uniq -c | sort -rn | head -20
```

## Common Causes & Resolutions / 常見原因與解法

### 1. L1 在 L2 更新後仍為舊值 — Pub/Sub 失效

**原因：** L2 更新時未發送失效通知到持有 L1 快取的所有 instance。

```go
// Go: 透過 Redis Pub/Sub 訂閱失效事件並清除 L1
type MultiLevelCache struct {
	l1    sync.Map
	redis *redis.Client
}

func (c *MultiLevelCache) SubscribeInvalidation(ctx context.Context) {
	sub := c.redis.Subscribe(ctx, "cache:invalidation")
	go func() {
		for msg := range sub.Channel() {
			c.l1.Delete(msg.Payload)
			log.Printf("[L1] invalidated key=%s via pub/sub", msg.Payload)
		}
	}()
}

func (c *MultiLevelCache) Set(ctx context.Context, key string, val []byte) error {
	if err := c.redis.Set(ctx, key, val, 0).Err(); err != nil {
		return err
	}
	c.l1.Store(key, val)
	return c.redis.Publish(ctx, "cache:invalidation", key).Err()
}
```

```rust
// Rust: 訂閱失效事件並清除 L1
use dashmap::DashMap;
use std::sync::Arc;

pub struct MultiLevelCache {
    l1: Arc<DashMap<String, Vec<u8>>>,
}

impl MultiLevelCache {
    pub async fn subscribe_invalidation(&self, mut shutdown: tokio::sync::broadcast::Receiver<()>) {
        let l1 = Arc::clone(&self.l1);
        let client = redis::Client::open("redis://127.0.0.1/").unwrap();
        let mut pubsub = client.get_async_pubsub().await.unwrap();
        pubsub.subscribe("cache:invalidation").await.unwrap();
        tokio::spawn(async move {
            let mut stream = pubsub.into_on_message();
            loop {
                tokio::select! {
                    Some(msg) = stream.next() => {
                        if let Ok(key) = msg.get_payload::<String>() {
                            l1.remove(&key);
                            tracing::info!(key = %key, "L1 invalidated via pub/sub");
                        }
                    }
                    _ = shutdown.recv() => break,
                }
            }
        });
    }
}
```

### 2. TTL 層級不一致導致 stale reads — 階層式 TTL

**原因：** L1 TTL 大於 L2 TTL，L2 過期重新載入新值後 L1 仍持有舊值。

```go
// Go: 階層式 TTL 策略
const (
	L1TTL = 30 * time.Second  // in-process: 最短
	L2TTL = 5 * time.Minute   // Redis: 中等
	L3TTL = 30 * time.Minute  // origin/CDN: 最長
)

func (c *MultiLevelCache) Get(ctx context.Context, key string) ([]byte, error) {
	if val, ok := c.l1.Load(key); ok {
		return val.([]byte), nil
	}
	val, err := c.redis.Get(ctx, key).Bytes()
	if err == redis.Nil {
		val, err = c.fetchFromOrigin(ctx, key)
		if err != nil { return nil, err }
		c.redis.Set(ctx, key, val, L2TTL)
	}
	c.l1.Store(key, val) // L1 TTL 由背景清理 goroutine 管理
	return val, nil
}
```

### 3. Write-through 部分失敗 — 版本號冪等寫入

**原因：** 寫入 DB 成功但更新快取失敗，導致不一致。

```rust
// Rust: 帶版本號的冪等寫入（Lua script 確保原子性）
use redis::Script;

pub async fn write_through_with_version(
    conn: &mut redis::aio::MultiplexedConnection,
    key: &str, value: &[u8], expected_version: u64,
) -> Result<bool, redis::RedisError> {
    let script = Script::new(r#"
        local cur = redis.call('HGET', KEYS[1], 'version')
        if cur == false or tonumber(cur) < tonumber(ARGV[2]) then
            redis.call('HSET', KEYS[1], 'data', ARGV[1], 'version', ARGV[2])
            redis.call('EXPIRE', KEYS[1], ARGV[3])
            redis.call('PUBLISH', 'cache:invalidation', KEYS[1])
            return 1
        end
        return 0
    "#);
    let result: i32 = script.key(key).arg(value).arg(expected_version)
        .arg(300).invoke_async(conn).await?;
    Ok(result == 1)
}
```

### 4. 事件驅動失效延遲過高 — CDC with Debezium

**原因：** 應用層發送失效事件有延遲，或在寫入與發送事件之間 crash。

```go
// Go: 消費 Debezium CDC 事件進行快取失效
func (c *MultiLevelCache) ConsumeCDCEvents(ctx context.Context, consumer *kafka.Consumer) {
	for {
		select {
		case <-ctx.Done():
			return
		default:
			msg, err := consumer.ReadMessage(ctx)
			if err != nil { log.Printf("[CDC] read error: %v", err); continue }
			var event struct {
				Table      string `json:"table"`
				PrimaryKey string `json:"primary_key"`
				Operation  string `json:"op"` // c=create, u=update, d=delete
			}
			if err := json.Unmarshal(msg.Value, &event); err != nil { continue }
			cacheKey := fmt.Sprintf("cache:%s:%s", event.Table, event.PrimaryKey)
			c.redis.Del(ctx, cacheKey)
			c.redis.Publish(ctx, "cache:invalidation", cacheKey)
			log.Printf("[CDC] invalidated key=%s op=%s", cacheKey, event.Operation)
		}
	}
}
```

## Prevention Checklist / 預防清單

- [ ] **採用事件驅動失效** — 避免僅依賴 TTL，使用 pub/sub 或 CDC 主動失效
- [ ] **嚴格遵守 TTL 階層** — L1 (10-30s) < L2 (1-5min) < L3 (5-30min)
- [ ] **實作快取版本號** — 每次寫入遞增版本號，防止 ABA 問題
- [ ] **監控各層命中率** — 告警閾值 L1 > 90%, L2 > 80%，異常波動立即調查
- [ ] **測試失效路徑** — 整合測試中驗證寫入後所有快取層皆已失效或更新
- [ ] **實作 cache stampede 保護** — 使用 singleflight (Go) 或分散式鎖防止同一 key 同時回源
- [ ] **設定重試與死信佇列** — 失效訊息遺失時有補償機制
- [ ] **定期快取一致性審計** — 抽樣比對快取值與 DB 值，量化不一致率
- [ ] **監控端到端失效延遲** — 從 DB 寫入到最後一層快取失效應 < 1s

## Cross-references / 交叉引用

- [[21_caching_redis_patterns]] — Redis 快取模式（Cache-Aside, Write-Through, Write-Behind）與基礎 Redis 操作指南

## References / 參考資料

- [Facebook TAO](https://www.usenix.org/conference/atc13/technical-sessions/presentation/bronson) — Meta 的多層快取一致性實踐
- [Scaling Memcache at Facebook](https://research.facebook.com/publications/scaling-memcache-at-facebook/) — 大規模快取失效策略
- [Debezium Documentation](https://debezium.io/documentation/) — CDC 實作參考
- [Redis Pub/Sub](https://redis.io/docs/interact/pubsub/) — 即時失效通知機制
- [Go singleflight](https://pkg.go.dev/golang.org/x/sync/singleflight) — 防止 cache stampede 的 Go 標準方案
