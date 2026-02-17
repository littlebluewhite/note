---
title: "Integration & Contract Testing / 整合與契約測試"
note_type: knowledge
domain: backend
category: engineering
tags: [backend, engineering, go, rust, integration-testing, contract-testing]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "34"
level: intermediate
review_interval_days: 14
next_review: 2026-03-03
---

# Integration & Contract Testing / 整合與契約測試

## Intent / 意圖

驗證多個元件組合後能正確協作，並確保服務間的 API 契約在獨立演進時保持穩定。整合測試回答的問題是「我的 SQL 查詢在真實資料庫上是否正確執行？」；契約測試回答的問題是「當 provider 變更 API 時，所有 consumer 是否仍然能正常運作？」兩者互補：整合測試驗證元件的垂直切面（handler → service → repository → DB），契約測試驗證服務的水平切面（consumer A ↔ provider ↔ consumer B）。

核心問題：**如何在不啟動整個分散式系統的前提下，確保元件互動正確、API 契約穩定，並在數秒內發現破壞性變更？**

---

## Problem / 問題情境

**場景一：Unit tests 全綠，但系統在整合點爆炸**

團隊的訂單服務有 95% 的 unit test 覆蓋率。所有 repository 方法都用 mock 測試過。部署到 staging 後，建立訂單的 API 回傳 500 Internal Server Error。原因：ORM 產生的 SQL 在 PostgreSQL 上觸發了型別轉換錯誤——`BIGINT` column 收到 `TEXT` 值。Unit test 中的 mock repository 跳過了真實的 SQL 執行，無法捕捉這類型別不匹配。團隊需要的是使用真實資料庫的整合測試。

**場景二：Provider 改了 API，Consumer 在 production 才發現**

支付團隊（provider）將 `/api/v1/payments` 的 response 欄位從 `payment_status: "completed"` 改為 `status: "COMPLETED"`（重新命名 + 大寫）。支付團隊的 unit test 全部通過，因為他們只測自己的 handler。訂單團隊（consumer）的 code 解析 `payment_status` 欄位，解析失敗時回傳 `null`。訂單服務沒有 crash，但所有訂單的付款狀態都顯示「未知」。直到客服接到投訴才發現問題。如果有 consumer-driven contract test，支付團隊在修改欄位名稱的 PR 階段就會收到紅燈。

**場景三：整合測試太慢，開發者跳過不跑**

整合測試直接連接共享的 staging database，每次測試前需要 seed 大量測試資料。測試互相污染——測試 A 建立的訂單影響測試 B 的查詢結果。測試執行時間 20 分鐘，且因為共享狀態而頻繁 flaky。開發者養成習慣：「整合測試在 CI 跑就好，本地不跑。」但 CI 排隊要 30 分鐘，一個 PR 的回饋週期超過 50 分鐘。團隊需要的是 testcontainers——每次測試 spin up 隔離的 Docker container，測試結束自動銷毀。

---

## Core Concepts / 核心概念

### Integration Test / 整合測試

測試多個元件的組合行為，使用真實的外部依賴（資料庫、message queue、cache）。與 unit test 的關鍵差異：整合測試不 mock 基礎設施層，而是驗證程式碼在真實環境中的行為。典型的整合測試覆蓋 handler → service → repository → 真實 DB 的完整 call chain。執行速度在秒級（含 container 啟動通常 5-15 秒），比 unit test 慢但比 E2E test 快一個數量級。

### Testcontainers / 測試容器

透過程式碼啟動 Docker container 作為測試依賴的函式庫。每個測試（或測試套件）擁有獨立的 container instance，確保完全隔離。支援 PostgreSQL、MySQL、Redis、Kafka、RabbitMQ 等常見基礎設施。Rust 用 `testcontainers-rs`，Go 用 `testcontainers-go`。Testcontainers 解決了整合測試的兩大痛點：(1) 環境不一致（每個人的本地 DB 版本不同）；(2) 測試互相污染（共享 DB 的殘留資料影響其他測試）。

### Test Database Setup & Teardown / 測試資料庫的建立與拆除

整合測試需要在每次測試前將資料庫還原到已知狀態。常見策略：(1) **Transaction rollback** — 每個測試在 transaction 中執行，結束時 rollback，速度最快但無法測試 commit 後觸發的 trigger/constraint；(2) **Truncate tables** — 每個測試結束後清空所有表，速度中等；(3) **Fresh database** — 每個測試 spin up 新的 container + 跑 migration，最隔離但最慢。最佳實踐：test suite 層級 spin up container + 跑 migration，每個測試用 transaction rollback 或 truncate。

### Contract Testing / 契約測試

驗證服務間的 API 契約（request 格式、response 結構、HTTP status code）是否被雙方遵守。不需要同時啟動 consumer 和 provider——各自獨立測試。**Consumer-Driven Contract Testing（CDCT）**：consumer 先定義期望（「我會送 `POST /orders`，期望收到 `201` 和 `{ id, status }`」），這些期望被打包為 contract file（pact file），provider 端驗證自己是否滿足所有 consumer 的期望。

### Pact Framework / Pact 框架

最廣泛使用的 CDCT 工具。Consumer 端使用 Pact DSL 定義期望的互動，Pact 產生 JSON 格式的 contract file。Contract file 上傳到 **Pact Broker**（中央儲存庫）。Provider 端從 Broker 下載所有 consumer 的 contract，逐一 replay 並驗證回應是否符合期望。Pact 支援 HTTP、gRPC、GraphQL、message queue 等協定。Rust 用 `pact-consumer` / `pact-verifier`，Go 用 `pact-go`。

### Provider Verification / Provider 驗證

Provider 端的 contract test。Provider 啟動真實的 HTTP server（或使用真實的 handler），Pact framework 將 consumer 定義的 request 逐一送出，比對 response 是否符合 contract 中的期望（status code、header、body 結構）。如果 provider 修改了 response schema，verification 會立即失敗，在 CI 階段阻止破壞性變更進入 main branch。

### Schema Compatibility / Schema 相容性

