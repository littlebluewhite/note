---
title: "Docker Container Fundamentals / Docker 容器基礎"
note_type: knowledge
domain: backend
category: infrastructure
tags: [backend, infrastructure, go, rust, docker, container, dockerfile, multi-stage-build]
created: 2026-02-18
updated: 2026-02-18
status: active
source: knowledge
series: backend
chapter: "57"
level: intermediate
review_interval_days: 14
next_review: 2026-03-04
---

# Docker Container Fundamentals / Docker 容器基礎

## Intent / 意圖

Docker 容器是將應用程式及其所有依賴打包成一個輕量、可移植、可重複建構的隔離單元的技術。透過掌握 Dockerfile 最佳實踐、多階段建構、映像層最佳化、容器安全強化（non-root、distroless）、Volume 掛載、網路模式與健康檢查，工程師能夠建構出體積小、啟動快、安全性高的生產級容器映像。

核心問題：**如何編寫高效的 Dockerfile 以產出最小化、安全、可快取的容器映像，並在不同環境（開發、CI/CD、生產）中以一致且可預測的方式運行應用程式？**

---

## Problem / 問題情境

**場景一：巨大的映像與緩慢的部署** — 團隊使用 `FROM ubuntu:22.04` 作為基礎映像，安裝了完整的 build toolchain（gcc、make、libssl-dev 等），最終映像大小達 1.8 GB。每次推送到 container registry 需要 4 分鐘，Kubernetes 拉取映像到新節點需要 90 秒。黑色星期五時 HPA 觸發擴展，但新 Pod 因映像拉取過慢而遲遲無法就緒，導致流量打到已經過載的現有 Pod 上。若使用多階段建構 + distroless 基礎映像，Rust 服務的最終映像僅 25 MB，拉取時間從 90 秒降到 3 秒。

**場景二：以 root 運行的安全漏洞** — 容器內的應用程式以 root 身份運行（Docker 預設行為）。攻擊者利用應用層漏洞取得容器內的 shell，因為是 root，他可以安裝工具（`apt-get install nmap`）、讀取 `/etc/shadow`、嘗試 container escape。若容器以 non-root user 運行且使用 distroless 映像（沒有 shell、沒有套件管理器），即使應用層被攻破，攻擊面大幅縮小。

**場景三：快取失效導致每次建構都從頭來** — Dockerfile 中先 `COPY . .` 再 `RUN cargo build --release`。每次修改任何一行程式碼，整個 `cargo build` 都從頭開始（因為 COPY 層的快取被破壞了，連帶後續所有層都失效）。一次 Rust 建構需要 15 分鐘，CI pipeline 因此極其緩慢。若先只 COPY `Cargo.toml` 和 `Cargo.lock` 並建構依賴層，再 COPY 原始碼建構應用程式，則修改原始碼時只需重新編譯應用程式本身（增量約 30 秒），依賴層從快取中載入。

**場景四：容器重啟後資料消失** — 開發者將 SQLite 資料庫檔案存在容器的 writable layer 中。容器因 OOM 被 kill 後重新啟動，所有資料遺失——因為容器的 writable layer 是短暫的（ephemeral），隨容器生命週期而存亡。若使用 Docker Volume 或 bind mount 將資料目錄掛載到 host，資料便能跨容器重啟持久化。

---

## Core Concepts / 核心概念

### Container Image Layers / 容器映像層

Docker 映像由多個唯讀層（read-only layers）堆疊而成，每條 Dockerfile 指令（`FROM`、`RUN`、`COPY`、`ADD`）都產生一個新層。層的核心特性：

- **內容定址（Content-addressable）**：每層以 SHA256 雜湊識別，內容完全相同的層只存儲一次
- **共享性（Shared）**：多個映像可以共享相同的基礎層，節省磁碟空間和網路傳輸
- **不可變（Immutable）**：一旦建立，層的內容不能修改
- **Union Filesystem**：運行容器時，在所有唯讀層之上新增一個 writable layer（容器層），所有寫入操作都發生在此層（Copy-on-Write 策略）

最佳化原則：將變動頻率低的指令（安裝系統依賴）放在前面，變動頻率高的指令（複製原始碼）放在後面，以最大化層快取（layer cache）的命中率。

### Multi-Stage Build / 多階段建構

多階段建構允許在一個 Dockerfile 中使用多個 `FROM` 指令，每個 `FROM` 開啟一個新的建構階段（stage）。只有最後一個階段的內容會出現在最終映像中。這讓我們可以：

1. **建構階段（Builder Stage）**：使用完整的 build toolchain（compiler、linker、development headers）編譯應用程式
2. **運行階段（Runtime Stage）**：使用最小化的基礎映像（alpine、distroless、scratch），只複製編譯好的二進位檔

效果：建構環境保留了所有需要的工具，但最終映像不包含 compiler、原始碼、中間產物，體積可縮小 10-100 倍。

### Distroless Images / 無發行版映像

Google 的 distroless 映像（`gcr.io/distroless/*`）只包含應用程式運行所需的最小依賴——沒有 shell（`/bin/sh`）、沒有套件管理器（`apt`/`apk`）、沒有常見的 Unix 工具（`ls`、`cat`、`curl`）。

安全優勢：
- **最小攻擊面**：攻擊者無法在容器內安裝工具或探索檔案系統
- **無 shell**：即使取得容器存取權，也無法啟動 shell 執行指令
- **更少的 CVE**：更少的套件意味著更少的已知漏洞

常用基礎映像比較：

| 映像 | 大小 | Shell | 套件管理器 | 適用場景 |
|------|------|-------|-----------|---------|
| `ubuntu:22.04` | ~77 MB | 有 | apt | 開發、除錯 |
| `alpine:3.19` | ~7 MB | 有 | apk | 輕量通用 |
| `gcr.io/distroless/cc` | ~20 MB | 無 | 無 | C/C++/Rust 靜態連結 |
| `gcr.io/distroless/static` | ~2 MB | 無 | 無 | Go（靜態連結）|
| `scratch` | 0 MB | 無 | 無 | 完全靜態二進位 |

