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

## Batch Learning Route (30 batches)

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
- Batch 16: `41`, `42` (容器與服務網格 — K8s Core, Service Mesh)
- Batch 17: `43`, `44` (資料庫水平擴展 — Sharding, Replication)
- Batch 18: `45` (NoSQL 選型)
- Batch 19: `46`, `47` (可靠性工程 — Chaos Engineering, Incident/DR)
- Batch 20: `48`, `49` (分散式深入 — Consensus, Leader Election)
- Batch 21: `50`, `51` (基礎設施自動化 — IaC, GitOps)
- Batch 22: `52`, `53` (資料管道 — Stream Processing, Batch Processing)
- Batch 23: `54`, `55`, `56` (架構補充 — Patterns, Schema Migration, Feature Flags)
- Batch 24: `57`, `68`, `61` (基礎設施補強 — Docker, DNS/Network, Object Storage & CDN)
- Batch 25: `58`, `70`, `71` (API 層進階 — API Gateway/BFF, Webhook, Realtime Patterns)
- Batch 26: `59`, `65`, `76` (分散式資料流 — Transactional Outbox, Serialization, Data Pipeline/ETL)
- Batch 27: `60`, `62`, `64` (資料庫進階 — Search Infrastructure, Multi-Tenancy, Database Design Patterns)
- Batch 28: `63`, `66`, `69` (工程實踐 — Graceful Shutdown, Background Job, Configuration/12-Factor)
- Batch 29: `67`, `73`, `74`, `75` (可觀測性 + 特化資料庫 + DI — Observability, Graph DB, Time-Series DB, Dependency Injection)
- Batch 30: `72` (金融交易 — Payment/Financial Transaction Patterns)

## Estimated Time Per Topic

- Comprehensive chapters: 75-90 min each.
- Troubleshooting guides: 45-60 min each.
- Quick references: 30 min each.
- Recommended cadence: 2-3 topics per week + 1 review day.

## Reading Priority

- Must-read (`必讀`): `01`, `02`, `03`, `04`, `07`, `08`, `11`, `12`, `13`, `15`, `16`, `17`, `19`, `20`, `21`, `24`, `25`, `26`, `33`, `39`, `41`, `43`, `44`, `46`, `48`, `57`, `58`, `59`, `63`, `64`, `67`, `72`
- Important (`重要`): `05`, `06`, `09`, `10`, `14`, `18`, `22`, `23`, `27`, `30`, `32`, `34`, `36`, `37`, `38`, `40`, `42`, `45`, `47`, `49`, `52`, `55`, `56`, `60`, `62`, `65`, `66`, `69`, `71`, `75`, `76`
- Skippable (`可跳讀`): `29`, `31`, `35`, `50`, `51`, `53`, `54`, `61`, `68`, `70`, `73`, `74`

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
- [45_nosql_selection_guide](system_design/45_nosql_selection_guide.md) - 重要 - 75 min
- [54_architecture_supplement_patterns](system_design/54_architecture_supplement_patterns.md) - 可跳讀 - 75 min
- [58_api_gateway_bff](system_design/58_api_gateway_bff.md) - 必讀 - 75 min
- [62_multi_tenancy_patterns](system_design/62_multi_tenancy_patterns.md) - 重要 - 90 min
- [64_database_design_patterns](system_design/64_database_design_patterns.md) - 必讀 - 90 min
- [70_webhook_design_patterns](system_design/70_webhook_design_patterns.md) - 可跳讀 - 75 min
- [71_realtime_patterns](system_design/71_realtime_patterns.md) - 重要 - 90 min
- [72_payment_financial_transactions](system_design/72_payment_financial_transactions.md) - 必讀 - 90 min
- [73_graph_database_patterns](system_design/73_graph_database_patterns.md) - 可跳讀 - 75 min
- [74_time_series_database](system_design/74_time_series_database.md) - 可跳讀 - 75 min

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
- [43_sharding_partitioning](distributed_systems/43_sharding_partitioning.md) - 必讀 - 90 min
- [44_database_replication](distributed_systems/44_database_replication.md) - 必讀 - 90 min
- [48_consensus_algorithms](distributed_systems/48_consensus_algorithms.md) - 必讀 - 90 min
- [49_leader_election_distributed_scheduling](distributed_systems/49_leader_election_distributed_scheduling.md) - 重要 - 75 min
- [52_stream_processing](distributed_systems/52_stream_processing.md) - 重要 - 90 min
- [53_batch_processing](distributed_systems/53_batch_processing.md) - 可跳讀 - 75 min
- [59_transactional_outbox](distributed_systems/59_transactional_outbox.md) - 必讀 - 75 min
- [65_data_serialization_schema_evolution](distributed_systems/65_data_serialization_schema_evolution.md) - 重要 - 75 min
- [76_data_pipeline_etl](distributed_systems/76_data_pipeline_etl.md) - 重要 - 90 min

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
- [41_kubernetes_core_concepts](infrastructure/41_kubernetes_core_concepts.md) - 必讀 - 90 min
- [42_service_mesh](infrastructure/42_service_mesh.md) - 重要 - 75 min
- [50_infrastructure_as_code](infrastructure/50_infrastructure_as_code.md) - 可跳讀 - 60 min
- [51_gitops](infrastructure/51_gitops.md) - 可跳讀 - 60 min
- [57_docker_container_fundamentals](infrastructure/57_docker_container_fundamentals.md) - 必讀 - 75 min
- [60_search_infrastructure](infrastructure/60_search_infrastructure.md) - 重要 - 90 min
- [61_object_storage_cdn](infrastructure/61_object_storage_cdn.md) - 可跳讀 - 75 min
- [67_observability_strategy](infrastructure/67_observability_strategy.md) - 必讀 - 90 min
- [68_dns_network_fundamentals](infrastructure/68_dns_network_fundamentals.md) - 可跳讀 - 75 min