API schema 演進時需要遵守的相容性規則。(1) **Backward compatible（向後相容）** — 新版 consumer 能處理舊版 provider 的 response。實踐：新增欄位可以，刪除/重命名欄位不行。(2) **Forward compatible（向前相容）** — 舊版 consumer 能處理新版 provider 的 response。實踐：consumer 忽略不認識的欄位。(3) **Full compatible** — 同時向後和向前相容。JSON API 天然支援 forward compatibility（忽略未知欄位），Protobuf 透過欄位編號保證 backward compatibility。

### API Compatibility Testing / API 相容性測試

超越 contract testing 的範疇，驗證 API 的語義行為是否一致。Contract test 只驗證「response 結構是否正確」，API compatibility test 還驗證「given 相同的 input，response 的值是否在預期範圍內」。工具：OpenAPI diff（比對 schema 差異）、Dredd（將 OpenAPI spec 當作 test case 執行）、Schemathesis（自動產生基於 schema 的 property-based test）。

### Test Fixtures vs Factories / 測試固件 vs 工廠

兩種產生測試資料的方式。**Fixture** — 預定義的靜態資料（JSON file、SQL seed script），每次測試載入相同的資料集。優點：可預測；缺點：隨著 schema 演進需要同步更新所有 fixture。**Factory** — 程式化產生測試資料的函式，每次呼叫產生不同的 instance，使用 builder pattern 允許覆寫特定欄位。優點：靈活、不易過時；缺點：需要維護 factory 程式碼。最佳實踐：integration test 用 factory（靈活應對 schema 變更），contract test 用 fixture（契約本身需要穩定）。

---

## Architecture / 架構

### Consumer-Driven Contract Testing 流程

```mermaid
sequenceDiagram
    participant Consumer as Consumer Service
    participant Pact as Pact Mock Server
    participant Broker as Pact Broker
    participant Provider as Provider Service
    participant ProviderDB as Provider Database

    Note over Consumer,Pact: Phase 1: Consumer Side (CI of Consumer)
    Consumer->>Pact: Define expected interactions<br/>(request + expected response)
    Pact-->>Consumer: Mock response matching expectations
    Consumer->>Consumer: Run consumer tests<br/>against mock server
    Consumer->>Broker: Publish pact file<br/>(contract JSON)

    Note over Broker,ProviderDB: Phase 2: Provider Side (CI of Provider)
    Broker-->>Provider: Download all consumer pacts
    loop For each consumer pact
        Provider->>Provider: Start real handler<br/>(or lightweight server)
        Provider->>ProviderDB: Execute real queries<br/>(test database)
        Provider-->>Broker: Report verification result<br/>(pass / fail per interaction)
    end

    Note over Broker: Phase 3: Deployment Gate
    Broker->>Broker: can-i-deploy check<br/>(all contracts verified?)
    Broker-->>Consumer: Safe to deploy? YES / NO
    Broker-->>Provider: Safe to deploy? YES / NO
```

### 整合測試與 Testcontainers 架構

```mermaid
flowchart TB
    subgraph TestSuite["Test Suite Lifecycle"]
        direction TB
        Setup["Suite Setup<br/>1. Start PostgreSQL container<br/>2. Run migrations<br/>3. Get connection pool"]
        Tests["Individual Tests<br/>Each test: BEGIN TX → test logic → ROLLBACK"]
        Teardown["Suite Teardown<br/>1. Drop connection pool<br/>2. Stop & remove container"]
        Setup --> Tests --> Teardown
    end

    subgraph Container["Docker Container (ephemeral)"]
        PG["PostgreSQL 16<br/>Random port mapping<br/>Isolated data volume"]
    end

    Tests -->|"sqlx::PgPool / pgxpool.Pool"| PG

    style TestSuite fill:#e3f2fd,stroke:#1565c0
    style Container fill:#fff3e0,stroke:#e65100
    style PG fill:#fff9c4,stroke:#f9a825,color:#000
```

---

## How It Works / 運作原理

### Testcontainers 生命週期

1. **Container 啟動**：測試框架呼叫 testcontainers API，指定 image（`postgres:16-alpine`）、環境變數（`POSTGRES_PASSWORD`）、exposed port。Testcontainers 透過 Docker API 拉取 image（首次需下載，後續使用 cache）、建立 container、等待 readiness probe（TCP port 可連線 + 自定義 health check）。啟動時間通常 2-5 秒。

2. **Port 映射**：Container 內部的 port（如 5432）被映射到 host 的隨機 port（如 55432）。測試程式碼透過 testcontainers API 取得 mapped port，組裝 connection string。隨機 port 確保多個測試套件可以平行執行不衝突。

3. **Database 初始化**：取得連線後執行 migration（Rust 用 `sqlx migrate`，Go 用 `golang-migrate` 或 `goose`）。Migration 建立所有表和索引。可選：用 factory 函式 seed 必要的參考資料（如 enum table、default config）。

4. **測試執行**：每個測試函式開始時建立 transaction，測試邏輯在 transaction 內執行所有 DB 操作。測試結束時 rollback transaction，確保不同測試之間零污染。如果測試需要驗證 commit 後的行為（trigger、constraint），改用 truncate 策略。

5. **Container 銷毀**：所有測試執行完畢後，testcontainers 自動 stop 並 remove container。即使測試 panic 或 process crash，testcontainers 的 Ryuk sidecar container 會在逾時後自動清理孤兒 container。

### Pact Consumer-Driven 流程

1. **Consumer 定義期望**：Consumer 端的測試使用 Pact DSL 定義「我會送什麼 request，期望收到什麼 response」。Pact 啟動一個 mock server，當 consumer 的 code 對 mock server 發送 request 時，mock server 驗證 request 是否符合期望，並回傳預定義的 response。

2. **產生 Pact File**：如果 consumer test 通過（所有 interaction 都被觸發且 request 格式正確），Pact 產生一個 JSON 檔案（pact file），記錄所有 interaction 的完整 request/response pair。

3. **上傳到 Pact Broker**：Consumer 的 CI pipeline 將 pact file 上傳到 Pact Broker，標註 consumer 的版本號和 branch。Pact Broker 是 contract 的中央真相來源。

