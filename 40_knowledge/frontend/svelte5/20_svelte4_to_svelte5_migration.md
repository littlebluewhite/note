---
title: "Svelte 4 to Svelte 5 Migration / Svelte 4 到 5 遷移指南"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "20"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [00_series_overview]
---

# Svelte 4 to Svelte 5 Migration / Svelte 4 到 5 遷移指南

## Goal

系統性地掌握從 Svelte 4 遷移到 Svelte 5 的完整流程。Svelte 5 帶來了根本性的 reactivity 架構變革——從隱式的編譯器魔法（`$:` label、`let` 自動響應）轉向顯式的 Runes 系統（`$state`、`$derived`、`$effect`），同時也翻新了事件處理、slot 機制與元件實例化 API。

本章提供完整的語法對照表、自動化遷移工具的使用方式、漸進式遷移策略，以及遷移決策矩陣，幫助你在實際專案中做出正確的遷移判斷。無論是維護既有 Svelte 4 專案還是規劃全面升級，本章都能提供可執行的步驟與避坑指南。

- 銜接上一章：前面章節已學會 Svelte 5 的所有核心語法與 SvelteKit 功能，現在要學習如何將既有 Svelte 4 程式碼升級到 Svelte 5。
- 下一章預告：Ch21 將介紹 Svelte 5 生態系中的常用套件與工具選型。

## Prerequisites

- 已完成 Ch00 系列總覽，理解 Svelte 5 的核心理念與 Runes 概念。
- 對 Svelte 4 語法有基本認識（`$:` reactive statements、`export let`、`on:event`、`<slot>`）。
- 具備 TypeScript 基礎型別標註能力。
- 有至少一個 Svelte 4 專案的開發經驗（建議但非必要）。

## Core Concepts

### 1. 完整語法遷移對照表

以下表格涵蓋 Svelte 4 到 Svelte 5 的所有主要語法變更。建議收藏此表作為遷移時的快速查閱手冊。

| 用途 | Svelte 4 | Svelte 5 |
|------|----------|----------|
| 響應式狀態 | `let x = 0` | `let x = $state(0)` |
| 衍生計算 | `$: doubled = x * 2` | `let doubled = $derived(x * 2)` |
| 多行衍生 | `$: { ... }` (reactive statement) | `let val = $derived.by(() => { ... })` |
| 副作用 | `$: { console.log(x) }` | `$effect(() => { console.log(x) })` |
| Props 宣告 | `export let name` | `let { name } = $props()` |
| Props 預設值 | `export let name = 'World'` | `let { name = 'World' } = $props()` |
| 可綁定 Props | `export let value` | `let { value = $bindable(0) } = $props()` |
| 事件處理 | `on:click={handler}` | `onclick={handler}` |
| 事件修飾符 | `on:click\|preventDefault` | 在 handler 中手動呼叫 `e.preventDefault()` |
| 元件事件 | `createEventDispatcher()` | callback props（傳入函式） |
| 預設 Slot | `<slot />` | `{@render children()}` |
| 具名 Slot | `<slot name="header">` | snippet props `{@render header()}` |
| Slot Props | `<slot {item}>` | `{@render row(item)}` |
| Slot 回退內容 | `<slot>fallback</slot>` | `{#if children}{@render children()}{:else}fallback{/if}` |
| 元件實例化 | `new Component({ target })` | `mount(Component, { target })` |
| Hydration | `new Component({ target, hydrate: true })` | `hydrate(Component, { target })` |
| 元件解除 | `component.$destroy()` | `unmount(component)` |

#### 事件處理遷移細節

Svelte 4 的事件修飾符（`|preventDefault`、`|stopPropagation`、`|once` 等）在 Svelte 5 中被移除，需在 handler 中手動處理：

