---
title: "WebSocket, TLS & mTLS / WebSocket、TLS 與 mTLS"
note_type: knowledge
domain: backend
category: infrastructure
tags: [backend, infrastructure, go, rust, websocket, tls, mtls]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "31"
level: advanced
review_interval_days: 14
next_review: 2026-03-03
---

# WebSocket, TLS & mTLS / WebSocket、TLS 與 mTLS

## Purpose / 目的

本文件旨在提供 WebSocket 連線生命週期、TLS 加密傳輸以及 mTLS 雙向認證的疑難排解指南。涵蓋範圍包括：

- **WebSocket 生命週期**：從 HTTP Upgrade 握手到持久連線的建立、維持與關閉流程。
- **TLS (Transport Layer Security)**：確保傳輸層加密，防止中間人攻擊與資料竊聽。
- **mTLS (Mutual TLS)**：在服務間通訊中要求雙方出示憑證，實現零信任架構下的身份驗證。

這三者經常在微服務架構中交互作用：WebSocket 透過 `wss://` 建立加密連線，而服務網格 (service mesh) 內部則透過 mTLS 確保每一次呼叫都經過身份驗證。

---

## Symptoms / 常見症狀

| 症狀 | 可能原因 |
|------|---------|
| WebSocket 連線建立後立即斷開 | Load balancer 未轉發 `Upgrade` 標頭 |
| `wss://` 連線失敗，`ws://` 正常 | 憑證鏈不完整或已過期 |
| TLS handshake failure (`ERR_SSL_PROTOCOL_ERROR`) | TLS 版本不匹配或密碼套件不支援 |
| mTLS 連線被拒 (`certificate required`) | 客戶端未提供憑證或 CA 不被信任 |
| 瀏覽器報 mixed content 錯誤 | HTTPS 頁面嘗試建立 `ws://` 而非 `wss://` 連線 |
| 連線閒置後逾時斷開 | Proxy 或 load balancer 的 idle timeout 設定過短 |
| `certificate verify failed` 錯誤 | 自簽憑證未加入信任存儲，或中繼 CA 憑證缺失 |

---

## Diagnostic Steps / 診斷步驟

### Step 1: 確認憑證鏈完整性

驗證伺服器憑證是否包含完整的中繼 CA 鏈，避免客戶端無法建立信任路徑。

### Step 2: 驗證 WebSocket Upgrade 標頭

確認 HTTP 請求中包含 `Connection: Upgrade` 與 `Upgrade: websocket` 標頭，且 load balancer / reverse proxy 正確轉發這些標頭。

### Step 3: 測試 TLS 連線

使用 `openssl s_client` 連線到目標伺服器，檢查回傳的憑證資訊、TLS 版本與密碼套件。

### Step 4: 驗證 mTLS 客戶端憑證

確認客戶端憑證由伺服器信任的 CA 簽發，且憑證尚未過期或被撤銷。

### Step 5: 檢查日誌

查看伺服器端、load balancer 與 proxy 的日誌，搜尋 `handshake`、`upgrade`、`certificate` 相關關鍵字。

---

## Detection Commands / 偵測指令

### 檢查憑證鏈與到期日

```bash
# 查看伺服器憑證完整資訊
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -dates -subject -issuer

# 檢查憑證到期時間
echo | openssl s_client -connect example.com:443 2>/dev/null \
  | openssl x509 -noout -enddate

# 驗證憑證鏈完整性
openssl s_client -connect example.com:443 -showcerts </dev/null 2>&1 \
  | grep -E "depth|verify"
```

### 測試 WebSocket 連線

```bash
# 使用 curl 測試 WebSocket upgrade（curl 7.86+）
curl -i --no-buffer \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  https://example.com/ws

# 使用 websocat 測試
websocat wss://example.com/ws
```

### 測試 mTLS 連線

```bash
# 以客戶端憑證連線
openssl s_client -connect example.com:443 \
  -cert client.crt -key client.key -CAfile ca.crt

# 驗證伺服器是否要求客戶端憑證
openssl s_client -connect example.com:443 </dev/null 2>&1 \
  | grep "Acceptable client certificate"
```

