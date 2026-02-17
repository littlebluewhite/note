---
title: "OAuth2 & JWT / OAuth2 與 JWT"
note_type: knowledge
domain: backend
category: infrastructure
tags: [backend, infrastructure, go, rust, oauth2, jwt, authentication]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "26"
level: intermediate
review_interval_days: 14
next_review: 2026-03-03
---

# OAuth2 & JWT / OAuth2 與 JWT

## Intent / 意圖

為 Web API 建立安全、標準化的認證（Authentication）與授權（Authorization）機制。OAuth2 定義了第三方應用程式如何在不取得使用者密碼的前提下安全地存取受保護資源；JWT 提供自包含、可驗證的 token 格式，使 stateless API 能在不查詢資料庫的情況下驗證身份與權限。

核心目標：**讓分散式系統中的每一個 API 請求都能被可靠地驗證身份、檢查授權，同時維持水平擴展能力，不依賴集中式 session 儲存。**

---

## Problem / 問題情境

**場景一：多服務之間的身份傳遞** -- 電商平台由 API Gateway、訂單、支付、通知服務組成。使用者登入後每個下游服務都需要知道「請求來自誰、有什麼權限」。傳統 session 機制要求每個服務查詢共享 session store（如 Redis），形成單點瓶頸。團隊需要去中心化的身份驗證——token 自身攜帶身份資訊，各服務只需驗證簽章。

**場景二：第三方應用整合的安全困境** -- 平台開放 API 給第三方開發者。早期做法讓使用者提供帳密給第三方，導致：第三方取得完整權限、改密碼後串接失效、無法細分權限範圍。需要 OAuth2 委託授權——使用者只授予特定 scope，可隨時撤回。

**場景三：Token 管理不當的安全事件** -- 團隊將 JWT 存 localStorage，遭 XSS 攻擊後 token 被竊。JWT 有效期 7 天且無 refresh token 機制，攻擊者冒充使用者一整週。JWT 簽發後無法主動撤銷，又沒有黑名單機制。

---

## Core Concepts / 核心概念

### OAuth2 Grant Types / 授權類型

- **Authorization Code**：最安全的流程，適用於有後端的 web 應用。使用者在授權伺服器登入後，authorization code 回傳至 redirect URI，客戶端用 code + client secret 換取 token。
- **Authorization Code + PKCE**：針對 SPA、行動 App 等公開客戶端。請求前產生隨機 `code_verifier`，計算 SHA256 得 `code_challenge`。換 token 時須提供原始 `code_verifier`，即使 code 被攔截也無法換取 token。
- **Client Credentials**：服務對服務（M2M）通訊，客戶端直接用 `client_id` + `client_secret` 取得 token。
- **Refresh Token**：搭配機制。Access token 短暫有效（15 分鐘），refresh token 長期有效（7 天），過期後用 refresh token 換新 token 無需重新登入。

### JWT Structure / JWT 結構

JWT 由 `header.payload.signature` 三部分組成（Base64URL 編碼，`.` 分隔）：

