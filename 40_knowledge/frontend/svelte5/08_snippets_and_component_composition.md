---
title: "Snippets and Component Composition / 程式碼片段與元件組合"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "08"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [07_stores_context_and_state_patterns]
---
# Snippets and Component Composition / 程式碼片段與元件組合

## Goal

學會 Svelte 5 獨有的 snippets 系統與進階元件組合模式，取代 Svelte 4 的 slot 機制。

Snippets 是 Svelte 5 最重要的模板複用機制，搭配 `{@render}` 與 TypeScript 泛型可建立高度靈活且型別安全的元件 API。理解這些組合模式將讓你能打造可維護的 UI 元件庫，並在實際專案中有效消除模板重複。

- 銜接上一章：Ch07 學會了狀態管理模式（stores、context、shared state），現在要處理元件間的組合與內容分發。
- 下一章預告：Ch09 將學習樣式、過渡與動畫。

## Prerequisites

- 已完成 Ch07（Stores, Context, and State Patterns），理解 `$state`、context 與跨元件狀態共享。
- 能建立可接收 props 的子元件，並在父元件中使用。
- `svelte5-lab` 專案可正常執行 `npm run dev`。

## Core Concepts

### 1. `{#snippet name(params)}` / `{@render snippet()}` — 模板片段定義與渲染

Svelte 5 的模板複用機制，可在同一元件內定義和渲染可重用模板片段。Snippet 是一段可接收參數的模板區塊，透過 `{@render}` 呼叫後才會產生實際的 DOM 輸出。

```svelte
{#snippet greeting(name)}
  <p>Hello, {name}!</p>
{/snippet}

{@render greeting('Alice')}
{@render greeting('Bob')}
```

- **何時用**：同一元件內出現重複的 markup 模式，例如多個相似的卡片區塊、重複的表單欄位樣板。Snippet 讓你在不抽成獨立元件的前提下消除模板重複。
- **何時不用**：當該片段包含獨立的邏輯與狀態時，應該抽成獨立元件而非 snippet。Snippet 僅解決模板層面的重複，不適合封裝複雜的行為邏輯。

### 2. Passing snippets as props (`Snippet<[Type]>`) — 將 snippet 作為 props 傳遞

可將 snippet 作為 props 傳入子元件，提供 render prop 式的靈活性。子元件透過 `{@render}` 呼叫父元件傳入的 snippet，並可傳遞資料回去讓父元件決定如何渲染。

```svelte
<!-- 子元件 -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    row: Snippet<[string, number]>;
  }

  let { row }: Props = $props();
</script>

{@render row('Alice', 1)}
{@render row('Bob', 2)}
```

- **何時用**：需要讓父元件控制子元件的部分渲染邏輯（如 table column template、list item renderer、card body），實現「控制反轉」模式。
- **何時不用**：簡單的內容投影只需要用 `children` snippet 即可，不需要額外定義具名 snippet prop。

### 3. `children` snippet 與 named snippets — 取代 Svelte 4 的 `<slot>`

Svelte 5 中 `children` 是特殊的 snippet，取代 Svelte 4 的 `<slot>`。當父元件在子元件標籤內放入內容時，該內容自動成為 `children` snippet。Named snippets 則取代 Svelte 4 的 `<slot name="...">`，允許多個具名插入點。

```svelte
<!-- Card.svelte（子元件） -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    children: Snippet;
    footer?: Snippet;
  }

  let { children, footer }: Props = $props();
</script>

<div class="card">
  <div class="card-body">
    {@render children()}
  </div>
  {#if footer}
    <div class="card-footer">
      {@render footer()}
    </div>
  {/if}
</div>
```

```svelte
<!-- 父元件使用方式 -->
<Card>
  <p>This becomes the children snippet.</p>

  {#snippet footer()}
    <button>Save</button>
  {/snippet}
</Card>
```

- **何時用 `children`**：簡單的內容包裝元件（Card、Modal、Dialog、Layout），父元件只需放入單一區塊的內容。
- **何時用 named snippets**：元件有多個插入點（header、body、footer），需要父元件分別提供不同區塊的內容。
- **Svelte 4 → Svelte 5 遷移對照**：`<slot>` → `{@render children()}`；`<slot name="header">` → `{@render header()}`（header 作為 snippet prop）。