```svelte
<!-- Svelte 4 -->
<form on:submit|preventDefault={handleSubmit}>
  <button on:click|once|stopPropagation={handleClick}>Click</button>
</form>

<!-- Svelte 5 -->
<script lang="ts">
  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    // submit logic
  }

  function handleClickOnce() {
    // 使用閉包模擬 |once
    let called = false;
    return (e: MouseEvent) => {
      if (called) return;
      called = true;
      e.stopPropagation();
      // click logic
    };
  }
</script>

<form onsubmit={handleSubmit}>
  <button onclick={handleClickOnce()}>Click</button>
</form>
```

#### 元件事件遷移細節

```svelte
<!-- Svelte 4：子元件使用 createEventDispatcher -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher<{ save: { data: string } }>();

  function handleSave() {
    dispatch('save', { data: 'hello' });
  }
</script>
<button on:click={handleSave}>Save</button>

<!-- Svelte 5：子元件改用 callback props -->
<script lang="ts">
  let { onSave } = $props<{ onSave: (data: string) => void }>();

  function handleSave() {
    onSave('hello');
  }
</script>
<button onclick={handleSave}>Save</button>
```

- **何時用此對照表**：在遷移專案中逐一轉換語法時，作為 cheat sheet 快速查閱。
- **何時不用**：全新 Svelte 5 專案不需要此對照表，直接使用 Svelte 5 語法即可。

### 2. `npx sv migrate svelte-5` 自動化遷移工具

Svelte 官方提供了自動化遷移工具，可以批次轉換大部分語法變更，大幅減少手動工作量。

#### 如何執行

```bash
# 在專案根目錄執行
npx sv migrate svelte-5
```

執行後，工具會掃描所有 `.svelte` 檔案並自動轉換語法。

#### 工具自動處理的項目

- `let x = 0` 轉換為 `let x = $state(0)`
- `$: doubled = x * 2` 轉換為 `let doubled = $derived(x * 2)`
- `$: { ... }` 轉換為 `$effect(() => { ... })`
- `export let` 轉換為 `$props()` 解構
- `on:click` 轉換為 `onclick`
- `<slot />` 轉換為 `{@render children()}`
- `createEventDispatcher` 轉換為 callback props
- 事件修飾符移除並加入手動 `e.preventDefault()` 等

#### 需要手動介入的項目

- **複雜的 `$:` reactive statements**：包含多重依賴、條件判斷或非標準寫法的 reactive 區塊可能轉換不正確。
- **自定義 Store 邏輯**：使用 `writable`/`readable` 且包含自定義 `set`/`update` 邏輯的 store，工具無法完整轉換。
- **進階 Slot 模式**：巢狀 slot、條件式 slot 等複雜模式需手動檢查。
- **動態元件事件**：透過動態字串分派事件的模式無法自動遷移。
- **生命週期函式中的響應式邏輯**：`onMount` 中使用 `$:` 的間接模式需手動處理。

#### 建議工作流程

```
1. 建立遷移分支        → git checkout -b migrate-svelte5
2. 執行自動遷移工具    → npx sv migrate svelte-5
3. 檢視變更差異        → git diff
4. 修正手動項目        → 逐一檢查轉換結果
5. 執行型別檢查        → npx svelte-check
6. 執行測試            → npm run test
7. 合併遷移分支        → git merge migrate-svelte5
```

- **何時用自動化工具**：專案有大量 `.svelte` 檔案需要遷移時，先用工具處理 80% 的機械性轉換，再手動修正剩餘 20%。
- **何時不用**：少量元件（< 5 個）的小專案，手動遷移可能更快更精確。

### 3. 漸進式遷移策略

Svelte 5 的一大優勢是支援 Svelte 4 與 Svelte 5 元件在同一專案中共存，讓你可以逐步遷移而非一次性全面翻新。

#### 共存規則

- Svelte 4 語法與 Svelte 5 Runes 語法**可以在同一個 app 中共存**（不同元件使用不同語法）。
- 但**不可以在同一個元件中混用** `$:` 和 runes（如 `$state`、`$derived`、`$effect`）。一個元件要嘛全用 Svelte 4 語法，要嘛全用 Svelte 5 語法。
- Svelte 4 元件可以匯入 Svelte 5 元件作為子元件，反之亦然。