### Engineering

- [33_testing_strategy](engineering/33_testing_strategy.md) - 必讀 - 75 min
- [34_integration_contract_testing](engineering/34_integration_contract_testing.md) - 重要 - 75 min
- [35_load_testing](engineering/35_load_testing.md) - 可跳讀 - 45 min
- [36_concurrency_patterns](engineering/36_concurrency_patterns.md) - 重要 - 90 min
- [37_performance_profiling](engineering/37_performance_profiling.md) - 重要 - 60 min
- [38_connection_pooling](engineering/38_connection_pooling.md) - 重要 - 45 min
- [39_error_handling_retry](engineering/39_error_handling_retry.md) - 必讀 - 75 min
- [40_cicd_deployment](engineering/40_cicd_deployment.md) - 重要 - 75 min
- [46_chaos_engineering](engineering/46_chaos_engineering.md) - 必讀 - 75 min
- [47_incident_management_disaster_recovery](engineering/47_incident_management_disaster_recovery.md) - 重要 - 75 min
- [55_zero_downtime_schema_migration](engineering/55_zero_downtime_schema_migration.md) - 重要 - 60 min
- [56_feature_flags](engineering/56_feature_flags.md) - 重要 - 60 min
- [63_graceful_shutdown_health_check](engineering/63_graceful_shutdown_health_check.md) - 必讀 - 75 min
- [66_background_job_task_queue](engineering/66_background_job_task_queue.md) - 重要 - 90 min
- [69_configuration_management_12_factor](engineering/69_configuration_management_12_factor.md) - 重要 - 60 min
- [75_dependency_injection](engineering/75_dependency_injection.md) - 重要 - 75 min

### Database

