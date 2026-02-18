---
title: "Zero-Downtime Schema Migration / 零停機 Schema 遷移"
note_type: knowledge
domain: backend
category: engineering
tags: [backend, engineering, go, rust, schema-migration, zero-downtime, expand-contract]
created: 2026-02-18
updated: 2026-02-18
status: active
source: knowledge
series: backend
chapter: "55"
level: advanced
review_interval_days: 14
next_review: 2026-03-04
---

# Zero-Downtime Schema Migration / 零停機 Schema 遷移

## Intent / 意圖

零停機 Schema 遷移的目標是**在不中斷服務的前提下安全地演進資料庫結構**。在現代持續部署的環境中，應用程式的多個版本可能同時運行（rolling update、canary deployment），資料庫 schema 的變更必須與新舊版本的程式碼相容。一次不當的 `ALTER TABLE` 可以鎖住整張表數分鐘、讓所有查詢排隊逾時、觸發雪崩式故障——而使用者看到的就是一片 500 錯誤。

核心問題：**如何在有流量的生產環境中安全地變更資料庫 schema——加欄位、改型別、重新命名、加索引、加約束——而不造成服務中斷、資料遺失或新舊版本程式碼不相容？**

---

## Problem / 問題情境

**場景一：ALTER TABLE 造成全表鎖定** — DBA 在尖峰時段對一張 5 億筆訂單表執行 `ALTER TABLE orders ADD COLUMN priority INT NOT NULL DEFAULT 0`。MySQL 5.x 取得 metadata lock 後開始重建整張表，所有 SELECT / INSERT 排隊等待。3 分鐘後應用程式的連線池耗盡，API timeout 雪崩，訂單系統全面停擺。事後分析：一行 DDL 導致 12 分鐘的完全停機，損失訂單金額超過 200 萬。

**場景二：部署新版程式碼同時刪除舊欄位** — 團隊在同一次 release 中執行 migration（`DROP COLUMN old_status`）並部署新版程式碼。Rolling update 過程中，舊版 pod 仍在運行且查詢 `SELECT old_status FROM orders`——column 已不存在，500 error 狂噴。直到所有舊版 pod 被替換完畢（約 5 分鐘），50% 的請求持續失敗。

**場景三：加 NOT NULL 約束導致寫入失敗** — 新需求要求 `users.phone` 欄位為必填。工程師直接 `ALTER TABLE users ALTER COLUMN phone SET NOT NULL`。但歷史資料中有 30 萬筆 phone 為 NULL 的記錄——migration 直接失敗。即使先回填資料再加約束，在約束生效的瞬間，舊版程式碼仍可能寫入 NULL 值（因為舊版不知道要填 phone）。

---

## Core Concepts / 核心概念

### Expand-and-Contract Pattern / 展開與收縮模式

零停機 schema 遷移的核心方法論。將一次破壞性變更拆分為三個安全的階段：

1. **Expand（展開）**：加入新的 schema 元素（新欄位、新表），不刪除任何舊元素。此時新舊版程式碼都能正常運作。
2. **Migrate（遷移）**：回填資料、雙寫新舊欄位、逐步將讀取切換至新欄位。確保新舊資料一致。
3. **Contract（收縮）**：確認所有應用實例都已使用新 schema 後，刪除舊的 schema 元素。此步驟在獨立的 release 中執行。

### Online DDL / 線上 DDL

在不阻塞讀寫的情況下執行 DDL 操作的技術。不同資料庫有不同的實作方式：

| 工具/方法 | 資料庫 | 原理 | 適用場景 |
|-----------|--------|------|---------|
| **pt-online-schema-change** | MySQL | 建立影子表、觸發器同步、最後 RENAME TABLE | 大表結構變更 |
| **gh-ost** | MySQL/GitHub | 建立影子表、binlog 同步（無觸發器）、最後 cut-over | 大表、高流量 |
| **InnoDB Online DDL** | MySQL 8.0+ | 原生 ALGORITHM=INPLACE / INSTANT | 部分 DDL 可即時完成 |
| **CREATE INDEX CONCURRENTLY** | PostgreSQL | 不取得排他鎖，分階段建索引 | 大表建索引 |
| **ALTER TABLE ... ADD COLUMN** | PostgreSQL 11+ | 加帶有非 volatile default 的欄位不重寫表 | 加欄位 |

### Backward-Compatible Migration / 向後相容遷移

每一次 migration 都必須讓**當前版本與前一版本的程式碼**都能正常運作。這意味著：

- **加欄位**：安全的（舊版程式碼不讀新欄位，不影響）
- **刪欄位**：危險的（舊版程式碼可能仍在讀取）
- **改名欄位**：危險的（舊版讀舊名、新版讀新名，兩者不能同時滿足）
- **改型別**：危險的（可能造成舊版寫入失敗）

### Dual-Write Pattern / 雙寫模式

在 Expand 階段，應用程式同時寫入新舊兩個欄位/表，確保新舊 schema 的資料一致。例如在欄位重新命名時：(1) 新增新欄位；(2) 程式碼同時寫入舊欄位和新欄位；(3) 回填歷史資料到新欄位；(4) 切換讀取至新欄位；(5) 停止寫入舊欄位；(6) 刪除舊欄位。

### Shadow Table / 影子表策略

pt-online-schema-change 和 gh-ost 的核心機制。建立一張與原表相同結構的影子表，套用 DDL 變更後，逐批複製原表資料到影子表，同時透過觸發器（pt-osc）或 binlog 串流（gh-ost）同步增量變更。最後透過原子性的 RENAME TABLE 切換。

### Migration Versioning / 遷移版本控制

每個 migration 都有唯一的版本號（時間戳或序號），形成線性的變更歷史。系統透過 migration table（如 `schema_migrations`）追蹤哪些 migration 已執行。支援 up（前進）和 down（回滾）兩個方向。

### Blue-Green Database Deployment / 藍綠資料庫部署

維護兩套完整的資料庫環境。migration 先在 green 環境執行並驗證，確認安全後切換流量。適用於高風險的大型 schema 變更，但需要資料同步機制（如邏輯複製）來保持兩套 DB 的資料一致。

### Large Table Migration Strategies / 大表遷移策略

對於超過千萬筆記錄的表，直接 ALTER TABLE 可能鎖表過久。常見策略：

1. **分批回填**：將資料更新拆分為小批次（如每批 1000 筆），每批之間 sleep 避免過度佔用資源。
2. **Online DDL 工具**：gh-ost / pt-osc 透過影子表避免鎖表。
3. **新表遷移**：建新表 → 雙寫 → 回填 → 切換讀取 → 刪舊表。
4. **分區表策略**：將大表分區後可以按分區執行變更。

---

## Architecture / 架構

### Expand-and-Contract 三階段流程

```mermaid
flowchart LR
    subgraph PHASE1["Phase 1: Expand / 展開"]
        direction TB
        E1["Migration: ADD COLUMN new_col"]
        E2["Deploy v2: 雙寫<br/>old_col + new_col"]
        E3["Backfill: 回填歷史資料<br/>到 new_col"]
        E1 --> E2 --> E3
    end

    subgraph PHASE2["Phase 2: Migrate / 遷移"]
        direction TB
        M1["驗證新舊欄位<br/>資料一致性"]
        M2["Deploy v3: 讀取<br/>切換至 new_col"]
        M3["停止寫入 old_col"]
        M1 --> M2 --> M3
    end

    subgraph PHASE3["Phase 3: Contract / 收縮"]
        direction TB
        C1["確認無舊版 pod<br/>仍在讀 old_col"]
        C2["Migration: DROP<br/>COLUMN old_col"]
        C3["Deploy v4: 移除<br/>old_col 相關程式碼"]
        C1 --> C2 --> C3
    end

    PHASE1 --> PHASE2 --> PHASE3

    style PHASE1 fill:#4a9eff,color:#fff
    style PHASE2 fill:#ff9f43,color:#fff
    style PHASE3 fill:#10ac84,color:#fff
```

### Column Rename 的安全遷移流程

```mermaid
sequenceDiagram
    participant App as Application
    participant DB as Database

    Note over App,DB: Phase 1 — Expand
    App->>DB: ALTER TABLE ADD new_name (nullable)
    App->>DB: INSERT: 同時寫 old_name + new_name
    App->>DB: UPDATE (batch): old rows SET new_name = old_name

    Note over App,DB: Phase 2 — Migrate
    App->>DB: SELECT new_name (切換讀取)
    App->>DB: Verify: COUNT WHERE new_name IS NULL = 0

    Note over App,DB: Phase 3 — Contract
    App->>DB: ALTER TABLE DROP old_name
    App->>App: 移除 old_name 相關程式碼
```

### gh-ost Online Schema Change 流程

