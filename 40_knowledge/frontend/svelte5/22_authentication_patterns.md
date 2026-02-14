---
title: "Authentication Patterns / 認證模式"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "22"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [14_advanced_routing_and_hooks]
---

# Authentication Patterns / 認證模式

## Goal

深入理解並實作 SvelteKit 應用中最常見的認證模式——JWT-based Auth、Session-based Auth、OAuth 整合，以及相關的安全實踐。認證是幾乎所有 Web 應用的基礎需求，正確實作認證不僅影響功能性，更直接關係到應用的安全性。

本章將從 JWT 的簽發與驗證開始，逐步建構完整的認證流程：登入 API、HttpOnly Cookie 管理、handle hook 自動驗證、受保護路由、角色權限控制（RBAC）、OAuth 第三方登入整合，以及 Token 刷新與安全登出。每個環節都提供完整的程式碼範例與安全考量說明。

- 銜接上一章：Ch14 學會了進階路由與 hooks，現在要利用 hooks 機制實作認證中介層。
- 下一章預告：後續章節將涵蓋更進階的主題如部署、效能優化等。

## Prerequisites

- 已完成 Ch14，理解 SvelteKit 的 hooks 機制（`handle`、`handleFetch`）和 `event.locals`。
- 理解 HTTP Cookie 的基本概念（domain、path、HttpOnly、Secure、SameSite）。
- 理解 SvelteKit 的 `+server.ts`（API route）和 `+page.server.ts`（form action / load）。
- 具備基礎的 Web 安全知識（HTTPS、XSS、CSRF）。

## Core Concepts

### 1. JWT-based Auth 完整實作

JWT（JSON Web Token）是一種自包含的認證 token，伺服器簽發後由客戶端保存，每次請求時附帶以驗證身份。在 SvelteKit 中，最佳實踐是將 JWT 存放在 HttpOnly Cookie 中，由 handle hook 在每次請求時自動驗證。

#### JWT 結構

一個 JWT 由三部分組成（以 `.` 分隔）：
- **Header**：演算法和類型（如 `{"alg": "HS256", "typ": "JWT"}`）
- **Payload**：使用者資訊和聲明（如 `{"sub": "user123", "role": "admin", "exp": 1700000000}`）
- **Signature**：使用密鑰對 header + payload 進行簽名，確保 token 未被竄改

#### jose 函式庫

推薦使用 `jose` 函式庫處理 JWT，它是純 JavaScript 實作，支援 Web Crypto API，可在 Node.js 和 Edge Runtime（如 Vercel Edge Functions）中運行。

```ts
// src/lib/server/auth.ts
import { SignJWT, jwtVerify, type JWTPayload } from 'jose';
import { JWT_SECRET } from '$env/static/private';

const secret = new TextEncoder().encode(JWT_SECRET);

export interface UserPayload extends JWTPayload {
  sub: string;
  email: string;
  role: 'user' | 'admin';
}

export async function createToken(user: { id: string; email: string; role: 'user' | 'admin' }) {
  return new SignJWT({
    sub: user.id,
    email: user.email,
    role: user.role
  })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('1h')
    .sign(secret);
}

export async function verifyToken(token: string): Promise<UserPayload | null> {
  try {
    const { payload } = await jwtVerify(token, secret);
    return payload as UserPayload;
  } catch {
    return null;
  }
}
```

#### Login API Endpoint

```ts
// src/routes/api/auth/login/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createToken } from '$lib/server/auth';

// 模擬使用者資料庫（實際應連接資料庫）
const USERS = [
  { id: '1', email: 'admin@example.com', password: 'hashed_password', role: 'admin' as const },
  { id: '2', email: 'user@example.com', password: 'hashed_password', role: 'user' as const }
];

export const POST: RequestHandler = async ({ request, cookies }) => {
  const { email, password } = await request.json();

  // 驗證使用者（實際應使用 bcrypt 比對 hash）
  const user = USERS.find(u => u.email === email);
  if (!user || user.password !== password) {
    return json({ error: 'Invalid credentials' }, { status: 401 });
  }

  // 簽發 JWT
  const token = await createToken({
    id: user.id,
    email: user.email,
    role: user.role
  });

  // 設定 HttpOnly Cookie
  cookies.set('auth_token', token, {
    path: '/',
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: 60 * 60 // 1 hour
  });

  return json({
    user: { id: user.id, email: user.email, role: user.role }
  });
};
```

