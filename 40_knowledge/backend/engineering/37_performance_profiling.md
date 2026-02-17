---
title: "Performance Profiling / 效能分析"
note_type: knowledge
domain: backend
category: engineering
tags: [backend, engineering, go, rust, profiling, performance]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "37"
level: advanced
review_interval_days: 14
next_review: 2026-03-03
---

# Performance Profiling / 效能分析

## Purpose / 目的

系統性地辨識與解決效能瓶頸。效能分析是一套**可重複的科學方法**：建立基線、提出假設、用 profiler 驗證、修正、再度量。目標是將「感覺慢」轉換為「函式 X 在 p99 路徑上佔了 38% CPU 時間」這樣可行動的洞察。本筆記以 Go (pprof) 與 Rust (perf / flamegraph / criterion) 為主軸，涵蓋 CPU、記憶體、鎖競爭、I/O 四大類瓶頸。

---

## Symptoms / 常見症狀

| 症狀 | 表現 | 可能瓶頸類型 |
|------|------|-------------|
| CPU 使用率持續偏高 | 單核或多核長時間 >80% | CPU-bound 熱點 |
| 記憶體持續增長 | RSS 隨時間線性上升，重啟後回落 | Memory leak |
| 回應時間劣化 | p50 正常但 p99 異常高 | Lock contention / GC pause |
| GC 暫停過長 (Go) | STW pause >10ms，頻率過高 | Allocation pressure |
| Goroutine / Task 暴增 | goroutine 數從數百飆至數萬 | Goroutine leak |
| I/O 延遲飆升 | 磁碟 await >20ms 或 socket read 超時 | I/O-bound / 連線池耗盡 |

---

## Diagnostic Steps / 診斷步驟

1. **建立基線 (Baseline)**：紀錄 p50/p95/p99 延遲、RPS、CPU%、RSS、goroutine count。沒有基線無法判斷「慢了多少」。
2. **辨識瓶頸類型**：CPU-bound（CPU 高）、Memory-bound（RSS 持續增長）、I/O-bound（CPU 低但回應慢）、Lock contention（回應時間抖動大）。
3. **選擇 Profiler**：根據瓶頸類型使用對應工具（見 Detection Commands）。
4. **分析熱點**：從 flamegraph 找出佔比最高的呼叫路徑，關注**累積時間 (cumulative)** 而非僅看 flat time。
5. **優化並驗證**：修改後重新 profiling 確認改善，用 benchmark 量化改善幅度。

---

## Detection Commands / 偵測指令

### Go — pprof

```go
import _ "net/http/pprof"

func main() {
    go func() {
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()
}
```

```bash
# CPU profile（30 秒）
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
# Heap / Goroutine / Mutex profile
go tool pprof http://localhost:6060/debug/pprof/heap
go tool pprof http://localhost:6060/debug/pprof/goroutine
go tool pprof http://localhost:6060/debug/pprof/mutex   # 需 runtime.SetMutexProfileFraction(5)
# 互動模式指令：web (flamegraph SVG), top 20, list funcName
```

```go
// 程式碼內嵌 CPU profile
f, _ := os.Create("cpu.prof"); pprof.StartCPUProfile(f); defer pprof.StopCPUProfile()
```

### Rust — perf / flamegraph / criterion

```bash
# cargo-flamegraph 產生 CPU flamegraph
cargo flamegraph --bin my_service -- --some-arg
# 或用 perf 手動收集（Linux）
perf record -g --call-graph dwarf ./target/release/my_service && perf report
```

```rust
// Criterion benchmark
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_parser(c: &mut Criterion) {
    let input = generate_test_data();
    c.bench_function("parse_request", |b| {
        b.iter(|| parse_request(black_box(&input)))
    });
}
criterion_group!(benches, bench_parser);
criterion_main!(benches);
```

```rust
// DHAT — 記憶體配置熱點分析
#[cfg(feature = "dhat-heap")]
#[global_allocator]
static ALLOC: dhat::Alloc = dhat::Alloc;
fn main() {
    #[cfg(feature = "dhat-heap")]
    let _profiler = dhat::Profiler::new_heap();
}
// tokio-console：安裝 tokio-console，程式啟用 console-subscriber 即可即時監控 async runtime
```

### System-level Tools

```bash
top -H -p $(pgrep my_service)      # Linux thread 級 CPU 觀察
strace -c -p <PID>                  # syscall 次數與耗時統計
ss -tnp | grep my_service          # TCP 連線數與狀態
```

---

## Common Causes & Resolutions / 常見原因與解法

### 1. CPU 熱點 (CPU Hotspot)

**原因**：演算法複雜度過高、正則重複編譯、hot path 上的反射/動態分派。