```mermaid
flowchart TB
    subgraph GHOST["gh-ost 執行流程"]
        direction TB
        G1["建立 ghost table<br/>（影子表）"]
        G2["在 ghost table 上<br/>執行 ALTER"]
        G3["連接 binlog 串流<br/>擷取增量變更"]
        G4["分批 rowcopy<br/>原表 → ghost table"]
        G5["持續套用 binlog<br/>增量到 ghost table"]
        G6["Throttle 檢查<br/>（lag、load）"]
        G7["Cut-over: 原子性<br/>RENAME TABLE 切換"]
        G1 --> G2 --> G3 --> G4
        G4 --> G5
        G5 --> G6
        G6 -->|"OK"| G7
        G6 -->|"overloaded"| G5
    end

    subgraph SAFETY["安全機制"]
        S1["--max-lag-millis<br/>replica lag 上限"]
        S2["--max-load<br/>Threads_running 上限"]
        S3["--postpone-cut-over<br/>手動確認 cut-over"]
        S4["--panic flag<br/>緊急中止"]
    end

    GHOST -.-> SAFETY

    style GHOST fill:#4a9eff,color:#fff
    style SAFETY fill:#ee5a6f,color:#fff
```

---

## How It Works / 運作原理

### 為什麼 Schema Migration 具有風險

1. **DDL 鎖定**：多數資料庫執行 DDL 時需要取得排他鎖（exclusive lock）。MySQL 的 metadata lock 會阻塞所有 DML（SELECT/INSERT/UPDATE/DELETE），PostgreSQL 的 `AccessExclusiveLock` 同理。表越大、鎖持有時間越長。
2. **表重寫**：某些 DDL 操作（如改變欄位型別、加帶有預設值的欄位）需要重寫整張表。5 億筆記錄的表重寫可能需要 10+ 分鐘。
3. **新舊版本共存**：rolling update 期間，新舊版本的程式碼同時運行。如果 migration 刪除了舊版需要的欄位，舊版立刻崩潰。
4. **不可逆操作**：`DROP COLUMN` 之後資料無法恢復。`ALTER COLUMN TYPE` 可能造成資料截斷。

### Expand-and-Contract 各階段詳細流程

**Phase 1 — Expand（展開）**

目標：在不影響現有功能的情況下，新增 schema 元素。

- 加新欄位時設為 **nullable** 且**無 NOT NULL 約束**，讓舊版程式碼寫入時不會因缺少該欄位而失敗。
- 如果需要預設值，在 PostgreSQL 11+ 中 `ADD COLUMN ... DEFAULT x` 不會重寫表（只要 default 是常數）；MySQL 8.0+ 的 `ALGORITHM=INSTANT` 也能做到。
- 部署新版程式碼時開啟**雙寫**：同時寫入新舊欄位，確保新欄位開始累積資料。
- 啟動**回填任務**：分批將歷史資料從舊欄位複製到新欄位。每批之間暫停 50-200ms 避免過度佔用 DB 資源。

**Phase 2 — Migrate（遷移）**

目標：驗證資料一致性並切換讀取路徑。

- 執行一致性檢查：`SELECT COUNT(*) WHERE new_col IS NULL AND old_col IS NOT NULL` 必須為 0。
- 部署新版程式碼將**讀取路徑切換至新欄位**。此時寫入仍然雙寫。
- 觀察一段時間（至少一個完整的 deploy cycle），確認無異常後停止寫入舊欄位。
- 如果是加 NOT NULL 約束，此時先透過 `CHECK CONSTRAINT` 驗證所有值非 NULL，再 `SET NOT NULL`。

**Phase 3 — Contract（收縮）**

目標：清理舊的 schema 元素。

- **確認所有應用實例都已升級**到不讀取舊欄位的版本。在 K8s 中可透過 `kubectl get pods -o jsonpath` 檢查 image tag。
- 執行 `DROP COLUMN old_col`。PostgreSQL 的 DROP COLUMN 幾乎是即時的（只標記為不可見，不重寫表）；MySQL 的 DROP COLUMN 仍需 metadata lock。
- 部署最終版本，移除程式碼中所有對舊欄位的引用。

### Online DDL 工具運作原理

**gh-ost（GitHub Online Schema Transformer）**

gh-ost 是 GitHub 開發的 MySQL online schema change 工具，不使用觸發器（避免觸發器的效能開銷和死鎖風險）：

1. 建立與原表相同結構的 ghost table。
2. 在 ghost table 上執行 ALTER TABLE。
3. 連接 MySQL binlog 串流，擷取原表的增量變更（INSERT/UPDATE/DELETE）。
4. 分批將原表的既有資料 rowcopy 到 ghost table。
5. 持續將 binlog 中的增量變更套用到 ghost table。
6. Rowcopy 完成後，進入 cut-over：透過原子性的 RENAME TABLE 將 ghost table 與原表互換。

gh-ost 的安全機制：
- `--max-lag-millis`：當 replica lag 超過閾值時暫停 rowcopy。
- `--max-load`：當 `Threads_running` 超過閾值時暫停。
- `--critical-load`：超過此值時直接中止整個操作。
- `--postpone-cut-over-flag-file`：寫入此檔案可延遲 cut-over，讓 DBA 手動確認。

**PostgreSQL CREATE INDEX CONCURRENTLY**

PostgreSQL 的 `CREATE INDEX` 預設取得 `ShareLock`，阻塞所有寫入。`CREATE INDEX CONCURRENTLY` 改為分兩次掃描表：第一次建立索引結構，第二次驗證並補上第一次掃描期間的新增資料。代價是建索引時間約為普通方式的 2-3 倍，且若中途失敗會留下 INVALID 索引需手動清理。

### Column Rename 安全策略

直接 `ALTER TABLE RENAME COLUMN` 會讓舊版程式碼立刻壞掉。安全做法：

```
Release 1: ADD COLUMN new_name; 雙寫 old_name + new_name; backfill
Release 2: 讀取切換至 new_name; 停止寫入 old_name
Release 3: DROP COLUMN old_name
```

### NOT NULL Constraint 安全添加

直接 `ALTER TABLE ALTER COLUMN SET NOT NULL` 在 PostgreSQL 中會掃描全表驗證（取得 AccessExclusiveLock），大表上耗時且鎖表。安全做法：

```sql
-- Step 1: 加 CHECK CONSTRAINT（PostgreSQL 12+ 可用 NOT VALID 避免掃描）
ALTER TABLE users ADD CONSTRAINT users_phone_not_null
    CHECK (phone IS NOT NULL) NOT VALID;

-- Step 2: 驗證約束（不取得排他鎖，只取得 ShareUpdateExclusiveLock）
ALTER TABLE users VALIDATE CONSTRAINT users_phone_not_null;

-- Step 3 (optional): 加正式的 NOT NULL（PostgreSQL 12+ 偵測到等效 CHECK 後會跳過全表掃描）
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;

-- Step 4: 移除 CHECK CONSTRAINT（已有 NOT NULL 保護）
ALTER TABLE users DROP CONSTRAINT users_phone_not_null;
```

### Migration Rollback 策略

每個 migration 都必須有對應的 rollback 計畫：

| 操作類型 | Rollback 方式 | 風險等級 |
|---------|--------------|---------|
| ADD COLUMN | DROP COLUMN | 低（資料量小時可即時完成） |
| DROP COLUMN | 無法直接 rollback（需從備份恢復） | 高 |
| ADD INDEX | DROP INDEX | 低 |
| ADD CONSTRAINT | DROP CONSTRAINT | 低 |
| ALTER COLUMN TYPE | ALTER COLUMN TYPE back（可能資料截斷） | 中 |
| RENAME COLUMN | RENAME COLUMN back | 低（但需考慮程式碼相容性） |

**原則**：在 Contract 階段之前，所有操作都可以安全 rollback。一旦進入 Contract（刪除舊元素），rollback 就變得困難或不可能。因此 Contract 階段必須在充分驗證後才執行。

### Testing Migrations 策略

1. **Schema diff 測試**：在 CI 中對空白資料庫執行所有 migration up，再執行所有 migration down，驗證回到初始狀態。
2. **Production clone 測試**：從 production 備份恢復到測試環境，執行 migration 驗證效能和正確性。
3. **相容性測試**：同時運行新舊版程式碼對已遷移的 schema 進行讀寫測試。
4. **Lock duration 測試**：在測試環境中監控 DDL 的鎖持有時間，確保不超過可接受的閾值（通常 < 1 秒）。

---

## Rust 實作

