---
title: "Runes and Reactivity / Runes 與響應式系統"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "03"
level: beginner
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [02_svelte_component_basics]
---

# Runes and Reactivity / Runes 與響應式系統

## Goal

深入理解 Svelte 5 的 Runes 響應式系統，這是 Svelte 5 與其他框架最大的差異點。Runes 讓響應式狀態的宣告從隱式（implicit）轉變為顯式（explicit），使程式碼意圖更清晰、更容易推理，同時也解鎖了在 `.svelte.ts` 檔案中使用響應式邏輯的能力。

Runes（`$state`、`$derived`、`$effect`）是 Svelte 5 整個 reactivity 系統的骨幹，後續章節的控制流程、事件處理、生命週期管理都建立在此基礎上。充分理解 `$state` 的 Proxy 追蹤機制、`$derived` 的純計算特性以及 `$state.raw` / `$state.snapshot` 的適用場景，能幫助你在實戰中選擇正確的工具並避免常見的響應式陷阱。

- 銜接上一章：Ch02 學會了元件基礎與 `$props()`，現在要理解如何在元件內管理響應式狀態。
- 下一章預告：Ch04 將學習流程控制語法（`{#if}`、`{#each}`、`{#key}`）來根據狀態渲染不同內容。

## Prerequisites

- 已完成 Ch02，理解 Svelte 元件的基本結構（`<script>`、markup、`<style>`）。
- 知道如何使用 `$props()` 接收外部傳入的資料。
- 具備 TypeScript 基礎型別標註能力（`string`、`number`、`boolean`、`array`、`interface`）。

## Core Concepts

### 1. `$state` / `$state.raw` / `$state.snapshot` — 響應式狀態家族

`$state` 是 Svelte 5 中建立響應式狀態的核心 rune。它有三個變體，分別適用於不同場景。

#### `$state(initialValue)`

建立深度響應式狀態。當傳入物件或陣列時，Svelte 會透過 Proxy 追蹤屬性層級的變更，任何對屬性的修改都會自動觸發相關 DOM 更新。

```svelte
<script lang="ts">
  let count = $state(0);
  let user = $state({ name: 'Alice', age: 30 });

  // 直接修改屬性，DOM 自動更新
  user.age = 31;
</script>
```

- **何時用 `$state`**：大多數元件內部狀態——計數器、表單欄位、UI 開關、清單資料等。這是最常用的 rune，預設選擇。
- **何時不用 `$state`**：值可以從其他狀態推導而來時，應使用 `$derived`；純粹接收外部傳入的資料時，應使用 `$props()`。

#### `$state.raw(initialValue)`

建立淺層響應式狀態。物件和陣列不會被包裝為 Proxy，只有整體重新賦值才會觸發更新，屬性層級的修改不會被追蹤。

```svelte
<script lang="ts">
  // 大型唯讀資料集：數千筆地理座標
  let geoPoints = $state.raw<{ lat: number; lng: number }[]>([]);

  // 整體替換會觸發更新
  geoPoints = await fetchGeoData();

  // 注意：geoPoints[0].lat = 999 不會觸發更新！
</script>
```

- **何時用 `$state.raw`**：大型唯讀資料集合（如 API 回傳的數千筆紀錄）、不需要追蹤屬性變更的情境，可避免深度 Proxy 的記憶體與效能開銷。
- **何時不用 `$state.raw`**：需要對物件屬性或陣列元素進行逐一修改並期望 UI 即時反映時，請使用一般的 `$state`。

#### `$state.snapshot(stateValue)`

取得響應式狀態的純 JavaScript 副本（plain object / array），移除所有 Proxy 包裝。回傳的是當下時間點的靜態快照，不具響應性。

