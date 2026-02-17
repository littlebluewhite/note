---
title: "OWASP & API Security / API 安全"
note_type: knowledge
domain: backend
category: infrastructure
tags: [backend, infrastructure, go, rust, owasp, api-security]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "28"
level: intermediate
review_interval_days: 14
next_review: 2026-03-03
---

# OWASP & API Security / API 安全

## Purpose / 目的

識別並防禦常見的 API 安全弱點。本篇以 OWASP API Security Top 10 為基礎，聚焦於後端工程師日常最容易疏忽的攻擊面——包括物件層級授權缺陷（BOLA）、認證機制破損、過度資料曝露、大量賦值、SSRF 及注入攻擊。每個弱點皆附上 Rust（Axum）與 Go 的「有漏洞 vs 修復後」程式碼，讓團隊在 code review 時能快速對照檢查。

---

## Symptoms / 常見症狀

| 症狀 | 可能弱點 |
|------|----------|
| 一般使用者可存取其他人的資料（修改 URL 中的 ID 即可） | BOLA（Broken Object Level Authorization） |
| 暴力嘗試登入無限制，帳號被大量鎖定 | Broken Authentication / 缺少 rate limiting |
| API 回應包含密碼 hash、內部 ID、敏感欄位 | Excessive Data Exposure |
| 前端未送出的欄位（如 `is_admin`）在 POST 時被寫入 | Mass Assignment |
| 伺服器對外發出非預期的 HTTP 請求 | SSRF（Server-Side Request Forgery） |
| 日誌中出現 `' OR 1=1 --` 等異常字串 | SQL / NoSQL Injection |
| 認證 token 過期時間極長或可被重播（replay） | JWT 配置不當 |

---

## Diagnostic Steps / 診斷步驟

按以下清單逐項檢查，每項標註嚴重等級（P0 = 立即修復，P1 = 一週內，P2 = 下個 sprint）：

1. **P0 — 授權中介層審查**：確認每個需要保護的路由都套用了 auth middleware，且在 handler 內部驗證「請求者是否有權操作該筆資源」。
2. **P0 — 輸入驗證**：所有使用者輸入是否經過型別檢查、長度限制、白名單過濾？特別注意 JSON body 中的巢狀物件與陣列。
3. **P0 — 注入測試**：對 SQL/NoSQL 查詢參數送入惡意 payload，確認系統使用參數化查詢而非字串拼接。
4. **P1 — Rate Limiting**：驗證登入、OTP 驗證、密碼重設等端點有請求速率限制。
5. **P1 — 錯誤回應資訊洩漏**：檢查 4xx/5xx 回應是否包含 stack trace、資料庫錯誤訊息、內部路徑。
6. **P2 — 回應欄位過濾**：API 回應是否只回傳前端需要的欄位？是否有 `SELECT *` 直接序列化到回應的情況？
7. **P2 — 依賴套件掃描**：定期執行 `cargo audit`（Rust）或 `govulncheck`（Go）檢查已知漏洞。

---

## Detection Commands / 偵測指令

```bash
# 1) 測試 BOLA：用 user_A 的 token 存取 user_B 資源，期望 403
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer <USER_A_TOKEN>" \
  https://api.example.com/v1/users/USER_B_ID/orders

# 2) 測試 SQL Injection
curl -s -H "Content-Type: application/json" \
  -d '{"username": "admin'\'' OR 1=1 --", "password": "x"}' \
  https://api.example.com/v1/login

# 3) 測試 Rate Limiting：連續 50 次，期望後半段出現 429
for i in $(seq 1 50); do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -d '{"email":"test@x.com","password":"wrong"}' \
    https://api.example.com/v1/login
done | sort | uniq -c

# 4) Log 分析：偵測注入嘗試與大量 403
grep -E "(OR\s+1=1|UNION\s+SELECT|<script>)" /var/log/api/access.log
awk '$9 == 403 {print $1}' /var/log/api/access.log | sort | uniq -c | sort -rn | head

# 5) OWASP ZAP 自動掃描
docker run -t zaproxy/zap-stable zap-baseline.py -t https://api.example.com -J report.json
```

---

## Common Causes & Resolutions / 常見原因與解法

### 1. BOLA — Broken Object Level Authorization

最常見的 API 弱點。攻擊者修改路徑或查詢參數中的資源 ID，即可存取不屬於自己的資料。

**Rust (Axum) — 有漏洞的寫法：**

```rust
async fn get_order(Path(order_id): Path<Uuid>) -> impl IntoResponse {
    // 危險：未驗證 order 是否屬於當前使用者
    let order = db::find_order(order_id).await?;
    Json(order)
}
```

**Rust (Axum) — 修復後：**

```rust
async fn get_order(
    State(state): State<AppState>,
    Extension(current_user): Extension<AuthUser>,
    Path(order_id): Path<Uuid>,
) -> Result<Json<OrderResponse>, ApiError> {
    let order = state.db.find_order(order_id).await?;
    if order.user_id != current_user.id {
        return Err(ApiError::Forbidden("無權存取此訂單"));
    }
    Ok(Json(OrderResponse::from(order))) // 使用 DTO 過濾欄位
}
```

