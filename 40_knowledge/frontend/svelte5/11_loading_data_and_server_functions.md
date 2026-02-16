---
title: "Loading Data and Server Functions / 資料載入與伺服器函式"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-17
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "11"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [10_sveltekit_project_bootstrap]
---
# Loading Data and Server Functions / 資料載入與伺服器函式

## Goal

掌握 SvelteKit 的資料載入機制，理解 universal load 與 server load 的差異，學會平行載入與資料失效策略。

資料載入是任何 web 應用的核心環節，SvelteKit 透過 `load` 函式提供了統一且型別安全的資料擷取模式。理解 universal load 與 server load 的差異、善用 `depends()` / `invalidate()` 失效機制，將讓你能建構出既安全又高效能的資料驅動頁面。

- **銜接上一章**：Ch10 建立了 SvelteKit 專案與路由，現在要讓頁面載入真正的資料。
- **下一章預告**：Ch12 將學習 form actions 處理資料變更（寫入操作）。

## Prerequisites

- 已完成第 10 章（SvelteKit Project Bootstrap）。
- 熟悉 SvelteKit 的檔案路由結構（`+page.svelte`、`+layout.svelte`）。
- 了解 TypeScript 基礎型別標註（Ch01）。
- 了解 JavaScript 非同步概念（`Promise`、`async/await`、`fetch`）。

## Core Concepts

### 1. Universal load (`+page.ts`) vs Server load (`+page.server.ts`)

SvelteKit 提供兩種 load function：

- **Universal load**（`+page.ts`）：在 server 與 client **都會執行**。首次請求時在 server 端執行（SSR），後續的 client-side navigation 時在 browser 端執行。適合不涉及機密的公開 API 資料載入。
- **Server load**（`+page.server.ts`）：**只在 server 端執行**，永遠不會將程式碼送到 client。適合存取資料庫、使用 API keys、處理 cookies 等機密操作。

```ts
// +page.ts — Universal load
// 這段程式碼會被打包到 client bundle 中！
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const res = await fetch('/api/posts');
  return { posts: await res.json() };
};
```

```ts
// +page.server.ts — Server load
// 這段程式碼永遠不會送到 client
import type { PageServerLoad } from './$types';
import { db } from '$lib/server/database';

export const load: PageServerLoad = async () => {
  const posts = await db.query('SELECT * FROM posts');
  return { posts };
};
```

| 何時用 Universal load (`+page.ts`) | 何時用 Server load (`+page.server.ts`) |
|---|---|
| 呼叫公開 API，不涉及機密 | 存取資料庫（DB query） |
| 需要在 client-side navigation 時重新載入資料 | 使用環境變數 / API keys |
| 回傳的資料需要包含不可序列化的值（如 component 建構子） | 處理 cookies / session |
| 需要用 `fetch` 以外的方式取得資料（如直接 import JSON） | 需要存取檔案系統 |

> **重要**：如果同一路由同時有 `+page.ts` 和 `+page.server.ts`，server load 的回傳值會作為 universal load 的 `data` 參數傳入。

### 2. Layout data sharing

`+layout.ts` / `+layout.server.ts` 的 load 結果會**自動傳給所有子路由**，不需要手動傳遞 props。

```ts
// src/routes/+layout.server.ts
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies }) => {
  const sessionId = cookies.get('session');
  return {
    user: sessionId ? { name: 'Alice' } : null
  };
};
```

子頁面可以直接在 `data` prop 中取得 layout data：

```svelte
<!-- src/routes/dashboard/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  // data.user 來自 layout load
</script>

<p>Welcome, {data.user?.name ?? 'Guest'}</p>
```

子 load 函式可透過 `await parent()` 取得父 layout 的 load 資料：

```ts
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ parent }) => {
  const { user } = await parent();
  // 可根據 user 決定要載入什麼資料
  return { dashboardData: user ? await fetchDashboard(user) : null };
};
```

| 何時在 layout 載入 | 何時在 page 載入 |
|---|---|
| 所有子頁面都需要的共用資料（如 user session、navigation items） | 只有該頁面需要的資料 |
| 資料變更頻率低 | 資料隨頁面不同而不同 |
| 需要在 layout UI 中顯示的資料 | 頁面特定的列表、詳情等 |

### 3. `PageData` typing and `data` prop

SvelteKit 自動從 load 函式的回傳值推斷型別，產生在 `.svelte-kit/types` 下的 `$types` 模組。

```ts
// src/routes/blog/+page.server.ts
import type { PageServerLoad } from './$types'; // 自動產生的型別

export const load: PageServerLoad = async () => {
  return {
    posts: [{ slug: 'hello', title: 'Hello' }],
    totalCount: 42
  };
};
```

