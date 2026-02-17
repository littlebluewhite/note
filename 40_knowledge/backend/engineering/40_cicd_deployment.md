---
title: "CI/CD & Deployment / CI/CD 與部署策略"
note_type: knowledge
domain: backend
category: engineering
tags: [backend, engineering, go, rust, cicd, deployment, docker, github-actions]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "40"
level: intermediate
review_interval_days: 14
next_review: 2026-03-03
---

# CI/CD & Deployment / CI/CD 與部署策略

## Intent / 意圖

透過**自動化建置、測試與部署流程**，實現可靠且可重現的軟體發佈。CI/CD 的核心價值是讓每一次部署都經過相同的驗證流程——從程式碼推送到正式環境，全程自動化、可追蹤、可回滾。好的流水線能在數分鐘內給予「這次改動是否安全上線」的信心，並在出問題時秒級回滾。

核心問題：**如何建構自動化流水線，確保每次變更都經過一致的建置、測試與部署驗證，同時支援零停機部署與快速回滾？**

---

## Problem / 問題情境

**場景一：手動部署造成人為錯誤** — 工程師照 wiki 的 12 步手冊 SSH 進 production 執行部署。第 8 步漏了 `export DATABASE_URL=...`，服務連不上 DB，500 error。修復花 40 分鐘，其中 30 分鐘在找漏了哪步。

**場景二："Works on my machine"** — 本機 Go 1.24，CI server Go 1.22。用了 `range over integer`（1.22+ 語法），本機全過、CI 編譯失敗。排查兩小時才發現版本差異。Docker 化建置環境能徹底消除此問題。

**場景三：環境不一致** — staging 用 `docker-compose`，production 用 K8s。staging 環境變數在 `.env`，production 在 ConfigMap。staging 驗證通過，production 缺 `REDIS_TLS_ENABLED=true` 導致 Redis 連線失敗 15 分鐘。

---

## Core Concepts / 核心概念

### Continuous Integration (CI) / 持續整合
每位開發者至少每天一次合併程式碼到主幹，自動觸發建置與測試。目標是**儘早發現整合衝突**，在合併時攔截問題而非上線後爆發。

### Continuous Delivery vs Continuous Deployment / 持續交付 vs 持續部署
**Delivery**：通過 CI 的建置**可以**部署到 production，但需人工核准。**Deployment**：通過 CI 即**自動**部署，無需人工介入。多數團隊從 delivery 開始，成熟後邁向 deployment。

### Pipeline Stages / 流水線階段
`Build` → `Unit Test` → `Lint` → `Integration Test` → `Build Image` → `Push Registry` → `Deploy Staging` → `Smoke Test` → `Deploy Production`。每階段失敗即中斷。

### Docker Multi-Stage Build / Docker 多階段建置
單一 Dockerfile 多個 `FROM`，前期編譯、最終僅複製 binary 至最小 base image。好處：(1) 建置工具不進正式映像檔；(2) 映像檔從數百 MB 縮至數十 MB；(3) layer caching 加速。

### Image Layer Caching / 映像檔層快取
Docker 按指令順序建構 layer，前層沒變則後層用快取。**依賴放前面、原始碼放後面**。Rust 用 `cargo-chef` 分離依賴層；Go 用 `go mod download` 獨立一層。

### Blue-Green Deployment / 藍綠部署
維護兩套完整環境，流量導向 blue，部署新版到 green，驗證後切換 LB。回滾秒級（切回 blue）。**缺點**：雙倍資源。

### Canary Deployment / 金絲雀部署
新版先部署到 5% pod，觀察 error rate、latency。正常後逐步擴大至 100%。爆炸半徑可控，但**需完善的可觀測性**。

### Rolling Deployment / 滾動部署
逐個替換舊版 pod。K8s 預設 `maxSurge: 25%, maxUnavailable: 25%`。新舊共存需 API 向後相容。

### Feature Flags / 功能旗標
程式碼部署與功能發佈解耦。新功能隱藏在 flag 後，透過設定（非部署）控制開關，實現漸進式發佈與緊急關閉。

