---
title: "Error Handling and Recovery / 錯誤處理與復原"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-17
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "15"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [14_advanced_routing_and_hooks]
---
# Error Handling and Recovery / 錯誤處理與復原

## Goal

建立完整的錯誤處理策略，涵蓋預期錯誤、未預期錯誤、以及使用者友善的復原機制。

良好的錯誤處理是使用者體驗的最後一道防線。學會區分 `error()` 與 `fail()` 的使用時機、設計多層級的 error boundary、以及提供有效的復原路徑，能確保即使在異常情況下，使用者仍能順利繼續操作而不會被「卡住」。

- **銜接上一章**：Ch14 學會了 hooks 與進階路由，現在要處理當事情出錯時的情況。
- **下一章預告**：Ch16 將深入效能優化與細粒度響應式。

## Prerequisites

- 已完成第 14 章（Advanced Routing and Hooks）。
- 熟悉 SvelteKit 路由系統、`load` function、`+page.server.ts`（Ch10–Ch11）。
- 理解 hooks 機制：`handle`、`handleFetch`（Ch14）。
- 熟悉 `$app/state`（`page`）與 `$app/navigation`（`goto`、`invalidateAll`）。
- 理解 form actions 與 `fail()` 的基本用法（Ch12）。

## Core Concepts

### 1. `+error.svelte` at route/layout levels — 路由層級的錯誤頁面

每個路由層級都可以有自己的 `+error.svelte`，作為該層級的 error boundary。當 `load` function 或頁面渲染發生錯誤時，SvelteKit 會**向上尋找最近的 `+error.svelte`** 來顯示錯誤畫面：

```
src/routes/
├── +error.svelte              # Root error boundary（最後防線）
├── +layout.svelte
├── dashboard/
│   ├── +error.svelte          # Dashboard 專屬 error boundary
│   ├── +layout.svelte
│   ├── +page.svelte
│   └── analytics/
│       └── +page.svelte       # 此頁面錯誤 → 使用 dashboard/+error.svelte
└── blog/
    └── [slug]/
        └── +page.svelte       # 此頁面錯誤 → 使用 root +error.svelte
```

錯誤 boundary 的尋找順序：

1. SvelteKit 從發生錯誤的路由開始，向上逐層尋找 `+error.svelte`。
2. 找到的第一個 `+error.svelte` 會被渲染在其**父層 layout** 中（error page 取代了出錯的頁面，但保留父層 layout 的 UI）。
3. 若一路找到 root 都沒有 `+error.svelte`，SvelteKit 會使用內建的極簡錯誤畫面。

**重要**：`+layout.svelte` 本身的錯誤**不會**被同層的 `+error.svelte` 捕獲，而是會被**上一層**的 `+error.svelte` 捕獲。這是因為 error page 需要渲染在父層 layout 中。

```svelte
<!-- src/routes/+error.svelte -->
<script lang="ts">
  import { page } from '$app/state';
</script>

<h1>{page.status} Error</h1>
<p>{page.error?.message}</p>
```

| 何時用路由級 `+error.svelte` | 何時用全域（root）`+error.svelte` |
|---|---|
| 特定區域（如 dashboard）需要不同的錯誤呈現風格 | 應用程式大部分頁面共用相同的錯誤樣式 |
| 錯誤頁面需要存取該層級 layout 的 UI 元素（sidebar、nav） | 提供最後防線，確保任何未被攔截的錯誤都有畫面 |
| 需要根據不同區域提供不同的復原選項 | 錯誤處理邏輯簡單，一個通用頁面即可 |

### 2. `error()` helper, expected vs unexpected errors — 預期錯誤與未預期錯誤

SvelteKit 將錯誤分為兩類：**預期錯誤（expected）** 和 **未預期錯誤（unexpected）**，處理方式截然不同。

#### Expected errors — 使用 `error()` helper

透過從 `@sveltejs/kit` 匯入的 `error()` helper 主動拋出的錯誤。這些是開發者預期會發生的情況（如資源不存在、權限不足）：

```ts
import { error } from '@sveltejs/kit';

// 基本用法：傳入 status code 和訊息字串
error(404, 'Not found');

// 結構化資料：傳入物件，可包含額外欄位
error(404, { message: 'Not found', code: 'ITEM_MISSING' });

// 權限不足
error(403, { message: 'You do not have access to this resource.' });
```

`error()` 會拋出一個 `HttpError`，SvelteKit 會：
1. 設定 HTTP status code。
2. 將錯誤資訊傳遞給最近的 `+error.svelte`。
3. **不會**觸發 `handleError` hook（因為這是預期行為）。

#### Unexpected errors — 非 `HttpError` 的例外

任何不是透過 `error()` 拋出的錯誤都是未預期錯誤（例如資料庫連線失敗、第三方 API timeout）：

```ts
export const load: PageServerLoad = async () => {
  const data = await db.query('SELECT * FROM posts');
  // 如果 db.query 拋出一般的 Error，這就是 unexpected error
  return { posts: data };
};
```

未預期錯誤的處理流程：
1. SvelteKit 呼叫 `handleError` hook（如果有定義的話）。
2. 錯誤的原始訊息**不會**暴露給使用者（避免洩漏敏感資訊）。
3. 使用者看到的是 `handleError` 回傳的安全訊息，或預設的 "Internal Error"。
4. HTTP status code 為 500。