```svelte
<!-- src/routes/blog/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types'; // 自動推斷出 { posts, totalCount }

  let { data }: { data: PageData } = $props();
  // data.posts — 型別為 { slug: string; title: string }[]
  // data.totalCount — 型別為 number
</script>
```

> **注意**：`$types` 是 SvelteKit 在開發時自動產生的虛擬模組。執行 `npm run dev` 或 `npm run build` 後才會產生。若 IDE 顯示 import 錯誤，先執行一次 dev server。

| 何時用 `$types` 自動推斷 | 何時不用 |
|---|---|
| 幾乎所有情況——預設都應該使用 | 幾乎沒有不用的理由 |
| SvelteKit 會自動保持型別同步 | 手動寫 `PageData` interface 會導致型別與實際 load 不一致 |

### 4. `depends()` / `invalidate()` / `invalidateAll()` — data revalidation

SvelteKit 提供精細的資料失效（revalidation）機制：

- **`depends(key)`**：在 load 函式中宣告對某個自訂 key 的依賴。
- **`invalidate(key)`**：在 client 端觸發重新執行所有依賴此 key 的 load 函式。
- **`invalidateAll()`**：重新執行所有 active load 函式。

```ts
// src/routes/todos/+page.server.ts
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends }) => {
  depends('app:todos'); // 宣告依賴

  const todos = await fetchTodos();
  return { todos };
};
```

```svelte
<!-- src/routes/todos/+page.svelte -->
<script lang="ts">
  import { invalidate } from '$app/navigation';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  async function addTodo(title: string) {
    await fetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify({ title }),
      headers: { 'Content-Type': 'application/json' }
    });
    // 觸發重新載入所有依賴 'app:todos' 的 load 函式
    await invalidate('app:todos');
  }
</script>
```

SvelteKit 預設也會追蹤 load 函式中 `fetch` 的 URL。當你呼叫 `invalidate(url)` 時，所有在 load 中 fetch 過該 URL 的 load 函式都會重新執行：

```ts
export const load: PageServerLoad = async ({ fetch }) => {
  // SvelteKit 自動追蹤此 URL
  const res = await fetch('/api/todos');
  return { todos: await res.json() };
};
```

```svelte
<script lang="ts">
  import { invalidate } from '$app/navigation';

  // 重新執行所有 fetch 過 '/api/todos' 的 load
  await invalidate('/api/todos');
</script>
```

| 何時用 custom dependency key（`app:*`） | 何時用 URL-based invalidation |
|---|---|
| 多個 load 共享同一組邏輯上的資料 | load 只是從某個 API endpoint 取資料 |
| 資料來源不是 URL（如 DB query） | 資料來源就是 fetch URL |
| 需要更語意化的 invalidation key | 簡單場景，不需要額外命名 |

### 5. Parallel loading patterns

SvelteKit **自動平行執行**同一路由層級的 layout load 與 page load。例如導航到 `/dashboard/settings` 時：

```
+layout.server.ts load()  ──┐
                             ├── 同時執行（parallel）
+page.server.ts load()   ──┘
```

**避免 waterfall 的關鍵**：不要在子 load 中先 `await parent()` 再發起自己的 fetch。這會把原本可以平行的載入變成瀑布式：

```ts
// 錯誤：造成 waterfall
export const load: PageServerLoad = async ({ parent, fetch }) => {
  const { user } = await parent(); // 等待 parent 完成
  const res = await fetch(`/api/posts?userId=${user.id}`); // 才開始 fetch
  return { posts: await res.json() };
};

// 正確：分離不依賴 parent 的 fetch
export const load: PageServerLoad = async ({ parent, fetch }) => {
  // 同時啟動所有非同步操作
  const [parentData, postsRes] = await Promise.all([
    parent(),
    fetch('/api/posts')  // 不依賴 parent 的 fetch 可以平行
  ]);

  return { posts: await postsRes.json() };
};
```

| 何時會自動平行 | 何時會變成 waterfall |
|---|---|
| layout load 與 page load 無 `await parent()` 依賴 | page load 中 `await parent()` 再 fetch |
| 使用 `Promise.all` 同時發起多個 fetch | 連續 `await` 多個 fetch |
| 善用 SvelteKit 的自動平行機制 | 不必要的資料依賴 |

## Step-by-step

### Step 1：建立 `+page.server.ts` 回傳 mock 資料

建立 `src/routes/blog/+page.server.ts`，寫一個 server load function 回傳部落格文章列表：

