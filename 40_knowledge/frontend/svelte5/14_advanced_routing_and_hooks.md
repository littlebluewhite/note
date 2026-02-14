---
title: "Advanced Routing and Hooks / 進階路由與中間件"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "14"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [13_ssr_streaming_and_page_options]
---
# Advanced Routing and Hooks / 進階路由與中間件

## Goal

掌握 SvelteKit 的 hooks 系統、REST API endpoints、route matchers 與 shallow routing。

這些進階路由功能是構建生產級 SvelteKit 應用的關鍵基礎設施。透過 hooks 實現認證中間件、透過 REST endpoints 提供 API 服務、透過 route matchers 強化路由安全性，能讓你的應用架構更加健全且易於維護。

- **銜接上一章**：Ch13 學會了 SSR 與 streaming，現在要學習路由系統的進階功能。
- **下一章預告**：Ch15 將學習錯誤處理與復原策略。

## Prerequisites

- 已完成第 13 章（SSR, Streaming & Page Options）。
- 熟悉 SvelteKit 路由系統與 `+page.server.ts` / `+layout.server.ts`（Ch10、Ch11）。
- 理解 `load` 函式與 form actions 的運作方式（Ch11、Ch12）。
- 熟悉 TypeScript 型別定義（Ch01）。

## Core Concepts

### 1. `hooks.server.ts`: `handle`, `handleFetch`, `handleError`

SvelteKit 的 server hooks 讓你在 request 層級攔截與處理邏輯，是應用的中間件層。所有 hooks 定義在 `src/hooks.server.ts` 中：

**`handle`** -- 攔截每個 request，可修改 request 或 response。典型用途包含 auth 驗證、locale 偵測、logging：

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  // 在 resolve 之前：修改 request（如設定 locals）
  const lang = event.cookies.get('lang') ?? 'zh-TW';
  event.locals.lang = lang;

  // 呼叫 resolve 取得 response
  const response = await resolve(event, {
    // 可選：轉換 HTML（例如設定 <html lang="...">）
    transformPageChunk: ({ html }) => html.replace('%lang%', lang)
  });

  // 在 resolve 之後：修改 response（如加 header）
  response.headers.set('X-Custom-Header', 'hello');
  return response;
};
```

**`handleFetch`** -- 攔截 server-side 的 `fetch` 呼叫。當 `load` 函式中使用 `fetch` 時，可以在這裡修改 headers 或重寫 URL：

```ts
import type { HandleFetch } from '@sveltejs/kit';

export const handleFetch: HandleFetch = async ({ event, request, fetch }) => {
  // 將 internal API 呼叫重寫為直接呼叫（避免多一次 HTTP roundtrip）
  if (request.url.startsWith('https://api.example.com/')) {
    request = new Request(
      request.url.replace('https://api.example.com/', 'http://localhost:3000/'),
      request
    );
  }

  // 自動附加認證 header
  if (request.url.startsWith('http://localhost:3000/')) {
    const cookie = event.request.headers.get('cookie');
    if (cookie) {
      request.headers.set('cookie', cookie);
    }
  }

  return fetch(request);
};
```

**`handleError`** -- 處理未預期的錯誤（非 `error()` 拋出的）。適合做 logging 和 error reporting：

```ts
import type { HandleServerError } from '@sveltejs/kit';

export const handleError: HandleServerError = async ({ error, event, status, message }) => {
  const errorId = crypto.randomUUID();
  console.error(`[${errorId}] ${event.url.pathname}:`, error);

  // 回傳的物件會成為 $page.error
  return {
    message: 'An unexpected error occurred.',
    errorId
  };
};
```

| 何時用 hooks | 何時用 layout load |
|---|---|
| 需要攔截每個 request（auth、logging） | 只需要為特定路由群組載入資料 |
| 需要修改 response headers 或 HTML | 需要根據路由載入不同的資料 |
| 中間件邏輯（guard、rate limiting） | 資料 fetching 與頁面渲染相關 |
| 在 `load` 之前就需要執行的邏輯 | 資料需要被子路由繼承 |

### 2. `hooks.client.ts`: `handleError`

Client-side hooks 定義在 `src/hooks.client.ts`，目前只支援 `handleError`，用於處理瀏覽器端的未預期錯誤：

```ts
// src/hooks.client.ts
import type { HandleClientError } from '@sveltejs/kit';