```rust
// zero_downtime_migrator.rs — Expand-and-Contract migration runner
// Rust 2024 edition, tokio 1, sqlx 0.8 (PostgreSQL)
//
// 實作完整的零停機 schema 遷移執行器，支援：
// - 版本追蹤（schema_migrations 表）
// - Expand / Migrate / Contract 三階段標記
// - 分批回填（避免大量 UPDATE 鎖表）
// - Rollback 支援
// - 遷移前後驗證

// Cargo.toml dependencies:
// sqlx = { version = "0.8", features = ["runtime-tokio", "postgres"] }
// tokio = { version = "1", features = ["full"] }
// chrono = { version = "0.4", features = ["serde"] }
// serde = { version = "1", features = ["derive"] }
// serde_json = "1"

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::{PgPool, postgres::PgPoolOptions, Row};
use std::time::Duration;

// ─── Migration Phase Enum ───

/// 遷移階段：對應 expand-and-contract 的三個階段
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum MigrationPhase {
    /// 展開：加入新 schema 元素，不刪除任何舊元素
    Expand,
    /// 遷移：回填資料、切換讀寫路徑
    Migrate,
    /// 收縮：刪除舊 schema 元素（不可逆）
    Contract,
}

impl std::fmt::Display for MigrationPhase {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            MigrationPhase::Expand => write!(f, "expand"),
            MigrationPhase::Migrate => write!(f, "migrate"),
            MigrationPhase::Contract => write!(f, "contract"),
        }
    }
}

// ─── Migration Definition ───

/// 單一遷移定義：包含 up/down SQL 和元資料
#[derive(Debug, Clone)]
pub struct Migration {
    /// 版本號（時間戳格式：20260218120000）
    pub version: i64,
    /// 遷移描述
    pub description: String,
    /// 遷移階段
    pub phase: MigrationPhase,
    /// 前進 SQL
    pub up_sql: String,
    /// 回滾 SQL
    pub down_sql: String,
    /// 是否需要分批回填
    pub requires_backfill: bool,
    /// 回填 SQL（分批執行，須包含 LIMIT 和 OFFSET 佔位符）
    pub backfill_sql: Option<String>,
    /// 每批回填筆數
    pub backfill_batch_size: i64,
}

// ─── Migration Record ───

/// 已執行的遷移記錄
#[derive(Debug, Clone, Serialize)]
pub struct MigrationRecord {
    pub version: i64,
    pub description: String,
    pub phase: String,
    pub applied_at: DateTime<Utc>,
    pub execution_time_ms: i64,
    pub rolled_back: bool,
}

// ─── Migrator ───

/// 零停機遷移執行器
pub struct Migrator {
    pool: PgPool,
    migrations: Vec<Migration>,
}

impl Migrator {
    /// 建立新的遷移執行器
    pub async fn new(database_url: &str) -> Result<Self, sqlx::Error> {
        let pool = PgPoolOptions::new()
            .max_connections(5)
            .acquire_timeout(Duration::from_secs(5))
            .connect(database_url)
            .await?;

        Ok(Self {
            pool,
            migrations: Vec::new(),
        })
    }

    /// 從既有 pool 建立（用於測試）
    pub fn from_pool(pool: PgPool) -> Self {
        Self {
            pool,
            migrations: Vec::new(),
        }
    }

    /// 註冊遷移
    pub fn add_migration(&mut self, migration: Migration) {
        self.migrations.push(migration);
        // 按版本號排序
        self.migrations.sort_by_key(|m| m.version);
    }

    /// 初始化 schema_migrations 表
    pub async fn initialize(&self) -> Result<(), sqlx::Error> {
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version      BIGINT PRIMARY KEY,
                description  TEXT NOT NULL,
                phase        TEXT NOT NULL,
                applied_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                execution_time_ms BIGINT NOT NULL DEFAULT 0,
                rolled_back  BOOLEAN NOT NULL DEFAULT FALSE
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        println!("[migrator] schema_migrations table ready");
        Ok(())
    }

    /// 取得已執行的版本列表
    pub async fn applied_versions(&self) -> Result<Vec<i64>, sqlx::Error> {
        let rows = sqlx::query(
            "SELECT version FROM schema_migrations WHERE rolled_back = FALSE ORDER BY version",
        )
        .fetch_all(&self.pool)
        .await?;

        Ok(rows.iter().map(|r| r.get::<i64, _>("version")).collect())
    }

    /// 取得待執行的遷移
    pub async fn pending_migrations(
        &self,
        target_phase: Option<MigrationPhase>,
    ) -> Result<Vec<&Migration>, sqlx::Error> {
        let applied = self.applied_versions().await?;
        let pending: Vec<&Migration> = self
            .migrations
            .iter()
            .filter(|m| {
                !applied.contains(&m.version)
                    && target_phase.as_ref().is_none_or(|p| m.phase == *p)
            })
            .collect();

        Ok(pending)
    }

    /// 執行指定階段的所有待執行遷移
    pub async fn run_phase(
        &self,
        phase: MigrationPhase,
    ) -> Result<Vec<MigrationRecord>, sqlx::Error> {
        let pending = self.pending_migrations(Some(phase)).await?;
        let mut records = Vec::new();

        if pending.is_empty() {
            println!("[migrator] no pending migrations for phase: {phase}");
            return Ok(records);
        }

        for migration in pending {
            println!(
                "[migrator] running v{} ({}) [{}]: {}",
                migration.version, phase, migration.description, migration.up_sql
            );

            let start = std::time::Instant::now();

            // 在 transaction 中執行 DDL + 記錄
            let mut tx = self.pool.begin().await?;

            sqlx::query(&migration.up_sql).execute(&mut *tx).await?;

            let elapsed_ms = start.elapsed().as_millis() as i64;

            sqlx::query(
                r#"
                INSERT INTO schema_migrations (version, description, phase, execution_time_ms)
                VALUES ($1, $2, $3, $4)
                "#,
            )
            .bind(migration.version)
            .bind(&migration.description)
            .bind(phase.to_string())
            .bind(elapsed_ms)
            .execute(&mut *tx)
            .await?;

            tx.commit().await?;

            // 如果需要回填，在 transaction 外分批執行
            if migration.requires_backfill {
                if let Some(ref backfill_sql) = migration.backfill_sql {
                    self.run_backfill(backfill_sql, migration.backfill_batch_size)
                        .await?;
                }
            }

            let record = MigrationRecord {
                version: migration.version,
                description: migration.description.clone(),
                phase: phase.to_string(),
                applied_at: Utc::now(),
                execution_time_ms: elapsed_ms,
                rolled_back: false,
            };

            println!(
                "[migrator] completed v{} in {}ms",
                migration.version, elapsed_ms
            );
            records.push(record);
        }

        Ok(records)
    }

    /// 分批回填：避免長時間鎖表
    async fn run_backfill(
        &self,
        backfill_sql: &str,
        batch_size: i64,
    ) -> Result<(), sqlx::Error> {
        let mut total_updated: i64 = 0;
        let mut batch_num: i64 = 0;

        loop {
            let result = sqlx::query(backfill_sql)
                .bind(batch_size)
                .execute(&self.pool)
                .await?;

            let rows_affected = result.rows_affected() as i64;
            total_updated += rows_affected;
            batch_num += 1;

            println!(
                "[backfill] batch {batch_num}: updated {rows_affected} rows (total: {total_updated})"
            );

            if rows_affected < batch_size {
                break; // 最後一批，回填完成
            }

            // 每批之間暫停，避免過度佔用 DB 資源
            tokio::time::sleep(Duration::from_millis(100)).await;
        }

        println!("[backfill] completed: {total_updated} rows updated in {batch_num} batches");
        Ok(())
    }

    /// 回滾指定版本的遷移
    pub async fn rollback_version(
        &self,
        version: i64,
    ) -> Result<Option<MigrationRecord>, sqlx::Error> {
        let migration = self.migrations.iter().find(|m| m.version == version);
        let Some(migration) = migration else {
            println!("[migrator] version {version} not found in registered migrations");
            return Ok(None);
        };

        // 檢查是否為 Contract 階段——回滾不可逆操作需要特別警告
        if migration.phase == MigrationPhase::Contract {
            println!(
                "[migrator] WARNING: rolling back contract phase migration v{version}. \
                 This may not fully restore dropped data!"
            );
        }

        println!(
            "[migrator] rolling back v{}: {}",
            version, migration.down_sql
        );

        let start = std::time::Instant::now();
        let mut tx = self.pool.begin().await?;

        sqlx::query(&migration.down_sql)
            .execute(&mut *tx)
            .await?;

        // 標記為已回滾
        sqlx::query(
            "UPDATE schema_migrations SET rolled_back = TRUE WHERE version = $1",
        )
        .bind(version)
        .execute(&mut *tx)
        .await?;

        tx.commit().await?;

        let elapsed_ms = start.elapsed().as_millis() as i64;
        println!("[migrator] rollback v{version} completed in {elapsed_ms}ms");

        Ok(Some(MigrationRecord {
            version,
            description: migration.description.clone(),
            phase: migration.phase.to_string(),
            applied_at: Utc::now(),
            execution_time_ms: elapsed_ms,
            rolled_back: true,
        }))
    }

    /// 取得遷移狀態摘要
    pub async fn status(&self) -> Result<Vec<MigrationRecord>, sqlx::Error> {
        let rows = sqlx::query(
            r#"
            SELECT version, description, phase, applied_at,
                   execution_time_ms, rolled_back
            FROM schema_migrations
            ORDER BY version
            "#,
        )
        .fetch_all(&self.pool)
        .await?;

        let records = rows
            .iter()
            .map(|r| MigrationRecord {
                version: r.get("version"),
                description: r.get("description"),
                phase: r.get("phase"),
                applied_at: r.get("applied_at"),
                execution_time_ms: r.get("execution_time_ms"),
                rolled_back: r.get("rolled_back"),
            })
            .collect();

        Ok(records)
    }
}

// ─── Example: Renaming a Column (3 phases) ───

/// 建立「重新命名 orders.status → orders.order_status」的三階段遷移
fn create_rename_column_migrations() -> Vec<Migration> {
    vec![
        // Phase 1: Expand — 加新欄位
        Migration {
            version: 20260218_100000,
            description: "add order_status column (expand)".to_string(),
            phase: MigrationPhase::Expand,
            up_sql: r#"
                ALTER TABLE orders ADD COLUMN order_status TEXT;
                COMMENT ON COLUMN orders.order_status IS 'Replaces orders.status';
            "#
            .to_string(),
            down_sql: "ALTER TABLE orders DROP COLUMN IF EXISTS order_status"
                .to_string(),
            requires_backfill: true,
            backfill_sql: Some(
                r#"
                UPDATE orders
                SET order_status = status
                WHERE order_status IS NULL
                  AND ctid IN (
                    SELECT ctid FROM orders
                    WHERE order_status IS NULL
                    LIMIT $1
                  )
                "#
                .to_string(),
            ),
            backfill_batch_size: 5000,
        },
        // Phase 2: Migrate — 切換讀取、加約束
        Migration {
            version: 20260218_110000,
            description: "add not-null check on order_status (migrate)".to_string(),
            phase: MigrationPhase::Migrate,
            up_sql: r#"
                ALTER TABLE orders
                    ADD CONSTRAINT orders_order_status_not_null
                    CHECK (order_status IS NOT NULL) NOT VALID;
                ALTER TABLE orders
                    VALIDATE CONSTRAINT orders_order_status_not_null;
            "#
            .to_string(),
            down_sql:
                "ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_order_status_not_null"
                    .to_string(),
            requires_backfill: false,
            backfill_sql: None,
            backfill_batch_size: 0,
        },
        // Phase 3: Contract — 刪除舊欄位
        Migration {
            version: 20260218_120000,
            description: "drop old status column (contract)".to_string(),
            phase: MigrationPhase::Contract,
            up_sql: "ALTER TABLE orders DROP COLUMN status".to_string(),
            down_sql: "ALTER TABLE orders ADD COLUMN status TEXT".to_string(),
            requires_backfill: false,
            backfill_sql: None,
            backfill_batch_size: 0,
        },
    ]
}

// ─── Main ───

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let database_url =
        std::env::var("DATABASE_URL").unwrap_or_else(|_| {
            "postgres://app:secret@localhost:5432/orders_db".to_string()
        });

    let mut migrator = Migrator::new(&database_url).await?;
    migrator.initialize().await?;

    // 建立測試用 orders 表
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'pending',
            amount NUMERIC(10,2) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        "#,
    )
    .execute(&migrator.pool)
    .await?;

    // 插入測試資料
    sqlx::query(
        "INSERT INTO orders (status, amount) VALUES ('pending', 99.99), ('completed', 45.50)"
    )
    .execute(&migrator.pool)
    .await?;

    // 註冊三階段遷移
    for m in create_rename_column_migrations() {
        migrator.add_migration(m);
    }

    // 執行 Phase 1: Expand
    println!("\n=== Phase 1: Expand ===");
    let expand_results = migrator.run_phase(MigrationPhase::Expand).await?;
    for r in &expand_results {
        println!("  applied v{} ({}ms)", r.version, r.execution_time_ms);
    }

    // 執行 Phase 2: Migrate
    println!("\n=== Phase 2: Migrate ===");
    let migrate_results = migrator.run_phase(MigrationPhase::Migrate).await?;
    for r in &migrate_results {
        println!("  applied v{} ({}ms)", r.version, r.execution_time_ms);
    }

    // 印出狀態
    println!("\n=== Migration Status ===");
    let status = migrator.status().await?;
    for s in &status {
        println!(
            "  v{}: {} [{}] {}ms rolled_back={}",
            s.version, s.description, s.phase, s.execution_time_ms, s.rolled_back
        );
    }

    // 示範 rollback Phase 2
    println!("\n=== Rollback Phase 2 ===");
    if let Some(record) = migrator.rollback_version(20260218_110000).await? {
        println!(
            "  rolled back v{} ({}ms)",
            record.version, record.execution_time_ms
        );
    }

    // 最終狀態
    println!("\n=== Final Status ===");
    let final_status = migrator.status().await?;
    for s in &final_status {
        println!(
            "  v{}: {} [{}] rolled_back={}",
            s.version, s.description, s.phase, s.rolled_back
        );
    }

    Ok(())

    // Output:
    // [migrator] schema_migrations table ready
    //
    // === Phase 1: Expand ===
    // [migrator] running v20260218100000 (expand) [add order_status column (expand)]: ...
    // [backfill] batch 1: updated 2 rows (total: 2)
    // [backfill] completed: 2 rows updated in 1 batches
    // [migrator] completed v20260218100000 in 12ms
    //   applied v20260218100000 (12ms)
    //
    // === Phase 2: Migrate ===
    // [migrator] running v20260218110000 (migrate) [add not-null check on order_status (migrate)]: ...
    // [migrator] completed v20260218110000 in 8ms
    //   applied v20260218110000 (8ms)
    //
    // === Migration Status ===
    //   v20260218100000: add order_status column (expand) [expand] 12ms rolled_back=false
    //   v20260218110000: add not-null check on order_status (migrate) [migrate] 8ms rolled_back=false
    //
    // === Rollback Phase 2 ===
    // [migrator] rolling back v20260218110000: ALTER TABLE orders DROP CONSTRAINT IF EXISTS ...
    // [migrator] rollback v20260218110000 completed in 5ms
    //   rolled back v20260218110000 (5ms)
    //
    // === Final Status ===
    //   v20260218100000: add order_status column (expand) [expand] rolled_back=false
    //   v20260218110000: add not-null check on order_status (migrate) [migrate] rolled_back=true
}
```