```ts
// src/routes/blog/+page.server.ts
import type { PageServerLoad } from './$types';

interface Post {
  slug: string;
  title: string;
  excerpt: string;
  publishedAt: string;
}

export const load: PageServerLoad = async () => {
  // 模擬資料庫查詢
  const posts: Post[] = [
    { slug: 'hello-world', title: 'Hello World', excerpt: 'My first post', publishedAt: '2026-02-14' },
    { slug: 'svelte-5', title: 'Svelte 5 is Amazing', excerpt: 'Why I love runes', publishedAt: '2026-02-13' },
  ];

  return { posts };
};
```

重點：`PageServerLoad` 型別確保 load 函式的參數和回傳值正確。回傳的物件必須是可序列化的（因為要從 server 傳到 client）。

### Step 2：在 `+page.svelte` 中用 `$props()` 接收資料

建立 `src/routes/blog/+page.svelte`，使用 Svelte 5 的 `$props()` 接收 load 資料：

```svelte
<!-- src/routes/blog/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
</script>

<h1>Blog</h1>
<ul>
  {#each data.posts as post (post.slug)}
    <li>
      <a href="/blog/{post.slug}">{post.title}</a>
      <p>{post.excerpt}</p>
      <time>{post.publishedAt}</time>
    </li>
  {/each}
</ul>
```

觀察：`data` 的型別由 SvelteKit 自動從 load 函式回傳值推斷。IDE 中 hover `data.posts` 可以看到完整的型別資訊。

### Step 3：加入 TypeScript 型別標註

確認 load 函式使用 `$types` 自動產生的型別：

```ts
// src/routes/blog/+page.server.ts
import type { PageServerLoad } from './$types'; // 自動產生

export const load: PageServerLoad = async () => {
  // 若回傳的物件結構不符合 PageServerLoad 的要求，TypeScript 會報錯
  return { posts: [] };
};
```

執行 `npx svelte-check` 確認型別正確：

```bash
npx svelte-check --tsconfig ./tsconfig.json
```

若看到 `$types` import 錯誤，確保已執行過 `npm run dev` 或 `npm run build` 至少一次。

### Step 4：建立 `+layout.server.ts` 分享 user session

建立根 layout 的 server load，將 user session 分享給所有路由：

```ts
// src/routes/+layout.server.ts
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies }) => {
  const sessionId = cookies.get('session');

  // 實際應用中會從 DB 查詢 session
  const user = sessionId
    ? { name: 'Alice', email: 'alice@example.com' }
    : null;

  return { user };
};
```

在任何子路由的 `+page.svelte` 中，`data` 會自動包含 layout load 的回傳值：

```svelte
<!-- src/routes/dashboard/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  // data.user 來自 +layout.server.ts
</script>

{#if data.user}
  <p>Hello, {data.user.name}!</p>
{:else}
  <p>Please log in.</p>
{/if}
```

### Step 5：建立 `+page.ts`（universal load）載入公開 API 資料

建立一個 universal load function，從公開 API 載入資料：

```ts
// src/routes/public/+page.ts
import type { PageLoad } from './$types';

interface GitHubRepo {
  id: number;
  name: string;
  description: string | null;
  stargazers_count: number;
}

export const load: PageLoad = async ({ fetch }) => {
  // 使用 SvelteKit 提供的 fetch（支援相對 URL 和 cookie forwarding）
  const res = await fetch('https://api.github.com/users/sveltejs/repos?sort=stars&per_page=5');

  if (!res.ok) {
    return { repos: [] as GitHubRepo[] };
  }

  const repos: GitHubRepo[] = await res.json();
  return { repos };
};
```

> **注意**：使用 load 函式參數中的 `fetch` 而不是全域 `fetch`。SvelteKit 提供的 `fetch` 會自動在 server 端轉換相對 URL、轉發 cookies、並追蹤 URL 依賴。

### Step 6：使用 `depends()` 和 `invalidate()` 實現資料重新載入

在 load 函式中宣告依賴，在元件中觸發失效：

```ts
// src/routes/todos/+page.server.ts
import type { PageServerLoad } from './$types';

let todoStore = [
  { id: 1, title: 'Learn SvelteKit', done: false },
  { id: 2, title: 'Build an app', done: false },
];

export const load: PageServerLoad = async ({ depends }) => {
  depends('app:todos'); // 宣告自訂依賴

  return { todos: [...todoStore] }; // 回傳副本
};
```

```svelte
<!-- src/routes/todos/+page.svelte -->
<script lang="ts">
  import { invalidate } from '$app/navigation';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  let newTitle = $state('');

  async function addTodo() {
    if (!newTitle.trim()) return;

    await fetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify({ title: newTitle }),
      headers: { 'Content-Type': 'application/json' }
    });

    newTitle = '';
    await invalidate('app:todos'); // 重新載入
  }
</script>

<form onsubmit={addTodo}>
  <input bind:value={newTitle} placeholder="New todo..." />
  <button type="submit">Add</button>
</form>

<ul>
  {#each data.todos as todo (todo.id)}
    <li>{todo.title}</li>
  {/each}
</ul>
```

