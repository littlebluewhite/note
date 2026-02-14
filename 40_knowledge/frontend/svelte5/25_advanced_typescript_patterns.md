---
title: "Advanced TypeScript Patterns / 進階 TypeScript 模式"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "25"
level: advanced
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [08_snippets_and_component_composition, 11_loading_data_and_server_functions]
---
# Advanced TypeScript Patterns / 進階 TypeScript 模式

## Goal

掌握 Svelte 5 中的進階 TypeScript 模式，建立型別安全的元件庫與 API 介面，善用 SvelteKit 的自動型別推導與泛型元件設計。

TypeScript 在 Svelte 5 中的支援已經非常成熟。透過 `generics` 屬性、`Snippet<[T]>` 型別、SvelteKit 的自動型別生成（`$types`），你可以建立完全型別安全的元件庫。本章將探討泛型元件的進階用法、discriminated unions 模式、polymorphic 元件設計，以及 CI 中的型別檢查整合。

- 銜接上一章：Ch08 學會了泛型元件基礎（`generics="T"` + `Snippet<[T]>`），Ch11 學會了 load 函式的型別推導（`$types`）。本章將這些知識推向進階應用。
- 本章是系列延伸篇最終章，整合前面所有章節的型別概念。

## Prerequisites

- 已完成 Ch08（Snippets and Component Composition），理解 `generics="T"` 與 `Snippet<[T]>` 的基本用法。
- 已完成 Ch11（Loading Data and Server Functions），理解 SvelteKit 的 `load` 函式與 `$types` 自動型別。
- 熟悉 TypeScript 泛型（generics）、聯合型別（union types）、型別收窄（type narrowing）。
- `svelte5-lab` 專案可正常執行 `npm run dev` 與 `npx svelte-check`。

## Core Concepts

### 1. Generic Components 進階 — 帶約束的泛型元件

Svelte 5 的 `generics` 屬性支援泛型約束（`extends`）和多泛型參數，讓元件在保持靈活性的同時確保型別安全。

**帶約束的泛型**

```svelte
<!-- src/lib/components/TypedSelect.svelte -->
<script lang="ts" generics="T extends { id: string; label: string }">
  import type { Snippet } from 'svelte';

  interface Props {
    items: T[];
    selected: T | null;
    onchange: (item: T) => void;
    children?: Snippet<[T]>;
    placeholder?: string;
  }

  let {
    items,
    selected = null,
    onchange,
    children,
    placeholder = 'Select an item...',
  }: Props = $props();

  let open = $state(false);

  function select(item: T) {
    onchange(item);
    open = false;
  }
</script>

<div class="select-container">
  <button
    onclick={() => open = !open}
    aria-expanded={open}
    aria-haspopup="listbox"
  >
    {selected?.label ?? placeholder}
  </button>

  {#if open}
    <ul role="listbox">
      {#each items as item (item.id)}
        <li
          role="option"
          aria-selected={selected?.id === item.id}
          onclick={() => select(item)}
        >
          {#if children}
            {@render children(item)}
          {:else}
            {item.label}
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</div>
```

使用方式 — TypeScript 會自動推導 `T` 的型別：

```svelte
<script lang="ts">
  import TypedSelect from '$lib/components/TypedSelect.svelte';

  interface User {
    id: string;
    label: string;
    email: string;
    role: 'admin' | 'editor' | 'viewer';
  }

  let users: User[] = [
    { id: '1', label: 'Alice', email: 'alice@example.com', role: 'admin' },
    { id: '2', label: 'Bob', email: 'bob@example.com', role: 'editor' },
  ];

  let selectedUser = $state<User | null>(null);
</script>

<!-- T 被推導為 User，children snippet 的參數也是 User -->
<TypedSelect
  items={users}
  selected={selectedUser}
  onchange={(user) => selectedUser = user}
>
  {#snippet children(user)}
    <div>
      <strong>{user.label}</strong>
      <span class="email">{user.email}</span>
      <span class="role">{user.role}</span>
    </div>
  {/snippet}
</TypedSelect>
```

**多泛型參數**

```svelte
<!-- src/lib/components/TypedMapper.svelte -->
<script lang="ts" generics="TInput, TOutput">
  interface Props {
    items: TInput[];
    transform: (item: TInput) => TOutput;
    render: import('svelte').Snippet<[TOutput, number]>;
  }

  let { items, transform, render }: Props = $props();

  let transformed = $derived(items.map(transform));
</script>

{#each transformed as item, i (i)}
  {@render render(item, i)}
{/each}
```

- **何時用**：建立可重用的容器元件（Select、List、Table、Tree），需要根據傳入的資料型別自動推導 snippet 參數、callback 參數的型別。泛型約束確保資料符合元件的最低結構要求（如必須有 `id` 和 `label`）。
- **何時不用**：簡單的展示元件不需要泛型。如果元件只接收固定型別的 props（如 `string`、`number`），使用具體型別更清晰。過度使用泛型會增加認知負擔。

### 2. Type-safe Load Functions — 型別安全的 Load 函式

SvelteKit 會自動在 `.svelte-kit/types` 目錄下生成 `$types` 模組，提供 `PageLoad`、`LayoutLoad`、`PageServerLoad` 等型別。這些型別會根據路由參數和返回值自動推導，是 SvelteKit 型別安全的核心。