### 設計重點

- **`MigrationPhase` enum**：型別安全地區分三個階段，確保 Contract 階段不會被意外提前執行。Rust 的 enum 在編譯期保證窮舉性。
- **分批回填**：`run_backfill` 方法使用 `LIMIT` 分批 UPDATE，每批之間 `tokio::time::sleep` 讓出 CPU 和 DB 資源。使用 `ctid` 子查詢避免 PostgreSQL 的 `UPDATE ... LIMIT` 不支援問題。
- **Transaction 包裹 DDL + 記錄**：DDL 和 `schema_migrations` 的 INSERT 在同一個 transaction 中，確保原子性——要嘛遷移成功且有記錄，要嘛兩者都不生效。
- **Rollback 警告**：回滾 Contract 階段時印出 WARNING，提醒操作者 DROP COLUMN 已造成不可逆的資料遺失。
- **sqlx compile-time checking**：生產環境中可使用 `sqlx::query!` 宏在編譯期驗證 SQL，此處為了簡潔使用動態 SQL。

---

## Go 實作

```go
// zero_downtime_migrator.go — Expand-and-Contract migration runner
// Go 1.24+, database/sql + pgx v5
//
// 實作完整的零停機 schema 遷移執行器，支援：
// - 版本追蹤（schema_migrations 表）
// - Expand / Migrate / Contract 三階段標記
// - 分批回填（避免大量 UPDATE 鎖表）
// - Rollback 支援
// - 遷移前後驗證

package main

import (
	"context"
	"database/sql"
	"fmt"
	"log/slog"
	"os"
	"slices"
	"time"

	_ "github.com/jackc/pgx/v5/stdlib"
)

// ─── Migration Phase ───

// MigrationPhase 代表 expand-and-contract 的三個階段
type MigrationPhase string

const (
	PhaseExpand   MigrationPhase = "expand"
	PhaseMigrate  MigrationPhase = "migrate"
	PhaseContract MigrationPhase = "contract"
)

// ─── Migration Definition ───

// Migration 定義單一遷移的 up/down SQL 和元資料
type Migration struct {
	Version          int64          // 版本號（時間戳格式：20260218120000）
	Description      string         // 遷移描述
	Phase            MigrationPhase // 遷移階段
	UpSQL            string         // 前進 SQL
	DownSQL          string         // 回滾 SQL
	RequiresBackfill bool           // 是否需要分批回填
	BackfillSQL      string         // 回填 SQL（需包含 $1 作為 LIMIT）
	BackfillBatch    int64          // 每批回填筆數
}

// ─── Migration Record ───

// MigrationRecord 記錄已執行的遷移
type MigrationRecord struct {
	Version         int64     `json:"version"`
	Description     string    `json:"description"`
	Phase           string    `json:"phase"`
	AppliedAt       time.Time `json:"applied_at"`
	ExecutionTimeMs int64     `json:"execution_time_ms"`
	RolledBack      bool      `json:"rolled_back"`
}

// ─── Migrator ───

// Migrator 是零停機遷移執行器
type Migrator struct {
	db         *sql.DB
	migrations []Migration
	logger     *slog.Logger
}

// NewMigrator 建立新的遷移執行器
func NewMigrator(databaseURL string) (*Migrator, error) {
	db, err := sql.Open("pgx", databaseURL)
	if err != nil {
		return nil, fmt.Errorf("open db: %w", err)
	}

	db.SetMaxOpenConns(5)
	db.SetMaxIdleConns(2)
	db.SetConnMaxLifetime(30 * time.Minute)

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		return nil, fmt.Errorf("ping db: %w", err)
	}

	return &Migrator{
		db:     db,
		logger: slog.New(slog.NewTextHandler(os.Stdout, nil)),
	}, nil
}

// FromDB 從既有 *sql.DB 建立（用於測試）
func FromDB(db *sql.DB) *Migrator {
	return &Migrator{
		db:     db,
		logger: slog.New(slog.NewTextHandler(os.Stdout, nil)),
	}
}

// AddMigration 註冊遷移
func (m *Migrator) AddMigration(migration Migration) {
	m.migrations = append(m.migrations, migration)
	slices.SortFunc(m.migrations, func(a, b Migration) int {
		if a.Version < b.Version {
			return -1
		}
		if a.Version > b.Version {
			return 1
		}
		return 0
	})
}

// Initialize 建立 schema_migrations 表
func (m *Migrator) Initialize(ctx context.Context) error {
	_, err := m.db.ExecContext(ctx, `
		CREATE TABLE IF NOT EXISTS schema_migrations (
			version          BIGINT PRIMARY KEY,
			description      TEXT NOT NULL,
			phase            TEXT NOT NULL,
			applied_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
			execution_time_ms BIGINT NOT NULL DEFAULT 0,
			rolled_back      BOOLEAN NOT NULL DEFAULT FALSE
		)
	`)
	if err != nil {
		return fmt.Errorf("create schema_migrations: %w", err)
	}

	m.logger.Info("schema_migrations table ready")
	return nil
}

// AppliedVersions 取得已執行的版本列表
func (m *Migrator) AppliedVersions(ctx context.Context) ([]int64, error) {
	rows, err := m.db.QueryContext(ctx,
		"SELECT version FROM schema_migrations WHERE rolled_back = FALSE ORDER BY version",
	)
	if err != nil {
		return nil, fmt.Errorf("query applied versions: %w", err)
	}
	defer rows.Close()

	var versions []int64
	for rows.Next() {
		var v int64
		if err := rows.Scan(&v); err != nil {
			return nil, fmt.Errorf("scan version: %w", err)
		}
		versions = append(versions, v)
	}
	return versions, rows.Err()
}

// PendingMigrations 取得指定階段的待執行遷移
func (m *Migrator) PendingMigrations(
	ctx context.Context,
	phase *MigrationPhase,
) ([]Migration, error) {
	applied, err := m.AppliedVersions(ctx)
	if err != nil {
		return nil, err
	}

	appliedSet := make(map[int64]bool, len(applied))
	for _, v := range applied {
		appliedSet[v] = true
	}

	var pending []Migration
	for _, mg := range m.migrations {
		if appliedSet[mg.Version] {
			continue
		}
		if phase != nil && mg.Phase != *phase {
			continue
		}
		pending = append(pending, mg)
	}
	return pending, nil
}

// RunPhase 執行指定階段的所有待執行遷移
func (m *Migrator) RunPhase(
	ctx context.Context,
	phase MigrationPhase,
) ([]MigrationRecord, error) {
	pending, err := m.PendingMigrations(ctx, &phase)
	if err != nil {
		return nil, err
	}

	if len(pending) == 0 {
		m.logger.Info("no pending migrations", "phase", phase)
		return nil, nil
	}

	var records []MigrationRecord

	for _, mg := range pending {
		m.logger.Info("running migration",
			"version", mg.Version,
			"phase", phase,
			"description", mg.Description,
		)

		start := time.Now()

		// 在 transaction 中執行 DDL + 記錄
		tx, err := m.db.BeginTx(ctx, nil)
		if err != nil {
			return records, fmt.Errorf("begin tx: %w", err)
		}

		if _, err := tx.ExecContext(ctx, mg.UpSQL); err != nil {
			tx.Rollback()
			return records, fmt.Errorf("exec migration v%d: %w", mg.Version, err)
		}

		elapsedMs := time.Since(start).Milliseconds()

		if _, err := tx.ExecContext(ctx, `
			INSERT INTO schema_migrations (version, description, phase, execution_time_ms)
			VALUES ($1, $2, $3, $4)
		`, mg.Version, mg.Description, string(phase), elapsedMs); err != nil {
			tx.Rollback()
			return records, fmt.Errorf("record migration v%d: %w", mg.Version, err)
		}

		if err := tx.Commit(); err != nil {
			return records, fmt.Errorf("commit migration v%d: %w", mg.Version, err)
		}

		// 分批回填（在 transaction 外執行）
		if mg.RequiresBackfill && mg.BackfillSQL != "" {
			if err := m.runBackfill(ctx, mg.BackfillSQL, mg.BackfillBatch); err != nil {
				return records, fmt.Errorf("backfill v%d: %w", mg.Version, err)
			}
		}

		record := MigrationRecord{
			Version:         mg.Version,
			Description:     mg.Description,
			Phase:           string(phase),
			AppliedAt:       time.Now(),
			ExecutionTimeMs: elapsedMs,
			RolledBack:      false,
		}
		records = append(records, record)

		m.logger.Info("migration completed",
			"version", mg.Version,
			"elapsed_ms", elapsedMs,
		)
	}

	return records, nil
}

// runBackfill 分批回填：避免長時間鎖表
func (m *Migrator) runBackfill(
	ctx context.Context,
	backfillSQL string,
	batchSize int64,
) error {
	var totalUpdated, batchNum int64

	for {
		result, err := m.db.ExecContext(ctx, backfillSQL, batchSize)
		if err != nil {
			return fmt.Errorf("backfill batch %d: %w", batchNum, err)
		}

		rowsAffected, _ := result.RowsAffected()
		totalUpdated += rowsAffected
		batchNum++

		m.logger.Info("backfill batch",
			"batch", batchNum,
			"rows", rowsAffected,
			"total", totalUpdated,
		)

		if rowsAffected < batchSize {
			break // 最後一批
		}

		// 每批之間暫停，避免過度佔用 DB 資源
		time.Sleep(100 * time.Millisecond)
	}

	m.logger.Info("backfill completed",
		"total_rows", totalUpdated,
		"batches", batchNum,
	)
	return nil
}

// RollbackVersion 回滾指定版本的遷移
func (m *Migrator) RollbackVersion(
	ctx context.Context,
	version int64,
) (*MigrationRecord, error) {
	// 找到對應的遷移定義
	var target *Migration
	for i := range m.migrations {
		if m.migrations[i].Version == version {
			target = &m.migrations[i]
			break
		}
	}

	if target == nil {
		m.logger.Warn("migration not found", "version", version)
		return nil, nil
	}

	if target.Phase == PhaseContract {
		m.logger.Warn("rolling back contract phase — data loss may be irreversible",
			"version", version,
		)
	}

	m.logger.Info("rolling back migration",
		"version", version,
		"down_sql", target.DownSQL,
	)

	start := time.Now()

	tx, err := m.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("begin tx: %w", err)
	}

	if _, err := tx.ExecContext(ctx, target.DownSQL); err != nil {
		tx.Rollback()
		return nil, fmt.Errorf("rollback v%d: %w", version, err)
	}

	if _, err := tx.ExecContext(ctx,
		"UPDATE schema_migrations SET rolled_back = TRUE WHERE version = $1",
		version,
	); err != nil {
		tx.Rollback()
		return nil, fmt.Errorf("record rollback v%d: %w", version, err)
	}

	if err := tx.Commit(); err != nil {
		return nil, fmt.Errorf("commit rollback v%d: %w", version, err)
	}

	elapsedMs := time.Since(start).Milliseconds()
	m.logger.Info("rollback completed",
		"version", version,
		"elapsed_ms", elapsedMs,
	)

	return &MigrationRecord{
		Version:         version,
		Description:     target.Description,
		Phase:           string(target.Phase),
		AppliedAt:       time.Now(),
		ExecutionTimeMs: elapsedMs,
		RolledBack:      true,
	}, nil
}

// Status 取得所有遷移狀態
func (m *Migrator) Status(ctx context.Context) ([]MigrationRecord, error) {
	rows, err := m.db.QueryContext(ctx, `
		SELECT version, description, phase, applied_at,
		       execution_time_ms, rolled_back
		FROM schema_migrations
		ORDER BY version
	`)
	if err != nil {
		return nil, fmt.Errorf("query status: %w", err)
	}
	defer rows.Close()

	var records []MigrationRecord
	for rows.Next() {
		var r MigrationRecord
		if err := rows.Scan(
			&r.Version, &r.Description, &r.Phase,
			&r.AppliedAt, &r.ExecutionTimeMs, &r.RolledBack,
		); err != nil {
			return nil, fmt.Errorf("scan record: %w", err)
		}
		records = append(records, r)
	}
	return records, rows.Err()
}

// Close 關閉資料庫連線
func (m *Migrator) Close() error {
	return m.db.Close()
}

// ─── Example: Renaming a Column (3 phases) ───

// createRenameColumnMigrations 建立重新命名欄位的三階段遷移
func createRenameColumnMigrations() []Migration {
	return []Migration{
		{
			Version:     20260218_100000,
			Description: "add order_status column (expand)",
			Phase:       PhaseExpand,
			UpSQL: `
				ALTER TABLE orders ADD COLUMN order_status TEXT;
				COMMENT ON COLUMN orders.order_status IS 'Replaces orders.status';
			`,
			DownSQL:          "ALTER TABLE orders DROP COLUMN IF EXISTS order_status",
			RequiresBackfill: true,
			BackfillSQL: `
				UPDATE orders
				SET order_status = status
				WHERE order_status IS NULL
				  AND ctid IN (
				    SELECT ctid FROM orders
				    WHERE order_status IS NULL
				    LIMIT $1
				  )
			`,
			BackfillBatch: 5000,
		},
		{
			Version:     20260218_110000,
			Description: "add not-null check on order_status (migrate)",
			Phase:       PhaseMigrate,
			UpSQL: `
				ALTER TABLE orders
				    ADD CONSTRAINT orders_order_status_not_null
				    CHECK (order_status IS NOT NULL) NOT VALID;
				ALTER TABLE orders
				    VALIDATE CONSTRAINT orders_order_status_not_null;
			`,
			DownSQL: "ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_order_status_not_null",
		},
		{
			Version:     20260218_120000,
			Description: "drop old status column (contract)",
			Phase:       PhaseContract,
			UpSQL:       "ALTER TABLE orders DROP COLUMN status",
			DownSQL:     "ALTER TABLE orders ADD COLUMN status TEXT",
		},
	}
}

// ─── Main ───

func main() {
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		databaseURL = "postgres://app:secret@localhost:5432/orders_db"
	}

	migrator, err := NewMigrator(databaseURL)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to create migrator: %v\n", err)
		os.Exit(1)
	}
	defer migrator.Close()

	ctx := context.Background()

	if err := migrator.Initialize(ctx); err != nil {
		fmt.Fprintf(os.Stderr, "failed to initialize: %v\n", err)
		os.Exit(1)
	}

	// 建立測試用 orders 表
	if _, err := migrator.db.ExecContext(ctx, `
		CREATE TABLE IF NOT EXISTS orders (
			id SERIAL PRIMARY KEY,
			status TEXT NOT NULL DEFAULT 'pending',
			amount NUMERIC(10,2) NOT NULL,
			created_at TIMESTAMPTZ DEFAULT NOW()
		)
	`); err != nil {
		fmt.Fprintf(os.Stderr, "create orders table: %v\n", err)
		os.Exit(1)
	}

	// 插入測試資料
	migrator.db.ExecContext(ctx,
		"INSERT INTO orders (status, amount) VALUES ('pending', 99.99), ('completed', 45.50)",
	)

	// 註冊三階段遷移
	for _, mg := range createRenameColumnMigrations() {
		migrator.AddMigration(mg)
	}

	// 執行 Phase 1: Expand
	fmt.Println("\n=== Phase 1: Expand ===")
	expandResults, err := migrator.RunPhase(ctx, PhaseExpand)
	if err != nil {
		fmt.Fprintf(os.Stderr, "expand failed: %v\n", err)
		os.Exit(1)
	}
	for _, r := range expandResults {
		fmt.Printf("  applied v%d (%dms)\n", r.Version, r.ExecutionTimeMs)
	}

	// 執行 Phase 2: Migrate
	fmt.Println("\n=== Phase 2: Migrate ===")
	migrateResults, err := migrator.RunPhase(ctx, PhaseMigrate)
	if err != nil {
		fmt.Fprintf(os.Stderr, "migrate failed: %v\n", err)
		os.Exit(1)
	}
	for _, r := range migrateResults {
		fmt.Printf("  applied v%d (%dms)\n", r.Version, r.ExecutionTimeMs)
	}

	// 印出狀態
	fmt.Println("\n=== Migration Status ===")
	status, _ := migrator.Status(ctx)
	for _, s := range status {
		fmt.Printf("  v%d: %s [%s] %dms rolled_back=%v\n",
			s.Version, s.Description, s.Phase, s.ExecutionTimeMs, s.RolledBack,
		)
	}

	// 示範 rollback Phase 2
	fmt.Println("\n=== Rollback Phase 2 ===")
	record, err := migrator.RollbackVersion(ctx, 20260218_110000)
	if err != nil {
		fmt.Fprintf(os.Stderr, "rollback failed: %v\n", err)
		os.Exit(1)
	}
	if record != nil {
		fmt.Printf("  rolled back v%d (%dms)\n", record.Version, record.ExecutionTimeMs)
	}

	// 最終狀態
	fmt.Println("\n=== Final Status ===")
	finalStatus, _ := migrator.Status(ctx)
	for _, s := range finalStatus {
		fmt.Printf("  v%d: %s [%s] rolled_back=%v\n",
			s.Version, s.Description, s.Phase, s.RolledBack,
		)
	}

	// Output:
	// time=... level=INFO msg="schema_migrations table ready"
	//
	// === Phase 1: Expand ===
	// time=... level=INFO msg="running migration" version=20260218100000 phase=expand description="add order_status column (expand)"
	// time=... level=INFO msg="backfill batch" batch=1 rows=2 total=2
	// time=... level=INFO msg="backfill completed" total_rows=2 batches=1
	// time=... level=INFO msg="migration completed" version=20260218100000 elapsed_ms=15
	//   applied v20260218100000 (15ms)
	//
	// === Phase 2: Migrate ===
	// time=... level=INFO msg="running migration" version=20260218110000 phase=migrate description="add not-null check on order_status (migrate)"
	// time=... level=INFO msg="migration completed" version=20260218110000 elapsed_ms=10
	//   applied v20260218110000 (10ms)
	//
	// === Migration Status ===
	//   v20260218100000: add order_status column (expand) [expand] 15ms rolled_back=false
	//   v20260218110000: add not-null check on order_status (migrate) [migrate] 10ms rolled_back=false
	//
	// === Rollback Phase 2 ===
	// time=... level=WARN msg="rolling back migration" version=20260218110000 ...
	// time=... level=INFO msg="rollback completed" version=20260218110000 elapsed_ms=6
	//   rolled back v20260218110000 (6ms)
	//
	// === Final Status ===
	//   v20260218100000: add order_status column (expand) [expand] rolled_back=false
	//   v20260218110000: add not-null check on order_status (migrate) [migrate] rolled_back=true
}
```