#### handle Hook 自動驗證

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { verifyToken } from '$lib/server/auth';

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get('auth_token');

  if (token) {
    const payload = await verifyToken(token);
    if (payload) {
      event.locals.user = {
        id: payload.sub!,
        email: payload.email,
        role: payload.role
      };
    } else {
      // Token 無效或過期，清除 cookie
      event.cookies.delete('auth_token', { path: '/' });
    }
  }

  return resolve(event);
};
```

#### 型別定義

```ts
// src/app.d.ts
declare global {
  namespace App {
    interface Locals {
      user?: {
        id: string;
        email: string;
        role: 'user' | 'admin';
      };
    }
  }
}

export {};
```

- **何時用 JWT-based Auth**：需要無狀態認證的場景——RESTful API、Serverless / Edge 部署（無法維持 session store）、微服務架構中跨服務認證。
- **何時不用**：需要即時撤銷 token（JWT 簽發後在過期前無法撤銷，除非搭配黑名單機制）、或需要儲存大量 session 資料的場景。

### 2. Session-based Auth

Session-based Auth 將使用者資訊儲存在伺服器端，客戶端只保存一個 session ID。

#### 與 JWT 的比較

| 特性 | JWT | Session |
|------|-----|---------|
| 狀態儲存 | 客戶端（token 自包含） | 伺服器端（記憶體/資料庫/Redis） |
| 可擴展性 | 高（無需伺服器端儲存） | 需要共享 session store |
| 即時撤銷 | 困難（需黑名單） | 容易（刪除 session 即可） |
| Token 大小 | 較大（含 payload） | 較小（僅 session ID） |
| 適合場景 | API、Serverless、微服務 | 傳統 Web App、需要即時撤銷 |
| 安全性 | Token 洩露風險較高 | Session hijacking 風險 |

#### Session Store 概念實作

```ts
// src/lib/server/session.ts
import { randomUUID } from 'crypto';

interface SessionData {
  userId: string;
  email: string;
  role: 'user' | 'admin';
  createdAt: number;
  expiresAt: number;
}

// 記憶體 session store（生產環境應使用 Redis 等持久化方案）
const sessions = new Map<string, SessionData>();

export function createSession(user: { id: string; email: string; role: 'user' | 'admin' }): string {
  const sessionId = randomUUID();
  const now = Date.now();

  sessions.set(sessionId, {
    userId: user.id,
    email: user.email,
    role: user.role,
    createdAt: now,
    expiresAt: now + 24 * 60 * 60 * 1000 // 24 hours
  });

  return sessionId;
}

export function getSession(sessionId: string): SessionData | null {
  const session = sessions.get(sessionId);
  if (!session) return null;
  if (Date.now() > session.expiresAt) {
    sessions.delete(sessionId);
    return null;
  }
  return session;
}

export function deleteSession(sessionId: string): void {
  sessions.delete(sessionId);
}
```

- **何時用 Session-based Auth**：傳統 Web 應用、需要即時撤銷權限（如管理員停用帳號後立即生效）、session 資料較多且頻繁變更的場景。
- **何時不用**：Serverless / Edge 部署（難以維持 session store）、需要跨域或跨服務共享認證的場景。

### 3. OAuth 整合 (Google / GitHub)

OAuth 讓使用者透過第三方服務（Google、GitHub 等）登入你的應用，無需在你的應用中建立密碼。

#### OAuth 2.0 流程說明

```
1. 使用者點擊「Login with GitHub」
2. 應用將使用者重導到 GitHub 授權頁面
3. 使用者在 GitHub 上授權
4. GitHub 將使用者重導回你的應用，附帶 authorization code
5. 你的應用用 code 向 GitHub 換取 access token
6. 你的應用用 access token 向 GitHub API 取得使用者資訊
7. 建立或更新本地使用者記錄，簽發 JWT 或建立 session
```

#### 使用 arctic 函式庫

`arctic` 是一個輕量的 OAuth 函式庫，支援多種 OAuth provider。

```bash
npm install arctic
```

#### GitHub OAuth 實作

```ts
// src/lib/server/oauth.ts
import { GitHub } from 'arctic';
import { GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET } from '$env/static/private';

