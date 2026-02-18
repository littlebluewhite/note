---
title: "Transactional Outbox Pattern / 交易式寄件匣模式"
note_type: knowledge
domain: backend
category: distributed_systems
tags: [backend, distributed-systems, go, rust, outbox, cdc, eventual-consistency, reliable-messaging]
created: 2026-02-18
updated: 2026-02-18
status: active
source: knowledge
series: backend
chapter: "59"
level: advanced
review_interval_days: 14
next_review: 2026-03-04
---

# Transactional Outbox Pattern / 交易式寄件匣模式

## Intent / 意圖

Transactional Outbox Pattern 解決微服務架構中最基本也最棘手的問題：**如何在更新資料庫的同時，可靠地發送事件到訊息佇列（如 Kafka），確保兩者的一致性——資料庫寫入和事件發佈要麼都成功，要麼都不發生？** 透過將事件寫入資料庫的 outbox 表（與業務寫入在同一個本地交易中），再由獨立的 publisher 程序讀取 outbox 表並發送事件到訊息佇列，實現原子性的「寫入 + 發佈」語義。

核心問題：**在沒有分散式交易的前提下，如何確保資料庫狀態變更和對外事件發佈的原子性，避免「資料庫寫入成功但事件發送失敗」或「事件發送成功但資料庫寫入被回滾」的不一致狀態？**

---

## Problem / 問題情境

**場景一：資料庫成功但事件遺失** — Order Service 在處理建立訂單的請求時，先將訂單寫入 `orders` 表，然後發送 `OrderCreated` 事件到 Kafka。某次資料庫寫入成功，但在發送 Kafka 訊息前，服務因 OOM 被 kill。訂單已存在於資料庫中，但 Inventory Service 從未收到 `OrderCreated` 事件，所以沒有扣減庫存。客戶下單成功，但庫存沒有減少。當另一個客戶購買同一商品時，系統允許購買（因為庫存顯示還有存貨），最終導致超賣。

```
1. BEGIN TRANSACTION
2. INSERT INTO orders (id, ...) VALUES (...)  ← 成功
3. COMMIT                                     ← 成功
4. kafka.produce("OrderCreated", ...)         ← 服務在此刻 crash，事件遺失！
```

**場景二：事件發送成功但資料庫回滾** — 有些團隊嘗試「先發事件、再寫資料庫」的順序。Order Service 先發送 `OrderCreated` 到 Kafka，再寫入資料庫。若資料庫寫入因唯一鍵衝突而失敗，但事件已經被 Inventory Service 消費——庫存被扣減了，但訂單根本不存在。

```
1. kafka.produce("OrderCreated", ...)         ← 成功，Inventory Service 已消費
2. BEGIN TRANSACTION
3. INSERT INTO orders (id, ...) VALUES (...)  ← 唯一鍵衝突，失敗！
4. ROLLBACK                                   ← 訂單不存在，但庫存已被扣減
```

**場景三：重複事件導致業務錯誤** — 團隊嘗試在資料庫交易內發送 Kafka 訊息。Kafka produce 成功（broker 已收到），但在收到 ack 前網路超時。應用程式認為發送失敗而重試，導致 `OrderCreated` 被發送兩次。Inventory Service 收到兩次 `OrderCreated`，扣了兩次庫存。

**場景四：分散式交易的效能災難** — 團隊考慮使用 2PC（Two-Phase Commit）同時提交資料庫和 Kafka。但 2PC 需要資料庫和 Kafka 都支援 XA transaction（Kafka 不支援 XA），且 2PC 在任一參與者不可用時會阻塞所有其他參與者——在微服務的規模下，這是不可接受的效能和可用性風險。

---

## Core Concepts / 核心概念

### Outbox Table / 寄件匣表

Outbox 表是一個特殊的資料庫表，用來暫存待發送的事件。它與業務表在同一個資料庫中，因此可以在**同一個本地交易（local transaction）**中同時寫入業務資料和事件記錄。

典型的 outbox 表結構：

```sql
CREATE TABLE outbox_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type  VARCHAR(255) NOT NULL,     -- 聚合根類型（如 'Order'）
    aggregate_id    VARCHAR(255) NOT NULL,     -- 聚合根 ID（如 order-123）
    event_type      VARCHAR(255) NOT NULL,     -- 事件類型（如 'OrderCreated'）
    payload         JSONB NOT NULL,            -- 事件資料（完整的事件內容）
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at    TIMESTAMPTZ,               -- 已發佈的時間戳（NULL 表示未發佈）
    retry_count     INT NOT NULL DEFAULT 0,    -- 重試次數
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING'  -- PENDING / PUBLISHED / FAILED
);

-- 索引：用於 polling publisher 查詢待發佈的事件
CREATE INDEX idx_outbox_pending ON outbox_events (status, created_at)
    WHERE status = 'PENDING';
```

### Polling Publisher / 輪詢發佈者

Polling Publisher 是一個獨立的程序（或 goroutine/tokio task），定期查詢 outbox 表中 `status = 'PENDING'` 的事件，將其發送到訊息佇列（Kafka/RabbitMQ），成功後將 status 更新為 `PUBLISHED`。

工作流程：
1. `SELECT * FROM outbox_events WHERE status = 'PENDING' ORDER BY created_at LIMIT 100`
2. 逐一（或批次）發送到 Kafka
3. 發送成功後 `UPDATE outbox_events SET status = 'PUBLISHED', published_at = NOW() WHERE id = ?`
4. 等待固定間隔（如 500ms）後重複

優點：簡單、不需要額外的基礎設施。
缺點：有延遲（polling interval）、對資料庫有額外的查詢負載。

### CDC（Change Data Capture）/ 變更資料擷取

CDC 是一種透過讀取資料庫的交易日誌（transaction log / WAL）來捕獲資料變更的技術。當 outbox 表有新的 INSERT 時，CDC 工具（如 Debezium）立即擷取到這個變更並轉發到 Kafka。

相比 Polling Publisher，CDC 的優勢：
- **低延遲**：事件在毫秒內被捕獲和轉發，不需要等待 polling interval
- **零查詢負載**：直接讀取 WAL，不對資料庫表執行 SELECT 查詢
- **保序**：WAL 中的事件順序與交易提交順序一致

主流 CDC 工具：
- **Debezium**：開源，支援 PostgreSQL、MySQL、MongoDB、SQL Server，與 Kafka Connect 整合
- **AWS DMS**：AWS 的 Database Migration Service，也支援 CDC 模式
- **Maxwell**：專為 MySQL 設計的 CDC 工具

### Exactly-Once Semantics / 恰好一次語義

在 outbox pattern 中，「恰好一次」是由兩個機制共同保證的：

1. **At-Least-Once Delivery（至少一次傳遞）**：Polling Publisher 或 CDC 確保每個 outbox 事件最終都會被發送到 Kafka——即使中途失敗，重試機制會再次嘗試
2. **Idempotent Consumer（冪等消費者）**：接收端（consumer）利用事件的唯一 ID（`outbox_events.id`）進行去重——若已處理過相同 ID 的事件，則跳過