### 設計重點

- **`context.Context` 貫穿全程**：Go 慣例——所有 DB 操作都接受 `ctx`，支援 timeout 和取消。生產環境中應為每次 migration 設定合理的 context timeout。
- **`defer rows.Close()`**：Go 中 `*sql.Rows` 必須明確關閉，否則連線洩漏。Rust 的 sqlx 由 Drop trait 自動處理，Go 需要開發者紀律。
- **`slices.SortFunc`**：使用 Go 1.21+ 的 `slices` 套件排序遷移，比自訂 `sort.Slice` 更清晰。
- **Transaction 內外分離**：DDL + schema_migrations 記錄在 transaction 內（原子性），backfill 在 transaction 外（避免長時間持有 transaction lock）。
- **`*sql.DB` vs 外部 pool**：Go 的 `database/sql` 內建連線池管理，`SetMaxOpenConns` / `SetMaxIdleConns` / `SetConnMaxLifetime` 控制池行為。不需要額外的 pool 套件。

---

## Rust vs Go 對照表

| 面向 | Rust (sqlx 0.8 + tokio) | Go 1.24+ (database/sql + pgx) |
|------|--------------------------|-------------------------------|
| **遷移版本型別安全** | `MigrationPhase` 是 `enum`，編譯器強制窮舉 match。若新增 `PhaseVerify` 變體，所有未處理的 match 會在編譯期報錯，不可能遺漏。 | `MigrationPhase` 是 `string` 常數，型別系統無法防止傳入 `"invalid_phase"` 這類非法值。需靠 runtime validation 或 linter 規則補強。 |
| **Transaction 生命週期** | `pool.begin()` 回傳 `Transaction` 物件，Drop 時若未 commit 則自動 rollback（RAII 語義）。開發者即使忘記呼叫 commit/rollback，transaction 也不會懸空。 | `db.BeginTx()` 回傳 `*sql.Tx`，需手動 `tx.Commit()` 或 `tx.Rollback()`。若函式提前 return 而忘記 rollback，transaction 會一直持有連線直到 GC 回收——導致連線洩漏。需 `defer tx.Rollback()` 防禦。 |
| **錯誤處理** | `Result<T, sqlx::Error>` + `?` 運算子，錯誤必須處理否則無法編譯。每個可能失敗的 DB 操作都強制開發者面對錯誤路徑。 | `if err != nil { return err }` 慣例，但編譯器不強制檢查。可以 `db.ExecContext(ctx, sql)` 忽略 error return——lint 規則（`errcheck`）可以補強但非語言保證。 |
| **分批回填的非同步** | `tokio::time::sleep` 在 await 期間讓出 executor，不佔用 OS thread。搭配 `tokio::select!` 可同時監聽取消信號。高併發場景下資源效率更高。 | `time.Sleep` 阻塞 goroutine（但 goroutine 極輕量，通常不是瓶頸）。搭配 `select` + `ctx.Done()` 支援取消。語法更直觀，但缺乏編譯期的 Future 組合保證。 |
| **Query 結果映射** | `sqlx::Row::get::<Type, _>("column")` 需明確指定型別。使用 `query!` 宏可在編譯期驗證 SQL 語法和型別映射。 | `rows.Scan(&field1, &field2)` 按位置順序映射。欄位順序和數量必須與 SELECT 一致，錯位在 runtime 才爆錯。 |