export const github = new GitHub(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, null);
```

```ts
// src/routes/auth/github/+server.ts
import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { github } from '$lib/server/oauth';
import { generateState } from 'arctic';

export const GET: RequestHandler = async ({ cookies }) => {
  const state = generateState();
  const url = github.createAuthorizationURL(state, ['user:email']);

  cookies.set('github_oauth_state', state, {
    path: '/',
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: 60 * 10 // 10 minutes
  });

  redirect(302, url.toString());
};
```

```ts
// src/routes/auth/github/callback/+server.ts
import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { github } from '$lib/server/oauth';
import { createToken } from '$lib/server/auth';

interface GitHubUser {
  id: number;
  login: string;
  email: string | null;
  avatar_url: string;
}

export const GET: RequestHandler = async ({ url, cookies }) => {
  const code = url.searchParams.get('code');
  const state = url.searchParams.get('state');
  const storedState = cookies.get('github_oauth_state');

  if (!code || !state || state !== storedState) {
    redirect(302, '/login?error=oauth_failed');
  }

  try {
    const tokens = await github.validateAuthorizationCode(code);

    // 取得 GitHub 使用者資訊
    const response = await fetch('https://api.github.com/user', {
      headers: {
        Authorization: `Bearer ${tokens.accessToken()}`
      }
    });

    const githubUser: GitHubUser = await response.json();

    // 查找或建立本地使用者（實際應操作資料庫）
    const localUser = {
      id: `github_${githubUser.id}`,
      email: githubUser.email ?? `${githubUser.login}@github.local`,
      role: 'user' as const
    };

    // 簽發 JWT
    const token = await createToken(localUser);

    cookies.set('auth_token', token, {
      path: '/',
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      maxAge: 60 * 60
    });

    // 清除 OAuth state cookie
    cookies.delete('github_oauth_state', { path: '/' });

    redirect(302, '/dashboard');
  } catch {
    redirect(302, '/login?error=oauth_failed');
  }
};
```

- **何時用 OAuth**：面向終端使用者的應用（讓使用者免除記憶密碼的負擔）、需要存取第三方 API 資料（如 GitHub repos、Google Calendar）、希望降低自行管理密碼的安全風險。
- **何時不用**：純內部系統（員工數有限，直接管理帳號更簡單）、不希望依賴第三方服務的場景。

### 4. Protected Routes & RBAC

在實際應用中，許多頁面需要限制存取——只有已認證的使用者或具有特定角色的使用者才能訪問。

#### Layout-level Auth Guard

利用 SvelteKit 的 route group 功能，建立一個 `(auth)` 群組來保護需要認證的路由：

```
src/routes/
├── (auth)/
│   ├── +layout.server.ts    ← 認證守衛
│   ├── dashboard/
│   │   └── +page.svelte
│   ├── settings/
│   │   └── +page.svelte
│   └── admin/               ← 需要 admin 角色
│       ├── +layout.server.ts ← 角色守衛
│       └── +page.svelte
├── login/
│   └── +page.svelte         ← 公開頁面
└── +page.svelte              ← 公開首頁
```

```ts
// src/routes/(auth)/+layout.server.ts
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  if (!locals.user) {
    redirect(303, '/login');
  }

  return {
    user: locals.user
  };
};
```

#### Role-based Access Control (RBAC)

```ts
// src/routes/(auth)/admin/+layout.server.ts
import { error, redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  if (!locals.user) {
    redirect(303, '/login');
  }

  if (locals.user.role !== 'admin') {
    error(403, 'Forbidden: Admin access required');
  }

  return {
    user: locals.user
  };
};
```

#### 在 Layout 元件中顯示使用者資訊

```svelte
<!-- src/routes/(auth)/+layout.svelte -->
<script lang="ts">
  import type { LayoutData } from './$types';
  import type { Snippet } from 'svelte';

  let { data, children }: { data: LayoutData; children: Snippet } = $props();
</script>