At-Least-Once + Idempotent Consumer = Effectively Exactly-Once

### Outbox + Saga 整合

在 Saga pattern 中，每個參與者（participant）需要：(1) 處理收到的 command/event；(2) 更新自己的資料；(3) 發送下一步的 command/event。步驟 (2) 和 (3) 正是 outbox pattern 解決的問題——將資料更新和事件發佈放在同一個本地交易中。

```
OrderService:  INSERT order + INSERT outbox(OrderCreated)  ← 同一交易
    ↓ (Kafka)
InventoryService:  UPDATE inventory + INSERT outbox(InventoryReserved)  ← 同一交易
    ↓ (Kafka)
PaymentService:  INSERT payment + INSERT outbox(PaymentProcessed)  ← 同一交易
```

### Ordering Guarantees / 順序保證

Outbox pattern 的事件順序保證取決於實作方式：

- **Polling Publisher**：`ORDER BY created_at` 確保按寫入順序發佈。但如果使用多個 publisher 實例，不同實例可能發佈不同事件，跨實例的順序無法保證
- **CDC**：WAL 的順序與交易提交順序一致，天然保序。Debezium 預設將同一 `aggregate_id` 的事件發送到 Kafka 的同一 partition，確保同一聚合根的事件按序處理

---

## Architecture / 架構

### Outbox Pattern 整體架構

```mermaid
flowchart TB
    subgraph OrderService["Order Service"]
        API["API Handler"]
        DB["PostgreSQL"]

        subgraph Transaction["本地交易 (Local Transaction)"]
            T1["INSERT INTO orders"]
            T2["INSERT INTO outbox_events"]
        end

        API --> Transaction
        Transaction --> DB
    end

    subgraph Publisher["事件發佈"]
        PP["Polling Publisher<br/>(定期查詢 outbox)"]
        CDC["CDC / Debezium<br/>(讀取 WAL)"]
    end

    subgraph MQ["訊息佇列"]
        KAFKA["Kafka Topic:<br/>order-events"]
    end

    subgraph Consumers["消費者服務"]
        INV["Inventory Service<br/>(冪等消費)"]
        PAY["Payment Service<br/>(冪等消費)"]
        NOTIFY["Notification Service<br/>(冪等消費)"]
    end

    DB -->|"SELECT pending events"| PP
    DB -->|"讀取 WAL"| CDC
    PP -->|"produce"| KAFKA
    CDC -->|"produce"| KAFKA
    KAFKA --> INV & PAY & NOTIFY

    style Transaction fill:#4a9eff,stroke:#333,color:#fff
    style DB fill:#ff9800,stroke:#333,color:#fff
    style KAFKA fill:#9c27b0,stroke:#333,color:#fff
    style PP fill:#4caf50,stroke:#333,color:#fff
    style CDC fill:#00bcd4,stroke:#333,color:#fff
```

### Polling Publisher vs CDC 比較

```mermaid
flowchart LR
    subgraph Polling["Polling Publisher 模式"]
        direction TB
        PDB["outbox_events 表"]
        PPub["Polling Publisher"]
        PK["Kafka"]

        PDB -->|"每 500ms SELECT<br/>WHERE status=PENDING"| PPub
        PPub -->|"produce event"| PK
        PPub -->|"UPDATE status=PUBLISHED"| PDB
    end

    subgraph CDCMode["CDC 模式 (Debezium)"]
        direction TB
        CDB["outbox_events 表"]
        WAL["PostgreSQL WAL<br/>(Write-Ahead Log)"]
        DEB["Debezium<br/>Connector"]
        CK["Kafka"]

        CDB -->|"交易提交"| WAL
        WAL -->|"串流讀取<br/>低延遲"| DEB
        DEB -->|"produce event"| CK
    end

    style PDB fill:#ff9800,stroke:#333,color:#fff
    style PPub fill:#4caf50,stroke:#333,color:#fff
    style CDB fill:#ff9800,stroke:#333,color:#fff
    style WAL fill:#9c27b0,stroke:#333,color:#fff
    style DEB fill:#00bcd4,stroke:#333,color:#fff
```

### 冪等消費者流程

```mermaid
sequenceDiagram
    participant Kafka
    participant Consumer as Inventory Service
    participant DB as Inventory DB
    participant Processed as processed_events 表

    Kafka->>Consumer: OrderCreated (event_id: evt-001)

    Consumer->>Processed: SELECT id FROM processed_events<br/>WHERE event_id = 'evt-001'
    Processed-->>Consumer: 不存在（首次處理）

    Consumer->>DB: BEGIN TRANSACTION
    Consumer->>DB: UPDATE inventory SET stock = stock - 1
    Consumer->>Processed: INSERT INTO processed_events (event_id)
    Consumer->>DB: COMMIT
    Consumer->>Kafka: ACK offset

    Note over Kafka,Consumer: --- 重複投遞（如 rebalance 後）---

    Kafka->>Consumer: OrderCreated (event_id: evt-001)
    Consumer->>Processed: SELECT id FROM processed_events<br/>WHERE event_id = 'evt-001'
    Processed-->>Consumer: 已存在（重複事件）
    Consumer->>Kafka: ACK offset（跳過處理）
```

### Outbox + Saga 整合流程

```mermaid
flowchart LR
    subgraph Step1["步驟 1: Order Service"]
        O1["INSERT order<br/>+ INSERT outbox<br/>(OrderCreated)"]
    end

    subgraph Step2["步驟 2: Inventory Service"]
        O2["UPDATE inventory<br/>+ INSERT outbox<br/>(InventoryReserved)"]
    end

    subgraph Step3["步驟 3: Payment Service"]
        O3["INSERT payment<br/>+ INSERT outbox<br/>(PaymentProcessed)"]
    end

    subgraph Step4["步驟 4: Order Service"]
        O4["UPDATE order status<br/>= CONFIRMED"]
    end

    K1["Kafka"]
    K2["Kafka"]
    K3["Kafka"]

    Step1 -->|"outbox → publish"| K1
    K1 --> Step2
    Step2 -->|"outbox → publish"| K2
    K2 --> Step3
    Step3 -->|"outbox → publish"| K3
    K3 --> Step4

    style O1 fill:#4a9eff,stroke:#333,color:#fff
    style O2 fill:#ff9800,stroke:#333,color:#fff
    style O3 fill:#9c27b0,stroke:#333,color:#fff
    style O4 fill:#4caf50,stroke:#333,color:#fff
```

---

## How It Works / 運作原理

Transactional Outbox Pattern 的核心原理是**利用本地資料庫交易的 ACID 保證來實現業務寫入和事件記錄的原子性**，再由非同步的 publisher 將事件可靠地傳遞到訊息佇列。

1. **業務請求進入**：API handler 收到建立訂單的請求。

2. **開啟本地交易**：在同一個資料庫交易（`BEGIN TRANSACTION`）中執行兩個操作：
   - 寫入業務表：`INSERT INTO orders (id, user_id, total, status) VALUES (...)`
   - 寫入 outbox 表：`INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload) VALUES ('Order', 'order-123', 'OrderCreated', '{...}')`