4. **Provider 驗證**：Provider 的 CI pipeline 從 Broker 下載所有 consumer 的 pact file。Provider 啟動真實的 HTTP handler（搭配 test database），Pact framework 逐一 replay consumer 定義的 request，比對 provider 的 actual response 與 pact 中的 expected response。

5. **Verification 結果**：Provider 將驗證結果回報給 Broker。如果 verification 失敗（response 不符合某個 consumer 的期望），Provider 的 CI 紅燈。Broker 的 `can-i-deploy` 命令在部署前檢查所有相關的 contract 是否都被驗證通過。

6. **Webhook 通知**：Pact Broker 可以設定 webhook——當 consumer 發佈新的 pact 時，自動觸發 provider 的 CI pipeline 執行 verification。這確保 provider 即時得知 consumer 的期望變更。

---

## Rust 實作

### 整合測試 — sqlx + testcontainers-rs 操作真實 PostgreSQL

```rust
// tests/user_repository_integration.rs
// 使用 testcontainers-rs 啟動 PostgreSQL container，驗證 repository 的 SQL 查詢

use sqlx::{PgPool, Row, postgres::PgPoolOptions};
use testcontainers::{
    core::{IntoContainerPort, WaitFor},
    runners::AsyncRunner,
    GenericImage, ImageExt,
};
use uuid::Uuid;

// ─── Domain ───

#[derive(Debug, Clone, PartialEq)]
struct User {
    id: Uuid,
    email: String,
    display_name: String,
    tier: String,
}

// ─── Repository ───

struct UserRepository {
    pool: PgPool,
}

impl UserRepository {
    fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    async fn create(&self, user: &User) -> Result<(), sqlx::Error> {
        sqlx::query(
            "INSERT INTO users (id, email, display_name, tier) VALUES ($1, $2, $3, $4)"
        )
        .bind(&user.id)
        .bind(&user.email)
        .bind(&user.display_name)
        .bind(&user.tier)
        .execute(&self.pool)
        .await?;
        Ok(())
    }

    async fn find_by_email(&self, email: &str) -> Result<Option<User>, sqlx::Error> {
        let row = sqlx::query(
            "SELECT id, email, display_name, tier FROM users WHERE email = $1"
        )
        .bind(email)
        .fetch_optional(&self.pool)
        .await?;

        Ok(row.map(|r| User {
            id: r.get("id"),
            email: r.get("email"),
            display_name: r.get("display_name"),
            tier: r.get("tier"),
        }))
    }

    async fn find_by_tier(&self, tier: &str) -> Result<Vec<User>, sqlx::Error> {
        let rows = sqlx::query(
            "SELECT id, email, display_name, tier FROM users WHERE tier = $1 ORDER BY email"
        )
        .bind(tier)
        .fetch_all(&self.pool)
        .await?;

        Ok(rows.iter().map(|r| User {
            id: r.get("id"),
            email: r.get("email"),
            display_name: r.get("display_name"),
            tier: r.get("tier"),
        }).collect())
    }
}

// ─── Test Helpers ───

async fn start_postgres_container() -> (testcontainers::ContainerAsync<GenericImage>, String) {
    let container = GenericImage::new("postgres", "16-alpine")
        .with_env_var("POSTGRES_USER", "testuser")
        .with_env_var("POSTGRES_PASSWORD", "testpass")
        .with_env_var("POSTGRES_DB", "testdb")
        .with_exposed_port(5432.tcp())
        .with_wait_for(WaitFor::message_on_stderr("ready to accept connections"))
        .start()
        .await
        .expect("Failed to start PostgreSQL container");

    let host_port = container
        .get_host_port_ipv4(5432)
        .await
        .expect("Failed to get mapped port");

    let connection_string = format!(
        "postgres://testuser:testpass@127.0.0.1:{}/testdb",
        host_port
    );

    (container, connection_string)
}

async fn run_migrations(pool: &PgPool) {
    sqlx::query(
        "CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            tier TEXT NOT NULL DEFAULT 'standard',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )"
    )
    .execute(pool)
    .await
    .expect("Failed to create users table");
}

fn build_user(email: &str, display_name: &str, tier: &str) -> User {
    User {
        id: Uuid::new_v4(),
        email: email.to_string(),
        display_name: display_name.to_string(),
        tier: tier.to_string(),
    }
}

// ─── Integration Tests ───

#[tokio::test]
async fn create_and_find_user_by_email() {
    let (_container, conn_str) = start_postgres_container().await;
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&conn_str)
        .await
        .expect("Failed to connect");

    run_migrations(&pool).await;
    let repo = UserRepository::new(pool);

    let user = build_user("alice@example.com", "Alice Chen", "gold");
    repo.create(&user).await.expect("Failed to create user");

    let found = repo
        .find_by_email("alice@example.com")
        .await
        .expect("Query failed")
        .expect("User not found");

    assert_eq!(found.email, "alice@example.com");
    assert_eq!(found.display_name, "Alice Chen");
    assert_eq!(found.tier, "gold");
    // _container dropped here → PostgreSQL container stops and is removed
}

#[tokio::test]
async fn find_by_email_returns_none_for_nonexistent_user() {
    let (_container, conn_str) = start_postgres_container().await;
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&conn_str)
        .await
        .expect("Failed to connect");

    run_migrations(&pool).await;
    let repo = UserRepository::new(pool);

    let result = repo
        .find_by_email("nobody@example.com")
        .await
        .expect("Query failed");

    assert!(result.is_none());
}

#[tokio::test]
async fn find_by_tier_returns_matching_users_sorted_by_email() {
    let (_container, conn_str) = start_postgres_container().await;
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&conn_str)
        .await
        .expect("Failed to connect");

    run_migrations(&pool).await;
    let repo = UserRepository::new(pool);

    let gold_user_a = build_user("bob@example.com", "Bob Wang", "gold");
    let gold_user_b = build_user("alice@example.com", "Alice Chen", "gold");
    let silver_user = build_user("carol@example.com", "Carol Liu", "silver");

    repo.create(&gold_user_a).await.unwrap();
    repo.create(&gold_user_b).await.unwrap();
    repo.create(&silver_user).await.unwrap();

    let gold_users = repo.find_by_tier("gold").await.expect("Query failed");

    assert_eq!(gold_users.len(), 2);
    assert_eq!(gold_users[0].email, "alice@example.com"); // sorted by email
    assert_eq!(gold_users[1].email, "bob@example.com");
}

#[tokio::test]
async fn duplicate_email_returns_unique_constraint_error() {
    let (_container, conn_str) = start_postgres_container().await;
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&conn_str)
        .await
        .expect("Failed to connect");

    run_migrations(&pool).await;
    let repo = UserRepository::new(pool);

    let user = build_user("dup@example.com", "First User", "standard");
    repo.create(&user).await.expect("Failed to create first user");

    let duplicate = build_user("dup@example.com", "Second User", "gold");
    let err = repo.create(&duplicate).await.unwrap_err();

    // Verify PostgreSQL returns a unique violation error
    let db_err = err.as_database_error().expect("Expected database error");
    assert_eq!(db_err.code().unwrap(), "23505"); // unique_violation
}

// Output:
// running 4 tests
// test create_and_find_user_by_email ... ok (3.2s)
// test find_by_email_returns_none_for_nonexistent_user ... ok (2.8s)
// test find_by_tier_returns_matching_users_sorted_by_email ... ok (3.1s)
// test duplicate_email_returns_unique_constraint_error ... ok (2.9s)
// test result: ok. 4 passed; 0 failed
```

