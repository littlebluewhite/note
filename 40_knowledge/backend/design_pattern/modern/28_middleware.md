---
title: "Middleware / 中間件模式"
note_type: knowledge
domain: backend
category: modern
tags: [design-pattern, backend, modern, go, rust, middleware]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: design_pattern
chapter: "28"
level: intermediate
review_interval_days: 14
next_review: 2026-03-03
---

# Middleware / 中間件模式

## Intent / 意圖
> 將請求處理流程中的橫切關注點（logging、認證、限流等）抽取為可組合的獨立處理單元，形成一條可插拔的處理管線。

## Problem / 問題情境
在 HTTP server 或 gRPC service 中，每個請求通常需要經過多個共同的處理步驟：

1. **程式碼重複**：每個 handler 都要手動加上 logging、auth check、error recovery 的程式碼
2. **職責混淆**：業務邏輯和基礎設施邏輯混在同一個函數中
3. **維護困難**：修改 logging 格式需要改動所有 handler
4. **組合困難**：不同的 endpoint 需要不同的中間件組合，hard-coded 的做法無法靈活配置

## Solution / 解決方案
定義一個統一的 handler 介面，中間件是一個接受 handler 並回傳新 handler 的函數（裝飾器）。每個中間件在呼叫下一個 handler 前後可以執行額外邏輯。多個中間件像洋蔥一樣層層包裹，形成處理管線。在 Go 中用 `func(http.Handler) http.Handler`，在 Rust 中用 tower::Layer / tower::Service。

## Structure / 結構

```mermaid
flowchart LR
    Client -->|Request| MW1[Logging MW]
    MW1 -->|Request| MW2[Auth MW]
    MW2 -->|Request| MW3[RateLimit MW]
    MW3 -->|Request| H[Handler]
    H -->|Response| MW3
    MW3 -->|Response| MW2
    MW2 -->|Response| MW1
    MW1 -->|Response| Client

    style MW1 fill:#e1f5fe
    style MW2 fill:#f3e5f5
    style MW3 fill:#fff3e0
    style H fill:#e8f5e9
```

## Participants / 參與者

| 角色 | 職責 |
|------|------|
| **Handler** | 核心業務處理函數，處理請求並產生回應 |
| **Middleware** | 包裝 handler 的函數，在呼叫前後加入橫切邏輯 |
| **Chain / Stack** | 將多個 middleware 組合成處理管線 |
| **Request / Response** | 流經管線的請求與回應物件 |

## Go 實作

```go
package main

import (
	"fmt"
	"log"
	"net/http"
	"net/http/httptest"
	"time"
)

// --- Middleware 型別 ---

// Middleware 接受一個 Handler 並回傳一個新的 Handler
type Middleware func(http.Handler) http.Handler

// --- Logging Middleware ---

func Logging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		log.Printf("--> %s %s", r.Method, r.URL.Path)

		next.ServeHTTP(w, r)

		log.Printf("<-- %s %s (%s)", r.Method, r.URL.Path, time.Since(start))
	})
}

// --- Auth Middleware ---

func Auth(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		token := r.Header.Get("Authorization")
		if token == "" {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}
		log.Printf("    [Auth] token=%s", token)
		next.ServeHTTP(w, r)
	})
}

// --- Recovery Middleware ---

func Recovery(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				log.Printf("    [Recovery] panic: %v", err)
				http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			}
		}()
		next.ServeHTTP(w, r)
	})
}

// --- Chain 組合多個 Middleware ---

func Chain(handler http.Handler, middlewares ...Middleware) http.Handler {
	// 從最後一個 middleware 開始包裝，確保執行順序正確
	for i := len(middlewares) - 1; i >= 0; i-- {
		handler = middlewares[i](handler)
	}
	return handler
}

// --- 業務 Handler ---

func helloHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Hello, World!")
}

func main() {
	// 組合 middleware chain: Recovery -> Logging -> Auth -> Handler
	handler := Chain(
		http.HandlerFunc(helloHandler),
		Recovery,
		Logging,
		Auth,
	)

	// 模擬請求（使用 httptest）
	fmt.Println("=== Request without auth ===")
	req1 := httptest.NewRequest("GET", "/api/hello", nil)
	rec1 := httptest.NewRecorder()
	handler.ServeHTTP(rec1, req1)
	fmt.Printf("Status: %d, Body: %s\n", rec1.Code, rec1.Body.String())

	fmt.Println("=== Request with auth ===")
	req2 := httptest.NewRequest("GET", "/api/hello", nil)
	req2.Header.Set("Authorization", "Bearer token123")
	rec2 := httptest.NewRecorder()
	handler.ServeHTTP(rec2, req2)
	fmt.Printf("Status: %d, Body: %s\n", rec2.Code, rec2.Body.String())
}

// Output:
// === Request without auth ===
// --> GET /api/hello
// <-- GET /api/hello (...)
// Status: 401, Body: Unauthorized
//
// === Request with auth ===
// --> GET /api/hello
//     [Auth] token=Bearer token123
// <-- GET /api/hello (...)
// Status: 200, Body: Hello, World!
```

