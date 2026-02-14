---
title: "Form Actions and Data Mutations / 表單動作與資料變更"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "12"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [11_loading_data_and_server_functions]
---
# Form Actions and Data Mutations / 表單動作與資料變更

## Goal

掌握 SvelteKit 的 form actions 機制，用 progressive enhancement 處理資料變更操作。

Form actions 是 SvelteKit 處理資料寫入的核心機制，它以標準 HTML `<form>` 為基礎，搭配 `use:enhance` 實現 progressive enhancement，確保即使 JavaScript 失效也能正常運作。學會 `fail()` 驗證回饋、`ActionData` 型別推斷與 optimistic UI 模式後，你將能建構出健壯且使用者友善的資料變更流程。

- **銜接上一章**：Ch11 學會了資料載入（讀取），現在要處理資料變更（寫入）。
- **下一章預告**：Ch13 將學習 SSR、streaming 與頁面渲染選項。

## Prerequisites

- 已完成第 11 章（Loading Data and Server Functions），理解 `+page.server.ts` 的 `load` 函式與 `PageServerLoad` 型別。
- 熟悉 HTTP 表單的基本概念（`method="POST"`、`FormData`）。
- `svelte5-lab` 專案可正常執行 `npm run dev`。

## Core Concepts

### 1. `+page.server.ts` actions — default 與 named actions

SvelteKit 的 form actions 定義在 `+page.server.ts` 中，透過匯出 `actions` 物件來處理表單提交。每個 action 是一個接收 `RequestEvent` 的非同步函式。

**Default action**：頁面只有一個表單操作時使用。

```ts
// src/routes/login/+page.server.ts
import type { Actions } from './$types';

export const actions: Actions = {
  default: async ({ request }) => {
    const formData = await request.formData();
    const email = formData.get('email')?.toString();
    // ... 處理登入邏輯
  }
};
```

**Named actions**：頁面有多個不同操作的表單時使用。表單透過 `action="?/actionName"` 指定要呼叫的 action。

```ts
// src/routes/todos/+page.server.ts
import type { Actions } from './$types';

export const actions: Actions = {
  create: async ({ request }) => {
    const formData = await request.formData();
    // ... 建立 todo
  },
  delete: async ({ request }) => {
    const formData = await request.formData();
    // ... 刪除 todo
  }
};
```

```svelte
<!-- 表單透過 action 屬性指定 named action -->
<form method="POST" action="?/create">...</form>
<form method="POST" action="?/delete">...</form>
```

| 何時用 default action | 何時用 named actions |
|---|---|
| 頁面只有一個表單操作 | 頁面有多個不同操作的表單 |
| 簡單的登入/註冊頁面 | Todo 清單（建立、刪除、切換完成狀態） |
| 單一 contact form | 設定頁面（更新個人資料、更改密碼、刪除帳號） |

### 2. `use:enhance` — progressive enhancement

`use:enhance` 是 SvelteKit 提供的 Svelte action，來自 `$app/forms`。加上後，表單提交改用 `fetch` 而非傳統的整頁刷新，同時自動處理 `ActionData` 更新與頁面失效重新載入。

```svelte
<script lang="ts">
  import { enhance } from '$app/forms';
</script>

<!-- 加上 use:enhance：用 fetch 提交，無整頁刷新 -->
<form method="POST" action="?/create" use:enhance>
  <input name="text" />
  <button type="submit">Add</button>
</form>
```

不加 `use:enhance` 的表單仍然可以正常運作（graceful degradation），這正是 progressive enhancement 的精髓 — JavaScript 禁用或載入失敗時，表單仍可透過傳統 POST 請求完成操作。

| 何時用 `use:enhance` | 何時不用 |
|---|---|
| 所有 form actions（建議預設加上） | 需要完全自訂 fetch 行為（改用自己的 fetch 邏輯） |
| 希望提交後不刷新整頁 | 有意讓表單以傳統方式提交（例如檔案下載） |
| 需要 loading 狀態、成功/失敗 callback | 表單提交後要導向外部網址 |

### 3. `fail()` / `ActionData` / 自訂 enhance callback