```svelte
<script lang="ts">
  let todos = $state([{ text: 'Learn runes', done: false }]);

  function debugTodos() {
    // console.log(todos) 會顯示 Proxy 物件
    // 使用 snapshot 取得乾淨的 plain object
    console.log($state.snapshot(todos));
  }

  function sendToApi() {
    // 傳給外部 API 時需要 plain object
    fetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify($state.snapshot(todos))
    });
  }
</script>
```

- **何時用 `$state.snapshot`**：需要取得 plain object 傳給外部 API（如 `JSON.stringify`、`structuredClone`、第三方函式庫）、在 `console.log` 中檢視乾淨的資料結構。
- **何時不用 `$state.snapshot`**：在 Svelte 模板或一般元件邏輯中直接使用 `$state` 值即可，不需要額外取 snapshot。

### 2. `$derived` / `$derived.by` — 衍生值計算

`$derived` 用於從其他響應式值計算衍生值，自動追蹤依賴。當依賴的響應式值變更時，衍生值會自動重新計算。

#### `$derived(expression)`

適用於單一表達式的衍生計算：

```svelte
<script lang="ts">
  let count = $state(0);
  let doubled = $derived(count * 2);
  let isEven = $derived(count % 2 === 0);
  let message = $derived(`Count is ${count}`);
</script>
```

#### `$derived.by(() => { ... })`

需要多行邏輯時使用 `$derived.by`，傳入一個函式：

```svelte
<script lang="ts">
  let items = $state<number[]>([3, 1, 4, 1, 5, 9]);
  let threshold = $state(3);

  let filteredAndSorted = $derived.by(() => {
    const filtered = items.filter(n => n >= threshold);
    return filtered.toSorted((a, b) => a - b);
  });
</script>
```

- **何時用 `$derived`**：值完全由其他響應式狀態決定，例如總價 = 單價 x 數量、過濾後的列表、格式化的顯示文字。
- **何時不用 `$derived`**：
  - 如果計算非常簡單且只在 markup 中使用一次，可以直接在模板中寫表達式（例如 `{count * 2}`），不必抽成 `$derived`。
  - 如果你需要的是「副作用」（side effect）而非「計算值」，請使用 `$effect`（Ch06 詳述），而非在 `$derived` 中觸發副作用。
- **`$derived` vs `$effect` 關鍵區別**：`$derived` 產生一個值，`$effect` 執行一個動作。衍生值不應有副作用——不應在 `$derived` 中修改其他狀態、呼叫 API 或操作 DOM。

### 3. `$bindable` — 可綁定 Props

`$bindable` 讓元件的 prop 支援父元件使用 `bind:` 進行雙向綁定。在 Svelte 5 中，prop 的可綁定性必須顯式宣告，不再像 Svelte 4 那樣所有 `export let` 自動支援 `bind:`。

#### 基本語法

子元件中宣告可綁定 prop：

```svelte
<script lang="ts">
  let { value = $bindable(0) } = $props();
</script>

<input type="range" bind:value={value} />
<p>Current: {value}</p>
```

父元件使用 `bind:` 雙向綁定：

```svelte
<script lang="ts">
  import RangeSlider from './RangeSlider.svelte';
  let volume = $state(50);
</script>

<RangeSlider bind:value={volume} />
<p>Volume: {volume}</p>
```

#### 完整範例：RangeSlider 元件

```svelte
<!-- src/lib/components/RangeSlider.svelte -->
<script lang="ts">
  interface Props {
    value: number;
    min?: number;
    max?: number;
    step?: number;
    label?: string;
  }

  let {
    value = $bindable(0),
    min = 0,
    max = 100,
    step = 1,
    label = 'Value'
  }: Props = $props();
</script>

<label>
  {label}: {value}
  <input type="range" bind:value={value} {min} {max} {step} />
</label>
```

