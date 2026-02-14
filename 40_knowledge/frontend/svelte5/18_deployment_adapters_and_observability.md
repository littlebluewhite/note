---
title: "Deployment, Adapters, and Observability / 部署與可觀測性"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "18"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [17_testing_with_vitest_and_svelte_testing_library]
---
# Deployment, Adapters, and Observability / 部署與可觀測性

## Goal

學會選擇正確的 adapter 部署 SvelteKit 應用，建立 CI 品質門檻與基本可觀測性。

從開發到生產的最後一哩路決定了使用者的實際體驗。理解不同 adapter 的適用場景、環境變數的正確使用方式、以及 structured logging 與 error tracking 的建置，能讓你的應用在生產環境中穩定運行且易於問題排查。

- 銜接上一章：Ch17 完成了測試覆蓋，現在要將應用部署到生產環境。
- 下一章預告：Ch19 將學習升級治理、安全與長期維護策略。

## Prerequisites

- 已完成 Ch17（Testing with Vitest and Svelte Testing Library），應用已具備單元與元件測試覆蓋。
- 熟悉 `npm run build` 與 `npm run preview` 的基本用途。
- 對 CI/CD 概念有基礎認識（GitHub Actions 或其他 CI 工具）。
- `svelte5-lab` 專案可正常執行 `npm run dev` 與 `npm run test`。

## Core Concepts

### 1. SvelteKit Adapters — 部署目標適配器

SvelteKit 使用 adapter 將你的應用轉換為特定部署目標的輸出格式。選擇正確的 adapter 是部署的第一步。

- **`adapter-auto`**：自動偵測部署平台（Vercel、Cloudflare、Netlify），在偵測到的平台上使用對應的最佳化 adapter。開發時的預設 adapter，不需要手動設定。
- **`adapter-node`**：部署到任何 Node.js 環境（Docker 容器、VM、VPS、自建伺服器）。產出一個可用 `node build` 執行的 Node.js server。最通用的 adapter，適合需要完全掌控基礎設施的團隊。
- **`adapter-static`**：將整個應用預先渲染為純靜態 HTML/CSS/JS 檔案。適合所有頁面都可以 prerender 的站點（blog、文件站、landing page）。不需要 Node.js server 執行，可直接放上 CDN。
- **`adapter-vercel`**：Vercel 平台專屬優化，支援 edge functions、ISR（Incremental Static Regeneration）、serverless functions 自動拆分。
- **`adapter-cloudflare`**：部署到 Cloudflare Pages/Workers，利用 Cloudflare 的 edge network。支援 KV、D1、R2 等 Cloudflare 服務的直接存取。

**Adapter 決策樹：**

| 場景 | 推薦 Adapter | 理由 |
|------|-------------|------|
| 部署到 Vercel/Netlify/Cloudflare | `adapter-auto` | 自動偵測並使用對應 adapter |
| 自建 Docker / VPS | `adapter-node` | 產出標準 Node.js server |
| 純靜態站點（blog、文件） | `adapter-static` | 不需 server，直接放 CDN |
| 需要 Vercel edge/ISR | `adapter-vercel` | 啟用 Vercel 專屬功能 |
| 需要 Cloudflare Workers/KV | `adapter-cloudflare` | 存取 Cloudflare 原生服務 |

- **何時用 `adapter-auto`**：專案剛開始或部署到主流雲平台，不想手動設定 adapter 時。
- **何時用 `adapter-node`**：需要自行管理基礎設施、在 Docker 容器中執行、或需要 WebSocket 等 Node.js 特定功能。
- **何時用 `adapter-static`**：所有頁面都能在 build 時確定內容，沒有 server-side routes（`+page.server.ts`、form actions）。
- **何時不用 `adapter-static`**：應用有任何需要 server-side 執行的邏輯（API routes、form actions、cookies 操作）。

### 2. `svelte.config.js` configuration — 專案設定

`svelte.config.js` 是 SvelteKit 專案的核心設定檔，控制 adapter、預處理器、路徑別名等。

```js
// svelte.config.js — 完整結構示範
import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // 預處理器：處理 TypeScript、SCSS 等非原生語法
  preprocess: vitePreprocess(),

  kit: {
    // 部署 adapter
    adapter: adapter({ out: 'build' }),

    // 路徑別名（搭配 tsconfig.json 的 paths）
    alias: {
      $components: 'src/lib/components',
      $utils: 'src/lib/utils'
    },

    // CSRF 保護設定
    csrf: {
      checkOrigin: true  // 預設 true，驗證 POST request 的 Origin header
    }
  }
};

export default config;
```

