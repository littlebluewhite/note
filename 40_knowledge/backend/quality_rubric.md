---
title: Backend Chapter Quality Rubric
note_type: system
domain: backend
tags: [system, backend]
created: 2026-02-17
updated: 2026-02-17
status: active
source: system
---
# Backend Chapter Quality Rubric

## Purpose

定義 `backend` 系列每章最低可教學品質，確保內容深度、雙語實作正確性、生產環境適用性一致。

## Scope

適用檔案：

- `system_design/01_scalability_fundamentals.md`
- `system_design/02_availability_and_fault_tolerance.md`
- `system_design/03_consistency_trade_offs.md`
- `system_design/04_api_design_rest.md`
- `system_design/05_api_design_grpc_graphql.md`
- `system_design/06_api_versioning.md`
- `system_design/07_microservices_vs_monolith.md`
- `system_design/08_event_driven_architecture.md`
- `system_design/09_cqrs_event_sourcing.md`
- `system_design/10_ddd_basics.md`
- `system_design/11_system_design_interview.md`
- `distributed_systems/12_cap_consistency_models.md`
- `distributed_systems/13_saga_pattern.md`
- `distributed_systems/14_two_phase_commit.md`
- `distributed_systems/15_distributed_locking.md`
- `distributed_systems/16_message_queue_fundamentals.md`
- `distributed_systems/17_kafka_deep_dive.md`
- `distributed_systems/18_kafka_operations.md`
- `distributed_systems/19_idempotency_design.md`
- `distributed_systems/20_rate_limiting.md`
- `infrastructure/21_caching_redis_patterns.md`
- `infrastructure/22_cache_invalidation.md`
- `infrastructure/23_structured_logging.md`
- `infrastructure/24_distributed_tracing.md`
- `infrastructure/25_metrics_sli_slo_sla.md`
- `infrastructure/26_oauth2_jwt.md`
- `infrastructure/27_rbac_abac.md`
- `infrastructure/28_owasp_api_security.md`
- `infrastructure/29_secrets_management.md`
- `infrastructure/30_http2_http3_grpc_transport.md`
- `infrastructure/31_websocket_tls_mtls.md`
- `infrastructure/32_load_balancing_service_discovery.md`
- `engineering/33_testing_strategy.md`
- `engineering/34_integration_contract_testing.md`
- `engineering/35_load_testing.md`
- `engineering/36_concurrency_patterns.md`
- `engineering/37_performance_profiling.md`
- `engineering/38_connection_pooling.md`
- `engineering/39_error_handling_retry.md`
- `engineering/40_cicd_deployment.md`

## Frontmatter Requirements

每章 frontmatter 必須包含以下欄位：

| 欄位 | 型別 | 說明 |
|------|------|------|
| `title` | string | 英文名 / 中文名 |
| `note_type` | string | 固定為 `knowledge` |
| `domain` | string | 固定為 `backend` |
| `category` | string | `system_design` / `distributed_systems` / `infrastructure` / `engineering` |
| `tags` | list | 至少含 `backend`, category, `go`, `rust`, topic kebab name |
| `created` | date | 建立日期 |
| `updated` | date | 最後更新日期 |
| `status` | string | `active` / `draft` |
| `source` | string | 固定為 `knowledge` |
| `series` | string | 固定為 `backend` |
| `chapter` | string | 兩位數字串，如 `"01"` |
| `level` | string | `intermediate` / `advanced` |
| `review_interval_days` | int | 複習間隔天數 |
| `next_review` | date | 下次複習日期 |

## Chapter-level Minimums — Comprehensive Teaching Chapter

章節合約：必須含以下固定標題，順序不可調換。

1. `Intent / 意圖`
2. `Problem / 問題情境`
3. `Core Concepts / 核心概念`
4. `Architecture / 架構`
5. `How It Works / 運作原理`
6. `Rust 實作`
7. `Go 實作`
8. `Rust vs Go 對照表`
9. `When to Use / 適用場景`
10. `When NOT to Use / 不適用場景`
11. `Real-World Examples / 真實世界案例`
12. `Interview Questions / 面試常見問題`
13. `Pitfalls / 常見陷阱`
14. `References / 參考資料`