- **何時用 `$bindable`**：元件提供表單控件（input、slider、toggle）需要父元件雙向同步值時；包裝原生 HTML 表單元素的元件。
- **何時不用 `$bindable`**：資料流是單向的（父→子），子元件只負責顯示不修改值時，使用一般 `$props()` 即可。子元件需要通知父元件某個事件發生時，使用 callback prop（如 `onchange`）比 `bind:` 更明確。
- **Svelte 4 對比**：Svelte 4 中所有 `export let` prop 自動支援 `bind:`，Svelte 5 必須用 `$bindable()` 顯式標記。這讓元件的 API 更清晰——一看就知道哪些 prop 支援雙向綁定。

### 4. `$host` — Custom Element 的 Host 元素存取

`$host` 讓你在 Svelte 元件被編譯為 Custom Element（Web Component）時，存取 host element 本身。這是一個特殊場景的 rune，只在 `customElement: true` 設定下才有效。

```svelte
<!-- 在 svelte.config.js 中設定 customElement: true 的元件 -->
<svelte:options customElement="my-counter" />

<script lang="ts">
  let count = $state(0);

  function increment() {
    count++;
    // 透過 host element dispatch 自訂事件
    $host().dispatchEvent(
      new CustomEvent('count-changed', {
        detail: { count },
        bubbles: true
      })
    );
  }
</script>

<button onclick={increment}>Count: {count}</button>
```

- **何時用 `$host`**：將 Svelte 元件發佈為 Web Component 時，需要透過 host element 與外部溝通（dispatch events、讀取 attributes）。
- **何時不用 `$host`**：一般的 Svelte 應用開發中，不需要也不能使用 `$host`。如果你不是在做 Custom Element，請忽略此 rune。

### 5. Svelte 4 vs Svelte 5 語法比較 — 重要遷移知識

理解新舊語法的對照，有助於閱讀既有 Svelte 4 程式碼與遷移既有專案。

| 用途 | Svelte 4 | Svelte 5 |
|------|----------|----------|
| 宣告響應式狀態 | `let count = 0;` | `let count = $state(0);` |
| 衍生計算 | `$: doubled = count * 2;` | `let doubled = $derived(count * 2);` |
| 多行衍生 | `$: { ... }` (reactive statement) | `let val = $derived.by(() => { ... });` |
| 元件 props | `export let name: string;` | `let { name } = $props<{ name: string }>();` |
| 副作用 | `$: { console.log(count); }` | `$effect(() => { console.log(count); });` |
| 可綁定 props | `export let value;`（自動支援 bind:） | `let { value = $bindable(0) } = $props();`（顯式宣告） |

**為什麼改變**：

- **更明確（Explicit）**：Svelte 4 的 `let count = 0` 看起來像普通變數，reactivity 是隱式的；Svelte 5 用 `$state` 清楚標記「這是響應式狀態」。
- **可組合（Composable）**：Runes 可以在 `.svelte.ts` 檔案中使用，讓你可以把響應式邏輯抽成可重用的函式。Svelte 4 的 `$:` 只能在 `.svelte` 元件中使用。
- **可預測（Predictable）**：Svelte 4 的 `$:` 有時會因為依賴追蹤順序產生非預期行為；Svelte 5 的 runes 依賴追蹤更精確。

- **何時需要了解 Svelte 4 語法**：維護或遷移既有 Svelte 4 專案、閱讀舊版教學文章與部落格。
- **何時不需要**：全新專案直接使用 Svelte 5 runes 語法即可，無需學習舊語法。

### 6. Signal-based Fine-grained DOM Updates 心智模型

Svelte 5 的響應式系統底層基於 signal 概念。理解這個心智模型有助於寫出更高效的程式碼。

**Svelte compiler 如何運作**：

1. 編譯時期，compiler 分析哪些 `$state` / `$derived` 變數被哪些 DOM 節點引用。
2. 執行時期，當某個 signal 的值改變，Svelte 直接更新受影響的 DOM 節點，不需要比對整棵虛擬 DOM 樹。
3. 這就是「fine-grained reactivity」：只有真正依賴該值的 DOM 片段會被更新。