### Rollback Strategies / 回滾策略
(1) **Image rollback**：指定前版 tag 部署；(2) **Git revert**：觸發 CI 重建；(3) **Instant switch**：藍綠切換。**任何部署都必須有回滾計畫，5 分鐘內完成。**

### Database Migration in CI / CI 中的資料庫遷移
遷移必須**向前相容**——先加欄位再部署新版，刪舊欄位在確認無舊版 pod 後的下個 release。切勿同步驟執行破壞性 migration。

### Artifact Registry / 製品倉庫
集中儲存 Docker image、binary、Helm chart。以 commit SHA 或 semver 標記，確保可追溯。常見：ghcr.io、ECR、Google Artifact Registry。

### GitOps / Git 即運維
Git repo 作為部署的 single source of truth。Argo CD / Flux 偵測變更後自動同步至 K8s cluster。審計清晰、可 revert、PR review 即 deployment review。

---

## Architecture / 架構

### CI/CD Pipeline Flow / CI/CD 流水線流程

```mermaid
flowchart LR
    PUSH["git push"] --> BUILD["Build<br/>(multi-stage Docker)"]
    BUILD --> UNIT["Unit Test<br/>+ Lint"]
    UNIT --> INTEG["Integration Test"]
    INTEG --> IMAGE["Build & Push<br/>Image to Registry"]
    IMAGE --> STAGING["Deploy to<br/>Staging"]
    STAGING --> SMOKE["Smoke Test<br/>on Staging"]
    SMOKE --> CANARY["Canary 5%<br/>Production"]
    CANARY --> OBSERVE{"Metrics OK?<br/>(error rate, p99)"}
    OBSERVE -->|Yes| ROLLOUT["Progressive<br/>Rollout 100%"]
    OBSERVE -->|No| ROLLBACK["Rollback to<br/>Previous Version"]
    ROLLBACK -.->|"alert"| ONCALL["On-Call<br/>Notification"]
    style PUSH fill:#4a9eff,color:#fff
    style BUILD fill:#4a9eff,color:#fff
    style UNIT fill:#10ac84,color:#fff
    style INTEG fill:#10ac84,color:#fff
    style IMAGE fill:#ff9f43,color:#fff
    style STAGING fill:#a55eea,color:#fff
    style CANARY fill:#ee5a6f,color:#fff
    style ROLLOUT fill:#10ac84,color:#fff
    style ROLLBACK fill:#ee5a6f,color:#fff
```

### Deployment Strategies Comparison / 部署策略比較

```mermaid
flowchart TB
    subgraph BG["Blue-Green"]
        direction LR
        LB1["Load Balancer"] -->|"100%"| BLUE["Blue (v1)"]
        LB1 -.->|"switch"| GREEN["Green (v2)"]
    end
    subgraph CN["Canary"]
        direction LR
        LB2["Load Balancer"] -->|"95%"| STABLE["Stable (v1)"]
        LB2 -->|"5%"| CANARY2["Canary (v2)"]
    end
    subgraph RL["Rolling"]
        direction LR
        POD1["Pod v2 ✓"] ~~~ POD2["Pod v2 ✓"] ~~~ POD3["Pod v1 → v2"] ~~~ POD4["Pod v1"]
    end
    style BLUE fill:#4a9eff,color:#fff
    style GREEN fill:#10ac84,color:#fff
    style STABLE fill:#4a9eff,color:#fff
    style CANARY2 fill:#ee5a6f,color:#fff
```

---

## How It Works / 運作原理

### GitHub Actions Key Mechanisms / GitHub Actions 關鍵機制

1. **Caching**：`actions/cache` 快取依賴（`~/.cargo/registry`、`~/go/pkg/mod`），避免每次重新下載。
2. **Matrix strategy**：平行測試多版本（Go 1.23 / 1.24、Rust stable / nightly）。
3. **Concurrency control**：`concurrency` 群組確保同一分支只跑一個 workflow，取消過時的。
4. **Environment protection**：production environment 設定 required reviewers，防止未經核准的部署。

### Docker Multi-Stage Build Optimization / Docker 多階段建置最佳化

**Rust**：`cargo-chef` 從 `Cargo.toml` + `Cargo.lock` 生成 recipe，先建置 dependency layer（可快取），再複製原始碼建置應用。只改業務程式碼時建置從 8 分鐘降至 1 分鐘。