```ts
// src/routes/blog/[slug]/+page.ts
import type { PageLoad } from './$types';

// $types 自動推導 params 包含 slug: string
export const load: PageLoad = async ({ params, fetch }) => {
  const response = await fetch(`/api/posts/${params.slug}`);

  if (!response.ok) {
    return { post: null, error: 'Post not found' };
  }

  const post: BlogPost = await response.json();

  // 回傳值的型別會自動傳遞到 +page.svelte 的 data prop
  return { post, error: null };
};
```

```ts
// src/lib/types/blog.ts — 共享型別定義
export interface BlogPost {
  slug: string;
  title: string;
  content: string;
  author: string;
  publishedAt: string;
  tags: string[];
}

export interface BlogListItem {
  slug: string;
  title: string;
  excerpt: string;
  publishedAt: string;
}
```

```svelte
<!-- src/routes/blog/[slug]/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';

  // PageData 自動包含 load 函式的回傳型別
  let { data }: { data: PageData } = $props();
</script>

{#if data.post}
  <article>
    <h1>{data.post.title}</h1>
    <p>By {data.post.author}</p>
    <div>{@html data.post.content}</div>
  </article>
{:else}
  <p>{data.error}</p>
{/if}
```

Layout data 與 page data 的合併：

```ts
// src/routes/blog/+layout.ts
import type { LayoutLoad } from './$types';
import type { BlogListItem } from '$lib/types/blog';

export const load: LayoutLoad = async ({ fetch }) => {
  const response = await fetch('/api/posts');
  const posts: BlogListItem[] = await response.json();

  return { posts };
};
```

```svelte
<!-- src/routes/blog/+layout.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { LayoutData } from './$types';

  // LayoutData 包含 layout load 的回傳型別
  // 子頁面的 PageData 會自動合併 layout data
  interface Props {
    data: LayoutData;
    children: Snippet;
  }

  let { data, children }: Props = $props();
</script>

<aside>
  <h2>All Posts</h2>
  <ul>
    {#each data.posts as post (post.slug)}
      <li><a href={`/blog/${post.slug}`}>{post.title}</a></li>
    {/each}
  </ul>
</aside>

<main>
  {@render children()}
</main>
```

- **何時用**：任何使用 SvelteKit 的 `load` 函式的場景。`$types` 是自動生成的，不需要手動維護，直接 import 即可獲得完整的型別安全。
- **何時不用**：純 client-side 的資料取得（如在 `$effect` 中 fetch）不會經過 `load` 函式，需要自己定義型別。

### 3. Type-safe Form Actions — 型別安全的表單 Actions

SvelteKit 的 form actions 搭配 Zod schema 驗證，可以實現從表單輸入到伺服器端處理的完整型別安全鏈。

```ts
// src/lib/schemas/registration.ts
import { z } from 'zod';

export const registrationSchema = z.object({
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(20, 'Username must be at most 20 characters')
    .regex(/^[a-zA-Z0-9_]+$/, 'Only letters, numbers, and underscores'),
  email: z
    .string()
    .email('Invalid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

// 從 Zod schema 推導出 TypeScript 型別
export type RegistrationInput = z.infer<typeof registrationSchema>;
```

```ts
// src/routes/register/+page.server.ts
import type { Actions } from './$types';
import { fail } from '@sveltejs/kit';
import { registrationSchema } from '$lib/schemas/registration';

export const actions: Actions = {
  default: async ({ request }) => {
    const formData = await request.formData();

    const rawData = {
      username: formData.get('username'),
      email: formData.get('email'),
      password: formData.get('password'),
      confirmPassword: formData.get('confirmPassword'),
    };

    const result = registrationSchema.safeParse(rawData);

    if (!result.success) {
      // fail() 的回傳型別會自動傳遞到 form prop
      return fail(400, {
        errors: result.error.flatten().fieldErrors,
        values: {
          username: rawData.username as string,
          email: rawData.email as string,
        },
      });
    }

    // result.data 的型別是 RegistrationInput
    const { username, email, password } = result.data;

    // 實際的使用者建立邏輯...
    // await createUser({ username, email, password });

    return { success: true as const };
  },
};
```

```svelte
<!-- src/routes/register/+page.svelte -->
<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData } from './$types';

  // ActionData 自動推導 form action 的回傳型別
  let { form }: { form: ActionData } = $props();
</script>

<form method="POST" use:enhance>
  <div>
    <label for="username">Username</label>
    <input
      id="username"
      name="username"
      type="text"
      value={form?.values?.username ?? ''}
      aria-invalid={form?.errors?.username ? true : undefined}
      aria-describedby={form?.errors?.username ? 'username-error' : undefined}
    />
    {#if form?.errors?.username}
      <p id="username-error" class="error">{form.errors.username[0]}</p>
    {/if}
  </div>

  <div>
    <label for="email">Email</label>
    <input
      id="email"
      name="email"
      type="email"
      value={form?.values?.email ?? ''}
      aria-invalid={form?.errors?.email ? true : undefined}
      aria-describedby={form?.errors?.email ? 'email-error' : undefined}
    />
    {#if form?.errors?.email}
      <p id="email-error" class="error">{form.errors.email[0]}</p>
    {/if}
  </div>

  <div>
    <label for="password">Password</label>
    <input id="password" name="password" type="password" />
    {#if form?.errors?.password}
      <p class="error">{form.errors.password[0]}</p>
    {/if}
  </div>

  <div>
    <label for="confirmPassword">Confirm Password</label>
    <input id="confirmPassword" name="confirmPassword" type="password" />
    {#if form?.errors?.confirmPassword}
      <p class="error">{form.errors.confirmPassword[0]}</p>
    {/if}
  </div>

  <button type="submit">Register</button>

  {#if form?.success}
    <p class="success">Registration successful!</p>
  {/if}
</form>
```

