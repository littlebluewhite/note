---
title: Backend Coverage Matrix
note_type: system
domain: backend
tags: [system, backend, audit]
created: 2026-02-17
updated: 2026-02-17
status: active
source: system
---
# Backend Coverage Matrix

## Coverage Status (2026-02-18)

| Capability Area | Required Topic | Coverage Files | Status |
| --- | --- | --- | --- |
| System Design | Scalability | `system_design/01_scalability_fundamentals.md` | Done |
| System Design | Availability | `system_design/02_availability_and_fault_tolerance.md` | Done |
| System Design | Consistency | `system_design/03_consistency_trade_offs.md` | Done |
| System Design | REST API Design | `system_design/04_api_design_rest.md` | Done |
| System Design | gRPC & GraphQL | `system_design/05_api_design_grpc_graphql.md` | Done |
| System Design | API Versioning | `system_design/06_api_versioning.md` | Done |
| System Design | Microservices vs Monolith | `system_design/07_microservices_vs_monolith.md` | Done |
| System Design | Event-Driven Architecture | `system_design/08_event_driven_architecture.md` | Done |
| System Design | CQRS & Event Sourcing | `system_design/09_cqrs_event_sourcing.md` | Done |
| System Design | DDD Basics | `system_design/10_ddd_basics.md` | Done |
| System Design | Interview Framework | `system_design/11_system_design_interview.md` | Done |
| Distributed Systems | CAP & Consistency | `distributed_systems/12_cap_consistency_models.md` | Done |
| Distributed Systems | Saga Pattern | `distributed_systems/13_saga_pattern.md` | Done |
| Distributed Systems | Two-Phase Commit | `distributed_systems/14_two_phase_commit.md` | Done |
| Distributed Systems | Distributed Locking | `distributed_systems/15_distributed_locking.md` | Done |
| Distributed Systems | Message Queue | `distributed_systems/16_message_queue_fundamentals.md` | Done |
| Distributed Systems | Kafka Deep Dive | `distributed_systems/17_kafka_deep_dive.md` | Done |
| Distributed Systems | Kafka Operations | `distributed_systems/18_kafka_operations.md` | Done |
| Distributed Systems | Idempotency | `distributed_systems/19_idempotency_design.md` | Done |
| Distributed Systems | Rate Limiting | `distributed_systems/20_rate_limiting.md` | Done |
| Infrastructure | Caching & Redis | `infrastructure/21_caching_redis_patterns.md` | Done |
| Infrastructure | Cache Invalidation | `infrastructure/22_cache_invalidation.md` | Done |
| Infrastructure | Structured Logging | `infrastructure/23_structured_logging.md` | Done |
| Infrastructure | Distributed Tracing | `infrastructure/24_distributed_tracing.md` | Done |
| Infrastructure | Metrics & SLI/SLO/SLA | `infrastructure/25_metrics_sli_slo_sla.md` | Done |
| Infrastructure | OAuth2 & JWT | `infrastructure/26_oauth2_jwt.md` | Done |
| Infrastructure | RBAC & ABAC | `infrastructure/27_rbac_abac.md` | Done |
| Infrastructure | OWASP & API Security | `infrastructure/28_owasp_api_security.md` | Done |
| Infrastructure | Secrets Management | `infrastructure/29_secrets_management.md` | Done |
| Infrastructure | HTTP/2, HTTP/3 & gRPC | `infrastructure/30_http2_http3_grpc_transport.md` | Done |
| Infrastructure | WebSocket, TLS & mTLS | `infrastructure/31_websocket_tls_mtls.md` | Done |
| Infrastructure | Load Balancing | `infrastructure/32_load_balancing_service_discovery.md` | Done |
| Engineering | Testing Strategy | `engineering/33_testing_strategy.md` | Done |
| Engineering | Integration & Contract Testing | `engineering/34_integration_contract_testing.md` | Done |
| Engineering | Load Testing | `engineering/35_load_testing.md` | Done |
| Engineering | Concurrency Patterns | `engineering/36_concurrency_patterns.md` | Done |
| Engineering | Performance Profiling | `engineering/37_performance_profiling.md` | Done |
| Engineering | Connection Pooling | `engineering/38_connection_pooling.md` | Done |
| Engineering | Error Handling & Retry | `engineering/39_error_handling_retry.md` | Done |
| Engineering | CI/CD & Deployment | `engineering/40_cicd_deployment.md` | Done |
| Infrastructure | Kubernetes Core Concepts | `infrastructure/41_kubernetes_core_concepts.md` | Done |
| Infrastructure | Service Mesh | `infrastructure/42_service_mesh.md` | Done |
| Distributed Systems | Sharding & Partitioning | `distributed_systems/43_sharding_partitioning.md` | Done |
| Distributed Systems | Database Replication | `distributed_systems/44_database_replication.md` | Done |
| System Design | NoSQL Selection Guide | `system_design/45_nosql_selection_guide.md` | Done |
| Engineering | Chaos Engineering | `engineering/46_chaos_engineering.md` | Done |
| Engineering | Incident Management & DR | `engineering/47_incident_management_disaster_recovery.md` | Done |
| Distributed Systems | Consensus Algorithms | `distributed_systems/48_consensus_algorithms.md` | Done |
| Distributed Systems | Leader Election & Scheduling | `distributed_systems/49_leader_election_distributed_scheduling.md` | Done |
| Infrastructure | Infrastructure as Code | `infrastructure/50_infrastructure_as_code.md` | Done |
| Infrastructure | GitOps | `infrastructure/51_gitops.md` | Done |
| Distributed Systems | Stream Processing | `distributed_systems/52_stream_processing.md` | Done |
| Distributed Systems | Batch Processing | `distributed_systems/53_batch_processing.md` | Done |
| System Design | Architecture Supplement Patterns | `system_design/54_architecture_supplement_patterns.md` | Done |
| Engineering | Zero-Downtime Schema Migration | `engineering/55_zero_downtime_schema_migration.md` | Done |
| Engineering | Feature Flags | `engineering/56_feature_flags.md` | Done |

## Cross-references with Existing Content

- `database/transactions.md` <-> `distributed_systems/13_saga_pattern.md`
- `database/postgres_lock_troubleshooting.md` <-> `distributed_systems/15_distributed_locking.md`
- `design_pattern/modern/30_circuit_breaker.md` <-> `engineering/39_error_handling_retry.md`
- `design_pattern/modern/27_repository.md` <-> `system_design/10_ddd_basics.md`
- `design_pattern/modern/29_worker_pool.md` <-> `engineering/36_concurrency_patterns.md`
- `design_pattern/modern/28_middleware.md` <-> `infrastructure/24_distributed_tracing.md`
- `rust/17_3-17_6` <-> `engineering/36_concurrency_patterns.md`
- `database/indexing.md` <-> `distributed_systems/43_sharding_partitioning.md`
- `database/transactions.md` <-> `distributed_systems/44_database_replication.md`
- `database/postgres_lock_troubleshooting.md` <-> `engineering/55_zero_downtime_schema_migration.md`

## Remaining Gaps

- 全部 56 篇已建立完成（2026-02-18）。
- 建議後續補充：至少 1 組 Rust Axum + 1 組 Go 的實際 production 專案程式碼連結。
