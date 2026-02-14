---
title: "SvelteKit Project Bootstrap / SvelteKit 專案建置與路由"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "10"
level: beginner
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [09_styling_transitions_and_animations]
---
# SvelteKit Project Bootstrap / SvelteKit 專案建置與路由

## Goal

完整理解 SvelteKit 專案結構與檔案路由系統，能從零建立並導航一個多頁應用。

SvelteKit 是 Svelte 的官方全端框架，其檔案路由（file-based routing）系統以直覺的目錄結構取代手動路由配置，大幅降低專案的配置成本。本章是從「元件開發」邁向「全端應用開發」的關鍵轉折點，所學內容將作為後續 data loading、form actions 與 SSR 等章節的基礎。

- **銜接上一章**：Ch09 完成了 Svelte 元件層面的學習（樣式、過渡與動畫），現在進入 SvelteKit 框架層。
- **下一章預告**：Ch11 將學習資料載入函式（`load`）與伺服器端函式。

## Prerequisites

- 已完成第 09 章（Styling, Transitions and Animations）。
- 熟悉 Svelte 5 元件基礎：`$state`、`$derived`、`$props`、`$effect`（Ch02–Ch06）。
- 理解 Svelte 元件的 props、events、slots / snippets 機制（Ch07–Ch08）。
- 具備基本的 HTTP 與 REST API 概念。

## Core Concepts

### 1. SvelteKit project structure — 專案目錄結構

SvelteKit 專案遵循**約定優於配置**的原則，關鍵目錄與檔案各有明確職責：

```
my-app/
├── src/
│   ├── routes/          # 檔案路由系統（每個資料夾/檔案對應一個 URL）
│   ├── lib/             # 共用程式碼（元件、工具函式、型別）
│   │   └── components/  # 共用元件
│   ├── app.html         # HTML shell template（%sveltekit.head%, %sveltekit.body%）
│   └── app.d.ts         # 型別宣告（App namespace）
├── static/              # 靜態資源（favicon、圖片、robots.txt）
├── svelte.config.js     # SvelteKit 配置（adapter、preprocess 等）
├── vite.config.ts       # Vite 建構工具配置
├── tsconfig.json        # TypeScript 配置
└── package.json
```

#### `src/routes/` — file-based routing

SvelteKit 的核心特色之一。資料夾結構直接對應 URL 路徑：

- `src/routes/+page.svelte` → `/`
- `src/routes/about/+page.svelte` → `/about`
- `src/routes/blog/[slug]/+page.svelte` → `/blog/hello-world`

#### `src/lib/` — shared code (alias `$lib`)

存放可重複使用的程式碼。SvelteKit 提供 `$lib` 別名，讓匯入路徑簡潔且不受目錄層級影響：

```ts
// 不需要 '../../../lib/components/Nav.svelte'
import Nav from '$lib/components/Nav.svelte';
```

#### `src/app.html` — HTML shell template

整個應用的 HTML 外殼，SvelteKit 會在 `%sveltekit.head%` 注入 `<head>` 內容，在 `%sveltekit.body%` 注入頁面渲染結果：

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    %sveltekit.head%
  </head>
  <body>
    <div style="display: contents">%sveltekit.body%</div>
  </body>
</html>
```

#### `svelte.config.js` / `vite.config.ts`

- `svelte.config.js`：SvelteKit 層級的配置，包含 adapter（部署目標）、preprocess（如 SCSS）、路由設定等。
- `vite.config.ts`：底層建構工具 Vite 的配置，可加入 Vite 外掛、調整 dev server 等。

#### `static/` — static assets

此目錄的檔案會直接複製到建構輸出的根目錄，適合放 favicon、`robots.txt`、不需處理的圖片等。

| 何時把程式碼放 `src/lib/` | 何時放 `src/routes/` |
|---|---|
| 可重複使用的元件、工具函式、型別定義 | 與特定頁面綁定的頁面元件（`+page.svelte`） |
| 不直接對應 URL 的共用邏輯 | 需要成為 URL 路徑的內容 |
| 需要透過 `$lib` 別名在多處匯入 | 頁面專屬的 load function、layout、error page |
| 商業邏輯、API client、常數定義 | API endpoints（`+server.ts`） |

### 2. File conventions in routes — 路由檔案命名約定

SvelteKit 使用 `+` 前綴來識別具有特殊意義的路由檔案。每個檔案都有明確的用途：

#### `+page.svelte` — page component

每個路由的頁面元件。收到導航請求時，SvelteKit 會渲染對應的 `+page.svelte`：

```svelte
<!-- src/routes/about/+page.svelte -->
<h1>About Us</h1>
<p>This is the about page.</p>
```

#### `+layout.svelte` — shared layout

包裹巢狀路由的共用佈局。使用 `{@render children()}` 渲染子頁面內容：

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  let { children } = $props();
</script>

<nav>
  <a href="/">Home</a>
  <a href="/about">About</a>
</nav>
<main>
  {@render children()}
</main>
<footer>My App &copy; 2026</footer>
```