### Non-Root User / 非 root 使用者

Docker 容器預設以 root（UID 0）運行。這意味著容器內的程式擁有 root 權限——若發生 container escape 漏洞，攻擊者直接以 root 身份存取 host。最佳實踐是在 Dockerfile 中建立非特權使用者並切換：

```dockerfile
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser
USER appuser
```

注意事項：
- 應用程式需要寫入的目錄（如 `/tmp`、`/var/log`）必須先設定適當權限
- 監聽 1024 以下的 port 需要 root 權限——改用 8080、3000 等高位 port
- Kubernetes 可透過 `securityContext.runAsNonRoot: true` 強制要求

### Docker Networking / Docker 網路

Docker 提供多種網路模式：

| 模式 | 說明 | 適用場景 |
|------|------|---------|
| **bridge**（預設） | 容器連接到虛擬網橋 `docker0`，透過 NAT 與外部通訊 | 單機開發、獨立服務 |
| **host** | 容器共享 host 的網路命名空間，無 NAT 開銷 | 效能敏感、需要直接存取 host 網路 |
| **none** | 容器無網路介面 | 安全敏感的批次處理 |
| **overlay** | 跨多個 Docker host 的虛擬網路 | Docker Swarm、多機部署 |
| **macvlan** | 容器獲得真實的 MAC 地址，像物理設備一樣出現在網路上 | 需要直接存取 L2 網路 |

自訂 bridge network 的優勢：容器之間可以用容器名稱（DNS）互相通訊，不需要知道 IP 地址。

### Docker Volumes / Docker 卷

資料持久化的三種方式：

1. **Named Volume**（`docker volume create mydata`）：由 Docker 管理，存儲在 `/var/lib/docker/volumes/` 下，跨容器共享，生命週期獨立於容器
2. **Bind Mount**（`-v /host/path:/container/path`）：將 host 的目錄直接掛載到容器內，適合開發時共享原始碼
3. **tmpfs Mount**：存在記憶體中的暫時掛載，容器停止後消失，適合機密資料（如密碼、token）

最佳實踐：生產環境使用 named volume（可被備份、遷移），開發環境使用 bind mount（即時反映程式碼變更）。

### Health Check / 健康檢查

Dockerfile 的 `HEALTHCHECK` 指令讓 Docker daemon 定期檢查容器是否健康：

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

參數說明：
- `interval`：檢查間隔（預設 30 秒）
- `timeout`：單次檢查超時（預設 30 秒）
- `start-period`：容器啟動後的寬限期，此期間檢查失敗不計入重試次數
- `retries`：連續失敗多少次後標記為 unhealthy（預設 3 次）

容器狀態：`starting` → `healthy` / `unhealthy`。Docker Compose 的 `depends_on` 可搭配 `condition: service_healthy` 確保依賴服務就緒後才啟動。

### Image Scanning / 映像掃描

映像掃描工具（Trivy、Grype、Snyk Container）分析映像中所有已安裝的套件和程式庫，比對已知漏洞資料庫（CVE），回報安全風險等級。應在 CI/CD pipeline 中自動掃描：

```bash
# Trivy 掃描
trivy image --severity HIGH,CRITICAL myapp:latest

# 設定門檻：有 CRITICAL 漏洞則 pipeline 失敗
trivy image --exit-code 1 --severity CRITICAL myapp:latest
```

最佳實踐：定期重建映像以取得基礎映像的安全更新、使用固定版本標籤（`alpine:3.19.1` 而非 `alpine:latest`）確保可重複建構。

### .dockerignore / 排除檔案

`.dockerignore` 類似 `.gitignore`，列出不應被 `COPY` 或 `ADD` 送入 build context 的檔案和目錄。正確配置 `.dockerignore` 可以：

- 減少 build context 傳輸量（`target/` 目錄可能數 GB）
- 避免將機密資料（`.env`、`credentials.json`）意外打包進映像
- 加速建構（更小的 context = 更快的傳輸）

```
target/
node_modules/
.git/
.env
*.md
Dockerfile
.dockerignore
```

---

## Architecture / 架構

### Docker 映像建構與運行架構

```mermaid
flowchart TB
    subgraph BuildPhase["建構階段 (Build Phase)"]
        DF["Dockerfile"]
        BC["Build Context<br/>(原始碼 + 依賴)"]
        BE["Docker Build Engine<br/>(BuildKit)"]

        DF --> BE
        BC --> BE

        subgraph Layers["映像層 (Image Layers)"]
            L1["Layer 1: FROM base image"]
            L2["Layer 2: RUN apt-get install"]
            L3["Layer 3: COPY dependencies"]
            L4["Layer 4: RUN build"]
            L5["Layer 5: COPY binary"]
            L1 --> L2 --> L3 --> L4 --> L5
        end

        BE --> Layers
    end

    subgraph Registry["Container Registry"]
        REG["Docker Hub / ECR / GCR / GHCR"]
        TAGS["Tags:<br/>latest, v1.2.3, sha-abc123"]
        REG --- TAGS
    end

    subgraph Runtime["運行階段 (Runtime)"]
        subgraph Container["Container"]
            RO["Read-Only Layers<br/>(映像層)"]
            RW["Read-Write Layer<br/>(容器層)"]
            PROC["Application Process<br/>(PID 1)"]
            RO --> RW
            RW --> PROC
        end

        VOL["Volume Mount<br/>(持久化資料)"]
        NET["Network<br/>(bridge/host/overlay)"]
        HC["Health Check<br/>(定期探測)"]

        VOL --> Container
        NET --> Container
        HC --> Container
    end

    Layers -->|"docker push"| Registry
    Registry -->|"docker pull"| Runtime

    style DF fill:#4a9eff,stroke:#333,color:#fff
    style BE fill:#2196f3,stroke:#333,color:#fff
    style REG fill:#ff9800,stroke:#333,color:#fff
    style PROC fill:#4caf50,stroke:#333,color:#fff
    style VOL fill:#9c27b0,stroke:#333,color:#fff
    style HC fill:#f44336,stroke:#333,color:#fff
```