#### 建議遷移順序

```
1. 葉節點元件（Leaf Components）
   → 按鈕、圖標、Badge 等無子元件的末端元件
   → 風險最低，不影響其他元件

2. 共享元件（Shared Components）
   → Modal、Toast、Form 元素等跨頁面使用的元件
   → 遷移後受益最大

3. Layout 元件
   → +layout.svelte 檔案
   → 影響範圍較廣，需仔細測試

4. 頁面元件（Page Components）
   → +page.svelte 檔案
   → 最後遷移，因為通常邏輯最複雜
```

#### 遷移時機判斷

- **立即遷移**：新開發的功能模組、正在重構的元件、頻繁修改的元件。
- **延後遷移**：穩定運作且不常修改的元件、即將被棄用的功能、外部依賴尚未支援 Svelte 5 的模組。
- **不需遷移**：即將移除的 legacy 功能、短期存在的實驗性元件。

- **何時用漸進式策略**：中大型專案（> 50 個元件），一次性遷移風險太高且團隊無法停下業務開發時。
- **何時不用**：小專案可以一次全面遷移，省去維護兩套語法的心智負擔。

### 4. 遷移決策矩陣

根據專案特性決定遷移策略：

| 專案特性 | 建議策略 | 理由 |
|----------|----------|------|
| 新專案 | 直接使用 Svelte 5 | 無歷史負擔，直接享受新語法優勢 |
| 小型專案（< 20 元件） | 一次性全面遷移 | 工作量小，可一次完成 |
| 中型專案（20-100 元件） | 漸進式遷移 + 自動化工具 | 用工具處理批量轉換，分批驗證 |
| 大型專案（> 100 元件） | 漸進式遷移 + 優先級排序 | 按模組分批遷移，避免影響業務 |
| 使用大量自定義 Store | 評估後決定 | Store 遷移複雜度高，需先驗證替代方案 |
| 高測試覆蓋率 | 大膽遷移 | 測試提供安全網，可快速驗證正確性 |
| 低測試覆蓋率 | 保守遷移 + 先補測試 | 先為關鍵路徑補充測試再遷移 |
| 外部套件依賴多 | 先確認套件相容性 | 部分套件可能尚未適配 Svelte 5 |

- **何時參考此矩陣**：在專案遷移規劃階段，需要說服團隊或產出遷移計畫文件時。
- **何時不用**：已經明確知道遷移策略的情況下。

## Step-by-step

### Step 1：使用自動遷移工具處理示範元件

假設你有一個 Svelte 4 的計數器元件。首先建立遷移分支並執行工具：

```bash
# 建立遷移分支
git checkout -b migrate-svelte5

# 執行自動遷移
npx sv migrate svelte-5

# 檢視所有變更
git diff
```

工具會自動轉換以下 Svelte 4 程式碼：

```svelte
<!-- 遷移前：Svelte 4 -->
<script lang="ts">
  let count = 0;
  $: doubled = count * 2;
  $: if (count > 10) {
    console.log('Count is high!');
  }
</script>

<button on:click={() => count++}>{count} x2 = {doubled}</button>
```

### Step 2：遷移 `let` 到 `$state`

將所有需要響應性的變數宣告加上 `$state`：

```svelte
<script lang="ts">
  // Before
  let count = 0;
  let name = 'World';
  let items: string[] = [];

  // After
  let count = $state(0);
  let name = $state('World');
  let items = $state<string[]>([]);
</script>
```

注意：不是所有 `let` 都需要改為 `$state`。如果變數從未被修改，或僅在初始化時賦值一次，就不需要 `$state`：

```svelte
<script lang="ts">
  // 這些不需要 $state，因為值不會改變
  let API_URL = '/api/v1';
  let formatter = new Intl.NumberFormat('zh-TW');
</script>
```

### Step 3：遷移 `$:` 衍生值到 `$derived`