Layout 是巢狀的：`src/routes/+layout.svelte` 是根 layout，`src/routes/dashboard/+layout.svelte` 會被包在根 layout 裡面。

#### `+error.svelte` — error page

當 load function 拋出錯誤或頁面不存在時，SvelteKit 會渲染最近的 `+error.svelte`：

```svelte
<!-- src/routes/+error.svelte -->
<script lang="ts">
  import { page } from '$app/stores';
</script>

<h1>{$page.status} Error</h1>
<p>{$page.error?.message}</p>
```

#### `+page.ts` — universal load function

在 client 與 server 端都會執行的資料載入函式。適合不涉及機密的資料擷取：

```ts
// src/routes/blog/+page.ts
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const res = await fetch('/api/posts');
  const posts = await res.json();
  return { posts };
};
```

#### `+page.server.ts` — server-only load function

只在伺服器端執行的資料載入函式。適合存取資料庫、使用 API secrets 等：

```ts
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';
import { db } from '$lib/server/database';

export const load: PageServerLoad = async ({ locals }) => {
  const user = await db.getUser(locals.userId);
  return { user };
};
```

#### `+layout.ts` / `+layout.server.ts` — layout data loading

與 `+page.ts` / `+page.server.ts` 相同概念，但資料會提供給 layout 及其所有子頁面。

#### `+server.ts` — API endpoint

建立 RESTful API endpoint，匯出 HTTP method 對應的 handler（`GET`、`POST`、`PUT`、`DELETE` 等）：

```ts
// src/routes/api/health/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => {
  return json({ status: 'ok', timestamp: new Date().toISOString() });
};
```

| 何時用 `+page.ts`（universal loader） | 何時用 `+page.server.ts`（server-only loader） |
|---|---|
| 資料來源是公開 API，不含機密 | 需要存取資料庫、環境變數、API secrets |
| 需要在 client-side navigation 時直接在瀏覽器端載入資料 | 資料處理邏輯不應暴露給前端 |
| 不涉及伺服器專屬的模組（如 `fs`、`db`） | 需要讀寫 cookies 或 session |
| 希望減少 server round-trip（client 直接 fetch） | 回傳的資料需要在傳送前過濾敏感欄位 |

### 3. Route parameters — 路由參數

SvelteKit 提供多種路由參數機制，滿足不同的 URL 模式需求：

#### `[param]` — required dynamic param

方括號定義動態路由段。URL 中的該段會被捕獲為參數：

```
src/routes/blog/[slug]/+page.svelte
→ /blog/hello-world  ⇒ params.slug = 'hello-world'
→ /blog/my-post      ⇒ params.slug = 'my-post'
→ /blog/             ⇒ 404（slug 是必要的）
```

#### `[...rest]` — catch-all / rest params

三個點表示「捕獲剩餘所有路由段」，值會以 `/` 分隔的字串形式取得：

```
src/routes/docs/[...path]/+page.svelte
→ /docs/getting-started          ⇒ params.path = 'getting-started'
→ /docs/guide/routing/basics     ⇒ params.path = 'guide/routing/basics'
→ /docs/                         ⇒ params.path = ''（空字串）
```

#### `[ [optional] ]` — optional param

雙層方括號表示可選參數。無論有無該段，路由都會匹配：