### 4. `<svelte:component>` / `<svelte:element>` — 動態渲染

根據執行時期的值動態決定要渲染哪個元件或 HTML 標籤。

```svelte
<!-- 動態元件 -->
<svelte:component this={currentComponent} {...componentProps} />

<!-- 動態 HTML 標籤 -->
<svelte:element this={tag}>Content</svelte:element>
```

- **何時用 `<svelte:component>`**：根據條件動態切換元件，例如 icon 系統（根據名稱選擇對應的 icon 元件）、widget 系統（根據設定渲染不同類型的 widget）、動態表單（根據欄位類型渲染不同的 input 元件）。
- **何時用 `<svelte:element>`**：動態 HTML 標籤，例如根據層級渲染 h1–h6、根據語意選擇 section/article/div、可設定根標籤的通用元件。
- **何時不用**：靜態已知的元件直接 import 使用即可，不需要引入動態渲染的額外複雜度。過度使用動態元件會降低可讀性與型別安全性。

## Step-by-step

### Step 1：在元件內定義 local snippet 並用 `{@render}` 呼叫

建立一個元件，用 `{#snippet}` 定義可重用的模板片段，再用 `{@render}` 渲染。

```svelte
<!-- src/routes/ch08/+page.svelte -->
<script lang="ts">
  let users = $state([
    { name: 'Alice', role: 'admin' },
    { name: 'Bob', role: 'editor' },
    { name: 'Charlie', role: 'viewer' },
  ]);
</script>

{#snippet userBadge(name, role)}
  <span class="badge">
    <strong>{name}</strong> — {role}
  </span>
{/snippet}

<div class="user-list">
  {#each users as user}
    {@render userBadge(user.name, user.role)}
  {/each}
</div>
```

Snippet 定義不會產生任何 DOM 輸出，只有透過 `{@render}` 呼叫時才會渲染。

### Step 2：為 snippet 傳遞參數 `{#snippet row(item, index)}`

Snippet 可接收多個參數，用於在不同呼叫時傳入不同的資料。

```svelte
<script lang="ts">
  interface Product {
    id: number;
    name: string;
    price: number;
  }

  let products = $state<Product[]>([
    { id: 1, name: 'Keyboard', price: 79.99 },
    { id: 2, name: 'Mouse', price: 49.99 },
    { id: 3, name: 'Monitor', price: 299.99 },
  ]);
</script>

{#snippet row(item, index)}
  <tr class:highlight={index % 2 === 0}>
    <td>{index + 1}</td>
    <td>{item.name}</td>
    <td>${item.price.toFixed(2)}</td>
  </tr>
{/snippet}

<table>
  <thead>
    <tr><th>#</th><th>Name</th><th>Price</th></tr>
  </thead>
  <tbody>
    {#each products as product, i (product.id)}
      {@render row(product, i)}
    {/each}
  </tbody>
</table>
```

### Step 3：建立 `DataTable` 元件，接受 `row` snippet 作為 prop

將 snippet 從父元件傳入子元件，實現「父元件控制渲染邏輯」的模式。

```svelte
<!-- src/lib/components/DataTable.svelte -->
<script lang="ts" generics="T">
  import type { Snippet } from 'svelte';

  interface Props {
    items: T[];
    header: Snippet;
    row: Snippet<[T, number]>;
    empty?: Snippet;
  }

  let { items, header, row, empty }: Props = $props();
</script>

<table>
  <thead>
    {@render header()}
  </thead>
  <tbody>
    {#if items.length === 0 && empty}
      <tr><td>{@render empty()}</td></tr>
    {:else}
      {#each items as item, i (i)}
        {@render row(item, i)}
      {/each}
    {/if}
  </tbody>
</table>
```

### Step 4：為 snippet prop 加上 TypeScript 型別 `Snippet<[Item, number]>`

`Snippet` 型別來自 `svelte` 模組，泛型參數為 tuple 形式，描述 snippet 接收的參數型別。

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';

  // Snippet 不接收參數
  let noArgs: Snippet;

  // Snippet 接收一個 string 參數
  let oneArg: Snippet<[string]>;

  // Snippet 接收兩個參數：Item 和 number
  interface Item { id: number; label: string; }
  let twoArgs: Snippet<[Item, number]>;