- **何時需要自訂 config**：更換 adapter、新增 alias、調整 CSRF 設定、設定 preprocess 時。
- **何時用預設值**：初始開發階段、使用 `adapter-auto` 且不需 alias 或特殊 preprocess 時，大部分預設值已足夠。

### 3. `svelte-check` and CI quality gates — 型別檢查與 CI 品質門檻

`svelte-check` 是 SvelteKit 官方提供的 CLI 工具，對 `.svelte` 檔案進行 TypeScript 型別檢查與 Svelte 語法驗證。

```bash
# 基本用法
npx svelte-check --tsconfig ./tsconfig.json

# 持續監聽模式（開發時使用）
npx svelte-check --watch

# 指定輸出格式（CI 中使用 machine-readable）
npx svelte-check --tsconfig ./tsconfig.json --output machine
```

**CI pipeline 建議順序：**

```
lint → svelte-check → test → build
```

- **`lint`**（ESLint）：程式碼風格與最佳實踐。
- **`svelte-check`**：TypeScript + Svelte 語法與型別檢查。比單獨跑 `tsc` 更完整，因為它理解 `.svelte` 檔案中的 `<script lang="ts">`。
- **`test`**（Vitest）：單元測試與元件測試。
- **`build`**：完整的 production build，確認所有 import 解析正確、SSR 無錯誤。

- **何時用 `svelte-check`**：任何含 `.svelte` 檔案的專案都應使用，它是 Svelte 專案中唯一能完整檢查 `.svelte` 檔案型別的工具。
- **何時用 `tsc`**：只需要檢查純 `.ts` 檔案（如 shared library、純後端邏輯）時。對 Svelte 專案來說，`svelte-check` 已包含 `tsc` 的功能並擴展了 `.svelte` 支援。
- **何時不用**：幾乎不存在不需要的場景。即使是小型專案，`svelte-check` 也能在 CI 中捕捉到 Vite 忽略的型別錯誤（Vite 的 dev server 不阻擋型別錯誤）。

### 4. Basic observability — 基本可觀測性

在生產環境中，structured logging、error tracking 與 performance monitoring 是維運的三根支柱。

**Structured logging in hooks：**

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  const start = performance.now();
  const response = await resolve(event);
  const duration = Math.round(performance.now() - start);

  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    method: event.request.method,
    path: event.url.pathname,
    status: response.status,
    duration_ms: duration
  }));

  return response;
};
```

**Error tracking with `handleError`：**

```ts
// src/hooks.server.ts
import type { HandleServerError } from '@sveltejs/kit';

export const handleError: HandleServerError = async ({ error, event, status, message }) => {
  const errorId = crypto.randomUUID();
  console.error(JSON.stringify({
    errorId,
    status,
    message,
    path: event.url.pathname,
    error: error instanceof Error ? error.stack : String(error)
  }));

  return { message: 'Internal Error', errorId };
};
```

**Performance monitoring — Core Web Vitals：**

Core Web Vitals（LCP、INP、CLS）可在 client 端透過 `web-vitals` library 收集，送回 analytics endpoint。

- **何時用正式 observability 工具（Sentry、Datadog）**：生產環境有大量使用者、需要 alerting、需要 error 分群與追蹤、需要 distributed tracing。
- **何時 `console.log` 配合 structured JSON 足夠**：早期階段、小型專案、流量低、或已有 log aggregation 服務（如 CloudWatch Logs、Vercel Logs）可收集 stdout。

## Step-by-step

### Step 1：安裝並設定 `adapter-node`

安裝 `adapter-node` 並在 `svelte.config.js` 中設定。

```bash
npm install -D @sveltejs/adapter-node
```

```js
// svelte.config.js
import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      out: 'build',        // 輸出目錄
      precompress: true,   // 產出 .gz 和 .br 預壓縮檔
      envPrefix: 'APP_'    // 環境變數前綴（預設無前綴）
    })
  }
};