```
src/routes/blog/[ [page] ]/+page.svelte
→ /blog       ⇒ params.page = undefined
→ /blog/2     ⇒ params.page = '2'
```

#### `(group)` — route group

小括號定義路由群組。群組名稱**不會**出現在 URL 中，但可以共用 layout：

```
src/routes/(marketing)/pricing/+page.svelte   → /pricing
src/routes/(marketing)/features/+page.svelte  → /features
src/routes/(marketing)/+layout.svelte         → 只套用在 marketing 群組
```

| 何時用 route groups | 何時用 nested layouts |
|---|---|
| 需要為不同頁面套用不同 layout，但 URL 不需要額外層級 | URL 結構本身就需要巢狀層級（如 `/dashboard/settings`） |
| 行銷頁面 vs 應用頁面需要完全不同的佈局 | 子頁面在邏輯上屬於父頁面的一部分 |
| 不同區域的 auth 需求不同 | 子頁面需要共用父頁面的 UI 元素（如 sidebar） |

### 4. Navigation and `$lib` alias — 導航與 `$lib` 別名

#### `<a href="/about">` — client-side navigation

SvelteKit 會自動攔截 `<a>` 標籤的點擊事件，改用 client-side navigation，避免完整頁面重新載入。這是 SvelteKit 的預設行為，不需要特殊元件（不像 React Router 的 `<Link>`）：

```svelte
<nav>
  <a href="/">Home</a>
  <a href="/about">About</a>
  <a href="/blog">Blog</a>
</nav>
```

若需要強制完整頁面載入（例如外部連結或非 SvelteKit 頁面），加上 `data-sveltekit-reload` 屬性：

```svelte
<a href="/legacy-page" data-sveltekit-reload>Legacy Page</a>
```

#### `goto()` — programmatic navigation

從 `$app/navigation` 匯入的函式，用於程式碼內的導航（如表單提交後跳轉）：

```svelte
<script lang="ts">
  import { goto } from '$app/navigation';

  async function handleLogin() {
    const success = await login();
    if (success) {
      await goto('/dashboard');
    }
  }
</script>
```

`goto()` 接受第二個參數來控制導航行為：

```ts
goto('/dashboard', { replaceState: true }); // 取代歷史記錄（不可返回）
goto('/dashboard', { invalidateAll: true }); // 重新執行所有 load function
```

#### `$lib` alias

SvelteKit 自動配置的路徑別名，指向 `src/lib/`。無論在任何深度的路由檔案中，都可以用 `$lib` 匯入共用程式碼：

```ts
// 在 src/routes/blog/[slug]/+page.svelte 中
import Nav from '$lib/components/Nav.svelte';
import { formatDate } from '$lib/utils/date';
import type { Post } from '$lib/types';
```

#### `$app/stores`: `page`, `navigating`, `updated`

SvelteKit 提供的 app-level stores，可在任何元件中存取：

```svelte
<script lang="ts">
  import { page, navigating, updated } from '$app/stores';
</script>

<!-- $page：當前頁面資訊（url, params, status, error, data） -->
<p>Current path: {$page.url.pathname}</p>
<p>Route params: {JSON.stringify($page.params)}</p>

<!-- $navigating：導航進行中時為 truthy，可用來顯示 loading indicator -->
{#if $navigating}
  <div class="loading-bar">Loading...</div>
{/if}

<!-- $updated：當新版應用部署後為 true，可提示使用者重新整理 -->
{#if $updated}
  <p>A new version is available. <a href={$page.url.href}>Refresh</a></p>
{/if}
```

| 何時用 `<a>` 標籤 | 何時用 `goto()` |
|---|---|
| 使用者主動點擊的導航連結 | 程式邏輯觸發的導航（表單提交後、條件跳轉） |
| 需要 SEO（搜尋引擎可索引的連結） | 動態決定目標 URL |
| 需要 progressive enhancement | 需要傳遞 `replaceState` 等導航選項 |

## Step-by-step

### Step 1：建立新的 SvelteKit 專案

使用 `sv`（Svelte CLI）建立一個最小化的 SvelteKit 專案：

```bash
npx sv create sveltekit-app --template minimal --types ts
cd sveltekit-app
npm install
```