### 驗證 Nginx mTLS 設定

```bash
# 確認 Nginx 設定中的 mTLS 指令
nginx -T 2>/dev/null | grep -E "ssl_client_certificate|ssl_verify_client|proxy_set_header.*Upgrade"
```

---

## Common Causes & Resolutions / 常見原因與解法

### 1. Load Balancer 未轉發 WebSocket Upgrade 標頭

許多 L7 load balancer 預設不會轉發 `Connection: Upgrade` 標頭，導致 WebSocket 握手失敗。

**Nginx 設定修正：**

```nginx
location /ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400s;  # 避免閒置逾時
}
```

### 2. 憑證過期 — 自動化輪替

使用 cert-manager 或 Let's Encrypt 自動化憑證管理，避免人工維護疏忽。

### 3. mTLS 客戶端憑證不被信任（CA Bundle 不一致）

伺服器端的 `ssl_client_certificate` 必須包含簽發客戶端憑證的 CA。當使用中繼 CA 時，需將完整 CA 鏈合併為一個 bundle 檔案。

### 4. TLS 版本不匹配

現代服務應至少支援 TLS 1.2，優先使用 TLS 1.3。停用 TLS 1.0/1.1 以避免已知弱點。

### 5. Rust WebSocket + TLS 範例（tokio-tungstenite + rustls）

```rust
use std::sync::Arc;
use tokio_tungstenite::connect_async_tls_with_config;
use tokio_tungstenite::Connector;
use rustls::{ClientConfig, RootCertStore};

async fn connect_wss() -> anyhow::Result<()> {
    // 建立 TLS 設定，載入系統根憑證
    let mut root_store = RootCertStore::empty();
    root_store.extend(webpki_roots::TLS_SERVER_ROOTS.iter().cloned());

    let tls_config = ClientConfig::builder()
        .with_root_certificates(root_store)
        .with_no_client_auth();

    let connector = Connector::Rustls(Arc::new(tls_config));
    let url = "wss://example.com/ws";

    let (ws_stream, response) = connect_async_tls_with_config(
        url, None, false, Some(connector),
    ).await?;

    println!("WebSocket 連線已建立，HTTP 狀態: {}", response.status());
    // ws_stream 可用於 send/receive 訊息
    Ok(())
}
```

### 6. Rust mTLS 客戶端範例（rustls）

```rust
use std::sync::Arc;
use std::fs;
use rustls::{ClientConfig, RootCertStore};
use rustls::pki_types::{CertificateDer, PrivateKeyDer};
use rustls_pemfile::{certs, private_key};

fn build_mtls_config() -> anyhow::Result<ClientConfig> {
    // 載入 CA 憑證
    let ca_pem = fs::read("ca.crt")?;
    let mut root_store = RootCertStore::empty();
    for cert in certs(&mut ca_pem.as_slice()) {
        root_store.add(cert?)?;
    }

    // 載入客戶端憑證與私鑰
    let cert_pem = fs::read("client.crt")?;
    let client_certs: Vec<CertificateDer<'static>> = certs(&mut cert_pem.as_slice())
        .collect::<Result<_, _>>()?;

    let key_pem = fs::read("client.key")?;
    let client_key: PrivateKeyDer<'static> = private_key(&mut key_pem.as_slice())?
        .ok_or_else(|| anyhow::anyhow!("找不到私鑰"))?;

    let config = ClientConfig::builder()
        .with_root_certificates(root_store)
        .with_client_auth_cert(client_certs, client_key)?;

    Ok(config)
}
```

### 7. Go WebSocket + TLS 範例（gorilla/websocket）