## Rust 實作

```rust
use std::fmt;
use std::time::Instant;

// --- 簡化的 Request / Response ---

#[derive(Debug, Clone)]
struct Request {
    method: String,
    path: String,
    headers: Vec<(String, String)>,
}

impl Request {
    fn new(method: &str, path: &str) -> Self {
        Self {
            method: method.to_string(),
            path: path.to_string(),
            headers: Vec::new(),
        }
    }

    fn header(mut self, key: &str, value: &str) -> Self {
        self.headers.push((key.to_string(), value.to_string()));
        self
    }

    fn get_header(&self, key: &str) -> Option<&str> {
        self.headers
            .iter()
            .find(|(k, _)| k == key)
            .map(|(_, v)| v.as_str())
    }
}

#[derive(Debug)]
struct Response {
    status: u16,
    body: String,
}

impl fmt::Display for Response {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Status: {}, Body: {}", self.status, self.body)
    }
}

// --- Handler trait ---

trait Handler: Send + Sync {
    fn handle(&self, req: &Request) -> Response;
}

// 允許 closure 作為 Handler
impl<F> Handler for F
where
    F: Fn(&Request) -> Response + Send + Sync,
{
    fn handle(&self, req: &Request) -> Response {
        self(req)
    }
}

// --- Middleware 實作 ---

// Logging middleware
struct LoggingMiddleware<H: Handler> {
    next: H,
}

impl<H: Handler> Handler for LoggingMiddleware<H> {
    fn handle(&self, req: &Request) -> Response {
        let start = Instant::now();
        println!("--> {} {}", req.method, req.path);

        let resp = self.next.handle(req);

        println!(
            "<-- {} {} ({:?}) [{}]",
            req.method,
            req.path,
            start.elapsed(),
            resp.status
        );
        resp
    }
}

// Auth middleware
struct AuthMiddleware<H: Handler> {
    next: H,
}

impl<H: Handler> Handler for AuthMiddleware<H> {
    fn handle(&self, req: &Request) -> Response {
        match req.get_header("Authorization") {
            Some(token) => {
                println!("    [Auth] token={token}");
                self.next.handle(req)
            }
            None => Response {
                status: 401,
                body: "Unauthorized".to_string(),
            },
        }
    }
}

// --- Chain builder ---

fn with_logging<H: Handler>(handler: H) -> LoggingMiddleware<H> {
    LoggingMiddleware { next: handler }
}

fn with_auth<H: Handler>(handler: H) -> AuthMiddleware<H> {
    AuthMiddleware { next: handler }
}

// --- 業務 Handler ---

fn hello_handler(req: &Request) -> Response {
    Response {
        status: 200,
        body: format!("Hello from {}!", req.path),
    }
}

fn main() {
    // 組合: Logging -> Auth -> Handler
    // 注意：最外層最先執行
    let handler = with_logging(with_auth(hello_handler));

    println!("=== Request without auth ===");
    let req1 = Request::new("GET", "/api/hello");
    let resp1 = handler.handle(&req1);
    println!("{resp1}\n");

    println!("=== Request with auth ===");
    let req2 = Request::new("GET", "/api/hello").header("Authorization", "Bearer token123");
    let resp2 = handler.handle(&req2);
    println!("{resp2}");
}

// Output:
// === Request without auth ===
// --> GET /api/hello
//     [Auth] token missing
// <-- GET /api/hello (...) [401]
// Status: 401, Body: Unauthorized
//
// === Request with auth ===
// --> GET /api/hello
//     [Auth] token=Bearer token123
// <-- GET /api/hello (...) [200]
// Status: 200, Body: Hello from /api/hello!
```