```svelte
<script lang="ts">
  let count = $state(0);
  let price = $state(100);
  let quantity = $state(2);

  // Before (Svelte 4)
  // $: doubled = count * 2;
  // $: total = price * quantity;
  // $: summary = `${quantity} items, total: $${total}`;

  // After (Svelte 5)
  let doubled = $derived(count * 2);
  let total = $derived(price * quantity);
  let summary = $derived(`${quantity} items, total: $${total}`);
</script>
```

對於多行衍生計算，使用 `$derived.by`：

```svelte
<script lang="ts">
  let items = $state<{ name: string; price: number; qty: number }[]>([]);

  // Before (Svelte 4)
  // $: totalPrice = items.reduce((sum, item) => {
  //   return sum + item.price * item.qty;
  // }, 0);

  // After (Svelte 5)
  let totalPrice = $derived.by(() => {
    return items.reduce((sum, item) => {
      return sum + item.price * item.qty;
    }, 0);
  });
</script>
```

### Step 4：遷移 `$:` 副作用到 `$effect`

```svelte
<script lang="ts">
  let count = $state(0);
  let searchQuery = $state('');

  // Before (Svelte 4)
  // $: {
  //   console.log('count changed:', count);
  // }
  // $: if (searchQuery.length > 2) {
  //   fetchResults(searchQuery);
  // }

  // After (Svelte 5)
  $effect(() => {
    console.log('count changed:', count);
  });

  $effect(() => {
    if (searchQuery.length > 2) {
      fetchResults(searchQuery);
    }
  });

  async function fetchResults(query: string) {
    const res = await fetch(`/api/search?q=${query}`);
    // handle response
  }
</script>
```

### Step 5：遷移 `export let` 到 `$props`

```svelte
<script lang="ts">
  // Before (Svelte 4)
  // export let name: string;
  // export let count = 0;
  // export let items: string[] = [];
  // export let onSave: (data: string) => void;

  // After (Svelte 5)
  let {
    name,
    count = 0,
    items = [],
    onSave
  } = $props<{
    name: string;
    count?: number;
    items?: string[];
    onSave: (data: string) => void;
  }>();
</script>
```

若 prop 需要支援 `bind:` 雙向綁定，使用 `$bindable`：

```svelte
<script lang="ts">
  // Before (Svelte 4)
  // export let value = '';

  // After (Svelte 5) — 支援 bind:value
  let { value = $bindable('') } = $props<{ value?: string }>();
</script>
```

### Step 6：遷移 `on:click` 到 `onclick` 並移除事件修飾符

```svelte
<!-- Before (Svelte 4) -->
<button on:click={handleClick}>Click</button>
<form on:submit|preventDefault={handleSubmit}>
  <input on:keydown|stopPropagation={handleKey} />
  <a href="/link" on:click|preventDefault|once={handleLink}>Link</a>
</form>

<!-- After (Svelte 5) -->
<script lang="ts">
  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    // submit logic
  }

  function handleKey(e: KeyboardEvent) {
    e.stopPropagation();
    // key logic
  }

  let linkClicked = false;
  function handleLink(e: MouseEvent) {
    e.preventDefault();
    if (linkClicked) return;
    linkClicked = true;
    // link logic
  }
</script>

<button onclick={handleClick}>Click</button>
<form onsubmit={handleSubmit}>
  <input onkeydown={handleKey} />
  <a href="/link" onclick={handleLink}>Link</a>
</form>
```

### Step 7：遷移 `createEventDispatcher` 到 callback props

```svelte
<!-- Before: Child (Svelte 4) -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher<{
    save: { id: number; name: string };
    cancel: void;
  }>();
</script>
<button on:click={() => dispatch('save', { id: 1, name: 'test' })}>Save</button>
<button on:click={() => dispatch('cancel')}>Cancel</button>

<!-- Before: Parent (Svelte 4) -->
<Child on:save={(e) => handleSave(e.detail)} on:cancel={handleCancel} />

<!-- After: Child (Svelte 5) -->
<script lang="ts">
  let { onSave, onCancel } = $props<{
    onSave: (data: { id: number; name: string }) => void;
    onCancel: () => void;
  }>();
</script>
<button onclick={() => onSave({ id: 1, name: 'test' })}>Save</button>
<button onclick={onCancel}>Cancel</button>

<!-- After: Parent (Svelte 5) -->
<Child onSave={handleSave} onCancel={handleCancel} />
```