---

## Go 實作

### 整合測試 — testcontainers-go 操作真實 PostgreSQL

```go
// user_repository_integration_test.go
// 使用 testcontainers-go 啟動 PostgreSQL container，驗證 repository 的 SQL 查詢

package repository_test

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

// ─── Domain ───

type User struct {
	ID          string
	Email       string
	DisplayName string
	Tier        string
}

// ─── Repository ───

type UserRepository struct {
	pool *pgxpool.Pool
}

func NewUserRepository(pool *pgxpool.Pool) *UserRepository {
	return &UserRepository{pool: pool}
}

func (r *UserRepository) Create(ctx context.Context, user *User) error {
	_, err := r.pool.Exec(ctx,
		"INSERT INTO users (id, email, display_name, tier) VALUES ($1, $2, $3, $4)",
		user.ID, user.Email, user.DisplayName, user.Tier,
	)
	return err
}

func (r *UserRepository) FindByEmail(ctx context.Context, email string) (*User, error) {
	row := r.pool.QueryRow(ctx,
		"SELECT id, email, display_name, tier FROM users WHERE email = $1",
		email,
	)
	var user User
	err := row.Scan(&user.ID, &user.Email, &user.DisplayName, &user.Tier)
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (r *UserRepository) FindByTier(ctx context.Context, tier string) ([]User, error) {
	rows, err := r.pool.Query(ctx,
		"SELECT id, email, display_name, tier FROM users WHERE tier = $1 ORDER BY email",
		tier,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var users []User
	for rows.Next() {
		var u User
		if err := rows.Scan(&u.ID, &u.Email, &u.DisplayName, &u.Tier); err != nil {
			return nil, err
		}
		users = append(users, u)
	}
	return users, rows.Err()
}

// ─── Test Helpers ───

type postgresContainer struct {
	container testcontainers.Container
	connStr   string
}

func startPostgresContainer(t *testing.T) *postgresContainer {
	t.Helper()
	ctx := context.Background()

	req := testcontainers.ContainerRequest{
		Image:        "postgres:16-alpine",
		ExposedPorts: []string{"5432/tcp"},
		Env: map[string]string{
			"POSTGRES_USER":     "testuser",
			"POSTGRES_PASSWORD": "testpass",
			"POSTGRES_DB":       "testdb",
		},
		WaitingFor: wait.ForLog("database system is ready to accept connections").
			WithOccurrence(2).
			WithStartupTimeout(30 * time.Second),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		t.Fatalf("failed to start postgres container: %v", err)
	}

	host, err := container.Host(ctx)
	if err != nil {
		t.Fatalf("failed to get container host: %v", err)
	}

	mappedPort, err := container.MappedPort(ctx, "5432")
	if err != nil {
		t.Fatalf("failed to get mapped port: %v", err)
	}

	connStr := fmt.Sprintf("postgres://testuser:testpass@%s:%s/testdb?sslmode=disable",
		host, mappedPort.Port())

	t.Cleanup(func() {
		if err := container.Terminate(ctx); err != nil {
			t.Logf("failed to terminate container: %v", err)
		}
	})

	return &postgresContainer{container: container, connStr: connStr}
}

func setupPool(t *testing.T, connStr string) *pgxpool.Pool {
	t.Helper()
	ctx := context.Background()

	pool, err := pgxpool.New(ctx, connStr)
	if err != nil {
		t.Fatalf("failed to create pool: %v", err)
	}
	t.Cleanup(pool.Close)

	// Run migration
	_, err = pool.Exec(ctx, `
		CREATE TABLE IF NOT EXISTS users (
			id TEXT PRIMARY KEY,
			email TEXT UNIQUE NOT NULL,
			display_name TEXT NOT NULL,
			tier TEXT NOT NULL DEFAULT 'standard',
			created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
		)
	`)
	if err != nil {
		t.Fatalf("failed to run migration: %v", err)
	}

	return pool
}

func buildUser(email, displayName, tier string) *User {
	return &User{
		ID:          uuid.New().String(),
		Email:       email,
		DisplayName: displayName,
		Tier:        tier,
	}
}

// ─── Integration Tests ───

func TestCreateAndFindUserByEmail(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	pg := startPostgresContainer(t)
	pool := setupPool(t, pg.connStr)
	repo := NewUserRepository(pool)
	ctx := context.Background()

	user := buildUser("alice@example.com", "Alice Chen", "gold")
	if err := repo.Create(ctx, user); err != nil {
		t.Fatalf("failed to create user: %v", err)
	}

	found, err := repo.FindByEmail(ctx, "alice@example.com")
	if err != nil {
		t.Fatalf("failed to find user: %v", err)
	}

	if found.Email != "alice@example.com" {
		t.Errorf("want email alice@example.com, got %s", found.Email)
	}
	if found.DisplayName != "Alice Chen" {
		t.Errorf("want display name Alice Chen, got %s", found.DisplayName)
	}
	if found.Tier != "gold" {
		t.Errorf("want tier gold, got %s", found.Tier)
	}
}

func TestFindByEmailReturnsErrorForNonexistentUser(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	pg := startPostgresContainer(t)
	pool := setupPool(t, pg.connStr)
	repo := NewUserRepository(pool)
	ctx := context.Background()

	_, err := repo.FindByEmail(ctx, "nobody@example.com")
	if err == nil {
		t.Fatal("expected error for nonexistent user, got nil")
	}
}

func TestFindByTierReturnsMatchingUsersSortedByEmail(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	pg := startPostgresContainer(t)
	pool := setupPool(t, pg.connStr)
	repo := NewUserRepository(pool)
	ctx := context.Background()

	goldUserA := buildUser("bob@example.com", "Bob Wang", "gold")
	goldUserB := buildUser("alice@example.com", "Alice Chen", "gold")
	silverUser := buildUser("carol@example.com", "Carol Liu", "silver")

	for _, u := range []*User{goldUserA, goldUserB, silverUser} {
		if err := repo.Create(ctx, u); err != nil {
			t.Fatalf("failed to create user %s: %v", u.Email, err)
		}
	}

	goldUsers, err := repo.FindByTier(ctx, "gold")
	if err != nil {
		t.Fatalf("failed to find by tier: %v", err)
	}

	if len(goldUsers) != 2 {
		t.Fatalf("want 2 gold users, got %d", len(goldUsers))
	}
	if goldUsers[0].Email != "alice@example.com" {
		t.Errorf("want first user alice@example.com, got %s", goldUsers[0].Email)
	}
	if goldUsers[1].Email != "bob@example.com" {
		t.Errorf("want second user bob@example.com, got %s", goldUsers[1].Email)
	}
}

func TestDuplicateEmailReturnsError(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	pg := startPostgresContainer(t)
	pool := setupPool(t, pg.connStr)
	repo := NewUserRepository(pool)
	ctx := context.Background()

	user := buildUser("dup@example.com", "First User", "standard")
	if err := repo.Create(ctx, user); err != nil {
		t.Fatalf("failed to create first user: %v", err)
	}

	duplicate := buildUser("dup@example.com", "Second User", "gold")
	err := repo.Create(ctx, duplicate)
	if err == nil {
		t.Fatal("expected unique constraint error, got nil")
	}
}

// Output:
// === RUN   TestCreateAndFindUserByEmail
// --- PASS: TestCreateAndFindUserByEmail (4.12s)
// === RUN   TestFindByEmailReturnsErrorForNonexistentUser
// --- PASS: TestFindByEmailReturnsErrorForNonexistentUser (3.56s)
// === RUN   TestFindByTierReturnsMatchingUsersSortedByEmail
// --- PASS: TestFindByTierReturnsMatchingUsersSortedByEmail (3.89s)
// === RUN   TestDuplicateEmailReturnsError
// --- PASS: TestDuplicateEmailReturnsError (3.71s)
// PASS
// ok  	repository	15.28s
```