### 多階段建構流程

```mermaid
flowchart LR
    subgraph Stage1["Stage 1: Builder"]
        S1FROM["FROM rust:1.84<br/>AS builder"]
        S1COPY["COPY Cargo.toml<br/>Cargo.lock"]
        S1DEP["RUN cargo build<br/>--release<br/>(依賴快取層)"]
        S1SRC["COPY src/ ."]
        S1BUILD["RUN cargo build<br/>--release<br/>(應用程式)"]
        S1BIN["Binary: /app/target/<br/>release/server"]

        S1FROM --> S1COPY --> S1DEP --> S1SRC --> S1BUILD --> S1BIN
    end

    subgraph Stage2["Stage 2: Runtime"]
        S2FROM["FROM gcr.io/distroless/<br/>cc-debian12"]
        S2COPY["COPY --from=builder<br/>/app/target/release/server<br/>/usr/local/bin/"]
        S2EXPOSE["EXPOSE 8080"]
        S2CMD["CMD [server]"]

        S2FROM --> S2COPY --> S2EXPOSE --> S2CMD
    end

    S1BIN -->|"只複製最終產物"| S2COPY

    subgraph FinalImage["最終映像 ≈ 25 MB"]
        FI["distroless base + 編譯好的 binary"]
    end

    S2CMD --> FinalImage

    style S1FROM fill:#e65100,stroke:#333,color:#fff
    style S2FROM fill:#1b5e20,stroke:#333,color:#fff
    style FinalImage fill:#4caf50,stroke:#333,color:#fff
    style S1BIN fill:#ff9800,stroke:#333,color:#fff
```

### 容器網路架構

```mermaid
flowchart TB
    subgraph Host["Docker Host"]
        subgraph BridgeNet["Bridge Network: app-network"]
            APP["app-container<br/>172.18.0.2:8080"]
            DB["postgres-container<br/>172.18.0.3:5432"]
            REDIS["redis-container<br/>172.18.0.4:6379"]

            APP -->|"postgres://db:5432"| DB
            APP -->|"redis://cache:6379"| REDIS
        end

        DOCKER0["docker0 bridge<br/>172.18.0.1"]
        BridgeNet --- DOCKER0

        IPTABLES["iptables NAT rules<br/>Host:80 → 172.18.0.2:8080"]
        DOCKER0 --- IPTABLES
    end

    CLIENT["External Client"]
    CLIENT -->|"Host:80"| IPTABLES

    style APP fill:#4a9eff,stroke:#333,color:#fff
    style DB fill:#ff9800,stroke:#333,color:#fff
    style REDIS fill:#f44336,stroke:#333,color:#fff
    style DOCKER0 fill:#9c27b0,stroke:#333,color:#fff
```

---

## How It Works / 運作原理

Docker 容器的運作原理基於 Linux kernel 的三大隔離機制：

1. **Namespace（命名空間隔離）**：每個容器擁有獨立的 PID namespace（只看到自己的程序）、Network namespace（獨立的網路棧和 IP）、Mount namespace（獨立的檔案系統視圖）、UTS namespace（獨立的 hostname）、IPC namespace（獨立的行程間通訊）和 User namespace（UID 映射）。這讓容器內的程序「以為」自己是系統中唯一的程序群組。

2. **Cgroups（資源限制）**：Control Groups 限制容器可使用的 CPU、記憶體、I/O、網路頻寬等資源。`docker run --memory=512m --cpus=1.5` 會建立對應的 cgroup 配置。超過記憶體限制的容器會被 OOM Killer 終止，超過 CPU 限制的容器會被 throttle。

3. **Union Filesystem（分層檔案系統）**：映像的每一層都是一個唯讀的檔案系統差異（diff）。OverlayFS（現代 Docker 的預設 storage driver）將多個層合併成一個統一的視圖。容器運行時在最上層新增一個 writable layer，所有檔案修改都透過 Copy-on-Write 發生在此層。

**映像建構流程**：

4. Docker CLI 將 build context（當前目錄，排除 `.dockerignore` 中的檔案）傳送給 Docker daemon（或 BuildKit）。

5. BuildKit 逐行解析 Dockerfile，每條指令在前一層的基礎上建立新層。若該指令的輸入（指令文本 + 檔案雜湊）與快取中的某層完全匹配，則直接使用快取層，跳過實際執行。

6. `FROM` 指令指定基礎映像（從 registry 拉取或使用本地快取）。多階段建構中，每個 `FROM` 開啟新的建構上下文，前一階段的所有層不會出現在下一階段。

7. `COPY --from=builder /app/binary /usr/local/bin/` 跨階段複製——只將需要的產物（編譯好的二進位檔）帶到最終映像。

8. 建構完成後，最終映像被打上標籤（tag）並推送到 container registry。

**容器啟動流程**：

9. `docker run` 時，Docker daemon 建立一個新的 container，分配 namespace 和 cgroup，在映像層之上新增 writable layer。

10. 設定網路——為容器分配 IP、建立 veth pair 連接到 bridge network、設定 iptables 規則。

11. 掛載 volume——將 named volume 或 bind mount 掛載到容器的檔案系統中。

12. 執行 `ENTRYPOINT` + `CMD`——容器的 PID 1 程序啟動。Docker daemon 開始按照 `HEALTHCHECK` 配置定期檢查容器健康狀態。

13. 當容器停止（程序結束或 `docker stop`），Docker 先發送 SIGTERM 給 PID 1，等待 grace period（預設 10 秒），若程序未結束則發送 SIGKILL 強制終止。Writable layer 被清除，但 volume 中的資料保留。