### Step 7：觀察平行載入

建立同時有 layout load 和 page load 的路由，觀察它們平行執行：

```ts
// src/routes/dashboard/+layout.server.ts
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async () => {
  console.log('[layout] load start');
  await new Promise((r) => setTimeout(r, 500)); // 模擬 500ms 查詢
  console.log('[layout] load end');
  return { navItems: ['Home', 'Settings', 'Profile'] };
};
```

```ts
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
  console.log('[page] load start');
  await new Promise((r) => setTimeout(r, 500)); // 模擬 500ms 查詢
  console.log('[page] load end');
  return { stats: { views: 1234, likes: 56 } };
};
```

觀察 console 輸出：`[layout] load start` 和 `[page] load start` 幾乎同時出現——SvelteKit 自動平行執行它們。總耗時約 500ms 而非 1000ms。

### Step 8：使用 `error()` 處理載入錯誤

從 `@sveltejs/kit` 匯入 `error` helper 來拋出 HTTP 錯誤：

```ts
// src/routes/blog/[slug]/+page.server.ts
import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params }) => {
  const post = await findPost(params.slug);

  if (!post) {
    error(404, {
      message: 'Post not found'
    });
  }

  return { post };
};

async function findPost(slug: string) {
  const posts = [
    { slug: 'hello-world', title: 'Hello World', content: 'Welcome to my blog.' },
  ];
  return posts.find(p => p.slug === slug) ?? null;
}
```

SvelteKit 會自動渲染最近的 `+error.svelte` 元件：

```svelte
<!-- src/routes/+error.svelte -->
<script lang="ts">
  import { page } from '$app/state';
</script>

<h1>{page.status}</h1>
<p>{page.error?.message}</p>
```

## Hands-on Lab

### Foundation：部落格列表頁

建立 `src/routes/blog/+page.server.ts` 和 `src/routes/blog/+page.svelte`：

- 在 server load 中回傳 mock 部落格文章列表（至少 3 篇），每篇包含 `slug`、`title`、`excerpt`、`publishedAt`。
- 使用 `PageServerLoad` 型別標註 load 函式。
- 在 `+page.svelte` 中用 `let { data }: { data: PageData } = $props()` 接收資料。
- 使用 `{#each}` 渲染文章列表，以 `slug` 作為 key。
- 每篇文章顯示標題（連結到 `/blog/{slug}`）、摘要和發布日期。

驗收：頁面正確顯示文章列表，`npx svelte-check` 通過。

### Advanced：Layout data sharing

在 Foundation 基礎上加入：

- 建立 `src/routes/+layout.server.ts`，載入 user session 資料（從 cookies 讀取）。
- 建立 `src/routes/dashboard/+layout.svelte`，顯示側邊導覽列。
- 建立 `src/routes/dashboard/+page.server.ts`，使用 `parent()` 取得 user session。
- 根據 user 是否存在，顯示不同的 dashboard 內容。
- 建立 `src/routes/dashboard/settings/+page.svelte`，驗證 layout data 在子路由中也可用。

驗收：所有 dashboard 子路由都能取得 user session；layout 只 load 一次，不重複查詢。

### Challenge：即時資料失效模式

在 Advanced 基礎上加入：

- 建立 `src/routes/posts/+page.server.ts`，使用 `depends('app:posts')` 宣告依賴。
- 建立 mock API（`src/routes/api/posts/+server.ts`）支援 GET 和 POST。
- 在 `+page.svelte` 中建立新增文章表單。
- 表單提交後呼叫 POST API，成功後呼叫 `invalidate('app:posts')` 重新載入列表。
- 列表應立即更新，無需手動 reload。

驗收：新增文章後列表即時更新；開啟 DevTools Network 面板可以看到 invalidate 觸發了新的 load 請求。

## Reference Solution

### Blog page — server load

```ts
// src/routes/blog/+page.server.ts
import type { PageServerLoad } from './$types';

interface Post {
  slug: string;
  title: string;
  excerpt: string;
  publishedAt: string;
}

export const load: PageServerLoad = async () => {
  // In production, this would be a DB query
  const posts: Post[] = [
    { slug: 'hello-world', title: 'Hello World', excerpt: 'My first post', publishedAt: '2026-02-14' },
    { slug: 'svelte-5', title: 'Svelte 5 is Amazing', excerpt: 'Why I love runes', publishedAt: '2026-02-13' },
  ];

  return { posts };
};
```

### Blog page — component