3. **提交交易**：`COMMIT`。因為兩個 INSERT 在同一個交易中，要麼都成功，要麼都失敗。不會出現「訂單存在但事件不存在」的不一致狀態。

4. **事件發佈（Polling Publisher 路徑）**：
   - 獨立的 polling task 每隔 N 毫秒查詢：`SELECT * FROM outbox_events WHERE status = 'PENDING' ORDER BY created_at LIMIT 100`
   - 對每個事件，呼叫 Kafka producer 發送到對應的 topic
   - 發送成功後更新：`UPDATE outbox_events SET status = 'PUBLISHED', published_at = NOW() WHERE id = ?`
   - 若發送失敗（Kafka 不可用），增加 retry_count 並在下次 polling 時重試
   - 超過最大重試次數的事件標記為 `FAILED`，觸發告警

5. **事件發佈（CDC 路徑）**：
   - Debezium connector 持續讀取 PostgreSQL 的 WAL（Write-Ahead Log）
   - 當偵測到 `outbox_events` 表的 INSERT 時，Debezium 將變更事件轉發到 Kafka
   - Debezium 的 outbox event router（`io.debezium.transforms.outbox.EventRouter`）會根據 `aggregate_type` 和 `event_type` 將事件路由到正確的 Kafka topic
   - 事件發佈後，可選擇性地從 outbox 表刪除已發佈的記錄（減少表膨脹）

6. **消費端冪等處理**：
   - Consumer 收到事件後，先檢查 `processed_events` 表中是否已存在該 `event_id`
   - 若已存在，表示是重複投遞，直接 ACK 並跳過
   - 若不存在，在同一個本地交易中：(a) 執行業務邏輯（如扣減庫存）；(b) 記錄 `event_id` 到 `processed_events` 表
   - COMMIT 後 ACK Kafka offset

7. **清理機制**：定期清理已發佈或已過期的 outbox 事件（如保留 7 天），防止 outbox 表無限膨脹。

---

## Rust 實作

以下展示完整的 outbox pattern 實作：業務寫入 + outbox 寫入在同一交易中，polling publisher 非同步發佈事件。