<nav>
  <span>Welcome, {data.user.email}</span>
  <span class="badge">{data.user.role}</span>
  <a href="/dashboard">Dashboard</a>
  {#if data.user.role === 'admin'}
    <a href="/admin">Admin Panel</a>
  {/if}
  <form method="POST" action="/api/auth/logout">
    <button type="submit">Logout</button>
  </form>
</nav>

<main>
  {@render children()}
</main>
```

- **何時用 route group 守衛**：大量路由需要相同的認證/授權邏輯時，用 layout 統一處理最高效。
- **何時不用**：只有一兩個頁面需要保護時，直接在個別 `+page.server.ts` 的 `load` 函式中檢查即可。

### 5. Token Refresh & Secure Logout

JWT 有效期通常設定較短（15 分鐘到 1 小時），需要 token 刷新機制來維持使用者登入狀態，並提供安全的登出流程。

#### Silent Refresh 實作

在 handle hook 中檢測 token 即將過期時自動刷新：

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { verifyToken, createToken, type UserPayload } from '$lib/server/auth';

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get('auth_token');

  if (token) {
    const payload = await verifyToken(token);

    if (payload) {
      event.locals.user = {
        id: payload.sub!,
        email: payload.email,
        role: payload.role
      };

      // 檢查 token 是否即將過期（剩餘 15 分鐘內）
      const exp = payload.exp ?? 0;
      const now = Math.floor(Date.now() / 1000);
      const remainingSeconds = exp - now;

      if (remainingSeconds < 15 * 60) {
        // 簽發新 token
        const newToken = await createToken({
          id: payload.sub!,
          email: payload.email,
          role: payload.role
        });

        event.cookies.set('auth_token', newToken, {
          path: '/',
          httpOnly: true,
          secure: true,
          sameSite: 'lax',
          maxAge: 60 * 60
        });
      }
    } else {
      // Token 無效，清除
      event.cookies.delete('auth_token', { path: '/' });
    }
  }

  return resolve(event);
};
```

#### Secure Logout

```ts
// src/routes/api/auth/logout/+server.ts
import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ cookies }) => {
  // 清除認證 cookie
  cookies.delete('auth_token', { path: '/' });

  // 如果使用 session-based auth，也要在伺服器端刪除 session
  // const sessionId = cookies.get('session_id');
  // if (sessionId) {
  //   deleteSession(sessionId);
  //   cookies.delete('session_id', { path: '/' });
  // }

  redirect(303, '/login');
};
```

#### 客戶端登出按鈕

```svelte
<script lang="ts">
  async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/login';
  }
</script>

<button onclick={logout}>Logout</button>
```

或使用原生表單（支援漸進增強）：

```svelte
<form method="POST" action="/api/auth/logout">
  <button type="submit">Logout</button>
</form>
```

- **何時需要 token refresh**：JWT 有效期較短（< 2 小時）且需要長時間保持登入狀態的場景。
- **何時不需要**：JWT 有效期較長（如 7 天）且安全要求較低的內部工具、或使用 session-based auth 時（session 可直接延長過期時間）。

## Step-by-step

### Step 1：安裝 jose 函式庫

```bash
npm install jose
```

`jose` 是一個零依賴的 JavaScript JOSE（JSON Object Signing and Encryption）實作，支援 JWT、JWS、JWE 等標準。

### Step 2：建立 JWT 工具模組

在 `src/lib/server/` 目錄下建立認證工具模組。注意 `server/` 目錄下的檔案只能在伺服器端載入。

```ts
// src/lib/server/auth.ts
import { SignJWT, jwtVerify, type JWTPayload } from 'jose';
import { JWT_SECRET } from '$env/static/private';

const secret = new TextEncoder().encode(JWT_SECRET);

export interface UserPayload extends JWTPayload {
  sub: string;
  email: string;
  role: 'user' | 'admin';
}

/** 簽發 JWT，有效期 1 小時 */
export async function createToken(user: {
  id: string;
  email: string;
  role: 'user' | 'admin';
}): Promise<string> {
  return new SignJWT({
    sub: user.id,
    email: user.email,
    role: user.role
  })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('1h')
    .sign(secret);
}

/** 驗證 JWT，回傳 payload 或 null */
export async function verifyToken(token: string): Promise<UserPayload | null> {
  try {
    const { payload } = await jwtVerify(token, secret);
    return payload as UserPayload;
  } catch {
    return null;
  }
}
```

別忘了在 `.env` 中設定密鑰：

```
JWT_SECRET=your-super-secret-key-at-least-32-chars-long
```

### Step 3：建立 Login API Endpoint

```ts
// src/routes/api/auth/login/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createToken } from '$lib/server/auth';

// 實際應用中應連接資料庫並使用 bcrypt 比對密碼
async function authenticateUser(email: string, password: string) {
  // 模擬資料庫查詢
  if (email === 'admin@example.com' && password === 'admin123') {
    return { id: '1', email, role: 'admin' as const };
  }
  if (email === 'user@example.com' && password === 'user123') {
    return { id: '2', email, role: 'user' as const };
  }
  return null;
}

export const POST: RequestHandler = async ({ request, cookies }) => {
  const body = await request.json();
  const { email, password } = body;

  if (!email || !password) {
    return json({ error: 'Email and password are required' }, { status: 400 });
  }

  const user = await authenticateUser(email, password);
  if (!user) {
    return json({ error: 'Invalid email or password' }, { status: 401 });
  }

  const token = await createToken(user);

  cookies.set('auth_token', token, {
    path: '/',
    httpOnly: true,    // 防止 JavaScript 存取
    secure: true,       // 只透過 HTTPS 傳送
    sameSite: 'lax',    // 防止 CSRF
    maxAge: 60 * 60     // 1 小時
  });

  return json({
    user: { id: user.id, email: user.email, role: user.role }
  });
};
```

### Step 4：建立 Login 表單頁面

```svelte
<!-- src/routes/login/+page.svelte -->
<script lang="ts">
  import { goto } from '$app/navigation';

  let email = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);

  async function handleLogin(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    loading = true;

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (!res.ok) {
        error = data.error ?? 'Login failed';
        return;
      }

      // 登入成功，跳轉到 dashboard
      await goto('/dashboard');
    } catch {
      error = 'Network error. Please try again.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="login-container">
  <h1>Login</h1>

  {#if error}
    <div class="error-banner" role="alert">{error}</div>
  {/if}

  <form onsubmit={handleLogin}>
    <div class="field">
      <label for="email">Email</label>
      <input
        id="email"
        type="email"
        bind:value={email}
        required
        autocomplete="email"
      />
    </div>

    <div class="field">
      <label for="password">Password</label>
      <input
        id="password"
        type="password"
        bind:value={password}
        required
        autocomplete="current-password"
      />
    </div>

    <button type="submit" disabled={loading}>
      {loading ? 'Logging in...' : 'Login'}
    </button>
  </form>

  <div class="oauth-section">
    <p>Or login with:</p>
    <a href="/auth/github" class="oauth-button">Login with GitHub</a>
  </div>
</div>

<style>
  .login-container { max-width: 400px; margin: 2rem auto; padding: 2rem; }
  .field { margin-bottom: 1rem; }
  .field label { display: block; margin-bottom: 0.25rem; font-weight: 600; }
  .field input { width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; }
  .error-banner { background: #fee; color: #c00; padding: 0.75rem; border-radius: 4px; margin-bottom: 1rem; }
  button[type="submit"] { width: 100%; padding: 0.75rem; background: #333; color: white; border: none; border-radius: 4px; cursor: pointer; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  .oauth-section { margin-top: 1.5rem; text-align: center; }
  .oauth-button { display: inline-block; padding: 0.5rem 1rem; border: 1px solid #333; border-radius: 4px; text-decoration: none; color: #333; }
</style>
```

### Step 5：實作 handle Hook 進行 JWT 自動驗證

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { verifyToken } from '$lib/server/auth';

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get('auth_token');

  if (token) {
    const payload = await verifyToken(token);
    if (payload) {
      event.locals.user = {
        id: payload.sub!,
        email: payload.email,
        role: payload.role
      };
    } else {
      // Token 無效或過期，清除 cookie
      event.cookies.delete('auth_token', { path: '/' });
    }
  }

  return resolve(event);
};
```

### Step 6：設定 `event.locals.user` 型別

```ts
// src/app.d.ts
declare global {
  namespace App {
    interface Locals {
      user?: {
        id: string;
        email: string;
        role: 'user' | 'admin';
      };
    }
  }
}