---

## Rust vs Go 對照表

| 面向 | Rust | Go |
|---|---|---|
| **Testcontainers 生態** | `testcontainers` crate 提供 async API（`runners::AsyncRunner`）。需要手動指定 image + wait condition。社群提供常見 image 的 module（`testcontainers-modules` 的 `postgres`、`redis`）。Container 的生命週期與 Rust ownership 綁定——container 變數 drop 時自動 stop，符合 RAII 慣例 | `testcontainers-go` 提供 `GenericContainer` 和針對常見服務的 module（`postgres.RunContainer`）。使用 `t.Cleanup` 註冊 teardown 函式。社群活躍，module 覆蓋度高。`wait.ForLog` / `wait.ForListeningPort` 等 strategy 開箱即用，設定更直覺 |
| **Database Driver 整合** | `sqlx` 是主流——compile-time checked queries（`sqlx::query!` macro 在編譯期驗證 SQL 語法和型別對應）。搭配 testcontainers 時，需先啟動 container 再建立 `PgPool`。`sqlx` 的 `migrate!` macro 可自動執行 migration。型別安全強制消除了「欄位型別不匹配」的整合問題 | `pgx` (v5) 是 PostgreSQL 的主流 driver，`database/sql` + `lib/pq` 是通用介面。`pgxpool.Pool` 支援 connection pooling。Migration 通常用 `golang-migrate` 或 `goose`。Go 的 interface 讓 repository 層容易替換 driver，但缺乏 compile-time SQL 驗證 |
| **Contract Testing 支援** | `pact_consumer` / `pact_verifier` crate 基於 Pact FFI（C 底層綁定）。設定較為冗長，需要手動建構 interaction。Rust 生態的 contract testing 工具成熟度較低，部分團隊改用 OpenAPI schema validation + `schemars` 產生 JSON Schema 做靜態驗證 | `pact-go` 是 Pact Foundation 官方維護的 Go binding，API 設計貼合 Go 慣例。搭配 `testing` package 使用，provider verification 可直接指向 `httptest.Server`。社群文件豐富，與 CI 整合的範例多。Go 在 contract testing 生態上明顯領先 Rust |
| **測試隔離策略** | `sqlx` 支援在測試中取得 transaction handle，測試結束 drop handle 時自動 rollback。`#[sqlx::test]` attribute macro 可自動建立 test database + 跑 migration + 注入 `PgPool`，極度方便。每個 `#[sqlx::test]` 都是完全隔離的 database | Go 常用 `t.Cleanup` 搭配 transaction rollback。也可用 `testcontainers` 每個 test function spin up 獨立 container（如本文範例）。`TestMain` 可用於 suite-level setup，但缺乏 Rust `#[sqlx::test]` 那樣的 zero-config 隔離體驗 |

---

## When to Use / 適用場景

### 1. Repository 層的 SQL 查詢驗證

