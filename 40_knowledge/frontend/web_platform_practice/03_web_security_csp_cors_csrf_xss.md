---
title: Web Security CSP CORS CSRF XSS
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, web-security]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: web_platform_practice
chapter: "03"
level: intermediate
stack: Browser security + HTTP headers
prerequisites: [http_cookie_token_basics]
---
# Web Security CSP CORS CSRF XSS

## Goal

建立前端最小安全基線，讓功能開發同時滿足可部署安全要求。

銜接上一章：worker/storage/offline。下一章預告：Core Web Vitals 與 profiling 實戰。

## Prerequisites

- 了解 cookie、origin、same-site。
- 了解 basic auth/session token。
- 可修改 dev server headers。

## Core Concepts

1. CSP 限制可執行來源。
- 何時用：任何上線網站。
- 何時不用：僅本地 demo 且未公開。

2. CORS 是資源分享規則，不是授權機制。
- 何時用：跨網域 API。
- 何時不用：同源部署且無跨域需求。

3. CSRF/XSS 防護需同時做。
- 何時用：有登入態與表單寫入行為。
- 何時不用：完全靜態內容。

## Step-by-step

1. 設定 CSP（script-src/style-src/connect-src）。
2. 設定 CORS allowlist（不要 `*` + credentials）。
3. 實作 CSRF token 或 same-site + double-submit 機制。
4. 統一輸入輸出消毒，禁止 `innerHTML` 直寫。
5. 導入安全測試：XSS payload、CSRF replay、CORS preflight。
6. 把安全檢查納入 CI。

## Hands-on Lab

### Foundation
- 實作基本 CSP 並記錄被阻擋來源。

### Advanced
- 加入 CSRF token 流程與失敗測試。

### Challenge
- 完成一份 threat model（資產、攻擊面、控制點）。

## Reference Solution

```http
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self';
```

## Evidence

- Command: `npm run test:security`
- Artifact: blocked CSP report, CSRF failure case log
- Route: `/security-lab`

## Common Pitfalls

- 把 CORS 當作權限控管。
- 用 `dangerouslySetInnerHTML` 渲染未信任資料。
- 忘記驗證 state-changing endpoint 的 CSRF。
- CSP policy 過寬導致實際無防護。

## Checklist

- [ ] CSP 已部署且有 report/violation 記錄。
- [ ] CORS allowlist 無萬用符號。
- [ ] CSRF 保護涵蓋所有寫入 API。
- [ ] 有 XSS 測試案例。
- [ ] 安全檢查納入 CI gate。

## Further Reading

- https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
- https://owasp.org/www-project-top-ten/