注意 Svelte 4 的 `e.detail` 在 Svelte 5 中不再需要，因為 callback props 直接傳遞資料。

### Step 8：遷移 `<slot>` 到 Snippets

```svelte
<!-- Before: Card 元件 (Svelte 4) -->
<div class="card">
  <div class="card-header">
    <slot name="header">Default Header</slot>
  </div>
  <div class="card-body">
    <slot />
  </div>
  <div class="card-footer">
    <slot name="footer" />
  </div>
</div>

<!-- Before: 使用 Card (Svelte 4) -->
<Card>
  <svelte:fragment slot="header">
    <h2>My Title</h2>
  </svelte:fragment>

  <p>Card body content</p>

  <svelte:fragment slot="footer">
    <button>OK</button>
  </svelte:fragment>
</Card>
```

```svelte
<!-- After: Card 元件 (Svelte 5) -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    header,
    children,
    footer
  } = $props<{
    header?: Snippet;
    children: Snippet;
    footer?: Snippet;
  }>();
</script>

<div class="card">
  <div class="card-header">
    {#if header}
      {@render header()}
    {:else}
      Default Header
    {/if}
  </div>
  <div class="card-body">
    {@render children()}
  </div>
  {#if footer}
    <div class="card-footer">
      {@render footer()}
    </div>
  {/if}
</div>

<!-- After: 使用 Card (Svelte 5) -->
<Card>
  {#snippet header()}
    <h2>My Title</h2>
  {/snippet}

  <p>Card body content</p>

  {#snippet footer()}
    <button>OK</button>
  {/snippet}
</Card>
```

對於有 slot props 的情況：

```svelte
<!-- Before: List (Svelte 4) -->
<ul>
  {#each items as item}
    <li><slot {item} /></li>
  {/each}
</ul>

<!-- After: List (Svelte 5) -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  let { items, row } = $props<{
    items: string[];
    row: Snippet<[string]>;
  }>();
</script>
<ul>
  {#each items as item}
    <li>{@render row(item)}</li>
  {/each}
</ul>

<!-- 使用 (Svelte 5) -->
<List items={['a', 'b', 'c']}>
  {#snippet row(item)}
    <span>{item.toUpperCase()}</span>
  {/snippet}
</List>
```

## Hands-on Lab

### Foundation 基礎層

**任務**：將一個 Svelte 4 計數器元件遷移到 Svelte 5。

要求：
- 將以下 Svelte 4 程式碼逐行遷移為 Svelte 5 語法。
- 遷移所有響應式變數（`let` → `$state`）。
- 遷移所有衍生值（`$:` → `$derived`）。
- 遷移事件處理（`on:click` → `onclick`）。
- 確保功能完全一致。

原始 Svelte 4 程式碼：

```svelte
<script lang="ts">
  let count = 0;
  let step = 1;
  $: doubled = count * 2;
  $: isEven = count % 2 === 0;
  $: label = `Count: ${count} (${isEven ? 'even' : 'odd'})`;
</script>

<h1>{label}</h1>
<p>Doubled: {doubled}</p>
<label>Step: <input type="number" bind:value={step} /></label>
<button on:click={() => count += step}>+ {step}</button>
<button on:click={() => count -= step}>- {step}</button>
<button on:click={() => count = 0}>Reset</button>
```

驗收條件：
- 遷移後功能與原版完全一致。
- 無任何 Svelte 4 語法殘留（無 `$:`、無 `on:`）。
- `npx svelte-check` 通過。

### Advanced 進階層

**任務**：遷移一個包含表單、事件派發與 Store 的元件。

