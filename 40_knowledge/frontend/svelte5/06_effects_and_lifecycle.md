---
title: "Effects and Lifecycle / 副作用與生命週期"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "06"
level: beginner
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [05_events_forms_and_bindings]
---
# Effects and Lifecycle / 副作用與生命週期

## Goal

學會使用 `$effect` 處理副作用（API 呼叫、計時器、DOM 操作），理解 Svelte 5 的生命週期機制。

`$effect` 是 Svelte 5 中連接響應式狀態與外部世界（DOM 操作、網路請求、瀏覽器 API）的關鍵 rune。與 React 的 `useEffect` 不同，Svelte 的 `$effect` 自動追蹤依賴，消除了手動維護 dependency array 的錯誤風險。搭配 `onMount`、`tick()`、`untrack()` 等生命週期工具，能完整掌控元件從建立到銷毀的整個過程。

- **銜接上一章**：Ch05 處理了使用者輸入事件，現在要處理表單以外的副作用。
- **下一章預告**：Ch07 將學習 stores、context 與更進階的狀態管理模式。

## Prerequisites

- 已完成第 05 章（Events, Forms and Bindings）。
- 熟悉 `$state` 與 `$derived` runes（Ch03）。
- 了解 JavaScript 非同步概念（`Promise`、`async/await`、`setTimeout`、`setInterval`）。

## Core Concepts

### 1. `$effect` — automatic dependency tracking

`$effect` 是 Svelte 5 處理副作用的核心 rune。它會**自動追蹤**回呼函式中讀取的所有響應式值，當這些值變化時自動重新執行——不需要像 React `useEffect` 那樣手動維護 dependency array。

```svelte
<script lang="ts">
  let count = $state(0);

  $effect(() => {
    console.log(`count 變為 ${count}`);
  });
</script>
```

Cleanup 機制：從 `$effect` 回傳一個函式，Svelte 會在 effect 重新執行前以及元件銷毀時呼叫它：

```svelte
<script lang="ts">
  let seconds = $state(0);

  $effect(() => {
    const id = setInterval(() => seconds++, 1000);
    return () => clearInterval(id); // cleanup
  });
</script>
```

| 何時用 `$effect` | 何時不用 `$effect` |
|---|---|
| 需要在狀態變化時執行副作用（sync to external system） | 計算衍生值（用 `$derived`） |
| DOM manipulation（如操作 Canvas、第三方程式庫） | 事件處理（用 event handler） |
| 訂閱外部資料源（WebSocket、EventSource） | 只是轉換資料格式（用 `$derived`） |

### 2. `$effect.pre` — runs before DOM update

`$effect.pre` 在 DOM 更新**之前**執行，適合需要在瀏覽器重繪前讀取或保存 DOM 狀態的場景。

```svelte
<script lang="ts">
  let messages = $state<string[]>([]);
  let container: HTMLDivElement;
  let shouldAutoScroll = $state(true);

  $effect.pre(() => {
    // 在 DOM 更新前檢查是否需要自動捲動
    if (container) {
      const { scrollTop, scrollHeight, clientHeight } = container;
      shouldAutoScroll = scrollHeight - scrollTop - clientHeight < 50;
    }
  });

  $effect(() => {
    // DOM 更新後，根據先前判斷決定是否捲到底部
    if (shouldAutoScroll && container) {
      container.scrollTop = container.scrollHeight;
    }
  });
</script>
```

| 何時用 `$effect.pre` | 何時不用 `$effect.pre` |
|---|---|
| 需要在 DOM 更新前讀取 DOM 狀態（如 scroll position preservation） | 大多數副作用——預設的 `$effect` 已足夠 |
| 需要在重繪前做計算以避免視覺閃爍 | 不涉及 DOM 狀態的副作用 |

### 3. `$effect.root` — untracked root effect

`$effect.root` 建立一個不被元件生命週期自動管理的 effect 根節點。它回傳一個 `destroy` 函式，需要手動呼叫來清理。

```ts
// src/lib/timer.svelte.ts
export function createTimer() {
  let count = $state(0);

  const destroy = $effect.root(() => {
    $effect(() => {
      const id = setInterval(() => count++, 1000);
      return () => clearInterval(id);
    });
  });

  return {
    get count() { return count; },
    destroy,
  };
}
```