---

## Rust 實作

以下展示一個完整的 Axum HTTP 服務，搭配最佳化的多階段 Dockerfile。

### Rust 應用程式碼

```rust
// src/main.rs
// Axum 0.8+ HTTP 服務，含健康檢查端點

use axum::{
    extract::State,
    http::StatusCode,
    routing::get,
    Json, Router,
};
use serde::Serialize;
use std::sync::Arc;
use std::time::Instant;
use tokio::net::TcpListener;
use tokio::signal;

/// 應用程式狀態，記錄啟動時間供健康檢查使用
#[derive(Clone)]
struct AppState {
    start_time: Instant,
    version: &'static str,
}

/// 健康檢查回應結構
#[derive(Serialize)]
struct HealthResponse {
    status: String,
    version: String,
    uptime_seconds: u64,
}

/// 業務端點回應
#[derive(Serialize)]
struct OrderResponse {
    order_id: String,
    status: String,
    message: String,
}

/// 健康檢查端點 — Docker HEALTHCHECK 會定期呼叫此端點
async fn health_check(State(state): State<Arc<AppState>>) -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "healthy".to_string(),
        version: state.version.to_string(),
        uptime_seconds: state.start_time.elapsed().as_secs(),
    })
}

/// 模擬業務端點：建立訂單
async fn create_order() -> (StatusCode, Json<OrderResponse>) {
    let order_id = format!("ORD-{}", chrono::Utc::now().timestamp_millis());
    (
        StatusCode::CREATED,
        Json(OrderResponse {
            order_id,
            status: "created".to_string(),
            message: "訂單已成功建立".to_string(),
        }),
    )
}

/// 模擬業務端點：查詢訂單
async fn get_orders() -> Json<Vec<OrderResponse>> {
    Json(vec![
        OrderResponse {
            order_id: "ORD-1708300000000".to_string(),
            status: "completed".to_string(),
            message: "訂單已完成".to_string(),
        },
        OrderResponse {
            order_id: "ORD-1708300001000".to_string(),
            status: "processing".to_string(),
            message: "訂單處理中".to_string(),
        },
    ])
}

/// 優雅關閉 — 正確處理 Docker 的 SIGTERM 信號
async fn graceful_shutdown() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install SIGTERM handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => { println!("收到 Ctrl+C，開始優雅關閉..."); }
        _ = terminate => { println!("收到 SIGTERM，開始優雅關閉..."); }
    }
}

#[tokio::main]
async fn main() {
    // 從環境變數讀取 port，預設 8080（非特權 port）
    let port = std::env::var("PORT").unwrap_or_else(|_| "8080".to_string());
    let bind_addr = format!("0.0.0.0:{}", port);

    let state = Arc::new(AppState {
        start_time: Instant::now(),
        version: env!("CARGO_PKG_VERSION"),
    });

    let app = Router::new()
        .route("/health", get(health_check))
        .route("/api/orders", get(get_orders).post(create_order))
        .with_state(state);

    println!("伺服器啟動於 {}", bind_addr);

    let listener = TcpListener::bind(&bind_addr).await.unwrap();
    axum::serve(listener, app)
        .with_graceful_shutdown(graceful_shutdown())
        .await
        .unwrap();

    println!("伺服器已優雅關閉");
}

// Output:
// 伺服器啟動於 0.0.0.0:8080
// (curl http://localhost:8080/health)
// {"status":"healthy","version":"0.1.0","uptime_seconds":5}
// (curl -X POST http://localhost:8080/api/orders)
// {"order_id":"ORD-1708300000000","status":"created","message":"訂單已成功建立"}
// (收到 SIGTERM)
// 收到 SIGTERM，開始優雅關閉...
// 伺服器已優雅關閉
```

### Cargo.toml

```toml
[package]
name = "order-service"
version = "0.1.0"
edition = "2024"

[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
chrono = "0.4"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true       # 移除 debug symbols，減少二進位檔大小
panic = "abort"    # 減少 unwinding 代碼
```

### 多階段 Dockerfile（Rust）

```dockerfile
# ============================================================
# Stage 1: 依賴快取層 — 只在 Cargo.toml/Cargo.lock 變更時重建
# ============================================================
FROM rust:1.84-bookworm AS chef
RUN cargo install cargo-chef
WORKDIR /app

# 產生 recipe（依賴清單）
FROM chef AS planner
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo chef prepare --recipe-path recipe.json

# 建構依賴（這一層可被快取，只要 recipe 不變）
FROM chef AS builder
COPY --from=planner /app/recipe.json recipe.json
RUN cargo chef cook --release --recipe-path recipe.json

# 複製原始碼並建構應用程式（只有這步在原始碼修改時重新執行）
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

# ============================================================
# Stage 2: 最小化運行映像 — distroless，無 shell，非 root
# ============================================================
FROM gcr.io/distroless/cc-debian12:nonroot AS runtime

# 以非 root 使用者運行（distroless:nonroot 預設 UID 65532）
USER nonroot:nonroot

# 只複製編譯好的二進位檔
COPY --from=builder --chown=nonroot:nonroot \
    /app/target/release/order-service /usr/local/bin/order-service

# 環境變數
ENV PORT=8080

# 暴露端口
EXPOSE 8080

# 健康檢查 — 注意 distroless 沒有 curl，所以用 Kubernetes 的
# liveness/readiness probe 取代 Dockerfile HEALTHCHECK
# 若需要 Docker 層級的 health check，可改用 alpine 並安裝 curl

# 啟動指令 — 使用 exec form 確保正確接收 SIGTERM
ENTRYPOINT ["order-service"]
```

### .dockerignore

```
target/
.git/
.gitignore
.env
*.md
Dockerfile
.dockerignore
docker-compose*.yml
```

### 建構與運行指令