- **何時用**：所有 SvelteKit form actions。Zod schema 提供了單一來源的驗證邏輯，同時生成 TypeScript 型別，避免手動維護型別定義和驗證邏輯兩份程式碼。
- **何時不用**：非表單的 API 互動（如 REST API client）可能更適合用其他方式定義型別。極簡的表單（只有一個欄位）可以不引入 Zod 的額外依賴。

### 4. Discriminated Unions for Component Variants — 用鑑別聯合型別定義元件變體

Discriminated unions 讓你定義互斥的 props 組合。例如 Button 元件可以是連結（有 `href`）或按鈕（有 `onclick`），但不能同時是兩者。TypeScript 的型別系統會確保使用者不會傳入矛盾的 props。

```svelte
<!-- src/lib/components/PolymorphicButton.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  // 共用的 props
  interface BaseProps {
    children: Snippet;
    variant?: 'primary' | 'secondary' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
  }

  // 作為 <a> 連結
  interface LinkProps extends BaseProps {
    href: string;
    target?: '_blank' | '_self';
    onclick?: never;  // 明確排除
  }

  // 作為 <button> 按鈕
  interface ButtonProps extends BaseProps {
    onclick: () => void;
    href?: never;     // 明確排除
    target?: never;
  }

  type Props = LinkProps | ButtonProps;

  let props: Props = $props();

  // 用型別收窄判斷是 link 還是 button
  let isLink = $derived('href' in props && typeof props.href === 'string');
</script>

{#if isLink}
  <a
    href={(props as LinkProps).href}
    target={(props as LinkProps).target}
    class="btn btn-{props.variant ?? 'primary'} btn-{props.size ?? 'md'}"
    class:disabled={props.disabled}
    aria-disabled={props.disabled}
  >
    {@render props.children()}
  </a>
{:else}
  <button
    onclick={(props as ButtonProps).onclick}
    disabled={props.disabled}
    class="btn btn-{props.variant ?? 'primary'} btn-{props.size ?? 'md'}"
  >
    {@render props.children()}
  </button>
{/if}

<style>
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
    font-weight: 500;
  }

  .btn-sm { padding: 0.25rem 0.5rem; font-size: 0.875rem; }
  .btn-md { padding: 0.5rem 1rem; font-size: 1rem; }
  .btn-lg { padding: 0.75rem 1.5rem; font-size: 1.125rem; }

  .btn-primary { background: #0066cc; color: white; }
  .btn-secondary { background: #6c757d; color: white; }
  .btn-ghost { background: transparent; color: #0066cc; }

  .btn:focus-visible {
    outline: 3px solid #4A90D9;
    outline-offset: 2px;
  }

  .btn:disabled, .disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
```

使用方式：

```svelte
<script lang="ts">
  import PolymorphicButton from '$lib/components/PolymorphicButton.svelte';
</script>

<!-- 作為連結 — TypeScript 允許 href，不允許 onclick -->
<PolymorphicButton href="/about" variant="ghost">
  About Us
</PolymorphicButton>

<!-- 作為按鈕 — TypeScript 允許 onclick，不允許 href -->
<PolymorphicButton onclick={() => console.log('clicked')} variant="primary">
  Click Me
</PolymorphicButton>

<!-- 型別錯誤：不能同時有 href 和 onclick -->
<!-- <PolymorphicButton href="/about" onclick={() => {}}>Both</PolymorphicButton> -->
```

- **何時用**：元件有多種使用模式且 props 互斥時。常見場景：連結 vs 按鈕、受控 vs 非受控 input、展開 vs 收合面板。Discriminated unions 在編譯時期就能捕捉不合法的 props 組合。
- **何時不用**：如果所有 props 都是獨立的（沒有互斥關係），使用普通的 optional props 即可。過度使用 discriminated unions 會讓 Props 型別定義變得冗長。

### 5. Component Library Type Design — 元件庫的型別設計

建立可發布的元件庫時，型別的匯出與設計至關重要。包含泛型包裝元件、polymorphic `as` prop、以及 `ComponentProps` utility type。

**Generic List 元件**

```svelte
<!-- src/lib/components/TypedList.svelte -->
<script lang="ts" generics="T extends { id: string }">
  import type { Snippet } from 'svelte';

  interface Props {
    items: T[];
    renderItem: Snippet<[T, number]>;
    emptyState?: Snippet;
    keyFn?: (item: T) => string;
    label?: string;
  }

  let {
    items,
    renderItem,
    emptyState,
    keyFn = (item) => item.id,
    label = 'List',
  }: Props = $props();
</script>

<ul role="list" aria-label={label}>
  {#if items.length === 0 && emptyState}
    <li>{@render emptyState()}</li>
  {:else}
    {#each items as item, i (keyFn(item))}
      <li>{@render renderItem(item, i)}</li>
    {/each}
  {/if}
</ul>
```