**Go**：靜態編譯產生單一二進位檔，映像檔可用 `scratch`（0 MB）或 `distroless/static`（~2 MB）。`go mod download` 獨立一層快取依賴，`CGO_ENABLED=0` 確保純靜態連結。

### Deployment Strategies Comparison / 部署策略比較

| 面向 | Blue-Green | Canary | Rolling |
|------|-----------|--------|---------|
| **回滾速度** | 秒級（切 LB） | 秒級（移除 canary） | 分鐘級 |
| **資源需求** | 雙倍 | +5~10% | 同等 |
| **風險控制** | 全有或全無 | 漸進式，可控 | 中等 |
| **版本共存** | 無 | 有（需 API 相容） | 有 |
| **適用場景** | DB schema 大改 | 高流量嚴格 SLA | 一般 stateless |

---

## Rust 實作

### Dockerfile — Multi-Stage with cargo-chef

```dockerfile
# ── Stage 1: Chef — 安裝 cargo-chef ──
FROM rust:1.82-bookworm AS chef
RUN cargo install cargo-chef
WORKDIR /app

# ── Stage 2: Planner — 生成依賴 recipe ──
FROM chef AS planner
COPY Cargo.toml Cargo.lock ./
COPY src/ src/
RUN cargo chef prepare --recipe-path recipe.json

# ── Stage 3: Builder — 先建置依賴（可快取），再建置應用 ──
FROM chef AS builder
COPY --from=planner /app/recipe.json recipe.json
# 建置依賴 layer（只要 Cargo.toml/Cargo.lock 沒變就用快取）
RUN cargo chef cook --release --recipe-path recipe.json
# 複製原始碼並建置應用程式
COPY Cargo.toml Cargo.lock ./
COPY src/ src/
RUN cargo build --release --bin order-service

# ── Stage 4: Runtime — 最小化正式映像檔 ──
FROM debian:bookworm-slim AS runtime
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
RUN groupadd --gid 1001 appuser && useradd --uid 1001 --gid appuser appuser
COPY --from=builder /app/target/release/order-service /usr/local/bin/
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD ["/usr/local/bin/order-service", "healthcheck"]
ENTRYPOINT ["/usr/local/bin/order-service"]
```

### GitHub Actions — Rust CI/CD Workflow

```yaml
# .github/workflows/rust-cicd.yml
name: Rust CI/CD
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
concurrency: { group: "rust-${{ github.ref }}", cancel-in-progress: true }
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/order-service

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with: { components: "rustfmt, clippy" }
      - uses: Swatinem/rust-cache@v2
        with: { cache-on-failure: true }
      - run: cargo fmt --all -- --check
      - run: cargo clippy --all-targets --all-features -- -D warnings
      - run: cargo test --lib --all-features
      - run: cargo test --test '*' --all-features
        env: { DATABASE_URL: "postgres://test:test@localhost:5432/test_db" }

  build-and-push:
    needs: lint-and-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: "${{ env.REGISTRY }}", username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}" }
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest
      - uses: docker/build-push-action@v6
        with: { context: ".", push: true, tags: "${{ steps.meta.outputs.tags }}", cache-from: "type=gha", cache-to: "type=gha,mode=max" }

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - run: kubectl set image deployment/order-service order-service=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} -n staging
      - run: kubectl rollout status deployment/order-service -n staging --timeout=300s
      - run: ./scripts/smoke-test.sh https://staging.example.com

  deploy-production:  # canary → full rollout
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production  # requires manual approval
    steps:
      - uses: actions/checkout@v4
      - run: kubectl set image deployment/order-service-canary order-service=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} -n production
      - run: ./scripts/canary-monitor.sh --duration=300 --max-error-rate=0.01
      - run: |
          kubectl set image deployment/order-service order-service=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} -n production
          kubectl rollout status deployment/order-service -n production --timeout=600s
```

---

## Go 實作

### Dockerfile — Multi-Stage with Distroless