```bash
# 建構映像
docker build -t order-service:v0.1.0 .

# 檢查映像大小
docker images order-service:v0.1.0
# REPOSITORY      TAG     IMAGE ID       CREATED          SIZE
# order-service   v0.1.0  abc123def456   10 seconds ago   28.5MB

# 運行容器（非 root、映射 port、設定環境變數）
docker run -d \
    --name order-service \
    -p 8080:8080 \
    -e PORT=8080 \
    --read-only \
    --cap-drop=ALL \
    order-service:v0.1.0

# 安全掃描
trivy image --severity HIGH,CRITICAL order-service:v0.1.0
```

---

## Go 實作

### Go 應用程式碼

```go
// main.go
// 純標準庫 HTTP 服務，含健康檢查端點與優雅關閉

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

// HealthResponse 健康檢查回應結構
type HealthResponse struct {
	Status        string `json:"status"`
	Version       string `json:"version"`
	UptimeSeconds int64  `json:"uptime_seconds"`
}

// OrderResponse 訂單回應結構
type OrderResponse struct {
	OrderID string `json:"order_id"`
	Status  string `json:"status"`
	Message string `json:"message"`
}

// Server 封裝 HTTP 伺服器與應用狀態
type Server struct {
	startTime time.Time
	version   string
	mux       *http.ServeMux
}

// NewServer 建立新的伺服器實例
func NewServer(version string) *Server {
	s := &Server{
		startTime: time.Now(),
		version:   version,
		mux:       http.NewServeMux(),
	}
	s.registerRoutes()
	return s
}

// registerRoutes 註冊所有路由
func (s *Server) registerRoutes() {
	s.mux.HandleFunc("GET /health", s.handleHealthCheck)
	s.mux.HandleFunc("GET /api/orders", s.handleGetOrders)
	s.mux.HandleFunc("POST /api/orders", s.handleCreateOrder)
}

// handleHealthCheck Docker HEALTHCHECK 會定期呼叫此端點
func (s *Server) handleHealthCheck(w http.ResponseWriter, _ *http.Request) {
	resp := HealthResponse{
		Status:        "healthy",
		Version:       s.version,
		UptimeSeconds: int64(time.Since(s.startTime).Seconds()),
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

// handleGetOrders 查詢訂單列表
func (s *Server) handleGetOrders(w http.ResponseWriter, _ *http.Request) {
	orders := []OrderResponse{
		{
			OrderID: "ORD-1708300000000",
			Status:  "completed",
			Message: "訂單已完成",
		},
		{
			OrderID: "ORD-1708300001000",
			Status:  "processing",
			Message: "訂單處理中",
		},
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(orders)
}

// handleCreateOrder 建立新訂單
func (s *Server) handleCreateOrder(w http.ResponseWriter, _ *http.Request) {
	order := OrderResponse{
		OrderID: fmt.Sprintf("ORD-%d", time.Now().UnixMilli()),
		Status:  "created",
		Message: "訂單已成功建立",
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(order)
}

func main() {
	// 從環境變數讀取 port，預設 8080
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	version := os.Getenv("APP_VERSION")
	if version == "" {
		version = "0.1.0"
	}

	server := NewServer(version)

	httpServer := &http.Server{
		Addr:         ":" + port,
		Handler:      server.mux,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// 優雅關閉：監聽 SIGTERM（Docker stop 發送的信號）
	shutdownCh := make(chan os.Signal, 1)
	signal.Notify(shutdownCh, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		log.Printf("伺服器啟動於 :%s\n", port)
		if err := httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("伺服器啟動失敗: %v\n", err)
		}
	}()

	// 等待關閉信號
	sig := <-shutdownCh
	log.Printf("收到信號 %s，開始優雅關閉...\n", sig)

	// 給予 30 秒完成正在處理的請求
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := httpServer.Shutdown(ctx); err != nil {
		log.Fatalf("伺服器強制關閉: %v\n", err)
	}

	log.Println("伺服器已優雅關閉")
}

// Output:
// 2026/02/18 10:00:00 伺服器啟動於 :8080
// (curl http://localhost:8080/health)
// {"status":"healthy","version":"0.1.0","uptime_seconds":5}
// (curl -X POST http://localhost:8080/api/orders)
// {"order_id":"ORD-1708300000000","status":"created","message":"訂單已成功建立"}
// (docker stop order-service)
// 2026/02/18 10:05:00 收到信號 terminated，開始優雅關閉...
// 2026/02/18 10:05:00 伺服器已優雅關閉
```

### 多階段 Dockerfile（Go）

```dockerfile
# ============================================================
# Stage 1: 建構階段 — 完整的 Go toolchain
# ============================================================
FROM golang:1.24-bookworm AS builder

WORKDIR /app

# 先複製 go.mod 和 go.sum 以利用依賴快取
COPY go.mod go.sum ./
RUN go mod download && go mod verify

# 複製原始碼並建構靜態連結的二進位檔
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-s -w -X main.Version=0.1.0" \
    -o /app/order-service ./main.go

# ============================================================
# Stage 2: 最小化運行映像 — scratch（零依賴）
# ============================================================
FROM scratch

# 複製 CA 憑證（HTTPS 需要）
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# 建立非 root 使用者
# scratch 映像無法 adduser，所以直接複製 /etc/passwd
COPY --from=builder /etc/passwd /etc/passwd

# 複製編譯好的二進位檔
COPY --from=builder /app/order-service /order-service

# 環境變數
ENV PORT=8080

# 暴露端口
EXPOSE 8080

# 健康檢查 — scratch 沒有 curl，依賴 Kubernetes probe 或
# Docker Compose 的 healthcheck 使用 wget
# 若需要 Docker 層級 health check，可改用 alpine:
# HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
#   CMD wget -qO- http://localhost:8080/health || exit 1

# 以 exec form 啟動，確保 PID 1 正確接收信號
ENTRYPOINT ["/order-service"]
```

### docker-compose.yml（開發環境）