要求：
- 遷移一個使用 `createEventDispatcher` 的子元件為 callback props。
- 遷移一個使用 `writable` store 的表單元件為 `$state` + context。
- 遷移表單的 `on:submit|preventDefault` 語法。
- 確保父子元件的資料流正確。

驗收條件：
- 父元件可正確接收子元件的事件回呼。
- 表單驗證與提交功能正常。
- 無 `createEventDispatcher` 殘留。
- `npx svelte-check` 通過。

### Challenge 挑戰層

**任務**：遷移一個包含具名 slot、slot props 與動態元件的元件庫。

要求：
- 遷移至少 3 個互相依賴的元件（Card、Modal、DataTable）。
- Card 使用具名 slot → 遷移為 snippet props。
- Modal 使用 slot 傳遞關閉函式 → 遷移為 snippet with argument。
- DataTable 使用 slot props 渲染自定義欄位 → 遷移為 snippet。
- 所有元件的使用端（consumer）也一併遷移。

驗收條件：
- 三個元件在遷移後功能完全一致。
- 所有使用端程式碼也已遷移。
- 無 `<slot>` 語法殘留。
- `npx svelte-check` 通過。

## Reference Solution

### Foundation：遷移後的計數器

```svelte
<!-- src/routes/migrated-counter/+page.svelte -->
<script lang="ts">
  let count = $state(0);
  let step = $state(1);
  let doubled = $derived(count * 2);
  let isEven = $derived(count % 2 === 0);
  let label = $derived(`Count: ${count} (${isEven ? 'even' : 'odd'})`);
</script>

<h1>{label}</h1>
<p>Doubled: {doubled}</p>
<label>Step: <input type="number" bind:value={step} /></label>
<button onclick={() => count += step}>+ {step}</button>
<button onclick={() => count -= step}>- {step}</button>
<button onclick={() => count = 0}>Reset</button>
```

### Advanced：遷移後的表單元件

```svelte
<!-- src/lib/components/ContactForm.svelte (Svelte 5) -->
<script lang="ts">
  interface ContactData {
    name: string;
    email: string;
    message: string;
  }

  let {
    onSubmit,
    onCancel
  } = $props<{
    onSubmit: (data: ContactData) => void;
    onCancel: () => void;
  }>();

  let name = $state('');
  let email = $state('');
  let message = $state('');
  let errors = $state<Record<string, string>>({});

  let isValid = $derived(
    name.trim().length > 0 &&
    email.includes('@') &&
    message.trim().length > 0
  );

  function validate(): boolean {
    const newErrors: Record<string, string> = {};
    if (!name.trim()) newErrors.name = 'Name is required';
    if (!email.includes('@')) newErrors.email = 'Invalid email';
    if (!message.trim()) newErrors.message = 'Message is required';
    errors = newErrors;
    return Object.keys(newErrors).length === 0;
  }

  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({ name, email, message });
  }
</script>

<form onsubmit={handleSubmit}>
  <div>
    <label for="name">Name</label>
    <input id="name" bind:value={name} />
    {#if errors.name}<span class="error">{errors.name}</span>{/if}
  </div>

  <div>
    <label for="email">Email</label>
    <input id="email" type="email" bind:value={email} />
    {#if errors.email}<span class="error">{errors.email}</span>{/if}
  </div>

  <div>
    <label for="message">Message</label>
    <textarea id="message" bind:value={message}></textarea>
    {#if errors.message}<span class="error">{errors.message}</span>{/if}
  </div>

  <div>
    <button type="submit" disabled={!isValid}>Submit</button>
    <button type="button" onclick={onCancel}>Cancel</button>
  </div>
</form>

<style>
  .error { color: red; font-size: 0.875rem; }
</style>
```

```svelte
<!-- src/routes/contact/+page.svelte (Svelte 5) -->
<script lang="ts">
  import ContactForm from '$lib/components/ContactForm.svelte';

  let submitted = $state(false);

  function handleSubmit(data: { name: string; email: string; message: string }) {
    console.log('Form submitted:', data);
    submitted = true;
  }

  function handleCancel() {
    history.back();
  }
</script>

{#if submitted}
  <p>Thank you for your message!</p>
{:else}
  <ContactForm onSubmit={handleSubmit} onCancel={handleCancel} />
{/if}
```