```rust
// src/main.rs
// Transactional Outbox Pattern — Axum 0.8 + sqlx + tokio

use axum::{
    extract::State,
    http::StatusCode,
    routing::{get, post},
    Json, Router,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::{postgres::PgPoolOptions, PgPool, Row};
use std::sync::Arc;
use std::time::Duration;
use tokio::net::TcpListener;
use uuid::Uuid;

// ============================================================
// 資料模型
// ============================================================

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
struct Order {
    id: Uuid,
    user_id: String,
    product_id: String,
    quantity: i32,
    total_amount: f64,
    status: String,
    created_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
struct CreateOrderRequest {
    user_id: String,
    product_id: String,
    quantity: i32,
    total_amount: f64,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
struct OutboxEvent {
    id: Uuid,
    aggregate_type: String,
    aggregate_id: String,
    event_type: String,
    payload: serde_json::Value,
    created_at: DateTime<Utc>,
    published_at: Option<DateTime<Utc>>,
    retry_count: i32,
    status: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct OrderCreatedPayload {
    order_id: String,
    user_id: String,
    product_id: String,
    quantity: i32,
    total_amount: f64,
    timestamp: DateTime<Utc>,
}

// ============================================================
// 應用狀態
// ============================================================

#[derive(Clone)]
struct AppState {
    pool: PgPool,
}

// ============================================================
// 資料庫初始化
// ============================================================

async fn initialize_database(pool: &PgPool) {
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS orders (
            id              UUID PRIMARY KEY,
            user_id         VARCHAR(255) NOT NULL,
            product_id      VARCHAR(255) NOT NULL,
            quantity        INT NOT NULL,
            total_amount    DOUBLE PRECISION NOT NULL,
            status          VARCHAR(50) NOT NULL DEFAULT 'CREATED',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS outbox_events (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            aggregate_type  VARCHAR(255) NOT NULL,
            aggregate_id    VARCHAR(255) NOT NULL,
            event_type      VARCHAR(255) NOT NULL,
            payload         JSONB NOT NULL,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            published_at    TIMESTAMPTZ,
            retry_count     INT NOT NULL DEFAULT 0,
            status          VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        );

        CREATE INDEX IF NOT EXISTS idx_outbox_pending
            ON outbox_events (status, created_at)
            WHERE status = 'PENDING';
        "#,
    )
    .execute(pool)
    .await
    .expect("資料庫初始化失敗");
}

// ============================================================
// 建立訂單（業務寫入 + outbox 寫入在同一交易中）
// ============================================================

async fn create_order(
    State(state): State<AppState>,
    Json(request): Json<CreateOrderRequest>,
) -> Result<(StatusCode, Json<Order>), (StatusCode, String)> {
    let order_id = Uuid::new_v4();
    let now = Utc::now();

    // 建構 outbox 事件 payload
    let event_payload = serde_json::to_value(OrderCreatedPayload {
        order_id: order_id.to_string(),
        user_id: request.user_id.clone(),
        product_id: request.product_id.clone(),
        quantity: request.quantity,
        total_amount: request.total_amount,
        timestamp: now,
    })
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    // ============================================================
    // 關鍵：同一個交易中寫入 orders 和 outbox_events
    // ============================================================
    let mut tx = state
        .pool
        .begin()
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    // 步驟 1：寫入業務表
    sqlx::query(
        r#"
        INSERT INTO orders (id, user_id, product_id, quantity, total_amount, status, created_at)
        VALUES ($1, $2, $3, $4, $5, 'CREATED', $6)
        "#,
    )
    .bind(order_id)
    .bind(&request.user_id)
    .bind(&request.product_id)
    .bind(request.quantity)
    .bind(request.total_amount)
    .bind(now)
    .execute(&mut *tx)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    // 步驟 2：寫入 outbox 事件表（同一交易）
    sqlx::query(
        r#"
        INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload)
        VALUES ('Order', $1, 'OrderCreated', $2)
        "#,
    )
    .bind(order_id.to_string())
    .bind(&event_payload)
    .execute(&mut *tx)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    // 步驟 3：提交交易 — 兩個 INSERT 要麼都成功，要麼都失敗
    tx.commit()
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let order = Order {
        id: order_id,
        user_id: request.user_id,
        product_id: request.product_id,
        quantity: request.quantity,
        total_amount: request.total_amount,
        status: "CREATED".to_string(),
        created_at: now,
    };

    println!(
        "訂單建立成功: {} (outbox 事件已寫入，等待發佈)",
        order_id
    );
    Ok((StatusCode::CREATED, Json(order)))
}

// ============================================================
// 查詢待發佈事件（供除錯使用）
// ============================================================

async fn get_pending_events(
    State(state): State<AppState>,
) -> Result<Json<Vec<OutboxEvent>>, (StatusCode, String)> {
    let events = sqlx::query_as::<_, OutboxEvent>(
        "SELECT * FROM outbox_events WHERE status = 'PENDING' ORDER BY created_at LIMIT 50",
    )
    .fetch_all(&state.pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(events))
}

// ============================================================
// Polling Publisher — 非同步任務，定期發佈 outbox 事件
// ============================================================

/// 模擬 Kafka producer — 生產環境應使用 rdkafka crate
async fn publish_to_kafka(event: &OutboxEvent) -> Result<(), String> {
    // 模擬發送到 Kafka（生產環境使用 rdkafka::producer::FutureProducer）
    println!(
        "  [Kafka] 發佈事件: topic={}, key={}, type={}, payload_size={}",
        format!("{}-events", event.aggregate_type.to_lowercase()),
        event.aggregate_id,
        event.event_type,
        event.payload.to_string().len()
    );

    // 模擬偶爾的發佈失敗
    // if rand::random::<f64>() < 0.1 { return Err("Kafka 暫時不可用".to_string()); }

    Ok(())
}

/// Polling Publisher 主迴圈
async fn polling_publisher(pool: PgPool, poll_interval: Duration, batch_size: i64) {
    println!(
        "Polling Publisher 啟動（間隔: {:?}, 批次大小: {}）",
        poll_interval, batch_size
    );

    let max_retries = 5;

    loop {
        // 查詢待發佈的事件
        let events = match sqlx::query_as::<_, OutboxEvent>(
            r#"
            SELECT * FROM outbox_events
            WHERE status = 'PENDING' AND retry_count < $1
            ORDER BY created_at
            LIMIT $2
            FOR UPDATE SKIP LOCKED
            "#,
        )
        .bind(max_retries)
        .bind(batch_size)
        .fetch_all(&pool)
        .await
        {
            Ok(events) => events,
            Err(e) => {
                eprintln!("查詢 outbox 事件失敗: {}", e);
                tokio::time::sleep(poll_interval).await;
                continue;
            }
        };

        if !events.is_empty() {
            println!("Polling Publisher: 發現 {} 個待發佈事件", events.len());
        }

        for event in &events {
            match publish_to_kafka(event).await {
                Ok(()) => {
                    // 發佈成功：更新狀態為 PUBLISHED
                    if let Err(e) = sqlx::query(
                        r#"
                        UPDATE outbox_events
                        SET status = 'PUBLISHED', published_at = NOW()
                        WHERE id = $1
                        "#,
                    )
                    .bind(event.id)
                    .execute(&pool)
                    .await
                    {
                        eprintln!("更新 outbox 狀態失敗: {}", e);
                    }
                }
                Err(e) => {
                    // 發佈失敗：增加重試次數
                    eprintln!(
                        "事件 {} 發佈失敗（第 {} 次）: {}",
                        event.id,
                        event.retry_count + 1,
                        e
                    );

                    let new_status = if event.retry_count + 1 >= max_retries {
                        "FAILED" // 超過最大重試次數，標記為失敗
                    } else {
                        "PENDING" // 仍可重試
                    };

                    let _ = sqlx::query(
                        r#"
                        UPDATE outbox_events
                        SET retry_count = retry_count + 1, status = $1
                        WHERE id = $2
                        "#,
                    )
                    .bind(new_status)
                    .bind(event.id)
                    .execute(&pool)
                    .await;
                }
            }
        }

        tokio::time::sleep(poll_interval).await;
    }
}

// ============================================================
// 健康檢查
// ============================================================

async fn health_check(State(state): State<AppState>) -> Json<serde_json::Value> {
    let pending_count: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM outbox_events WHERE status = 'PENDING'",
    )
    .fetch_one(&state.pool)
    .await
    .unwrap_or(0);

    Json(serde_json::json!({
        "status": "healthy",
        "pending_outbox_events": pending_count,
    }))
}

// ============================================================
// 主程式
// ============================================================

#[tokio::main]
async fn main() {
    let database_url =
        std::env::var("DATABASE_URL").unwrap_or_else(|_| {
            "postgres://postgres:password@localhost:5432/orders".to_string()
        });

    let pool = PgPoolOptions::new()
        .max_connections(20)
        .connect(&database_url)
        .await
        .expect("無法連接資料庫");

    initialize_database(&pool).await;

    let state = AppState { pool: pool.clone() };

    // 啟動 Polling Publisher（背景任務）
    let publisher_pool = pool.clone();
    tokio::spawn(async move {
        polling_publisher(
            publisher_pool,
            Duration::from_millis(500), // 每 500ms 查詢一次
            100,                        // 每次最多處理 100 個事件
        )
        .await;
    });

    let app = Router::new()
        .route("/health", get(health_check))
        .route("/api/orders", post(create_order))
        .route("/api/outbox/pending", get(get_pending_events))
        .with_state(state);

    let addr = "0.0.0.0:8080";
    println!("Order Service 啟動於 {}", addr);

    let listener = TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

// Output:
// Order Service 啟動於 0.0.0.0:8080
// Polling Publisher 啟動（間隔: 500ms, 批次大小: 100）
// (curl -X POST http://localhost:8080/api/orders -H "Content-Type: application/json"
//   -d '{"user_id":"u-1","product_id":"p-1","quantity":2,"total_amount":99.99}')
// 訂單建立成功: 550e8400-... (outbox 事件已寫入，等待發佈)
// Polling Publisher: 發現 1 個待發佈事件
//   [Kafka] 發佈事件: topic=order-events, key=550e8400-..., type=OrderCreated, payload_size=156
```

### Cargo.toml

```toml
[package]
name = "outbox-service"
version = "0.1.0"
edition = "2024"

[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
sqlx = { version = "0.8", features = ["runtime-tokio", "postgres", "chrono", "uuid"] }
uuid = { version = "1", features = ["v4", "serde"] }
chrono = { version = "0.4", features = ["serde"] }
```

---

## Go 實作

