---
title: "SSR, Streaming, and Page Options / SSR、串流與頁面選項"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "13"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [12_form_actions_and_data_mutations]
---
# SSR, Streaming, and Page Options / SSR、串流與頁面選項

## Goal

理解 SvelteKit 的渲染策略選項，學會控制 SSR、CSR、prerender，以及使用 streaming 提升載入體驗。

SvelteKit 的強大之處在於讓開發者可以逐頁選擇最適合的渲染策略，而非整個應用使用單一模式。透過本章學習 `ssr`、`csr`、`prerender` 三個 page option 的組合方式，以及 streaming deferred promises 的技巧，你將能針對 SEO、效能與使用者體驗做出最佳化的渲染決策。

- 銜接上一章：Ch12 學會了 form actions 處理資料變更，現在要理解頁面如何被渲染。
- 下一章預告：Ch14 將學習進階路由與 hooks 中間件。

## Prerequisites

- 已完成 Ch12（Form Actions and Data Mutations），理解 load function 與 form actions 的資料流。
- 能建立 `+page.server.ts` 中的 `load` 函式並在 `+page.svelte` 中使用 `data` prop。
- `svelte5-lab` 專案可正常執行 `npm run dev`。

## Core Concepts

### 1. Page options: `ssr`, `csr`, `prerender` — 頁面渲染策略

SvelteKit 讓你在每個頁面或 layout 層級控制渲染策略。透過在 `+page.ts`（或 `+page.server.ts`）和 `+layout.ts`（或 `+layout.server.ts`）中匯出常數來設定。

- `export const ssr = true/false`：控制是否在 server 端渲染 HTML。設為 `false` 時，server 只送出空殼 HTML，由 client 端 JavaScript 負責渲染。
- `export const csr = true/false`：控制是否在 client 端 hydrate（注入互動性）。設為 `false` 時，頁面為純靜態 HTML，不會載入任何 client-side JavaScript。
- `export const prerender = true/false`：在 `build` 時生成靜態 HTML 檔案。適合內容不隨請求變化的頁面。

**組合使用場景：**

| 模式 | `ssr` | `csr` | 行為 | 適用場景 |
|------|-------|-------|------|----------|
| SSR + CSR（預設） | `true` | `true` | 首次由 server 渲染 HTML，client 接手 hydrate 後續導航 | 大多數頁面 |
| SSR only | `true` | `false` | 僅 server 渲染，不載入 client JS | 靜態內容頁、不需互動 |
| CSR only | `false` | `true` | 不在 server 渲染，完全由 client 建構 | Dashboard、依賴 browser API |
| Prerender | `true` | `true` | build 時產出靜態 HTML，部署後不需 server | About、Blog、Landing page |

- **何時用 SSR + CSR（預設）**：絕大多數頁面的最佳選擇，兼顧 SEO 與互動性。
- **何時用 SSR only（`csr = false`）**：純展示內容、不需任何 client-side 互動的頁面，可減少 JS bundle size。
- **何時用 CSR only（`ssr = false`）**：需要 `window`、`document` 等 browser API 的頁面（如 canvas 繪圖、地圖元件），或不需要 SEO 的後台管理頁面。
- **何時用 Prerender**：內容在 build 時就能確定、不依賴 request-time 資料的頁面，如 about、blog posts、文件頁。
- **何時不用 Prerender**：頁面依賴 cookies、headers、URL search params 等 request-time 資訊。

### 2. Streaming via deferred promises in load — 串流延遲載入

在 `load` 函式中回傳 Promise（不 `await`），SvelteKit 會先將已解析的資料送出並渲染頁面，待 Promise resolve 後再透過 HTTP streaming 將結果補充到頁面上。

```ts
// 傳統做法：所有資料都 await，載入最慢的資料阻擋整個頁面
export const load = async () => {
  const fast = await getFastData();   // 50ms
  const slow = await getSlowData();   // 3000ms — 整個頁面等 3 秒
  return { fast, slow };
};

// Streaming 做法：快資料先送，慢資料串流補上
export const load = async () => {
  const fast = await getFastData();   // 50ms — 先送出
  const slow = getSlowData();         // 不 await，作為 Promise 回傳
  return { fast, slow };              // 頁面先顯示 fast，slow 稍後串流到達
};
```