| 何時用 `$effect.root` | 何時不用 `$effect.root` |
|---|---|
| 在非元件上下文中建立 effect（如 `.svelte.ts` 模組） | 一般元件內直接用 `$effect` |
| 需要手動控制 effect 的生命週期 | 效果應跟隨元件自動銷毀時 |
| 測試環境中需要建立獨立的 reactive scope | 簡單的元件層級副作用 |

### 4. `onMount` / `onDestroy` / `tick()` / `untrack()`

#### `onMount`

元件首次掛載到 DOM 後執行一次。適合一次性 setup，如 fetch initial data、初始化第三方程式庫。

```svelte
<script lang="ts">
  import { onMount } from 'svelte';

  let data = $state<string[]>([]);

  onMount(async () => {
    const res = await fetch('/api/items');
    data = await res.json();
  });
</script>
```

#### `onDestroy`

元件從 DOM 移除前執行。適合清理不透過 `$effect` 管理的資源。

```svelte
<script lang="ts">
  import { onDestroy } from 'svelte';

  const controller = new AbortController();

  onDestroy(() => {
    controller.abort();
  });
</script>
```

#### `tick()`

回傳一個 Promise，等待 Svelte 完成下一次 DOM 更新。類似 Vue 的 `nextTick`。

```svelte
<script lang="ts">
  import { tick } from 'svelte';

  let text = $state('');
  let input: HTMLInputElement;

  async function handleClick() {
    text = 'Hello!';
    await tick(); // 等待 DOM 更新完成
    input.select(); // 現在可以安全操作更新後的 DOM
  }
</script>
```

#### `untrack()`

在 `$effect` 或 `$derived` 中讀取響應式值但**不建立追蹤依賴**。

```svelte
<script lang="ts">
  import { untrack } from 'svelte';

  let searchTerm = $state('');
  let logCount = $state(0);

  $effect(() => {
    // searchTerm 被追蹤，logCount 不被追蹤
    console.log(`搜尋 "${searchTerm}"，這是第 ${untrack(() => logCount)} 次`);
    logCount++;
  });
</script>
```

| 何時用 `onMount` | 何時用 `$effect` |
|---|---|
| 一次性 setup（fetch initial data、初始化第三方程式庫） | 需要在響應式依賴變化時重新執行 |
| 只需在瀏覽器環境執行（SSR 時不會執行） | 自動追蹤依賴並重跑 |
| 回傳值為 cleanup function | 回傳值為 cleanup function |

## Step-by-step

### Step 1：建立使用 `$effect` 記錄狀態變化的元件

建立 `src/lib/components/Counter.svelte`，使用 `$effect` 在 count 變化時輸出 log：

```svelte
<script lang="ts">
  let count = $state(0);

  $effect(() => {
    console.log(`[Effect] count is now: ${count}`);
  });
</script>

<button onclick={() => count++}>
  Clicked {count} times
</button>
```

觀察：每次點擊按鈕，console 都會輸出新的 count 值。`$effect` 自動追蹤了 `count`，不需要手動宣告 dependency。

### Step 2：加入 cleanup function 處理計時器

在 `$effect` 回傳一個函式，用來清理 `setInterval`：

```svelte
<script lang="ts">
  let isRunning = $state(false);
  let count = $state(0);

  $effect(() => {
    if (isRunning) {
      const id = setInterval(() => count++, 1000);
      return () => {
        console.log('[Cleanup] clearing interval');
        clearInterval(id);
      };
    }
  });
</script>

<p>Count: {count}</p>
<button onclick={() => isRunning = !isRunning}>
  {isRunning ? 'Stop' : 'Start'}
</button>
```

觀察：切換 `isRunning` 時，舊的 interval 會被清理，新的會被建立（或不建立）。

### Step 3：建立時鐘元件

組合 `$effect` + `setInterval` + cleanup，建立一個顯示即時時間的元件：

```svelte
<!-- src/lib/components/Clock.svelte -->
<script lang="ts">
  let time = $state(new Date());

  $effect(() => {
    const interval = setInterval(() => {
      time = new Date();
    }, 1000);

    return () => clearInterval(interval);
  });
</script>

<p>Current time: {time.toLocaleTimeString()}</p>
```