## Go vs Rust 對照表

| 面向 | Go | Rust |
|------|----|----|
| Handler 抽象 | `http.Handler` interface | `tower::Service` trait 或自定義 trait |
| Middleware 簽名 | `func(http.Handler) http.Handler` | `tower::Layer` 或泛型 struct wrapping |
| 組合方式 | 函數鏈式呼叫 `f(g(h))` | `ServiceBuilder::new().layer(a).layer(b)` |
| 非同步支援 | 原生（goroutine per request） | `async fn` + `Pin<Box<dyn Future>>` |
| 型別安全 | 弱（`interface{}` context） | 強（泛型保留完整型別資訊） |
| 生態系統 | `net/http`, chi, gin, echo | tower, axum, actix-web |

## When to Use / 適用場景

- HTTP/gRPC server 需要統一的 logging、tracing、auth、rate limiting 等橫切邏輯
- 不同的 API endpoint 需要不同的中間件組合（如公開 API vs 內部 API）
- 需要在不修改業務邏輯的情況下增加新的處理步驟

## When NOT to Use / 不適用場景

- 只有一兩個簡單的 handler，沒有共同的處理邏輯 -- 直接寫在 handler 裡更簡單
- 中間件之間有複雜的資料依賴關係（如後面的 middleware 依賴前面 middleware 解析的結果） -- 會讓 context 傳遞變得混亂
- 非請求/回應模式的處理流程（如 event streaming） -- 應考慮 pipeline 或 observer 模式

## Real-World Examples / 真實世界案例

- **Go `net/http`**：標準庫的 `http.Handler` interface 天然支援 middleware wrapping，是 Go 生態系中最廣泛使用的模式
- **Go `chi` router**：`r.Use(middleware.Logger, middleware.Recoverer)` 提供豐富的內建 middleware
- **Rust `tower`**：Tokio 生態的 middleware 框架，`axum` 和 `tonic`（gRPC）都建構在 tower 之上
- **Rust `actix-web`**：`App::new().wrap(Logger::default()).wrap(auth_middleware)` 提供 actor-based middleware

## Related Patterns / 相關模式

- **Chain of Responsibility (GoF)**：Middleware 是 CoR 的現代實現，每個 middleware 決定是否將請求傳遞給下一個
- **Decorator (GoF)**：Middleware 在結構上就是 Decorator -- 包裝 handler 並增強功能
- **Strategy (GoF)**：不同的 middleware 組合可視為不同的處理策略

## Pitfalls / 常見陷阱

1. **執行順序混淆**：Middleware 的包裝順序和執行順序相反。`Chain(handler, A, B, C)` 的執行順序是 A -> B -> C -> handler -> C -> B -> A，常被搞混
2. **Context 汙染**：Go 中習慣用 `context.WithValue` 在 middleware 間傳遞資料，但 key 衝突和型別斷言容易出錯
3. **錯誤處理不一致**：某些 middleware 直接回傳錯誤（如 auth 401），某些記錄後繼續。需要統一的錯誤處理策略
4. **效能開銷累積**：每增加一層 middleware 就增加一層函數呼叫。在極高吞吐量場景（>100K RPS），過多 middleware 層可能成為瓶頸

## References / 參考資料

- Go `net/http` package documentation: https://pkg.go.dev/net/http
- Mat Ryer, "Writing Middleware in Go": https://medium.com/@matryer/writing-middleware-in-golang-and-how-go-makes-it-so-much-fun-4375c1246e81
- Tower (Rust): https://docs.rs/tower/latest/tower/
- Axum middleware guide: https://docs.rs/axum/latest/axum/middleware/index.html