**`fail()`**：回傳帶 HTTP 狀態碼的錯誤資料，讓表單可以顯示驗證錯誤而不跳到錯誤頁面。

```ts
import { fail } from '@sveltejs/kit';

export const actions: Actions = {
  default: async ({ request }) => {
    const formData = await request.formData();
    const email = formData.get('email')?.toString().trim();

    if (!email) {
      return fail(400, { email, missing: true });
    }

    if (!email.includes('@')) {
      return fail(400, { email, invalid: true });
    }

    // ... 成功處理
    return { success: true };
  }
};
```

**`ActionData`**：action 的回傳值會自動傳到頁面元件的 `form` prop 中，型別由 SvelteKit 從 actions 定義自動推斷。

```svelte
<script lang="ts">
  import type { ActionData } from './$types';

  let { form }: { form: ActionData } = $props();
</script>

{#if form?.missing}
  <p class="error">Email is required.</p>
{/if}
{#if form?.invalid}
  <p class="error">Email is invalid.</p>
{/if}
```

**自訂 enhance callback**：可傳入函式控制 loading 狀態與提交後的行為。

```svelte
<script lang="ts">
  import { enhance } from '$app/forms';

  let loading = $state(false);
</script>

<form
  method="POST"
  use:enhance={() => {
    loading = true;
    return async ({ update }) => {
      await update();
      loading = false;
    };
  }}
>
  <button disabled={loading}>
    {loading ? 'Saving...' : 'Save'}
  </button>
</form>
```

| 何時用 `fail()` | 何時用 `throw error()` |
|---|---|
| 表單驗證失敗，需要回傳錯誤訊息讓使用者修正 | 嚴重錯誤（404 找不到資源、403 無權限） |
| 使用者輸入不合法（缺少必填欄位、格式錯誤） | 伺服器內部錯誤、資料庫連線失敗 |
| 需要保留使用者已輸入的資料 | 要顯示完整的錯誤頁面 |

### 4. `redirect()` — mutation 後重導向

在 action 成功處理後，常見的模式是重導向到另一個頁面（Post-Redirect-Get, PRG pattern），避免使用者重新整理時重複提交表單。

```ts
import { redirect } from '@sveltejs/kit';

export const actions: Actions = {
  create: async ({ request }) => {
    const formData = await request.formData();
    const title = formData.get('title')?.toString().trim();

    // ... 驗證與建立資源
    const newPost = await db.createPost({ title });

    // 成功後重導向到新建立的資源頁面
    redirect(303, `/posts/${newPost.id}`);
  }
};
```

> **注意**：`redirect()` 在 SvelteKit 中使用 `throw` 語義 — 呼叫後會立即中止 action 執行並發出重導向回應。狀態碼 303（See Other）是 POST 後重導向的標準選擇。

| 何時用 `redirect()` | 何時不用 |
|---|---|
| 成功建立資源後導到新頁面（PRG pattern） | 留在同頁顯示操作結果 |
| 登入成功後導到 dashboard | 表單驗證失敗（應用 `fail()` 留在原頁） |
| 刪除資源後導回列表頁 | 需要向使用者顯示成功訊息後才跳轉 |

## Step-by-step

### Step 1：建立 todo 表單與 default action

建立 `src/routes/todos/+page.server.ts`，匯出一個包含 `default` action 的 `actions` 物件：

```ts
// src/routes/todos/+page.server.ts
import type { Actions } from './$types';

let todos = [
  { id: '1', text: 'Learn SvelteKit', done: false },
];

export const actions: Actions = {
  default: async ({ request }) => {
    const formData = await request.formData();
    const text = formData.get('text')?.toString().trim();

    if (!text) {
      return { error: 'Todo text is required.' };
    }

    todos.push({ id: crypto.randomUUID(), text, done: false });
    return { success: true };
  }
};
```

重點：`actions` 物件中的每個 key 就是一個 action 名稱，`default` 是當表單沒有指定 `action` 屬性時的預設目標。

### Step 2：使用 `request.formData()` 解析表單資料

action 的參數中 `request` 是標準的 Web `Request` 物件，透過 `formData()` 方法取得表單欄位：