這會生成包含 `src/routes/+page.svelte`、`src/app.html`、`svelte.config.js`、`vite.config.ts` 等基本檔案的專案。

### Step 2：探索生成的專案結構

執行 `npm run dev` 啟動開發伺服器，然後瀏覽專案資料夾：

```
sveltekit-app/
├── src/
│   ├── routes/
│   │   └── +page.svelte     # 首頁（對應 /）
│   ├── app.html              # HTML shell
│   └── app.d.ts              # 型別宣告
├── static/
│   └── favicon.png
├── svelte.config.js
├── vite.config.ts
├── tsconfig.json
└── package.json
```

在瀏覽器打開 `http://localhost:5173`，確認首頁正常渲染。

### Step 3：建立靜態 About 頁面

建立 `src/routes/about/+page.svelte`：

```svelte
<!-- src/routes/about/+page.svelte -->
<svelte:head>
  <title>About</title>
</svelte:head>

<h1>About</h1>
<p>這是關於我們的頁面。SvelteKit 根據資料夾結構自動建立 /about 路由。</p>
```

存檔後瀏覽 `http://localhost:5173/about`，頁面應該立即可見。

### Step 4：建立根 Layout 加入導航列

建立 `src/routes/+layout.svelte`，使用 `{@render children()}` 渲染子頁面：

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import Nav from '$lib/components/Nav.svelte';
  let { children } = $props();
</script>

<Nav />
<main>
  {@render children()}
</main>
<footer>
  <p>SvelteKit Demo &copy; 2026</p>
</footer>

<style>
  main {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
  }
</style>
```

> 注意：此步驟需要先完成 Step 9 建立 `Nav.svelte`，或先用 inline nav 替代。

### Step 5：建立動態路由頁面

建立 `src/routes/blog/[slug]/+page.svelte`，使用動態路由參數：

```svelte
<!-- src/routes/blog/[slug]/+page.svelte -->
<script lang="ts">
  import { page } from '$app/stores';
</script>

<svelte:head>
  <title>Blog - {$page.params.slug}</title>
</svelte:head>

<h1>Blog Post: {$page.params.slug}</h1>
<p>這個頁面的 slug 參數是：<code>{$page.params.slug}</code></p>
<p><a href="/blog">← Back to blog</a></p>
```

瀏覽 `http://localhost:5173/blog/hello-world`，頁面會顯示 slug 為 `hello-world`。

### Step 6：透過 load function 存取路由參數

在 Step 5 我們用 `$page.params` 讀取參數。另一種更結構化的方式是透過 load function：

```ts
// src/routes/blog/[slug]/+page.ts
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
  return {
    slug: params.slug,
    title: params.slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
  };
};
```

```svelte
<!-- src/routes/blog/[slug]/+page.svelte（使用 load function 版本） -->
<script lang="ts">
  let { data } = $props();
</script>

<h1>{data.title}</h1>
<p>Slug: <code>{data.slug}</code></p>
```

load function 的資料會透過 `data` prop 自動傳遞給 `+page.svelte`。

### Step 7：建立 route group 頁面

建立 `src/routes/(marketing)/pricing/+page.svelte`——小括號中的 `(marketing)` 不會出現在 URL 中：

```svelte
<!-- src/routes/(marketing)/pricing/+page.svelte -->
<svelte:head>
  <title>Pricing</title>
</svelte:head>

<h1>Pricing</h1>
<p>此頁面的 URL 是 /pricing，不是 /marketing/pricing。</p>
<p>route group 讓我們可以為一組頁面共用 layout，而不影響 URL 結構。</p>
```

可為 marketing 群組建立專屬 layout：

```svelte
<!-- src/routes/(marketing)/+layout.svelte -->
<script lang="ts">
  let { children } = $props();
</script>

<div class="marketing-layout">
  <header>Marketing Section</header>
  {@render children()}
</div>
```

瀏覽 `http://localhost:5173/pricing` 確認頁面正常渲染。

### Step 8：建立 API endpoint

建立 `src/routes/api/health/+server.ts`：

```ts
// src/routes/api/health/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => {
  return json({
    status: 'ok',
    timestamp: new Date().toISOString(),
  });
};
```