### Step 4：使用 `onMount` 在元件掛載時擷取資料

```svelte
<!-- src/lib/components/UserList.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';

  interface User {
    id: number;
    name: string;
  }

  let users = $state<User[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);

  onMount(async () => {
    try {
      const res = await fetch('https://jsonplaceholder.typicode.com/users');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      users = await res.json();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Unknown error';
    } finally {
      loading = false;
    }
  });
</script>

{#if loading}
  <p>Loading...</p>
{:else if error}
  <p>Error: {error}</p>
{:else}
  <ul>
    {#each users as user}
      <li>{user.name}</li>
    {/each}
  </ul>
{/if}
```

重點：`onMount` 在 SSR 時不會執行，因此瀏覽器專屬的 `fetch` 在這裡是安全的。若需要 SSR 資料載入，應使用 SvelteKit 的 `load` function（Ch10+ 會介紹）。

### Step 5：觀察 `$effect` 自動追蹤依賴

```svelte
<script lang="ts">
  let firstName = $state('Alice');
  let lastName = $state('Smith');
  let showFullName = $state(true);

  $effect(() => {
    // 當 showFullName 為 true 時，追蹤 firstName 和 lastName
    // 當 showFullName 為 false 時，只追蹤 firstName
    if (showFullName) {
      console.log(`Full name: ${firstName} ${lastName}`);
    } else {
      console.log(`First name: ${firstName}`);
    }
  });
</script>

<input bind:value={firstName} placeholder="First name" />
<input bind:value={lastName} placeholder="Last name" />
<label>
  <input type="checkbox" bind:checked={showFullName} />
  Show full name
</label>
```

觀察：當 `showFullName` 為 `false` 時，修改 `lastName` **不會**觸發 effect——因為 Svelte 的追蹤是基於上一次執行時實際讀取的值，而非靜態分析。

### Step 6：使用 `untrack()` 避免不必要的依賴

```svelte
<script lang="ts">
  import { untrack } from 'svelte';

  let searchTerm = $state('');
  let searchCount = $state(0);

  $effect(() => {
    // 只在 searchTerm 變化時執行
    // searchCount 的變化不會觸發此 effect
    const term = searchTerm;
    const count = untrack(() => ++searchCount);
    console.log(`Search #${count}: "${term}"`);
  });
</script>

<input bind:value={searchTerm} placeholder="搜尋..." />
<p>已搜尋 {searchCount} 次</p>
```

### Step 7：使用 `tick()` 等待 DOM 更新後操作元素

```svelte
<script lang="ts">
  import { tick } from 'svelte';

  let items = $state<string[]>([]);
  let list: HTMLUListElement;

  async function addItem() {
    items = [...items, `Item ${items.length + 1}`];
    await tick(); // 等待 DOM 更新
    // 現在可以安全讀取更新後的 DOM
    const lastChild = list.lastElementChild;
    lastChild?.scrollIntoView({ behavior: 'smooth' });
  }
</script>

<button onclick={addItem}>Add item</button>