```ts
export const actions: Actions = {
  default: async ({ request }) => {
    const formData = await request.formData();

    // formData.get() 回傳 FormDataEntryValue | null
    const text = formData.get('text');       // string | File | null
    const count = formData.get('count');     // string | File | null

    // 安全地轉為字串
    const textStr = text?.toString().trim() ?? '';
    const countNum = Number(count) || 0;
  }
};
```

重點：`formData.get()` 回傳的是 `FormDataEntryValue | null`（可能是 `string` 或 `File`），需要用 `.toString()` 轉為字串，或用 `Number()` 轉為數字。

### Step 3：使用 `fail()` 回傳驗證錯誤

引入 `fail` 函式，在驗證失敗時回傳帶 HTTP 狀態碼的錯誤資料：

```ts
import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
  default: async ({ request }) => {
    const formData = await request.formData();
    const text = formData.get('text')?.toString().trim();

    if (!text) {
      return fail(400, { text: '', error: 'Todo text is required.' });
    }

    if (text.length < 2) {
      return fail(400, { text, error: 'Todo must be at least 2 characters.' });
    }

    // ... 建立 todo
    return { success: true };
  }
};
```

重點：`fail(statusCode, data)` 的第二個參數會傳到頁面元件的 `form` prop。將使用者已輸入的值（如 `text`）一起回傳，可在表單中保留使用者的輸入。

### Step 4：在表單加上 `use:enhance`

在 `+page.svelte` 中引入 `enhance` 並加到表單上：

```svelte
<script lang="ts">
  import { enhance } from '$app/forms';
</script>

<form method="POST" use:enhance>
  <input name="text" placeholder="Add a todo..." />
  <button type="submit">Add</button>
</form>
```

重點：只需要 `import { enhance } from '$app/forms'` 然後在 `<form>` 標籤加上 `use:enhance`。SvelteKit 會自動攔截表單提交、用 fetch 發送請求、更新 `form` prop 與重新執行 `load` 函式。

### Step 5：顯示 `ActionData` 錯誤訊息

在頁面元件中透過 `$props()` 取得 `form` prop，並根據回傳的資料顯示錯誤：

```svelte
<script lang="ts">
  import { enhance } from '$app/forms';
  import type { PageData, ActionData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();
</script>

<form method="POST" use:enhance>
  <input name="text" value={form?.text ?? ''} placeholder="Add a todo..." />
  <button type="submit">Add</button>
  {#if form?.error}
    <p class="error" role="alert">{form.error}</p>
  {/if}
</form>
```

重點：`form` prop 在頁面首次載入時為 `null`，只有在 action 被呼叫後才會有值。使用 `form?.error` 安全存取。`value={form?.text ?? ''}` 可在驗證失敗時保留使用者的輸入。

### Step 6：加入 named actions — `create` 和 `delete`

將 `default` action 拆分為多個 named actions：

```ts
export const actions: Actions = {
  create: async ({ request }) => {
    const formData = await request.formData();
    const text = formData.get('text')?.toString().trim();
    if (!text) return fail(400, { text, error: 'Todo text is required.' });

    todos.push({ id: crypto.randomUUID(), text, done: false });
    return { success: true };
  },

  delete: async ({ request }) => {
    const formData = await request.formData();
    const id = formData.get('id')?.toString();
    if (!id) return fail(400, { error: 'Missing todo ID.' });

    todos = todos.filter(t => t.id !== id);
    return { success: true };
  }
};
```

重點：從 `default` 改為 named actions 後，表單必須加上 `action="?/actionName"` 指定要呼叫的 action。

### Step 7：使用 `action="?/delete"` 搭配 hidden input 傳遞 ID

在模板中為每個 todo 項目建立刪除表單：

```svelte
<ul>
  {#each data.todos as todo (todo.id)}
    <li>
      <span>{todo.text}</span>
      <form method="POST" action="?/delete" use:enhance style="display:inline">
        <input type="hidden" name="id" value={todo.id} />
        <button type="submit" aria-label="Delete {todo.text}">x</button>
      </form>
    </li>
  {/each}
</ul>
```

重點：每個刪除按鈕都是一個獨立的 `<form>`，透過 `<input type="hidden">` 帶入該 todo 的 `id`。`action="?/delete"` 指定呼叫 `delete` action。