```go
package main

import (
	"crypto/tls"
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

func connectWSS() error {
	// TLS 設定：指定最低版本為 TLS 1.2
	tlsConfig := &tls.Config{
		MinVersion: tls.VersionTLS12,
	}

	dialer := websocket.Dialer{
		TLSClientConfig: tlsConfig,
	}

	header := http.Header{}
	conn, resp, err := dialer.Dial("wss://example.com/ws", header)
	if err != nil {
		return fmt.Errorf("WebSocket 連線失敗: %w", err)
	}
	defer conn.Close()

	log.Printf("連線成功，HTTP 狀態: %d", resp.StatusCode)
	return nil
}
```

### 8. Go mTLS 客戶端範例（crypto/tls）

```go
package main

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"net/http"
	"os"
)

func buildMTLSClient() (*http.Client, error) {
	// 載入客戶端憑證
	cert, err := tls.LoadX509KeyPair("client.crt", "client.key")
	if err != nil {
		return nil, fmt.Errorf("載入客戶端憑證失敗: %w", err)
	}

	// 載入 CA 憑證
	caCert, err := os.ReadFile("ca.crt")
	if err != nil {
		return nil, fmt.Errorf("讀取 CA 憑證失敗: %w", err)
	}
	caCertPool := x509.NewCertPool()
	if !caCertPool.AppendCertsFromPEM(caCert) {
		return nil, fmt.Errorf("無法解析 CA 憑證")
	}

	tlsConfig := &tls.Config{
		Certificates: []tls.Certificate{cert},
		RootCAs:      caCertPool,
		MinVersion:   tls.VersionTLS12,
	}

	return &http.Client{
		Transport: &http.Transport{TLSClientConfig: tlsConfig},
	}, nil
}
```

---

## Prevention Checklist / 預防清單

- [ ] **自動化憑證輪替**：使用 cert-manager (Kubernetes) 或 Let's Encrypt + certbot 自動續約憑證，設定到期前 30 天告警。
- [ ] **強制 TLS 1.2+**：在所有服務中設定 `MinVersion: tls.VersionTLS12`（Go）或 rustls 預設即停用舊版 TLS。優先使用 TLS 1.3。
- [ ] **WebSocket 健康檢查**：實作 ping/pong 機制，定期偵測連線狀態，設定合理的 idle timeout（建議 >=60s）。
- [ ] **mTLS CA Bundle 統一管理**：使用集中式 secret store（如 Vault）管理 CA 憑證，確保所有服務使用一致的 CA bundle。
- [ ] **監控憑證到期日**：整合 Prometheus `x509_cert_expiry` 指標或使用 `ssl-cert-check` 腳本，並設定 Alertmanager 告警規則。
- [ ] **Load Balancer 設定審查**：確認 `Connection: Upgrade` 標頭轉發、WebSocket timeout 設定。撰寫 infrastructure-as-code 測試。
- [ ] **OCSP Stapling**：啟用 OCSP stapling 減少客戶端驗證延遲，同時確保即時撤銷檢查。
- [ ] **憑證透明度 (CT) 監控**：訂閱 Certificate Transparency Log 通知，偵測未授權的憑證簽發。

---

## Cross-references / 交叉引用

- [[30_http2_http3_grpc_transport]] — HTTP/2、HTTP/3 與 gRPC 傳輸層，TLS 為其基礎
- [[26_oauth2_jwt]] — OAuth2/JWT 認證機制，常與 TLS 搭配使用
- [[29_secrets_management]] — 密鑰與憑證的集中式管理
- [[28_owasp_api_security]] — API 安全最佳實踐，涵蓋傳輸層加密要求

---

## References / 參考資料

- [RFC 6455 — The WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- [RFC 8446 — TLS 1.3](https://datatracker.ietf.org/doc/html/rfc8446)
- [RFC 5246 — TLS 1.2](https://datatracker.ietf.org/doc/html/rfc5246)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [cert-manager Documentation](https://cert-manager.io/docs/)
- [rustls Crate Documentation](https://docs.rs/rustls/latest/rustls/)
- [tokio-tungstenite Crate Documentation](https://docs.rs/tokio-tungstenite/latest/tokio_tungstenite/)
- [gorilla/websocket Go Package](https://pkg.go.dev/github.com/gorilla/websocket)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