在頁面中搭配 `{#await}` 區塊顯示 loading 狀態：

```svelte
{#await data.slow}
  <p>Loading...</p>
{:then result}
  <p>{result}</p>
{:catch error}
  <p>Error: {error.message}</p>
{/await}
```

- **何時用 streaming**：次要資料載入慢但不應阻擋主要內容的顯示。例如 dashboard 中的摘要統計（快）和詳細分析圖表（慢）。
- **何時不用**：所有資料都是關鍵內容、需要一起完整顯示時。例如表單的初始值——欄位不能只顯示一半。

### 3. `$app/environment`: `browser`, `building`, `dev` — 環境偵測

SvelteKit 提供三個從 `$app/environment` 匯入的常數，用於區分當前的執行環境。

```ts
import { browser, building, dev } from '$app/environment';
```

- **`browser`**（`boolean`）：是否在瀏覽器環境中執行。在 SSR 期間為 `false`，在 client 端為 `true`。用於防止在 SSR 中執行 browser-only code（如存取 `localStorage`、`window`）。
- **`building`**（`boolean`）：是否在 `vite build` 階段執行（prerender 時為 `true`）。可用於在 build 時執行特殊邏輯。
- **`dev`**（`boolean`）：是否在開發模式（`npm run dev`）。可用於在開發環境顯示除錯資訊。

**`browser` 判斷 vs `onMount` 的選擇：**

```ts
// 用 browser：import-time 判斷，適合條件匯入或全域副作用
import { browser } from '$app/environment';
if (browser) {
  // 這段在 module 載入時（client 端）立刻執行
  console.log('Running in browser');
}

// 用 onMount：元件掛載後才執行，適合 DOM 操作與元件生命週期相關的副作用
import { onMount } from 'svelte';
onMount(() => {
  // 這段在元件掛載到 DOM 後才執行
  const chart = new Chart(canvas);
  return () => chart.destroy(); // cleanup
});
```

- **何時用 `browser`**：在 module scope 或非元件程式碼中，需要判斷環境來決定行為（如 conditional import、初始化全域 SDK）。
- **何時用 `onMount`**：在元件內部，需要在 DOM 掛載後才執行的操作（如初始化第三方 DOM library、設定 IntersectionObserver）。

### 4. `trailingSlash` and `entries` — 路由配置

控制 URL 尾端斜線行為與 prerender 動態路由的參數。

```ts
// +layout.ts 或 +page.ts
export const trailingSlash = 'never'; // 'always' | 'never' | 'ignore'
```

- **`'never'`**（預設）：`/about/` 會重導向到 `/about`。
- **`'always'`**：`/about` 會重導向到 `/about/`。某些靜態主機（如 S3、某些 CDN）需要此設定來正確對應到 `index.html`。
- **`'ignore'`**：兩者都接受，不做重導向。

```ts
// src/routes/blog/[slug]/+page.ts
export const prerender = true;

// 告訴 SvelteKit 在 prerender 時要生成哪些動態路由
export function entries() {
  return [
    { slug: 'hello-world' },
    { slug: 'svelte-5-guide' },
    { slug: 'sveltekit-streaming' },
  ];
}
```

- **何時需要 `trailingSlash`**：使用 static adapter 部署到 S3、GitHub Pages 或特定 CDN 時，需要設為 `'always'` 以確保路由正確解析。
- **何時需要 `entries`**：prerender 動態路由（如 `[slug]`、`[id]`）時，SvelteKit 需要知道有哪些參數值要預先生成。若不指定，SvelteKit 只能 prerender 從其他已知頁面的連結中探索到的路由。

## Step-by-step

### Step 1：建立一個 prerender 的靜態頁面

在 `+page.ts` 中匯出 `prerender = true`，讓 SvelteKit 在 build 時產出靜態 HTML。

