---
title: "Load Testing / 負載測試"
note_type: knowledge
domain: backend
category: engineering
tags: [backend, engineering, go, rust, load-testing, benchmarking]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "35"
level: intermediate
review_interval_days: 14
next_review: 2026-03-03
---

# Load Testing / 負載測試

## Purpose / 目的

負載測試的核心目標是驗證系統在預期負載與峰值負載下的效能表現。透過模擬真實流量模式，我們能在上線前找出效能瓶頸、確認系統容量上限，並驗證是否滿足 SLO 目標。

負載測試涵蓋以下情境：

- **基準測試 (Baseline)**：在標準負載下建立效能基線，作為後續比較依據
- **壓力測試 (Stress)**：逐步增加負載直到系統崩潰，找出容量天花板
- **尖峰測試 (Spike)**：模擬突發流量（如促銷活動），驗證系統彈性
- **耐久測試 (Soak)**：長時間穩定負載，偵測記憶體洩漏與資源耗盡問題

---

## Symptoms / 常見症狀

當系統在負載下出現問題時，通常會觀察到以下症狀：

| 症狀 | 表現 | 嚴重程度 |
|------|------|----------|
| 回應時間劣化 | p99 從 50ms 飆升到 2s+ | High |
| 錯誤率飆升 | 5xx 錯誤率超過 1% | Critical |
| 資源耗盡 | CPU >90%、記憶體持續攀升、連線池用盡 | Critical |
| 吞吐量平原 | RPS 不再隨並發數增加而提升 | Medium |
| 連線超時 | 上游服務或資料庫連線逾時 | High |
| GC 停頓加劇 | Go 的 STW pause 或頻繁 GC 導致延遲抖動 | Medium |

---

## Diagnostic Steps / 診斷步驟

### Step 1：建立基線指標

在任何負載測試前，先在低流量下記錄基線數據：

- 回應時間分位數：p50 / p95 / p99
- 吞吐量 (RPS)
- 錯誤率
- 資源使用率：CPU、記憶體、goroutine / tokio task 數量、DB 連線數

### Step 2：定義負載模型

根據實際流量模式設計測試情境：

- **Ramp-up 階段**：5 分鐘內從 0 逐步升至目標 RPS
- **Steady 階段**：維持目標 RPS 持續 10-15 分鐘
- **Spike 階段**：瞬間 3-5 倍流量持續 2 分鐘
- **Cool-down 階段**：流量歸零，觀察資源是否正常釋放

### Step 3：執行負載測試並監控

同時觀察以下維度：

1. 應用層：回應時間、錯誤率、吞吐量
2. 系統層：CPU / Memory / Disk I/O / Network I/O
3. 依賴層：DB query latency、Redis hit rate、外部 API 回應時間

### Step 4：識別瓶頸類型

- **CPU-bound**：CPU 使用率高、profile 顯示計算密集函式佔比大
- **I/O-bound**：CPU 低但延遲高、等待外部資源的時間長
- **Memory-bound**：記憶體持續成長、GC 頻率增加
- **Connection-bound**：連線池使用率飽和、排隊等待連線

### Step 5：分析分位數而非平均值

平均值會隱藏長尾延遲。務必檢查 p95 和 p99，它們代表使用者實際感受到的最差體驗。

---

## Detection Commands / 偵測指令

### k6 基本負載測試腳本

```javascript
// load_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const latency = new Trend('request_latency');

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // ramp-up
    { duration: '5m', target: 100 },  // steady
    { duration: '30s', target: 500 }, // spike
    { duration: '2m', target: 100 },  // recover
    { duration: '1m', target: 0 },    // cool-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    errors: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('http://localhost:8080/api/v1/items');
  check(res, { 'status is 200': (r) => r.status === 200 });
  errorRate.add(res.status !== 200);
  latency.add(res.timings.duration);
  sleep(1);
}
```

```bash
# 執行 k6 測試並輸出結果到 Grafana
k6 run --out influxdb=http://localhost:8086/k6 load_test.js

# 快速 smoke test
k6 run --vus 10 --duration 30s load_test.js
```

### wrk / wrk2 指令

```bash
# wrk: 基本壓力測試 (12 threads, 400 connections, 30 seconds)
wrk -t12 -c400 -d30s http://localhost:8080/api/v1/items

# wrk2: 固定速率測試 (每秒 2000 請求，測試 60 秒)
wrk2 -t8 -c200 -d60s -R2000 http://localhost:8080/api/v1/items

# wrk2 搭配 Lua 腳本送 POST 請求
wrk2 -t4 -c100 -d30s -R1000 -s post.lua http://localhost:8080/api/v1/items
```

### Go Benchmark (testing.B)

```go
func BenchmarkHandleRequest(b *testing.B) {
    srv := setupTestServer()
    defer srv.Close()

    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        client := &http.Client{Timeout: 5 * time.Second}
        for pb.Next() {
            resp, err := client.Get(srv.URL + "/api/v1/items")
            if err != nil {
                b.Fatal(err)
            }
            resp.Body.Close()
        }
    })
}
```

```bash
# 執行 benchmark 並比較結果
go test -bench=BenchmarkHandleRequest -benchmem -count=5 ./... | tee new.txt
benchstat old.txt new.txt
```