#### `error()` vs `fail()` — 顯示 error page vs 回傳表單資料

這是最常被混淆的兩個 helper：

```ts
import { error, fail } from '@sveltejs/kit';

// error()：顯示 error page，整個頁面被替換
// 用於：load function 中找不到資源、權限檢查失敗
error(404, { message: 'Post not found.' });

// fail()：回傳資料到表單，頁面不會被替換
// 用於：form action 中的驗證失敗、業務邏輯錯誤
return fail(400, { email, errors: { email: 'Invalid email format.' } });
```

| 何時用 `error()` | 何時用 `fail()` |
|---|---|
| 在 `load` function 中找不到資源 | 在 form action 中處理驗證失敗 |
| 權限不足、未授權，整頁應顯示錯誤 | 使用者輸入有誤，需要回傳表單資料讓使用者修正 |
| 結果是**頁面被替換為 error page** | 結果是**頁面保持不變**，表單收到 `form` prop 中的錯誤資料 |

### 3. `page.error` / `page.status` and recovery patterns — 錯誤資訊與復原模式

在 `+error.svelte` 中，透過 `page` 物件取得錯誤的詳細資訊：

```svelte
<script lang="ts">
  import { page } from '$app/state';
</script>

<!-- page.status: HTTP status code (404, 500, etc.) -->
<h1>Error {page.status}</h1>

<!-- page.error: 錯誤物件，包含 message 及 handleError 回傳的額外欄位 -->
<p>{page.error?.message}</p>

<!-- 如果 handleError 回傳了 errorId -->
{#if page.error?.errorId}
  <p class="error-id">Error ID: {page.error.errorId}</p>
{/if}
```

#### Recovery patterns — 復原模式

良好的錯誤頁面不只顯示錯誤，更要提供使用者繼續操作的路徑：

**1. Retry（重試）**：呼叫 `invalidateAll()` 重新執行所有 `load` function，適合暫時性錯誤（網路問題、伺服器暫時不可用）：

```svelte
<script lang="ts">
  import { invalidateAll } from '$app/navigation';

  let retrying = $state(false);

  async function retry() {
    retrying = true;
    await invalidateAll();
    retrying = false;
  }
</script>

<button onclick={retry} disabled={retrying}>
  {retrying ? 'Retrying...' : 'Try again'}
</button>
```

**2. Back navigation（返回上一頁）**：使用瀏覽器的 `history.back()`：

```svelte
<button onclick={() => history.back()}>Go back</button>
```

**3. Redirect to safe page（導向安全頁面）**：提供回到首頁或其他已知安全頁面的連結：

```svelte
<a href="/">Go home</a>
<a href="/dashboard">Back to dashboard</a>
```

| 何時顯示重試按鈕 | 何時導向首頁/安全頁面 |
|---|---|
| 500 系列錯誤（伺服器暫時問題、timeout） | 404 錯誤（資源確定不存在，重試無意義） |
| 網路連線問題可能是暫時的 | 403 錯誤（權限問題，重試不會改變結果） |
| 資料來源可能在短時間內恢復 | 使用者明顯迷路，需要引導回主要頁面 |

### 4. Root error fallback and `error.html` — 最終 fallback

#### `src/error.html` — 純 HTML 的最後防線

當 SvelteKit 本身無法正常運作時（例如 JavaScript 載入失敗、SvelteKit runtime 發生致命錯誤），`+error.svelte` 元件也無法渲染。此時 SvelteKit 會使用 `src/error.html` 作為**最後的 fallback**。

`src/error.html` 是一個純 HTML 檔案，不能使用任何 Svelte 語法或 JavaScript 模組。SvelteKit 提供兩個佔位符：

- `%sveltekit.status%`：HTTP status code
- `%sveltekit.error.message%`：錯誤訊息

```html
<!-- src/error.html -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>%sveltekit.status% | Error</title>
    <style>
      body {
        font-family: system-ui, -apple-system, sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        margin: 0;
        background: #f8fafc;
        color: #334155;
      }
      .error-container {
        text-align: center;
        padding: 2rem;
      }
      h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        color: #0f172a;
      }
      p {
        font-size: 1.25rem;
        color: #64748b;
      }
      a {
        display: inline-block;
        margin-top: 1.5rem;
        color: #2563eb;
        text-decoration: none;
      }
      a:hover {
        text-decoration: underline;
      }
    </style>
  </head>
  <body>
    <div class="error-container">
      <h1>%sveltekit.status%</h1>
      <p>%sveltekit.error.message%</p>
      <a href="/">Go home</a>
    </div>
  </body>
</html>
```

**重要注意事項**：
- `src/error.html` 不是 Svelte 元件，不能用 `{}`、`{#if}` 等模板語法。
- 不能匯入 JavaScript，因為此時 SvelteKit 的 runtime 可能尚未載入。
- 只有 `%sveltekit.status%` 和 `%sveltekit.error.message%` 兩個佔位符可用。
- 如果未提供此檔案，SvelteKit 會使用內建的預設 fallback 頁面。