**Generic Table 元件**

```svelte
<!-- src/lib/components/TypedTable.svelte -->
<script lang="ts" generics="T extends Record<string, unknown>">
  import type { Snippet } from 'svelte';

  interface Column<U> {
    key: string;
    label: string;
    render?: Snippet<[U]>;
  }

  interface Props {
    items: T[];
    columns: Column<T>[];
    header?: Snippet<[Column<T>[]]>;
    row?: Snippet<[T, number]>;
    caption?: string;
  }

  let { items, columns, header, row, caption }: Props = $props();
</script>

<table>
  {#if caption}
    <caption>{caption}</caption>
  {/if}
  <thead>
    {#if header}
      {@render header(columns)}
    {:else}
      <tr>
        {#each columns as col (col.key)}
          <th>{col.label}</th>
        {/each}
      </tr>
    {/if}
  </thead>
  <tbody>
    {#each items as item, i (i)}
      {#if row}
        {@render row(item, i)}
      {:else}
        <tr>
          {#each columns as col (col.key)}
            <td>
              {#if col.render}
                {@render col.render(item)}
              {:else}
                {String(item[col.key] ?? '')}
              {/if}
            </td>
          {/each}
        </tr>
      {/if}
    {/each}
  </tbody>
</table>
```

**Polymorphic Box 元件（`as` prop）**

```svelte
<!-- src/lib/components/Box.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    as?: string;
    children: Snippet;
    class?: string;
    [key: string]: unknown;
  }

  let { as = 'div', children, class: className, ...rest }: Props = $props();
</script>

<svelte:element this={as} class={className} {...rest}>
  {@render children()}
</svelte:element>
```

使用方式：

```svelte
<script lang="ts">
  import Box from '$lib/components/Box.svelte';
</script>

<Box as="section" class="hero">
  <h1>Welcome</h1>
</Box>

<Box as="article" class="post">
  <p>Content here</p>
</Box>

<Box as="nav" aria-label="Main">
  <a href="/">Home</a>
</Box>
```

**匯出元件庫型別**

```ts
// src/lib/index.ts — 元件庫入口
export { default as TypedSelect } from './components/TypedSelect.svelte';
export { default as TypedList } from './components/TypedList.svelte';
export { default as TypedTable } from './components/TypedTable.svelte';
export { default as PolymorphicButton } from './components/PolymorphicButton.svelte';
export { default as Box } from './components/Box.svelte';

// 匯出型別
export type { BlogPost, BlogListItem } from './types/blog';
```

```ts
// 使用 ComponentProps 取得元件的 props 型別
import type { ComponentProps } from 'svelte';
import type TypedSelect from '$lib/components/TypedSelect.svelte';

// 取得 TypedSelect 的 props 型別（但泛型參數會被推導為 unknown）
type SelectProps = ComponentProps<typeof TypedSelect>;
```

- **何時用**：建立共享的元件庫或 design system。正確的型別匯出讓使用者在自己的專案中獲得完整的 IDE 支援與型別檢查。Polymorphic 元件減少重複的 wrapper 元件。
- **何時不用**：應用內部的一次性元件不需要這麼嚴格的型別設計。過度的抽象（如每個 `<div>` 都用 `<Box>`）會降低可讀性。

### 6. svelte-check in CI — 在 CI 中整合型別檢查

`svelte-check` 是 Svelte 的官方型別檢查工具，能檢查 `.svelte` 檔案中的 TypeScript 錯誤。在 CI 中整合可以確保每次 commit 都通過型別檢查。

```json
// package.json
{
  "scripts": {
    "check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json",
    "check:watch": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json --watch"
  }
}
```

```json
// tsconfig.json — 嚴格模式設定
{
  "extends": "./.svelte-kit/tsconfig.json",
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": false,
    "moduleResolution": "bundler"
  }
}
```

GitHub Actions 整合：

```yaml
# .github/workflows/check.yml
name: Type Check

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - run: npm ci

      - name: Sync SvelteKit types
        run: npx svelte-kit sync

      - name: Run svelte-check
        run: npx svelte-check --tsconfig ./tsconfig.json --fail-on-warnings

      - name: Run TypeScript compiler check
        run: npx tsc --noEmit
```

常見的 `svelte-check` 錯誤與修正：

```ts
// 錯誤：Type 'string' is not assignable to type 'Snippet'
// 原因：傳入字串給需要 Snippet 的 prop
// 修正：使用 {#snippet} 定義模板

// 錯誤：Property 'X' does not exist on type 'PageData'
// 原因：load 函式未返回該屬性，或忘記執行 svelte-kit sync
// 修正：npx svelte-kit sync 重新生成型別

// 錯誤：Argument of type '...' is not assignable to parameter of type '...'
// 原因：泛型推導結果與預期不符
// 修正：檢查泛型約束是否正確，或手動標注型別
```

- **何時用**：所有 Svelte + TypeScript 專案都應在 CI 中執行 `svelte-check`。它能捕捉 `.svelte` 檔案中 `tsc` 看不到的型別錯誤。
- **何時不用**：沒有使用 TypeScript 的純 JavaScript Svelte 專案。