```svelte
<!-- src/routes/blog/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
</script>

<h1>Blog</h1>
<ul>
  {#each data.posts as post (post.slug)}
    <li>
      <a href="/blog/{post.slug}">{post.title}</a>
      <p>{post.excerpt}</p>
    </li>
  {/each}
</ul>
```

### Root layout — session sharing

```ts
// src/routes/+layout.server.ts
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies }) => {
  const sessionId = cookies.get('session');
  return {
    user: sessionId ? { name: 'Alice', email: 'alice@example.com' } : null
  };
};
```

### Invalidation pattern

```ts
// src/routes/posts/+page.server.ts
import type { PageServerLoad } from './$types';

const posts = [
  { id: 1, title: 'First Post' },
  { id: 2, title: 'Second Post' },
];

export const load: PageServerLoad = async ({ depends }) => {
  depends('app:posts');
  return { posts: [...posts] };
};
```

```svelte
<!-- src/routes/posts/+page.svelte -->
<script lang="ts">
  import { invalidate } from '$app/navigation';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  let newTitle = $state('');

  async function createPost() {
    if (!newTitle.trim()) return;

    await fetch('/api/posts', {
      method: 'POST',
      body: JSON.stringify({ title: newTitle }),
      headers: { 'Content-Type': 'application/json' }
    });

    newTitle = '';
    await invalidate('app:posts');
  }
</script>

<h1>Posts</h1>

<form onsubmit={createPost}>
  <input bind:value={newTitle} placeholder="New post title..." />
  <button type="submit">Create</button>
</form>

<ul>
  {#each data.posts as post (post.id)}
    <li>{post.title}</li>
  {/each}
</ul>
```

## Common Pitfalls

### 1. 在 `+page.ts` 中放置機密資訊

Universal load（`+page.ts`）的程式碼會被打包到 client bundle 中。**API keys、DB 密碼、環境變數等機密資訊絕對不能放在 `+page.ts`**，應使用 `+page.server.ts`。

```ts
// 錯誤：+page.ts（client 看得到）
export const load: PageLoad = async ({ fetch }) => {
  const res = await fetch('https://api.example.com/data', {
    headers: { 'Authorization': 'Bearer sk-secret-key-12345' } // 洩漏！
  });
  return { data: await res.json() };
};

// 正確：+page.server.ts（只在 server 執行）
import { SECRET_API_KEY } from '$env/static/private';

export const load: PageServerLoad = async ({ fetch }) => {
  const res = await fetch('https://api.example.com/data', {
    headers: { 'Authorization': `Bearer ${SECRET_API_KEY}` }
  });
  return { data: await res.json() };
};
```

### 2. 在 `await parent()` 之後才發起 fetch（造成 waterfall）

```ts
// 錯誤：waterfall — layout load 完成 → parent() 完成 → 才開始 fetch
export const load: PageServerLoad = async ({ parent, fetch }) => {
  const { user } = await parent();
  const res = await fetch('/api/posts'); // 不依賴 user 的 fetch 被不必要地延遲
  return { posts: await res.json() };
};

// 正確：平行執行
export const load: PageServerLoad = async ({ parent, fetch }) => {
  const [{ user }, postsRes] = await Promise.all([
    parent(),
    fetch('/api/posts')
  ]);
  return { posts: await postsRes.json() };
};
```

### 3. 在 server load 中使用瀏覽器 API

`+page.server.ts` 只在 server 端執行，`window`、`document`、`localStorage` 等瀏覽器 API 不可用：

```ts
// 錯誤：server load 中使用 localStorage
export const load: PageServerLoad = async () => {
  const theme = localStorage.getItem('theme'); // ReferenceError: localStorage is not defined
  return { theme };
};

// 正確：使用 cookies 替代
export const load: PageServerLoad = async ({ cookies }) => {
  const theme = cookies.get('theme') ?? 'light';
  return { theme };
};
```

### 4. 手動宣告 `PageData` interface 而非使用 `$types`

```svelte
<script lang="ts">
  // 錯誤：手動宣告，容易與實際 load 回傳值不同步
  interface PageData {
    posts: { slug: string; title: string }[];
  }
  let { data }: { data: PageData } = $props();

  // 正確：使用 SvelteKit 自動產生的 $types
  import type { PageData } from './$types';
  let { data }: { data: PageData } = $props();
</script>
```

### 5. 使用全域 `fetch` 而非 load 參數中的 `fetch`

SvelteKit 在 load 函式中提供的 `fetch` 有幾個關鍵增強：

- **相對 URL 解析**：server 端也能使用 `/api/posts` 這類相對路徑。
- **Cookie 轉發**：server 端呼叫內部 API 時，會自動轉發使用者的 cookies。
- **依賴追蹤**：SvelteKit 追蹤 fetch 的 URL，支援 `invalidate(url)` 重新載入。