---

## When to Use / 適用場景

- **Rolling Update / Canary 部署環境** — 當應用程式使用 rolling update 或 canary 部署時，多個版本的程式碼同時運行是常態。任何 schema 變更都必須與新舊版本相容，否則舊版 pod 會立刻崩潰。Expand-and-contract 模式確保每個階段的 schema 都同時相容當前和前一版本的程式碼。

- **高流量生產環境的大表變更** — 當表的記錄數超過千萬筆時，直接 `ALTER TABLE` 可能鎖表數分鐘。Online DDL 工具（gh-ost、pt-osc）或 PostgreSQL 的 `CREATE INDEX CONCURRENTLY` 讓 DDL 在不阻塞讀寫的情況下完成，維持服務可用性。

- **SLA 要求 99.9%+ 可用性的服務** — 對於 SLA 嚴格的關鍵服務（支付、訂單、認證），任何計劃性停機都不可接受。零停機 schema 遷移讓資料庫結構演進成為「常規操作」而非「需要維護窗口的特殊事件」。

- **微服務架構中的共享資料庫** — 當多個服務共享同一個資料庫（雖然不推薦，但現實中常見）時，schema 變更的影響範圍更大。Expand-and-contract 模式讓每個服務都有充足的時間適配新 schema。

---

## When NOT to Use / 不適用場景