```text
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyXzQyIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

- **Header**：演算法（HS256、RS256、ES256）和型別（JWT）
- **Payload**：claims——關於實體的聲明與元資料
- **Signature**：對 header+payload 的簽章，確保未被竄改

### Standard Claims / 標準宣告

| Claim | 說明 | Claim | 說明 |
|-------|------|-------|------|
| `iss` | 簽發者 | `exp` | 過期時間（Unix timestamp） |
| `sub` | 主體（使用者 ID） | `iat` | 簽發時間 |
| `aud` | 受眾（目標接收者） | `jti` | Token 唯一 ID（防重放攻擊） |

### Access Token vs Refresh Token

| 特性 | Access Token | Refresh Token |
|------|-------------|---------------|
| 有效期 | 短（5-30 分鐘） | 長（數天到數週） |
| 儲存 | 記憶體 / httpOnly cookie | httpOnly + Secure cookie |
| 傳輸 | Authorization header | 僅送往 token endpoint |

### Token Rotation / 令牌輪替

每次用 refresh token 換新 token 時，同時簽發新 refresh token 並使舊的失效。若偵測到已使用過的 token 被重複使用（**reuse detection**），立即撤銷該使用者所有 refresh token。

### JWK / JWKS

公鑰以 JSON 格式發布在 `/.well-known/jwks.json`。Resource server 取得公鑰驗證簽章，透過 `kid` 欄位支援 key rotation。

### Session vs Token-Based Auth

| 特性 | Session-Based | Token-Based (JWT) |
|------|--------------|-------------------|
| 狀態 | Stateful（伺服器儲存） | Stateless（自包含） |
| 擴展 | 需共享 session store | 任意節點可驗證 |
| 撤銷 | 刪除 session 即時生效 | 需黑名單機制 |
| 跨域 | 受 cookie 限制 | Bearer token 天然跨域 |

### OpenID Connect (OIDC)

建構在 OAuth2 之上的身份層。OAuth2 處理授權，OIDC 增加認證（「使用者是誰」）。核心：**ID Token**（含身份資訊的 JWT）、**UserInfo Endpoint**、**Discovery**（`/.well-known/openid-configuration`）。

---

## Architecture / 架構

```mermaid
sequenceDiagram
    participant User as 使用者 (Browser)
    participant Client as 客戶端 (SPA)
    participant AuthServer as 授權伺服器
    participant API as 資源伺服器

    Note over Client: 產生 code_verifier<br/>code_challenge = SHA256(code_verifier)
    User->>Client: 點擊「登入」
    Client->>AuthServer: GET /authorize?response_type=code&client_id=spa_app<br/>&code_challenge=...&code_challenge_method=S256&state=xyz
    AuthServer->>User: 顯示登入頁面
    User->>AuthServer: 輸入帳密 + 同意授權
    AuthServer->>Client: 302 callback?code=AUTH_CODE&state=xyz
    Note over Client: 驗證 state 防 CSRF
    Client->>AuthServer: POST /token (grant_type=authorization_code, code, code_verifier)
    AuthServer->>AuthServer: SHA256(code_verifier) == code_challenge?
    AuthServer->>Client: { access_token, refresh_token, id_token }
    Client->>API: GET /api/orders — Authorization: Bearer <access_token>
    API->>API: 驗證 JWT 簽章 + claims
    API->>Client: 200 OK { orders: [...] }
    Note over Client: access token 過期
    Client->>AuthServer: POST /token (grant_type=refresh_token)
    AuthServer->>Client: { new_access_token, new_refresh_token }
```

```mermaid
flowchart TD
    A[收到 API 請求] --> B{Authorization header?}
    B -->|否| C[401 Unauthorized]
    B -->|是| D[提取 Bearer token]
    D --> E{alg 在允許清單?}
    E -->|否| F[401 Algorithm Not Allowed]
    E -->|是| G[依 kid 取公鑰 → 驗證簽章]
    G -->|失敗| H[401 Invalid Signature]
    G -->|成功| I{exp / iss / aud 有效?}
    I -->|否| J[401 Invalid Claims]
    I -->|是| K{黑名單檢查}
    K -->|已撤銷| L[401 Revoked]
    K -->|通過| M[注入 claims → 繼續處理]
```

---

## How It Works / 運作原理

**1. Issue（簽發）**：認證通過後，授權伺服器建立 JWT payload（sub、iss、aud、exp、roles），私鑰簽章，回傳 access token（exp=15m）和 refresh token（存入 DB 標記 active）。

**2. Verify（驗證）**：Resource server 從 `Authorization: Bearer` 提取 JWT，依 `kid` 從 JWKS 快取取得公鑰驗證簽章，接著檢查 exp、iss、aud、nbf，通過後提取 claims 注入 request context。

**3. Refresh（更新）**：Access token 過期後，客戶端用 refresh token 換新 token。授權伺服器驗證 DB 中 refresh token 為 active，簽發新 access + refresh token（rotation），舊 refresh token 標記 used。

**4. Revoke（撤銷）**：登出時刪除 refresh token。已簽發 access token 的處理：(a) 接受短 exp 內仍可用；(b) 將 jti 加入 Redis 黑名單（TTL = 剩餘有效期）。

---

## Rust 實作

```rust
// Cargo.toml: axum = "0.8", jsonwebtoken = "9", serde, chrono, uuid