## Step-by-step

### Step 1：建立型別安全的泛型 Select 元件

```svelte
<!-- src/lib/components/TypedSelect.svelte -->
<script lang="ts" generics="T extends { id: string; label: string }">
  import type { Snippet } from 'svelte';

  interface Props {
    items: T[];
    selected: T | null;
    onchange: (item: T) => void;
    children?: Snippet<[T]>;
    placeholder?: string;
  }

  let {
    items,
    selected = null,
    onchange,
    children,
    placeholder = 'Select...',
  }: Props = $props();

  let open = $state(false);
</script>

<div class="typed-select">
  <button onclick={() => open = !open} aria-expanded={open}>
    {selected?.label ?? placeholder}
  </button>

  {#if open}
    <ul role="listbox">
      {#each items as item (item.id)}
        <li
          role="option"
          aria-selected={selected?.id === item.id}
          onclick={() => { onchange(item); open = false; }}
        >
          {#if children}
            {@render children(item)}
          {:else}
            {item.label}
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</div>
```

泛型約束 `T extends { id: string; label: string }` 確保傳入的資料至少有 `id` 和 `label` 屬性，但允許有額外的屬性（如 `email`、`role`）。

### Step 2：建立型別安全的 load 函式與共享型別

```ts
// src/lib/types/blog.ts
export interface BlogPost {
  slug: string;
  title: string;
  content: string;
  author: string;
  publishedAt: string;
  tags: string[];
}

export interface BlogListItem {
  slug: string;
  title: string;
  excerpt: string;
  publishedAt: string;
}
```

```ts
// src/routes/blog/[slug]/+page.ts
import type { PageLoad } from './$types';
import type { BlogPost } from '$lib/types/blog';

export const load: PageLoad = async ({ params, fetch }) => {
  const response = await fetch(`/api/posts/${params.slug}`);
  const post: BlogPost = await response.json();

  return { post };
};
```

```svelte
<!-- src/routes/blog/[slug]/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  // data.post 自動推導為 BlogPost
</script>

<article>
  <h1>{data.post.title}</h1>
  <time>{data.post.publishedAt}</time>
  <div>{@html data.post.content}</div>
</article>
```

### Step 3：使用 Zod 建立型別安全的 form action

```ts
// src/lib/schemas/registration.ts
import { z } from 'zod';

export const registrationSchema = z.object({
  username: z.string().min(3).max(20),
  email: z.string().email(),
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

export type RegistrationInput = z.infer<typeof registrationSchema>;
```

```ts
// src/routes/register/+page.server.ts
import type { Actions } from './$types';
import { fail } from '@sveltejs/kit';
import { registrationSchema } from '$lib/schemas/registration';

export const actions: Actions = {
  default: async ({ request }) => {
    const formData = await request.formData();

    const result = registrationSchema.safeParse(
      Object.fromEntries(formData)
    );

    if (!result.success) {
      return fail(400, {
        errors: result.error.flatten().fieldErrors,
      });
    }

    // result.data 型別為 RegistrationInput
    return { success: true as const };
  },
};
```

### Step 4：實作 discriminated union 的 Button 元件

```svelte
<!-- src/lib/components/PolyButton.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface BaseProps {
    children: Snippet;
    variant?: 'primary' | 'secondary';
    disabled?: boolean;
  }

  interface AsLink extends BaseProps {
    href: string;
    target?: '_blank' | '_self';
    onclick?: never;
  }

  interface AsButton extends BaseProps {
    onclick: () => void;
    type?: 'button' | 'submit' | 'reset';
    href?: never;
    target?: never;
  }

  type Props = AsLink | AsButton;

  let props: Props = $props();
</script>

{#if 'href' in props && props.href}
  <a
    href={props.href}
    target={props.target}
    class="poly-btn poly-btn-{props.variant ?? 'primary'}"
    class:disabled={props.disabled}
    aria-disabled={props.disabled}
  >
    {@render props.children()}
  </a>
{:else}
  <button
    onclick={(props as AsButton).onclick}
    type={(props as AsButton).type ?? 'button'}
    disabled={props.disabled}
    class="poly-btn poly-btn-{props.variant ?? 'primary'}"
  >
    {@render props.children()}
  </button>
{/if}
```

### Step 5：建立 Generic List 包裝元件

```svelte
<!-- src/lib/components/TypedList.svelte -->
<script lang="ts" generics="T extends { id: string }">
  import type { Snippet } from 'svelte';

  interface Props {
    items: T[];
    renderItem: Snippet<[T, number]>;
    emptyState?: Snippet;
    ordered?: boolean;
    label?: string;
  }

  let {
    items,
    renderItem,
    emptyState,
    ordered = false,
    label = 'List',
  }: Props = $props();

  let tag = $derived(ordered ? 'ol' : 'ul');
</script>

<svelte:element this={tag} role="list" aria-label={label}>
  {#if items.length === 0 && emptyState}
    <li>{@render emptyState()}</li>
  {:else}
    {#each items as item, i (item.id)}
      <li>{@render renderItem(item, i)}</li>
    {/each}
  {/if}
</svelte:element>
```

使用方式：