**與 React 的對比**：

- React：狀態改變 → 整個元件函式重新執行 → virtual DOM diff → 找出差異 → 更新真實 DOM。
- Svelte 5：signal 改變 → 直接更新綁定該 signal 的 DOM 節點，跳過 diff 階段。

- **何時理解此心智模型有幫助**：在做效能優化時、理解為什麼某些更新比預期快或慢時、與其他框架做技術選型比較時。
- **何時不需要深入**：初學者可先跳過實作細節，只需知道「Svelte 會自動且精確地更新受影響的 DOM」即可。隨著經驗累積再回來深入理解。

## Step-by-step

### Step 1：使用 `$state` 建立計數器元件

建立 `src/routes/counter/+page.svelte`：

```svelte
<script lang="ts">
  let count = $state(0);
</script>

<h1>Counter: {count}</h1>
<button onclick={() => count++}>+1</button>
<button onclick={() => count--}>-1</button>
<button onclick={() => count = 0}>Reset</button>
```

啟動開發伺服器後瀏覽 `/counter`，點擊按鈕確認計數器可正常增減與重置。

### Step 2：加入 `$derived` 衍生值

在同一檔案中，加入衍生值：

```svelte
<script lang="ts">
  let count = $state(0);
  let doubled = $derived(count * 2);
  let isEven = $derived(count % 2 === 0);
  let label = $derived(isEven ? 'even' : 'odd');
</script>

<h1>Counter: {count}</h1>
<p>Doubled: {doubled}</p>
<p>Parity: {label}</p>
<button onclick={() => count++}>+1</button>
<button onclick={() => count--}>-1</button>
```

確認修改 `count` 後，`doubled`、`isEven`、`label` 都會自動更新。

### Step 3：使用 `$derived.by` 進行多行衍生計算

建立 `src/routes/derived-demo/+page.svelte`：

```svelte
<script lang="ts">
  let numbers = $state([3, 1, 4, 1, 5, 9, 2, 6]);
  let minValue = $state(3);

  let filteredAndSorted = $derived.by(() => {
    const filtered = numbers.filter(n => n >= minValue);
    const sorted = filtered.toSorted((a, b) => a - b);
    return sorted;
  });

  let summary = $derived(`${filteredAndSorted.length} items, min=${minValue}`);
</script>

<label>
  Minimum value: <input type="number" bind:value={minValue} />
</label>
<p>{summary}</p>
<ul>
  {#each filteredAndSorted as num}
    <li>{num}</li>
  {/each}
</ul>
```

調整 `minValue` 的滑桿，觀察列表自動重新過濾與排序。

### Step 4：展示 `$state` 對物件屬性變更的追蹤

建立 `src/routes/object-state/+page.svelte`：

```svelte
<script lang="ts">
  interface User {
    name: string;
    age: number;
    email: string;
  }

  let user = $state<User>({
    name: 'Alice',
    age: 30,
    email: 'alice@example.com'
  });
</script>

<h2>{user.name} ({user.age})</h2>
<p>{user.email}</p>

<button onclick={() => user.age++}>Birthday (+1 age)</button>
<button onclick={() => user.name = 'Bob'}>Change name to Bob</button>
```

點擊按鈕確認：直接修改物件屬性（`user.age++`、`user.name = 'Bob'`）會觸發 DOM 更新，不需要重新賦值整個物件。

### Step 5：展示 `$state` 對陣列操作的追蹤

建立 `src/routes/array-state/+page.svelte`：

```svelte
<script lang="ts">
  let items = $state<string[]>(['apple', 'banana']);

  function addItem() {
    items.push('cherry');  // push 可直接觸發更新
  }

  function removeFirst() {
    items.splice(0, 1);    // splice 也可以
  }

  function replaceAll() {
    items = ['x', 'y', 'z'];  // 整體重新賦值同樣有效
  }
</script>

<ul>
  {#each items as item}
    <li>{item}</li>
  {/each}
</ul>
<p>Total: {items.length}</p>

<button onclick={addItem}>Add cherry</button>
<button onclick={removeFirst}>Remove first</button>
<button onclick={replaceAll}>Replace all</button>
```

