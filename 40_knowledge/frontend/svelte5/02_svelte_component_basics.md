---
title: "Svelte Component Basics / Svelte 元件基礎"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-17
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "02"
level: beginner
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [01_web_js_fundamentals_for_svelte]
---
# Svelte Component Basics / Svelte 元件基礎

## Goal

理解 `.svelte` 檔案的組成結構，學會使用 `$props()` 接收外部資料，並用 `{@render children()}` 做內容投影。

元件是 Svelte 應用的基本構建單位，所有 UI 邏輯與畫面都封裝在 `.svelte` 單檔案元件中。熟悉 Svelte 5 的 `$props()` rune 與 `{@render children()}` snippet 語法，能讓你從一開始就使用正確的 Svelte 5 模式，避免在後續章節中因混用 Svelte 4 舊語法（`export let`、`<slot>`）而產生困惑。

- **銜接上一章**：Ch01 補齊了 JS/Web 基礎，現在正式進入 Svelte 元件世界。
- **下一章預告**：Ch03 將深入 Svelte 5 最核心的 Runes 響應式系統（`$state`、`$derived`、`$effect`）。

## Prerequisites

- 已完成第 01 章（Web / JS 基礎）。
- 熟悉 TypeScript 基本型別語法（`interface`、型別註記）。

## Core Concepts

### 1. `.svelte` 單檔案元件結構

一個 `.svelte` 檔由三個區塊組成，順序慣例為 `<script>` → markup → `<style>`：

```svelte
<script lang="ts">
  // 邏輯區：宣告變數、匯入模組、定義 props
</script>

<!-- 標記區：HTML + Svelte 模板語法 -->
<h1>Hello</h1>

<style>
  /* 樣式區：預設 scoped，只影響本元件 */
  h1 { color: steelblue; }
</style>
```

| 何時用單檔案元件 | 何時拆分邏輯到 `.ts` 模組 |
|---|---|
| 元件邏輯簡單、自包含 | 多個元件共用同一段商業邏輯或工具函式 |
| 快速建立 UI 原型 | 純計算邏輯不依賴 DOM，想獨立測試 |
| 標準的頁面或 UI 元件 | 狀態管理邏輯複雜，需拆到 store 模組 |

### 2. `$props()` Rune — 接收外部資料

> **重要**：Svelte 5 使用 `$props()` rune，**不再使用** Svelte 4 的 `export let` 語法。

透過 TypeScript `interface` 定義 props 形狀，再以解構賦值搭配 `$props()` 取值：

```svelte
<script lang="ts">
  interface Props {
    name: string;
    greeting?: string;
  }

  let { name, greeting = 'Hello' }: Props = $props();
</script>

<p>{greeting}, {name}!</p>
```

| 何時用 `$props()` | 何時用 context / stores（Ch07） |
|---|---|
| 父元件直接傳遞資料給子元件 | 資料需跨多層元件共享，避免 prop drilling |
| 資料流向單一、清晰 | 全域狀態（主題色、使用者驗證、語系） |
| 元件介面需要明確型別約束 | 多個不相關元件需讀寫同一份狀態 |

### 3. `$props.id()` — SSR 安全的唯一 ID 產生器

> **Svelte 5.20.0+** 新增。`$props.id()` 會為每個元件實例產生一個唯一 ID，在 SSR 與 client hydration 之間保持一致，不會發生 ID mismatch。

表單中 `<label>` 的 `for` 屬性需要對應 `<input>` 的 `id`，在 SSR 環境下若使用 `Math.random()` 或 `crypto.randomUUID()` 產生 ID，server 與 client 會得到不同值，導致 hydration 錯誤。`$props.id()` 專門解決此問題：

```svelte
<script lang="ts">
  const uid = $props.id();
</script>

<form>
  <label for="{uid}-email">Email：</label>
  <input id="{uid}-email" type="email" />

  <label for="{uid}-password">密碼：</label>
  <input id="{uid}-password" type="password" />
</form>
```

也可用於 `aria-labelledby`、`aria-describedby` 等 accessibility 屬性：

```svelte
<script lang="ts">
  const uid = $props.id();
</script>

<div>
  <span id="{uid}-label">搜尋關鍵字</span>
  <span id="{uid}-desc">輸入至少 2 個字元開始搜尋</span>
  <input
    type="search"
    aria-labelledby="{uid}-label"
    aria-describedby="{uid}-desc"
  />
</div>
```