```dockerfile
# ── Stage 1: Builder — 建置靜態二進位檔 ──
FROM golang:1.24-bookworm AS builder
WORKDIR /app

# 依賴 layer（go.mod/go.sum 沒變就用快取）
COPY go.mod go.sum ./
RUN go mod download && go mod verify

# 建置應用程式（純靜態連結）
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-s -w -X main.version=$(git describe --tags --always)" \
    -o /app/bin/payment-gateway ./cmd/payment-gateway

# ── Stage 2: Runtime — distroless 最小映像檔 ──
FROM gcr.io/distroless/static-debian12:nonroot AS runtime
COPY --from=builder /app/bin/payment-gateway /payment-gateway
EXPOSE 8080
USER nonroot:nonroot
ENTRYPOINT ["/payment-gateway"]
```

### GitHub Actions — Go CI/CD Workflow

```yaml
# .github/workflows/go-cicd.yml
name: Go CI/CD
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
concurrency: { group: "go-${{ github.ref }}", cancel-in-progress: true }
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/payment-gateway

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: "1.24", cache: true }
      - uses: golangci/golangci-lint-action@v6
        with: { version: latest }
      - name: Unit tests + coverage gate
        run: |
          go test -race -coverprofile=coverage.out -covermode=atomic ./...
          COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
          echo "Coverage: ${COVERAGE}%"
          (( $(echo "$COVERAGE < 80" | bc -l) )) && echo "Below 80% threshold" && exit 1 || true
      - run: go test -tags=integration -race -count=1 ./...
        env: { DATABASE_URL: "postgres://test:test@localhost:5432/test_db" }

  build-and-push:
    needs: lint-and-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write }
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }  # git tags for ldflags
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: "${{ env.REGISTRY }}", username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}" }
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest
      - uses: docker/build-push-action@v6
        with: { context: ".", push: true, tags: "${{ steps.meta.outputs.tags }}", cache-from: "type=gha", cache-to: "type=gha,mode=max" }

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - run: kubectl set image deployment/payment-gateway payment-gateway=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} -n staging
      - run: kubectl rollout status deployment/payment-gateway -n staging --timeout=300s
      - run: ./scripts/smoke-test.sh https://staging.example.com

  deploy-production:  # blue-green switch
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Blue-green switch
        run: |
          ACTIVE=$(kubectl get svc payment-gateway -n production -o jsonpath='{.spec.selector.slot}')
          INACTIVE=$([ "$ACTIVE" = "blue" ] && echo "green" || echo "blue")
          kubectl set image deployment/payment-gateway-${INACTIVE} \
            payment-gateway=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} -n production
          kubectl rollout status deployment/payment-gateway-${INACTIVE} -n production --timeout=600s
          kubectl patch svc payment-gateway -n production \
            -p "{\"spec\":{\"selector\":{\"slot\":\"${INACTIVE}\"}}}"
```

---

## Rust vs Go 對照表

| 面向 | Rust | Go |
|------|------|-----|
| **建置時間** | 首次 5-15 min，增量 30-90s。`cargo-chef` caching 降至 1-2 min | 首次 30s-2min，增量 5-15s。快取後 15-45s。編譯速度顯著優勢 |
| **映像檔大小** | `debian-slim` ~80MB + binary 5-20MB = **85-100 MB**。`alpine`+`musl` 可降至 ~20MB | `distroless/static` ~2MB + binary 8-15MB = **10-17 MB**。體積優勢明顯 |
| **CI 快取策略** | `Swatinem/rust-cache` 快取 `target/`（可達數 GB）+ `cargo-chef` 分離依賴層 | `setup-go` 內建 cache（< 500MB）+ `go mod download` 獨立層。管理簡單 |
| **靜態分析** | `cargo fmt` + `clippy`（內建，600+ lint 規則） | `golangci-lint`（100+ linter，需設定 `.golangci.yml`） |
| **跨平台建置** | `cross` 或 `--target`，需安裝對應 toolchain | `GOOS`+`GOARCH` 環境變數，原生交叉編譯，極簡單 |

---

## When to Use / 適用場景