```go
// main.go
// Transactional Outbox Pattern — Go 1.24+ 標準庫 + database/sql

package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/google/uuid"
	_ "github.com/lib/pq"
)

// ============================================================
// 資料模型
// ============================================================

// Order 訂單結構
type Order struct {
	ID          string    `json:"id"`
	UserID      string    `json:"user_id"`
	ProductID   string    `json:"product_id"`
	Quantity    int       `json:"quantity"`
	TotalAmount float64   `json:"total_amount"`
	Status      string    `json:"status"`
	CreatedAt   time.Time `json:"created_at"`
}

// CreateOrderRequest 建立訂單請求
type CreateOrderRequest struct {
	UserID      string  `json:"user_id"`
	ProductID   string  `json:"product_id"`
	Quantity    int     `json:"quantity"`
	TotalAmount float64 `json:"total_amount"`
}

// OutboxEvent outbox 事件結構
type OutboxEvent struct {
	ID            string     `json:"id"`
	AggregateType string     `json:"aggregate_type"`
	AggregateID   string     `json:"aggregate_id"`
	EventType     string     `json:"event_type"`
	Payload       string     `json:"payload"`
	CreatedAt     time.Time  `json:"created_at"`
	PublishedAt   *time.Time `json:"published_at"`
	RetryCount    int        `json:"retry_count"`
	Status        string     `json:"status"`
}

// OrderCreatedPayload OrderCreated 事件的 payload
type OrderCreatedPayload struct {
	OrderID     string    `json:"order_id"`
	UserID      string    `json:"user_id"`
	ProductID   string    `json:"product_id"`
	Quantity    int       `json:"quantity"`
	TotalAmount float64   `json:"total_amount"`
	Timestamp   time.Time `json:"timestamp"`
}

// ============================================================
// 應用程式
// ============================================================

// App 封裝應用狀態
type App struct {
	db *sql.DB
}

// NewApp 建立新的應用實例
func NewApp(db *sql.DB) *App {
	return &App{db: db}
}

// InitDatabase 初始化資料庫表
func (app *App) InitDatabase(ctx context.Context) error {
	query := `
	CREATE TABLE IF NOT EXISTS orders (
		id              UUID PRIMARY KEY,
		user_id         VARCHAR(255) NOT NULL,
		product_id      VARCHAR(255) NOT NULL,
		quantity        INT NOT NULL,
		total_amount    DOUBLE PRECISION NOT NULL,
		status          VARCHAR(50) NOT NULL DEFAULT 'CREATED',
		created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
	);

	CREATE TABLE IF NOT EXISTS outbox_events (
		id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
		aggregate_type  VARCHAR(255) NOT NULL,
		aggregate_id    VARCHAR(255) NOT NULL,
		event_type      VARCHAR(255) NOT NULL,
		payload         JSONB NOT NULL,
		created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		published_at    TIMESTAMPTZ,
		retry_count     INT NOT NULL DEFAULT 0,
		status          VARCHAR(20) NOT NULL DEFAULT 'PENDING'
	);

	CREATE INDEX IF NOT EXISTS idx_outbox_pending
		ON outbox_events (status, created_at)
		WHERE status = 'PENDING';
	`
	_, err := app.db.ExecContext(ctx, query)
	return err
}

// ============================================================
// 建立訂單（業務寫入 + outbox 寫入在同一交易中）
// ============================================================

// CreateOrder 在同一個資料庫交易中寫入訂單和 outbox 事件
func (app *App) CreateOrder(ctx context.Context, req CreateOrderRequest) (*Order, error) {
	orderID := uuid.New().String()
	now := time.Now().UTC()

	// 建構 outbox 事件 payload
	payload := OrderCreatedPayload{
		OrderID:     orderID,
		UserID:      req.UserID,
		ProductID:   req.ProductID,
		Quantity:    req.Quantity,
		TotalAmount: req.TotalAmount,
		Timestamp:   now,
	}
	payloadJSON, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("序列化 payload 失敗: %w", err)
	}

	// ============================================================
	// 關鍵：同一個交易中寫入 orders 和 outbox_events
	// ============================================================
	tx, err := app.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("開啟交易失敗: %w", err)
	}
	defer tx.Rollback() // 若未 Commit，自動 Rollback

	// 步驟 1：寫入業務表
	_, err = tx.ExecContext(ctx,
		`INSERT INTO orders (id, user_id, product_id, quantity, total_amount, status, created_at)
		 VALUES ($1, $2, $3, $4, $5, 'CREATED', $6)`,
		orderID, req.UserID, req.ProductID, req.Quantity, req.TotalAmount, now,
	)
	if err != nil {
		return nil, fmt.Errorf("寫入訂單失敗: %w", err)
	}

	// 步驟 2：寫入 outbox 事件表（同一交易）
	_, err = tx.ExecContext(ctx,
		`INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload)
		 VALUES ('Order', $1, 'OrderCreated', $2)`,
		orderID, payloadJSON,
	)
	if err != nil {
		return nil, fmt.Errorf("寫入 outbox 事件失敗: %w", err)
	}

	// 步驟 3：提交交易 — 兩個 INSERT 要麼都成功，要麼都失敗
	if err := tx.Commit(); err != nil {
		return nil, fmt.Errorf("提交交易失敗: %w", err)
	}

	order := &Order{
		ID:          orderID,
		UserID:      req.UserID,
		ProductID:   req.ProductID,
		Quantity:    req.Quantity,
		TotalAmount: req.TotalAmount,
		Status:      "CREATED",
		CreatedAt:   now,
	}

	log.Printf("訂單建立成功: %s (outbox 事件已寫入，等待發佈)", orderID)
	return order, nil
}

// ============================================================
// Polling Publisher — goroutine，定期發佈 outbox 事件
// ============================================================

// publishToKafka 模擬發送到 Kafka
func publishToKafka(event *OutboxEvent) error {
	log.Printf("  [Kafka] 發佈事件: topic=%s-events, key=%s, type=%s",
		event.AggregateType, event.AggregateID, event.EventType)
	return nil
}

// PollingPublisher 定期查詢 outbox 表並發佈事件
func (app *App) PollingPublisher(ctx context.Context, pollInterval time.Duration, batchSize int) {
	log.Printf("Polling Publisher 啟動（間隔: %v, 批次大小: %d）", pollInterval, batchSize)

	maxRetries := 5
	ticker := time.NewTicker(pollInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			log.Println("Polling Publisher 收到停止信號，退出")
			return
		case <-ticker.C:
			app.publishBatch(ctx, batchSize, maxRetries)
		}
	}
}

func (app *App) publishBatch(ctx context.Context, batchSize, maxRetries int) {
	// 使用 FOR UPDATE SKIP LOCKED 避免多個 publisher 實例處理同一事件
	rows, err := app.db.QueryContext(ctx,
		`SELECT id, aggregate_type, aggregate_id, event_type, payload,
		        created_at, published_at, retry_count, status
		 FROM outbox_events
		 WHERE status = 'PENDING' AND retry_count < $1
		 ORDER BY created_at
		 LIMIT $2
		 FOR UPDATE SKIP LOCKED`,
		maxRetries, batchSize,
	)
	if err != nil {
		log.Printf("查詢 outbox 事件失敗: %v", err)
		return
	}
	defer rows.Close()

	var events []*OutboxEvent
	for rows.Next() {
		var event OutboxEvent
		err := rows.Scan(
			&event.ID, &event.AggregateType, &event.AggregateID,
			&event.EventType, &event.Payload, &event.CreatedAt,
			&event.PublishedAt, &event.RetryCount, &event.Status,
		)
		if err != nil {
			log.Printf("掃描 outbox 事件失敗: %v", err)
			continue
		}
		events = append(events, &event)
	}

	if len(events) > 0 {
		log.Printf("Polling Publisher: 發現 %d 個待發佈事件", len(events))
	}

	for _, event := range events {
		if err := publishToKafka(event); err != nil {
			// 發佈失敗：增加重試次數
			log.Printf("事件 %s 發佈失敗（第 %d 次）: %v",
				event.ID, event.RetryCount+1, err)

			newStatus := "PENDING"
			if event.RetryCount+1 >= maxRetries {
				newStatus = "FAILED"
			}

			app.db.ExecContext(ctx,
				`UPDATE outbox_events SET retry_count = retry_count + 1, status = $1 WHERE id = $2`,
				newStatus, event.ID,
			)
		} else {
			// 發佈成功：更新狀態
			app.db.ExecContext(ctx,
				`UPDATE outbox_events SET status = 'PUBLISHED', published_at = NOW() WHERE id = $1`,
				event.ID,
			)
		}
	}
}

// ============================================================
// HTTP Handlers
// ============================================================

func (app *App) handleCreateOrder(w http.ResponseWriter, r *http.Request) {
	var req CreateOrderRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"error":"invalid request body"}`, http.StatusBadRequest)
		return
	}

	order, err := app.CreateOrder(r.Context(), req)
	if err != nil {
		http.Error(w, fmt.Sprintf(`{"error":"%s"}`, err.Error()), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(order)
}

func (app *App) handleHealthCheck(w http.ResponseWriter, r *http.Request) {
	var pendingCount int
	app.db.QueryRowContext(r.Context(),
		"SELECT COUNT(*) FROM outbox_events WHERE status = 'PENDING'",
	).Scan(&pendingCount)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]any{
		"status":                "healthy",
		"pending_outbox_events": pendingCount,
	})
}