Unit test 用 mock repository 只驗證 service 層的邏輯，無法驗證 SQL 語法、JOIN 條件、WHERE 子句、index 使用是否正確。當 repository 包含複雜的 SQL（多表 JOIN、子查詢、window function、JSONB 操作）時，必須用 testcontainers 搭配真實資料庫執行整合測試。特別是 ORM 產生的 SQL——你不知道 ORM 在特定 edge case 會產生什麼查詢，只有真實 DB 能驗證。

### 2. 多團隊微服務架構的 API 契約保護

當 3 個以上的團隊各自維護微服務，且服務間透過 HTTP/gRPC 通信時，contract testing 是防止破壞性變更的最有效手段。場景：Payment Service 有 5 個 consumer（Order、Invoice、Refund、Analytics、Notification）。沒有 contract test，Payment 團隊修改 response schema 時需要手動通知 5 個團隊並等待各自確認——這在實務上不可能落實。有了 Pact，Payment 團隊在 CI 階段就能看到「此變更會 break Order Service 和 Invoice Service 的 contract」。

### 3. 資料庫 migration 的正確性驗證

每次新增 migration 時（加欄位、改型別、加 constraint），整合測試驗證 migration 後的 schema 是否與 application code 的 query 相容。場景：migration 將 `price` 欄位從 `INTEGER`（分為單位）改為 `NUMERIC(10,2)`（元為單位）。如果 application code 仍然將查詢結果當作 `i32` 處理，整合測試會在 CI 階段捕捉到型別不匹配。

---

## When NOT to Use / 不適用場景

### 1. 純邏輯的商業規則計算

折扣計算、權限判斷、狀態機轉換等不涉及 I/O 的純函式，用 unit test 驗證效率高出 1000 倍。整合測試啟動 container 需要 3-5 秒，unit test 在 1 毫秒內完成。對這類邏輯使用整合測試是殺雞用牛刀——增加 CI 時間，降低開發者回饋速度，且不提供額外的驗證價值。

### 2. 團隊內部的 service-to-service 溝通

如果兩個服務由同一個團隊維護、同一個 repo（monorepo）、一起部署，contract testing 的價值大幅降低。Contract testing 解決的核心問題是「獨立團隊獨立部署時的契約斷裂」。同一團隊可以用整合測試（啟動兩個服務跑 E2E）或 code review 來確保一致性。引入 Pact Broker 的維運成本不值得。

### 3. 頻繁變動的早期原型 API

當 API 還在快速迭代、每週 schema 都在大改時，contract test 會頻繁 break，開發者花更多時間更新 pact file 而非寫功能。Contract testing 適合 API 進入穩定期後引入——當 schema 變更頻率從「每週」降到「每月」時。早期原型階段用 OpenAPI schema validation 搭配 linter（Spectral）就足夠了。

---

## Real-World Examples / 真實世界案例

### Pact Foundation 的實踐

Pact 是 consumer-driven contract testing 的開源標準，由 REA Group（澳洲最大房產平台）於 2013 年內部開發，2014 年開源。截至 2025 年，Pact 支援 15+ 種程式語言，被 Atlassian、ING Bank、Accenture、Sainsbury's 等企業採用。Pact 的核心設計哲學：(1) **Consumer-driven** — 契約由 consumer 定義，因為 consumer 最清楚自己需要什麼；(2) **分散式驗證** — consumer 和 provider 各自在自己的 CI pipeline 驗證，不需要同時啟動；(3) **Pact Broker as Source of Truth** — 所有 contract 和 verification 結果集中管理，`can-i-deploy` 命令在部署前檢查安全性。ING Bank 的案例：1000+ 微服務，全面採用 Pact，每天產生 5000+ contract verification，將跨服務的整合 bug 減少了 80%。

### Spring Cloud Contract

Spring 生態的 contract testing 方案，採用 **provider-driven** 模式（與 Pact 的 consumer-driven 相反）。Provider 使用 Groovy DSL 定義契約，Spring Cloud Contract 自動產生 (1) provider 端的 integration test；(2) consumer 端的 WireMock stub。這種模式適合 provider 主導 API 設計的場景。Netflix 和 Pivotal 是早期採用者。Spring Cloud Contract 與 Spring Boot 深度整合——`@AutoConfigureStubRunner` annotation 自動下載並啟動 stub server，consumer 測試只需指向 stub。缺點：僅支援 JVM 生態系，跨語言團隊需要搭配 Pact 使用。

### Testcontainers 的普及

Testcontainers 最初是 Java 生態的函式庫（2015），現已擴展到 Go、Rust、.NET、Python、Node.js。Docker 公司於 2023 年收購 AtomicJar（Testcontainers 背後的公司），將 Testcontainers 納入 Docker 官方生態。這意味著 testcontainers 成為整合測試的事實標準。Spotify 在 2024 年分享的經驗：全面從共享 staging database 遷移到 testcontainers 後，整合測試的 flaky rate 從 12% 降到 0.5%，CI 時間反而減少 40%（因為不再等待共享資源的 lock）。

---

## Interview Questions / 面試常見問題

### Q1: Integration test 和 unit test 的根本差異是什麼？何時該選擇哪一種？

**A:** 根本差異在於 dependency boundary。Unit test 在被測程式碼的邊界處切斷所有外部依賴（用 mock/stub/fake 替代），只驗證該 unit 的邏輯。Integration test 跨越依賴邊界，使用真實的外部系統（DB、cache、queue）驗證元件間的互動行為。選擇原則：純邏輯（計算、驗證、轉換）用 unit test；涉及 I/O 且 I/O 行為本身是測試重點（SQL 查詢是否正確、message 是否能正確序列化到 Kafka）用 integration test。常見錯誤是用 integration test 覆蓋所有 case，導致 CI 極慢。正確做法：unit test 覆蓋所有 edge case 和分支邏輯，integration test 只覆蓋「happy path + 幾個 infrastructure-specific 的 failure mode」。

### Q2: 解釋 Consumer-Driven Contract Testing 的流程，以及它解決什麼問題。