export default config;
```

`out` 指定 build 輸出目錄。`precompress` 會自動產出 Brotli 和 Gzip 壓縮版本，省去 reverse proxy 即時壓縮的成本。`envPrefix` 限制可被讀取的環境變數前綴，增加安全性。

### Step 2：執行 `npm run build` 並檢查輸出

```bash
npm run build
```

Build 完成後，檢查 `build/` 目錄的結構：

```
build/
├── client/           # Client-side assets（JS、CSS、images）
│   ├── _app/
│   │   ├── immutable/  # 帶 hash 的不可變檔案（長快取）
│   │   └── version.json
│   └── favicon.png
├── server/           # Server-side code
│   ├── chunks/
│   ├── index.js      # Server entry point
│   └── manifest.json
├── handler.js        # Request handler
├── index.js          # Main entry point — 用 node 執行此檔案
└── env.js            # Environment variable handling
```

`build/index.js` 是主要進入點。`client/` 中的 `immutable/` 資料夾內的檔案名稱含 content hash，可設定長期快取（1 年）。

### Step 3：以 production 模式執行 built app

```bash
# 設定 port 與 host
PORT=3000 HOST=0.0.0.0 node build
```

Server 預設監聽 `PORT` 環境變數（fallback 為 3000）和 `HOST` 環境變數。訪問 `http://localhost:3000` 確認應用運作正常。

若設定了 `envPrefix: 'APP_'`，可以透過 `APP_PORT` 和 `APP_HOST` 來控制（adapter-node 自有的 `PORT`/`HOST` 不受 prefix 影響）。

### Step 4：設定環境變數

SvelteKit 提供四個環境變數模組，依據 scope（public/private）和 timing（static/dynamic）區分：

```ts
// 靜態私有 — build 時嵌入，不可在 client 使用
import { DATABASE_URL, API_SECRET } from '$env/static/private';

// 動態私有 — 執行時讀取，每次 request 可能不同
import { env } from '$env/dynamic/private';
const dbUrl = env.DATABASE_URL;

// 靜態公開 — build 時嵌入，可在 client 使用（需 PUBLIC_ 前綴）
import { PUBLIC_API_URL } from '$env/static/public';

// 動態公開 — 執行時讀取，可在 client 使用
import { env } from '$env/dynamic/public';
const apiUrl = env.PUBLIC_API_URL;
```

| 模組 | 時機 | 可用範圍 | 適用場景 |
|------|------|----------|----------|
| `$env/static/private` | Build-time | Server only | 不常變動的 secrets（DB URL、API key） |
| `$env/dynamic/private` | Runtime | Server only | 需要每次部署可變的值（feature flags） |
| `$env/static/public` | Build-time | Server + Client | 不常變動的公開值（API base URL） |
| `$env/dynamic/public` | Runtime | Server + Client | 執行時可變的公開值 |

Private 模組只能在 server-side code（`+page.server.ts`、`+server.ts`、`hooks.server.ts`）中使用。在 client-side code 中 import private 模組會造成 build error。

### Step 5：設定 CI pipeline

建立 GitHub Actions workflow，依序執行 lint、svelte-check、test、build。

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npx svelte-check --tsconfig ./tsconfig.json
      - run: npm run test -- --run
      - run: npm run build
```

每一步驟都是品質門檻：前一步失敗則後續不執行。`npm run test -- --run` 中的 `--run` 讓 Vitest 執行一次後退出（不進入 watch 模式）。

### Step 6：切換至 `adapter-static` 進行全站預渲染

若應用的所有頁面都可以 prerender（沒有 server-side routes），可以切換到 `adapter-static`。

```bash
npm install -D @sveltejs/adapter-static
```

```js
// svelte.config.js
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      pages: 'build',       // HTML 輸出目錄
      assets: 'build',      // 靜態資源輸出目錄
      fallback: '404.html', // SPA fallback 頁面
      precompress: true     // 產出壓縮檔
    })
  }
};

export default config;
```

同時，需要在根 layout 中啟用全站 prerender：

```ts
// src/routes/+layout.ts
export const prerender = true;
```

Build 後的 `build/` 目錄可直接部署到任何靜態主機（Nginx、S3、GitHub Pages、Cloudflare Pages）。

### Step 7：在 `hooks.server.ts` 中加入 structured logging

為每個 request 記錄 method、path、status、duration，輸出為 JSON 格式方便 log aggregation 工具解析。

```ts
// src/hooks.server.ts
import type { Handle, HandleServerError } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  const requestId = crypto.randomUUID();
  const start = performance.now();

  // 將 requestId 注入 locals，供後續 handler 使用
  event.locals.requestId = requestId;

  const response = await resolve(event);
  const duration = Math.round(performance.now() - start);

  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    requestId,
    method: event.request.method,
    path: event.url.pathname,
    status: response.status,
    duration_ms: duration,
    userAgent: event.request.headers.get('user-agent') ?? 'unknown'
  }));

  return response;
};