<ul bind:this={list}>
  {#each items as item}
    <li>{item}</li>
  {/each}
</ul>
```

### Step 8：比較 React `useEffect` 與 Svelte `$effect`

| 特性 | React `useEffect` | Svelte `$effect` |
|---|---|---|
| 依賴追蹤 | 手動列出 dependency array | **自動追蹤**讀取的響應式值 |
| 遺漏依賴風險 | 高（dependency array 可能過時） | 無（自動追蹤，不需手動維護） |
| 執行時機 | commit phase 之後 | DOM 更新之後（類似 `useEffect`） |
| Cleanup | return function | return function（語法相同） |
| 條件式依賴 | 不支援（hooks 規則要求固定呼叫） | 支援（追蹤基於實際執行路徑） |
| SSR 行為 | 不在 server 執行 | 不在 server 執行 |
| 空依賴（只跑一次） | `useEffect(() => {}, [])` | 用 `onMount` 替代 |

Svelte `$effect` 的自動追蹤消除了 React 中常見的「遺漏依賴」和「不必要的重新渲染」問題。

## Hands-on Lab

### Foundation：即時時鐘元件

建立 `src/lib/components/Clock.svelte`：

- 使用 `$state` 儲存當前時間（`new Date()`）。
- 使用 `$effect` + `setInterval` 每秒更新時間。
- 回傳 cleanup function 清除 interval。
- 在頁面顯示格式化的時間字串（`toLocaleTimeString()`）。

驗收：時間每秒更新，元件卸載時 interval 被正確清除（無 console 警告）。

### Advanced：防抖搜尋元件

建立 `src/lib/components/DebouncedSearch.svelte`：

- 使用 `$state` 追蹤搜尋輸入值。
- 使用 `$effect` 自動追蹤搜尋詞，加入 300ms debounce 後呼叫 API。
- cleanup function 清除尚未觸發的 `setTimeout`。
- 顯示 loading 狀態與搜尋結果。

驗收：輸入文字後 300ms 才發出請求，快速輸入不會產生多餘請求。

### Challenge：localStorage 同步模組

建立 `src/lib/persisted.svelte.ts`：

- 建立 `persisted<T>(key, initial)` 函式，回傳一個可讀寫的響應式值。
- 使用 `$effect` 在值變化時自動寫入 `localStorage`。
- 使用 `$state.snapshot()` 取得可序列化的值。
- 加入 SSR 安全檢查：`typeof window !== 'undefined'`。
- 頁面重新整理後，值應從 `localStorage` 恢復。

驗收：在元件中使用 `persisted('counter', 0)`，重新整理頁面後計數器恢復上次的值。

## Reference Solution

### Clock.svelte

```svelte
<!-- src/lib/components/Clock.svelte -->
<script lang="ts">
  let time = $state(new Date());

  $effect(() => {
    const interval = setInterval(() => {
      time = new Date();
    }, 1000);

    return () => clearInterval(interval);
  });
</script>

<p>Current time: {time.toLocaleTimeString()}</p>
```

### DebouncedSearch.svelte

```svelte
<!-- src/lib/components/DebouncedSearch.svelte -->
<script lang="ts">
  interface SearchResult {
    id: number;
    title: string;
  }

  let query = $state('');
  let results = $state<SearchResult[]>([]);
  let loading = $state(false);

  $effect(() => {
    const term = query.trim();

    if (term.length < 2) {
      results = [];
      return;
    }

    loading = true;

    const timeout = setTimeout(async () => {
      try {
        const res = await fetch(
          `https://jsonplaceholder.typicode.com/posts?title_like=${encodeURIComponent(term)}`
        );
        results = await res.json();
      } catch {
        results = [];
      } finally {
        loading = false;
      }
    }, 300);

    return () => {
      clearTimeout(timeout);
      loading = false;
    };
  });
</script>

<input bind:value={query} placeholder="搜尋文章..." />

{#if loading}
  <p>搜尋中...</p>
{:else if results.length > 0}
  <ul>
    {#each results as result}
      <li>{result.title}</li>
    {/each}
  </ul>
{:else if query.trim().length >= 2}
  <p>無結果</p>
{/if}
```

### persisted.svelte.ts

```ts
// src/lib/persisted.svelte.ts
export function persisted<T>(key: string, initial: T) {
  let value = $state(initial);

  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem(key);
    if (stored) {
      try {
        value = JSON.parse(stored);
      } catch {
        // stored value is invalid JSON, use initial
      }
    }
  }

  $effect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(key, JSON.stringify($state.snapshot(value)));
    }
  });

  return {
    get value() { return value; },
    set value(v: T) { value = v; },
  };
}
```

使用方式：

```svelte
<!-- src/routes/+page.svelte -->
<script lang="ts">
  import { persisted } from '$lib/persisted.svelte';

  const counter = persisted('counter', 0);
</script>

<p>Count: {counter.value}</p>
<button onclick={() => counter.value++}>+1</button>
<button onclick={() => counter.value = 0}>Reset</button>
```

## Common Pitfalls

### 1. 使用 `$effect` 計算衍生值（應使用 `$derived`）

`$effect` 的用途是副作用（side effects），不是計算衍生資料。若用 `$effect` 來更新另一個 `$state`，會產生不必要的中間狀態和額外的重新渲染。

```svelte
<script lang="ts">
  let price = $state(100);
  let quantity = $state(2);

  // 錯誤：用 $effect 計算衍生值
  let total = $state(0);
  $effect(() => {
    total = price * quantity;
  });

  // 正確：用 $derived
  let total = $derived(price * quantity);