export {};
```

這讓 TypeScript 能正確推導 `event.locals.user` 的型別，在所有 `+page.server.ts` 和 `+server.ts` 中都可安全存取。

### Step 7：建立受保護的 Layout

```ts
// src/routes/(auth)/+layout.server.ts
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  if (!locals.user) {
    redirect(303, '/login');
  }

  return {
    user: locals.user
  };
};
```

### Step 8：未認證使用者重導機制

在 Login 頁面的 `load` 中，已認證的使用者應直接跳轉到 dashboard：

```ts
// src/routes/login/+page.server.ts
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  // 已登入的使用者不需要看 login 頁面
  if (locals.user) {
    redirect(303, '/dashboard');
  }
};
```

對於需要保存原始目標 URL 的情況：

```ts
// src/routes/(auth)/+layout.server.ts
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals, url }) => {
  if (!locals.user) {
    // 保存原始目標 URL，登入後跳回
    const redirectTo = encodeURIComponent(url.pathname + url.search);
    redirect(303, `/login?redirect=${redirectTo}`);
  }

  return { user: locals.user };
};
```

### Step 9：加入 Token Refresh 邏輯

更新 `hooks.server.ts` 加入自動刷新：

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { verifyToken, createToken } from '$lib/server/auth';

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get('auth_token');

  if (token) {
    const payload = await verifyToken(token);

    if (payload) {
      event.locals.user = {
        id: payload.sub!,
        email: payload.email,
        role: payload.role
      };

      // 自動刷新：如果 token 將在 15 分鐘內過期
      const exp = payload.exp ?? 0;
      const now = Math.floor(Date.now() / 1000);
      if (exp - now < 15 * 60) {
        const newToken = await createToken({
          id: payload.sub!,
          email: payload.email,
          role: payload.role
        });
        event.cookies.set('auth_token', newToken, {
          path: '/',
          httpOnly: true,
          secure: true,
          sameSite: 'lax',
          maxAge: 60 * 60
        });
      }
    } else {
      event.cookies.delete('auth_token', { path: '/' });
    }
  }

  return resolve(event);
};
```