use axum::{extract::{FromRequestParts, State}, http::{header::AUTHORIZATION, request::Parts, StatusCode}, response::Json, routing::{get, post}, Router};
use chrono::{Duration, Utc};
use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, TokenData, Validation};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

#[derive(Debug, Serialize, Deserialize, Clone)]
struct TokenClaims {
    sub: String, iss: String, aud: String,
    exp: i64, iat: i64, jti: String,
    roles: Vec<String>,
}

#[derive(Clone)]
struct AppState {
    encoding_key: EncodingKey, decoding_key: DecodingKey,
    issuer: String, audience: String,
}

#[derive(Serialize)]
struct TokenResponse { access_token: String, refresh_token: String, token_type: String, expires_in: i64 }

fn issue_access_token(state: &AppState, user_id: &str, roles: Vec<String>) -> String {
    let now = Utc::now();
    let claims = TokenClaims {
        sub: user_id.into(), iss: state.issuer.clone(), aud: state.audience.clone(),
        exp: (now + Duration::minutes(15)).timestamp(), iat: now.timestamp(),
        jti: uuid::Uuid::new_v4().to_string(), roles,
    };
    encode(&Header::default(), &claims, &state.encoding_key).expect("valid key")
}

fn issue_refresh_token(state: &AppState, user_id: &str) -> String {
    let now = Utc::now();
    let claims = TokenClaims {
        sub: user_id.into(), iss: state.issuer.clone(), aud: state.audience.clone(),
        exp: (now + Duration::days(7)).timestamp(), iat: now.timestamp(),
        jti: uuid::Uuid::new_v4().to_string(), roles: vec![],
    };
    encode(&Header::default(), &claims, &state.encoding_key).expect("valid key")
    // 實務上：將 jti 存入 DB 標記 active
}

// --- JWT Extractor（自動驗證） ---
#[axum::async_trait]
impl FromRequestParts<Arc<AppState>> for TokenClaims {
    type Rejection = StatusCode;
    async fn from_request_parts(parts: &mut Parts, state: &Arc<AppState>) -> Result<Self, Self::Rejection> {
        let header = parts.headers.get(AUTHORIZATION)
            .and_then(|v| v.to_str().ok()).ok_or(StatusCode::UNAUTHORIZED)?;
        let token = header.strip_prefix("Bearer ").ok_or(StatusCode::UNAUTHORIZED)?;

        let mut validation = Validation::default();
        validation.set_issuer(&[&state.issuer]);
        validation.set_audience(&[&state.audience]);

        let data: TokenData<TokenClaims> = decode(token, &state.decoding_key, &validation)
            .map_err(|_| StatusCode::UNAUTHORIZED)?;
        // 實務上：檢查 jti 黑名單
        Ok(data.claims)
    }
}

// --- Handlers ---
async fn login_handler(State(state): State<Arc<AppState>>, Json(req): Json<serde_json::Value>) -> Result<Json<TokenResponse>, StatusCode> {
    // 實務上：bcrypt/argon2 驗證密碼
    let (user, pass) = (req["username"].as_str().unwrap_or(""), req["password"].as_str().unwrap_or(""));
    if user != "engineer" || pass != "secure_password" { return Err(StatusCode::UNAUTHORIZED); }

    let roles = vec!["read:orders".into(), "write:orders".into()];
    Ok(Json(TokenResponse {
        access_token: issue_access_token(&state, "user_42", roles),
        refresh_token: issue_refresh_token(&state, "user_42"),
        token_type: "Bearer".into(), expires_in: 900,
    }))
}

async fn protected_orders(claims: TokenClaims) -> Json<serde_json::Value> {
    Json(serde_json::json!({ "user": claims.sub, "roles": claims.roles }))
}