// ============================================================
// 主程式
// ============================================================

func main() {
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		dbURL = "postgres://postgres:password@localhost:5432/orders?sslmode=disable"
	}

	db, err := sql.Open("postgres", dbURL)
	if err != nil {
		log.Fatalf("無法連接資料庫: %v", err)
	}
	defer db.Close()

	db.SetMaxOpenConns(20)
	db.SetMaxIdleConns(10)
	db.SetConnMaxLifetime(5 * time.Minute)

	app := NewApp(db)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	if err := app.InitDatabase(ctx); err != nil {
		log.Fatalf("資料庫初始化失敗: %v", err)
	}

	// 啟動 Polling Publisher（背景 goroutine）
	go app.PollingPublisher(ctx, 500*time.Millisecond, 100)

	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", app.handleHealthCheck)
	mux.HandleFunc("POST /api/orders", app.handleCreateOrder)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	server := &http.Server{
		Addr:    ":" + port,
		Handler: mux,
	}

	// 優雅關閉
	shutdownCh := make(chan os.Signal, 1)
	signal.Notify(shutdownCh, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		log.Printf("Order Service 啟動於 :%s\n", port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("啟動失敗: %v\n", err)
		}
	}()

	<-shutdownCh
	log.Println("收到停止信號，開始優雅關閉...")
	cancel() // 停止 Polling Publisher

	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer shutdownCancel()

	server.Shutdown(shutdownCtx)
	log.Println("Order Service 已關閉")
}