```yaml
# docker-compose.yml — 本地開發用，包含服務、資料庫、快取的完整環境
services:
  order-service:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - DATABASE_URL=postgres://appuser:secret@postgres:5432/orders?sslmode=disable
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:8080/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s
    networks:
      - app-network
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: orders
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d orders"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - app-network

volumes:
  postgres-data:
    driver: local

networks:
  app-network:
    driver: bridge
```

---

## Rust vs Go 對照表

| 比較維度 | Rust | Go |
|---------|------|-----|
| **最終映像大小** | ~25-30 MB（distroless/cc）或 ~5 MB（musl 靜態連結 + scratch） | ~5-10 MB（scratch + 靜態連結），Go 天生支援靜態連結（`CGO_ENABLED=0`） |
| **建構時間** | 首次 10-20 分鐘（依賴編譯），增量 30 秒-2 分鐘 | 首次 1-3 分鐘，增量 5-15 秒。Go 編譯器極快 |
| **依賴快取策略** | `cargo-chef` prepare/cook 分離依賴和應用程式建構，快取效果良好 | `go mod download` 原生支援，Go 模組系統天然適合 Docker 層快取 |
| **基礎映像選擇** | `distroless/cc`（需要 libc）或 `scratch`（musl 靜態連結） | `scratch` 或 `distroless/static`，Go 靜態連結後零外部依賴 |
| **交叉編譯** | 需要 `cross` 工具或設定 target triple + linker | 原生支援：`GOOS=linux GOARCH=arm64 go build` 一行搞定 |
| **信號處理（SIGTERM）** | 需要手動設定 `tokio::signal::unix::signal` | `signal.Notify` 原生支援，配合 `http.Server.Shutdown` |
| **二進位檔大小** | Release + LTO + strip 後 3-8 MB | `-ldflags="-s -w"` 後 5-12 MB |
| **安全掃描結果** | distroless 映像通常 0 CVE，但 Rust crate 生態的漏洞需用 `cargo audit` 檢查 | distroless/scratch 通常 0 CVE，Go 標準庫漏洞由 `govulncheck` 檢查 |

---

## When to Use / 適用場景

**場景一：微服務容器化部署** — 每個微服務打包為獨立的容器映像，透過 container registry 版本管理，搭配 Kubernetes 或 ECS 進行編排。多階段建構確保映像最小化，加速 CI/CD pipeline 和 Kubernetes 的 Pod 擴展。

**場景二：統一開發環境** — 使用 `docker-compose.yml` 定義完整的本地開發環境（應用程式 + 資料庫 + 快取 + 訊息佇列），新工程師 `docker compose up` 一鍵啟動，不需要手動安裝 PostgreSQL、Redis、Kafka 等依賴。

**場景三：CI/CD Pipeline 中的建構隔離** — 在 CI 環境中使用 Docker 建構映像，確保每次建構在相同的環境下執行（不依賴 CI runner 的系統配置），實現可重複建構（reproducible build）。

**場景四：邊緣部署與 IoT** — 將應用程式容器化後部署到邊緣節點（edge），利用小映像和低資源佔用在受限的硬體上運行。

---

## When NOT to Use / 不適用場景

**反模式一：容器內運行有狀態資料庫** — 雖然技術上可行（搭配 StatefulSet + PVC），但在 Docker 單機環境下直接用容器運行 PostgreSQL 或 MySQL 作為生產資料庫是危險的——writable layer 不適合高 I/O 工作負載，Volume 的效能損耗在 OLTP 場景中明顯，且缺乏叢集管理能力。生產級資料庫應使用雲端託管服務（RDS、Cloud SQL）或專用 Operator（如 CloudNativePG）。

**反模式二：過度微服務化後每個服務一個容器** — 如果系統只有 2 個開發者和 3 個簡單的 API endpoint，將每個 endpoint 拆成獨立的容器映像只會增加建構時間、映像管理成本和網路跳轉延遲。先用 monolith 容器，等真正需要獨立擴展和部署時再拆分。

**反模式三：用 Docker 取代 VM 層級的安全隔離** — Docker 容器共享 host 的 kernel，namespace 和 cgroup 的隔離強度遠低於 hypervisor。如果工作負載需要強安全隔離（如多租戶雲環境），應使用 VM 或 Kata Containers / gVisor / Firecracker 等微虛擬機技術。

---

## Real-World Examples / 真實世界案例

### Netflix — Container Image 最佳化

Netflix 的 Titus container platform 管理數百萬個容器。他們發現映像大小直接影響啟動延遲和成本：

- **映像預快取策略**：熱門映像預先拉取到所有節點，避免在擴展時等待映像下載
- **映像分層共享**：鼓勵團隊使用統一的基礎映像（internal base image），最大化跨服務的層共享率
- **安全基線映像**：安全團隊維護加固過的基礎映像（已移除不必要的套件、設定了安全配置），所有團隊必須基於此映像建構
- **自動化掃描**：每次映像推送到 registry 時自動觸發 Trivy 掃描，CRITICAL 漏洞阻擋部署

### Google — Distroless 映像

Google 開源了 distroless 映像系列，並在內部廣泛使用：

- 所有 Google Cloud 的微服務都運行在 distroless 映像上
- 透過移除 shell 和套件管理器，將容器的攻擊面降低 70%+
- 映像大小從平均 300 MB（基於 Ubuntu）降到 20-30 MB（distroless）

### Shopify — Multi-Stage Build 加速 CI

Shopify 將 Rails 應用的 Docker 建構從 20 分鐘優化到 3 分鐘：

- 使用多階段建構分離 asset compilation 和 runtime
- 利用 Docker BuildKit 的 `--mount=type=cache` 快取 Ruby gems 和 Node modules
- 最終映像從 2.1 GB 縮小到 380 MB

---

## Interview Questions / 面試常見問題

### Q1: Docker Image 和 Container 有什麼區別？

