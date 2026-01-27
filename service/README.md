# service - ecommerce plan

## Stack chosen

- frontend: Svelte + SvelteKit
- backend: Rust + Axum
- api: REST
- database: PostgreSQL
- db access: sqlx
- payment: ECPay (綠界)
- auth/authorization: ABAC
- background jobs/queue: Kafka
- search: Elasticsearch
- auth/session: JWT
- cache/session store: Redis
- object storage: S3 compatible
- observability: Prometheus/Grafana
- deployment: Docker
- CI/CD: GitHub Actions
- testing: backend tests + frontend tests (split)
- object storage provider: AWS S3
- email/notifications: SendGrid

## Docs

- [PLAN](PLAN.md): 需求、模組、資料模型、API 草案
- `service/openapi.yaml`: REST API skeleton (OpenAPI)
- `service/db/migrations/0001_init.sql`: SQLX migration skeleton

## Remaining tech choices (TBD)

- deployment target: VPS/Fly.io/Render/K8s