### Intent / 意圖

- 1-2 句話，明確表達此主題的核心概念。
- 需讓讀者在 10 秒內理解「這個主題解決什麼問題」。

### Problem / 問題情境

- 至少 1 個具體生產場景（非抽象描述）。
- 場景需包含「沒有此知識時的痛點」。

### Core Concepts / 核心概念

- 至少 3 個已定義術語與解釋。
- 術語需中英對照。

### Architecture / 架構

- 必須包含 Mermaid diagram（sequence / flowchart / architecture 擇一適合者）。
- Diagram 需覆蓋核心流程。

### How It Works / 運作原理

- 步驟式說明，以編號列表呈現。
- 每步驟需明確說明「誰」做了「什麼」。

### Rust 實作

- 完整可編譯可執行，含 `fn main()` 或 Axum handler 範例。
- 程式碼尾端需以註解標注預期輸出（`// Output:` 區塊）。
- 語法需符合 Rust 2024 edition，使用 Axum 0.8+ / sqlx 0.8+ / tokio 1.x。
- 變數與函式命名具意圖，不使用 `foo`, `bar`。

### Go 實作

- 完整可編譯可執行，含 `package main`、`import`、`func main()`。
- 程式碼尾端需以註解標注預期輸出（`// Output:` 區塊）。
- 語法需符合 Go 1.24+，優先使用標準庫。
- 變數與函式命名具意圖，不使用 `foo`, `bar`。

### Rust vs Go 對照表

- 至少 3 個面向的比較（如：型別系統、並行安全、生態系、慣用寫法等）。

### When to Use / 適用場景

- 至少 2 條具體使用情境。

### When NOT to Use / 不適用場景

- 至少 2 條具體不適用情境。

### Real-World Examples / 真實世界案例

- 至少 1 個知名系統的實際案例（如 Netflix, Stripe, Uber, AWS）。
- 需附上系統名稱與簡要說明。

### Interview Questions / 面試常見問題

- 3-5 個常見面試問題。
- 每題附簡潔答案（3-5 句）。

### Pitfalls / 常見陷阱

- 至少 3 條。
- 需針對 Go 與 Rust 各至少提及 1 個語言特有陷阱。

### References / 參考資料

- 至少列出 2 個參考來源。
- 優先使用 DDIA、官方文件、RFC、經典書籍。

## Chapter-level Minimums — Troubleshooting Guide

必須含以下固定標題，順序不可調換。

1. `Purpose / 目的`
2. `Symptoms / 常見症狀`
3. `Diagnostic Steps / 診斷步驟`
4. `Detection Commands / 偵測指令`
5. `Common Causes & Resolutions / 常見原因與解法`
6. `Prevention Checklist / 預防清單`
7. `References / 參考資料`

## Chapter-level Minimums — Quick Reference

必須含以下固定標題，順序不可調換。

1. `Purpose / 目的`
2. `Core Concepts / 核心概念`
3. `Comparison Table / 比較表`
4. `Usage Examples / 使用範例`
5. `Decision Guide / 選擇指南`
6. `References / 參考資料`

## Code Snippet Standards

- Rust: tokio 1.x, axum 0.8+, sqlx 0.8+, Rust 2024 edition
- Go: Go 1.24+, standard library preferred
- Variable naming: intentful, no foo/bar
- Each code block annotated with expected output
- Code block language tag required (rust / go / sql / bash / yaml)

## Review Checklist

- [ ] Frontmatter 所有必填欄位完整。
- [ ] 固定標題完整且順序正確（依筆記類型）。
- [ ] Intent 精簡且準確（1-2 句）。
- [ ] Problem 含具體生產場景。
- [ ] Architecture 含 Mermaid diagram。
- [ ] Rust 程式碼可直接編譯執行。
- [ ] Go 程式碼可直接編譯執行。
- [ ] 對照表至少 3 行。
- [ ] 適用 / 不適用各至少 2 條。
- [ ] Real-World Examples 至少 1 個。
- [ ] Interview Questions 至少 3 題。
- [ ] Pitfalls 至少 3 條且含語言特有陷阱。
- [ ] References 至少 2 個來源。
- [ ] Cross-references 連結相關現有筆記。