```ts
// 錯誤：使用全域 fetch
export const load: PageServerLoad = async () => {
  // 相對 URL 在 server 端會失敗
  // 不會轉發 cookies
  // 不支援 URL-based invalidation
  const res = await fetch('/api/posts');
  return { posts: await res.json() };
};

// 正確：使用參數中的 fetch
export const load: PageServerLoad = async ({ fetch }) => {
  const res = await fetch('/api/posts');
  return { posts: await res.json() };
};
```

### 6. 在 load 函式中回傳不可序列化的值

Server load 的回傳值需要通過網路從 server 傳到 client，因此必須是可序列化的。SvelteKit 支援 JSON 基本型別外加 `Date`、`BigInt`、`RegExp`、`Map`、`Set` 等（透過 devalue 序列化），但不支援函式、class instance 等：

```ts
// 錯誤：回傳不可序列化的值
export const load: PageServerLoad = async () => {
  return {
    getData: () => fetch('/api/data'), // 函式不可序列化
    connection: new DatabaseConnection(), // class instance 不可序列化
  };
};

// 正確：回傳可序列化的資料
export const load: PageServerLoad = async () => {
  const data = await fetch('/api/data').then(r => r.json());
  return { data };
};
```

## Remote Functions — 遠端函式（⚠️ Experimental）

> **實驗性功能**：Remote Functions 目前為 SvelteKit 實驗性功能，API 可能在未來版本變動。啟用前請確認已閱讀官方文件並了解風險。

### 概念 Concept

Remote Functions 是 SvelteKit 提供的一種新模式，允許你在 server-only 的模組中定義函式，然後**直接從 browser 端呼叫**。SvelteKit 會自動將 browser 端的呼叫轉換為 `fetch` 請求，在 server 端執行函式後回傳結果。這消除了手動建立 API endpoint 的需要。

Remote Functions 分為兩種：

- **`query`**：用於**讀取**資料（類似 GET 請求）。結果可被快取與去重。
- **`command`**：用於**寫入/變更**資料（類似 POST 請求）。每次呼叫都會實際執行。

```
Browser 端呼叫 getUser(id)
        │
        ▼  SvelteKit 自動產生 fetch POST
        │
Server 端執行 getUser(id)
        │
        ▼  回傳序列化結果
        │
Browser 端取得結果
```

### 啟用設定 Configuration

需要在 `svelte.config.js` 中同時啟用兩個實驗性選項：

```ts
/// file: svelte.config.js
/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    experimental: {
      remoteFunctions: true  // 啟用 remote functions
    }
  },
  compilerOptions: {
    experimental: {
      async: true  // 啟用元件內 await 語法（搭配 async SSR）
    }
  }
};

export default config;
```

> **注意**：`compilerOptions.experimental.async` 是可選的，僅在需要於元件內直接使用 `await` 表達式時才需要。若只用 `query` / `command` 搭配 `{#await}`，則不需要此選項。

### `query` — 遠端查詢

`query` 用於從 browser 端呼叫 server 函式來**讀取**資料。函式必須定義在 server-only 的模組中（檔案路徑包含 `.server`，或位於 `$lib/server/` 下）。

```ts
// src/lib/server/api.ts — 此檔案只在 server 端執行
import { query } from '$app/server';
import * as v from 'valibot';
import { db } from '$lib/server/database';

// 基本用法：'unchecked' 表示不驗證輸入（適合內部使用、簡單場景）
export const getUser = query('unchecked', async (id: string) => {
  const user = await db.findUser(id);
  return user;
});

// 使用 Standard Schema 驗證輸入（推薦用於接收使用者輸入的場景）
export const searchPosts = query(
  v.object({
    keyword: v.pipe(v.string(), v.minLength(1)),
    page: v.optional(v.pipe(v.number(), v.minValue(1)), 1)
  }),
  async ({ keyword, page }) => {
    return db.searchPosts(keyword, page);
  }
);
```

在 Svelte 元件中使用：

```svelte
<!-- src/routes/user/[id]/+page.svelte -->
<script lang="ts">
  import { getUser } from '$lib/server/api';

  let { data } = $props();

  // 方法 1：搭配 {#await}（不需要 async 編譯選項）
  const userPromise = getUser(data.userId);
</script>

{#await userPromise}
  <p>Loading user...</p>
{:then user}
  <h1>{user.name}</h1>
  <p>{user.email}</p>
{:catch error}
  <p>Failed to load user: {error.message}</p>
{/await}
```

### `query.batch` — 批次查詢解決 N+1 問題