| 何時用 `$props.id()` | 何時不用 |
|---|---|
| 表單 `<label>` / `<input>` 配對，需要唯一 `id` 與 `for` | 不需要 HTML `id` 屬性的場景 |
| SSR 環境中產生元素 ID | 純 client-side 應用可用其他方式（但仍推薦使用） |
| `aria-labelledby` / `aria-describedby` 等 a11y 屬性 | 元素間不需要 ID 關聯 |

> **注意**：`$props.id()` 只能在元件的頂層 `<script>` 中呼叫（與其他 runes 相同），不可在事件處理器或 `$effect` 中呼叫。每次呼叫產生同一個 ID（每個元件實例一個），多個欄位透過加後綴（如 `{uid}-email`、`{uid}-password`）區分。

### 4. `{@render children()}` — 內容投影

> **重要**：Svelte 5 使用 `{@render children()}` 做內容投影，**不再使用** Svelte 4 的 `<slot>`。

`children` 是一個特殊的 snippet prop，代表父元件放在標籤之間的內容：

```svelte
<!-- Card.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    children: Snippet;
  }

  let { children }: Props = $props();
</script>

<div class="card">
  {@render children()}
</div>
```

使用時：

```svelte
<Card>
  <p>這段內容會被投影到 Card 內部</p>
</Card>
```

| 何時用 `children` 投影 | 何時用 named snippets（Ch08） |
|---|---|
| 元件只有一個投影區域 | 需要多個具名投影區（如 header / body / footer） |
| 簡單的容器、卡片、佈局 | 投影內容需要從子元件接收資料（render props 模式） |
| 直覺的「包裹」語義 | 需要條件式渲染不同區塊 |

### 5. Component 匯入與命名慣例

- **檔名使用 PascalCase**：`UserCard.svelte`、`NavBar.svelte`。
- 匯入時名稱必須以大寫開頭，Svelte 才能區分自訂元件與 HTML 標籤：

```svelte
<script lang="ts">
  import UserCard from '$lib/components/UserCard.svelte';
  import NavBar from '$lib/components/NavBar.svelte';
</script>

<NavBar />
<UserCard name="Alice" email="alice@example.com" />
```

- `$lib` 是 SvelteKit 提供的路徑別名，指向 `src/lib`。
- 元件資料夾建議放在 `src/lib/components/`。

## Step-by-step

### Step 1：建立第一個元件

建立 `src/lib/components/Greeting.svelte`：

```svelte
<script lang="ts">
  // 暫時沒有邏輯
</script>

<h2>Hello, Svelte 5!</h2>

<style>
  h2 {
    color: #ff3e00;
    font-family: system-ui, sans-serif;
  }
</style>
```

### Step 2：用 `$props()` 接收外部資料

為 `Greeting.svelte` 加入 `name` prop：

```svelte
<script lang="ts">
  interface Props {
    name: string;
  }

  let { name }: Props = $props();
</script>

<h2>Hello, {name}!</h2>
```

### Step 3：在 markup 中使用表達式

Svelte 使用 `{}` 花括號將 JavaScript 表達式嵌入標記：

```svelte
<h2>Hello, {name.toUpperCase()}!</h2>
<p>名字有 {name.length} 個字元</p>
```

### Step 4：加入 scoped 樣式

Svelte 的 `<style>` 預設是 scoped — 只影響該元件，不會洩漏到其他元件：

```svelte
<style>
  h2 {
    color: #ff3e00;
    margin-bottom: 0.5rem;
  }

  p {
    color: #666;
    font-size: 0.875rem;
  }
</style>
```

### Step 5：建立使用 `{@render children()}` 的容器元件

建立 `src/lib/components/Card.svelte`：

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    title?: string;
    children: Snippet;
  }

  let { title, children }: Props = $props();
</script>