```ts
// src/routes/about/+page.ts
export const prerender = true;
```

```svelte
<!-- src/routes/about/+page.svelte -->
<h1>About Us</h1>
<p>This page is prerendered at build time.</p>
<p>It does not require a running server to serve.</p>
```

執行 `npm run build` 後，在 `.svelte-kit/output` 目錄下會產生對應的靜態 HTML 檔案。Prerendered 頁面不能使用 `cookies`、`request` 等 server-only 功能。

### Step 2：建立一個 CSR-only 的頁面

設定 `ssr = false`，讓頁面完全在 client 端渲染，適合使用 browser-only API 的頁面。

```ts
// src/routes/app/+page.ts
export const ssr = false; // Client-only rendering
```

```svelte
<!-- src/routes/app/+page.svelte -->
<script lang="ts">
  let width = $state(window.innerWidth);

  function handleResize() {
    width = window.innerWidth;
  }
</script>

<svelte:window onresize={handleResize} />

<h1>Client-Only App</h1>
<p>Window width: {width}px</p>
<p>This page is rendered entirely in the browser.</p>
```

因為 `ssr = false`，可以安全地在 `<script>` 頂層使用 `window`，因為此程式碼只會在 browser 中執行。

### Step 3：觀察預設 SSR + CSR 行為

預設模式下，SvelteKit 先在 server 端渲染 HTML，然後在 client 端 hydrate。

```svelte
<!-- src/routes/ch13/ssr-demo/+page.svelte -->
<script lang="ts">
  import { browser } from '$app/environment';

  let environment = $derived(browser ? 'client (hydrated)' : 'server');
</script>

<h1>SSR + CSR Demo</h1>
<p>Currently running on: {environment}</p>
<p>View source to see the server-rendered HTML, then watch it hydrate.</p>
```

在瀏覽器中「檢視頁面原始碼」會看到完整的 HTML（由 server 渲染），但頁面載入後 `environment` 會更新為 `'client (hydrated)'`，表示 hydration 已完成。

### Step 4：實作 streaming — 在 load 中回傳不 await 的 Promise

在 `+page.server.ts` 的 `load` 函式中，將慢速資料以 Promise（不 `await`）的形式回傳。

```ts
// src/routes/ch13/streaming/+page.server.ts
import type { PageServerLoad } from './$types';

async function getQuickData() {
  return { title: 'Dashboard', totalUsers: 1234 };
}

async function getSlowReport() {
  await new Promise(resolve => setTimeout(resolve, 2000));
  return {
    revenue: 45678,
    topProducts: ['Keyboard', 'Mouse', 'Monitor'],
    conversionRate: 3.2
  };
}

export const load: PageServerLoad = async () => {
  return {
    quick: await getQuickData(),     // 立即可用
    report: getSlowReport()          // 不 await — 將被 stream
  };
};
```

`quick` 使用 `await` 等待結果，因此會包含在初始 HTML 中。`report` 沒有 `await`，作為 Promise 回傳，SvelteKit 會在 Promise resolve 後串流結果到 client。

### Step 5：在頁面中用 `{#await}` 顯示 streaming 載入狀態

搭配 `{#await}` 區塊，為串流資料提供 loading、success、error 三種狀態的 UI。

```svelte
<!-- src/routes/ch13/streaming/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';
  let { data }: { data: PageData } = $props();
</script>

<h1>{data.quick.title}</h1>

<section>
  <h2>Quick Stats</h2>
  <p>Total Users: {data.quick.totalUsers}</p>
</section>

<section>
  <h2>Detailed Report</h2>
  {#await data.report}
    <div class="loading">
      <p>Loading detailed report...</p>
    </div>
  {:then report}
    <p>Revenue: ${report.revenue.toLocaleString()}</p>
    <p>Conversion Rate: {report.conversionRate}%</p>
    <h3>Top Products</h3>
    <ul>
      {#each report.topProducts as product}
        <li>{product}</li>
      {/each}
    </ul>
  {:catch error}
    <p class="error">Failed to load report: {error.message}</p>
  {/await}
</section>
```