- **初次上線前的 schema 建立** — 系統尚未上線、沒有流量時，不需要零停機遷移的複雜流程。直接執行 `CREATE TABLE` 即可。Expand-and-contract 的三階段流程在此場景下只是增加不必要的複雜度。

- **開發/測試環境** — 開發環境中可以直接 `DROP TABLE` + `CREATE TABLE`，不需要分階段遷移。測試環境通常在每次 CI 運行前重建 schema，零停機遷移的安全性保證在此毫無價值。

- **小型低流量應用** — 如果應用的流量極低（如每分鐘數十次請求）且可以接受數秒的短暫不可用，直接 `ALTER TABLE` 加上短暫的維護窗口（30 秒）比三階段遷移的工程複雜度更務實。

- **完全不可變的 schema** — 如果系統設計為 schema-on-read（如 NoSQL document store），或使用 event sourcing 且 events 是 append-only 的，則沒有 schema migration 的需求。

---

## Real-World Examples / 真實世界案例

### GitHub — gh-ost 的誕生

GitHub 是零停機 schema 遷移的先驅。他們的 MySQL 資料庫包含超過數百億筆記錄的表，任何鎖表操作都會影響數百萬使用者。最初使用 pt-online-schema-change，但觸發器帶來的效能開銷和偶發死鎖問題促使他們開發了 gh-ost。

gh-ost 的關鍵創新：
- **無觸發器**：改用 binlog 串流擷取增量變更，消除觸發器的效能開銷（約 10-30% 的寫入效能影響）和死鎖風險。
- **可控性**：支援動態調整 throttle 參數（`max-lag-millis`、`max-load`），DBA 可在遷移進行中調整速度。
- **可暫停/恢復**：遷移可以在任何時刻暫停並於稍後恢復，不需要從頭開始。
- **可測試**：提供 `--test-on-replica` 模式，先在 replica 上測試完整流程後再對 master 執行。

GitHub 的實際案例：對一張 2 億筆記錄的表進行 `ADD COLUMN`，gh-ost 耗時約 4 小時完成 rowcopy 和 cut-over，期間服務完全正常、零 downtime、對使用者不可見。

### Stripe — 安全的大規模 Schema 遷移

Stripe 處理全球支付，對資料一致性和可用性的要求極為嚴格。他們的 schema 遷移實踐：

- **強制 Expand-and-Contract**：所有 schema 變更必須分至少兩次 release 完成。團隊內部將此稱為「兩步遷移規則」——任何 migration PR 都必須標記屬於哪個階段。
- **遷移前後驗證腳本**：每個 migration 附帶驗證腳本，在 CI 中對 production clone 執行。驗證內容包括鎖等待時間、execution plan 變化、資料一致性。
- **自動化 Dual-Write**：Stripe 的 ORM 層內建 dual-write 支援。開發者在 schema 定義中標記「遷移中」的欄位，框架自動處理雙寫和讀取路由。
- **Shadow Traffic Verification**：遷移完成後，將 production 流量的副本導向使用新 schema 的測試環境，比對新舊讀取路徑的結果是否一致。

### Shopify — 大規模 MySQL 遷移

Shopify 的資料庫支撐全球數百萬商家，核心表達到數十億筆記錄。他們的經驗：

- **LHM (Large Hadron Migrator)**：Shopify 早期開發的 online schema change 工具，後來轉用 gh-ost。
- **分片策略**：將大表分片到多個 MySQL 實例，每個分片獨立遷移，降低單次遷移的影響範圍。
- **遷移排程**：大型遷移排在流量低谷（通常 UTC 凌晨）執行，但不要求完全沒有流量——仍然是零停機。
- **回滾演練**：每個 migration 的 rollback 在 staging 環境上預先演練，確認 rollback 可在 5 分鐘內完成。

---

## Interview Questions / 面試常見問題

**Q1：什麼是 Expand-and-Contract 模式？為什麼不能在一次 release 中完成 schema 變更？**

Expand-and-Contract 將破壞性的 schema 變更拆分為三個安全的階段：Expand（加入新元素）、Migrate（回填資料並切換讀寫）、Contract（刪除舊元素）。不能在一次 release 中完成的原因是 rolling update——在部署過程中，新舊版本的程式碼同時運行。如果一次性刪除舊欄位，舊版 pod 查詢該欄位時會立刻 500 error。如果一次性重新命名欄位，舊版讀舊名、新版讀新名，兩者至少有一個會失敗。三階段模式確保每個階段的 schema 都同時與新版和前一版的程式碼相容。

**Q2：在一張 5 億筆記錄的 MySQL 表上加索引，如何避免鎖表？**

有三種主要方案：(1) **gh-ost**：建立影子表 → 在影子表上 CREATE INDEX → binlog 同步增量 → rowcopy 既有資料 → 原子性 RENAME 切換。整個過程不取得長時間 metadata lock，只在最後的 cut-over 有極短暫的鎖（毫秒級）；(2) **pt-online-schema-change**：類似 gh-ost 但使用觸發器同步增量，有輕微的寫入效能影響；(3) **MySQL 8.0+ Online DDL**：`ALTER TABLE t ADD INDEX idx (col), ALGORITHM=INPLACE, LOCK=NONE`——InnoDB 原生支援部分 DDL 的 online 執行，但並非所有 DDL 都支援 INPLACE。選擇依據：表大小、寫入量、MySQL 版本、DBA 的工具熟悉度。

**Q3：如何安全地重新命名一個欄位（column rename）？**

安全的欄位重新命名需要三次 release：(1) **Release N**（Expand）：`ADD COLUMN new_name`，程式碼開始雙寫 `old_name` + `new_name`，啟動分批回填歷史資料到 `new_name`；(2) **Release N+1**（Migrate）：讀取切換至 `new_name`，驗證資料一致性（`COUNT WHERE new_name IS NULL AND old_name IS NOT NULL = 0`），停止寫入 `old_name`；(3) **Release N+2**（Contract）：確認所有 pod 都已升級，`DROP COLUMN old_name`。每個階段之間可以間隔數天，直到團隊確信安全為止。

**Q4：PostgreSQL 的 CREATE INDEX CONCURRENTLY 有什麼限制和風險？**

`CREATE INDEX CONCURRENTLY` 不取得排他鎖（使用 `ShareUpdateExclusiveLock`），允許建索引期間繼續讀寫。但有幾個風險：(1) 如果建索引過程中斷（如 OOM、手動取消），會留下 INVALID 索引，需手動 `DROP INDEX` 清理，否則會浪費寫入時的維護開銷且 query planner 不會使用它；(2) 建索引時間約為非 concurrent 方式的 2-3 倍；(3) 不能在 transaction block 中使用；(4) 建索引期間 autovacuum 無法清理死行，可能導致 table bloat；(5) 若 transaction ID wraparound 接近閾值，建索引可能被 cancel。

**Q5：Dual-Write 模式中如何確保新舊欄位的資料一致性？**

確保一致性的關鍵步驟：(1) 應用層同時寫入新舊欄位，確保每筆新寫入的資料在兩個欄位中一致；(2) 分批回填歷史資料，使用 `WHERE new_col IS NULL AND old_col IS NOT NULL` 條件找出待回填的行；(3) 回填完成後，執行一致性驗證查詢確認所有行的新舊欄位值相同；(4) 如果發現不一致（通常因為 race condition），需要再次回填並確保應用層的寫入邏輯正確處理了並發情況。最終目標是 `SELECT COUNT(*) WHERE new_col != old_col` 結果為 0。

---

## Pitfalls / 常見陷阱

### 1. 同一次 release 中執行 migration 並部署不相容的程式碼