| 何時由 `+error.svelte` 處理 | 何時由 `error.html` 處理 |
|---|---|
| `load` function 拋出錯誤 | SvelteKit runtime 本身無法載入 |
| 頁面渲染過程中發生錯誤 | JavaScript bundle 載入失敗 |
| 應用正常運作但遇到業務錯誤 | 伺服器在 SvelteKit 初始化前就出錯 |
| 可以使用 Svelte 元件、stores、navigation | 只能使用純 HTML 和 inline CSS |

## Step-by-step

### Step 1：建立 root `+error.svelte` 顯示基本錯誤資訊

在 `src/routes/+error.svelte` 建立根層級的 error boundary，顯示 HTTP status code 和錯誤訊息：

```svelte
<!-- src/routes/+error.svelte -->
<script lang="ts">
  import { page } from '$app/state';
</script>

<div class="error-page">
  <h1>{page.status}</h1>
  <p>{page.error?.message ?? 'Something went wrong.'}</p>
  <a href="/">Go home</a>
</div>

<style>
  .error-page {
    text-align: center;
    padding: 4rem 1rem;
  }
  h1 {
    font-size: 4rem;
    margin-bottom: 0.5rem;
  }
</style>
```

此時任何路由的錯誤都會被這個根 error page 攔截。

### Step 2：在 load function 中使用 `error(404)` 處理缺失資源

假設有一個 blog 動態路由 `src/routes/blog/[slug]/+page.server.ts`，當文章不存在時拋出 404：

```ts
// src/routes/blog/[slug]/+page.server.ts
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const posts: Record<string, { title: string; content: string }> = {
  'hello-world': { title: 'Hello World', content: 'Welcome to my blog!' },
  'sveltekit-tips': { title: 'SvelteKit Tips', content: 'Here are some tips...' },
};

export const load: PageServerLoad = async ({ params }) => {
  const post = posts[params.slug];

  if (!post) {
    error(404, { message: `Post "${params.slug}" not found.` });
  }

  return { post };
};
```

瀏覽 `/blog/nonexistent` 會觸發 Step 1 建立的 root error page，顯示 `404` 和 `Post "nonexistent" not found.`。

### Step 3：為 `/dashboard` 建立巢狀的 `+error.svelte`

Dashboard 區域需要不同的錯誤風格，保留 dashboard layout 的 sidebar，只替換主要內容區域：

```svelte
<!-- src/routes/dashboard/+error.svelte -->
<script lang="ts">
  import { page } from '$app/state';
  import { invalidateAll } from '$app/navigation';

  let retrying = $state(false);

  async function retry() {
    retrying = true;
    await invalidateAll();
    retrying = false;
  }
</script>

<div class="dashboard-error">
  <div class="error-icon">⚠</div>
  <h2>Dashboard Error ({page.status})</h2>
  <p>{page.error?.message ?? 'Failed to load dashboard data.'}</p>

  <div class="actions">
    <button onclick={retry} disabled={retrying}>
      {retrying ? 'Retrying...' : 'Retry'}
    </button>
    <a href="/dashboard">Dashboard Home</a>
  </div>
</div>

<style>
  .dashboard-error {
    padding: 2rem;
    text-align: center;
  }
  .error-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  .actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 1.5rem;
  }
</style>
```

當 `/dashboard/analytics` 的 load function 發生錯誤時，dashboard 的 sidebar layout 會保留，只有主要內容區域顯示此 error page。

### Step 4：在 `hooks.server.ts` 中實作 `handleError` 處理未預期錯誤

`handleError` hook 會在未預期錯誤（非 `HttpError`）發生時被呼叫。用它來記錄錯誤並回傳安全的訊息：

```ts
// src/hooks.server.ts
import type { HandleServerError } from '@sveltejs/kit';

export const handleError: HandleServerError = async ({ error, event, status, message }) => {
  const errorId = crypto.randomUUID();

  // 記錄完整的錯誤資訊到 server log（含 stack trace、request 資訊）
  console.error(`[${errorId}] ${event.request.method} ${event.url.pathname}:`, error);

  // 回傳安全的錯誤資訊給使用者（不含敏感的 stack trace 或內部訊息）
  return {
    message: 'An unexpected error occurred.',
    errorId
  };
};
```

回傳的物件會成為 `page.error` 的值。`errorId` 讓使用者可以回報錯誤 ID，方便開發者在 log 中查找。

### Step 5：在 `hooks.client.ts` 中實作 client-side `handleError`

Client-side 的未預期錯誤（如元件渲染時的 runtime error）也需要處理：

```ts
// src/hooks.client.ts
import type { HandleClientError } from '@sveltejs/kit';

export const handleError: HandleClientError = async ({ error, status, message }) => {
  const errorId = crypto.randomUUID();

  console.error(`[${errorId}] Client error:`, error);

  // 可以在這裡將錯誤送到外部 error reporting 服務
  // await reportError({ errorId, error, status });

  return {
    message: 'Something went wrong on the client.',
    errorId
  };
};
```

**注意**：client hook 的 callback 參數沒有 `event`（因為 client-side 沒有 `RequestEvent`）。

### Step 6：加入重試按鈕，呼叫 `invalidateAll()` 重新執行 load