export const handleError: HandleServerError = async ({ error, event, status, message }) => {
  const errorId = crypto.randomUUID();

  console.error(JSON.stringify({
    timestamp: new Date().toISOString(),
    errorId,
    requestId: event.locals.requestId,
    status,
    message,
    path: event.url.pathname,
    stack: error instanceof Error ? error.stack : String(error)
  }));

  return {
    message: 'An unexpected error occurred.',
    errorId
  };
};
```

回傳的 `errorId` 會傳到 `+error.svelte` 的 `$page.error` 中，使用者可以回報 `errorId` 供維運人員追查。

### Step 8：部署到平台（Vercel / Cloudflare / Docker）

**Vercel 部署（最簡單）：**

```bash
# 安裝 Vercel CLI
npm i -g vercel

# 部署（adapter-auto 會自動使用 adapter-vercel）
vercel
```

**Cloudflare Pages 部署：**

```bash
npm install -D @sveltejs/adapter-cloudflare
```

在 `svelte.config.js` 中切換 adapter 後，透過 Cloudflare Dashboard 或 `wrangler` CLI 部署。

**Docker 部署（adapter-node）：**

```dockerfile
# Dockerfile
FROM node:22-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
RUN npm prune --production

FROM node:22-slim
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000
CMD ["node", "build"]
```

```bash
# 建置並執行 Docker 容器
docker build -t my-sveltekit-app .
docker run -p 3000:3000 my-sveltekit-app
```

Multi-stage build 確保最終 image 只包含 production dependencies 和 build 產出物，大幅縮小 image 大小。

## Hands-on Lab

任務：將 SvelteKit 應用部署到生產環境，建立 CI 品質門檻與基本可觀測性。

### Foundation 基礎層

設定 `adapter-node`，build 應用並以 production 模式執行：

- 安裝 `@sveltejs/adapter-node`，在 `svelte.config.js` 中設定 `out: 'build'` 和 `precompress: true`。
- 執行 `npm run build`，確認 `build/` 目錄產出了 `index.js`、`client/`、`server/` 等檔案。
- 用 `PORT=3000 node build` 啟動 server，在瀏覽器中訪問 `http://localhost:3000` 確認運作正常。
- 在 `hooks.server.ts` 中加入基本的 structured logging，記錄每個 request 的 method、path、status、duration。
- 確認 terminal 中印出 JSON 格式的 log。

### Advanced 進階層

建立 GitHub Actions CI pipeline，含 lint/check/test/build 四道品質門檻：

- 建立 `.github/workflows/ci.yml`，使用 `ubuntu-latest` 和 Node.js 22。
- Pipeline 依序執行：`npm run lint` → `npx svelte-check --tsconfig ./tsconfig.json` → `npm run test -- --run` → `npm run build`。
- 在程式碼中故意引入一個型別錯誤（如將 `string` 賦值給 `number` 變數），確認 `svelte-check` 步驟失敗，後續步驟不執行。
- 修正錯誤後，確認整條 pipeline 通過。
- 額外：加入 `handleError` hook，確保 unhandled error 被記錄並回傳 `errorId`。

### Challenge 挑戰層

建立 Dockerfile 並部署到容器平台：

- 撰寫 multi-stage Dockerfile：builder stage 安裝依賴並 build，production stage 只複製必要檔案。
- 使用 `docker build -t sveltekit-app .` 建置 image。
- 使用 `docker run -p 3000:3000 -e APP_DATABASE_URL=postgres://... sveltekit-app` 啟動容器，驗證環境變數透過 `$env/dynamic/private` 正確讀取。
- 加入 `.dockerignore` 排除 `node_modules`、`.svelte-kit`、`.env` 等不必要的檔案。
- 部署到容器平台（如 Fly.io、Railway、Google Cloud Run），確認生產環境正常運作。

## Reference Solution

完整的 `adapter-node` 設定，含 precompress 與 envPrefix。

```js
// svelte.config.js (adapter-node)
import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      out: 'build',
      precompress: true,
      envPrefix: 'APP_'
    })
  }
};

export default config;
```

GitHub Actions CI workflow，含四道品質門檻。

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npx svelte-check --tsconfig ./tsconfig.json
      - run: npm run test -- --run
      - run: npm run build
```

Multi-stage Dockerfile，用於 `adapter-node` build 產出物。

```dockerfile
# Dockerfile
FROM node:22-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
RUN npm prune --production

FROM node:22-slim
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000
CMD ["node", "build"]
```

完整的 `adapter-static` 設定，適合全站預渲染。

```js
// svelte.config.js (adapter-static)
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: '404.html',
      precompress: true
    })
  }
};