### Challenge：遷移後的 Card 元件

```svelte
<!-- src/lib/components/Card.svelte (Svelte 5) -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    header,
    children,
    footer,
    variant = 'default'
  } = $props<{
    header?: Snippet;
    children: Snippet;
    footer?: Snippet;
    variant?: 'default' | 'outlined' | 'elevated';
  }>();
</script>

<div class="card card-{variant}">
  {#if header}
    <div class="card-header">
      {@render header()}
    </div>
  {/if}

  <div class="card-body">
    {@render children()}
  </div>

  {#if footer}
    <div class="card-footer">
      {@render footer()}
    </div>
  {/if}
</div>

<style>
  .card { border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; }
  .card-elevated { box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); }
  .card-outlined { border: 2px solid #333; }
  .card-header { padding: 1rem; border-bottom: 1px solid #e0e0e0; font-weight: bold; }
  .card-body { padding: 1rem; }
  .card-footer { padding: 1rem; border-top: 1px solid #e0e0e0; }
</style>
```

```svelte
<!-- src/lib/components/Modal.svelte (Svelte 5) -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    open = $bindable(false),
    title,
    children,
    footer
  } = $props<{
    open?: boolean;
    title: string;
    children: Snippet<[() => void]>;
    footer?: Snippet<[() => void]>;
  }>();

  function close() {
    open = false;
  }
</script>

{#if open}
  <div class="backdrop" onclick={close} role="presentation">
    <div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
      <header>
        <h2>{title}</h2>
        <button onclick={close} aria-label="Close">&times;</button>
      </header>
      <div class="content">
        {@render children(close)}
      </div>
      {#if footer}
        <div class="footer">
          {@render footer(close)}
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .backdrop {
    position: fixed; inset: 0; background: rgba(0, 0, 0, 0.5);
    display: flex; align-items: center; justify-content: center;
  }
  .modal { background: white; border-radius: 8px; min-width: 400px; max-width: 90vw; }
  header { display: flex; justify-content: space-between; padding: 1rem; border-bottom: 1px solid #e0e0e0; }
  .content { padding: 1rem; }
  .footer { padding: 1rem; border-top: 1px solid #e0e0e0; }
</style>
```

```svelte
<!-- 使用遷移後的元件 -->
<script lang="ts">
  import Card from '$lib/components/Card.svelte';
  import Modal from '$lib/components/Modal.svelte';

  let showModal = $state(false);
</script>

<Card variant="elevated">
  {#snippet header()}
    <h3>User Profile</h3>
  {/snippet}

  <p>Card content goes here.</p>

  {#snippet footer()}
    <button onclick={() => showModal = true}>Open Modal</button>
  {/snippet}
</Card>

<Modal bind:open={showModal} title="Confirm Action">
  {#snippet children(close)}
    <p>Are you sure you want to proceed?</p>
    <button onclick={close}>Cancel</button>
  {/snippet}

  {#snippet footer(close)}
    <button onclick={close}>Confirm</button>
  {/snippet}
</Modal>
```

## Common Pitfalls

1. **在同一元件中混用 Svelte 4 和 Svelte 5 語法**
   一個元件必須完全使用 Svelte 4 或完全使用 Svelte 5 語法，不可混用。Compiler 偵測到 runes 後會以 rune mode 編譯該元件，`$:` 將被視為普通 JavaScript label 而非 reactive statement。

   ```svelte
   <!-- Bad: 混用 -->
   <script lang="ts">
     let count = $state(0);       // Svelte 5 rune
     $: doubled = count * 2;      // Svelte 4 語法 — 不會有響應性！
   </script>

   <!-- Good: 全部使用 Svelte 5 -->
   <script lang="ts">
     let count = $state(0);
     let doubled = $derived(count * 2);
   </script>
   ```