更新 root `+error.svelte`，加入 retry 機制：

```svelte
<!-- src/routes/+error.svelte（更新版） -->
<script lang="ts">
  import { page } from '$app/state';
  import { invalidateAll } from '$app/navigation';

  let retrying = $state(false);

  async function retry() {
    retrying = true;
    await invalidateAll();
    retrying = false;
  }
</script>

<div class="error-page">
  <h1>{page.status}</h1>
  <p>{page.error?.message ?? 'Something went wrong.'}</p>

  {#if page.error?.errorId}
    <p class="error-id">Error ID: {page.error.errorId}</p>
  {/if}

  <div class="actions">
    {#if page.status >= 500}
      <button onclick={retry} disabled={retrying}>
        {retrying ? 'Retrying...' : 'Try again'}
      </button>
    {/if}
    <a href="/">Go home</a>
  </div>
</div>

<style>
  .error-page { text-align: center; padding: 4rem 1rem; }
  .error-id { font-size: 0.875rem; color: #94a3b8; font-family: monospace; }
  .actions { display: flex; gap: 1rem; justify-content: center; margin-top: 2rem; }
  button { padding: 0.5rem 1rem; border-radius: 0.375rem; cursor: pointer; }
  a { padding: 0.5rem 1rem; color: #2563eb; text-decoration: none; }
</style>
```

`invalidateAll()` 會重新執行當前頁面的所有 `load` function。如果錯誤是暫時性的（如網路中斷），重試可能會成功，頁面會自動恢復正常。注意我們只在 500 系列錯誤時才顯示重試按鈕，因為 404 等 client error 重試沒有意義。

### Step 7：加入 "Go back" 和 "Go home" 復原連結

在 error page 中提供多種導航選項，讓使用者不會被「卡住」：

```svelte
<div class="actions">
  {#if page.status >= 500}
    <button onclick={retry} disabled={retrying}>
      {retrying ? 'Retrying...' : 'Try again'}
    </button>
  {/if}
  <button onclick={() => history.back()}>Go back</button>
  <a href="/">Go home</a>
</div>
```

三種復原選項的適用時機：
- **Try again**：500 系列錯誤，暫時性問題可能已修復。
- **Go back**：使用者從某個頁面導航而來，返回上一頁是最直覺的選擇。
- **Go home**：當使用者直接透過 URL 進入錯誤頁面，或不確定上一頁是哪裡。

### Step 8：自訂 `src/error.html` 應對 SvelteKit 本身的故障

建立 `src/error.html` 作為最終 fallback：

```html
<!-- src/error.html -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>%sveltekit.status% | Error</title>
    <style>
      body {
        font-family: system-ui, -apple-system, sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        margin: 0;
        background: #f8fafc;
        color: #334155;
      }
      .error-container { text-align: center; padding: 2rem; }
      h1 { font-size: 3rem; margin-bottom: 0.5rem; color: #0f172a; }
      p { font-size: 1.125rem; color: #64748b; }
      a {
        display: inline-block;
        margin-top: 1.5rem;
        padding: 0.5rem 1.5rem;
        background: #2563eb;
        color: white;
        border-radius: 0.375rem;
        text-decoration: none;
      }
      a:hover { background: #1d4ed8; }
    </style>
  </head>
  <body>
    <div class="error-container">
      <h1>%sveltekit.status%</h1>
      <p>%sveltekit.error.message%</p>
      <a href="/">Go home</a>
    </div>
  </body>
</html>
```

此檔案只在 SvelteKit 無法正常運作時使用（例如 JavaScript bundle 載入失敗）。平時不會被觸發。

## Hands-on Lab

### Foundation：建立 root 與 dashboard error page，處理 404

**目標**：建立基本的錯誤處理架構。

1. 在 `src/routes/+error.svelte` 建立 root error page，顯示 status 和 message。
2. 在 `src/routes/dashboard/+error.svelte` 建立 dashboard 專屬 error page，風格與 root 不同。
3. 在 `src/routes/blog/[slug]/+page.server.ts` 中，當文章不存在時使用 `error(404)` 拋出錯誤。
4. 瀏覽 `/blog/nonexistent` 確認 root error page 顯示。
5. 在 `/dashboard` 的 load function 中模擬錯誤，確認 dashboard error page 顯示。

**驗收標準**：
- [ ] `/blog/nonexistent` 顯示 root error page，status 為 404。
- [ ] Dashboard 區域的錯誤顯示 dashboard 專屬 error page。
- [ ] Error page 保留對應的 layout（dashboard error page 有 sidebar）。

### Advanced：結構化錯誤處理與 `handleError` hooks

**目標**：實作完整的錯誤處理 pipeline。

1. 在 `src/hooks.server.ts` 實作 `handleError`，生成 `errorId` 並記錄完整錯誤資訊。
2. 在 `src/hooks.client.ts` 實作 `handleError`，同樣生成 `errorId`。
3. 更新 `+error.svelte`，顯示 `errorId`（如果存在）。
4. 在 `app.d.ts` 中擴充 `App.Error` 型別，加入 `errorId` 欄位：
   ```ts
   declare global {
     namespace App {
       interface Error {
         message: string;
         errorId?: string;
       }
     }
   }
   ```