- [indexing](database/indexing.md) - 必讀 - 30 min
- [transactions](database/transactions.md) - 必讀 - 30 min
- [isolation_levels](database/isolation_levels.md) - 必讀 - 30 min
- [postgres_gotchas](database/postgres_gotchas.md) - 重要 - 30 min
- [postgres_explain_guide](database/postgres_explain_guide.md) - 重要 - 45 min
- [postgres_explain_examples](database/postgres_explain_examples.md) - 重要 - 30 min
- [postgres_index_join_guide](database/postgres_index_join_guide.md) - 重要 - 30 min
- [postgres_lock_troubleshooting](database/postgres_lock_troubleshooting.md) - 重要 - 45 min
- [postgres_slow_query_triage](database/postgres_slow_query_triage.md) - 重要 - 45 min
- [alembic/01_baseline](database/alembic/01_baseline.md) - 可跳讀 - 30 min
- [alembic/02_autogenerate](database/alembic/02_autogenerate.md) - 可跳讀 - 30 min
- [alembic/03_data_migrations](database/alembic/03_data_migrations.md) - 可跳讀 - 30 min
- [alembic/04_commands](database/alembic/04_commands.md) - 可跳讀 - 30 min
- [alembic/05_troubleshooting](database/alembic/05_troubleshooting.md) - 可跳讀 - 30 min

### Design Pattern

- [01_singleton](design_pattern/creational/01_singleton.md) - 必讀 - 60 min
- [02_factory_method](design_pattern/creational/02_factory_method.md) - 必讀 - 60 min
- [03_abstract_factory](design_pattern/creational/03_abstract_factory.md) - 可跳讀 - 60 min
- [04_builder](design_pattern/creational/04_builder.md) - 必讀 - 75 min
- [05_prototype](design_pattern/creational/05_prototype.md) - 可跳讀 - 60 min
- [06_adapter](design_pattern/structural/06_adapter.md) - 必讀 - 60 min
- [07_bridge](design_pattern/structural/07_bridge.md) - 可跳讀 - 60 min
- [08_composite](design_pattern/structural/08_composite.md) - 必讀 - 75 min
- [09_decorator](design_pattern/structural/09_decorator.md) - 必讀 - 75 min
- [10_facade](design_pattern/structural/10_facade.md) - 必讀 - 60 min
- [11_flyweight](design_pattern/structural/11_flyweight.md) - 可跳讀 - 60 min
- [12_proxy](design_pattern/structural/12_proxy.md) - 可跳讀 - 60 min
- [13_chain_of_responsibility](design_pattern/behavioral/13_chain_of_responsibility.md) - 可跳讀 - 60 min
- [14_command](design_pattern/behavioral/14_command.md) - 可跳讀 - 60 min
- [15_iterator](design_pattern/behavioral/15_iterator.md) - 可跳讀 - 60 min
- [16_mediator](design_pattern/behavioral/16_mediator.md) - 可跳讀 - 60 min
- [17_memento](design_pattern/behavioral/17_memento.md) - 可跳讀 - 60 min
- [18_observer](design_pattern/behavioral/18_observer.md) - 必讀 - 75 min
- [19_state](design_pattern/behavioral/19_state.md) - 必讀 - 75 min
- [20_strategy](design_pattern/behavioral/20_strategy.md) - 必讀 - 60 min
- [21_template_method](design_pattern/behavioral/21_template_method.md) - 必讀 - 60 min
- [22_visitor](design_pattern/behavioral/22_visitor.md) - 可跳讀 - 75 min
- [23_interpreter](design_pattern/behavioral/23_interpreter.md) - 可跳讀 - 60 min
- [24_functional_options](design_pattern/modern/24_functional_options.md) - 必讀 - 75 min
- [25_newtype](design_pattern/modern/25_newtype.md) - 必讀 - 60 min
- [26_typestate](design_pattern/modern/26_typestate.md) - 可跳讀 - 75 min
- [27_repository](design_pattern/modern/27_repository.md) - 可跳讀 - 60 min
- [28_middleware](design_pattern/modern/28_middleware.md) - 可跳讀 - 60 min
- [29_worker_pool](design_pattern/modern/29_worker_pool.md) - 必讀 - 90 min
- [30_circuit_breaker](design_pattern/modern/30_circuit_breaker.md) - 可跳讀 - 75 min
- [31_raii_drop_guard](design_pattern/modern/31_raii_drop_guard.md) - 可跳讀 - 60 min