export const handleError: HandleClientError = async ({ error, event, status, message }) => {
  const errorId = crypto.randomUUID();

  // 傳送到 error tracking 服務（如 Sentry）
  // await Sentry.captureException(error, { extra: { errorId, url: event.url.href } });
  console.error(`[Client ${errorId}]`, error);

  return {
    message: 'Something went wrong on the client.',
    errorId
  };
};
```

| 何時用 `hooks.client.ts` | 何時不用 |
|---|---|
| 統一的 client-side error reporting | 個別元件的錯誤處理（用 `{#snippet}` 或 try-catch） |
| 將錯誤傳送到 Sentry / LogRocket 等服務 | 已預期的錯誤（用 `error()` 明確拋出） |
| 需要為所有 client 錯誤產生追蹤 ID | 只需要顯示錯誤訊息給使用者 |

### 3. `event.locals` 與 `sequence()`

**`event.locals`** 是在 request 生命週期中傳遞資料的機制。在 hooks 中設定，後續的 `load` 函式和 form actions 都可以讀取：

```ts
// src/app.d.ts -- 定義 locals 型別
declare global {
  namespace App {
    interface Locals {
      user: { id: string; name: string; role: string } | null;
      lang: string;
      requestId: string;
    }
  }
}
export {};
```

典型用途：auth middleware 設定 `locals.user`，讓所有 load 函式都能取得當前使用者：

```ts
// 在 hooks.server.ts 中設定
const auth: Handle = async ({ event, resolve }) => {
  const sessionId = event.cookies.get('session');
  if (sessionId) {
    const user = await db.getUserBySession(sessionId);
    event.locals.user = user;
  } else {
    event.locals.user = null;
  }
  return resolve(event);
};

// 在 +page.server.ts 中讀取
export const load: PageServerLoad = async ({ locals }) => {
  return { user: locals.user };
};
```

**`sequence()`** 讓你按順序組合多個 `handle` 函式，每個函式負責單一職責：

```ts
import { sequence } from '@sveltejs/kit/hooks';

const auth: Handle = async ({ event, resolve }) => { /* ... */ };
const logger: Handle = async ({ event, resolve }) => { /* ... */ };
const i18n: Handle = async ({ event, resolve }) => { /* ... */ };

// 依序執行：auth → i18n → logger
export const handle = sequence(auth, i18n, logger);
```

執行順序很重要：`auth` 先設定 `locals.user`，後續的 `i18n` 和 `logger` 才能讀取到使用者資訊。

#### 完整 JWT Auth Middleware 範例

在生產環境中，常見的做法是在 `handle` hook 中驗證 JWT token，並將解碼後的使用者資訊設定到 `event.locals`：

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { redirect } from '@sveltejs/kit';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET ?? 'your-secret-key';

interface JwtPayload {
  sub: string;
  name: string;
  role: string;
  exp: number;
}

const auth: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get('access_token');

  if (token) {
    try {
      const payload = jwt.verify(token, JWT_SECRET) as JwtPayload;
      event.locals.user = {
        id: payload.sub,
        name: payload.name,
        role: payload.role
      };
    } catch (err) {
      // Token 過期或無效：清除 cookie，視為未登入
      event.cookies.delete('access_token', { path: '/' });
      event.locals.user = null;
    }
  } else {
    event.locals.user = null;
  }

  return resolve(event);
};

export const handle = sequence(auth, /* ...other hooks */);
```

```ts
// src/app.d.ts
declare global {
  namespace App {
    interface Locals {
      user: { id: string; name: string; role: string } | null;
    }
  }
}
export {};
```

#### Protected Route Pattern — 路由保護模式

使用 SvelteKit 的 route group 搭配 layout load 函式，建立統一的路由保護機制：

```
src/routes/
  (public)/
    login/+page.svelte
    register/+page.svelte
  (authenticated)/
    +layout.server.ts       ← 檢查 locals.user，未登入 redirect
    dashboard/+page.svelte
    settings/+page.svelte
    profile/+page.svelte