使用者會先看到 Quick Stats（立刻顯示），然後在約 2 秒後看到 Detailed Report 的資料取代 loading 文字。

### Step 6：使用 `$app/environment` 條件性執行 browser-only 程式碼

利用 `browser` 常數在 module scope 判斷環境，避免 SSR 錯誤。

```svelte
<!-- src/routes/ch13/env-demo/+page.svelte -->
<script lang="ts">
  import { browser, building, dev } from '$app/environment';
  import { onMount } from 'svelte';

  // Module scope — 用 browser 判斷
  let savedTheme = browser ? localStorage.getItem('theme') ?? 'light' : 'light';

  let canvasEl: HTMLCanvasElement;

  // 元件掛載後 — 用 onMount
  onMount(() => {
    const ctx = canvasEl.getContext('2d');
    if (ctx) {
      ctx.fillStyle = 'steelblue';
      ctx.fillRect(10, 10, 100, 50);
    }
  });
</script>

<h1>Environment Demo</h1>
<p>browser: {browser}</p>
<p>building: {building}</p>
<p>dev: {dev}</p>
<p>Theme: {savedTheme}</p>

<canvas bind:this={canvasEl} width="200" height="100"></canvas>
```

`localStorage.getItem` 在 module scope 使用 `browser` 守衛，避免 SSR 時拋出 `localStorage is not defined` 錯誤。Canvas 操作則放在 `onMount` 中，因為需要等 DOM 元素掛載。

### Step 7：在 layout 中配置 `trailingSlash`

在 `+layout.ts` 中統一設定整個子路由樹的 trailing slash 行為。

```ts
// src/routes/+layout.ts
export const trailingSlash = 'never';
```

設定 `'never'` 後，訪問 `/about/` 會自動 301 重導向到 `/about`。如果你的靜態部署環境要求尾端斜線（如某些 CDN 的 directory index 行為），改為 `'always'`。

此設定也可在子 layout 中覆蓋：

```ts
// src/routes/docs/+layout.ts
// 僅 /docs 子路由使用 trailing slash
export const trailingSlash = 'always';
```

### Step 8：為動態路由設定 prerender entries

使用 `entries()` 函式告訴 SvelteKit 在 prerender 時要生成哪些動態路由頁面。

```ts
// src/routes/blog/[slug]/+page.ts
export const prerender = true;

export function entries() {
  return [
    { slug: 'hello-world' },
    { slug: 'getting-started-with-svelte-5' },
    { slug: 'understanding-ssr-and-streaming' },
  ];
}
```

```ts
// src/routes/blog/[slug]/+page.server.ts
import type { PageServerLoad } from './$types';

const posts: Record<string, { title: string; content: string }> = {
  'hello-world': {
    title: 'Hello World',
    content: 'Welcome to the blog!'
  },
  'getting-started-with-svelte-5': {
    title: 'Getting Started with Svelte 5',
    content: 'Svelte 5 introduces runes...'
  },
  'understanding-ssr-and-streaming': {
    title: 'Understanding SSR and Streaming',
    content: 'SvelteKit provides powerful rendering options...'
  },
};

export const load: PageServerLoad = async ({ params }) => {
  const post = posts[params.slug];
  if (!post) throw new Error('Post not found');
  return { post };
};
```

執行 `npm run build` 時，SvelteKit 會為 `entries()` 回傳的每一個 `{ slug }` 產出對應的靜態 HTML 檔案。在正式環境中，`entries()` 通常會從資料庫或 CMS API 取得所有 slug。

## Hands-on Lab

任務：運用頁面選項與 streaming，為不同場景選擇適當的渲染策略。

### Foundation 基礎層

建立 3 個頁面，各使用不同的渲染模式，並驗證其行為：