5. 在某個 load function 中故意拋出一般的 `Error`（不使用 `error()`），觀察 `handleError` 的執行與 `errorId` 的顯示。

**驗收標準**：
- [ ] 未預期錯誤觸發 `handleError`，console 中可見 `errorId` 和完整 stack trace。
- [ ] Error page 顯示 `errorId`，但不暴露 stack trace 或內部訊息。
- [ ] 預期錯誤（`error(404)`）**不會**觸發 `handleError`。
- [ ] `App.Error` 型別已正確擴充，TypeScript 無錯誤。

### Challenge：Resilient data loading — 具備重試與 fallback 的資料載入

**目標**：建立生產級的彈性載入模式。

1. 建立一個 `$lib/utils/resilient-fetch.ts` 工具函式，支援：
   - 自動重試（configurable retry count）。
   - 指數退避（exponential backoff）：每次重試的等待時間加倍。
   - 超時控制（timeout）。
2. 在 load function 中使用此工具函式載入資料。
3. 當所有重試都失敗後，提供 fallback content（如快取的舊資料或預設內容）。
4. Error page 的 retry 按鈕使用 `invalidateAll()` 重新載入。
5. 加入 exponential backoff 的 retry：error page 的 retry 按鈕在連續失敗時增加等待時間。

**驗收標準**：
- [ ] `resilient-fetch` 在第一次失敗後自動重試，直到達到最大次數。
- [ ] 重試之間的等待時間遵循指數退避策略（如 1s → 2s → 4s）。
- [ ] 所有重試失敗後，頁面顯示 fallback content 而非 error page（graceful degradation）。
- [ ] Error page 的 retry 按鈕正常運作，且不會在短時間內過度請求。

## Reference Solution

### Root `+error.svelte`（完整版）

```svelte
<!-- src/routes/+error.svelte -->
<script lang="ts">
  import { page } from '$app/state';
  import { invalidateAll } from '$app/navigation';

  let retrying = $state(false);

  async function retry() {
    retrying = true;
    await invalidateAll();
    retrying = false;
  }
</script>

<div class="error-page">
  <h1>{page.status}</h1>
  <p>{page.error?.message ?? 'Something went wrong.'}</p>

  {#if page.error?.errorId}
    <p class="error-id">Error ID: {page.error.errorId}</p>
  {/if}

  <div class="actions">
    {#if page.status >= 500}
      <button onclick={retry} disabled={retrying}>
        {retrying ? 'Retrying...' : 'Try again'}
      </button>
    {/if}
    <button onclick={() => history.back()}>Go back</button>
    <a href="/">Go home</a>
  </div>
</div>

<style>
  .error-page { text-align: center; padding: 4rem 1rem; }
  h1 { font-size: 4rem; margin-bottom: 0.5rem; }
  .error-id { font-size: 0.875rem; color: #94a3b8; font-family: monospace; }
  .actions { display: flex; gap: 1rem; justify-content: center; margin-top: 2rem; }
  button {
    padding: 0.5rem 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.375rem;
    background: white;
    cursor: pointer;
  }
  button:hover { background: #f8fafc; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  a { padding: 0.5rem 1rem; color: #2563eb; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
```

### Load function with `error()`

```ts
// src/routes/blog/[slug]/+page.server.ts
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const posts: Record<string, { title: string; content: string }> = {
  'hello-world': { title: 'Hello World', content: 'Welcome to my blog!' },
  'sveltekit-tips': { title: 'SvelteKit Tips', content: 'Here are some useful tips...' },
};

export const load: PageServerLoad = async ({ params }) => {
  const post = posts[params.slug];

  if (!post) {
    error(404, { message: `Post "${params.slug}" not found.` });
  }

  return { post };
};
```

### Server-side `handleError`

```ts
// src/hooks.server.ts
import type { HandleServerError } from '@sveltejs/kit';

export const handleError: HandleServerError = async ({ error, event, status, message }) => {
  const errorId = crypto.randomUUID();

  // Log full error details for debugging (visible in server logs only)
  console.error(`[${errorId}] ${event.request.method} ${event.url.pathname}:`, error);

  // Return safe error info to the client (no stack traces, no internal details)
  return {
    message: 'An unexpected error occurred.',
    errorId
  };
};
```

### Client-side `handleError`

```ts
// src/hooks.client.ts
import type { HandleClientError } from '@sveltejs/kit';

export const handleError: HandleClientError = async ({ error, status, message }) => {
  const errorId = crypto.randomUUID();

  console.error(`[${errorId}] Client error:`, error);

  // Could send to an error reporting service (e.g., Sentry)
  // await reportToSentry({ errorId, error, status });

  return {
    message: 'Something went wrong on the client.',
    errorId
  };
};
```

### `App.Error` 型別擴充

```ts
// src/app.d.ts
declare global {
  namespace App {
    interface Error {
      message: string;
      errorId?: string;
    }
  }
}

export {};
```

### Resilient fetch utility（Challenge 參考解答）