分別測試 `push`、`splice`、重新賦值三種操作，確認 UI 都能正確更新。

### Step 6：使用 `$state.raw` 處理大型唯讀資料集

建立 `src/routes/raw-demo/+page.svelte`：

```svelte
<script lang="ts">
  interface DataPoint {
    id: number;
    value: number;
  }

  // 模擬大量唯讀資料，使用 raw 避免深度 proxy 開銷
  let dataset = $state.raw<DataPoint[]>([]);

  function loadData() {
    // 模擬 API 回傳大量資料
    dataset = Array.from({ length: 10000 }, (_, i) => ({
      id: i,
      value: Math.random() * 100
    }));
  }

  let count = $derived(dataset.length);
</script>

<button onclick={loadData}>Load 10,000 data points</button>
<p>Loaded: {count} points</p>

{#if dataset.length > 0}
  <p>First item value: {dataset[0].value}</p>
{/if}
```

注意：`dataset[0].value = 999` 不會觸發更新，因為 `$state.raw` 不追蹤屬性變更。只有整體重新賦值 `dataset = [...]` 才會觸發更新。

### Step 7：使用 `$state.snapshot` 傳遞乾淨資料

在任一範例中加入 debug 功能：

```svelte
<script lang="ts">
  let todos = $state([
    { text: 'Learn $state', done: true },
    { text: 'Learn $derived', done: false }
  ]);

  function debugState() {
    // 不使用 snapshot：console 中會顯示 Proxy 物件
    console.log('With proxy:', todos);

    // 使用 snapshot：console 中顯示乾淨的 plain object
    console.log('Snapshot:', $state.snapshot(todos));
  }

  function exportAsJson() {
    const plain = $state.snapshot(todos);
    const json = JSON.stringify(plain, null, 2);
    console.log(json);
  }
</script>

<button onclick={debugState}>Debug to console</button>
<button onclick={exportAsJson}>Export JSON</button>
```

開啟瀏覽器 DevTools Console，分別點擊兩個按鈕，觀察 Proxy 與 snapshot 的差異。

### Step 8：Svelte 4 與 Svelte 5 語法並排對照

以下為同一功能在兩個版本中的寫法對照，方便理解遷移方向：

**Svelte 4 寫法（已過時）**：

```svelte
<!-- Svelte 4 — 不要在新專案中使用 -->
<script lang="ts">
  let count = 0;
  $: doubled = count * 2;
  $: isPositive = count > 0;
  $: {
    console.log('count changed to', count);
  }
</script>

<button on:click={() => count++}>{count} x2 = {doubled}</button>
```

**Svelte 5 寫法（推薦）**：

```svelte
<!-- Svelte 5 — rune-based, explicit -->
<script lang="ts">
  let count = $state(0);
  let doubled = $derived(count * 2);
  let isPositive = $derived(count > 0);

  $effect(() => {
    console.log('count changed to', count);
  });
</script>

<button onclick={() => count++}>{count} x2 = {doubled}</button>
```

比較重點：
- `let count = 0` → `let count = $state(0)`
- `$: doubled = ...` → `let doubled = $derived(...)`
- `$: { ... }` → `$effect(() => { ... })`
- `on:click` → `onclick`

### Step 9：使用 `$bindable` 建立 RangeSlider 元件

建立 `src/lib/components/RangeSlider.svelte`：

```svelte
<!-- src/lib/components/RangeSlider.svelte -->
<script lang="ts">
  interface Props {
    value: number;
    min?: number;
    max?: number;
    step?: number;
    label?: string;
  }

  let {
    value = $bindable(0),
    min = 0,
    max = 100,
    step = 1,
    label = 'Value'
  }: Props = $props();
</script>

<label>
  {label}: {value}
  <input type="range" bind:value={value} {min} {max} {step} />
</label>
```