```svelte
<script lang="ts">
  import TypedList from '$lib/components/TypedList.svelte';

  interface Todo {
    id: string;
    text: string;
    done: boolean;
  }

  let todos = $state<Todo[]>([
    { id: '1', text: 'Learn Svelte 5', done: true },
    { id: '2', text: 'Build an app', done: false },
  ]);
</script>

<!-- T 自動推導為 Todo -->
<TypedList items={todos}>
  {#snippet renderItem(todo, index)}
    <label>
      <input type="checkbox" checked={todo.done} />
      {todo.text}
    </label>
  {/snippet}

  {#snippet emptyState()}
    <p>No todos yet!</p>
  {/snippet}
</TypedList>
```

### Step 6：建立 Polymorphic Box 元件

```svelte
<!-- src/lib/components/Box.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    as?: string;
    children: Snippet;
    class?: string;
    [key: string]: unknown;
  }

  let { as = 'div', children, class: className = '', ...rest }: Props = $props();
</script>

<svelte:element this={as} class={className} {...rest}>
  {@render children()}
</svelte:element>
```

使用方式：

```svelte
<script lang="ts">
  import Box from '$lib/components/Box.svelte';
</script>

<!-- 作為 section -->
<Box as="section" class="hero" id="hero-section">
  <h1>Welcome</h1>
  <p>This renders as a &lt;section&gt; tag.</p>
</Box>

<!-- 作為 nav -->
<Box as="nav" aria-label="Breadcrumb" class="breadcrumb">
  <a href="/">Home</a> / <a href="/about">About</a>
</Box>

<!-- 預設為 div -->
<Box class="container">
  <p>This renders as a &lt;div&gt; tag.</p>
</Box>
```

### Step 7：匯出元件庫型別

```ts
// src/lib/index.ts
// 元件匯出
export { default as TypedSelect } from './components/TypedSelect.svelte';
export { default as TypedList } from './components/TypedList.svelte';
export { default as TypedTable } from './components/TypedTable.svelte';
export { default as PolymorphicButton } from './components/PolymorphicButton.svelte';
export { default as Box } from './components/Box.svelte';

// 型別匯出
export type { BlogPost, BlogListItem } from './types/blog';
export type { RegistrationInput } from './schemas/registration';
```

```json
// package.json — svelte 套件設定
{
  "name": "my-ui-lib",
  "svelte": "./src/lib/index.ts",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "svelte": "./src/lib/index.ts"
    }
  }
}
```

### Step 8：在 CI 中設定 svelte-check

```yaml
# .github/workflows/check.yml
name: Type Check & Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - run: npm ci

      - name: Sync SvelteKit types
        run: npx svelte-kit sync

      - name: Run svelte-check
        run: npx svelte-check --tsconfig ./tsconfig.json --fail-on-warnings

      - name: Run tsc
        run: npx tsc --noEmit
```

本地執行：

```bash
# 一次性檢查
npx svelte-check --tsconfig ./tsconfig.json

# 監聽模式（開發時持續檢查）
npx svelte-check --tsconfig ./tsconfig.json --watch

# 嚴格模式（警告也視為錯誤）
npx svelte-check --tsconfig ./tsconfig.json --fail-on-warnings
```

## Hands-on Lab

任務：建立一套型別安全的元件庫，展示進階 TypeScript 模式。

### Foundation 基礎層

建立一個泛型的 TypedList 元件：

- 使用 `generics="T extends { id: string }"` 定義泛型約束。
- 接收 `items: T[]` 和 `renderItem: Snippet<[T, number]>`。
- 支援 `emptyState` snippet 作為空狀態顯示。
- 用兩種不同的資料型別（如 `Todo[]` 和 `User[]`）使用同一個元件，驗證型別推導正確。

**驗收條件：**
- [ ] TypedList 能接受不同型別的 items 且型別自動推導。
- [ ] renderItem snippet 的參數型別正確（如 `todo: Todo`）。
- [ ] emptyState 在 items 為空時正確顯示。
- [ ] `npx svelte-check` 通過，無型別錯誤。

### Advanced 進階層

建立一個型別安全的表單，搭配 Zod schema 驗證：

- 定義 Zod schema 並用 `z.infer` 推導型別。
- 建立 form action 使用 `safeParse` 驗證。
- 在表單元件中顯示 field-level 錯誤訊息。
- `ActionData` 型別自動推導正確。
- 使用 `use:enhance` 實現 progressive enhancement。

**驗收條件：**
- [ ] Zod schema 與 TypeScript 型別一致（`z.infer`）。
- [ ] form action 的錯誤回應型別正確傳遞到元件。
- [ ] 驗證失敗時顯示對應欄位的錯誤訊息。
- [ ] 表單在 JavaScript 停用時仍能運作。

### Challenge 挑戰層

建立一個完整的 polymorphic 元件庫：

- 建立 PolymorphicButton 元件（discriminated union: link vs button）。
- 建立 Box 元件（`as` prop 支援動態 HTML 標籤）。
- 建立 TypedTable 元件（泛型 + column 定義 + 自訂 render snippet）。
- 所有元件從 `$lib/index.ts` 匯出。
- 設定 `svelte-check` CI workflow。