**答**：Docker Image（映像）是一個**不可變的、分層的檔案系統快照**，包含應用程式的二進位檔、依賴庫、設定檔和環境變數。可以把它想像成一個「類別定義（class definition）」。Container（容器）是映像的一個**運行實例**，就像「物件（object）」。容器在映像的所有唯讀層之上新增一個 writable layer（使用 Copy-on-Write），所有運行時的檔案修改都發生在此層。同一個映像可以同時運行多個容器，每個容器有自己獨立的 writable layer、網路命名空間、PID 命名空間。當容器被刪除，writable layer 也隨之消失，但映像不受影響。

### Q2: 為什麼 Dockerfile 中指令的順序很重要？如何最佳化建構快取？

**答**：Docker 的建構快取機制是**逐層比對**的——每條指令產生的層都有一個基於指令內容和輸入檔案的雜湊值。當某一層的快取失效（cache miss），該層之後的所有層都必須重新建構。因此最佳化原則是：

1. **將變動頻率低的指令放在前面**：如 `FROM`、`RUN apt-get install`（系統依賴很少變動）
2. **先複製依賴定義檔**：`COPY go.mod go.sum ./` + `RUN go mod download`，只有依賴變更時才重新下載
3. **最後複製原始碼**：`COPY . .`，每次程式碼修改只需重建最後幾層
4. **合併 RUN 指令**：多個 `RUN` 合成一個以減少層數，且用 `&&` 連接可以在同一層中安裝並清理快取（`apt-get clean`）

錯誤做法：先 `COPY . .` 再安裝依賴——任何原始碼修改都導致依賴重新安裝。

### Q3: 什麼是 Docker 多階段建構？解決了什麼問題？

**答**：多階段建構允許在一個 Dockerfile 中使用多個 `FROM` 指令，每個 `FROM` 開啟一個新的建構階段。只有最後一個階段的內容會進入最終映像。它解決的核心問題是**建構環境 vs 運行環境的分離**：

- **建構階段**需要完整的 compiler、linker、development headers（如 `rust:1.84`、`golang:1.24`），這些工具可能佔用數百 MB 到數 GB
- **運行階段**只需要編譯好的二進位檔和最小的 runtime（如 `scratch`、`distroless`）

沒有多階段建構之前，工程師要麼接受臃腫的映像（將 compiler 留在最終映像中），要麼維護兩個 Dockerfile（一個建構、一個打包）並用 shell script 協調。多階段建構用一個 Dockerfile 解決了這個問題，且 `COPY --from=builder` 跨階段複製讓產物傳遞非常清晰。

### Q4: 容器的 PID 1 問題是什麼？為什麼重要？

**答**：在 Linux 中，PID 1 是 init 程序，它有兩個特殊責任：(1) **收割孤兒程序（reap zombie processes）**——當子程序結束但父程序未呼叫 `wait()` 時，子程序成為殭屍（zombie），PID 1 負責清理；(2) **信號處理**——預設情況下，PID 1 不會被 SIGTERM 殺掉（kernel 的保護機制）。

在 Docker 容器中，`ENTRYPOINT` 或 `CMD` 指定的程序成為 PID 1。如果使用 shell form（`CMD node server.js`），實際的 PID 1 是 `/bin/sh -c`，`node` 是它的子程序。當 `docker stop` 發送 SIGTERM 時，shell 收到但不會轉發給 `node`——等待 grace period 後 Docker 發送 SIGKILL 強制終止，導致不優雅的關閉（正在處理的請求被中斷、資料庫連線未正確關閉）。

解決方案：(1) 使用 exec form（`CMD ["node", "server.js"]`），讓應用程式成為真正的 PID 1；(2) 使用 `tini` 或 `dumb-init` 作為 PID 1（負責信號轉發和殭屍收割），應用程式作為其子程序。Docker 的 `--init` flag 或 Kubernetes 會自動處理。

### Q5: 如何確保 Docker 容器的安全性？

**答**：生產環境的容器安全是一個多層防禦策略：

1. **最小化映像**：使用 distroless 或 scratch 基礎映像，移除不必要的工具（shell、套件管理器、curl），減少攻擊面
2. **非 root 運行**：在 Dockerfile 中 `USER nonroot` 或 Kubernetes 的 `securityContext.runAsNonRoot: true`
3. **唯讀檔案系統**：`docker run --read-only` 或 K8s 的 `readOnlyRootFilesystem: true`，防止攻擊者寫入惡意檔案
4. **刪除所有 capabilities**：`--cap-drop=ALL`，只按需新增（`--cap-add=NET_BIND_SERVICE`）
5. **映像掃描**：在 CI 中用 Trivy/Grype 掃描已知漏洞，CRITICAL 漏洞阻擋部署
6. **固定版本標籤**：使用 `alpine:3.19.1` 而非 `alpine:latest`，確保可重複建構
7. **機密管理**：絕不在映像中嵌入 secrets（`.env`、API key），使用 Docker Secrets 或外部 secret manager（Vault）
8. **多階段建構**：最終映像不包含原始碼、build tools、development dependencies
9. **`no-new-privileges`**：防止容器內程序透過 `setuid` 提升權限

---

## Pitfalls / 常見陷阱

### 陷阱 1：使用 `latest` 標籤導致不可重複建構

```dockerfile
# 錯誤：latest 標籤指向的映像會變動，今天和明天建構出不同的映像
FROM rust:latest
RUN apt-get update && apt-get install -y libssl-dev

# 正確：固定完整的版本標籤，確保可重複建構
FROM rust:1.84.0-bookworm
RUN apt-get update && apt-get install -y libssl-dev=3.0.13-1~deb12u1
```

**說明**：`latest` 是一個浮動標籤（mutable tag），registry 上的 `latest` 可能隨時指向新版本。同一個 Dockerfile 在不同時間建構可能產生不同的映像，違反可重複建構原則。更嚴重的是，新基礎映像可能引入不相容的變更或新漏洞。