### Step 10：實作安全登出

```ts
// src/routes/api/auth/logout/+server.ts
import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ cookies }) => {
  cookies.delete('auth_token', { path: '/' });
  redirect(303, '/login');
};
```

在受保護的 layout 中加入登出按鈕：

```svelte
<!-- src/routes/(auth)/+layout.svelte -->
<script lang="ts">
  import type { LayoutData } from './$types';
  import type { Snippet } from 'svelte';

  let { data, children }: { data: LayoutData; children: Snippet } = $props();
</script>

<header>
  <nav>
    <a href="/dashboard">Dashboard</a>
    {#if data.user.role === 'admin'}
      <a href="/admin">Admin</a>
    {/if}
    <span>{data.user.email} ({data.user.role})</span>
    <form method="POST" action="/api/auth/logout" style="display:inline;">
      <button type="submit">Logout</button>
    </form>
  </nav>
</header>

<main>
  {@render children()}
</main>
```

## Hands-on Lab

### Foundation 基礎層

**任務**：實作基本的 Login / Logout 流程。

要求：
- 建立 JWT 工具模組（`src/lib/server/auth.ts`）。
- 建立 Login API endpoint（`POST /api/auth/login`）。
- 建立 Logout API endpoint（`POST /api/auth/logout`）。
- 建立 Login 頁面，包含 email 和 password 表單。
- 登入成功後跳轉到 `/dashboard`。
- 登出後跳轉到 `/login`。

驗收條件：
- 使用正確帳號可成功登入並看到 dashboard。
- 使用錯誤帳號會顯示錯誤訊息。
- 登出後無法存取 dashboard。
- `npx svelte-check` 通過。

### Advanced 進階層

**任務**：加入 JWT 自動驗證、Token Refresh 和受保護路由。

要求：
- 實作 `handle` hook 在每次請求時自動驗證 JWT。
- 建立 `(auth)` route group 保護 `/dashboard` 和 `/settings` 路由。
- 未認證使用者訪問受保護路由時自動重導到 `/login`。
- 實作 token refresh——token 即將過期時自動刷新。
- 在 `app.d.ts` 中正確定義 `Locals` 型別。

驗收條件：
- 未登入時訪問 `/dashboard` 會自動跳轉到 `/login`。
- 已登入時再訪問 `/login` 會自動跳轉到 `/dashboard`。
- Token 在即將過期時自動刷新，使用者無需重新登入。
- `npx svelte-check` 通過。

### Challenge 挑戰層

**任務**：加入 GitHub OAuth 登入和 RBAC 權限控制。