### Step 8：自訂 enhance callback 顯示 loading 狀態

傳入函式給 `use:enhance`，控制提交前後的行為：

```svelte
<script lang="ts">
  import { enhance } from '$app/forms';
  import type { PageData, ActionData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();
  let creating = $state(false);
</script>

<form
  method="POST"
  action="?/create"
  use:enhance={() => {
    creating = true;
    return async ({ update }) => {
      await update();
      creating = false;
    };
  }}
>
  <input name="text" value={form?.text ?? ''} disabled={creating} />
  <button type="submit" disabled={creating}>
    {creating ? 'Adding...' : 'Add'}
  </button>
  {#if form?.error}
    <p class="error" role="alert">{form.error}</p>
  {/if}
</form>
```

重點：`use:enhance` 接受一個 submit function，在表單提交前執行（設定 loading 狀態），並回傳一個函式在收到回應後執行（清除 loading 狀態）。`update()` 會執行預設的更新行為（更新 `form` prop、重新執行 `load` 函式等）。

## Hands-on Lab

### Foundation：Todo 建立與表單驗證

**任務：建立一個 todo 應用，支援新增功能與表單驗證。**

1. 建立 `src/routes/todos/+page.server.ts`，匯出 `load` 函式回傳 todo 清單，以及包含 `create` action 的 `actions`。
2. 在 `create` action 中驗證輸入：不可為空、至少 2 個字元。驗證失敗時使用 `fail()` 回傳錯誤。
3. 建立 `src/routes/todos/+page.svelte`，顯示 todo 清單與新增表單。
4. 加上 `use:enhance`，在表單中顯示 `ActionData` 的錯誤訊息。

**驗收條件：**
- 提交空白表單時顯示 "Todo text is required." 錯誤。
- 提交少於 2 字元時顯示 "Todo must be at least 2 characters." 錯誤。
- 成功新增後清單即時更新，不需整頁刷新。
- 驗證失敗時保留使用者已輸入的文字。

### Advanced：Named actions 與完整 CRUD

**任務：擴充 todo 應用，加入 delete 和 toggle 操作。**

1. 新增 `delete` named action：透過 hidden input 取得 todo id，從清單中移除。
2. 新增 `toggle` named action：切換 todo 的完成狀態。
3. 每個操作都使用 `fail()` 處理找不到 todo 的情況。
4. 所有表單都加上 `use:enhance`。

**驗收條件：**
- 可以刪除任何 todo 項目。
- 可以點擊 todo 文字切換完成/未完成狀態，完成的項目顯示刪除線。
- 對不存在的 todo 操作時回傳 `fail(404, ...)`。
- TypeScript 型別完整，無 `any`。

### Challenge：Optimistic UI 與 rollback

**任務：實作自訂 `use:enhance` callback，加入 optimistic UI 更新與失敗回滾。**

1. 在 `delete` action 中自訂 enhance callback：提交前立即從本地清單移除 todo（optimistic update）。
2. 若 server 回傳錯誤，自動將 todo 加回原本的位置（rollback）。
3. 在 `toggle` action 中實作相同的 optimistic UI 模式。
4. 加入 loading spinner 或 disabled 狀態，防止重複提交。

**驗收條件：**
- 刪除/切換操作立即反映在 UI 上（不等 server 回應）。
- Server 錯誤時 UI 自動回滾到操作前的狀態。
- 操作期間按鈕顯示 disabled 或 loading 狀態。
- `npx svelte-check` 通過。

## Reference Solution

### +page.server.ts — Server-side actions