當頁面上有多個元件各自呼叫同一個 `query`（例如列表中每一行都需要查詢天氣資料），SvelteKit 會自動將這些呼叫**批次合併為單一 fetch 請求**，在 server 端一次處理。

```ts
// src/lib/server/api.ts
import { query } from '$app/server';
import * as v from 'valibot';
import * as db from '$lib/server/database';

// query.batch：接收陣列，回傳 lookup 函式
export const getWeather = query.batch(
  v.string(),  // 驗證每個輸入為 string
  async (cityIds: string[]) => {
    // 一次查詢所有城市（而非 N 次個別查詢）
    const weather = await db.sql`
      SELECT * FROM weather WHERE city_id = ANY(${cityIds})
    `;
    const lookup = new Map(weather.map((w) => [w.city_id, w]));

    // 回傳 lookup 函式，SvelteKit 會用它解析每個個別呼叫
    return (cityId: string) => lookup.get(cityId);
  }
);
```

```svelte
<!-- src/routes/cities/+page.svelte -->
<script lang="ts">
  import { getWeather } from '$lib/server/api';

  let { data } = $props();
</script>

<!-- 每個 city 都呼叫 getWeather(city.id)，
     但 SvelteKit 會將它們合併為一次 batch 請求 -->
{#each data.cities as city (city.id)}
  {#await getWeather(city.id)}
    <p>{city.name}: loading...</p>
  {:then weather}
    <p>{city.name}: {weather?.temperature}°C</p>
  {/await}
{/each}
```

**batch 的執行流程**：

1. Browser 端多個元件呼叫 `getWeather('taipei')`、`getWeather('tokyo')`、`getWeather('seoul')`。
2. SvelteKit 收集同一批次的呼叫，合併為單一 HTTP 請求送到 server。
3. Server 端 callback 收到 `['taipei', 'tokyo', 'seoul']` 陣列，一次查詢。
4. 回傳的 lookup 函式被用來解析每個個別呼叫的結果。

### `command` — 遠端命令（寫入操作）

`command` 用於**寫入或變更**資料，每次呼叫都會實際執行（不會被快取或去重）：

```ts
// src/lib/server/api.ts
import { command } from '$app/server';
import * as v from 'valibot';
import { db } from '$lib/server/database';

// 無參數的 command
export const clearCache = command(async () => {
  await db.clearCache();
  return { success: true };
});

// 帶驗證的 command
export const createPost = command(
  v.object({
    title: v.pipe(v.string(), v.minLength(1), v.maxLength(200)),
    content: v.string(),
    published: v.optional(v.boolean(), false)
  }),
  async ({ title, content, published }) => {
    const post = await db.createPost({ title, content, published });
    return post;
  }
);
```

```svelte
<!-- src/routes/posts/new/+page.svelte -->
<script lang="ts">
  import { createPost } from '$lib/server/api';
  import { goto } from '$app/navigation';

  let title = $state('');
  let content = $state('');
  let submitting = $state(false);

  async function handleSubmit() {
    submitting = true;
    try {
      const post = await createPost({ title, content, published: true });
      await goto(`/posts/${post.slug}`);
    } catch (err) {
      console.error('Failed to create post:', err);
    } finally {
      submitting = false;
    }
  }
</script>

<form onsubmit|preventDefault={handleSubmit}>
  <input bind:value={title} placeholder="Title" />
  <textarea bind:value={content} placeholder="Content"></textarea>
  <button type="submit" disabled={submitting}>
    {submitting ? 'Creating...' : 'Create Post'}
  </button>
</form>
```

### 表單 Remote Functions — Form Remote Functions

Remote Functions 也可以搭配 `<form>` 的 progressive enhancement。使用 `command` 時，可作為 form action 的替代方案，同時保留在 JavaScript 停用時也能運作的能力（fallback 到傳統 form submit）。

### Lazy Discovery — 延遲探索

Remote Functions 使用 **lazy discovery** 機制。SvelteKit 不會在 build 時預先產生所有 remote function 的 endpoint。當 browser 端首次呼叫某個 remote function 時，SvelteKit 才會建立對應的 HTTP endpoint。這意味著：

- 未被使用的 remote function 不會佔用任何 server 資源。
- 新增 remote function 不需要重新 build。
- endpoint URL 是自動產生的，不需手動管理路由。

### 安全注意事項 Security Notes

1. **永遠驗證輸入**：雖然 `'unchecked'` 方便快速開發，正式環境應使用 Standard Schema（如 Valibot、Zod）驗證所有輸入：
   ```ts
   // 不建議在正式環境使用
   export const dangerousQuery = query('unchecked', async (input: any) => { ... });

   // 推薦：使用 schema 驗證
   export const safeQuery = query(v.string(), async (id) => { ... });
   ```