要求：
- 使用 `arctic` 函式庫實作 GitHub OAuth 登入。
- 建立 OAuth 發起路由（`/auth/github`）和 callback 路由（`/auth/github/callback`）。
- 實作 RBAC：建立 `admin` route group，僅 admin 角色可存取。
- 非 admin 角色訪問 admin 頁面時顯示 403 錯誤。
- 整合 OAuth 登入與 JWT 認證（OAuth 成功後簽發 JWT）。

驗收條件：
- 點擊「Login with GitHub」可跳轉到 GitHub 授權頁面。
- 授權後正確回到應用並建立認證。
- admin 頁面僅 admin 角色可存取。
- 一般使用者訪問 admin 頁面看到 403 錯誤。
- `npx svelte-check` 通過。

## Reference Solution

### 完整專案結構

```
src/
├── app.d.ts
├── hooks.server.ts
├── lib/
│   └── server/
│       ├── auth.ts
│       └── oauth.ts
├── routes/
│   ├── (auth)/
│   │   ├── +layout.server.ts
│   │   ├── +layout.svelte
│   │   ├── dashboard/
│   │   │   └── +page.svelte
│   │   ├── settings/
│   │   │   └── +page.svelte
│   │   └── admin/
│   │       ├── +layout.server.ts
│   │       └── +page.svelte
│   ├── api/auth/
│   │   ├── login/+server.ts
│   │   └── logout/+server.ts
│   ├── auth/
│   │   └── github/
│   │       ├── +server.ts
│   │       └── callback/+server.ts
│   ├── login/
│   │   ├── +page.server.ts
│   │   └── +page.svelte
│   └── +page.svelte
```

### JWT 工具模組

```ts
// src/lib/server/auth.ts
import { SignJWT, jwtVerify, type JWTPayload } from 'jose';
import { JWT_SECRET } from '$env/static/private';

const secret = new TextEncoder().encode(JWT_SECRET);

export interface UserPayload extends JWTPayload {
  sub: string;
  email: string;
  role: 'user' | 'admin';
}

export async function createToken(user: {
  id: string;
  email: string;
  role: 'user' | 'admin';
}): Promise<string> {
  return new SignJWT({
    sub: user.id,
    email: user.email,
    role: user.role
  })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('1h')
    .sign(secret);
}

export async function verifyToken(token: string): Promise<UserPayload | null> {
  try {
    const { payload } = await jwtVerify(token, secret);
    return payload as UserPayload;
  } catch {
    return null;
  }
}
```

### Handle Hook（含 Token Refresh）

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { verifyToken, createToken } from '$lib/server/auth';

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get('auth_token');

  if (token) {
    const payload = await verifyToken(token);

    if (payload) {
      event.locals.user = {
        id: payload.sub!,
        email: payload.email,
        role: payload.role
      };

      // Token refresh: 剩餘 15 分鐘內時自動刷新
      const exp = payload.exp ?? 0;
      const now = Math.floor(Date.now() / 1000);
      if (exp - now < 15 * 60) {
        const newToken = await createToken({
          id: payload.sub!,
          email: payload.email,
          role: payload.role
        });
        event.cookies.set('auth_token', newToken, {
          path: '/',
          httpOnly: true,
          secure: true,
          sameSite: 'lax',
          maxAge: 60 * 60
        });
      }
    } else {
      event.cookies.delete('auth_token', { path: '/' });
    }
  }

  return resolve(event);
};
```

### Auth Guard Layout

```ts
// src/routes/(auth)/+layout.server.ts
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals, url }) => {
  if (!locals.user) {
    const redirectTo = encodeURIComponent(url.pathname + url.search);
    redirect(303, `/login?redirect=${redirectTo}`);
  }

  return { user: locals.user };
};
```

### Admin RBAC Layout

```ts
// src/routes/(auth)/admin/+layout.server.ts
import { error } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  if (locals.user?.role !== 'admin') {
    error(403, {
      message: 'Forbidden: You need admin privileges to access this page.'
    });
  }
};
```

### Dashboard 頁面

```svelte
<!-- src/routes/(auth)/dashboard/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
</script>

<h1>Dashboard</h1>
<p>Welcome, {data.user.email}!</p>
<p>Your role: <strong>{data.user.role}</strong></p>

