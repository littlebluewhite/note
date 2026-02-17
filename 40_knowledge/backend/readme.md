---
title: Backend Series README
note_type: system
domain: backend
tags: [system, backend, go, rust]
created: 2026-02-17
updated: 2026-02-17
status: active
source: system
---
# Backend Series README

## Summary

- Audience: senior backend engineers preparing for interviews and building production systems.
- Language baseline: Rust 2024 edition + Axum 0.8+ / Go 1.24+.
- Baseline date: 2026-02-17.
- Learning mode: each batch covers 2-3 topics with dual-language implementation.

## Batch Learning Route (15 batches)

- Batch 1: `01`, `02`, `03` (可擴展性基礎三柱 — Scalability, Availability, Consistency)
- Batch 2: `04`, `05`, `06` (API 設計 — REST, gRPC/GraphQL, Versioning)
- Batch 3: `07`, `08` (架構風格 — Microservices vs Monolith, Event-Driven)
- Batch 4: `09`, `10` (DDD & CQRS — CQRS/Event Sourcing, DDD Basics)
- Batch 5: `11`, `12` (面試框架 + CAP — Interview Framework, CAP Theorem)
- Batch 6: `13`, `14`, `15` (分散式交易與鎖 — Saga, 2PC, Distributed Locking)
- Batch 7: `16`, `17`, `18` (訊息佇列 — MQ Fundamentals, Kafka Deep Dive, Kafka Ops)
- Batch 8: `19`, `20`, `21` (冪等 + 限流 + Redis — Idempotency, Rate Limiting, Caching)
- Batch 9: `22`, `23`, `24` (快取失效 + 可觀測性 — Cache Invalidation, Logging, Tracing)
- Batch 10: `25`, `26`, `27` (指標 + 認證授權 — Metrics/SLO, OAuth2/JWT, RBAC/ABAC)
- Batch 11: `28`, `29`, `30` (API 安全 + 傳輸協定 — OWASP, Secrets, HTTP/2/3/gRPC)
- Batch 12: `31`, `32`, `33` (網路 + 測試基礎 — WebSocket/TLS, Load Balancing, Testing)
- Batch 13: `34`, `35`, `36` (進階測試 + 並行 — Contract Testing, Load Testing, Concurrency)
- Batch 14: `37`, `38`, `39` (效能 + 錯誤處理 — Profiling, Connection Pool, Retry)
- Batch 15: `40` (CI/CD — Deployment Strategies)

## Estimated Time Per Topic

- Comprehensive chapters: 75-90 min each.
- Troubleshooting guides: 45-60 min each.
- Quick references: 30 min each.
- Recommended cadence: 2-3 topics per week + 1 review day.

## Reading Priority

- Must-read (`必讀`): `01`, `02`, `03`, `04`, `07`, `08`, `11`, `12`, `13`, `15`, `16`, `17`, `19`, `20`, `21`, `24`, `25`, `26`, `33`, `39`
- Important (`重要`): `05`, `06`, `09`, `10`, `14`, `18`, `22`, `23`, `27`, `30`, `32`, `34`, `36`, `37`, `38`, `40`
- Skippable (`可跳讀`): `29`, `31`, `35`

## Support Documents

- [quality_rubric](quality_rubric.md)
- [coverage_matrix](coverage_matrix.md)

## Chapters

### System Design

- [01_scalability_fundamentals](system_design/01_scalability_fundamentals.md) - 必讀 - 90 min
- [02_availability_and_fault_tolerance](system_design/02_availability_and_fault_tolerance.md) - 必讀 - 75 min
- [03_consistency_trade_offs](system_design/03_consistency_trade_offs.md) - 必讀 - 75 min
- [04_api_design_rest](system_design/04_api_design_rest.md) - 必讀 - 90 min
- [05_api_design_grpc_graphql](system_design/05_api_design_grpc_graphql.md) - 重要 - 75 min
- [06_api_versioning](system_design/06_api_versioning.md) - 重要 - 30 min
- [07_microservices_vs_monolith](system_design/07_microservices_vs_monolith.md) - 必讀 - 90 min
- [08_event_driven_architecture](system_design/08_event_driven_architecture.md) - 必讀 - 90 min
- [09_cqrs_event_sourcing](system_design/09_cqrs_event_sourcing.md) - 重要 - 90 min
- [10_ddd_basics](system_design/10_ddd_basics.md) - 重要 - 90 min
- [11_system_design_interview](system_design/11_system_design_interview.md) - 必讀 - 75 min

### Distributed Systems

- [12_cap_consistency_models](distributed_systems/12_cap_consistency_models.md) - 必讀 - 90 min
- [13_saga_pattern](distributed_systems/13_saga_pattern.md) - 必讀 - 90 min
- [14_two_phase_commit](distributed_systems/14_two_phase_commit.md) - 重要 - 45 min
- [15_distributed_locking](distributed_systems/15_distributed_locking.md) - 必讀 - 75 min
- [16_message_queue_fundamentals](distributed_systems/16_message_queue_fundamentals.md) - 必讀 - 75 min
- [17_kafka_deep_dive](distributed_systems/17_kafka_deep_dive.md) - 必讀 - 90 min
- [18_kafka_operations](distributed_systems/18_kafka_operations.md) - 重要 - 60 min
- [19_idempotency_design](distributed_systems/19_idempotency_design.md) - 必讀 - 75 min
- [20_rate_limiting](distributed_systems/20_rate_limiting.md) - 必讀 - 75 min

### Infrastructure

- [21_caching_redis_patterns](infrastructure/21_caching_redis_patterns.md) - 必讀 - 90 min
- [22_cache_invalidation](infrastructure/22_cache_invalidation.md) - 重要 - 45 min
- [23_structured_logging](infrastructure/23_structured_logging.md) - 重要 - 60 min
- [24_distributed_tracing](infrastructure/24_distributed_tracing.md) - 必讀 - 75 min
- [25_metrics_sli_slo_sla](infrastructure/25_metrics_sli_slo_sla.md) - 必讀 - 75 min
- [26_oauth2_jwt](infrastructure/26_oauth2_jwt.md) - 必讀 - 90 min
- [27_rbac_abac](infrastructure/27_rbac_abac.md) - 重要 - 75 min
- [28_owasp_api_security](infrastructure/28_owasp_api_security.md) - 重要 - 60 min
- [29_secrets_management](infrastructure/29_secrets_management.md) - 可跳讀 - 30 min
- [30_http2_http3_grpc_transport](infrastructure/30_http2_http3_grpc_transport.md) - 重要 - 75 min
- [31_websocket_tls_mtls](infrastructure/31_websocket_tls_mtls.md) - 可跳讀 - 45 min
- [32_load_balancing_service_discovery](infrastructure/32_load_balancing_service_discovery.md) - 重要 - 75 min

### Engineering

- [33_testing_strategy](engineering/33_testing_strategy.md) - 必讀 - 75 min
- [34_integration_contract_testing](engineering/34_integration_contract_testing.md) - 重要 - 75 min
- [35_load_testing](engineering/35_load_testing.md) - 可跳讀 - 45 min
- [36_concurrency_patterns](engineering/36_concurrency_patterns.md) - 重要 - 90 min
- [37_performance_profiling](engineering/37_performance_profiling.md) - 重要 - 60 min
- [38_connection_pooling](engineering/38_connection_pooling.md) - 重要 - 45 min
- [39_error_handling_retry](engineering/39_error_handling_retry.md) - 必讀 - 75 min
- [40_cicd_deployment](engineering/40_cicd_deployment.md) - 重要 - 75 min