2. **遷移事件時忘記手動處理修飾符**
   Svelte 5 移除了所有事件修飾符。如果原本有 `|preventDefault`、`|stopPropagation`、`|once` 等修飾符，必須在 handler 中手動實作。自動遷移工具會處理大多數情況，但建議逐一確認。

   ```svelte
   <!-- Bad: 忘記 preventDefault -->
   <script lang="ts">
     function handleSubmit() {
       // 表單會被真的提交！
       console.log('submitted');
     }
   </script>
   <form onsubmit={handleSubmit}>...</form>

   <!-- Good: 手動加上 preventDefault -->
   <script lang="ts">
     function handleSubmit(e: SubmitEvent) {
       e.preventDefault();
       console.log('submitted');
     }
   </script>
   <form onsubmit={handleSubmit}>...</form>
   ```

3. **Slot 回退內容遷移不完整**
   Svelte 4 的 `<slot>fallback</slot>` 語法在 Svelte 5 中需要用 `{#if}` 條件判斷實作：

   ```svelte
   <!-- Bad: 直接 render 可能報錯 -->
   <script lang="ts">
     import type { Snippet } from 'svelte';
     let { children } = $props<{ children?: Snippet }>();
   </script>
   {@render children()}  <!-- children 可能是 undefined -->

   <!-- Good: 加上 fallback 條件 -->
   {#if children}
     {@render children()}
   {:else}
     <p>Default content</p>
   {/if}
   ```

4. **Store 訂閱語法的變化**
   Svelte 4 中 `$storeName` 語法糖仍可在 Svelte 5 元件中使用（因為 stores 與 runes 可以共存），但若想完全遷移到 runes，需要將 store 替換為 `$state`：

   ```ts
   // Before: Svelte 4 store
   // import { writable } from 'svelte/store';
   // export const count = writable(0);

   // After: Svelte 5 rune（在 .svelte.ts 檔案中）
   // src/lib/state/count.svelte.ts
   let count = $state(0);
   export function getCount() { return count; }
   export function setCount(value: number) { count = value; }
   export function increment() { count++; }
   ```

   注意：store 的 `$` 前綴語法仍可使用，但不能與 runes 在同一元件中混用。

5. **元件實例化 API 變更**
   Svelte 5 不再支援 `new Component()` 語法。如果你有在 JavaScript 中動態建立元件的程式碼（常見於測試或嵌入式使用），必須遷移為 `mount()`/`hydrate()`：

   ```ts
   // Before (Svelte 4)
   // const app = new App({
   //   target: document.getElementById('app')!,
   //   props: { name: 'World' }
   // });
   // app.$destroy();

   // After (Svelte 5)
   import { mount, unmount } from 'svelte';
   import App from './App.svelte';

   const app = mount(App, {
     target: document.getElementById('app')!,
     props: { name: 'World' }
   });
   unmount(app);
   ```

## Checklist

- [ ] 能使用語法對照表將 Svelte 4 程式碼逐一轉換為 Svelte 5 語法
- [ ] 能執行 `npx sv migrate svelte-5` 自動遷移工具並正確檢視結果
- [ ] 能識別自動遷移工具無法處理的情況並手動修正
- [ ] 能規劃漸進式遷移策略，決定元件遷移優先順序
- [ ] 能正確遷移 `<slot>` 到 snippets（包含具名 slot 與 slot props）
- [ ] 遷移後 `npx svelte-check` 通過，無型別錯誤且功能完全一致

## Further Reading

- [Svelte 5 Migration Guide](https://svelte.dev/docs/svelte/v5-migration-guide)
- [Svelte 5 Deprecations](https://svelte.dev/docs/svelte/v5-migration-guide#Components-are-no-longer-classes)
- [sv migrate Command](https://svelte.dev/docs/cli/sv-migrate)
- [Svelte 5 Runes Documentation](https://svelte.dev/docs/svelte/$state)
- [Svelte 5 Snippets Documentation](https://svelte.dev/docs/svelte/snippet)
- [Svelte GitHub Repository](https://github.com/sveltejs/svelte)
