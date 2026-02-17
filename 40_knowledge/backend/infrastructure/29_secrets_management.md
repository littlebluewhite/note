---
title: "Secrets Management / 機密管理"
note_type: knowledge
domain: backend
category: infrastructure
tags: [backend, infrastructure, go, rust, secrets-management]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "29"
level: intermediate
review_interval_days: 14
next_review: 2026-03-03
---

# Secrets Management / 機密管理

## Purpose / 目的

安全地儲存、存取與輪換應用程式機密（密碼、API key、TLS 憑證、連線字串）。避免機密以明文出現在原始碼或日誌中，確保洩漏時可快速輪換並留有稽核軌跡。

## Core Concepts / 核心概念

- **Secrets vs Config**：設定可公開；機密洩漏即有風險，須加密儲存並限制存取。
- **Env Vars（12-Factor）**：機密注入環境變數，簡單但缺輪換與稽核。
- **HashiCorp Vault**：業界標準，支援 dynamic secrets、自動輪換、租約、稽核、多後端（KV/PKI/DB）。
- **AWS Secrets Manager / GCP Secret Manager**：雲端託管，IAM 整合，自動輪換與版本控管。
- **Sealed Secrets + External Secrets Operator**：K8s 環境下從 Vault / 雲端自動同步機密。
- **Secret Rotation**：定期或每次請求產生短生命週期憑證，限制洩漏影響範圍。
- **Zero-Trust Access**：每次存取皆需認證授權，最小權限，全操作稽核。

## Comparison Table / 比較表

| 面向 | Vault | AWS SM | Env Vars | `.env` |
|---|---|---|---|---|
| **安全性** | 高（加密+ACL+稽核） | 高（IAM+KMS） | 中（process 可見） | 低（明文） |
| **輪換** | dynamic secrets | Lambda rotation | 不支援 | 不支援 |
| **稽核** | 完整 | CloudTrail | 無 | 無 |
| **成本** | 自架/HCP 付費 | $0.40/secret/月 | 免費 | 免費 |
| **複雜度** | 高 | 中 | 低 | 極低 |

## Usage Examples / 使用範例

**Rust** — env var + Vault（`vaultrs`）：
```rust
let db_url = std::env::var("DATABASE_URL")?;
// Vault KV v2
let client = VaultClient::new(VaultClientSettingsBuilder::default()
    .address("https://vault:8200").token(std::env::var("VAULT_TOKEN")?).build()?)?;
let secret: HashMap<String, String> = kv2::read(&client, "secret", "myapp/db").await?;
```

**Go** — env var + AWS Secrets Manager：
```go
dbURL := os.Getenv("DATABASE_URL")
cfg, _ := config.LoadDefaultConfig(context.TODO())
out, _ := secretsmanager.NewFromConfig(cfg).GetSecretValue(context.TODO(),
    &secretsmanager.GetSecretValueInput{SecretId: aws.String("myapp/db-password")})
password := *out.SecretString
```

**Kubernetes** — External Secrets Operator：
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
spec:
  refreshInterval: 1h
  secretStoreRef: { name: vault-backend, kind: ClusterSecretStore }
  target: { name: myapp-db-secret }
  data:
    - secretKey: password
      remoteRef: { key: secret/data/myapp/db, property: password }
```

## Decision Guide / 選擇指南

| 規模 | 方案 |
|---|---|
| 小型/個人 | env vars + `.env`（`.gitignore`）+ `direnv` |
| 中型/單一雲端 | 雲端 Secrets Manager（AWS/GCP/Azure），IAM 整合 |
| 大型/多雲 | HashiCorp Vault，統一跨雲機密與動態憑證 |
| Kubernetes | External Secrets Operator + Vault 或雲端 SM |

## Cross-references / 交叉引用

- [[26_oauth2_jwt]] — JWT 簽章金鑰的儲存與輪換是 secrets management 典型場景
- [[27_rbac_abac]] — Vault / SM 存取控制依賴 RBAC/ABAC 限制機密讀取權限

## References / 參考資料

- [HashiCorp Vault](https://developer.hashicorp.com/vault/docs) / [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/) / [GCP Secret Manager](https://cloud.google.com/secret-manager/docs)
- [The Twelve-Factor App — Config](https://12factor.net/config) / [External Secrets Operator](https://external-secrets.io/)