- **Page 1 — SSR + CSR（預設）**：建立 `/ch13/default` 頁面，不設定任何 page option。在 `<script>` 中使用 `$app/environment` 的 `browser` 顯示當前環境。用「檢視頁面原始碼」確認 HTML 有 server 渲染的內容。
- **Page 2 — Prerender**：建立 `/ch13/static` 頁面，設定 `export const prerender = true`。顯示一段靜態說明文字。執行 `npm run build`，確認 `.svelte-kit/output` 中生成了靜態檔案。
- **Page 3 — CSR only**：建立 `/ch13/client-only` 頁面，設定 `export const ssr = false`。在頁面中使用 `window.navigator.userAgent` 顯示瀏覽器資訊。確認「檢視頁面原始碼」中沒有該內容（因為 server 沒有渲染）。

### Advanced 進階層

實作一個 streaming dashboard，載入快速摘要資料與緩慢的詳細分析：

- 在 `+page.server.ts` 的 `load` 函式中：
  - `await` 取得快速的摘要資料（users count、orders count），模擬 100ms 延遲。
  - 不 `await` 取得慢速的詳細分析（revenue breakdown、top products、conversion funnel），模擬 3 秒延遲。
- 在 `+page.svelte` 中：
  - 摘要區塊立即顯示。
  - 詳細分析區塊使用 `{#await}` 顯示 skeleton loading 效果。
  - 加入 `{:catch}` 處理錯誤情況。
- 測試：開啟頁面後，摘要應在 100ms 內出現，詳細分析在約 3 秒後補上。

### Challenge 挑戰層

建立一個完整的 prerendered blog 系統，支援動態 `[slug]` 路由：

- 建立 `/blog` 列表頁面，prerender，顯示所有文章標題與連結。
- 建立 `/blog/[slug]` 文章頁面，prerender，使用 `entries()` 指定至少 5 篇文章。
- 文章資料從一個 `$lib/data/posts.ts` 檔案匯入（模擬 CMS）。
- 設定 `trailingSlash = 'never'` 確保 URL 格式一致。
- 執行 `npm run build`，確認所有指定的 slug 都產生了靜態 HTML。
- 額外挑戰：在 blog layout 中設定 `csr = false`，讓 blog 成為完全靜態、零 JS 的閱讀體驗。

## Reference Solution

完整的 streaming dashboard 範例，涵蓋 deferred promises、`{#await}` 區塊與環境偵測。

```ts
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';

async function getQuickStats() {
  // Fast query
  return { users: 1234, orders: 567 };
}

async function getDetailedAnalytics() {
  // Slow query - simulate 2 second delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  return {
    revenue: 45678,
    topProducts: ['Keyboard', 'Mouse', 'Monitor'],
    conversionRate: 3.2
  };
}

export const load: PageServerLoad = async () => {
  return {
    stats: await getQuickStats(),
    // Don't await - this will be streamed
    analytics: getDetailedAnalytics()
  };
};
```

```svelte
<!-- src/routes/dashboard/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';
  let { data }: { data: PageData } = $props();
</script>

<h1>Dashboard</h1>

<!-- Immediate data -->
<section>
  <h2>Quick Stats</h2>
  <p>Users: {data.stats.users}</p>
  <p>Orders: {data.stats.orders}</p>
</section>

<!-- Streamed data -->
<section>
  <h2>Analytics</h2>
  {#await data.analytics}
    <p>Loading analytics...</p>
  {:then analytics}
    <p>Revenue: ${analytics.revenue}</p>
    <p>Conversion: {analytics.conversionRate}%</p>
    <ul>
      {#each analytics.topProducts as product}
        <li>{product}</li>
      {/each}
    </ul>
  {:catch error}
    <p>Failed to load analytics: {error.message}</p>
  {/await}
</section>
```

Prerender 與 CSR-only 頁面的 page option 設定。

```ts
// src/routes/about/+page.ts
export const prerender = true;
```

```ts
// src/routes/app/+page.ts
export const ssr = false; // Client-only page
```

Prerendered blog 的動態路由與 `entries` 設定。

```ts
// src/routes/blog/[slug]/+page.ts
export const prerender = true;

export function entries() {
  return [
    { slug: 'hello-world' },
    { slug: 'svelte-5-guide' },
    { slug: 'sveltekit-streaming' },
  ];
}
```