{#if data.user.role === 'admin'}
  <section>
    <h2>Admin Quick Actions</h2>
    <a href="/admin">Go to Admin Panel</a>
  </section>
{/if}
```

## Common Pitfalls

1. **將 JWT 存放在 localStorage 而非 HttpOnly Cookie**
   `localStorage` 中的值可以被任何 JavaScript 讀取，包括 XSS 攻擊注入的腳本。HttpOnly Cookie 無法被 JavaScript 存取，大幅降低 token 被竊取的風險。

   ```ts
   // Bad: 存在 localStorage
   // localStorage.setItem('token', jwt);
   // fetch('/api', { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });

   // Good: 存在 HttpOnly Cookie（由 server 設定）
   cookies.set('auth_token', jwt, {
     path: '/',
     httpOnly: true,   // JavaScript 無法存取
     secure: true,      // 僅 HTTPS
     sameSite: 'lax'    // 基本 CSRF 防護
   });
   ```

2. **Cookie 未設定 HttpOnly 和 Secure 屬性**
   即使使用 cookie 存放 token，如果沒有設定 `httpOnly: true`，JavaScript 仍然可以透過 `document.cookie` 讀取。`secure: true` 確保 cookie 只在 HTTPS 連線中傳送。

   ```ts
   // Bad: 缺少安全屬性
   cookies.set('auth_token', jwt, { path: '/' });

   // Good: 完整安全屬性
   cookies.set('auth_token', jwt, {
     path: '/',
     httpOnly: true,
     secure: true,
     sameSite: 'lax',
     maxAge: 60 * 60
   });
   ```

3. **未在伺服器端驗證認證（僅靠客戶端檢查）**
   客戶端的認證檢查（如檢查 cookie 是否存在）可以被繞過。所有認證驗證必須在伺服器端（`+page.server.ts`、`+layout.server.ts`、hooks）進行。

   ```svelte
   <!-- Bad: 僅客戶端檢查 -->
   <script lang="ts">
     import { goto } from '$app/navigation';
     import { onMount } from 'svelte';
     onMount(() => {
       if (!document.cookie.includes('auth_token')) goto('/login');
     });
   </script>

   <!-- Good: 伺服器端檢查（在 +layout.server.ts 中） -->
   ```

   ```ts
   // +layout.server.ts
   export const load: LayoutServerLoad = async ({ locals }) => {
     if (!locals.user) redirect(303, '/login');
     return { user: locals.user };
   };
   ```

4. **缺少 CSRF 防護**
   雖然 `sameSite: 'lax'` 提供基本的 CSRF 防護，但對於敏感操作（如修改密碼、刪除帳號）建議加入額外的 CSRF token。SvelteKit 的 form actions 內建 CSRF 防護，但自訂 API endpoint 需要自行處理。

5. **在程式碼中硬編碼密鑰**
   JWT 密鑰、OAuth client secret 等敏感資訊絕對不能寫死在程式碼中。應使用環境變數，透過 SvelteKit 的 `$env/static/private` 載入。

   ```ts
   // Bad: 硬編碼密鑰
   // const secret = new TextEncoder().encode('my-super-secret');

   // Good: 使用環境變數
   import { JWT_SECRET } from '$env/static/private';
   const secret = new TextEncoder().encode(JWT_SECRET);
   ```

## Checklist

- [ ] 能使用 jose 函式庫簽發和驗證 JWT
- [ ] 能建立 Login API endpoint 並將 JWT 存入 HttpOnly Cookie
- [ ] 能實作 handle hook 在每次請求時自動驗證 JWT
- [ ] 能使用 route group 和 layout load 建立受保護路由
- [ ] 能實作 RBAC（角色權限控制），限制特定角色存取特定路由
- [ ] 能實作 OAuth 登入流程（GitHub/Google）
- [ ] 能實作 Token Refresh 和安全登出機制

## Further Reading

- [SvelteKit Hooks Documentation](https://svelte.dev/docs/kit/hooks)
- [SvelteKit Cookies API](https://svelte.dev/docs/kit/@sveltejs-kit#Cookies)
- [jose Library Documentation](https://github.com/panva/jose)
- [arctic OAuth Library](https://github.com/pilcrowonpaper/arctic)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [SvelteKit Form Actions](https://svelte.dev/docs/kit/form-actions)
- [MDN: HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