```

```ts
// src/routes/(authenticated)/+layout.server.ts
import type { LayoutServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: LayoutServerLoad = async ({ locals, url }) => {
  if (!locals.user) {
    // 保留原始 URL，登入後可 redirect 回來
    const redirectTo = encodeURIComponent(url.pathname + url.search);
    redirect(303, `/login?redirect=${redirectTo}`);
  }

  return {
    user: locals.user
  };
};
```

```svelte
<!-- src/routes/(public)/login/+page.svelte -->
<script lang="ts">
  import { page } from '$app/state';

  let { form } = $props();

  // 登入成功後 redirect 到原始頁面
  const redirectTo = $derived(
    page.url.searchParams.get('redirect') ?? '/dashboard'
  );
</script>

<h1>Login</h1>
<form method="POST" action="/api/auth/login">
  <input type="hidden" name="redirect" value={redirectTo} />
  <input type="email" name="email" placeholder="Email" required />
  <input type="password" name="password" placeholder="Password" required />
  <button type="submit">Login</button>
  {#if form?.error}
    <p class="error">{form.error}</p>
  {/if}
</form>
```

#### Token Refresh Flow — Token 續期流程

當 access token 即將過期時，利用 refresh token 自動續期，避免使用者被強制登出：

```ts
// src/hooks.server.ts（擴充 auth handle）
const auth: Handle = async ({ event, resolve }) => {
  const accessToken = event.cookies.get('access_token');
  const refreshToken = event.cookies.get('refresh_token');

  if (accessToken) {
    try {
      const payload = jwt.verify(accessToken, JWT_SECRET) as JwtPayload;
      event.locals.user = {
        id: payload.sub,
        name: payload.name,
        role: payload.role
      };
    } catch (err) {
      // Access token 過期，嘗試用 refresh token 續期
      if (refreshToken) {
        try {
          const newTokens = await refreshAccessToken(refreshToken);

          // 設定新的 cookies
          event.cookies.set('access_token', newTokens.accessToken, {
            path: '/',
            httpOnly: true,
            secure: true,
            sameSite: 'lax',
            maxAge: 60 * 15 // 15 分鐘
          });

          event.cookies.set('refresh_token', newTokens.refreshToken, {
            path: '/',
            httpOnly: true,
            secure: true,
            sameSite: 'lax',
            maxAge: 60 * 60 * 24 * 7 // 7 天
          });

          const payload = jwt.verify(newTokens.accessToken, JWT_SECRET) as JwtPayload;
          event.locals.user = {
            id: payload.sub,
            name: payload.name,
            role: payload.role
          };
        } catch {
          // Refresh token 也無效：清除所有 token
          event.cookies.delete('access_token', { path: '/' });
          event.cookies.delete('refresh_token', { path: '/' });
          event.locals.user = null;
        }
      } else {
        event.cookies.delete('access_token', { path: '/' });
        event.locals.user = null;
      }
    }
  } else {
    event.locals.user = null;
  }

  return resolve(event);
};

async function refreshAccessToken(refreshToken: string) {
  // 呼叫 auth server 或自行驗證 refresh token
  const response = await fetch('http://localhost:3000/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refreshToken })
  });

  if (!response.ok) throw new Error('Refresh failed');
  return response.json() as Promise<{ accessToken: string; refreshToken: string }>;
}
```

#### JWT vs Session 比較表

| 比較項目 | JWT（Token-based） | Session（Server-side） |
|---|---|---|
| 狀態儲存 | Client-side（cookie / header） | Server-side（DB / Redis） |
| 擴展性 | 無狀態，易水平擴展 | 需要共享 session store |
| 撤銷 | 困難（需要 blocklist） | 容易（刪除 session 紀錄） |
| 資料攜帶 | Token 內包含使用者資訊 | 只有 session ID |
| 效能 | 不需查 DB 驗證（除非用 blocklist） | 每次 request 需查 session store |
| 安全性 | Token 洩漏無法即時撤銷 | 可即時撤銷，更安全 |
| 適用場景 | API-first、微服務、第三方整合 | 傳統 Web 應用、需要即時撤銷權限 |
| SvelteKit 實作 | `handle` hook 驗證 token | `handle` hook 查詢 session store |

- **何時用 JWT**：API-first 架構、需要跨服務認證、前後端分離部署、行動端 + Web 共用 API。
- **何時用 Session**：傳統 Web 應用、需要即時撤銷使用者權限、不需要跨服務認證、安全性要求高於擴展性。

### 4. `+server.ts` REST endpoints 與 route matchers

**`+server.ts`** 讓你在 SvelteKit 路由中定義 REST API endpoints，export 對應的 HTTP method handler：

```ts
// src/routes/api/items/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url, locals }) => {
  const limit = Number(url.searchParams.get('limit')) || 20;
  const items = await db.getItems({ limit, userId: locals.user?.id });
  return json(items);
};

export const POST: RequestHandler = async ({ request, locals }) => {
  if (!locals.user) return new Response('Unauthorized', { status: 401 });
  const data = await request.json();
  const item = await db.createItem(data);
  return json(item, { status: 201 });
};
```

**Route matchers** 讓你限制動態路由參數的格式。定義在 `src/params/` 資料夾中：

```ts
// src/params/integer.ts
import type { ParamMatcher } from '@sveltejs/kit';

export const match: ParamMatcher = (param) => {
  return /^\d+$/.test(param);
};
```

在路由中使用：`src/routes/api/items/[id=integer]/+server.ts`。如果 URL 中的 `id` 不是整數，SvelteKit 會自動回傳 404，不會進入 handler。

| 何時用 `+server.ts` | 何時用 form actions |
|---|---|
| 提供 REST API 給外部系統或前端 fetch | 處理表單提交，搭配 progressive enhancement |
| 需要回傳 JSON 資料 | 需要 `use:enhance` 的自動表單處理 |
| 非同源的 client 需要呼叫 | 只在自己的 SvelteKit 頁面中使用 |
| WebSocket / SSE / streaming 回應 | 需要自動處理 redirect 與 validation |

### 5. Shallow routing (`pushState`, `replaceState`)

Shallow routing 讓你更新 URL 而不觸發 `load` 函式。適用於 modal overlay、tab switching 等場景，URL 需要反映當前狀態，但不需要重新載入資料：

```svelte
<script lang="ts">
  import { pushState, replaceState } from '$app/navigation';
  import { page } from '$app/state';

  let { data } = $props();

  function openPhoto(photo: { id: string; url: string; title: string }) {
    // 更新 URL 到 /photos/123，但不觸發該路由的 load
    pushState(`/photos/${photo.id}`, {
      selectedPhoto: photo
    });
  }

  function closePhoto() {
    history.back();
  }

  // 從 page.state 讀取 shallow routing 傳入的狀態
  const selectedPhoto = $derived(page.state.selectedPhoto);
</script>