在父元件中使用 `bind:` 雙向綁定：

```svelte
<!-- src/routes/slider-demo/+page.svelte -->
<script lang="ts">
  import RangeSlider from '$lib/components/RangeSlider.svelte';

  let volume = $state(50);
  let brightness = $state(75);
</script>

<h1>RangeSlider Demo</h1>

<RangeSlider bind:value={volume} label="Volume" />
<p>Volume in parent: {volume}</p>

<RangeSlider bind:value={brightness} label="Brightness" max={100} step={5} />
<p>Brightness in parent: {brightness}</p>
```

拖動 slider 確認：子元件的值與父元件的 `volume` / `brightness` 保持同步。這就是 `$bindable` 的雙向綁定效果。

## Hands-on Lab

### Foundation 基礎層

**任務**：建立一個 Todo List，使用 `$state` 管理待辦事項陣列，使用 `$derived` 顯示統計數據。

要求：
- 建立 `src/routes/todo/+page.svelte`。
- 用 `$state<Todo[]>([])` 管理待辦清單。
- 實作新增待辦事項功能（輸入文字 + 按按鈕或 Enter 新增）。
- 實作刪除待辦事項功能。
- 實作切換完成狀態功能（checkbox）。
- 用 `$derived` 計算剩餘未完成數量。

驗收條件：
- 可新增、刪除、勾選待辦事項。
- 剩餘數量隨勾選狀態即時更新。
- `npx svelte-check` 通過。

**額外任務**：建立 `$bindable` RangeSlider 元件。

- 建立 `src/lib/components/RangeSlider.svelte`，使用 `$bindable` 宣告 `value` prop。
- 在父元件中使用 `bind:value` 綁定，確認拖動 slider 後父元件的值同步更新。

### Advanced 進階層

**任務**：在基礎層之上加入篩選功能與全選切換。

要求：
- 加入篩選機制：`all` / `active` / `completed` 三種模式。
- 用 `$derived.by` 根據目前篩選模式過濾待辦清單。
- 實作 toggle-all 功能：一鍵全部勾選或全部取消。
- 顯示各篩選模式下的數量。

驗收條件：
- 切換篩選模式後，列表即時更新。
- toggle-all 按鈕在全部完成時顯示不同狀態。
- 所有功能在不同篩選模式下正常運作。

### Challenge 挑戰層

**任務**：將計數器邏輯抽取到 `.svelte.ts` 共享模組，展示 runes 在元件外部使用的能力。

要求：
- 建立 `src/lib/counter.svelte.ts`，用 runes 實作共享計數器工廠函式。
- 匯出的函式回傳具有 `count`、`doubled`、`increment`、`decrement`、`reset` 的物件。
- 在兩個不同的元件中匯入並使用同一個計數器實例，驗證狀態共享。
- 在另一個元件中建立獨立的計數器實例，驗證狀態隔離。

驗收條件：
- 兩個元件共享同一計數器實例時，操作其中一個元件會同步影響另一個。
- 獨立實例之間互不影響。
- `npx svelte-check` 通過。

## Reference Solution

### Todo List 完整元件（Foundation + Advanced）