瀏覽 `http://localhost:5173/api/health` 或使用 `curl`：

```bash
curl http://localhost:5173/api/health
# {"status":"ok","timestamp":"2026-02-14T..."}
```

### Step 9：建立共用 Nav 元件並使用 `$lib` 別名

建立 `src/lib/components/Nav.svelte`：

```svelte
<!-- src/lib/components/Nav.svelte -->
<script lang="ts">
  import { page } from '$app/stores';

  const links = [
    { href: '/', label: 'Home' },
    { href: '/about', label: 'About' },
    { href: '/blog', label: 'Blog' },
    { href: '/pricing', label: 'Pricing' },
    { href: '/dashboard', label: 'Dashboard' },
  ];
</script>

<nav>
  {#each links as { href, label }}
    <a {href} class:active={$page.url.pathname === href}>
      {label}
    </a>
  {/each}
</nav>

<style>
  nav {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #e2e8f0;
  }

  a {
    text-decoration: none;
    color: #64748b;
  }

  a.active {
    color: #0f172a;
    font-weight: bold;
  }
</style>
```

在任何路由檔案中，使用 `$lib` 別名匯入：

```ts
import Nav from '$lib/components/Nav.svelte';
```

### Step 10：測試導航行為

驗證以下導航行為：

1. **連結導航**：點擊 nav 中的連結，觀察頁面內容切換但**不會整頁重新載入**（SvelteKit client-side navigation）。

2. **瀏覽器前進/後退**：使用瀏覽器的上一頁/下一頁按鈕，確認導航正常運作。

3. **程式化導航**：在某個頁面中加入 `goto()` 測試：

```svelte
<!-- src/routes/+page.svelte -->
<script lang="ts">
  import { goto } from '$app/navigation';
</script>

<h1>Home</h1>
<button onclick={() => goto('/about')}>Go to About</button>
<button onclick={() => goto('/blog/my-first-post')}>Read Blog Post</button>
```

4. **導航狀態**：觀察 `$navigating` store 在導航時是否為 truthy，確認 loading indicator 運作正常。

## Hands-on Lab

### Foundation：建立 3 頁應用

建立一個包含 Home、About、Contact 三個頁面的 SvelteKit 應用：

- 建立 `src/routes/+page.svelte`（Home）、`src/routes/about/+page.svelte`、`src/routes/contact/+page.svelte`。
- 建立 `src/routes/+layout.svelte`，包含導航列與 `{@render children()}`。
- 每個頁面使用 `<svelte:head>` 設定頁面標題。

**驗收標準**：
- [ ] 三個頁面都可透過導航列切換。
- [ ] 導航不觸發整頁重新載入。
- [ ] 每個頁面的 `<title>` 正確顯示。

### Advanced：動態路由與 route group

在 Foundation 基礎上擴充：

- 建立 `/blog` 頁面列出幾篇假文章的連結。
- 建立 `/blog/[slug]` 動態路由，顯示對應的 slug。
- 建立 `(marketing)` route group，包含 `/pricing` 和 `/features` 頁面，使用獨立的 marketing layout。

**驗收標準**：
- [ ] `/blog/hello-world` 正確顯示 slug 參數。
- [ ] `/pricing` URL 中不包含 `marketing`。
- [ ] marketing 頁面使用與其他頁面不同的 layout。

### Challenge：Dashboard 巢狀 layout + API endpoint

在 Advanced 基礎上擴充：

- 建立 `/dashboard` 路由，含獨立的 `+layout.svelte`（sidebar 導航）。
- 建立 `/dashboard/settings` 子頁面，繼承 dashboard layout。
- 建立 `/api/health` API endpoint，回傳 JSON `{ status: 'ok', timestamp: '...' }`。
- 在 dashboard 頁面使用 `onMount` 呼叫 `/api/health` 並顯示結果。

**驗收標準**：
- [ ] `/dashboard` 和 `/dashboard/settings` 都有 sidebar 導航。
- [ ] sidebar 正確標示當前頁面（active state）。
- [ ] `curl http://localhost:5173/api/health` 回傳正確 JSON。
- [ ] dashboard 頁面成功顯示 health check 結果。