**驗收條件：**
- [ ] PolymorphicButton 以 link 模式使用時不允許 `onclick`。
- [ ] PolymorphicButton 以 button 模式使用時不允許 `href`。
- [ ] Box 元件可渲染為不同的 HTML 標籤。
- [ ] TypedTable 的 column render snippet 參數型別正確。
- [ ] `npx svelte-check --fail-on-warnings` 通過。
- [ ] CI workflow 配置完成且能執行。

## Reference Solution

完整的泛型 Select 元件：

```svelte
<!-- src/lib/components/TypedSelect.svelte -->
<script lang="ts" generics="T extends { id: string; label: string }">
  import type { Snippet } from 'svelte';

  interface Props {
    items: T[];
    selected: T | null;
    onchange: (item: T) => void;
    children?: Snippet<[T]>;
    placeholder?: string;
  }

  let {
    items,
    selected = null,
    onchange,
    children,
    placeholder = 'Select...',
  }: Props = $props();

  let open = $state(false);
  let activeIndex = $state(-1);
  let listRef = $state<HTMLUListElement | null>(null);

  function selectItem(item: T) {
    onchange(item);
    open = false;
  }

  function handleKeydown(e: KeyboardEvent) {
    if (!open) {
      if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        open = true;
        activeIndex = 0;
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        activeIndex = (activeIndex + 1) % items.length;
        break;
      case 'ArrowUp':
        e.preventDefault();
        activeIndex = (activeIndex - 1 + items.length) % items.length;
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (activeIndex >= 0 && items[activeIndex]) {
          selectItem(items[activeIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        open = false;
        break;
    }
  }
</script>

<div class="typed-select" onkeydown={handleKeydown}>
  <button
    onclick={() => { open = !open; activeIndex = 0; }}
    aria-expanded={open}
    aria-haspopup="listbox"
    class="select-trigger"
  >
    {selected?.label ?? placeholder}
  </button>

  {#if open}
    <ul bind:this={listRef} role="listbox" class="select-options">
      {#each items as item, i (item.id)}
        <li
          role="option"
          aria-selected={selected?.id === item.id}
          class:active={i === activeIndex}
          onclick={() => selectItem(item)}
        >
          {#if children}
            {@render children(item)}
          {:else}
            {item.label}
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .typed-select {
    position: relative;
    display: inline-block;
  }

  .select-trigger {
    padding: 0.5rem 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    min-width: 200px;
    text-align: left;
  }

  .select-trigger:focus-visible {
    outline: 3px solid #4A90D9;
    outline-offset: 2px;
  }

  .select-options {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    margin: 0;
    padding: 0;
    list-style: none;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    max-height: 200px;
    overflow-y: auto;
    z-index: 100;
  }

  .select-options li {
    padding: 0.5rem 1rem;
    cursor: pointer;
  }

  .select-options li:hover,
  .select-options li.active {
    background: #f0f0f0;
  }

  .select-options li[aria-selected='true'] {
    background: #e0ecff;
  }
</style>
```

完整的 PolymorphicButton 元件：

```svelte
<!-- src/lib/components/PolymorphicButton.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface BaseProps {
    children: Snippet;
    variant?: 'primary' | 'secondary' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    class?: string;
  }

  interface LinkProps extends BaseProps {
    href: string;
    target?: '_blank' | '_self';
    onclick?: never;
    type?: never;
  }

  interface ButtonProps extends BaseProps {
    onclick: () => void;
    type?: 'button' | 'submit' | 'reset';
    href?: never;
    target?: never;
  }

  type Props = LinkProps | ButtonProps;

  let props: Props = $props();

  let isLink = $derived('href' in props && typeof props.href === 'string');

  let classes = $derived(
    [
      'poly-btn',
      `poly-btn-${props.variant ?? 'primary'}`,
      `poly-btn-${props.size ?? 'md'}`,
      props.class,
    ]
      .filter(Boolean)
      .join(' ')
  );
</script>

{#if isLink}
  <a
    href={(props as LinkProps).href}
    target={(props as LinkProps).target}
    class={classes}
    class:disabled={props.disabled}
    aria-disabled={props.disabled}
  >
    {@render props.children()}
  </a>
{:else}
  <button
    onclick={(props as ButtonProps).onclick}
    type={(props as ButtonProps).type ?? 'button'}
    disabled={props.disabled}
    class={classes}
  >
    {@render props.children()}
  </button>
{/if}

<style>
  .poly-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    text-decoration: none;
    font-weight: 500;
    transition: opacity 0.2s;
  }

  .poly-btn-sm { padding: 0.25rem 0.75rem; font-size: 0.875rem; }
  .poly-btn-md { padding: 0.5rem 1rem; font-size: 1rem; }
  .poly-btn-lg { padding: 0.75rem 1.5rem; font-size: 1.125rem; }

  .poly-btn-primary { background: #0066cc; color: white; }
  .poly-btn-secondary { background: #6c757d; color: white; }
  .poly-btn-ghost { background: transparent; color: #0066cc; border: 1px solid #0066cc; }

  .poly-btn:hover { opacity: 0.9; }

  .poly-btn:focus-visible {
    outline: 3px solid #4A90D9;
    outline-offset: 2px;
  }

  .poly-btn:disabled, .disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
```

完整的 TypedList 元件：