// Output:
// 2026/02/18 10:00:00 Order Service 啟動於 :8080
// 2026/02/18 10:00:00 Polling Publisher 啟動（間隔: 500ms, 批次大小: 100）
// (curl -X POST http://localhost:8080/api/orders -H "Content-Type: application/json"
//   -d '{"user_id":"u-1","product_id":"p-1","quantity":2,"total_amount":99.99}')
// 2026/02/18 10:00:05 訂單建立成功: 550e8400-... (outbox 事件已寫入，等待發佈)
// 2026/02/18 10:00:05 Polling Publisher: 發現 1 個待發佈事件
// 2026/02/18 10:00:05   [Kafka] 發佈事件: topic=Order-events, key=550e8400-..., type=OrderCreated
```

---

## Rust vs Go 對照表

| 比較維度 | Rust | Go |
|---------|------|-----|
| **資料庫交易 API** | `sqlx` 的 `pool.begin()` 回傳 `Transaction`，所有操作傳入 `&mut *tx`，compile time 確保交易正確使用 | `sql.DB.BeginTx()` 回傳 `*sql.Tx`，需手動 `defer tx.Rollback()` + 最後 `tx.Commit()`，遺漏 rollback 是常見 bug |
| **JSON 序列化** | `serde_json::to_value` 回傳 `Result`，型別不匹配在編譯期捕獲 | `json.Marshal` 回傳 `([]byte, error)`，運行時才發現序列化問題 |
| **背景任務** | `tokio::spawn` 啟動非同步 task，透過 `CancellationToken` 或 `select!` 優雅停止 | `go func()` 啟動 goroutine，透過 `context.WithCancel` 優雅停止 |
| **並發安全** | 編譯器透過 ownership + `Send`/`Sync` trait 保證不會有 data race | 需要 `sync.Mutex` 或 channel，`-race` flag 在運行時檢測 |
| **錯誤處理** | `Result<T, E>` + `?` operator，每個錯誤路徑都被編譯器強制處理 | `if err != nil` 模式，容易遺漏錯誤檢查 |
| **ORM/Query Builder** | `sqlx` 提供 compile-time SQL 驗證（`sqlx::query!` 巨集），SQL 語法錯誤在建構時發現 | `database/sql` 是裸 SQL，語法錯誤在運行時才發現 |

---

## When to Use / 適用場景

**場景一：微服務之間的可靠事件傳遞** — 每當一個服務的資料狀態變更需要通知其他服務時（如訂單建立後通知庫存服務、支付服務、通知服務），使用 outbox pattern 確保事件不會遺失。這是微服務架構中實現 eventual consistency 的標準方式。

**場景二：Saga 編排的事件步驟** — 在 Choreography-based Saga 中，每個參與者需要在完成自己的步驟後發佈事件觸發下一個參與者。Outbox pattern 確保每個步驟的資料更新和事件發佈是原子的——不會出現「庫存已扣減但事件未發出」的中間狀態。

**場景三：事件溯源系統的事件持久化** — 在 Event Sourcing 架構中，每個領域事件既需要持久化（作為狀態的真實來源），又需要發佈到事件匯流排供其他服務消費。Outbox table 天然符合這個需求。

---

## When NOT to Use / 不適用場景

**反模式一：跨多個資料庫的交易** — Outbox pattern 依賴本地資料庫交易。如果業務操作需要同時寫入多個資料庫（如 MySQL + MongoDB），outbox 只能保證與其中一個資料庫的原子性。此時應考慮 Saga pattern 來協調跨服務的交易。

**反模式二：需要即時一致性（strong consistency）的場景** — Outbox pattern 本質上是 eventually consistent——事件從寫入 outbox 到被消費者處理之間有延遲（polling interval + Kafka 傳遞 + 消費者處理）。如果業務需求是「訂單建立後，使用者立即看到庫存減少」，outbox 的延遲可能不可接受。此時應在同一服務中同步處理，或接受 eventual consistency 但在 UI 上做樂觀更新。

**反模式三：極簡單的系統（不需要微服務的場景）** — 如果系統是 monolith，所有資料在同一個資料庫中，直接在同一個交易中更新多個表即可——不需要 outbox pattern。Outbox 是為了解決微服務中「每個服務有自己的資料庫」的限制，如果沒有這個限制，outbox 是不必要的複雜度。

---

## Real-World Examples / 真實世界案例

### Shopify — 高吞吐量 Outbox

Shopify 在其電商平台中大量使用 Transactional Outbox Pattern：

- **規模**：每天處理數十億個 outbox 事件
- **實作**：使用 MySQL 的 outbox 表 + 自建的 polling publisher（稱為 "ghostferry" 的衍生工具）
- **最佳化**：outbox 表使用分區（partition by date），舊的分區定期 DROP，避免表膨脹
- **延遲**：從事件寫入到 Kafka 投遞，P99 延遲 < 100ms

### Wix — Debezium CDC + Outbox

Wix 使用 Debezium CDC 來實作 outbox pattern：

- 每個微服務的 PostgreSQL 資料庫中都有 `outbox_events` 表
- Debezium connector 讀取每個資料庫的 WAL，將 outbox 事件路由到 Kafka
- Debezium 的 `outbox.EventRouter` SMT（Single Message Transform）自動將 outbox 記錄轉換為業務事件格式
- 消費端使用冪等處理 + deduplication table

### Stripe — 事件可靠性保證

Stripe 的事件系統核心就是 outbox pattern 的變體：

- 每筆支付操作在同一個資料庫交易中寫入支付記錄和事件記錄
- 獨立的 publisher 服務將事件發送到內部訊息系統和 webhook
- webhook 使用指數退避重試（exponential backoff）確保最終傳遞
- 每個 webhook event 有唯一 ID，接收方可用來去重

---

## Interview Questions / 面試常見問題

### Q1: 為什麼不能直接在資料庫交易中發送 Kafka 訊息？

**答**：將 Kafka produce 放在資料庫交易中會產生三個嚴重問題：

1. **不支援兩階段提交**：資料庫和 Kafka 是兩個獨立的系統，無法用同一個交易協調。Kafka 不支援 XA transaction（分散式交易協定），所以無法透過 2PC 來確保原子性。

2. **交易時間延長**：Kafka produce 是一個網路操作，可能需要數十毫秒甚至更久（若 Kafka broker 繁忙）。將網路呼叫放在資料庫交易中會延長交易持有 lock 的時間，增加鎖競爭，降低吞吐量。

3. **不一致的失敗模式**：
   - 若 Kafka produce 成功但 DB commit 失敗（如 deadlock retry）→ 事件已被消費但資料不存在
   - 若 DB commit 成功但在收到 Kafka ack 前網路超時 → 不確定事件是否發送成功，重試可能導致重複

Outbox pattern 的解決方案：將事件寫入同一資料庫的 outbox 表（本地交易，100% 原子），再由獨立程序非同步發送到 Kafka。

### Q2: Polling Publisher 和 CDC（Debezium）各自的優缺點？如何選擇？

**答**：

**Polling Publisher**：
- 優點：簡單，不需要額外基礎設施，任何資料庫都支援
- 缺點：有延遲（polling interval，通常 100ms-1s）、對資料庫有額外查詢負載、多實例需要 `FOR UPDATE SKIP LOCKED` 協調
- 適合：中小規模系統、團隊不熟悉 CDC 工具、不需要毫秒級延遲的場景

**CDC（Debezium）**：
- 優點：毫秒級延遲（直接讀取 WAL）、零查詢負載（不 SELECT 表）、天然保序
- 缺點：額外的基礎設施依賴（Kafka Connect + Debezium connector）、需要資料庫的 WAL 存取權限、配置和運維複雜
- 適合：大規模系統、高吞吐量場景、需要低延遲的場景、已有 Kafka Connect 基礎設施的團隊

經驗法則：如果團隊已經在使用 Kafka Connect，優先選擇 Debezium CDC。如果是剛開始引入 outbox pattern，先用 Polling Publisher 驗證模式，等規模成長後再遷移到 CDC。

### Q3: 如何確保消費者的冪等性？

**答**：冪等消費者的實作有幾種策略：

1. **Processed Events Table（已處理事件表）**：消費者在自己的資料庫中維護一個 `processed_events` 表，每次處理事件前先查詢是否已處理過。業務操作和 INSERT 到 `processed_events` 在同一交易中。

   ```sql
   BEGIN;
   -- 檢查是否已處理
   SELECT 1 FROM processed_events WHERE event_id = 'evt-001';
   -- 若不存在，執行業務邏輯
   UPDATE inventory SET stock = stock - 1 WHERE product_id = 'p-1';
   INSERT INTO processed_events (event_id) VALUES ('evt-001');
   COMMIT;
   ```

2. **Natural Idempotency（自然冪等）**：某些操作天然冪等——如 `SET stock = 10`（無論執行幾次結果都一樣）。但 `SET stock = stock - 1` 不是冪等的。

3. **Conditional Update（條件更新）**：在 WHERE 子句中加入版本號或狀態檢查——`UPDATE orders SET status = 'CONFIRMED' WHERE id = ? AND status = 'CREATED'`，重複執行時 WHERE 條件不匹配，UPDATE 影響 0 行。

4. **Kafka Consumer Offset**：Kafka 的 consumer offset 可以防止 rebalance 後的重複消費——但 offset commit 和業務處理之間仍可能不一致（如業務處理成功但 offset commit 失敗），所以仍需要應用層的冪等機制。

### Q4: Outbox 表會不會無限增長？如何管理？

**答**：是的，如果不清理，outbox 表會持續增長。管理策略：

1. **定期刪除已發佈的事件**：設定排程任務，刪除 `status = 'PUBLISHED'` 且 `published_at < NOW() - INTERVAL '7 days'` 的記錄。保留近期記錄供除錯和重播。

2. **表分區（Table Partitioning）**：按日期分區，直接 DROP 過期的分區——比 DELETE 快得多（O(1) vs O(N）），且不產生死行（dead tuples）。

3. **CDC 模式下的即時刪除**：使用 Debezium 時，可以配置在事件被捕獲後立即刪除 outbox 記錄（因為 CDC 讀取的是 WAL，不是表）。

4. **監控 outbox 表大小**：設定告警——若 `PENDING` 事件數量超過閾值（如 10000），可能表示 publisher 故障或 Kafka 不可用。

### Q5: 如果 Polling Publisher 本身 crash 了怎麼辦？

**答**：Polling Publisher crash 不會導致資料遺失——outbox 事件安全地存在於資料庫中，等待 publisher 恢復後繼續處理。

具體保證：
1. **事件不會遺失**：因為事件在資料庫中，資料庫的持久性保證（WAL + fsync）確保事件即使在 crash 後也存在
2. **事件可能被重複發佈**：若 publisher 在 Kafka produce 成功後、UPDATE status 之前 crash，恢復後會重新查詢到該事件並再次發佈。因此消費端必須是冪等的
3. **延遲會增加**：publisher crash 期間事件不會被發佈，恢復後需要處理積壓的事件
4. **高可用部署**：運行多個 publisher 實例，使用 `FOR UPDATE SKIP LOCKED`（PostgreSQL）確保同一事件不被多個實例同時處理。或使用 leader election 確保只有一個活躍的 publisher

---

## Pitfalls / 常見陷阱

### 陷阱 1：outbox 事件不在業務交易中

```sql
-- 錯誤：outbox INSERT 在交易外，不是原子的
BEGIN;
INSERT INTO orders (id, ...) VALUES (...);
COMMIT;

-- 若此刻 crash，事件不會被寫入
INSERT INTO outbox_events (...) VALUES (...);  -- ← 不在交易中！