async fn refresh_handler(State(state): State<Arc<AppState>>, Json(req): Json<serde_json::Value>) -> Result<Json<TokenResponse>, StatusCode> {
    let refresh_str = req["refresh_token"].as_str().ok_or(StatusCode::BAD_REQUEST)?;
    let mut validation = Validation::default();
    validation.set_issuer(&[&state.issuer]);
    validation.set_audience(&[&state.audience]);
    let data = decode::<TokenClaims>(refresh_str, &state.decoding_key, &validation)
        .map_err(|_| StatusCode::UNAUTHORIZED)?;
    // 實務上：DB 確認 jti active → 標記 used（reuse detection）
    let roles = vec!["read:orders".into(), "write:orders".into()];
    Ok(Json(TokenResponse {
        access_token: issue_access_token(&state, &data.claims.sub, roles),
        refresh_token: issue_refresh_token(&state, &data.claims.sub),
        token_type: "Bearer".into(), expires_in: 900,
    }))
}

#[tokio::main]
async fn main() {
    let secret = b"production-should-use-rsa-or-ecdsa-keypair";
    let state = Arc::new(AppState {
        encoding_key: EncodingKey::from_secret(secret), decoding_key: DecodingKey::from_secret(secret),
        issuer: "https://auth.example.com".into(), audience: "https://api.example.com".into(),
    });
    let app = Router::new()
        .route("/auth/login", post(login_handler))
        .route("/auth/refresh", post(refresh_handler))
        .route("/api/orders", get(protected_orders))
        .with_state(state);
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
// Output:
// POST /auth/login  -> { access_token, refresh_token, token_type, expires_in }
// GET  /api/orders   -> 401 or 200 { user, roles }
// POST /auth/refresh -> { new access_token, new refresh_token }
```

---

## Go 實作

```go
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
)

type TokenClaims struct {
	Roles []string `json:"roles"`
	jwt.RegisteredClaims
}

type contextKey string
const claimsKey contextKey = "claims"

var (
	jwtSecret = []byte("production-should-use-rsa-or-ecdsa-keypair")
	iss       = "https://auth.example.com"
	aud       = "https://api.example.com"
)

func issueAccessToken(userID string, roles []string) (string, error) {
	claims := TokenClaims{Roles: roles, RegisteredClaims: jwt.RegisteredClaims{
		Subject: userID, Issuer: iss, Audience: jwt.ClaimStrings{aud},
		ExpiresAt: jwt.NewNumericDate(time.Now().Add(15 * time.Minute)),
		IssuedAt: jwt.NewNumericDate(time.Now()), ID: uuid.New().String(),
	}}
	return jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString(jwtSecret)
}

func issueRefreshToken(userID string) (string, error) {
	claims := TokenClaims{Roles: []string{}, RegisteredClaims: jwt.RegisteredClaims{
		Subject: userID, Issuer: iss, Audience: jwt.ClaimStrings{aud},
		ExpiresAt: jwt.NewNumericDate(time.Now().Add(7 * 24 * time.Hour)),
		IssuedAt: jwt.NewNumericDate(time.Now()), ID: uuid.New().String(),
	}}
	return jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString(jwtSecret)
	// 實務上：將 jti 存入 DB 標記 active
}

// --- JWT Middleware：防禦 algorithm confusion ---
func jwtAuth(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		bearer, found := strings.CutPrefix(r.Header.Get("Authorization"), "Bearer ")
		if !found {
			http.Error(w, `{"error":"missing bearer token"}`, http.StatusUnauthorized)
			return
		}
		token, err := jwt.ParseWithClaims(bearer, &TokenClaims{},
			func(t *jwt.Token) (interface{}, error) {
				if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
					return nil, fmt.Errorf("unexpected alg: %v", t.Header["alg"])
				}
				return jwtSecret, nil
			}, jwt.WithIssuer(iss), jwt.WithAudience(aud), jwt.WithExpirationRequired())
		if err != nil || !token.Valid {
			http.Error(w, `{"error":"invalid token"}`, http.StatusUnauthorized)
			return
		}
		claims := token.Claims.(*TokenClaims)
		// 實務上：檢查 claims.ID 黑名單
		ctx := context.WithValue(r.Context(), claimsKey, claims)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
	var req struct{ Username, Password string }
	json.NewDecoder(r.Body).Decode(&req)
	if req.Username != "engineer" || req.Password != "secure_password" {
		http.Error(w, `{"error":"unauthorized"}`, http.StatusUnauthorized); return
	}
	access, _ := issueAccessToken("user_42", []string{"read:orders", "write:orders"})
	refresh, _ := issueRefreshToken("user_42")
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"access_token": access, "refresh_token": refresh, "token_type": "Bearer", "expires_in": 900,
	})
}