### 陷阱 2：在映像中嵌入機密資料

```dockerfile
# 錯誤：機密資料被永久嵌入映像層中，即使後續刪除也可用 docker history 看到
COPY .env /app/.env
RUN source /app/.env && npm run build
RUN rm /app/.env  # ← 無效！.env 仍存在於前一層

# 正確：使用 BuildKit 的 --mount=type=secret
RUN --mount=type=secret,id=env_file,target=/app/.env \
    source /app/.env && npm run build
# Secret 不會被寫入任何映像層
```

**說明**：Docker 映像的每一層都是不可變的。即使在後續層中 `RUN rm`，檔案仍然存在於建立它的那一層中。任何人 `docker pull` 映像後都可以用 `docker history` 或 `dive` 工具檢視每一層的內容。

### 陷阱 3（Rust 特定）：未利用依賴快取導致每次建構 15 分鐘

```dockerfile
# 錯誤：COPY 所有檔案後建構，任何原始碼修改都重新編譯所有依賴
FROM rust:1.84 AS builder
WORKDIR /app
COPY . .
RUN cargo build --release  # 每次 15 分鐘

# 正確：用 cargo-chef 分離依賴建構和應用程式建構
FROM rust:1.84 AS chef
RUN cargo install cargo-chef
WORKDIR /app

FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

FROM chef AS builder
COPY --from=planner /app/recipe.json recipe.json
RUN cargo chef cook --release --recipe-path recipe.json  # 依賴層，可快取
COPY . .
RUN cargo build --release  # 只編譯應用程式，30 秒
```

**說明**：Rust 的 crate 編譯是建構中最耗時的部分。`cargo-chef` 透過 `prepare`（產生依賴清單）和 `cook`（只建構依賴）兩步，將依賴建構分離為獨立的 Docker 層。只要 `Cargo.toml` 和 `Cargo.lock` 不變，依賴層就能從快取中載入。

### 陷阱 4（Go 特定）：忘記 `CGO_ENABLED=0` 導致映像無法運行

```dockerfile
# 錯誤：Go 預設啟用 CGO，連結 glibc，但 scratch/alpine 映像沒有 glibc
FROM golang:1.24 AS builder
WORKDIR /app
COPY . .
RUN go build -o server .

FROM scratch
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]
# 運行時報錯：exec /server: no such file or directory
# （因為找不到 glibc 動態連結庫）

# 正確：禁用 CGO 以產生靜態連結的二進位檔
FROM golang:1.24 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server .

FROM scratch
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]
# 正常運行
```

**說明**：Go 預設啟用 CGO（使用系統 C 庫），編譯出的二進位檔動態連結到 glibc。`scratch` 映像沒有任何系統庫，所以執行時報錯（錯誤訊息「no such file or directory」具有誤導性，看起來像是檔案不存在，實際上是找不到動態連結器 `ld-linux`）。`CGO_ENABLED=0` 強制純 Go 編譯，產生完全靜態連結的二進位檔。

### 陷阱 5：使用 shell form 而非 exec form 導致信號無法傳遞

```dockerfile
# 錯誤：shell form — 實際 PID 1 是 /bin/sh，應用程式收不到 SIGTERM
CMD node server.js
# docker stop 時 node 收不到 SIGTERM，等 10 秒後被 SIGKILL

# 正確：exec form — 應用程式直接成為 PID 1
CMD ["node", "server.js"]
# docker stop 時 node 收到 SIGTERM，可以優雅關閉
```

### 陷阱 6：每個 RUN 指令產生一個層，未清理快取導致映像臃腫

```dockerfile
# 錯誤：apt cache 被保留在映像層中，佔用 ~50 MB
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get clean  # 無效！快取已在前兩層中

# 正確：合併為一條 RUN 指令，同一層中安裝並清理
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### 陷阱 7（Rust 特定）：未設定 `strip = true` 導致二進位檔過大

```toml
# 錯誤：預設 release 包含 debug symbols
[profile.release]
opt-level = 3  # 二進位檔 30-50 MB

# 正確：strip debug symbols + LTO 最佳化
[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true       # 移除 debug symbols，二進位檔 3-8 MB
panic = "abort"    # 移除 unwinding 代碼
```

### 陷阱 8（Go 特定）：未設定 `-ldflags="-s -w"` 導致二進位檔包含 debug 資訊

```bash
# 錯誤：預設包含 symbol table 和 DWARF debug info
go build -o server .  # 二進位檔 ~15 MB

# 正確：strip symbol table (-s) 和 DWARF debug info (-w)
go build -ldflags="-s -w" -o server .  # 二進位檔 ~8 MB
```

---

## Cross-references / 交叉引用

- [[41_kubernetes_core_concepts]] — K8s 是容器編排的下一步，本章的映像最佳化直接影響 K8s 的 Pod 啟動速度
- [[42_service_mesh]] — Service Mesh 的 sidecar 容器（Envoy）也需要最佳化映像大小
- [[40_cicd_deployment]] — CI/CD pipeline 中的映像建構、掃描、推送流程
- [[50_infrastructure_as_code]] — Terraform/Pulumi 管理 container registry、ECS/EKS 等基礎設施
- [[28_owasp_api_security]] — 容器安全是 API 安全的一環，non-root 和 distroless 是防禦縱深的一部分

---

## References / 參考資料

- Docker 官方文件 — Dockerfile Best Practices: https://docs.docker.com/build/building/best-practices/
- Google Distroless Images: https://github.com/GoogleContainerTools/distroless
- Docker BuildKit: https://docs.docker.com/build/buildkit/
- Trivy Container Scanner: https://aquasecurity.github.io/trivy/
- cargo-chef — Rust Docker 依賴快取工具: https://github.com/LukeMathWalker/cargo-chef
- CIS Docker Benchmark — 容器安全基線: https://www.cisecurity.org/benchmark/docker
- Kubernetes Container Security — Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/