</script>
```

### 2. 忘記回傳 cleanup function，導致記憶體洩漏

計時器、事件監聽器、WebSocket 連線等都需要在 effect 清理時釋放：

```svelte
<script lang="ts">
  let width = $state(0);

  // 錯誤：沒有 cleanup，每次 effect 重跑都新增一個 listener
  $effect(() => {
    const handler = () => { width = window.innerWidth; };
    window.addEventListener('resize', handler);
    // 缺少 return () => window.removeEventListener('resize', handler);
  });

  // 正確：回傳 cleanup function
  $effect(() => {
    const handler = () => { width = window.innerWidth; };
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  });
</script>
```

### 3. 無限迴圈：`$effect` 讀取並寫入同一個值

如果 `$effect` 讀取一個響應式值，又在同一個 effect 中寫入它，會造成無限重新觸發：

```svelte
<script lang="ts">
  let count = $state(0);

  // 錯誤：讀取 count 又寫入 count → 無限迴圈
  $effect(() => {
    count = count + 1; // 永遠不要這樣做！
  });

  // 正確：如果需要基於前值更新，使用 untrack 避免追蹤讀取
  $effect(() => {
    // 僅在其他依賴觸發時執行
    someOtherValue; // 被追蹤的依賴
    count = untrack(() => count) + 1;
  });
</script>
```

### 4. 在 SSR 環境中使用瀏覽器 API 而未做安全檢查

`$effect` 在 server 端不會執行，但 `<script>` 頂層程式碼會。存取 `window`、`document`、`localStorage` 等瀏覽器 API 前務必檢查：

```ts
// 錯誤：在頂層直接存取 localStorage（SSR 時會報錯）
let theme = $state(localStorage.getItem('theme') ?? 'light');

// 正確：加入環境檢查
let theme = $state('light');
if (typeof window !== 'undefined') {
  theme = localStorage.getItem('theme') ?? 'light';
}
```

### 5. 不理解 `$effect` 的執行時機

`$effect` 在 DOM 更新**之後**執行。如果需要在 DOM 更新**之前**讀取 DOM 狀態（如保存 scroll position），應使用 `$effect.pre`：

```svelte
<script lang="ts">
  let messages = $state<string[]>([]);
  let div: HTMLDivElement;

  // 錯誤：$effect 在 DOM 更新後執行，此時 scrollHeight 已經改變
  // 無法正確判斷使用者是否在底部

  // 正確：用 $effect.pre 在 DOM 更新前讀取 scroll 狀態
  $effect.pre(() => {
    if (div) {
      // 在 DOM 更新前讀取，保存 scroll 位置
    }
  });
</script>
```

## Checklist

- [ ] 能建立 `$effect` 並理解自動依賴追蹤機制
- [ ] 能從 `$effect` 回傳 cleanup function 清理計時器、訂閱等資源
- [ ] 能使用 `onMount` 進行一次性初始化（如 fetch data）
- [ ] 能使用 `untrack()` 讀取響應式值而不建立追蹤依賴
- [ ] 能使用 `tick()` 等待 DOM 更新完成後再操作元素
- [ ] 能說明何時用 `$effect`、何時用 `$derived`、何時用 `onMount`
- [ ] `npx svelte-check` 通過，無型別錯誤

## Further Reading

- [$effect — Svelte 5 Runes](https://svelte.dev/docs/svelte/$effect)
- [onMount — Svelte Lifecycle](https://svelte.dev/docs/svelte/lifecycle-hooks#onMount)
- [onDestroy — Svelte Lifecycle](https://svelte.dev/docs/svelte/lifecycle-hooks#onDestroy)
- [tick — Svelte](https://svelte.dev/docs/svelte/lifecycle-hooks#tick)
- [untrack — Svelte](https://svelte.dev/docs/svelte/svelte#untrack)
- [Svelte 5 Runes Overview](https://svelte.dev/docs/svelte/what-are-runes)