func ordersHandler(w http.ResponseWriter, r *http.Request) {
	claims := r.Context().Value(claimsKey).(*TokenClaims)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{"user": claims.Subject, "roles": claims.Roles})
}

func refreshHandler(w http.ResponseWriter, r *http.Request) {
	var req struct{ RefreshToken string `json:"refresh_token"` }
	json.NewDecoder(r.Body).Decode(&req)
	token, err := jwt.ParseWithClaims(req.RefreshToken, &TokenClaims{},
		func(t *jwt.Token) (interface{}, error) {
			if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected alg")
			}
			return jwtSecret, nil
		}, jwt.WithIssuer(iss), jwt.WithAudience(aud))
	if err != nil { http.Error(w, `{"error":"invalid refresh"}`, http.StatusUnauthorized); return }
	claims := token.Claims.(*TokenClaims)
	// 實務上：DB reuse detection → 撤銷所有 token
	access, _ := issueAccessToken(claims.Subject, []string{"read:orders", "write:orders"})
	refresh, _ := issueRefreshToken(claims.Subject)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"access_token": access, "refresh_token": refresh, "token_type": "Bearer", "expires_in": 900,
	})
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("POST /auth/login", loginHandler)
	mux.HandleFunc("POST /auth/refresh", refreshHandler)
	mux.Handle("GET /api/orders", jwtAuth(http.HandlerFunc(ordersHandler)))
	fmt.Println("listening :3000")
	http.ListenAndServe(":3000", mux)
}
// Output:
// POST /auth/login  -> { access_token, refresh_token, token_type, expires_in }
// GET  /api/orders   -> 401 or 200 { user, roles }
// POST /auth/refresh -> { new access_token, new refresh_token }
```

---

## Rust vs Go 對照表

| 面向 | Rust (Axum + jsonwebtoken) | Go (net/http + golang-jwt) |
|------|---------------------------|---------------------------|
| **Claims 定義** | `#[derive(Serialize, Deserialize)]` struct，serde 自動序列化 | 嵌入 `jwt.RegisteredClaims`，手動定義 JSON tag |
| **Middleware 整合** | `FromRequestParts` trait → handler 參數自動注入 claims | `func(http.Handler) http.Handler` + `context.WithValue` 手動傳遞 |
| **驗證設定** | `Validation` struct 一次設定 issuer/audience/algorithm | `ParseWithClaims` + option functions，需在 key func 手動檢查 alg |
| **錯誤處理** | `Result<T, E>` + `?` 運算子，編譯期強制 | `if err != nil` 逐一檢查，容易遺漏 |
| **類型安全** | 編譯期確保 claims 欄位存在 | 需 `token.Claims.(*TokenClaims)` 型別斷言，執行期可能 panic |

---

## When to Use / 適用場景

**1. 微服務架構的 API 認證**：JWT stateless 特性讓每個服務獨立驗證 token，搭配 JWKS endpoint 實現公鑰分發，無需集中式認證服務。

**2. 第三方 API 整合（OAuth2）**：開放 API 給外部開發者時，authorization code + PKCE 提供安全的委託授權，使用者明確授權特定 scope。

**3. SPA / 行動 App 認證**：公開客戶端使用 PKCE + 短 exp access token + httpOnly cookie refresh token，兼顧安全性與體驗。

---

## When NOT to Use / 不適用場景

**1. 需要即時撤銷的高安全場景**：銀行、醫療系統需立即使 token 失效。JWT stateless 本質使即時撤銷需依賴黑名單（又回到 stateful），opaque token + 集中驗證可能更直接。

**2. Token payload 過大成為瓶頸**：數百個 fine-grained permissions 會讓 JWT 顯著增加每個請求 overhead，應改用 opaque token + 後端權限查詢。

**3. 傳統伺服器端渲染 Web 應用**：MPA 用 cookie-based session 更簡單安全（httpOnly、SameSite），引入 JWT 只增加不必要複雜度。

---

## Real-World Examples / 真實世界案例