2. **server-only 模組**：Remote function 必須定義在 server-only 模組中（`.server.ts` 檔案或 `$lib/server/` 目錄）。若放在可被 client 存取的模組中，build 時會報錯。
3. **授權檢查**：Remote function 不會自動檢查使用者權限。你必須在函式內部自行驗證（例如從 cookies 中取得 session）。
4. **回傳值必須可序列化**：與 `load` 函式相同，回傳值需通過網路傳輸，必須是可序列化的（支援 JSON 基本型別 + `Date`、`Map`、`Set` 等 devalue 支援的型別）。

### `query` vs `command` vs `load` function 比較

| 特性 | `query` | `command` | `load` function |
|------|---------|-----------|-----------------|
| 用途 | 讀取資料 | 寫入/變更資料 | 頁面載入時取得資料 |
| 呼叫方式 | 元件內直接呼叫 | 元件內直接呼叫 | SvelteKit 路由系統自動呼叫 |
| 快取/去重 | 可快取、可去重 | 每次實際執行 | 由 SvelteKit 管理 |
| batch 支援 | `query.batch` | 不支援 | 不適用 |
| 輸入驗證 | Standard Schema / `'unchecked'` | Standard Schema / `'unchecked'` | 由路由參數定義 |
| 適合場景 | 元件級資料取得、互動式查詢 | 表單提交、狀態變更 | 頁面級初始資料載入 |

| 何時用 Remote Functions | 何時用傳統 `load` / form actions |
|---|---|
| 元件需要自行取得資料，不適合在 page load 中集中載入 | 頁面初始載入的主要資料 |
| 需要 batch 解決 N+1 問題 | 資料在 SSR 時就需要完成載入（SEO 考量） |
| 互動式查詢（搜尋、篩選、無限捲動） | 需要與 SvelteKit 的 `invalidate` 機制整合 |
| 想減少 API endpoint 的手動管理 | 不想啟用實驗性功能 |

### Remote Functions 常見陷阱

1. **忘記啟用實驗性選項**：需要同時在 `kit.experimental.remoteFunctions` 和（可選）`compilerOptions.experimental.async` 中啟用。
2. **將 remote function 放在非 server-only 模組中**：會導致 server 程式碼被打包到 client bundle，build 時報錯。
3. **在 `query` 中執行副作用**：`query` 可能被快取或去重，副作用可能不會每次都執行。寫入操作應使用 `command`。
4. **未處理錯誤**：Remote function 的錯誤會以 Promise rejection 的形式傳到 browser 端，務必使用 `try/catch` 或 `{:catch}` 處理。
5. **過度使用 `'unchecked'`**：在正式環境中，未驗證的輸入是安全隱患。建議統一使用 Standard Schema 驗證。

## Checklist

- [ ] 能建立 `+page.server.ts` 的 server load function 並使用 `PageServerLoad` 型別
- [ ] 能建立 `+page.ts` 的 universal load function 並使用 `PageLoad` 型別
- [ ] 能建立 `+layout.server.ts` 分享 session / 共用資料給所有子路由
- [ ] 能使用 `depends()` 宣告自訂依賴、`invalidate()` 觸發資料重新載入
- [ ] 能解釋 server load 與 universal load 的執行環境差異及選用時機
- [ ] 能識別並避免 `await parent()` 造成的 data loading waterfall
- [ ] 能使用 `error()` helper 拋出 HTTP 錯誤並渲染 `+error.svelte`
- [ ] 能啟用 Remote Functions 實驗性選項並建立 `query` / `command`（⚠️ Experimental）
- [ ] 能使用 `query.batch` 解決元件級 N+1 資料查詢問題（⚠️ Experimental）
- [ ] `npx svelte-check` 通過，無型別錯誤

## Further Reading

- [Loading data — SvelteKit](https://svelte.dev/docs/kit/load)
- [Universal vs server — SvelteKit](https://svelte.dev/docs/kit/load#Universal-vs-server)
- [Invalidation — SvelteKit](https://svelte.dev/docs/kit/load#Rerunning-load-functions-Manual-invalidation)
- [$app/navigation: invalidate — SvelteKit](https://svelte.dev/docs/kit/$app-navigation#invalidate)
- [$app/navigation: invalidateAll — SvelteKit](https://svelte.dev/docs/kit/$app-navigation#invalidateAll)
- [Error handling — SvelteKit](https://svelte.dev/docs/kit/errors)
- [$types — SvelteKit](https://svelte.dev/docs/kit/$types)
- [Remote Functions (Experimental) — SvelteKit](https://svelte.dev/docs/kit/remote-functions)
- [$app/server: query / command — SvelteKit](https://svelte.dev/docs/kit/$app-server)