```go
// Bad：每次請求編譯正則
func handler(w http.ResponseWriter, r *http.Request) {
    re := regexp.MustCompile(`\d+`)
    matches := re.FindAllString(input, -1)
}

// Good：編譯一次，重複使用
var reDigits = regexp.MustCompile(`\d+`)
func handler(w http.ResponseWriter, r *http.Request) {
    matches := reDigits.FindAllString(input, -1)
}
```

**解法**：替換演算法、快取重複計算結果、避免 hot path 上的 `reflect` 或 `fmt.Sprintf`。

### 2. 記憶體洩漏 (Memory Leak)

**Go — Goroutine leak**：goroutine 等待已無人寫入的 channel，永遠不結束。用 goroutine profile 偵測。

```go
// 解法：context 控制 goroutine 生命週期
func worker(ctx context.Context, ch <-chan Job) {
    for {
        select {
        case <-ctx.Done():
            return
        case job, ok := <-ch:
            if !ok { return }
            process(job)
        }
    }
}
```

**Rust — Arc cycle**：`Arc<Mutex<T>>` 形成迴圈引用時不會被釋放。

```rust
use std::sync::{Arc, Weak, Mutex};
struct Node {
    parent: Weak<Mutex<Node>>,       // Weak 打破迴圈
    children: Vec<Arc<Mutex<Node>>>,
}
```

### 3. 鎖競爭 (Lock Contention)

**原因**：critical section 過大、讀多寫少場景用了互斥鎖。

```rust
// Bad：鎖住整段計算
let mut data = cache.lock().await;
let result = expensive_compute(&data); // 不需要持鎖
data.insert(key, result);

// Good：只在存取共享資料時持鎖
let snapshot = { cache.lock().await.get(&key).cloned() };
let result = expensive_compute(&snapshot);
cache.lock().await.insert(key, result);
```

**解法**：縮小 critical section、改用 `sync.RWMutex` / `tokio::sync::RwLock`、考慮 lock-free 結構（`crossbeam` / `dashmap`）。

### 4. 過度配置 (Excessive Allocation)

**原因**：hot path 上頻繁建立短命物件，導致 GC 壓力或 allocator 負擔。

```go
// Go：sync.Pool 重複利用物件
var bufPool = sync.Pool{
    New: func() any { return new(bytes.Buffer) },
}
func process(data []byte) {
    buf := bufPool.Get().(*bytes.Buffer)
    defer func() { buf.Reset(); bufPool.Put(buf) }()
    buf.Write(data)
}
```

```rust
// Rust：bumpalo arena allocator 批次配置
use bumpalo::Bump;
fn process_batch(items: &[Item]) -> Vec<ProcessedItem> {
    let arena = Bump::new();
    let temp: &mut Vec<&str> = arena.alloc(Vec::new());
    for item in items {
        temp.push(arena.alloc_str(&item.name));
    }
    build_results(temp) // arena 結束時一次性釋放
}
```

---

## Prevention Checklist / 預防清單

- [ ] **持續 Profiling**：部署 Pyroscope / Parca，長期收集 profile，可回溯「從哪次部署開始變慢」
- [ ] **CI Benchmark**：`go test -bench` 或 `criterion` 在 CI 中跑，偵測效能回歸
- [ ] **資源預算**：為 container 設定 memory/CPU limits，超過時觸發告警
- [ ] **優化前後都 Profile**：每次調整必須有 before/after 數據佐證
- [ ] **避免過早優化**：先用 profiler 確認瓶頸再針對性優化
- [ ] **Review hot path 配置**：留意 `make`、`new`、`fmt.Sprintf`、`String::from` 等操作
- [ ] **監控 GC (Go)**：追蹤 `go_gc_duration_seconds`，設定 alert threshold
- [ ] **監控 async runtime (Rust)**：整合 `tokio-metrics` 或 `tokio-console`

---

## Cross-references / 交叉引用

- [[35_load_testing|Load Testing / 負載測試]] — 負載測試產生流量觸發瓶頸，profiling 結果可回饋調整負載場景
- [[../infrastructure/25_metrics_sli_slo_sla|Metrics & SLI/SLO/SLA]] — SLO 定義效能目標，profiling 是找出違反 SLO 根因的手段

---

## References / 參考資料

- [Go pprof documentation](https://pkg.go.dev/net/http/pprof) — 官方 pprof 套件文件
- [flamegraph-rs](https://github.com/flamegraph-rs/flamegraph) — Rust flamegraph 產生工具
- [Criterion.rs](https://github.com/bheisler/criterion.rs) — Rust micro-benchmark 框架
- [tokio-console](https://github.com/tokio-rs/console) — Tokio async runtime 診斷工具
- Brendan Gregg, *Systems Performance*, 2nd Ed. — 系統效能分析權威著作
- [Pyroscope](https://pyroscope.io/) — 開源持續 Profiling 平台
