---
title: "API Versioning / API 版本控制"
note_type: knowledge
domain: backend
category: system_design
tags: [backend, system-design, go, rust, api-versioning]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "06"
level: intermediate
review_interval_days: 14
next_review: 2026-03-03
---
# API Versioning / API 版本控制
## Purpose / 目的
API 版本控制讓服務端在不中斷既有客戶端的前提下演進介面。缺乏版本策略會導致 breaking change 連鎖影響所有消費者，造成部署耦合與生產事故。
## Core Concepts / 核心概念
- **URL Path Versioning**：版本編碼在路徑（`/v1/users`），最直觀，Stripe 與 Google Cloud 採用。
- **Header Versioning**：透過 `Accept` 或自訂 header（GitHub `X-GitHub-Api-Version`）傳遞，URL 保持乾淨。
- **Query Param Versioning**：`?version=2` 傳遞，實作簡單但易被快取層忽略。
- **Content Negotiation**：以 media type 指定版本（`application/vnd.api+json;version=2`），符合 REST 但不直覺。
- **Semantic Versioning**：`MAJOR.MINOR.PATCH`，MAJOR 遞增代表 breaking change。
- **Breaking vs Non-breaking**：移除欄位、改型別為 breaking；新增可選欄位、新 endpoint 為 non-breaking。
## Comparison Table / 比較表
| 策略 | 優點 | 缺點 | 採用者 |
|------|------|------|--------|
| URL Path `/v1/` | 直觀、易除錯、快取友善 | URL 膨脹、升版需改 client 路徑 | Stripe, Google, Twilio |
| Header | URL 乾淨、彈性高 | 瀏覽器不易測試 | GitHub, Azure |
| Query `?v=2` | 實作最簡單 | 易遺漏、CDN 快取可能忽略 | 少數內部 API |
## Usage Examples / 使用範例
```rust
use axum::{routing::get, Json, Router};
use serde::Serialize;
#[derive(Serialize)] struct User { id: u64, name: String }
#[derive(Serialize)] struct UserV2 { id: u64, name: String, email: String }
async fn list_v1() -> Json<User> { Json(User { id: 1, name: "alice".into() }) }
async fn list_v2() -> Json<UserV2> {
    Json(UserV2 { id: 1, name: "alice".into(), email: "a@ex.com".into() })
}
fn app() -> Router {
    Router::new()
        .nest("/v1", Router::new().route("/users", get(list_v1)))
        .nest("/v2", Router::new().route("/users", get(list_v2)))
}
// GET /v1/users -> {"id":1,"name":"alice"}
// GET /v2/users -> {"id":1,"name":"alice","email":"a@ex.com"}
```
```go
package main
import ("encoding/json"; "net/http")
type User struct { ID int `json:"id"`; Name string `json:"name"` }
type UserV2 struct { ID int `json:"id"`; Name string `json:"name"`; Email string `json:"email"` }
func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("GET /v1/users", func(w http.ResponseWriter, _ *http.Request) {
        json.NewEncoder(w).Encode(User{1, "alice"})
    })
    mux.HandleFunc("GET /v2/users", func(w http.ResponseWriter, _ *http.Request) {
        json.NewEncoder(w).Encode(UserV2{1, "alice", "a@ex.com"})
    })
    http.ListenAndServe(":3000", mux)
}
// GET /v1/users -> {"id":1,"name":"alice"}
// GET /v2/users -> {"id":1,"name":"alice","email":"a@ex.com"}
```
## Decision Guide / 選擇指南
1. **公開 API、消費者眾多？** -> URL Path。Stripe 模式已成業界標準。
2. **同一 URL 需回傳不同表示？** -> Header + content negotiation。
3. **內部微服務？** -> 優先 non-breaking 演進（加欄位、新 endpoint），減少版本化需求。
4. **Deprecation Policy**：公告 6-12 個月棄用週期，加 `Sunset` header（RFC 8594），監控流量後移除。
## References / 參考資料
- Stripe API Versioning: https://stripe.com/docs/api/versioning
- GitHub API Versions: https://docs.github.com/en/rest/about-the-rest-api/api-versions
- RFC 8594 (Sunset Header): https://www.rfc-editor.org/rfc/rfc8594
## Cross-references / 交叉引用
- [[01_scalability_fundamentals|Scalability Fundamentals]] — 版本化路由與負載均衡、無狀態設計相關
- [[03_consistency_trade_offs|Consistency Trade-offs]] — 新舊版本 API 並存期間的資料一致性策略