```ts
// src/routes/blog/[slug]/+page.server.ts
import type { PageServerLoad } from './$types';

const posts: Record<string, { title: string; content: string }> = {
  'hello-world': { title: 'Hello World', content: 'Welcome to our blog.' },
  'svelte-5-guide': { title: 'Svelte 5 Guide', content: 'Runes are great...' },
  'sveltekit-streaming': { title: 'SvelteKit Streaming', content: 'Stream your data...' },
};

export const load: PageServerLoad = async ({ params }) => {
  const post = posts[params.slug];
  if (!post) throw new Error('Post not found');
  return { post };
};
```

## Common Pitfalls

- **全域設定 `ssr = false` 而非僅在需要的頁面設定**：在 `+layout.ts` 中設 `export const ssr = false` 會影響所有子路由，導致整個網站失去 SSR 的 SEO 優勢。應該只在確實需要 CSR-only 的個別頁面（如 dashboard、canvas app）設定 `ssr = false`，其餘頁面保持預設的 SSR 行為。
- **Prerendered 頁面使用了 request-time 資料**：Prerender 在 `build` 時執行，此時沒有真實的 HTTP request。在 prerendered 頁面的 `load` 函式中使用 `cookies`、`request.headers`、`url.searchParams` 等 request-time 資訊會導致 build 錯誤或產出不正確的內容。解決方式：這類頁面不應 prerender，或改用 client-side 取得動態資料。
- **Streaming 的 Promise reject 卻沒有 `{:catch}` 區塊**：若 deferred promise 拋出錯誤但頁面中只寫了 `{#await data.report}{:then result}...{/await}` 而沒有 `{:catch}`，會導致 unhandled promise rejection。永遠為 streaming 資料加上 `{:catch error}` 區塊，提供使用者友善的錯誤訊息。
- **用 `browser` 判斷來執行應在 `onMount` 中執行的操作**：`browser` 適合 module-scope 或 import-time 的環境檢查（如 `if (browser) { ... }`）。但如果操作涉及 DOM 元素（如初始化圖表、綁定事件），應使用 `onMount`，因為 `browser` 為 `true` 時不保證 DOM 已掛載完成。
- **設定 `csr = false` 後加入需要互動的元素**：`csr = false` 表示不載入 client-side JavaScript，因此所有 `onclick` 事件處理器、`bind:value`、`$state` 等互動機制都不會生效。若頁面需要任何使用者互動，就不應設定 `csr = false`。

## Checklist

- [ ] 能在 `+page.ts` 或 `+layout.ts` 中設定 `ssr`、`csr`、`prerender` 控制頁面渲染策略。
- [ ] 能在 `load` 函式中使用不 `await` 的 Promise 實作 streaming，讓快資料先送達。
- [ ] 能使用 `{#await data.xxx}` 搭配 `{:then}`、`{:catch}` 為 streaming 資料提供 loading 與 error 狀態。
- [ ] 能使用 `$app/environment` 的 `browser`、`building`、`dev` 根據環境條件性執行程式碼。
- [ ] 能說明何時使用 SSR + CSR、SSR only、CSR only、Prerender 四種渲染策略。
- [ ] `npx svelte-check` 通過，無型別錯誤。

## Further Reading

- [SvelteKit Docs — Page options](https://svelte.dev/docs/kit/page-options)
- [SvelteKit Docs — Streaming](https://svelte.dev/docs/kit/load#Streaming-with-promises)
- [SvelteKit Docs — $app/environment](https://svelte.dev/docs/kit/$app-environment)
- [SvelteKit Docs — Prerendering](https://svelte.dev/docs/kit/page-options#prerender)
- [SvelteKit Docs — Adapters](https://svelte.dev/docs/kit/adapters)
- [Svelte Docs — {#await ...}](https://svelte.dev/docs/svelte/await)
- [SvelteKit Tutorial — Page options](https://svelte.dev/tutorial/kit/page-options)