**Auth0** -- 全託管 IDaaS。RS256 JWT + JWKS endpoint、refresh token rotation 含 reuse detection、Universal Login 支援社交登入與企業 SSO、Actions pipeline 注入自訂簽發邏輯。

**Keycloak** -- Red Hat 開源 IAM。自建託管，支援 OAuth2/OIDC/SAML 2.0。Admin console 管理 realm/client/role/scope，User Federation 對接 LDAP/AD，微服務透過 JWKS 驗證其簽發的 JWT。

**Firebase Auth** -- Google BaaS 認證。客戶端 SDK 處理 OAuth2 流程，ID token 為標準 JWT，自動 refresh token 管理。適合快速原型，深度客製化需搭配 Cloud Functions。

---

## Interview Questions / 面試常見問題

**Q1: JWT 與 session-based auth 的優缺點？** -- JWT stateless 支援水平擴展和跨域，但無法即時撤銷、token 較大。Session 登出即時生效、ID 很小，但需共享 session store。微服務偏好 JWT，單體應用 session 更簡單。

**Q2: JWT 如何實現 token 撤銷？** -- (1) 短 exp + refresh token rotation：最多等 15 分鐘自然過期；(2) Token 黑名單：jti 存 Redis（TTL = 剩餘有效期）；(3) 版本號機制：JWT 嵌入 token_version，撤銷時遞增，驗證時比對。

**Q3: Algorithm confusion attack 是什麼？如何防禦？** -- 攻擊者改 `alg` 為 HS256，用公開的 RSA 公鑰作 HMAC secret 簽章。防禦：驗證時明確指定允許的演算法白名單，不信任 header 的 `alg`。

**Q4: PKCE 解決什麼問題？** -- 公開客戶端的 authorization code 攔截。即使 code 被劫持，沒有 `code_verifier` 也無法換 token。OAuth 2.1 建議所有客戶端都使用 PKCE。

**Q5: 如何安全地在瀏覽器存 JWT？** -- refresh token 存 httpOnly + Secure + SameSite=Strict cookie，access token 僅存 JS 記憶體。頁面重載時用 refresh cookie 取新 access token。考慮 BFF 模式：前端不持有 token，BFF 代管並用 session cookie 與前端通訊。

---

## Pitfalls / 常見陷阱

**1. JWT 存 localStorage** -- XSS 攻擊可讀取所有 localStorage。httpOnly cookie 無法被 JS 存取。建議：access token 存記憶體，refresh token 存 httpOnly cookie。

**2. 未實作撤銷機制** -- 使用者改密碼、帳號被盜、員工離職後 token 仍有效。至少實作短 exp + refresh token rotation + reuse detection。

**3. Algorithm Confusion Attack** -- 驗證邏輯信任 header `alg` 欄位，攻擊者改 RS256 為 HS256 用公鑰簽章。防禦：`Validation`（Rust）或 key function（Go）中明確檢查演算法。

**4. Payload 放敏感資訊** -- JWT payload 僅 Base64URL 編碼，非加密，任何人可解碼閱讀。不可放密碼、信用卡號。需加密用 JWE。

**5. 未驗證 iss / aud** -- 多環境共用 signing key 時，dev token 可存取 production。必須驗證 `iss` 和 `aud`。

---

## Cross-references / 交叉引用

- [[21_caching_redis_patterns]] -- Token 黑名單可用 Redis 實作，TTL = token 剩餘有效期
- [[23_structured_logging]] -- 認證事件（login、refresh、revocation）的結構化日誌
- [[24_distributed_tracing]] -- Trace context 傳遞使用者身份（sub claim）關聯追蹤

---

## References / 參考資料

- [RFC 6749 - The OAuth 2.0 Authorization Framework](https://datatracker.ietf.org/doc/html/rfc6749)
- [RFC 7519 - JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)
- [RFC 7636 - Proof Key for Code Exchange (PKCE)](https://datatracker.ietf.org/doc/html/rfc7636)
- [RFC 7517 - JSON Web Key (JWK)](https://datatracker.ietf.org/doc/html/rfc7517)
- [OWASP - JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [OWASP - OAuth2 Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [jsonwebtoken crate](https://docs.rs/jsonwebtoken) / [golang-jwt/jwt](https://github.com/golang-jwt/jwt)