export default config;
```

Structured logging 與 error tracking 的 hooks 設定。

```ts
// src/hooks.server.ts
import type { Handle, HandleServerError } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  const requestId = crypto.randomUUID();
  const start = performance.now();
  event.locals.requestId = requestId;

  const response = await resolve(event);
  const duration = Math.round(performance.now() - start);

  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    requestId,
    method: event.request.method,
    path: event.url.pathname,
    status: response.status,
    duration_ms: duration
  }));

  return response;
};

export const handleError: HandleServerError = async ({ error, event, status, message }) => {
  const errorId = crypto.randomUUID();
  console.error(JSON.stringify({
    errorId,
    requestId: event.locals.requestId,
    status,
    message,
    path: event.url.pathname,
    stack: error instanceof Error ? error.stack : String(error)
  }));
  return { message: 'An unexpected error occurred.', errorId };
};
```

## Common Pitfalls

- **使用 `adapter-static` 但應用有 server-side routes**：`adapter-static` 只能 prerender 頁面，無法執行 server-side code。如果應用中有 `+page.server.ts`（含 form actions）、`+server.ts`（API routes）、或任何使用 `cookies`、`request` 的 load function，`adapter-static` build 會失敗或產出不完整的結果。解法：改用 `adapter-node` 或 `adapter-auto`，或將 server 邏輯移到外部 API。
- **使用 `adapter-static` 但忘了設定全站 `prerender = true`**：`adapter-static` 要求所有頁面都必須 prerender。若根 layout 沒有 `export const prerender = true`，且有頁面未個別設定 prerender，build 時會出現 `Error: The following routes were marked as prerenderable, but were not prerendered` 錯誤。解法：在 `src/routes/+layout.ts` 中加上 `export const prerender = true`。
- **在原始碼中硬寫 secrets**：直接在程式碼中寫入 API key、database URL 等敏感資訊，會導致 secrets 隨原始碼進入 Git repository。解法：使用 `$env/static/private` 或 `$env/dynamic/private` 讀取環境變數，並將 `.env` 加入 `.gitignore`。
- **CI 中未執行 `svelte-check`**：Vite 的 dev server 和 build 過程不會阻擋 TypeScript 型別錯誤，因此型別錯誤可能在不知情的狀況下被部署到生產環境。`svelte-check` 是唯一能完整檢查 `.svelte` 檔案型別的工具。解法：在 CI pipeline 中加入 `npx svelte-check --tsconfig ./tsconfig.json`，放在 `npm run build` 之前。
- **對每次部署都會變動的值使用 `$env/static/private`**：`$env/static/private` 在 build 時嵌入值，一旦 build 完成就不會再變。如果同一個 build artifact 要部署到不同環境（staging、production），需要用 `$env/dynamic/private` 在 runtime 讀取環境變數。錯誤範例：用 `$env/static/private` 讀取 `DATABASE_URL`，導致 staging build 帶著 staging 的 DB URL 被誤部署到 production。

## Checklist

- [ ] 能解釋 `adapter-auto`、`adapter-node`、`adapter-static`、`adapter-vercel`、`adapter-cloudflare` 各自的用途與適用場景。
- [ ] 能使用 `adapter-node` build 應用並用 `node build` 在 production 模式執行。
- [ ] CI pipeline 包含 lint、svelte-check、test、build 四道品質門檻。
- [ ] 環境變數正確使用 `$env/static/private`、`$env/dynamic/private`、`$env/static/public`、`$env/dynamic/public` 模組。
- [ ] `npm run build` 成功完成且無錯誤。
- [ ] `npx svelte-check` 通過，無型別錯誤。
- [ ] `hooks.server.ts` 中有 structured logging 記錄 request 資訊。
- [ ] 能撰寫 multi-stage Dockerfile 部署 `adapter-node` build 產出物。

## Further Reading

- [SvelteKit Docs — Adapters](https://svelte.dev/docs/kit/adapters)
- [SvelteKit Docs — adapter-node](https://svelte.dev/docs/kit/adapter-node)
- [SvelteKit Docs — adapter-static](https://svelte.dev/docs/kit/adapter-static)
- [SvelteKit Docs — adapter-vercel](https://svelte.dev/docs/kit/adapter-vercel)
- [SvelteKit Docs — adapter-cloudflare](https://svelte.dev/docs/kit/adapter-cloudflare)
- [SvelteKit Docs — Building your app](https://svelte.dev/docs/kit/building-your-app)
- [SvelteKit Docs — Configuration](https://svelte.dev/docs/kit/configuration)
- [SvelteKit Docs — Hooks](https://svelte.dev/docs/kit/hooks)
- [SvelteKit Docs — $env](https://svelte.dev/docs/kit/$env-static-private)
- [GitHub — sveltejs/kit](https://github.com/sveltejs/kit)