**Go — 修復後：**

```go
func (h *Handler) GetOrder(w http.ResponseWriter, r *http.Request) {
    userID := r.Context().Value(ctxKeyUserID).(uuid.UUID)
    orderID := chi.URLParam(r, "orderID")

    order, err := h.store.FindOrder(r.Context(), orderID)
    if err != nil { writeError(w, http.StatusNotFound, "order not found"); return }

    if order.UserID != userID {
        writeError(w, http.StatusForbidden, "access denied")
        return
    }
    writeJSON(w, http.StatusOK, toOrderResponse(order))
}
```

### 2. Broken Authentication

Token 缺乏過期機制、未驗證簽章演算法、或允許弱密碼。詳見 [[26_oauth2_jwt]]。

**Go — 拒絕 `alg: none` 攻擊：**

```go
token, err := jwt.ParseWithClaims(tokenStr, &Claims{}, func(t *jwt.Token) (interface{}, error) {
    if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
        return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
    }
    return []byte(os.Getenv("JWT_SECRET")), nil
})
```

### 3. Excessive Data Exposure / Mass Assignment

直接序列化 DB model 會洩漏敏感欄位；直接 bind 請求 body 到 DB model 會被塞入 `is_admin` 等欄位。解法相同：**使用專屬的 input/output DTO**。

**Rust — Response DTO：**

```rust
#[derive(Serialize)]
struct UserResponse { id: Uuid, email: String, created_at: DateTime<Utc> }
// 不包含 password_hash、internal_score 等欄位
impl From<User> for UserResponse {
    fn from(u: User) -> Self { Self { id: u.id, email: u.email, created_at: u.created_at } }
}
```

**Go — Input DTO（防止 mass assignment）：**

```go
type UpdateProfileInput struct {
    Name  string `json:"name" validate:"required,max=100"`
    Email string `json:"email" validate:"required,email"`
    // 不含 is_admin、role 等欄位，攻擊者無法透過 JSON 覆寫
}
```

### 4. SSRF — Server-Side Request Forgery

使用者控制的 URL 被伺服器直接 fetch，可存取內網服務（如 `http://169.254.169.254/`）。

**Rust — 白名單驗證：**

```rust
fn validate_url(input: &str) -> Result<Url, ApiError> {
    let url = Url::parse(input).map_err(|_| ApiError::BadRequest("invalid URL"))?;
    let allowed = ["cdn.example.com", "images.example.com"];
    match url.host_str() {
        Some(host) if url.scheme() == "https" && allowed.contains(&host) => Ok(url),
        _ => Err(ApiError::BadRequest("URL domain not allowed")),
    }
}
```

### 5. Injection (SQL)

字串拼接建構查詢是最經典的安全漏洞。一律使用參數化查詢。

**Rust (sqlx) — 有漏洞 vs 修復：**

```rust
// 危險：字串拼接
let q = format!("SELECT * FROM users WHERE name = '{}'", user_input);
sqlx::query(&q).fetch_all(&pool).await?;

// 安全：參數化查詢
sqlx::query_as::<_, User>("SELECT * FROM users WHERE name = $1")
    .bind(&user_input)
    .fetch_all(&pool)
    .await?;
```

---

## Prevention Checklist / 預防清單

- [ ] 所有路由套用認證 middleware（參考 [[26_oauth2_jwt]]）
- [ ] Handler 內部驗證資源所有權（BOLA 防護）
- [ ] 每個 endpoint 使用獨立的 input/output DTO，禁止直接序列化 DB model
- [ ] SQL/NoSQL 一律使用參數化查詢，禁止字串拼接
- [ ] 登入、OTP、密碼重設端點配置 rate limiting（如 IP + 帳號雙維度）
- [ ] CORS 設定只允許特定 origin，避免 `Access-Control-Allow-Origin: *`
- [ ] 加入安全 headers：`X-Content-Type-Options: nosniff`、`Strict-Transport-Security`、`X-Frame-Options: DENY`
- [ ] 錯誤回應不暴露 stack trace 或內部路徑，僅回傳標準化錯誤碼
- [ ] 定期執行依賴掃描：`cargo audit`（Rust）、`govulncheck ./...`（Go）
- [ ] JWT 強制驗證 `alg` 欄位，設定合理的過期時間（access token <= 15 分鐘）
- [ ] 對外發出的 HTTP 請求驗證目標 URL（SSRF 防護），禁止存取 `169.254.x.x` 等內網位址
- [ ] 啟用 RBAC/ABAC 授權策略（參考 [[27_rbac_abac]]）

---

## References / 參考資料

- [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)

---

## Cross-references / 交叉引用

- [[26_oauth2_jwt]] — JWT 簽章驗證、token 過期策略、refresh token rotation
- [[27_rbac_abac]] — 角色與屬性存取控制模型，搭配 BOLA 防護確保每筆資源都有授權檢查