## Reference Solution

### 專案目錄結構

```
src/routes/
├── +layout.svelte          # Root layout with nav
├── +page.svelte            # Home page
├── about/
│   └── +page.svelte        # About page
├── contact/
│   └── +page.svelte        # Contact page
├── blog/
│   ├── +page.svelte        # Blog index
│   └── [slug]/
│       ├── +page.ts        # Blog post load function
│       └── +page.svelte    # Blog post (dynamic)
├── (marketing)/
│   ├── +layout.svelte      # Marketing layout
│   ├── pricing/
│   │   └── +page.svelte    # Pricing (marketing group)
│   └── features/
│       └── +page.svelte    # Features (marketing group)
├── dashboard/
│   ├── +layout.svelte      # Dashboard layout with sidebar
│   ├── +page.svelte        # Dashboard home
│   └── settings/
│       └── +page.svelte    # Dashboard settings
└── api/
    └── health/
        └── +server.ts      # Health check endpoint

src/lib/
└── components/
    └── Nav.svelte          # Shared navigation component
```

### Root Layout

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import Nav from '$lib/components/Nav.svelte';
  let { children } = $props();
</script>

<Nav />
<main>
  {@render children()}
</main>
```

### Shared Nav Component

```svelte
<!-- src/lib/components/Nav.svelte -->
<script lang="ts">
  import { page } from '$app/stores';

  const links = [
    { href: '/', label: 'Home' },
    { href: '/about', label: 'About' },
    { href: '/blog', label: 'Blog' },
    { href: '/pricing', label: 'Pricing' },
    { href: '/dashboard', label: 'Dashboard' },
  ];
</script>