</script>
```

搭配 `generics` 屬性可建立完全型別安全的泛型元件（如 Step 3 的 `DataTable`），父元件傳入的 snippet 參數型別會自動推導。

### Step 5：在 `Modal` 元件中使用 `children` snippet 取代 `<slot>`

`children` 是 Svelte 5 的特殊 snippet，自動接收父元件標籤內的內容。

```svelte
<!-- src/lib/components/Modal.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    open: boolean;
    onclose: () => void;
    children: Snippet;
    title?: string;
  }

  let { open, onclose, children, title = 'Dialog' }: Props = $props();
</script>

{#if open}
  <div class="overlay" onclick={onclose} role="presentation">
    <div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-label={title}>
      <header>
        <h2>{title}</h2>
        <button onclick={onclose} aria-label="Close">×</button>
      </header>
      <div class="modal-body">
        {@render children()}
      </div>
    </div>
  </div>
{/if}
```

```svelte
<!-- 父元件使用 -->
<script lang="ts">
  import Modal from '$lib/components/Modal.svelte';

  let showModal = $state(false);
</script>

<button onclick={() => showModal = true}>Open Modal</button>

<Modal open={showModal} onclose={() => showModal = false} title="Confirmation">
  <p>Are you sure you want to proceed?</p>
  <button onclick={() => showModal = false}>Confirm</button>
</Modal>
```

### Step 6：在 `Panel` 元件中使用 named snippets 取代 named slots

Named snippets 讓元件擁有多個可自訂的插入點。

```svelte
<!-- src/lib/components/Panel.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    header: Snippet;
    body: Snippet;
    footer?: Snippet;
  }

  let { header, body, footer }: Props = $props();
</script>