- **多人協作的任何專案** — 只要團隊超過一人，CI 就是必要的。它確保每個人的程式碼在合併前經過相同的驗證，消除「他 push 的 code 弄壞了我的 feature」的情境。
- **需要可靠部署的 Production 服務** — 面對使用者的服務不容許手動部署的人為錯誤。自動化流水線確保每次部署都經過完整驗證。
- **高 SLA 要求的關鍵服務** — 99.9%+ 可用性要求零停機部署與秒級回滾。藍綠或金絲雀策略是必要的。
- **頻繁發佈的敏捷團隊** — 每天部署數次的團隊，若無 CI/CD 會被手動流程拖垮。自動化是高頻發佈的前提。

---

## When NOT to Use / 不適用場景

- **一次性腳本或原型** — 用完即丟的 script 不需要建置流水線。投入 CI/CD 的時間遠超手動執行。
- **早期 POC / 驗證階段** — 商業模式尚未驗證時，花時間建置完整 CI/CD 是過度工程。先用最簡單的方式部署（如 `fly deploy`），待產品方向確定後再投資。
- **無需部署的 Library / SDK** — 純函式庫需要 CI（測試、發佈），但不需要 CD（沒有 server 要部署）。CI 仍有價值，但部署階段不適用。
- **單人 side project 的初期** — 一個人寫的 weekend project，初期手動 `docker build && docker push` 即可。當程式碼穩定、開始有使用者時，再加入 CI/CD。

---

## Real-World Examples / 真實世界案例

### GitHub — Blue-Green Deployment
GitHub 自身使用藍綠部署，由 `chatops` 工具觸發流量切換，15 分鐘觀察窗口內任何工程師可一鍵 rollback。每天 30-50 次部署，commit-to-production 中位數約 10 分鐘。藍綠策略讓高頻部署下仍維持極高可用性。

### Netflix — Spinnaker Canary Analysis
Netflix 的 Spinnaker CD 平台內建 Automated Canary Analysis (ACA)。每次部署啟動 canary instance 與等量 baseline instance，Kayenta 引擎用統計方法比對 error rate、latency p50/p99、CPU。Canary score 低於閾值時自動回滾，日均數百次微服務部署中 production incident 極低。

### Argo CD — GitOps for Kubernetes
Intuit、Red Hat、Tesla 採用。Git repo 存放 K8s manifest，Argo CD controller 持續比對 repo 與 cluster 狀態，差異時自動同步。所有變更有 Git commit 審計、`git revert` 即 rollback、PR review 即 deployment review、杜絕 drift。

---

## Interview Questions / 面試常見問題

**Q1：Blue-Green 與 Canary 部署的差別？**
Blue-Green 兩套環境瞬間切換，適合原子性部署（DB schema 大改）。Canary 漸進式導入，適合高流量精細風控。Blue-Green 需雙倍資源但回滾秒級；Canary 僅 +5-10% 資源但需完善監控。

**Q2：如何設計安全的回滾機制？**
(1) **映像檔**：git SHA 作 image tag，回滾指定前版 SHA；(2) **資料庫**：migration 向前相容，加欄位在部署前、刪欄位在確認無舊版後；(3) **流程**：腳本內建 `--rollback`，5 分鐘內完成，不需新 build。

**Q3：CI 中如何處理 Database Migration？**
「先遷移、後部署」，migration 必須向前相容。(1) CI 跑 migration 至 staging 並測試新舊版相容；(2) Production 部署前跑 migration 加欄位；(3) 部署新版使用新欄位；(4) 確認無舊版 pod 後下個 release 刪舊欄位。

**Q4：如何確保 CI/CD pipeline 本身的安全性？**
(1) Secrets 用 GitHub Encrypted Secrets 或 Vault，不硬編碼；(2) 每個 job 最小權限（`contents: read`, `packages: write`）；(3) pin action 至 commit SHA 防供應鏈攻擊；(4) production environment 設 required reviewers；(5) Trivy/Grype 掃描映像檔漏洞。

**Q5：GitOps 與傳統 push-based CD 的差別？**
Push-based：CI 完成後 `kubectl apply` 推送至 cluster，CI 需 cluster credentials，可能 drift。GitOps (pull-based)：Argo CD 從 cluster 內拉取 Git repo 狀態同步，CI 不需 cluster credentials（職責分離），drift 自動修正。更安全、可審計、可 revert。

---

## Pitfalls / 常見陷阱

### 1. 部署程式碼同時執行破壞性 Migration