```ts
// src/lib/utils/resilient-fetch.ts
interface ResilientFetchOptions {
  retries?: number;
  baseDelay?: number;   // ms, base delay before first retry
  timeout?: number;     // ms, per-request timeout
}

export async function resilientFetch(
  url: string,
  fetchFn: typeof fetch,
  options: ResilientFetchOptions = {}
): Promise<Response> {
  const { retries = 3, baseDelay = 1000, timeout = 5000 } = options;

  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetchFn(url, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response;
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err));

      if (attempt < retries) {
        // Exponential backoff: 1s → 2s → 4s → ...
        const delay = baseDelay * Math.pow(2, attempt);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError ?? new Error('All retries exhausted.');
}
```

```ts
// Usage in a load function
import { resilientFetch } from '$lib/utils/resilient-fetch';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const fallbackData = { items: [], stale: true };

export const load: PageServerLoad = async ({ fetch }) => {
  try {
    const response = await resilientFetch('/api/dashboard/stats', fetch, {
      retries: 3,
      baseDelay: 500,
      timeout: 3000,
    });
    return { stats: await response.json() };
  } catch (err) {
    // Graceful degradation: return fallback content instead of error page
    console.error('Failed to load dashboard stats after retries:', err);
    return { stats: fallbackData };
  }
};
```

## Common Pitfalls

### 1. 未建立 `src/error.html` — SvelteKit 本身故障時使用者看到空白頁面

如果 SvelteKit 的 JavaScript bundle 載入失敗（CDN 故障、網路不穩定），`+error.svelte` 也無法渲染。若未提供 `src/error.html`，使用者會看到 SvelteKit 的極簡預設錯誤頁面，缺乏品牌識別和導航選項：

```
解法：建立 src/error.html，加入品牌 logo、基本樣式，以及回到首頁的連結。
     不需要複雜的 JavaScript，純 HTML + inline CSS 即可。
```

### 2. 在 error page 中暴露內部錯誤細節（stack trace、SQL error）

未預期錯誤的原始訊息可能包含敏感資訊（資料庫查詢、檔案路徑、API key）。如果直接將這些訊息傳給前端，會造成安全風險：

```ts
// 錯誤：未設定 handleError，未預期錯誤的原始訊息可能洩漏
// SvelteKit 預設行為已經會過濾，但最佳實踐是明確設定 handleError

// 正確：在 handleError 中回傳安全訊息
export const handleError: HandleServerError = async ({ error, event }) => {
  const errorId = crypto.randomUUID();
  console.error(`[${errorId}]`, error);  // 完整錯誤只記錄在 server log

  return {
    message: 'An unexpected error occurred.',  // 使用者只看到通用訊息
    errorId                                     // 提供 ID 方便回報
  };
};
```

### 3. 在 form action 中使用 `error()` 而非 `fail()`

`error()` 會顯示 error page，整個頁面被替換。在 form action 中，通常希望保留表單狀態讓使用者修正輸入，應使用 `fail()`：

```ts
// 錯誤：表單驗證失敗時使用 error()，使用者看到 error page，失去所有填寫的內容
export const actions = {
  default: async ({ request }) => {
    const data = await request.formData();
    const email = data.get('email') as string;
    if (!email.includes('@')) {
      error(400, 'Invalid email');  // 使用者看到 error page
    }
  }
};

// 正確：使用 fail() 回傳資料到表單
export const actions = {
  default: async ({ request }) => {
    const data = await request.formData();
    const email = data.get('email') as string;
    if (!email.includes('@')) {
      return fail(400, { email, error: 'Invalid email format.' });  // 表單保留使用者輸入
    }
  }
};
```

### 4. 忘記 layout group 中的 `+error.svelte` 會捕獲所有子路由的錯誤

在 `(group)/+error.svelte` 會成為該 group 下所有子路由的 error boundary。如果 group 下有些路由需要不同的錯誤處理，需要在子路由層級額外建立 `+error.svelte`：

```
src/routes/(app)/
├── +error.svelte           # 捕獲 (app) group 下所有子路由的錯誤
├── +layout.svelte
├── dashboard/
│   └── +page.svelte        # 錯誤 → 使用 (app)/+error.svelte
└── settings/
    ├── +error.svelte       # 覆蓋：settings 有自己的 error page
    └── +page.svelte        # 錯誤 → 使用 settings/+error.svelte
```

### 5. Error page 不提供復原選項，使用者被「卡住」

只顯示錯誤訊息而不提供任何操作選項，使用者除了手動修改 URL 或按瀏覽器返回鍵外無法繼續操作：

```svelte
<!-- 不良實踐：只顯示錯誤，沒有出路 -->
<h1>Error {page.status}</h1>
<p>{page.error?.message}</p>

<!-- 良好實踐：提供多種復原路徑 -->
<h1>Error {page.status}</h1>
<p>{page.error?.message}</p>
<div class="actions">
  <button onclick={retry}>Try again</button>
  <button onclick={() => history.back()}>Go back</button>
  <a href="/">Go home</a>
</div>
```

## `<svelte:boundary>` — 錯誤邊界元素

> Svelte 5 新增。`<svelte:boundary>` 是一個內建的特殊元素，可在元件樹的任意位置建立錯誤邊界（error boundary）。當其子元素在渲染時拋出錯誤，`<svelte:boundary>` 會攔截錯誤並顯示 fallback UI，而不會讓整個應用崩潰。