<div class="card">
  {#if title}
    <h3 class="card-title">{title}</h3>
  {/if}
  <div class="card-body">
    {@render children()}
  </div>
</div>

<style>
  .card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .card-title {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.125rem;
  }
</style>
```

### Step 6：在頁面中組合元件

在 `src/routes/+page.svelte` 匯入並使用：

```svelte
<script lang="ts">
  import Greeting from '$lib/components/Greeting.svelte';
  import Card from '$lib/components/Card.svelte';
</script>

<main>
  <Card title="歡迎">
    <Greeting name="Svelte 5" />
  </Card>

  <Card title="關於">
    <p>這是用 Svelte 5 元件組合出來的頁面。</p>
  </Card>
</main>
```

### Step 7：傳遞不同 props 給多個實例

同一個元件可建立多個實例，各自接收不同資料：

```svelte
<Greeting name="Alice" />
<Greeting name="Bob" />
<Greeting name="Charlie" />
```

### Step 8：使用複雜 props 與預設值

定義含有 optional 欄位與 default 值的 TypeScript interface：

```svelte
<script lang="ts">
  interface Props {
    name: string;
    email: string;
    role?: string;
    avatarUrl?: string;
    isActive?: boolean;
  }

  let {
    name,
    email,
    role = 'member',
    avatarUrl = '/default-avatar.png',
    isActive = true,
  }: Props = $props();
</script>

<div class="profile" class:inactive={!isActive}>
  <img src={avatarUrl} alt="{name}'s avatar" />
  <h2>{name}</h2>
  <p>{email}</p>
  <span class="badge">{role}</span>
</div>
```

重點：透過解構賦值的 `=` 設定預設值，可選欄位在 `interface` 中以 `?` 標記。

## Hands-on Lab

### Foundation：UserCard 元件

建立 `src/lib/components/UserCard.svelte`：

- 定義 TypeScript `interface Props`，含 `name: string`、`email: string`、`avatarUrl?: string`。
- 使用 `$props()` 接收 props，`avatarUrl` 預設為 `'/default-avatar.png'`。
- 在 markup 中顯示大頭照、名字、信箱。
- 加入 scoped style 做基本排版。

驗收：在 `+page.svelte` 顯示至少 2 張不同的 UserCard。

### Advanced：Layout 容器元件

建立 `src/lib/components/Layout.svelte`：

- 使用 `{@render children()}` 將內容投影到主區域。
- 接受 `title: string` prop 做為頁面標題。
- 包含固定的 header（顯示 title）和 footer（顯示版權文字）。
- 加入 scoped style 設定最大寬度、置中、間距。

驗收：在 `+page.svelte` 用 `<Layout>` 包裹所有內容，確認 header/footer 正常顯示。

### Challenge：可配置 Button 元件

建立 `src/lib/components/Button.svelte`：

- 定義 `variant` prop：`'primary' | 'secondary' | 'danger'`，預設 `'primary'`。
- 定義 `disabled?: boolean` prop，預設 `false`。
- 使用 `{@render children()}` 讓按鈕文字由外部決定。
- 根據 variant 動態切換 CSS class。
- 確保 `disabled` 時樣式變灰且不可點擊。

驗收：頁面顯示三種 variant 的 Button，其中一個為 disabled 狀態。

## Reference Solution

### UserCard.svelte

```svelte
<script lang="ts">
  interface Props {
    name: string;
    email: string;
    avatarUrl?: string;
  }

  let { name, email, avatarUrl = '/default-avatar.png' }: Props = $props();
</script>

<div class="user-card">
  <img src={avatarUrl} alt="{name}'s avatar" />
  <h2>{name}</h2>
  <p>{email}</p>
</div>

<style>
  .user-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    max-width: 280px;
  }

  img {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    margin-bottom: 0.75rem;
  }

  h2 {
    margin: 0 0 0.25rem;
    font-size: 1.125rem;
  }

  p {
    margin: 0;
    color: #666;
    font-size: 0.875rem;
  }
</style>
```

### Layout.svelte

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    title: string;
    children: Snippet;
  }

  let { title, children }: Props = $props();
</script>

<div class="layout">
  <header>
    <h1>{title}</h1>
  </header>

  <main>
    {@render children()}
  </main>

  <footer>
    <p>&copy; {new Date().getFullYear()} My SvelteKit App</p>
  </footer>
</div>

<style>
  .layout {
    max-width: 960px;
    margin: 0 auto;
    padding: 1rem 2rem;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    border-bottom: 2px solid #ff3e00;
    padding-bottom: 1rem;
    margin-bottom: 2rem;
  }

  main {
    flex: 1;
  }

  footer {
    border-top: 1px solid #e0e0e0;
    padding-top: 1rem;
    margin-top: 2rem;
    text-align: center;
    color: #999;
    font-size: 0.8rem;
  }
</style>
```

### Button.svelte

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    variant?: 'primary' | 'secondary' | 'danger';
    disabled?: boolean;
    children: Snippet;
  }

  let {
    variant = 'primary',
    disabled = false,
    children,
  }: Props = $props();
</script>

<button class="btn btn-{variant}" {disabled}>
  {@render children()}