```ts
// src/routes/todos/+page.server.ts
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

interface Todo {
  id: string;
  text: string;
  done: boolean;
}

// In-memory store (replace with DB in production)
let todos: Todo[] = [
  { id: '1', text: 'Learn SvelteKit', done: false },
  { id: '2', text: 'Build an app', done: false },
];

export const load: PageServerLoad = async () => {
  return { todos: structuredClone(todos) };
};

export const actions: Actions = {
  create: async ({ request }) => {
    const formData = await request.formData();
    const text = formData.get('text')?.toString().trim();

    if (!text) {
      return fail(400, { text, error: 'Todo text is required.' });
    }

    if (text.length < 2) {
      return fail(400, { text, error: 'Todo must be at least 2 characters.' });
    }

    todos.push({ id: crypto.randomUUID(), text, done: false });
    return { success: true };
  },

  delete: async ({ request }) => {
    const formData = await request.formData();
    const id = formData.get('id')?.toString();

    if (!id) return fail(400, { error: 'Missing todo ID.' });

    todos = todos.filter(t => t.id !== id);
    return { success: true };
  },

  toggle: async ({ request }) => {
    const formData = await request.formData();
    const id = formData.get('id')?.toString();

    const todo = todos.find(t => t.id === id);
    if (!todo) return fail(404, { error: 'Todo not found.' });

    todo.done = !todo.done;
    return { success: true };
  }
};
```

### +page.svelte — Client-side form with progressive enhancement

```svelte
<!-- src/routes/todos/+page.svelte -->
<script lang="ts">
  import { enhance } from '$app/forms';
  import type { PageData, ActionData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();
</script>

<h1>Todos</h1>

<form method="POST" action="?/create" use:enhance>
  <input name="text" value={form?.text ?? ''} placeholder="Add a todo..." />
  <button type="submit">Add</button>
  {#if form?.error}
    <p class="error" role="alert">{form.error}</p>
  {/if}
</form>

<ul>
  {#each data.todos as todo (todo.id)}
    <li>
      <form method="POST" action="?/toggle" use:enhance style="display:inline">
        <input type="hidden" name="id" value={todo.id} />
        <button type="submit" class:done={todo.done}>
          {todo.text}
        </button>
      </form>
      <form method="POST" action="?/delete" use:enhance style="display:inline">
        <input type="hidden" name="id" value={todo.id} />
        <button type="submit" aria-label="Delete {todo.text}">x</button>
      </form>
    </li>
  {/each}
</ul>

<style>
  .done { text-decoration: line-through; opacity: 0.6; }
  .error { color: red; }
</style>
```

### Optimistic UI enhance callback

```svelte
<!-- src/routes/todos/+page.svelte（Challenge 版本 — optimistic delete） -->
<script lang="ts">
  import { enhance } from '$app/forms';
  import type { PageData, ActionData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();
  let deletingId = $state<string | null>(null);
</script>

{#each data.todos as todo (todo.id)}
  <li class:deleting={deletingId === todo.id}>
    <span class:done={todo.done}>{todo.text}</span>
    <form
      method="POST"
      action="?/delete"
      use:enhance={() => {
        deletingId = todo.id;

        return async ({ result, update }) => {
          if (result.type === 'success') {
            await update();
          } else {
            // Rollback：server 錯誤時恢復顯示
            deletingId = null;
          }
        };
      }}
      style="display:inline"
    >
      <input type="hidden" name="id" value={todo.id} />
      <button type="submit" disabled={deletingId === todo.id}>
        {deletingId === todo.id ? '...' : 'x'}
      </button>
    </form>
  </li>
{/each}

<style>
  .deleting { opacity: 0.4; pointer-events: none; }
  .done { text-decoration: line-through; opacity: 0.6; }
</style>
```

## Common Pitfalls

### 1. 忘記在 `<form>` 加上 `method="POST"`

Form actions 只接受 POST 請求。如果省略 `method="POST"`，表單預設使用 GET，SvelteKit 不會執行 action。

```svelte
<!-- 錯誤：預設是 GET，action 不會被呼叫 -->
<form action="?/create">
  <input name="text" />
  <button>Add</button>
</form>

<!-- 正確：明確指定 POST -->
<form method="POST" action="?/create">
  <input name="text" />
  <button>Add</button>
</form>
```

### 2. 沒有加 `use:enhance` — 表單會整頁刷新

不加 `use:enhance` 時表單仍然可以運作，但每次提交都會觸發完整的頁面重新載入（傳統 HTML form 行為）。這不是 bug，但通常不是你想要的體驗。