### Rust Criterion Benchmark

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_serialization(c: &mut Criterion) {
    let data = generate_test_payload();

    c.bench_function("serialize_json", |b| {
        b.iter(|| {
            serde_json::to_vec(black_box(&data)).unwrap()
        })
    });

    c.bench_function("serialize_simd_json", |b| {
        b.iter(|| {
            simd_json::to_vec(black_box(&data)).unwrap()
        })
    });
}

criterion_group!(benches, bench_serialization);
criterion_main!(benches);
```

```bash
cargo bench -- --output-format bencher
```

### Grafana 負載測試期間查詢

```promql
# HTTP 請求延遲分位數
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[1m]))

# 錯誤率
sum(rate(http_requests_total{status=~"5.."}[1m]))
  / sum(rate(http_requests_total[1m]))

# Goroutine 數量趨勢
go_goroutines

# DB 連線池使用率
db_pool_active_connections / db_pool_max_connections
```

---

## Common Causes & Resolutions / 常見原因與解法

### 1. 資料庫連線池耗盡

**症狀**：高並發下出現 `connection pool exhausted` 或連線等待逾時。

**解法**：
- 適當調整連線池大小（通常 `max_connections = CPU cores * 2 + disk_spindles`）
- 優化慢查詢、加入適當索引以縮短連線佔用時間
- 使用 connection multiplexing（如 PgBouncer）

```go
// Go: 設定連線池參數
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(10)
db.SetConnMaxLifetime(5 * time.Minute)
db.SetConnMaxIdleTime(1 * time.Minute)
```

### 2. Goroutine / Tokio Task 爆量

**症狀**：goroutine 數量隨負載無限成長、記憶體飆升。

**解法**：使用有界並發控制，限制同時執行的任務數量。

```go
// Go: 使用 semaphore 限制並發
sem := make(chan struct{}, 100) // 最多 100 個並發

for req := range requests {
    sem <- struct{}{}
    go func(r Request) {
        defer func() { <-sem }()
        process(r)
    }(req)
}
```

```rust
// Rust: 使用 tokio Semaphore
let semaphore = Arc::new(Semaphore::new(100));

for req in requests {
    let permit = semaphore.clone().acquire_owned().await?;
    tokio::spawn(async move {
        process(req).await;
        drop(permit);
    });
}
```

### 3. 負載下的記憶體洩漏

**症狀**：長時間測試中記憶體持續攀升且不回落。

**解法**：使用 profiling 工具定位洩漏來源。

```bash
# Go: pprof 記憶體分析
curl -o heap.pb.gz http://localhost:6060/debug/pprof/heap
go tool pprof -http=:9090 heap.pb.gz

# Rust: 使用 DHAT 分析
cargo run --features dhat-heap -- --bench
```

### 4. 序列化效能瓶頸

**症狀**：CPU profile 顯示大量時間花在 JSON 序列化/反序列化。

**解法**：改用高效能序列化方案。

- Go：使用 `sonic` 或 `go-json` 替代 `encoding/json`
- Rust：使用 `simd-json` 替代標準 `serde_json`
- 考慮 Protocol Buffers / FlatBuffers 取代 JSON

### 5. 不當的 HTTP Client 設定

**症狀**：大量 `TIME_WAIT` 連線、DNS 解析延遲。

**解法**：重用 HTTP client、啟用 keep-alive、設定合理的 timeout。

```go
// Go: 正確的 HTTP client 設定（全域重用）
var httpClient = &http.Client{
    Timeout: 10 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 20,
        IdleConnTimeout:     90 * time.Second,
    },
}
```

---

## Prevention Checklist / 預防清單

- [ ] 每次 release 前執行基線負載測試，與前一版比較
- [ ] CI pipeline 中整合自動化負載測試（至少 smoke test 等級）
- [ ] 定義明確的 SLO 目標（如 p99 < 200ms、可用性 > 99.9%）
- [ ] 監控 p99 延遲，不要只看平均值或中位數
- [ ] 連線池、goroutine 數量、記憶體等資源設有上限與告警
- [ ] 負載測試環境盡可能貼近生產環境（硬體規格、資料量）
- [ ] 測試情境包含尖峰流量與長時間耐久測試
- [ ] 建立效能回歸偵測機制（如 benchstat / criterion 比較報告）
- [ ] 負載測試結果納入 PR review checklist（效能敏感變更時）
- [ ] 定期更新負載模型以反映實際流量成長

---

## Cross-references / 交叉引用

- [[33_testing_strategy|Testing Strategy / 測試策略]] — 負載測試在整體測試策略中的定位與分層
- [[../infrastructure/25_metrics_sli_slo_sla|Metrics & SLI/SLO/SLA]] — 負載測試的目標值應對齊 SLO 定義

---

## References / 參考資料

- [k6 Documentation](https://grafana.com/docs/k6/latest/) — 現代化負載測試工具，支援 JavaScript 腳本與 Grafana 整合
- [Criterion.rs](https://bheisler.github.io/criterion.rs/book/) — Rust 微基準測試框架，提供統計分析與回歸偵測
- [wrk2](https://github.com/giltene/wrk2) — 支援固定速率的 HTTP 壓力測試工具，解決 coordinated omission 問題
- [Go testing.B](https://pkg.go.dev/testing#B) — Go 內建 benchmark 框架
- [benchstat](https://pkg.go.dev/golang.org/x/perf/cmd/benchstat) — Go benchmark 結果統計比較工具