```svelte
<!-- src/routes/todo/+page.svelte -->
<script lang="ts">
  interface Todo {
    id: number;
    text: string;
    done: boolean;
  }

  let todos = $state<Todo[]>([]);
  let filter = $state<'all' | 'active' | 'completed'>('all');
  let newText = $state('');

  let filtered = $derived.by(() => {
    switch (filter) {
      case 'active': return todos.filter(t => !t.done);
      case 'completed': return todos.filter(t => t.done);
      default: return todos;
    }
  });

  let remaining = $derived(todos.filter(t => !t.done).length);
  let allDone = $derived(todos.length > 0 && remaining === 0);

  function addTodo() {
    const trimmed = newText.trim();
    if (!trimmed) return;
    todos.push({
      id: Date.now(),
      text: trimmed,
      done: false
    });
    newText = '';
  }

  function removeTodo(id: number) {
    const index = todos.findIndex(t => t.id === id);
    if (index !== -1) todos.splice(index, 1);
  }

  function toggleAll() {
    const targetState = !allDone;
    for (const todo of todos) {
      todo.done = targetState;
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') addTodo();
  }
</script>

<h1>Todo List</h1>

<div>
  <input
    type="text"
    placeholder="What needs to be done?"
    bind:value={newText}
    onkeydown={handleKeydown}
  />
  <button onclick={addTodo}>Add</button>
</div>

{#if todos.length > 0}
  <div>
    <button onclick={toggleAll}>
      {allDone ? 'Uncheck all' : 'Check all'}
    </button>
  </div>

  <nav>
    <button onclick={() => filter = 'all'}>All ({todos.length})</button>
    <button onclick={() => filter = 'active'}>Active ({remaining})</button>
    <button onclick={() => filter = 'completed'}>
      Completed ({todos.length - remaining})
    </button>
  </nav>

  <ul>
    {#each filtered as todo (todo.id)}
      <li>
        <label>
          <input type="checkbox" bind:checked={todo.done} />
          <span style:text-decoration={todo.done ? 'line-through' : 'none'}>
            {todo.text}
          </span>
        </label>
        <button onclick={() => removeTodo(todo.id)}>Delete</button>
      </li>
    {/each}
  </ul>

  <p>{remaining} item{remaining === 1 ? '' : 's'} remaining</p>
{:else}
  <p>No todos yet. Add one above!</p>
{/if}
```

### 共享計數器模組（Challenge）

```ts
// src/lib/counter.svelte.ts
export function createCounter(initial = 0) {
  let count = $state(initial);
  let doubled = $derived(count * 2);

  return {
    get count() { return count; },
    get doubled() { return doubled; },
    increment() { count++; },
    decrement() { count--; },
    reset() { count = initial; }
  };
}
```

```svelte
<!-- src/routes/shared-counter/+page.svelte -->
<script lang="ts">
  import { createCounter } from '$lib/counter.svelte';

  // 兩個元件共享同一個實例
  const shared = createCounter(0);

  // 另一個獨立實例
  const independent = createCounter(100);
</script>

<h1>Shared Counter Demo</h1>

<section>
  <h2>Shared instance (Component A view)</h2>
  <p>Count: {shared.count} | Doubled: {shared.doubled}</p>
  <button onclick={shared.increment}>+1</button>
  <button onclick={shared.decrement}>-1</button>
  <button onclick={shared.reset}>Reset</button>
</section>

<section>
  <h2>Shared instance (Component B view)</h2>
  <p>Count: {shared.count} | Doubled: {shared.doubled}</p>
  <button onclick={shared.increment}>+1</button>
</section>

<section>
  <h2>Independent instance</h2>
  <p>Count: {independent.count} | Doubled: {independent.doubled}</p>
  <button onclick={independent.increment}>+1</button>
  <button onclick={independent.reset}>Reset</button>
</section>
```

> 注意：上面的範例為了簡化，在同一個頁面中展示共享與獨立實例。在實際應用中，你可以將 `shared` 實例透過 module-level 變數或 context 傳遞給不同的子元件。

## Common Pitfalls

1. **使用 `$:` 響應式宣告（Svelte 4 語法）而非 `$derived`（Svelte 5 語法）**
   Svelte 5 中 `$:` label 語法已被棄用。如果你看到教學或範例使用 `$: doubled = count * 2`，請改用 `let doubled = $derived(count * 2)`。混用新舊語法會導致非預期行為。