```svelte
<!-- 可運作，但每次提交都會整頁刷新 -->
<form method="POST" action="?/create">...</form>

<!-- 加上 use:enhance，改用 fetch 提交 -->
<form method="POST" action="?/create" use:enhance>...</form>
```

建議預設總是加上 `use:enhance`。只有在特殊需求（如檔案下載觸發）時才考慮省略。

### 3. 用 `throw error()` 處理表單驗證錯誤

`error()` 會讓 SvelteKit 渲染錯誤頁面（`+error.svelte`），使用者離開了表單。`fail()` 則是回傳資料到原頁面，讓使用者可以修正輸入。

```ts
import { error, fail } from '@sveltejs/kit';

export const actions: Actions = {
  default: async ({ request }) => {
    const formData = await request.formData();
    const text = formData.get('text')?.toString().trim();

    // 錯誤：使用者看到錯誤頁面，無法修正輸入
    if (!text) throw error(400, 'Text is required');

    // 正確：回傳錯誤資料到表單，使用者可以修正
    if (!text) return fail(400, { error: 'Text is required' });
  }
};
```

經驗法則：使用者可修正的錯誤用 `fail()`，系統層級的錯誤用 `error()`。

### 4. 假設 form data 是 JSON

HTML 表單提交的資料是 `multipart/form-data` 或 `application/x-www-form-urlencoded`，不是 JSON。必須用 `request.formData()` 解析，不能用 `request.json()`。

```ts
export const actions: Actions = {
  default: async ({ request }) => {
    // 錯誤：form submission 不是 JSON
    const data = await request.json();

    // 正確：使用 formData() 解析
    const formData = await request.formData();
    const text = formData.get('text')?.toString();
  }
};
```

### 5. 忘記在模板中使用 `form` prop 顯示錯誤

Action 回傳的資料需要在頁面元件中透過 `form` prop 接收並顯示，否則使用者看不到驗證錯誤。

```svelte
<script lang="ts">
  import type { ActionData } from './$types';

  // 錯誤：忘記從 $props() 取得 form
  let { data } = $props();

  // 正確：取出 form prop
  let { data, form }: { data: PageData; form: ActionData } = $props();
</script>

<!-- 然後在模板中顯示錯誤 -->
{#if form?.error}
  <p class="error">{form.error}</p>
{/if}
```

### 6. 在 named action 頁面中省略 `action` 屬性

當 `actions` 物件中沒有 `default` key 時，表單必須透過 `action` 屬性指定要呼叫的 named action，否則 SvelteKit 會回傳 405 Method Not Allowed。

```svelte
<!-- 若 actions = { create, delete } 而沒有 default -->

<!-- 錯誤：沒有 default action，會得到 405 -->
<form method="POST">...</form>

<!-- 正確：指定 named action -->
<form method="POST" action="?/create">...</form>
```

## Checklist

- [ ] 能建立 default 與 named form actions
- [ ] 能驗證表單資料並用 `fail()` 回傳錯誤
- [ ] 能在表單中透過 `form` prop 顯示 action 錯誤訊息
- [ ] 能使用 `use:enhance` 實現 progressive enhancement
- [ ] 能使用 `redirect()` 在 mutation 後重導向
- [ ] 能解釋 PRG（Post-Redirect-Get）pattern 的目的與運作方式
- [ ] 能自訂 `use:enhance` callback 控制 loading 狀態
- [ ] `npx svelte-check` 通過，無型別錯誤

## Further Reading

- [Form Actions](https://svelte.dev/docs/kit/form-actions) -- SvelteKit form actions 完整 API 與使用指南。
- [$app/forms — enhance](https://svelte.dev/docs/kit/$app-forms) -- `enhance` action 與 `applyAction`、`deserialize` 工具函式。
- [fail](https://svelte.dev/docs/kit/@sveltejs-kit#fail) -- `fail()` 函式 API 參考。
- [redirect](https://svelte.dev/docs/kit/@sveltejs-kit#redirect) -- `redirect()` 函式 API 參考。
- [Loading Data](https://svelte.dev/docs/kit/load) -- `load` 函式與 form actions 的互動（action 後自動重跑 load）。
- [Tutorial — Form Actions](https://svelte.dev/tutorial/kit/the-form-element) -- 官方互動教學。