### 基本語法 Basic Syntax

`<svelte:boundary>` 透過 `failed` snippet 定義錯誤 fallback UI，透過 `onerror` 回呼處理錯誤紀錄：

```svelte
<svelte:boundary onerror={(error, reset) => console.error(error)}>
  <FlakyComponent />

  {#snippet failed(error, reset)}
    <div class="error-fallback">
      <p>Something went wrong: {error.message}</p>
      <button onclick={reset}>Try again</button>
    </div>
  {/snippet}
</svelte:boundary>
```

- **子元素**：正常的元件內容。若渲染過程中拋出錯誤，會被 boundary 攔截。
- **`{#snippet failed(error, reset)}`**：定義錯誤 fallback UI。`error` 是捕獲的錯誤物件，`reset` 是一個函式，呼叫後會嘗試重新渲染子元素。
- **`onerror`**：可選的事件處理器，在錯誤發生時被呼叫。可用於紀錄錯誤（如送到 Sentry）。接收 `error` 和 `reset` 兩個參數。

### `failed` snippet — 錯誤 fallback UI

`failed` snippet 是 `<svelte:boundary>` 最核心的功能。它接收兩個參數：

```svelte
<svelte:boundary>
  <UserProfile userId={data.userId} />

  {#snippet failed(error, reset)}
    <div class="error-card">
      <h3>Failed to load profile</h3>
      <p>{error.message}</p>
      <div class="actions">
        <button onclick={reset}>Retry</button>
        <a href="/users">Back to list</a>
      </div>
    </div>
  {/snippet}
</svelte:boundary>
```

**`reset` 函式的行為**：呼叫 `reset()` 會清除錯誤狀態，並嘗試重新渲染 boundary 內的子元素。如果造成錯誤的條件仍然存在（例如 props 沒變），錯誤會再次發生並再次顯示 fallback。

### `pending` snippet — 非同步 loading fallback（搭配 Async SSR）

> 需要啟用 `compilerOptions.experimental.async`。

搭配 Async SSR（Ch13），`<svelte:boundary>` 支援 `pending` snippet，在子元素中的 `await` 表達式尚未完成時顯示 loading UI：

```svelte
<svelte:boundary>
  <!-- 這些 await 表達式會在 server 端被解析 -->
  <h1>{await getUser(userId)}</h1>
  <p>{await getUserBio(userId)}</p>

  {#snippet pending()}
    <div class="skeleton">
      <div class="skeleton-title"></div>
      <div class="skeleton-text"></div>
    </div>
  {/snippet}

  {#snippet failed(error, reset)}
    <p>Error: {error.message}</p>
    <button onclick={reset}>Retry</button>
  {/snippet}
</svelte:boundary>
```

- **Server 端行為**：server 渲染時，若子元素中有 `await` 表達式尚未完成，server 會先送出 `pending` snippet 的 HTML，待 `await` 完成後再串流完整結果。
- **Client 端行為**：`pending` snippet 在 client 端導航時也會作為 loading fallback。
- 同一個 `<svelte:boundary>` 可以同時有 `pending` 和 `failed` snippet，分別處理 loading 和 error 狀態。

### 巢狀 boundary Nested Boundaries

`<svelte:boundary>` 可以巢狀使用，內層 boundary 攔截不到的錯誤會向上冒泡到外層 boundary：

```svelte
<!-- 外層 boundary：攔截整個 dashboard 的錯誤 -->
<svelte:boundary>
  <div class="dashboard">
    <h1>Dashboard</h1>

    <!-- 內層 boundary：只攔截 chart 的錯誤 -->
    <svelte:boundary>
      <Chart data={chartData} />

      {#snippet failed(error, reset)}
        <div class="chart-error">
          <p>Chart failed to render</p>
          <button onclick={reset}>Retry chart</button>
        </div>
      {/snippet}
    </svelte:boundary>

    <!-- 此區塊的錯誤由外層 boundary 處理 -->
    <StatsPanel />
  </div>

  {#snippet failed(error, reset)}
    <p>Dashboard error: {error.message}</p>
    <button onclick={reset}>Reload dashboard</button>
  {/snippet}
</svelte:boundary>
```

### `<svelte:boundary>` vs SvelteKit `+error.svelte` 比較

| 特性 | `<svelte:boundary>` | `+error.svelte` |
|------|---------------------|-----------------|
| 層級 | 元件層級（任意位置） | 路由層級（`src/routes/` 下） |
| 攔截範圍 | 子元件渲染時的 runtime error | `load` function 錯誤 + 頁面渲染錯誤 |
| 粒度 | 可包裝任意元件子樹 | 以路由為單位 |
| reset 支援 | 內建 `reset` 函式 | 需要手動 `invalidateAll()` |
| pending 支援 | 內建 `pending` snippet（async SSR） | 不支援 |
| HTTP status | 無（元件層級概念） | 有（設定 HTTP status code） |
| 適用 | 元件級的局部錯誤隔離 | 頁面級的錯誤頁面 |

### 與 React Error Boundary 的比較