```yaml
# 危險：同一次部署中刪除舊欄位 + 部署新程式碼
steps:
  - name: Run migration
    run: migrate up  # DROP COLUMN old_status
  - name: Deploy new version
    run: kubectl set image deployment/orders ...
# Rolling update 期間，舊版 pod 仍在 SELECT old_status → column not found → 500

# 正確：分三次 release 執行 expand-and-contract
# Release N:   ALTER TABLE ADD new_status; 雙寫 old + new; 回填
# Release N+1: 讀取切換至 new_status; 停止寫入 old_status
# Release N+2: ALTER TABLE DROP old_status（確認無舊版 pod）
```

### 2. 大表直接加 NOT NULL DEFAULT（MySQL < 8.0）

```sql
-- 危險：MySQL 5.7 對大表加 NOT NULL DEFAULT 需要重寫全表
ALTER TABLE orders ADD COLUMN priority INT NOT NULL DEFAULT 0;
-- 5 億筆 → 重寫全表 → metadata lock → 所有查詢排隊 → timeout 雪崩

-- 正確：分步驟執行
-- Step 1: 加 NULLABLE 欄位（MySQL 8.0+ INSTANT，不重寫表）
ALTER TABLE orders ADD COLUMN priority INT DEFAULT NULL;
-- Step 2: 分批回填
-- Step 3: 在應用層確保所有寫入都填入 priority
-- Step 4: 加 NOT NULL 約束
```

### 3. Rust 特有：sqlx Transaction 的 lifetime 與 async 互動

```rust
// 危險：在 transaction 內做長時間的非同步操作
// sqlx 的 Transaction 持有連線，長時間持有 = 連線池枯竭
async fn bad_migration(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    sqlx::query("ALTER TABLE orders ADD COLUMN new_col TEXT")
        .execute(&mut *tx)
        .await?;

    // 危險：在 transaction 內做回填——大表可能耗時數小時
    // 期間這條連線被 transaction 獨佔，連線池有效容量 -1
    for batch in 0..10000 {
        sqlx::query("UPDATE orders SET new_col = old_col WHERE id BETWEEN $1 AND $2")
            .bind(batch * 1000)
            .bind((batch + 1) * 1000)
            .execute(&mut *tx)
            .await?;
    }

    tx.commit().await?; // 數小時後才 commit
    Ok(())
}

// 正確：DDL 在 transaction 內，回填在 transaction 外
async fn good_migration(pool: &PgPool) -> Result<(), sqlx::Error> {
    // Step 1: DDL 在短 transaction 內
    let mut tx = pool.begin().await?;
    sqlx::query("ALTER TABLE orders ADD COLUMN new_col TEXT")
        .execute(&mut *tx)
        .await?;
    tx.commit().await?; // 毫秒級完成

    // Step 2: 回填在 transaction 外，每批獨立
    // 即使中斷也可以安全重新執行（冪等設計）
    loop {
        let result = sqlx::query(
            "UPDATE orders SET new_col = old_col WHERE new_col IS NULL LIMIT 1000"
        )
        .execute(pool)  // 使用 pool 而非 tx，每批獨立取連線
        .await?;

        if result.rows_affected() == 0 { break; }
        tokio::time::sleep(Duration::from_millis(100)).await;
    }
    Ok(())
}
```

### 4. Go 特有：忘記 defer rows.Close() 導致遷移期間連線洩漏

```go
// 危險：遷移驗證查詢忘記關閉 rows，連線洩漏
func verifyMigrationBad(db *sql.DB) error {
    rows, err := db.Query(
        "SELECT COUNT(*) FROM orders WHERE new_status IS NULL",
    )
    if err != nil {
        return err
    }
    // 忘記 defer rows.Close()！
    // rows 持有的連線不會歸還到連線池
    // 如果 verifyMigration 被多次呼叫（如每批回填後驗證），
    // 連線池逐漸枯竭 → 後續的 migration query timeout

    var count int
    if rows.Next() {
        rows.Scan(&count)
    }
    fmt.Printf("remaining null rows: %d\n", count)
    return nil
}

// 正確：使用 defer rows.Close()，或更好——用 QueryRow 取單一值
func verifyMigrationGood(db *sql.DB) error {
    var count int
    // QueryRow 自動關閉底層 rows，不需要手動管理
    err := db.QueryRow(
        "SELECT COUNT(*) FROM orders WHERE new_status IS NULL",
    ).Scan(&count)
    if err != nil {
        return fmt.Errorf("verify migration: %w", err)
    }
    fmt.Printf("remaining null rows: %d\n", count)
    return nil
}
```

### 5. 回填未設計為冪等操作

```sql
-- 危險：回填中途失敗後重新執行，部分行被重複處理
-- 如果 new_col 的值依賴計算（如 hash），重複計算可能與中間狀態衝突
UPDATE orders SET new_col = CONCAT(status, '_', id)
WHERE new_col IS NULL;
-- 若回填跑到一半失敗，部分行已設值，部分為 NULL
-- 重新執行時 WHERE new_col IS NULL 只處理剩餘的——這是正確的！
-- 但如果 WHERE 條件設計不當（如無條件更新），就會覆蓋已處理的行

-- 正確做法：回填的 WHERE 條件必須具備冪等性
-- 使用 "WHERE target IS NULL" 確保只處理未完成的行
-- 使用 "WHERE target != source" 確保只處理需要更新的行
```

### 6. 忽略 PostgreSQL 的 CREATE INDEX CONCURRENTLY 失敗後遺症

```sql
-- 危險：CREATE INDEX CONCURRENTLY 中途失敗後不清理
CREATE INDEX CONCURRENTLY idx_orders_status ON orders (status);
-- 若 OOM 或手動取消，索引狀態為 INVALID
-- INVALID 索引不會被 query planner 使用
-- 但每次 INSERT/UPDATE 仍然需要維護這個索引 → 白白浪費寫入效能

-- 檢查 INVALID 索引
SELECT indexrelid::regclass, indisvalid
FROM pg_index
WHERE NOT indisvalid;

-- 正確：失敗後清理 INVALID 索引再重試
DROP INDEX IF EXISTS idx_orders_status;
CREATE INDEX CONCURRENTLY idx_orders_status ON orders (status);
```

---

## Cross-references / 交叉引用

- [[../database/transactions|Database Transactions]](../database/transactions.md) — Schema 遷移必須尊重 transaction 邊界。DDL 在 PostgreSQL 中是 transactional 的（可以 ROLLBACK），但在 MySQL 中 DDL 會隱式 COMMIT 當前 transaction。了解 transaction 的行為是設計安全 migration 的前提。
- [[../database/postgres_lock_troubleshooting|PostgreSQL Lock Troubleshooting]](../database/postgres_lock_troubleshooting.md) — DDL 操作需要取得各種等級的鎖（AccessExclusiveLock、ShareLock 等）。不當的 DDL 會造成 lock contention，所有等待該鎖的查詢排隊，觸發連鎖的 timeout 和雪崩。理解 PostgreSQL 的鎖機制是執行安全 DDL 的關鍵。
- [[40_cicd_deployment|CI/CD & Deployment]](40_cicd_deployment.md) — Schema migration 必須整合到 CI/CD pipeline 中。最佳實踐是「先遷移、後部署」——CI pipeline 先執行 Expand 階段的 migration，驗證成功後再部署新版程式碼。Contract 階段的 migration 則在下一個 release cycle 中執行。

---

## References / 參考資料

1. **GitHub Engineering — gh-ost: GitHub's Online Schema Migration Tool** — (https://github.blog/engineering/infrastructure/gh-ost-github-s-online-schema-migration-tool-for-mysql/) gh-ost 的設計動機、架構、binlog 串流機制，以及與 pt-online-schema-change 的比較。
2. **Percona — pt-online-schema-change** — (https://docs.percona.com/percona-toolkit/pt-online-schema-change.html) MySQL online schema change 的經典工具，觸發器機制、使用限制和最佳實踐。
3. **PostgreSQL Documentation — ALTER TABLE** — (https://www.postgresql.org/docs/current/sql-altertable.html) PostgreSQL DDL 操作的官方文件，包含鎖等級、CONCURRENTLY 選項和 NOT VALID 約束。
4. **Martin Fowler — Evolutionary Database Design** — (https://martinfowler.com/articles/evodb.html) 資料庫演進設計的經典文章，expand-and-contract 模式的理論基礎。
5. **Stripe Engineering — Online Migrations at Scale** — (https://stripe.com/blog/online-migrations) Stripe 的大規模線上遷移實踐，dual-write 策略和四階段遷移流程。
6. **Skeema — Declarative MySQL Schema Management** — (https://www.skeema.io/) 聲明式 MySQL schema 管理工具，將 schema 定義為 SQL 檔案，自動生成安全的 ALTER 語句。
7. **Andrew Kane — Strong Migrations** — (https://github.com/ankane/strong_migrations) 檢測危險 migration 的 linter 工具（Ruby/Rails），其規則集（如禁止 `ADD COLUMN ... NOT NULL` 不帶 default）適用於所有語言。
8. **PlanetScale — Non-Blocking Schema Changes** — (https://planetscale.com/docs/concepts/nonblocking-schema-changes) PlanetScale（Vitess-based MySQL）的非阻塞 schema 變更機制，基於 gh-ost 但深度整合到 branching workflow。