{#if selectedPhoto}
  <div class="modal-overlay" onclick={closePhoto} role="presentation">
    <div class="modal" onclick={(e) => { e.stopPropagation(); }}>
      <img src={selectedPhoto.url} alt={selectedPhoto.title} />
      <h2>{selectedPhoto.title}</h2>
    </div>
  </div>
{/if}
```

`replaceState` 的用法與 `pushState` 相同，但會取代當前的 history entry 而不是新增：

```ts
// 適用於 tab switching -- 不希望每次切換 tab 都新增 history entry
replaceState(`/settings/${tab}`, { activeTab: tab });
```

| 何時用 shallow routing | 何時不用 |
|---|---|
| Modal / dialog overlay 需要獨立 URL | 頁面需要根據 URL 載入不同資料 |
| Tab switching 要反映在 URL | 使用者可能直接造訪該 URL（需要 load） |
| 保留 back button 行為 | SEO 需要每個 URL 有獨立內容 |
| URL 變化只影響 UI 狀態 | 需要 server-side 資料 |

## Step-by-step

### Step 1：建立 `src/hooks.server.ts` -- 基本 `handle` logging

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  const start = Date.now();
  const response = await resolve(event);
  const duration = Date.now() - start;

  console.log(
    `[${new Date().toISOString()}] ${event.request.method} ${event.url.pathname} → ${response.status} (${duration}ms)`
  );

  return response;
};
```

> **重點**：`handle` 必須呼叫 `resolve(event)` 並回傳其結果。如果忘記呼叫，request 會永遠不回應。

### Step 2：加入 auth middleware -- 檢查 cookie 並設定 `event.locals.user`

首先定義 `Locals` 型別：

```ts
// src/app.d.ts
declare global {
  namespace App {
    interface Locals {
      user: { id: string; name: string; role: string } | null;
    }
    interface PageState {
      selectedPhoto?: { id: string; url: string; title: string };
    }
  }
}
export {};
```

然後建立 auth handle：

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';

const auth: Handle = async ({ event, resolve }) => {
  const sessionId = event.cookies.get('session');

  if (sessionId) {
    // 實際應用中，這裡會查詢資料庫驗證 session
    event.locals.user = { id: '1', name: 'Alice', role: 'admin' };
  } else {
    event.locals.user = null;
  }

  return resolve(event);
};

export const handle = auth;
```

### Step 3：使用 `sequence()` 組合 auth + guard + logger hooks

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { redirect } from '@sveltejs/kit';

const auth: Handle = async ({ event, resolve }) => {
  const sessionId = event.cookies.get('session');
  if (sessionId) {
    event.locals.user = { id: '1', name: 'Alice', role: 'admin' };
  } else {
    event.locals.user = null;
  }
  return resolve(event);
};

const guard: Handle = async ({ event, resolve }) => {
  // 注意：排除 /login 路徑，避免無限 redirect loop
  if (event.url.pathname.startsWith('/dashboard') && !event.locals.user) {
    redirect(303, '/login');
  }
  return resolve(event);
};

const logger: Handle = async ({ event, resolve }) => {
  const start = Date.now();
  const response = await resolve(event);
  const duration = Date.now() - start;
  console.log(`${event.request.method} ${event.url.pathname} - ${response.status} (${duration}ms)`);
  return response;
};

// auth 先執行，設定 locals.user → guard 檢查權限 → logger 記錄結果
export const handle = sequence(auth, guard, logger);
```

### Step 4：建立 `+server.ts` REST endpoint（GET 和 POST）

```ts
// src/routes/api/todos/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Mock data
const todos = [
  { id: 1, text: 'Learn SvelteKit hooks', done: true },
  { id: 2, text: 'Build REST API', done: false },
  { id: 3, text: 'Deploy to production', done: false }
];

export const GET: RequestHandler = async ({ url }) => {
  const done = url.searchParams.get('done');
  const filtered = done !== null
    ? todos.filter(t => t.done === (done === 'true'))
    : todos;
  return json(filtered);
};

export const POST: RequestHandler = async ({ request, locals }) => {
  if (!locals.user) {
    return json({ error: 'Unauthorized' }, { status: 401 });
  }
  const { text } = await request.json();
  const newTodo = { id: todos.length + 1, text, done: false };
  todos.push(newTodo);
  return json(newTodo, { status: 201 });
};
```

### Step 5：建立 route matcher `src/params/slug.ts`

```ts
// src/params/integer.ts
import type { ParamMatcher } from '@sveltejs/kit';

export const match: ParamMatcher = (param) => {
  return /^\d+$/.test(param);
};
```

```ts
// src/params/slug.ts
import type { ParamMatcher } from '@sveltejs/kit';

export const match: ParamMatcher = (param) => {
  return /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(param);
};
```

使用方式：在路由資料夾名稱中加入 `=matcher`：

- `src/routes/api/todos/[id=integer]/+server.ts` -- 只匹配數字
- `src/routes/blog/[slug=slug]/+page.svelte` -- 只匹配 slug 格式

當參數不符合 matcher 時，SvelteKit 會自動回傳 404，不會執行 load 或 handler。

### Step 6：在 `+page.server.ts` 中使用 `event.locals.user`

```ts
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  // guard hook 已確保到這裡時 locals.user 一定存在
  const user = locals.user!;

  // 根據使用者角色載入不同資料
  const dashboardData = await getDashboardData(user.id);

  return {
    user: {
      name: user.name,
      role: user.role
    },
    stats: dashboardData.stats,
    recentActivity: dashboardData.recentActivity
  };
};

async function getDashboardData(userId: string) {
  // Mock: 實際應用中查詢資料庫
  return {
    stats: { totalTodos: 42, completed: 28 },
    recentActivity: [
      { action: 'Completed task', timestamp: new Date().toISOString() }
    ]
  };
}
```

### Step 7：實作 `handleError` 做結構化錯誤記錄

```ts
// src/hooks.server.ts（加入 handleError）
import type { HandleServerError } from '@sveltejs/kit';

export const handleError: HandleServerError = async ({ error, event, status, message }) => {
  const errorId = crypto.randomUUID();

  // 結構化 logging -- 方便在 log aggregation 工具中搜尋
  console.error(JSON.stringify({
    errorId,
    timestamp: new Date().toISOString(),
    method: event.request.method,
    path: event.url.pathname,
    status,
    message,
    stack: error instanceof Error ? error.stack : String(error),
    userId: event.locals.user?.id ?? 'anonymous'
  }));

  // 回傳給客戶端的錯誤資訊（不要洩漏內部細節）
  return {
    message: 'An unexpected error occurred.',
    errorId
  };
};
```

```ts
// src/hooks.client.ts
import type { HandleClientError } from '@sveltejs/kit';

export const handleError: HandleClientError = async ({ error, event, status, message }) => {
  const errorId = crypto.randomUUID();
  console.error(`[Client Error ${errorId}]`, error);

  // 可在這裡傳送到 Sentry / LogRocket 等服務
  // await reportToErrorService({ errorId, error, url: event.url.href });

  return {
    message: 'Something went wrong.',
    errorId
  };
};
```

### Step 8：使用 `pushState` 實作 shallow routing（modal URL 模式）

```svelte
<!-- src/routes/photos/+page.svelte -->
<script lang="ts">
  import { pushState } from '$app/navigation';
  import { page } from '$app/state';

  let { data } = $props();

  function openPhoto(photo: { id: string; url: string; title: string }) {
    pushState(`/photos/${photo.id}`, {
      selectedPhoto: photo
    });
  }

  function closeModal() {
    history.back();
  }

  const selectedPhoto = $derived(page.state.selectedPhoto);
</script>

<h1>Photo Gallery</h1>

<div class="grid">
  {#each data.photos as photo}
    <button class="photo-card" onclick={() => openPhoto(photo)}>
      <img src={photo.url} alt={photo.title} />
      <span>{photo.title}</span>
    </button>
  {/each}
</div>

{#if selectedPhoto}
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <div class="overlay" onclick={closeModal} role="dialog">
    <div class="modal" onclick={(e) => e.stopPropagation()}>
      <button class="close-btn" onclick={closeModal}>Close</button>
      <img src={selectedPhoto.url} alt={selectedPhoto.title} />
      <h2>{selectedPhoto.title}</h2>
    </div>
  </div>
{/if}
```

> **注意**：當使用者直接造訪 `/photos/123`（如分享連結），`page.state` 會是空的。你需要在 `/photos/[id]/+page.svelte` 中有對應的完整頁面，或在 `/photos/+page.svelte` 的 load 中處理這個情境。

### Step 9：實作 JWT Auth Middleware 與 Protected Route Group

建立 `(authenticated)` route group 與 layout guard：

```
src/routes/
  (public)/
    login/+page.svelte
  (authenticated)/
    +layout.server.ts
    dashboard/+page.svelte
```

```ts
// src/routes/(authenticated)/+layout.server.ts
import type { LayoutServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: LayoutServerLoad = async ({ locals, url }) => {
  if (!locals.user) {
    const redirectTo = encodeURIComponent(url.pathname + url.search);
    redirect(303, `/login?redirect=${redirectTo}`);
  }

  return { user: locals.user };
};
```

在 `hooks.server.ts` 中加入 JWT 驗證邏輯：

```ts
// src/hooks.server.ts（加入 JWT 驗證）
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET ?? 'dev-secret';

const auth: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get('access_token');

  if (token) {
    try {
      const payload = jwt.verify(token, JWT_SECRET) as {
        sub: string; name: string; role: string;
      };
      event.locals.user = {
        id: payload.sub,
        name: payload.name,
        role: payload.role
      };
    } catch {
      event.cookies.delete('access_token', { path: '/' });
      event.locals.user = null;
    }
  } else {
    event.locals.user = null;
  }

  return resolve(event);
};
```

> **重點**：使用 route group `(authenticated)` 搭配 `+layout.server.ts` 是 SvelteKit 推薦的保護路由方式。所有放在 `(authenticated)/` 下的頁面都會自動經過 layout load 的登入檢查。

### Step 10：實作 Login API Endpoint 與 Token 發放

建立登入 API endpoint 負責驗證帳密並發放 JWT：

```ts
// src/routes/api/auth/login/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET ?? 'dev-secret';

export const POST: RequestHandler = async ({ request, cookies }) => {
  const { email, password } = await request.json();

  // 實際應用中，這裡應查詢資料庫並驗證密碼 hash
  if (email === 'admin@example.com' && password === 'password') {
    const accessToken = jwt.sign(
      { sub: '1', name: 'Admin', role: 'admin' },
      JWT_SECRET,
      { expiresIn: '15m' }
    );

    const refreshToken = jwt.sign(
      { sub: '1', type: 'refresh' },
      JWT_SECRET,
      { expiresIn: '7d' }
    );

    cookies.set('access_token', accessToken, {
      path: '/',
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      maxAge: 60 * 15
    });

    cookies.set('refresh_token', refreshToken, {
      path: '/',
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7
    });

    return json({ success: true });
  }

  return json({ error: 'Invalid credentials' }, { status: 401 });
};
```

> **重點**：Token 存放在 `httpOnly` cookie 中，JavaScript 無法讀取，可有效防止 XSS 攻擊竊取 token。`secure: true` 確保只在 HTTPS 下傳送。

## Hands-on Lab

### Foundation：Auth Hook 與路由保護

建立完整的 auth hook 系統：

- 在 `src/hooks.server.ts` 中建立 `auth` handle，檢查 `session` cookie。
- 若有合法 session，從 mock data 取得使用者並設定 `locals.user`。
- 建立 `guard` handle，未登入使用者造訪 `/dashboard` 時 redirect 到 `/login`。
- 使用 `sequence(auth, guard)` 組合兩個 hooks。
- 在 `/dashboard/+page.server.ts` 中讀取 `locals.user` 並傳入頁面。

**驗收標準**：
- [ ] 沒有 `session` cookie 時，造訪 `/dashboard` 會被 redirect 到 `/login`。
- [ ] 有 `session` cookie 時，`/dashboard` 頁面顯示使用者名稱。
- [ ] `event.locals.user` 型別在 `app.d.ts` 中正確定義。
- [ ] `sequence()` 正確組合 auth 和 guard。

### Advanced：REST API 與 Route Matcher

建立完整的 todo REST API：

- 建立 `src/params/integer.ts` route matcher。
- 建立 `src/routes/api/todos/+server.ts`（GET 列表、POST 新增）。
- 建立 `src/routes/api/todos/[id=integer]/+server.ts`（GET 單一、PUT 更新、DELETE 刪除）。
- 所有寫入操作（POST / PUT / DELETE）需檢查 `locals.user`，未登入回傳 401。
- 回傳適當的 HTTP status codes（200、201、204、401、404）。

**驗收標準**：
- [ ] `GET /api/todos` 回傳 todo 列表。
- [ ] `POST /api/todos` 建立新 todo，回傳 201。
- [ ] `GET /api/todos/1` 回傳單一 todo。
- [ ] `DELETE /api/todos/1` 刪除 todo，未登入回傳 401。
- [ ] `GET /api/todos/abc` 回傳 404（route matcher 攔截）。
- [ ] 所有 response 使用正確的 HTTP status code。

**額外任務：Protected Route Group**

- 建立 `(authenticated)` route group，在 `+layout.server.ts` 中檢查 `locals.user`。
- 將 `/dashboard` 和 `/settings` 放入 `(authenticated)` 群組。
- 未登入時 redirect 到 `/login`，並在 URL 中帶上 `redirect` 參數。
- 建立 `/api/auth/login` endpoint，驗證帳密後發放 JWT cookie。
- 登入成功後 redirect 回原始頁面。

**額外驗收標準**：
- [ ] 未登入訪問 `/dashboard` 時 redirect 到 `/login?redirect=%2Fdashboard`。
- [ ] 登入後自動 redirect 回 `/dashboard`。
- [ ] JWT 存放在 `httpOnly` cookie 中。

### Challenge：Photo Gallery Shallow Routing

建立照片 gallery，使用 shallow routing 實現 modal 瀏覽：

- `/photos` 頁面顯示照片 grid。
- 點擊照片時，URL 更新為 `/photos/[id]`，但不觸發 load（使用 `pushState`）。
- 照片以 modal overlay 顯示，點擊 overlay 背景或按 Escape 關閉。
- 按瀏覽器 back button 可正確關閉 modal。
- 直接造訪 `/photos/[id]` 時（如分享連結），仍能正確顯示照片（fallback 到完整頁面）。
- 在 `app.d.ts` 中定義 `PageState` 型別。

**驗收標準**：
- [ ] 點擊照片時 URL 更新但不觸發頁面 load。
- [ ] Modal 正確顯示所選照片。
- [ ] Back button 關閉 modal 並回到 `/photos`。
- [ ] 直接造訪 `/photos/123` 可正確顯示（不依賴 shallow state）。
- [ ] `PageState` 型別正確定義在 `app.d.ts`。
- [ ] Escape 鍵可關閉 modal。

## Reference Solution

### hooks.server.ts

```ts
// src/hooks.server.ts
import type { Handle, HandleServerError } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { redirect } from '@sveltejs/kit';

const auth: Handle = async ({ event, resolve }) => {
  const sessionId = event.cookies.get('session');
  if (sessionId) {
    // In production, validate session against DB
    event.locals.user = { id: '1', name: 'Alice', role: 'admin' };
  } else {
    event.locals.user = null;
  }
  return resolve(event);
};

const logger: Handle = async ({ event, resolve }) => {
  const start = Date.now();
  const response = await resolve(event);
  const duration = Date.now() - start;
  console.log(`${event.request.method} ${event.url.pathname} - ${response.status} (${duration}ms)`);
  return response;
};

const guard: Handle = async ({ event, resolve }) => {
  if (event.url.pathname.startsWith('/dashboard') && !event.locals.user) {
    redirect(303, '/login');
  }
  return resolve(event);
};

export const handle = sequence(auth, guard, logger);

export const handleError: HandleServerError = async ({ error, event }) => {
  const errorId = crypto.randomUUID();
  console.error(`Unhandled error [${errorId}] on ${event.url.pathname}:`, error);
  return {
    message: 'An unexpected error occurred.',
    errorId
  };
};
```

### Route Matcher

```ts
// src/params/integer.ts
import type { ParamMatcher } from '@sveltejs/kit';

export const match: ParamMatcher = (param) => {
  return /^\d+$/.test(param);
};
```

### REST API Endpoint

```ts
// src/routes/api/todos/[id=integer]/+server.ts
import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const todos = new Map([
  [1, { id: 1, text: 'Learn SvelteKit hooks', done: true }],
  [2, { id: 2, text: 'Build REST API', done: false }],
  [3, { id: 3, text: 'Deploy to production', done: false }]
]);

export const GET: RequestHandler = async ({ params }) => {
  const id = parseInt(params.id);
  const todo = todos.get(id);
  if (!todo) error(404, 'Todo not found');
  return json(todo);
};

export const PUT: RequestHandler = async ({ params, request, locals }) => {
  if (!locals.user) error(401, 'Unauthorized');
  const id = parseInt(params.id);
  const todo = todos.get(id);
  if (!todo) error(404, 'Todo not found');
  const updates = await request.json();
  const updated = { ...todo, ...updates };
  todos.set(id, updated);
  return json(updated);
};

export const DELETE: RequestHandler = async ({ params, locals }) => {
  if (!locals.user) error(401, 'Unauthorized');
  const id = parseInt(params.id);
  if (!todos.has(id)) error(404, 'Todo not found');
  todos.delete(id);
  return json({ deleted: true, id });
};
```

### Shallow Routing Photo Gallery

```svelte
<!-- src/routes/photos/+page.svelte -->
<script lang="ts">
  import { pushState } from '$app/navigation';
  import { page } from '$app/state';

  let { data } = $props();

  interface Photo {
    id: string;
    url: string;
    title: string;
  }

  function openPhoto(photo: Photo) {
    pushState(`/photos/${photo.id}`, { selectedPhoto: photo });
  }

  function closeModal() {
    history.back();
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && page.state.selectedPhoto) {
      closeModal();
    }
  }

  const selectedPhoto = $derived(page.state.selectedPhoto as Photo | undefined);
</script>

<svelte:window onkeydown={handleKeydown} />

<h1>Photo Gallery</h1>

<div class="grid">
  {#each data.photos as photo}
    <button class="photo-card" onclick={() => openPhoto(photo)}>
      <img src={photo.url} alt={photo.title} loading="lazy" />
      <span>{photo.title}</span>
    </button>
  {/each}
</div>

{#if selectedPhoto}
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <div class="overlay" onclick={closeModal} role="dialog" aria-modal="true">
    <div class="modal" onclick={(e) => e.stopPropagation()}>
      <button class="close-btn" onclick={closeModal} aria-label="Close">x</button>
      <img src={selectedPhoto.url} alt={selectedPhoto.title} />
      <h2>{selectedPhoto.title}</h2>
    </div>
  </div>
{/if}

<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }
  .photo-card {
    border: none;
    background: none;
    cursor: pointer;
    padding: 0;
  }
  .photo-card img {
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
    border-radius: 8px;
  }
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }
  .modal {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    max-width: 90vw;
    max-height: 90vh;
    position: relative;
  }
  .modal img {
    max-width: 100%;
    max-height: 70vh;
    border-radius: 8px;
  }
  .close-btn {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: rgba(0, 0, 0, 0.5);
    color: white;
    border: none;
    border-radius: 50%;
    width: 2rem;
    height: 2rem;
    cursor: pointer;
    font-size: 1rem;
  }
</style>
```

**重點解析**：

- `sequence(auth, guard, logger)` 的執行順序至關重要：auth 必須先設定 `locals.user`，guard 才能判斷是否要 redirect。
- `handleError` 回傳的物件會成為 `$page.error`，注意不要洩漏內部錯誤細節。
- Route matcher 讓你在路由層級就過濾掉不合法的參數，避免在 handler 中手動驗證。
- `pushState` 的第二個參數是 state 物件，可在 `page.state` 中讀取。直接造訪該 URL 時 `page.state` 為空，需要有 fallback 機制。

## Common Pitfalls

### 1. 忘記在 `handle` 中呼叫 `resolve(event)` -- request 永遠不回應

```ts
// 錯誤：沒有呼叫 resolve，request 會 hang 住
const broken: Handle = async ({ event, resolve }) => {
  console.log('Logging request...');
  // 忘記 return resolve(event)
};

// 正確：一定要呼叫 resolve 並回傳結果
const correct: Handle = async ({ event, resolve }) => {
  console.log('Logging request...');
  return resolve(event);  // 必須呼叫且回傳
};
```

`handle` 函式的 `resolve` 就像 Express 的 `next()`，不呼叫就不會繼續處理 request。

### 2. 在 hooks 中放入過重的邏輯 -- 影響每個 request 的效能

```ts
// 錯誤：每個 request 都查詢資料庫兩次
const heavyHook: Handle = async ({ event, resolve }) => {
  const user = await db.getUserBySession(event.cookies.get('session'));  // DB query
  const permissions = await db.getPermissions(user?.id);                 // 又一次 DB query
  const preferences = await db.getPreferences(user?.id);                 // 又一次！
  event.locals.user = user;
  event.locals.permissions = permissions;
  event.locals.preferences = preferences;
  return resolve(event);
};

// 正確：只做必要的驗證，其餘延遲到需要時才載入
const efficientHook: Handle = async ({ event, resolve }) => {
  const sessionId = event.cookies.get('session');
  if (sessionId) {
    // 只做基本驗證，一次 DB query
    event.locals.user = await db.getUserBySession(sessionId);
  }
  return resolve(event);
};
```

Hooks 在每個 request 都會執行，務必保持輕量。詳細資料應在各別的 `load` 函式中按需載入。

### 3. `redirect()` 沒有排除目標路徑 -- 無限 redirect loop

```ts
// 錯誤：/login 也匹配 guard，造成無限 redirect
const guard: Handle = async ({ event, resolve }) => {
  if (!event.locals.user) {
    redirect(303, '/login');  // /login 也會觸發這個 guard！
  }
  return resolve(event);
};

// 正確：明確排除不需要認證的路徑
const guard: Handle = async ({ event, resolve }) => {
  const publicPaths = ['/login', '/register', '/api/auth'];
  const isPublic = publicPaths.some(path => event.url.pathname.startsWith(path));

  if (!isPublic && !event.locals.user) {
    redirect(303, '/login');
  }
  return resolve(event);
};
```

設計 guard 時，一定要定義哪些路徑是公開的（whitelist）或哪些路徑需要保護（blacklist）。

### 4. 混淆 `+server.ts` 與 `+page.server.ts` 的用途

```
src/routes/api/todos/
  +server.ts         ← REST API endpoint（回傳 JSON）
  +page.server.ts    ← 頁面資料載入（回傳給 Svelte 元件）
  +page.svelte       ← 頁面 UI
```

- `+server.ts`：處理 HTTP methods（GET/POST/PUT/DELETE），回傳 `Response` 物件，適合給外部或 `fetch` 呼叫。
- `+page.server.ts`：export `load` 函式回傳頁面資料，export `actions` 處理表單提交，只供同路由的 `+page.svelte` 使用。

如果同一路由同時有 `+server.ts` 和 `+page.server.ts`，SvelteKit 會根據 `Accept` header 決定用哪一個。純 API route 通常不會有 `+page.svelte`。

### 5. 修改 `event.locals` 型別但忘記更新 `app.d.ts`

```ts
// hooks.server.ts 中使用了新的 locals 欄位
event.locals.requestId = crypto.randomUUID();  // TypeScript error!

// 必須在 app.d.ts 中先定義
// src/app.d.ts
declare global {
  namespace App {
    interface Locals {
      user: { id: string; name: string; role: string } | null;
      requestId: string;  // 新增這行
    }
  }
}
export {};
```

`app.d.ts` 是 SvelteKit 的型別定義檔，所有 `Locals`、`PageData`、`PageState`、`Error` 的自訂型別都在這裡定義。修改 locals 結構時務必同步更新。

## Checklist

- [ ] 能在 `hooks.server.ts` 中建立 `handle` 並正確呼叫 `resolve(event)`
- [ ] 能使用 `sequence()` 組合多個 handle 函式（auth, guard, logger）
- [ ] 能設定 `event.locals` 並在 `+page.server.ts` 的 load 函式中讀取
- [ ] 能建立 `+server.ts` REST API endpoints（GET / POST / PUT / DELETE）
- [ ] 能建立 route parameter matcher（`src/params/integer.ts`）
- [ ] 能使用 `pushState` / `replaceState` 實作 shallow routing
- [ ] 能實作 JWT auth middleware 保護路由
- [ ] 能在 `app.d.ts` 中正確定義 `Locals` 和 `PageState` 型別
- [ ] `npx svelte-check` 通過

## Further Reading

- [Hooks -- SvelteKit docs](https://svelte.dev/docs/kit/hooks)
- [handle -- SvelteKit docs](https://svelte.dev/docs/kit/@sveltejs-kit#Handle)
- [handleFetch -- SvelteKit docs](https://svelte.dev/docs/kit/@sveltejs-kit#HandleFetch)
- [handleError -- SvelteKit docs](https://svelte.dev/docs/kit/@sveltejs-kit#HandleServerError)
- [sequence -- SvelteKit docs](https://svelte.dev/docs/kit/@sveltejs-kit-hooks)
- [Routing -- SvelteKit docs](https://svelte.dev/docs/kit/routing)
- [+server -- SvelteKit docs](https://svelte.dev/docs/kit/+server)
- [Page options -- SvelteKit docs](https://svelte.dev/docs/kit/page-options)
- [Shallow routing -- SvelteKit docs](https://svelte.dev/docs/kit/shallow-routing)
- [Types -- SvelteKit docs (app.d.ts)](https://svelte.dev/docs/kit/types)
- [SvelteKit Tutorial: Hooks](https://svelte.dev/tutorial/kit/handle)
- [SvelteKit Tutorial: API routes](https://svelte.dev/tutorial/kit/get-handlers)