</button>

<style>
  .btn {
    padding: 0.5rem 1.25rem;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: opacity 0.2s;
  }

  .btn:hover:not(:disabled) {
    opacity: 0.85;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-primary {
    background-color: #ff3e00;
    color: white;
  }

  .btn-secondary {
    background-color: #e0e0e0;
    color: #333;
  }

  .btn-danger {
    background-color: #dc2626;
    color: white;
  }
</style>
```

### 在 +page.svelte 中組合使用

```svelte
<script lang="ts">
  import Layout from '$lib/components/Layout.svelte';
  import UserCard from '$lib/components/UserCard.svelte';
  import Button from '$lib/components/Button.svelte';
</script>

<Layout title="Svelte 5 元件基礎">
  <section>
    <h2>User Cards</h2>
    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
      <UserCard name="Alice" email="alice@example.com" />
      <UserCard
        name="Bob"
        email="bob@example.com"
        avatarUrl="/bob-avatar.png"
      />
    </div>
  </section>

  <section>
    <h2>Buttons</h2>
    <div style="display: flex; gap: 0.5rem; align-items: center;">
      <Button>Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="danger">Danger</Button>
      <Button disabled>Disabled</Button>
    </div>
  </section>
</Layout>
```

## Common Pitfalls

### 1. 使用 `export let`（Svelte 4）而非 `$props()`（Svelte 5）

這是 Svelte 4 → 5 最常見的遷移錯誤。

```svelte
<!-- 錯誤：Svelte 4 語法 -->
<script lang="ts">
  export let name: string;
</script>

<!-- 正確：Svelte 5 語法 -->
<script lang="ts">
  let { name }: { name: string } = $props();
</script>
```

### 2. 使用 `<slot>`（Svelte 4）而非 `{@render children()}`（Svelte 5）

```svelte
<!-- 錯誤：Svelte 4 語法 -->
<div class="card">
  <slot />
</div>

<!-- 正確：Svelte 5 語法 -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  let { children }: { children: Snippet } = $props();
</script>

<div class="card">
  {@render children()}
</div>
```

### 3. 忘記在 `<script>` 標籤加上 `lang="ts"`

```svelte
<!-- 錯誤：沒有 lang="ts"，TypeScript 語法會報錯 -->
<script>
  interface Props { name: string; }
</script>

<!-- 正確 -->
<script lang="ts">
  interface Props { name: string; }
</script>
```

### 4. 直接修改 props 值

Props 應視為唯讀輸入。如需修改，應在元件內建立本地狀態（Ch03 `$state`）：

```svelte
<script lang="ts">
  let { count }: { count: number } = $props();

  // 錯誤：直接修改 prop
  // count = count + 1;

  // 正確：建立本地狀態（Ch03 會詳細介紹）
  // let localCount = $state(count);
</script>
```

### 5. 元件檔名未使用 PascalCase

```
錯誤：user-card.svelte、userCard.svelte
正確：UserCard.svelte
```

Svelte 需要 PascalCase 檔名來區分自訂元件與 HTML 原生標籤。若匯入名稱以小寫開頭，Svelte 會將其當作 HTML 標籤處理。

## Checklist

- [ ] 能建立含 `<script lang="ts">` / markup / `<style>` 三區塊的 `.svelte` 檔案
- [ ] 能用 `$props()` 搭配 TypeScript `interface` 定義並接收 props
- [ ] 能用 `$props.id()` 產生 SSR-safe 唯一 ID，正確配對 `<label>` 與 `<input>`
- [ ] 能用 `{@render children()}` 做內容投影
- [ ] 能匯入並組合多個元件到頁面中
- [ ] 能透過解構語法設定 prop 預設值
- [ ] `npx svelte-check` 通過，無型別錯誤

## Further Reading

- [Svelte 5 Overview](https://svelte.dev/docs/svelte/overview)
- [$props — Svelte 5 Runes](https://svelte.dev/docs/svelte/$props)
- [$props.id() — SSR-safe unique ID](https://svelte.dev/docs/svelte/$props#$props.id)
- [{@render} — Svelte 5 Template Syntax](https://svelte.dev/docs/svelte/{@render})
- [Snippet — Svelte 5 Template Syntax](https://svelte.dev/docs/svelte/snippet)
- [<style> — Scoped Styles](https://svelte.dev/docs/svelte/styling)
- [SvelteKit Project Structure](https://svelte.dev/docs/kit/project-structure)