```svelte
<!-- src/lib/components/TypedList.svelte -->
<script lang="ts" generics="T extends { id: string }">
  import type { Snippet } from 'svelte';

  interface Props {
    items: T[];
    renderItem: Snippet<[T, number]>;
    emptyState?: Snippet;
    ordered?: boolean;
    label?: string;
  }

  let {
    items,
    renderItem,
    emptyState,
    ordered = false,
    label = 'List',
  }: Props = $props();

  let tag = $derived(ordered ? 'ol' : 'ul');
</script>

<svelte:element this={tag} role="list" aria-label={label}>
  {#if items.length === 0 && emptyState}
    <li>{@render emptyState()}</li>
  {:else}
    {#each items as item, i (item.id)}
      <li>{@render renderItem(item, i)}</li>
    {/each}
  {/if}
</svelte:element>
```

完整的 Box 元件：

```svelte
<!-- src/lib/components/Box.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    as?: string;
    children: Snippet;
    class?: string;
    [key: string]: unknown;
  }

  let { as = 'div', children, class: className = '', ...rest }: Props = $props();
</script>

<svelte:element this={as} class={className} {...rest}>
  {@render children()}
</svelte:element>
```

## Common Pitfalls

1. **用 `as any` 繞過型別推導而非修正根本問題**：`as any` 會讓 TypeScript 完全放棄型別檢查。當泛型推導不如預期時，應檢查泛型約束是否正確、資料型別是否符合約束，而非直接強制轉型。

   ```ts
   // BAD: 遺失所有型別安全
   let value = someGenericFn(data as any);

   // GOOD: 明確標注型別
   let value = someGenericFn<MyType>(data);
   ```

2. **忘記在 `<script>` 標籤加上 `generics` 屬性**：Svelte 5 的泛型元件必須在 `<script>` 標籤上宣告 `generics` 屬性。沒有這個屬性，`T` 會被視為一般的 TypeScript 型別參數而非 Svelte 元件泛型。

   ```svelte
   <!-- BAD: T 無法被推導 -->
   <script lang="ts">
     // T 不存在
     interface Props { items: T[] }
   </script>

   <!-- GOOD: 宣告泛型 -->
   <script lang="ts" generics="T extends { id: string }">
     interface Props { items: T[] }
   </script>
   ```

3. **Snippet 型別參數使用 `Snippet<T>` 而非 `Snippet<[T]>`**：`Snippet` 的泛型參數必須是 tuple 形式。`Snippet<[T]>` 表示接收一個 `T` 型別的參數，`Snippet<[T, number]>` 表示接收兩個參數。忘記用 tuple 會導致型別錯誤。

   ```ts
   // BAD: 型別錯誤
   let render: Snippet<string>;

   // GOOD: tuple 形式
   let render: Snippet<[string]>;
   let renderWithIndex: Snippet<[string, number]>;
   ```

4. **沒有使用 `$types` 自動生成的型別**：SvelteKit 會自動在 `.svelte-kit/types` 中生成 `PageLoad`、`PageData`、`ActionData` 等型別。手動定義這些型別不僅多餘，還可能與實際的 load 函式回傳值不一致。

   ```ts
   // BAD: 手動定義型別，可能與 load 不一致
   interface PageData {
     posts: Post[];
   }
   let { data }: { data: PageData } = $props();

   // GOOD: 使用自動生成的型別
   import type { PageData } from './$types';
   let { data }: { data: PageData } = $props();
   ```

5. **過度複雜的泛型約束導致型別推導失敗**：層層嵌套的泛型約束（如 `T extends Record<K, V extends Array<U>>`) 會讓 TypeScript 的型別推導引擎無法正確推導。保持泛型約束簡單明確，必要時拆分為多個元件或 helper 函式。

   ```ts
   // BAD: 過度複雜，推導常常失敗
   generics="T extends Record<string, Array<U>>, U extends { id: K }, K extends string"

   // GOOD: 簡單明確
   generics="T extends { id: string }"
   // 在元件內部處理更細緻的型別邏輯
   ```

## Checklist

- [ ] 能使用 `generics="T extends ..."` 建立帶約束的泛型元件。
- [ ] 能使用 `$types`（`PageLoad`、`PageData`、`ActionData`）自動型別推導。
- [ ] 能用 Zod schema 搭配 `z.infer` 建立型別安全的 form action。
- [ ] 能用 discriminated unions 定義互斥的元件 props（如 link vs button）。
- [ ] 能建立 polymorphic 元件（`as` prop + `<svelte:element>`）。
- [ ] 能從 `$lib/index.ts` 正確匯出元件與型別。
- [ ] 能在 CI 中設定 `svelte-check --fail-on-warnings` 確保型別安全。

## Further Reading

- [Svelte Docs — TypeScript](https://svelte.dev/docs/svelte/typescript)
- [Svelte Docs — $types](https://svelte.dev/docs/kit/$types)
- [Svelte Docs — Component type](https://svelte.dev/docs/svelte/Component)
- [SvelteKit Docs — Form actions](https://svelte.dev/docs/kit/form-actions)
- [SvelteKit Docs — Types](https://svelte.dev/docs/kit/types)
- [TypeScript Handbook — Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [TypeScript Handbook — Discriminated Unions](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions)
- [Zod — GitHub](https://github.com/colinhacks/zod)
- [svelte-check — npm](https://www.npmjs.com/package/svelte-check)