2. **對應該用 `$derived` 的值使用 `$state`（手動同步陷阱）**
   如果一個值完全由其他狀態決定，不要用 `$state` + 手動更新的方式：
   ```ts
   // Bad: 手動同步，容易忘記更新
   let count = $state(0);
   let doubled = $state(0);
   // 每次 count 改變都要記得同步 doubled... 容易出錯

   // Good: 讓 $derived 自動追蹤
   let count = $state(0);
   let doubled = $derived(count * 2);
   ```

3. **在非 rune-aware 檔案中使用 `$state`**
   Runes 只能在 `.svelte` 和 `.svelte.ts`（或 `.svelte.js`）檔案中使用。如果你在一般的 `.ts` 檔案中寫 `$state`，Svelte compiler 不會處理它，會產生語法錯誤。需要在元件外使用 runes 時，檔案副檔名必須是 `.svelte.ts`。

4. **忘記 `$state` 物件是 Proxy — `console.log` 顯示不直觀**
   直接 `console.log` 一個 `$state` 物件會看到 Proxy 包裝，屬性不易閱讀。解決方法是使用 `$state.snapshot()`：
   ```ts
   let user = $state({ name: 'Alice' });
   console.log(user);                    // Proxy { ... } — 不直觀
   console.log($state.snapshot(user));    // { name: 'Alice' } — 乾淨
   ```

5. **使用 `$state.raw` 後期望屬性變更能觸發更新**
   `$state.raw` 禁用深度 reactivity，只有整體重新賦值才會觸發更新。如果你需要修改陣列元素的屬性並期望 UI 更新，請使用一般的 `$state`：
   ```ts
   let items = $state.raw([{ name: 'A', active: true }]);
   items[0].active = false; // 不會觸發更新！

   // 解法一：使用 $state 而非 $state.raw
   let items = $state([{ name: 'A', active: true }]);
   items[0].active = false; // 會觸發更新

   // 解法二：如果堅持用 raw，需整體替換
   items = items.map(item =>
     item.name === 'A' ? { ...item, active: false } : item
   );
   ```

6. **在 `$derived` 中執行副作用**
   `$derived` 是純計算，不應在其中修改狀態、呼叫 API 或操作 DOM。如需副作用，請使用 `$effect`（Ch06）：
   ```ts
   // Bad: derived 中有副作用
   let count = $state(0);
   let doubled = $derived.by(() => {
     console.log('computing...');  // 副作用！不應放在 derived 中
     fetch('/api/log');            // 副作用！絕對不要
     return count * 2;
   });

   // Good: 純計算
   let doubled = $derived(count * 2);
   ```

## Checklist

- [ ] 能使用 `$state` 建立響應式狀態，並在模板中顯示與更新
- [ ] 能使用 `$derived` 和 `$derived.by` 建立衍生計算值
- [ ] 能解釋 `$state`、`$state.raw`、`$state.snapshot` 三者的差異與各自適用場景
- [ ] 能對照 Svelte 4 與 Svelte 5 的響應式語法差異（`$:` vs `$derived`、`let` vs `$state`）
- [ ] 能使用 `$bindable` 建立支援雙向綁定的 prop
- [ ] 能在 `.svelte.ts` 檔案中使用 runes 建立可重用的響應式邏輯
- [ ] `npx svelte-check` 對所有練習檔案通過，無型別錯誤

## Further Reading

- [Svelte 5 Runes Documentation](https://svelte.dev/docs/svelte/$state)
- [Svelte 5 $derived Documentation](https://svelte.dev/docs/svelte/$derived)
- [Svelte Tutorial: State](https://svelte.dev/tutorial/svelte/state)
- [Svelte Tutorial: Derived State](https://svelte.dev/tutorial/svelte/derived-state)
- [Svelte 5 Migration Guide](https://svelte.dev/docs/svelte/v5-migration-guide)
- [Svelte GitHub Repository](https://github.com/sveltejs/svelte)