-- 正確：outbox INSERT 必須在同一個交易中
BEGIN;
INSERT INTO orders (id, ...) VALUES (...);
INSERT INTO outbox_events (...) VALUES (...);  -- ← 同一交易
COMMIT;
```

### 陷阱 2：未實作消費者冪等性

```go
// 錯誤：直接處理事件，重複投遞會導致庫存被扣兩次
func handleOrderCreated(event OutboxEvent) error {
    _, err := db.Exec("UPDATE inventory SET stock = stock - 1 WHERE product_id = $1",
        event.ProductID)
    return err  // 重複處理 → 庫存多扣一次！
}

// 正確：用 processed_events 表去重
func handleOrderCreated(event OutboxEvent) error {
    tx, _ := db.Begin()
    defer tx.Rollback()

    // 檢查是否已處理
    var exists bool
    tx.QueryRow("SELECT EXISTS(SELECT 1 FROM processed_events WHERE event_id = $1)",
        event.ID).Scan(&exists)
    if exists {
        return nil // 已處理，跳過
    }

    // 執行業務邏輯 + 記錄已處理（同一交易）
    tx.Exec("UPDATE inventory SET stock = stock - 1 WHERE product_id = $1", event.ProductID)
    tx.Exec("INSERT INTO processed_events (event_id) VALUES ($1)", event.ID)
    return tx.Commit()
}
```

### 陷阱 3（Rust 特定）：sqlx Transaction 的生命週期問題

```rust
// 錯誤：交易在 scope 結束時被 drop，自動 rollback
async fn create_order(pool: &PgPool) -> Result<(), sqlx::Error> {
    let tx = pool.begin().await?;

    sqlx::query("INSERT INTO orders ...").execute(&*tx).await?;
    // ← tx 離開 scope 時被 drop，交易自動 rollback！
    // 需要傳入 &mut *tx 而非 &*tx

    Ok(())
}

// 正確：使用 &mut *tx 並在最後 commit
async fn create_order(pool: &PgPool) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    sqlx::query("INSERT INTO orders ...")
        .execute(&mut *tx)  // ← &mut *tx
        .await?;

    sqlx::query("INSERT INTO outbox_events ...")
        .execute(&mut *tx)  // ← 同一個 tx
        .await?;

    tx.commit().await?;  // ← 明確 commit
    Ok(())
}
```

### 陷阱 4（Go 特定）：忘記 defer tx.Rollback()

```go
// 錯誤：若中間步驟 panic 或 return error，交易不會被 rollback
// 資料庫連線被佔用直到連線超時
func createOrder(ctx context.Context, db *sql.DB) error {
    tx, _ := db.BeginTx(ctx, nil)
    // 沒有 defer tx.Rollback()

    _, err := tx.ExecContext(ctx, "INSERT INTO orders ...")
    if err != nil {
        return err  // ← 交易未 rollback，連線洩漏！
    }
    return tx.Commit()
}

// 正確：始終 defer tx.Rollback()，Commit 後 Rollback 是 no-op
func createOrder(ctx context.Context, db *sql.DB) error {
    tx, err := db.BeginTx(ctx, nil)
    if err != nil {
        return err
    }
    defer tx.Rollback()  // ← 安全網：Commit 成功後 Rollback 不會做任何事

    _, err = tx.ExecContext(ctx, "INSERT INTO orders ...")
    if err != nil {
        return err  // ← 自動 rollback（defer）
    }

    _, err = tx.ExecContext(ctx, "INSERT INTO outbox_events ...")
    if err != nil {
        return err  // ← 自動 rollback（defer）
    }

    return tx.Commit()  // ← 成功 commit
}
```

### 陷阱 5：Polling Publisher 未使用 FOR UPDATE SKIP LOCKED

```sql
-- 錯誤：多個 publisher 實例查詢到同一批事件，導致重複發佈
SELECT * FROM outbox_events WHERE status = 'PENDING' ORDER BY created_at LIMIT 100;
-- 兩個 publisher 同時執行，都拿到相同的 100 個事件

-- 正確：FOR UPDATE SKIP LOCKED 確保每個事件只被一個 publisher 處理
SELECT * FROM outbox_events
WHERE status = 'PENDING'
ORDER BY created_at
LIMIT 100
FOR UPDATE SKIP LOCKED;
-- publisher A 鎖定前 100 個事件
-- publisher B 跳過已鎖定的，拿到第 101-200 個事件（如果有的話）
```

### 陷阱 6：outbox payload 包含過大的資料

```sql
-- 錯誤：將完整的文件內容（如 10 MB 的 PDF）存在 outbox payload 中
-- outbox 表爆炸增長，polling query 變慢
INSERT INTO outbox_events (payload)
VALUES ('{"document_content": "<base64 encoded 10MB PDF>"}');

-- 正確：payload 只存引用（ID 或 URL），消費者按需拉取完整資料
INSERT INTO outbox_events (payload)
VALUES ('{"document_id": "doc-123", "storage_url": "s3://bucket/doc-123.pdf"}');
```

### 陷阱 7（Rust 特定）：使用 `sqlx::query!` 巨集時 outbox 表不存在導致編譯失敗

```rust
// 問題：sqlx::query! 巨集在編譯期檢查 SQL，需要資料庫中有對應的表
// 若 CI 環境的資料庫沒有 outbox_events 表，編譯會失敗

// 解法 1：使用 sqlx::query（非巨集版本），放棄編譯期檢查
sqlx::query("INSERT INTO outbox_events (...) VALUES (...)")
    .bind(value)
    .execute(&mut *tx)
    .await?;

// 解法 2：在 CI 中使用 sqlx 的 offline mode（.sqlx/ 目錄）
// cargo sqlx prepare -- 產生離線查詢資料
```

---

## Cross-references / 交叉引用

- [[13_saga_pattern]] — Saga 每個步驟都適合用 outbox 確保事件的可靠發佈
- [[08_event_driven_architecture]] — Outbox pattern 是事件驅動架構中可靠事件發佈的基石
- [[19_idempotency_design]] — 消費端的冪等處理是 outbox pattern 正確性的另一半
- [[16_message_queue_fundamentals]] — Outbox 事件最終發送到的目的地——MQ/Kafka 的基礎知識
- [[17_kafka_deep_dive]] — Kafka 的 partition、offset、consumer group 如何影響事件順序和重複投遞

---

## References / 參考資料

- Chris Richardson, "Microservices Patterns" — Chapter 3: Transactional Outbox Pattern
- Martin Kleppmann, "Designing Data-Intensive Applications" — Chapter 11: Stream Processing（CDC 的理論基礎）
- Debezium 官方文件 — Outbox Event Router: https://debezium.io/documentation/reference/transformations/outbox-event-router.html
- Gunnar Morling, "Reliable Microservices Data Exchange With the Outbox Pattern": https://debezium.io/blog/2019/02/19/reliable-microservices-data-exchange-with-the-outbox-pattern/
- PostgreSQL WAL 文件: https://www.postgresql.org/docs/current/wal-intro.html