**A:** CDCT 解決的核心問題是：在微服務獨立部署的架構中，provider 的 API 變更可能 silently break 所有 consumer。流程：(1) Consumer 端使用 Pact DSL 定義「我期望送出什麼 request，收到什麼 response」，Pact 產生 contract file（JSON）；(2) Contract file 上傳到 Pact Broker；(3) Provider 端從 Broker 下載所有 consumer 的 contract，啟動真實 handler，逐一 replay request 並驗證 response 是否符合 contract；(4) Verification 結果回報 Broker，`can-i-deploy` 命令檢查是否所有 contract 都被驗證通過。優勢：各服務獨立測試、不需要同時啟動整個系統、回饋速度快（秒級）、能精確指出「哪個 consumer 的哪個期望被 break」。

### Q3: Testcontainers 如何確保測試隔離？跟共享 staging DB 相比有何優勢？

**A:** Testcontainers 為每個 test suite（或每個 test function，取決於設定）啟動獨立的 Docker container。每個 container 有自己的 data volume、自己的 port mapping，容器間完全隔離。與共享 staging DB 相比：(1) **零污染** — 測試 A 的資料不會影響測試 B，因為跑在不同的 container 或不同的 transaction；(2) **版本一致** — 所有人用相同的 container image，不會出現「你本地跑 PG 15 但 CI 跑 PG 14」的問題；(3) **平行安全** — 多個 CI job 同時跑，各自的 container 互不干擾，不需要搶 lock；(4) **自動清理** — 測試結束 container 自動銷毀，即使 crash 也有 Ryuk sidecar 兜底。代價是啟動 container 需要 2-5 秒，但比共享 DB 的 flaky test debug 時間節省多個數量級。

### Q4: Schema compatibility 有哪些類型？在 API 版本演進中如何確保不 break consumer？

**A:** 三種相容性：(1) **Backward compatible** — 新版 provider 仍能被舊版 consumer 使用。規則：可以新增欄位，不可以刪除或重命名欄位，不可以改變欄位型別。(2) **Forward compatible** — 舊版 provider 的 response 能被新版 consumer 處理。規則：consumer 必須忽略不認識的欄位（JSON 天然支援，Protobuf 透過欄位編號支援）。(3) **Full compatible** — 同時滿足 backward 和 forward。確保不 break consumer 的實踐：(a) API versioning（`/v1/`, `/v2/`），重大變更走新版本；(b) Pact contract test 在 provider 的 CI 驗證所有 consumer 的期望；(c) Deprecation policy——宣佈棄用後維持 N 個月，給 consumer 遷移時間；(d) OpenAPI diff 工具（如 `oasdiff`）在 PR 階段自動比對 schema 變更，標記 breaking change。

### Q5: 如果整合測試在 CI 頻繁失敗但在本地通過，你會如何排查？

**A:** 系統性排查步驟：(1) **資源差異** — CI machine 的 CPU/memory 可能不足以及時 spin up container，調高 testcontainers 的 startup timeout。(2) **Docker 環境** — 確認 CI 的 Docker daemon 版本、磁碟空間（image pull 需要空間）、network mode（某些 CI 禁止 host network）。(3) **Port 衝突** — 檢查是否 hardcode 了 port（應使用 random port mapping）。(4) **共享狀態** — 即使用了 testcontainers，也可能因為 test 之間未正確 rollback/truncate 而殘留資料。檢查 test 執行順序是否影響結果（`go test -count=1 -shuffle=on` 或 Rust 的 `cargo test -- --test-threads=1`）。(5) **時間相依** — CI 的時鐘可能與本地不同步，或 sleep-based assertion 在高負載下失敗。(6) **Docker image cache** — 首次執行需要 pull image，可能超過 timeout。在 CI 設定 image pre-pull 步驟或使用 Docker layer caching。

---

## Pitfalls / 常見陷阱

### 1. 在整合測試中 Mock 掉你真正要測的東西

整合測試的價值在於驗證真實元件的互動。如果你在 repository 的整合測試中 mock 了資料庫，那這個測試就退化成了 unit test——無法驗證 SQL 語法、constraint、index 行為。常見的錯誤模式：「我們有整合測試」但實際上所有外部依賴都被 mock，測試只驗證了 glue code 的 happy path。

```rust
// 反面範例：整合測試 mock 了 DB，失去驗證 SQL 的價值
#[tokio::test]
async fn integration_test_with_mock_db() {
    let mock_pool = MockPgPool::new(); // 不是真實 DB
    mock_pool.expect_query().returning(|_| Ok(vec![mock_row()]));
    let repo = UserRepository::new(mock_pool);

    let user = repo.find_by_email("alice@example.com").await.unwrap();
    assert_eq!(user.email, "alice@example.com");
    // 問題：SQL 語法錯誤、型別不匹配、missing column 都不會被發現
}

// 正面範例：使用 testcontainers 真實 DB
#[tokio::test]
async fn integration_test_with_real_db() {
    let (_container, conn_str) = start_postgres_container().await;
    let pool = PgPoolOptions::new().connect(&conn_str).await.unwrap();
    run_migrations(&pool).await;
    let repo = UserRepository::new(pool);

    let user = build_user("alice@example.com", "Alice Chen", "gold");
    repo.create(&user).await.unwrap();

    let found = repo.find_by_email("alice@example.com").await.unwrap();
    assert_eq!(found.unwrap().email, "alice@example.com");
    // SQL 語法、型別對應、constraint 都被真實驗證
}
```

**對策**：明確區分 unit test 和 integration test 的職責。Unit test mock 外部依賴驗證商業邏輯，integration test 使用 testcontainers 驗證真實基礎設施互動。不要混淆兩者。

### 2. Contract Test 只驗證結構，忽略語義

Pact 預設只驗證 response 的結構（欄位名稱、型別），不驗證語義值。場景：contract 定義 `status` 欄位為 `string` 型別。Provider 回傳 `status: "UNKNOWN"` 也能通過 contract verification，但 consumer 期望的是 `"completed"` 或 `"failed"`。Consumer 收到 `"UNKNOWN"` 後的行為未被測試。

```go
// 反面範例：Contract 只驗證型別，不驗證值域
// consumer pact 定義
// {
//   "status": "completed"    // Pact 只驗證 status 是 string
// }
// provider 回傳 "UNKNOWN" 也會 pass

// 正面範例：使用 Pact matchers 限制值域
// consumer pact 定義
// {
//   "status": Term("completed", "^(completed|failed|pending)$")
// }
// provider 必須回傳 completed、failed 或 pending 其中之一
```