<nav>
  {#each links as { href, label }}
    <a {href} class:active={$page.url.pathname === href}>
      {label}
    </a>
  {/each}
</nav>
```

### Blog Dynamic Route

```svelte
<!-- src/routes/blog/[slug]/+page.svelte -->
<script lang="ts">
  import { page } from '$app/stores';
</script>

<svelte:head>
  <title>Blog - {$page.params.slug}</title>
</svelte:head>

<h1>Blog Post: {$page.params.slug}</h1>
<p><a href="/blog">&larr; Back to blog</a></p>
```

### Dashboard Layout with Sidebar

```svelte
<!-- src/routes/dashboard/+layout.svelte -->
<script lang="ts">
  import { page } from '$app/stores';
  let { children } = $props();

  const sidebarLinks = [
    { href: '/dashboard', label: 'Overview' },
    { href: '/dashboard/settings', label: 'Settings' },
  ];
</script>

<div class="dashboard">
  <aside>
    <h2>Dashboard</h2>
    <nav>
      {#each sidebarLinks as { href, label }}
        <a {href} class:active={$page.url.pathname === href}>
          {label}
        </a>
      {/each}
    </nav>
  </aside>
  <section>
    {@render children()}
  </section>
</div>

<style>
  .dashboard {
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 1rem;
  }

  aside {
    padding: 1rem;
    border-right: 1px solid #e2e8f0;
  }

  aside nav {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  a.active {
    font-weight: bold;
  }
</style>
```

### API Endpoint

```ts
// src/routes/api/health/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async () => {
  return json({
    status: 'ok',
    timestamp: new Date().toISOString(),
  });
};
```

### Dashboard Page (calling the API)

```svelte
<!-- src/routes/dashboard/+page.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';

  interface HealthCheck {
    status: string;
    timestamp: string;
  }

  let health = $state<HealthCheck | null>(null);

  onMount(async () => {
    const res = await fetch('/api/health');
    health = await res.json();
  });
</script>

<svelte:head>
  <title>Dashboard</title>
</svelte:head>

<h1>Dashboard</h1>

{#if health}
  <p>API Status: {health.status}</p>
  <p>Timestamp: {health.timestamp}</p>
{:else}
  <p>Loading health check...</p>
{/if}
```

## Common Pitfalls

### 1. 忘記 `+` 前綴：`page.svelte` 不會被識別為路由

SvelteKit 只識別以 `+` 開頭的檔案作為路由檔案。沒有 `+` 前綴的檔案會被忽略：

```
src/routes/about/page.svelte     ← 錯誤：不會產生路由
src/routes/about/+page.svelte    ← 正確：產生 /about 路由
```

### 2. 把共用元件放在 `src/routes/` 而非 `src/lib/`

`src/routes/` 下的檔案有特殊意義。若把一般元件放在 `src/routes/` 中，可能造成意料之外的行為。共用元件、工具函式、型別定義應放在 `src/lib/`：

```
src/routes/Nav.svelte           ← 錯誤：會被當作路由相關檔案
src/lib/components/Nav.svelte   ← 正確：使用 $lib 別名匯入
```

### 3. Layout 中使用 `<slot>` 而非 `{@render children()}`（Svelte 5）

Svelte 5 以 snippets 取代了 slots。Layout 中必須使用 `{@render children()}` 來渲染子頁面內容：

```svelte
<!-- 錯誤：Svelte 4 語法 -->
<nav>...</nav>
<slot />

<!-- 正確：Svelte 5 語法 -->
<script lang="ts">
  let { children } = $props();
</script>
<nav>...</nav>
{@render children()}
```

### 4. 混淆 `[param]`（必要）與 `[ [param] ]`（可選）

`[param]` 是必要的動態段，URL 中必須包含該段才會匹配。`[ [param] ]` 是可選的，有無都會匹配：

```
src/routes/blog/[slug]/+page.svelte
→ /blog/hello   ✓ (params.slug = 'hello')
→ /blog/        ✗ 404

src/routes/blog/[ [slug] ]/+page.svelte
→ /blog/hello   ✓ (params.slug = 'hello')
→ /blog/        ✓ (params.slug = undefined)
```

### 5. 不理解 `(group)` 資料夾不產生 URL 段

Route group 使用小括號命名，**不會**成為 URL 的一部分。這是常見的誤解：

```
src/routes/(marketing)/pricing/+page.svelte
→ URL 是 /pricing     ✓
→ URL 不是 /marketing/pricing
```

Route group 的目的是讓一組不相鄰的頁面共用 layout，而不增加 URL 層級。

### 6. 在 `+server.ts` 中忘記回傳 `Response` 物件

API endpoint 的 handler 必須回傳 `Response` 物件。使用 SvelteKit 提供的 `json()` helper 最為方便：

```ts
// 錯誤：直接回傳物件
export const GET: RequestHandler = async () => {
  return { status: 'ok' }; // TypeError
};

// 正確：使用 json() helper
export const GET: RequestHandler = async () => {
  return json({ status: 'ok' });
};
```

## Checklist

- [ ] 能使用 `npx sv create` 從零建立 SvelteKit 專案
- [ ] 能說明每個 `+` 前綴檔案的用途（`+page.svelte`、`+layout.svelte`、`+error.svelte`、`+page.ts`、`+page.server.ts`、`+server.ts`）
- [ ] 能建立靜態路由、動態 `[param]` 路由、可選 `[ [param] ]` 路由、catch-all `[...rest]` 路由
- [ ] 能使用 `(group)` route group 為不同頁面套用不同 layout
- [ ] 能使用 `$lib` 別名匯入 `src/lib/` 下的共用程式碼
- [ ] 能建立 API endpoints（`+server.ts`）並回傳 JSON response
- [ ] 能使用 `+layout.svelte` 搭配 `{@render children()}` 建立共用佈局
- [ ] `npm run dev` 正常啟動，所有路由均可存取且導航正常運作

## Further Reading

- [SvelteKit Routing — Official Docs](https://svelte.dev/docs/kit/routing)
- [Project Structure — SvelteKit](https://svelte.dev/docs/kit/project-structure)
- [Loading Data — SvelteKit](https://svelte.dev/docs/kit/load)
- [API Routes (+server) — SvelteKit](https://svelte.dev/docs/kit/routing#server)
- [$app/navigation — SvelteKit](https://svelte.dev/docs/kit/$app-navigation)
- [$app/stores — SvelteKit](https://svelte.dev/docs/kit/$app-stores)
- [Advanced Routing — SvelteKit](https://svelte.dev/docs/kit/advanced-routing)