```yaml
# 危險：同一步驟刪除欄位並部署新程式碼
steps:
  - name: Run migration (DROP COLUMN old_status)
    run: migrate up
  - name: Deploy new version
    run: kubectl rollout restart deployment/order-service
# 舊版 pod 仍在運行，SELECT old_status → column not found → 500 error

# 正確：分三個 release 執行
# Release N:   migration 加新欄位 + 雙寫
# Release N+1: 讀取新欄位、停止讀舊欄位
# Release N+2: migration 刪除舊欄位（確認無舊版 pod）
```

### 2. 無回滾計畫就上線

```yaml
# 危險：部署完就結束，出問題不知道如何回滾
- run: kubectl set image deployment/app app=registry/app:${{ github.sha }}

# 正確：部署後驗證，失敗自動回滾
- run: kubectl set image deployment/app app=registry/app:${{ github.sha }}
- run: kubectl rollout status deployment/app --timeout=300s ||
       (kubectl rollout undo deployment/app && exit 1)
- run: ./scripts/smoke-test.sh || kubectl rollout undo deployment/app
```

### 3. Secret 洩漏至 Docker Image

```dockerfile
# 危險：ARG 殘留在 image layer，docker history 可見
ARG DATABASE_URL
RUN echo $DATABASE_URL > /tmp/debug.log

# 正確：secret 只在 runtime 注入（K8s Secret / env），不進入 image
```

### 4. CI 快取未設定

```yaml
# 危險：Rust 每次從零編譯所有 crate（10+ 分鐘）
- run: cargo test

# 正確：Swatinem/rust-cache 快取 target/ → 2-3 分鐘
- uses: Swatinem/rust-cache@v2
  with: { cache-on-failure: true }
- run: cargo test
```

### 5. 未鎖定 CI Action 版本

```yaml
# 危險：major tag 可被覆蓋，supply chain attack 風險
- uses: actions/checkout@v4

# 正確：pin 至 commit SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
```

---

## References / 參考資料

1. **GitHub Actions Documentation** — (https://docs.github.com/en/actions) workflow 語法、runner 規格、environment protection rules、reusable workflows。
2. **Docker — Best Practices for Writing Dockerfiles** — (https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) multi-stage build、layer caching、security scanning。
3. **Argo CD Documentation** — (https://argo-cd.readthedocs.io/) GitOps 原理、Application CRD、sync policy、rollback、multi-cluster。
4. **cargo-chef — Optimizing Rust Docker Builds** — (https://github.com/LukeMathWalker/cargo-chef) recipe 機制、layer caching 原理、與 BuildKit 整合。
5. **Google Distroless Images** — (https://github.com/GoogleContainerTools/distroless) 各語言 base image、nonroot variant、debug variant。
6. **Martin Fowler — Continuous Integration / Continuous Delivery** — (https://martinfowler.com/articles/continuousIntegration.html) CI/CD 的定義、原則與實踐。
7. **Netflix — Automated Canary Analysis at Netflix** — (https://netflixtechblog.com/automated-canary-analysis-at-netflix-with-kayenta-3260bc7acc69) Kayenta 統計分析引擎、canary score、自動回滾。
8. **Kubernetes — Deployment Strategies** — (https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy) rolling update、maxSurge、maxUnavailable、revision history。

---

## Cross-references / 交叉引用

- [[33_testing_strategy|Testing Strategy / 測試策略]](33_testing_strategy.md) — CI 流水線的核心是測試。本筆記的 `lint-and-test` job 依賴測試策略中定義的分層測試體系——unit test 跑在 CI 的前期（快速回饋），integration test 跑在建置映像檔之前（驗證元件互動）。測試策略決定「測什麼」，CI/CD 決定「何時、如何自動跑」。
- [[25_metrics_sli_slo_sla|Metrics & SLI/SLO/SLA]](../infrastructure/25_metrics_sli_slo_sla.md) — Canary 部署的核心判斷依據是 SLI（error rate、latency p99）。部署後的觀察窗口需要比對 canary 與 baseline 的 SLI，若 canary 的 error rate 超過 SLO 定義的 error budget，立即觸發回滾。沒有完善的 metrics 基礎設施，canary 部署就只是「盲目地部署到一部分 pod」。