**對策**：使用 Pact 的 matcher（`Term`、`Like`、`EachLike`）限制欄位的值域而非只限制型別。關鍵的 enum 欄位使用 regex matcher，數值欄位使用 range matcher。Contract test 應該回答「consumer 收到的資料是否在預期範圍內」。

### 3. 每個 Test Function 都 Spin Up 新 Container 導致 CI 極慢

每個 test function 啟動獨立的 PostgreSQL container 需要 3-5 秒。如果有 50 個 integration test，光 container 啟動就要 250 秒，即使 container 平行啟動也受限於 CI machine 的 Docker daemon 效能和可用記憶體。

```go
// 反面範例：每個 test 都啟動新 container
func TestCreateUser(t *testing.T) {
    pg := startPostgresContainer(t) // 3-5 秒
    pool := setupPool(t, pg.connStr)
    // ... 測試邏輯 0.01 秒
}

func TestFindUser(t *testing.T) {
    pg := startPostgresContainer(t) // 又 3-5 秒
    pool := setupPool(t, pg.connStr)
    // ... 測試邏輯 0.01 秒
}

// 正面範例：TestMain 啟動一次 container，每個 test 用 transaction 隔離
var testPool *pgxpool.Pool

func TestMain(m *testing.M) {
    ctx := context.Background()
    container, connStr := mustStartPostgres(ctx) // 啟動一次
    testPool = mustCreatePool(ctx, connStr)
    code := m.Run()
    container.Terminate(ctx)
    os.Exit(code)
}

func TestCreateUser(t *testing.T) {
    tx := mustBeginTx(t, testPool) // 用 transaction 隔離
    defer tx.Rollback(context.Background())
    // ... 測試邏輯，使用 tx 而非 pool
}
```

**對策**：Test suite 層級啟動一次 container + 跑 migration，每個 test function 用 transaction rollback 或 `TRUNCATE` 隔離。如果測試數量龐大，可以按功能分組為多個 test suite，每個 suite 共享一個 container。

### 4. Pact Broker 成為 Single Point of Failure

所有 CI pipeline 依賴 Pact Broker 下載 contract 和上傳 verification 結果。如果 Broker 故障（磁碟滿、network partition、certificate 過期），所有服務的 CI 紅燈——不是因為程式碼有問題，而是基礎設施故障。

**對策**：(1) Pact Broker 部署為 HA（至少 2 instance + 共享 database）；(2) CI pipeline 設定 Broker 不可用時 graceful degradation（warning 而非 hard fail，搭配 alert 通知 infra team）；(3) 定期備份 Broker 的 database；(4) 考慮使用 PactFlow（Pact 的 SaaS hosted Broker）降低維運負擔。

---

## Cross-references / 交叉引用

- [[33_testing_strategy|Testing Strategy / 測試策略]] — 第 33 章建立測試金字塔的基礎概念（unit test、integration test、E2E test 的職責與比例）。本章（第 34 章）深入中間層的整合測試實作（testcontainers、真實 DB 測試）和契約測試（Pact、consumer-driven flow）。閱讀順序：先讀第 33 章建立分層概念，再讀本章了解如何落地。
- [[39_error_handling_retry|Error Handling & Retry / 錯誤處理與重試]] — 整合測試中最容易忽略的是 error path：database connection timeout、unique constraint violation、network partition。本章的 `duplicate_email_returns_unique_constraint_error` 測試示範了如何驗證 DB error handling。Retry policy 的正確性也需要 integration test 驗證（是否真的在 transient failure 後重試？是否在 permanent failure 後停止？）。
- [[40_cicd_deployment|CI/CD & Deployment / 持續整合與部署]] — 整合測試和 contract test 在 CI pipeline 中的位置：unit test（pre-commit / PR 快速階段）→ integration test（PR pipeline，需要 Docker）→ contract verification（merge 後或 on-demand trigger）→ `can-i-deploy` check（部署前 gate）。Pipeline stage 的設計直接受測試分層影響。

---

## References / 參考資料

1. **Pact Documentation** — (https://docs.pact.io/) Pact Foundation 官方文件，涵蓋 consumer test、provider verification、Pact Broker 設定、CI/CD 整合的完整指南。
2. **Testcontainers Official Site** — (https://testcontainers.com/) Docker 官方支援的 testcontainers 文件，包含 Java、Go、Rust、.NET、Python、Node.js 等語言的使用指南和 module 列表。
3. **Contract Testing in Practice** — (https://martinfowler.com/articles/consumerDrivenContracts.html) Ian Robinson, Martin Fowler Blog. Consumer-Driven Contracts 的原始論文，定義了 CDCT 的核心概念和動機。
4. **Software Engineering at Google** — Winters, Manshreck, Wright, O'Reilly, 2020. Chapter 14: Larger Testing. 涵蓋 Google 如何在數千個微服務之間管理整合測試和 contract verification。
5. **testcontainers-rs** — (https://github.com/testcontainers/testcontainers-rs) Rust 版 testcontainers 的 GitHub repo，包含 PostgreSQL、Redis、Kafka 等常見 container 的使用範例。
6. **testcontainers-go** — (https://github.com/testcontainers/testcontainers-go) Go 版 testcontainers 的 GitHub repo。`modules/` 目錄提供 PostgreSQL、MySQL、Redis、Kafka、Elasticsearch 等 20+ 種服務的 ready-to-use module。
7. **pact-go** — (https://github.com/pact-foundation/pact-go) Pact Foundation 官方 Go binding，包含 HTTP、message、gRPC 三種 interaction type 的範例。
8. **The Practical Test Pyramid** — Ham Vocke, Martin Fowler Blog, 2018. (https://martinfowler.com/articles/practical-test-pyramid.html) 測試金字塔的實踐指南，Section "Contract Tests" 深入解釋何時用 contract test 取代 E2E test。
9. **API Evolution and Compatibility** — (https://cloud.google.com/apis/design/compatibility) Google Cloud API Design Guide 的 compatibility section，定義了 backward/forward compatibility 的具體規則和範例。