<div class="panel">
  <div class="panel-header">
    {@render header()}
  </div>
  <div class="panel-body">
    {@render body()}
  </div>
  {#if footer}
    <div class="panel-footer">
      {@render footer()}
    </div>
  {/if}
</div>
```

```svelte
<!-- 父元件使用 -->
<script lang="ts">
  import Panel from '$lib/components/Panel.svelte';
</script>

<Panel>
  {#snippet header()}
    <h3>User Profile</h3>
  {/snippet}

  {#snippet body()}
    <p>Name: Alice</p>
    <p>Email: alice@example.com</p>
  {/snippet}

  {#snippet footer()}
    <button>Edit</button>
    <button>Delete</button>
  {/snippet}
</Panel>
```

### Step 7：使用 `<svelte:component>` 實現動態元件渲染

根據執行時期的值動態切換要渲染的元件。

```svelte
<!-- src/lib/components/icons/IconHome.svelte -->
<script lang="ts">
  let { size = 24 }: { size?: number } = $props();
</script>
<svg width={size} height={size} viewBox="0 0 24 24">
  <path d="M3 12l9-9 9 9M5 10v10a1 1 0 001 1h3m10-11v10a1 1 0 01-1 1h-3" />
</svg>
```

```svelte
<!-- src/routes/ch08/dynamic/+page.svelte -->
<script lang="ts">
  import IconHome from '$lib/components/icons/IconHome.svelte';
  import IconSettings from '$lib/components/icons/IconSettings.svelte';
  import IconUser from '$lib/components/icons/IconUser.svelte';
  import type { Component } from 'svelte';

  const iconMap: Record<string, Component<{ size?: number }>> = {
    home: IconHome,
    settings: IconSettings,
    user: IconUser,
  };

  let selected = $state('home');
  let currentIcon = $derived(iconMap[selected]);
</script>

<select bind:value={selected}>
  <option value="home">Home</option>
  <option value="settings">Settings</option>
  <option value="user">User</option>
</select>

<svelte:component this={currentIcon} size={32} />
```

### Step 8：使用 `<svelte:element>` 實現動態 HTML 標籤

根據 props 或狀態動態決定要渲染的 HTML 標籤。

```svelte
<!-- src/lib/components/Heading.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    level: 1 | 2 | 3 | 4 | 5 | 6;
    children: Snippet;
  }

  let { level, children }: Props = $props();

  let tag = $derived(`h${level}` as const);
</script>

<svelte:element this={tag}>
  {@render children()}
</svelte:element>
```

```svelte
<!-- 使用方式 -->
<script lang="ts">
  import Heading from '$lib/components/Heading.svelte';
</script>

<Heading level={1}>Main Title</Heading>
<Heading level={2}>Subtitle</Heading>
<Heading level={3}>Section</Heading>
```

`<svelte:element>` 讓你建立語意靈活的通用元件，根據上下文渲染不同的 HTML 標籤，同時保持單一元件的結構。

## Hands-on Lab

任務：運用 snippets 與元件組合模式，建立可複用的 UI 元件。

### Foundation 基礎層

建立一個 `Card` 元件，支援 `children` snippet 和一個 `badge` snippet prop：

- 使用 `children` snippet 作為卡片的主要內容區域。
- 定義一個可選的 `badge: Snippet<[string]>` prop，用於在卡片右上角渲染一個標籤（如 "NEW"、"SALE"）。
- 為 `children` 和 `badge` 加上正確的 TypeScript 型別。
- 在父元件中建立多張 Card，部分傳入 badge、部分不傳。

**驗收條件：**
- [ ] 成功定義至少一個 `{#snippet}` 並使用 `{@render}` 呈現。
- [ ] 瀏覽器顯示 snippet 渲染結果正確。
- [ ] `children` snippet 正確接收並渲染父元件傳入的內容。
- [ ] 可選的 `badge` snippet prop 在傳入時渲染、未傳入時不渲染。
- [ ] TypeScript 型別標註完整（`Snippet`、`Snippet<[string]>`），`npx svelte-check` 通過。

### Advanced 進階層

建立一個型別安全的 `DataTable` 元件，支援 `header` 和 `row` snippet props：

- 使用 `generics="T"` 讓 `DataTable` 支援任意資料型別。
- `header: Snippet` 用於渲染表頭列。
- `row: Snippet<[T, number]>` 用於渲染每一資料列，接收資料項與索引。
- `empty?: Snippet` 用於在無資料時渲染空狀態提示。
- 在父元件中用不同的資料型別（如 `User[]`、`Product[]`）使用同一個 `DataTable`，驗證型別推導正確。

### Challenge 挑戰層

建立一個動態表單渲染器，使用 `<svelte:component>` 根據設定渲染不同的欄位類型：

- 定義一個表單設定陣列，每項包含 `type`（text、number、select、checkbox）、`label`、`name` 等欄位。
- 為每種欄位類型建立對應的元件（`TextField`、`NumberField`、`SelectField`、`CheckboxField`）。
- 使用 `<svelte:component>` 根據 `type` 動態渲染對應的元件。
- 使用 snippet prop 讓外部自訂欄位的 label 渲染方式。
- 收集所有欄位的值為一個 reactive object，並在表單下方即時顯示 JSON 結果。

## Reference Solution

完整的 `DataTable` 泛型元件與使用範例，涵蓋 snippet props、TypeScript 泛型、`children` snippet 與 named snippets。

```svelte
<!-- src/lib/components/DataTable.svelte -->
<script lang="ts" generics="T">
  import type { Snippet } from 'svelte';

  interface Props {
    items: T[];
    header: Snippet;
    row: Snippet<[T, number]>;
    empty?: Snippet;
  }

  let { items, header, row, empty }: Props = $props();
</script>

<table>
  <thead>
    {@render header()}
  </thead>
  <tbody>
    {#if items.length === 0 && empty}
      <tr><td>{@render empty()}</td></tr>
    {:else}
      {#each items as item, i (i)}
        {@render row(item, i)}
      {/each}
    {/if}
  </tbody>
</table>
```

```svelte
<!-- src/routes/ch08/+page.svelte -->
<script lang="ts">
  import DataTable from '$lib/components/DataTable.svelte';

  interface User {
    id: number;
    name: string;
    email: string;
  }

  let users = $state<User[]>([
    { id: 1, name: 'Alice', email: 'alice@example.com' },
    { id: 2, name: 'Bob', email: 'bob@example.com' },
  ]);
</script>

<DataTable items={users}>
  {#snippet header()}
    <tr><th>Name</th><th>Email</th></tr>
  {/snippet}

  {#snippet row(user, index)}
    <tr>
      <td>{user.name}</td>
      <td>{user.email}</td>
    </tr>
  {/snippet}

  {#snippet empty()}
    <p>No users found.</p>
  {/snippet}
</DataTable>
```

完整的 `Card` 元件，示範 `children` 與可選 snippet prop 的搭配。

```svelte
<!-- src/lib/components/Card.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    children: Snippet;
    badge?: Snippet<[string]>;
    badgeText?: string;
  }

  let { children, badge, badgeText = '' }: Props = $props();
</script>

<div class="card">
  {#if badge && badgeText}
    <div class="card-badge">
      {@render badge(badgeText)}
    </div>
  {/if}
  <div class="card-content">
    {@render children()}
  </div>
</div>
```

```svelte
<!-- 使用方式 -->
<script lang="ts">
  import Card from '$lib/components/Card.svelte';
</script>

<Card badgeText="NEW">
  <h3>Product A</h3>
  <p>Description of product A.</p>

  {#snippet badge(text)}
    <span class="badge badge-new">{text}</span>
  {/snippet}
</Card>

<Card>
  <h3>Product B</h3>
  <p>No badge on this card.</p>
</Card>
```

## Common Pitfalls

- **使用 `<slot>` 而非 `{@render children()}`**：Svelte 5 以 snippet 系統完全取代了 Svelte 4 的 slot 機制。如果你在 Svelte 5 中寫 `<slot>`，編譯器會發出 deprecation 警告。遷移方式：`<slot>` → `{@render children()}`，並在 `Props` 介面中宣告 `children: Snippet`。
- **使用 `<slot name="header">` 而非 named snippet props**：Svelte 4 的 `<slot name="header">` 在 Svelte 5 中應改為將 `header` 定義為 `Snippet` 型別的 prop，在模板中用 `{@render header()}` 渲染。父元件端則用 `{#snippet header()}...{/snippet}` 在子元件標籤內定義。
- **忘記從 `svelte` 匯入 `Snippet` 型別**：在 TypeScript 中為 snippet prop 加型別時，必須 `import type { Snippet } from 'svelte'`。忘記匯入會導致型別錯誤 `Cannot find name 'Snippet'`。
- **定義了 snippet 卻忘記 `{@render}`**：`{#snippet}` 區塊本身不會產生任何 DOM 輸出，它只是定義一個可渲染的模板片段。必須搭配 `{@render snippetName()}` 才會實際渲染到頁面上。常見的錯誤是定義了 snippet 後就以為它會自動出現。
- **混淆 snippets（模板複用）與 components（封裝邏輯與狀態）**：Snippet 適合消除同一元件內的模板重複，但它不擁有自己的 `<script>` 區塊、不能有獨立的生命週期或響應式狀態。當模板片段需要自己的狀態或邏輯時，應該抽成獨立元件。

## Checklist

- [ ] 能使用 `{#snippet}` 定義 local snippet 並用 `{@render}` 渲染。
- [ ] 能將 snippet 作為 prop 傳入子元件，並使用 `Snippet<[...]>` 正確標注型別。
- [ ] 能使用 `children` snippet 取代 Svelte 4 的 `<slot>`，實現內容包裝。
- [ ] 能使用 named snippets 取代 Svelte 4 的 named slots，實現多插入點的元件。
- [ ] 能使用 `<svelte:component this={...}>` 根據條件動態渲染不同元件。
- [ ] 能使用 `<svelte:element this={tag}>` 動態決定 HTML 標籤。
- [ ] `npx svelte-check` 通過，無型別錯誤。

## Further Reading

- [Svelte Docs — {#snippet ...}](https://svelte.dev/docs/svelte/snippet)
- [Svelte Docs — {@render ...}](https://svelte.dev/docs/svelte/render)
- [Svelte Docs — Snippet type](https://svelte.dev/docs/svelte/Snippet)
- [Svelte Docs — <svelte:component>](https://svelte.dev/docs/svelte/svelte-component)
- [Svelte Docs — <svelte:element>](https://svelte.dev/docs/svelte/svelte-element)
- [Svelte Tutorial — Snippets](https://svelte.dev/tutorial/svelte/snippets)
- [Svelte 5 Migration Guide — Slots to Snippets](https://svelte.dev/docs/svelte/v5-migration-guide#Snippets-instead-of-slots)