| 特性 | Svelte `<svelte:boundary>` | React `ErrorBoundary` |
|------|---------------------------|----------------------|
| 語法 | 內建特殊元素，宣告式 | 需要 class component 或第三方 library（react-error-boundary） |
| 設定 | `{#snippet failed(error, reset)}` | `getDerivedStateFromError` + `componentDidCatch` |
| reset 機制 | 內建 `reset` 函式參數 | 需要手動管理 state（`resetKeys` 等） |
| async loading | 內建 `pending` snippet | 需要 `<Suspense>` 配合 |
| 事件處理 | `onerror` 屬性 | `componentDidCatch` 生命週期方法 |
| 函式元件支援 | N/A（Svelte 沒有 class/function 元件之分） | class component only（或用 react-error-boundary） |
| 複雜度 | 極低——幾行宣告式語法 | 中等——需要理解 class component 或引入第三方套件 |

```svelte
<!-- Svelte：簡潔的宣告式語法 -->
<svelte:boundary>
  <MyComponent />

  {#snippet failed(error, reset)}
    <p>{error.message}</p>
    <button onclick={reset}>Retry</button>
  {/snippet}
</svelte:boundary>
```

```tsx
// React：需要 class component 或 react-error-boundary
import { ErrorBoundary } from 'react-error-boundary';

function Fallback({ error, resetErrorBoundary }) {
  return (
    <div>
      <p>{error.message}</p>
      <button onClick={resetErrorBoundary}>Retry</button>
    </div>
  );
}

<ErrorBoundary FallbackComponent={Fallback}>
  <MyComponent />
</ErrorBoundary>
```

| 何時用 `<svelte:boundary>` | 何時用 `+error.svelte` |
|---|---|
| 頁面中某個區塊（widget、chart）可能出錯，但不希望整頁崩潰 | 整個頁面的 `load` 失敗（404、500）需要顯示錯誤頁面 |
| 需要在出錯區域原地顯示 fallback UI 和 retry 按鈕 | 需要設定 HTTP status code（如 404 回應） |
| 使用 Async SSR，需要 `pending` fallback 處理 loading 狀態 | 需要與 SvelteKit 路由系統整合的錯誤處理 |
| 第三方元件可能拋出未知的 runtime error | 需要統一的錯誤頁面風格（共用 layout） |

### `<svelte:boundary>` 常見陷阱

1. **沒有提供 `failed` snippet**：若 boundary 內發生錯誤但沒有 `failed` snippet，錯誤會向上冒泡到父層。確保至少有一個 boundary 提供 fallback UI。
2. **`reset` 不會修復根本原因**：`reset()` 只是重新渲染子元素。如果錯誤的根本原因沒有解決（如 props 仍然有問題），錯誤會再次發生。可考慮在 `reset` 前先修改 state。
3. **不會攔截 `load` function 的錯誤**：`<svelte:boundary>` 只攔截**渲染時**的 runtime error。`load` function 中使用 `error()` 拋出的錯誤仍由 SvelteKit 的 `+error.svelte` 處理。
4. **不會攔截事件處理器中的錯誤**：`onclick`、`onsubmit` 等事件處理器中的錯誤不會被 boundary 攔截（因為不是在渲染過程中發生的）。需要在事件處理器中自行 `try/catch`。
5. **巢狀 boundary 的效能考量**：過度巢狀的 boundary 會增加元件樹的複雜度。只在確實需要錯誤隔離的區域使用。

## Checklist

- [ ] Root `+error.svelte` 存在，並顯示 `page.status` 和 `page.error?.message`
- [ ] `handleError` hooks 已設定（`hooks.server.ts` + `hooks.client.ts`），回傳安全訊息和 `errorId`
- [ ] 預期錯誤使用 `error()`，form 錯誤使用 `fail()`，兩者不混用
- [ ] Error page 包含復原選項：retry（500 系列）、go back、go home
- [ ] `src/error.html` 存在，作為 SvelteKit 無法載入時的最後防線
- [ ] `App.Error` 型別已在 `app.d.ts` 中擴充以包含 `errorId`
- [ ] 未預期錯誤不會暴露 stack trace 或內部訊息給使用者
- [ ] 能使用 `<svelte:boundary>` 搭配 `failed` snippet 建立元件級錯誤邊界
- [ ] 能使用 `<svelte:boundary>` 的 `pending` snippet 搭配 Async SSR 提供 loading fallback（⚠️ Experimental）
- [ ] 能區分 `<svelte:boundary>`（元件級）與 `+error.svelte`（路由級）的適用場景
- [ ] `npx svelte-check` 通過，無型別錯誤

## Further Reading

- [Error Handling — SvelteKit Official Docs](https://svelte.dev/docs/kit/error-handling)
- [Errors and Redirects — SvelteKit Official Docs](https://svelte.dev/docs/kit/errors-and-redirects)
- [Hooks — SvelteKit Official Docs](https://svelte.dev/docs/kit/hooks)
- [$app/state — SvelteKit Official Docs](https://svelte.dev/docs/kit/$app-state)
- [$app/navigation — SvelteKit Official Docs](https://svelte.dev/docs/kit/$app-navigation)
- [Project Structure (error.html) — SvelteKit Official Docs](https://svelte.dev/docs/kit/project-structure)
- [`<svelte:boundary>` — Svelte Official Docs](https://svelte.dev/docs/svelte/svelte-boundary)
