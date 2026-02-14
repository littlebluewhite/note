---
title: "Performance and Fine-grained Reactivity / 效能與細粒度響應"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "16"
level: advanced
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [15_error_handling_and_recovery]
---
# Performance and Fine-grained Reactivity / 效能與細粒度響應

## Goal

理解 Svelte 的效能特性，學會診斷與優化效能問題，善用細粒度響應式的優勢。

Svelte 5 的 compiler-driven reactivity 讓大多數應用天生就具備良好效能，但面對大型資料集與複雜 UI 時，仍需理解 `$state` vs `$state.raw` 的取捨、bundle 分析與 lazy loading 策略。掌握這些技巧能讓你在效能瓶頸出現時快速診斷並對症下藥。

- **銜接上一章**：Ch15 學會了錯誤處理與復原策略，現在要確保應用在效能上也表現良好。
- **下一章預告**：Ch17 將學習使用 Vitest 與 Svelte Testing Library 進行測試。

## Prerequisites

- 已完成第 15 章（Error Handling and Recovery）。
- 熟悉 Svelte 5 的 runes 系統（`$state`、`$derived`、`$effect`）（Ch03）。
- 了解 SvelteKit 的路由與載入機制（Ch10–Ch11）。
- 了解瀏覽器 DevTools 基本操作（Performance tab、Network tab）。

## Core Concepts

### 1. Why Svelte rarely needs memoization

傳統框架（特別是 React）需要 `React.memo`、`useMemo`、`useCallback` 來避免不必要的重新渲染。Svelte 不需要這些，原因如下：

- **沒有 virtual DOM diffing**：Svelte 在編譯階段分析依賴關係，直接產生更新特定 DOM 節點的程式碼，不需要 runtime 比較整棵 virtual DOM tree。
- **Compiler 追蹤依賴**：Svelte compiler 靜態分析每個 reactive 值影響哪些 DOM 節點，只更新受影響的部分。
- **`$derived` 自動快取**：`$derived` 只在依賴的值真正變化時重新計算，等同於自動 memoization。不需要手動指定 dependency array。
- **`$derived.by` 處理複雜推導**：當推導邏輯較複雜時，使用 `$derived.by(() => { ... })` 提供函式形式，同樣自動快取。

```svelte
<script lang="ts">
  let count = $state(0);
  let name = $state('Alice');

  // 只在 count 變化時重新計算——自動 memoization
  let doubled = $derived(count * 2);

  // 只在 name 變化時重新計算
  let greeting = $derived(`Hello, ${name}!`);
</script>

<!-- 修改 count 時，greeting 不會重新計算；反之亦然 -->
<p>{doubled}</p>
<p>{greeting}</p>
```

| 何時這很重要 | 何時不需要擔心 |
|---|---|
| 從 React 遷移時，不需要尋找 `useMemo` 的替代方案 | 小型元件中的簡單計算——Svelte 預設就很快 |
| 複雜的推導邏輯（如排序、過濾大型清單） | 不涉及大量資料的普通頁面 |
| 需要向團隊解釋為何沒有 memoization 程式碼 | 大部分日常開發——Svelte 的預設行為就是最佳化的 |

### 2. `$state.raw` for large collections

`$state` 透過 deep proxy 追蹤物件和陣列的每一層屬性變更。對於大型資料集合（1000+ items），建立大量 proxy 的開銷可能變得顯著。`$state.raw` 只追蹤**變數本身的重新賦值**，不建立 deep proxy。

```ts
// $state：建立 deep proxy，追蹤每個 item 和其屬性的變更
let items = $state<Item[]>([...]); // 10,000 items → 10,000+ proxies

// $state.raw：不建立 proxy，只追蹤 items 變數的重新賦值
let items = $state.raw<Item[]>([...]); // 10,000 items → 0 proxies
```

**關鍵差異**：使用 `$state.raw` 時，直接修改屬性（mutation）不會觸發 UI 更新，必須透過重新賦值：

```ts
let items = $state.raw<Item[]>([...]);

// 錯誤：mutation 不會觸發更新
items[0].name = 'New Name'; // UI 不會更新
items.push(newItem);         // UI 不會更新

// 正確：重新賦值觸發更新
items = items.map(item =>
  item.id === 0 ? { ...item, name: 'New Name' } : item
);
items = [...items, newItem];
```

| 何時用 `$state.raw` | 何時用 `$state` |
|---|---|
| 大型唯讀清單（1000+ items） | 小型狀態物件（表單資料、UI 狀態） |
| 從 API 載入的資料，通常整批替換 | 需要細粒度 mutation tracking（如拖放排序） |
| 效能分析顯示 proxy 開銷是瓶頸 | 預設選擇——除非有明確效能需求 |
| 搭配 immutable update patterns 使用 | 頻繁修改單一屬性的場景 |

### 3. `$inspect` and `$effect.tracking()`

Svelte 5 提供兩個 debug 專用工具，幫助理解 reactivity 的運作方式。

#### `$inspect(value)`

開發模式下，當 `value` 變化時自動 `console.log`。**只在 dev mode 生效**，production build 會被自動移除。

```svelte
<script lang="ts">
  let count = $state(0);
  let items = $state.raw<string[]>([]);

  // 每次 count 變化時，console 會印出新值
  $inspect(count);

  // 可同時觀察多個值
  $inspect(count, items);

  // 自訂 inspector callback
  $inspect(count).with((type, value) => {
    if (type === 'update') {
      console.log(`count updated to: ${value}`);
    }
  });
</script>
```

`$inspect` 的 `.with(fn)` callback 接收兩個參數：
- `type`：`'init'`（初始化時）或 `'update'`（值變化時）。
- `...values`：被觀察的值。

#### `$effect.tracking()`

回傳布林值，表示目前程式碼是否在 reactive tracking context 中執行。主要用於 debug，幫助確認某段程式碼是否被 Svelte 追蹤。

```svelte
<script lang="ts">
  let count = $state(0);

  $effect(() => {
    console.log($effect.tracking()); // true — 在 $effect 內部
  });

  function handleClick() {
    console.log($effect.tracking()); // false — 事件處理器不在 tracking context
  }
</script>
```

| 何時用 | 何時不用 |
|---|---|
| Debug：追蹤某個值為何沒有更新 UI | Production code——`$inspect` 不應留在正式程式碼中 |
| 驗證 `$derived` 是否正確快取 | 當作 logging 工具——改用正式的 logging library |
| 確認程式碼是否在 reactive context 中 | 不需要 debug 時——移除以保持程式碼整潔 |

### 4. Bundle analysis and lazy loading

Svelte 本身已經非常輕量（compiler 產出的 runtime code 極少），但應用的 bundle 大小仍受第三方套件影響。

#### Bundle 分析

使用 `vite-plugin-visualizer` 視覺化分析 bundle 組成：

```bash
npm install -D vite-plugin-visualizer
```

```ts
// vite.config.ts
import { sveltekit } from '@sveltejs/kit/vite';
import { visualizer } from 'vite-plugin-visualizer';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    sveltekit(),
    visualizer({
      filename: 'stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ]
});
```

執行 `npm run build` 後會自動開啟互動式圖表，顯示每個模組的大小。

#### Dynamic import 和 lazy loading

SvelteKit 已自動對每個路由進行 code-splitting，但有時候需要手動拆分：

```ts
// 動態載入：只在需要時才下載模組
const module = await import('$lib/heavy-module.ts');
```

搭配 `<svelte:component>` 做元件級 lazy loading：

```svelte
<script lang="ts">
  import { onMount } from 'svelte';

  let ChartComponent: any = $state(null);

  onMount(async () => {
    const module = await import('$lib/components/HeavyChart.svelte');
    ChartComponent = module.default;
  });
</script>

{#if ChartComponent}
  <svelte:component this={ChartComponent} />
{:else}
  <p>Loading chart...</p>
{/if}
```

| 何時需要手動 code-split | 何時信任 SvelteKit 自動分割 |
|---|---|
| 單一頁面引入非常大的第三方套件（如圖表庫、PDF viewer） | 一般路由元件——SvelteKit 已自動分割 |
| 只有部分使用者會用到的功能（如管理面板） | 每個頁面都需要的核心程式碼 |
| 初始載入時間過長，需要減少 initial JS | 共用的 layout 元件和工具函式 |
| 條件性顯示的重量級元件 | 輕量的 UI 元件 |

### 5. Image optimization and Core Web Vitals

圖片通常是網頁中最大的資源，直接影響 Core Web Vitals 指標。

#### `@sveltejs/enhanced-img`

SvelteKit 官方提供的圖片最佳化套件，自動處理：
- 產生不同尺寸的響應式圖片
- 轉換為現代格式（WebP、AVIF）
- 自動設定 `width` 和 `height` 避免 layout shift

```bash
npm install -D @sveltejs/enhanced-img
```

```svelte
<script lang="ts">
  import { enhancedImg } from '@sveltejs/enhanced-img';
</script>

<enhanced:img src="./hero.jpg" alt="Hero image" />
```

#### Lazy loading images

對於非首屏圖片，使用原生 `loading="lazy"` 延遲載入：

```html
<!-- 首屏圖片：不使用 lazy loading -->
<img src="/hero.jpg" alt="Hero" />

<!-- 非首屏圖片：使用 lazy loading -->
<img src="/gallery-1.jpg" alt="Gallery" loading="lazy" />
```

#### Core Web Vitals 指標

| 指標 | 全名 | 說明 | 優化方向 |
|---|---|---|---|
| LCP | Largest Contentful Paint | 最大內容繪製時間 | 最佳化圖片、預載關鍵資源 |
| INP | Interaction to Next Paint | 互動到下次繪製延遲 | 減少 main thread blocking |
| CLS | Cumulative Layout Shift | 累積版面位移 | 設定圖片 `width`/`height`、避免動態插入內容 |

| 何時專注圖片最佳化 | 何時專注其他效能面向 |
|---|---|
| 圖片密集的頁面（商品列表、相簿） | SPA 互動密集型應用 |
| LCP 指標不佳 | INP 指標不佳——專注 JavaScript 效能 |
| 行動裝置使用者佔比高 | Bundle 大小是主要瓶頸 |

## Step-by-step

### Step 1：使用 `$inspect` 觀察 reactivity 流程

建立一個元件，用 `$inspect` 觀察 reactive 值的變化：

```svelte
<!-- src/routes/perf-lab/+page.svelte -->
<script lang="ts">
  let count = $state(0);
  let multiplier = $state(2);

  let result = $derived(count * multiplier);

  // 觀察各個值的變化
  $inspect(count);
  $inspect(multiplier);
  $inspect(result);

  // 使用 .with() 加上更詳細的 log
  $inspect(result).with((type, value) => {
    console.log(`[result] ${type}: ${value}`);
  });
</script>

<button onclick={() => count++}>count: {count}</button>
<button onclick={() => multiplier++}>multiplier: {multiplier}</button>
<p>Result: {result}</p>
```

開啟 DevTools Console，點擊按鈕觀察：
- 點擊 count 按鈕：`count` 和 `result` 的 `$inspect` 會觸發，但 `multiplier` 不會。
- 這證明了 Svelte 的細粒度響應——只有依賴變化的值才會重新計算。

### Step 2：比較 `$state` 與 `$state.raw` 的效能

建立一個大型清單，比較兩種方式的建立時間：

```svelte
<!-- src/routes/perf-lab/state-compare/+page.svelte -->
<script lang="ts">
  interface Item {
    id: number;
    name: string;
    value: number;
  }

  function generateItems(n: number): Item[] {
    return Array.from({ length: n }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
      value: Math.random() * 100
    }));
  }

  let stateTime = $state(0);
  let rawTime = $state(0);

  function benchmarkState() {
    const start = performance.now();
    let data = $state<Item[]>(generateItems(10000));
    stateTime = performance.now() - start;
  }

  function benchmarkRaw() {
    const start = performance.now();
    let data = $state.raw<Item[]>(generateItems(10000));
    rawTime = performance.now() - start;
  }
</script>

<button onclick={benchmarkState}>Benchmark $state</button>
<button onclick={benchmarkRaw}>Benchmark $state.raw</button>

<p>$state: {stateTime.toFixed(2)}ms</p>
<p>$state.raw: {rawTime.toFixed(2)}ms</p>
```

觀察：`$state.raw` 通常比 `$state` 快數倍，因為它不需要對每個物件建立 deep proxy。

### Step 3：使用 `$effect.tracking()` 確認追蹤上下文

在不同位置呼叫 `$effect.tracking()`，理解哪些地方是 reactive tracking context：

```svelte
<script lang="ts">
  let count = $state(0);

  // 在元件頂層
  console.log('Top-level tracking:', $effect.tracking()); // false

  $effect(() => {
    // 在 $effect 內部
    console.log('Inside $effect:', $effect.tracking()); // true
    console.log('count is', count);
  });

  let doubled = $derived.by(() => {
    // 在 $derived 內部
    console.log('Inside $derived:', $effect.tracking()); // true
    return count * 2;
  });

  function handleClick() {
    // 在事件處理器中
    console.log('In event handler:', $effect.tracking()); // false
    count++;
  }
</script>

<button onclick={handleClick}>Increment: {count} (doubled: {doubled})</button>
```

重點：只有在 `$effect` 和 `$derived` 內部，`$effect.tracking()` 才回傳 `true`。

### Step 4：安裝與設定 `vite-plugin-visualizer`

```bash
npm install -D vite-plugin-visualizer
```

修改 `vite.config.ts`：

```ts
import { sveltekit } from '@sveltejs/kit/vite';
import { visualizer } from 'vite-plugin-visualizer';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    sveltekit(),
    visualizer({
      filename: 'stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ]
});
```

執行 `npm run build`，瀏覽器會自動開啟 `stats.html`，呈現互動式 treemap 圖表。觀察：
- 哪些第三方套件佔據最多空間？
- Svelte runtime 本身佔多少？（通常非常小）
- 有沒有不必要被打包的模組？

### Step 5：用 dynamic import 實作元件 lazy loading

建立一個重量級元件，並使用 dynamic import 延遲載入：

```svelte
<!-- src/lib/components/HeavyChart.svelte -->
<script lang="ts">
  // 假設這個元件引用了大型圖表庫
  let { data = [] }: { data: number[] } = $props();
</script>

<div class="chart">
  {#each data as value, i}
    <div
      class="bar"
      style="height: {value}%; width: {100 / data.length}%"
    ></div>
  {/each}
</div>
```

在頁面中 lazy loading：

```svelte
<!-- src/routes/analytics/+page.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';

  let ChartComponent: any = $state(null);
  let isLoading = $state(true);

  const chartData = [30, 50, 80, 45, 90, 65, 72];

  onMount(async () => {
    const module = await import('$lib/components/HeavyChart.svelte');
    ChartComponent = module.default;
    isLoading = false;
  });
</script>

{#if isLoading}
  <p>Loading chart...</p>
{:else if ChartComponent}
  <svelte:component this={ChartComponent} data={chartData} />
{/if}
```

觀察 Network tab：`HeavyChart.svelte` 對應的 JS chunk 只有在進入 `/analytics` 頁面後才會被下載。

### Step 6：用 `$state.raw` 和 immutable update 最佳化大型清單

```svelte
<!-- src/routes/perf-lab/optimized-list/+page.svelte -->
<script lang="ts">
  interface Item {
    id: number;
    name: string;
    value: number;
    active: boolean;
  }

  // 使用 $state.raw：不建立 deep proxy
  let items = $state.raw<Item[]>(
    Array.from({ length: 10000 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
      value: Math.random() * 100,
      active: false
    }))
  );

  // Immutable update: toggle active
  function toggleItem(id: number) {
    items = items.map(item =>
      item.id === id ? { ...item, active: !item.active } : item
    );
  }

  // Immutable update: add item
  function addItem() {
    const newId = items.length;
    items = [...items, {
      id: newId,
      name: `Item ${newId}`,
      value: Math.random() * 100,
      active: false
    }];
  }

  // Immutable update: remove item
  function removeItem(id: number) {
    items = items.filter(item => item.id !== id);
  }

  let activeCount = $derived(items.filter(i => i.active).length);
</script>

<p>Total: {items.length} | Active: {activeCount}</p>
<button onclick={addItem}>Add Item</button>

<ul>
  {#each items.slice(0, 50) as item (item.id)}
    <li>
      <button onclick={() => toggleItem(item.id)}>
        {item.active ? '✓' : '○'} {item.name}: {item.value.toFixed(2)}
      </button>
      <button onclick={() => removeItem(item.id)}>Remove</button>
    </li>
  {/each}
</ul>
```

### Step 7：加入圖片 `loading="lazy"` 並觀察 LCP 變化

```svelte
<!-- src/routes/gallery/+page.svelte -->
<script lang="ts">
  const images = Array.from({ length: 20 }, (_, i) => ({
    src: `https://picsum.photos/seed/${i}/800/600`,
    alt: `Photo ${i + 1}`
  }));
</script>

<h1>Gallery</h1>

<div class="gallery">
  {#each images as image, i}
    <img
      src={image.src}
      alt={image.alt}
      width="800"
      height="600"
      loading={i < 2 ? 'eager' : 'lazy'}
    />
  {/each}
</div>

<style>
  .gallery {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }
  img {
    width: 100%;
    height: auto;
    border-radius: 8px;
  }
</style>
```

重點：
- 前 2 張圖片使用 `loading="eager"`（預設值），確保首屏圖片立即載入。
- 其餘圖片使用 `loading="lazy"`，只有滾動到可視範圍時才載入。
- 明確設定 `width` 和 `height` 避免 CLS（版面位移）。

開啟 DevTools → Lighthouse，執行效能審核，觀察 LCP 和 CLS 指標。

### Step 8：使用 Browser DevTools Performance tab 做效能分析

1. 開啟 Chrome DevTools → **Performance** tab。
2. 點擊 **Record** 按鈕。
3. 在頁面上執行操作（如過濾清單、切換頁面）。
4. 停止錄製，分析結果：
   - **Main thread**：檢查是否有 long task（>50ms 的黃色條塊）。
   - **Scripting**：JavaScript 執行時間佔比。
   - **Rendering**：DOM 更新和 layout 計算時間。
   - **Painting**：繪製時間。

Tips：
- 使用 `performance.now()` 在程式碼中精確測量特定操作的耗時。
- 在 Performance tab 中使用 CPU throttling（4x slowdown）模擬低階裝置。
- 注意 Svelte 的更新通常非常快（幾毫秒），如果看到長時間 scripting，通常是第三方套件或大量 DOM 操作造成的。

## Hands-on Lab

### Foundation：大型清單效能比較

建立一個包含 10,000 筆資料的清單元件：

- 建立兩個版本：一個使用 `$state`，一個使用 `$state.raw`。
- 加入搜尋過濾功能（使用 `$derived` 過濾清單）。
- 使用 `performance.now()` 測量初始化時間和更新時間。
- 只渲染前 100 筆（避免 DOM 過多影響測量）。
- 使用 `$inspect` 觀察 `$derived` 何時重新計算。

驗收：能清楚看到 `$state.raw` 在大型清單上的效能優勢；`npx svelte-check` 通過。

### Advanced：虛擬滾動（Virtual Scrolling）

在 Foundation 基礎上加入：

- 實作虛擬滾動（virtual scrolling / windowing），只渲染可視範圍內的 items。
- 計算可視區域的起始和結束 index，使用 `$derived` 從完整清單中切片。
- 使用 `$effect` 監聽 scroll 事件更新可視範圍。
- 測量滾動時的 frame rate（使用 `requestAnimationFrame` 或 Performance tab）。
- 對比有無虛擬滾動的 DOM 節點數量和渲染效能。

驗收：即使清單有 10,000 筆，DOM 中同時只有約 20–50 個 `<li>` 節點；滾動流暢無卡頓。

### Challenge：完整 SvelteKit 應用效能最佳化

在 Advanced 基礎上，對一個完整 SvelteKit 應用進行效能最佳化：

- 使用 `vite-plugin-visualizer` 分析 bundle 組成，找出最大的依賴。
- 對非關鍵元件實作 lazy loading（dynamic import）。
- 將大型清單資料改用 `$state.raw` + immutable update patterns。
- 最佳化圖片：使用 `loading="lazy"` 和明確的 `width`/`height`。
- 目標：initial JS bundle < 100KB（gzipped）。
- 使用 Lighthouse 驗證 Core Web Vitals 全部為綠色。

驗收：initial JS < 100KB gzipped；Lighthouse Performance 分數 > 90；所有 CWV 指標為綠色。

## Reference Solution

### Performance demo — `$state.raw` with filtered large list

```svelte
<!-- PerformanceDemo.svelte -->
<script lang="ts">
  interface Item {
    id: number;
    name: string;
    value: number;
  }

  // For large read-only datasets, use $state.raw
  let items = $state.raw<Item[]>(
    Array.from({ length: 10000 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
      value: Math.random() * 100
    }))
  );

  let search = $state('');

  // $derived automatically caches - no manual memoization needed
  let filtered = $derived.by(() => {
    if (!search) return items;
    const term = search.toLowerCase();
    return items.filter(item => item.name.toLowerCase().includes(term));
  });

  let count = $derived(filtered.length);

  // Debug: inspect reactivity in dev mode
  $inspect(count);

  function regenerate() {
    // With $state.raw, must reassign (not mutate)
    items = Array.from({ length: 10000 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
      value: Math.random() * 100
    }));
  }
</script>

<div>
  <input bind:value={search} placeholder="Filter items..." />
  <p>Showing {count} of {items.length} items</p>
  <button onclick={regenerate}>Regenerate</button>

  <ul>
    {#each filtered.slice(0, 100) as item (item.id)}
      <li>{item.name}: {item.value.toFixed(2)}</li>
    {/each}
    {#if filtered.length > 100}
      <li>... and {filtered.length - 100} more</li>
    {/if}
  </ul>
</div>
```

### Lazy loading pattern

```svelte
<!-- src/routes/analytics/+page.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';

  let ChartComponent: any = $state(null);

  const chartData = [30, 50, 80, 45, 90, 65, 72];

  onMount(async () => {
    const module = await import('$lib/components/HeavyChart.svelte');
    ChartComponent = module.default;
  });
</script>

{#if ChartComponent}
  <svelte:component this={ChartComponent} data={chartData} />
{:else}
  <p>Loading chart...</p>
{/if}
```

### `$inspect` and debugging pattern

```svelte
<!-- src/routes/perf-lab/debug/+page.svelte -->
<script lang="ts">
  let items = $state.raw<string[]>(['apple', 'banana', 'cherry']);
  let filter = $state('');

  let filtered = $derived.by(() => {
    if (!filter) return items;
    return items.filter(i => i.includes(filter));
  });

  // Inspect: see when derived recalculates
  $inspect(filtered).with((type, value) => {
    console.log(`[filtered] ${type}:`, value);
  });

  // Verify tracking context
  $effect(() => {
    console.log('Tracking inside $effect:', $effect.tracking()); // true
    console.log('Filtered count:', filtered.length);
  });

  function addItem() {
    console.log('Tracking in handler:', $effect.tracking()); // false
    items = [...items, `item-${items.length}`];
  }
</script>

<input bind:value={filter} placeholder="Filter..." />
<button onclick={addItem}>Add</button>

<ul>
  {#each filtered as item}
    <li>{item}</li>
  {/each}
</ul>
```

## Common Pitfalls

### 1. 過早使用 `$state.raw` 進行最佳化

```ts
// 不必要：小型資料集用 $state 就好
let formData = $state.raw({ name: '', email: '' });
// 改用 $state.raw 後，formData.name = 'Alice' 不會觸發更新！

// 正確：小型可變狀態使用 $state
let formData = $state({ name: '', email: '' });
formData.name = 'Alice'; // 正常觸發 UI 更新
```

**原則**：`$state` 是預設選擇。只有在效能分析明確顯示 proxy 開銷是瓶頸時（通常 1000+ items），才考慮 `$state.raw`。

### 2. `$state.raw` 使用 mutation 而非 reassignment

```ts
let items = $state.raw<Item[]>([...]);

// 錯誤：直接 mutation → UI 不會更新
items.push({ id: 999, name: 'New' });
items[0].name = 'Updated';

// 正確：重新賦值
items = [...items, { id: 999, name: 'New' }];
items = items.map(item =>
  item.id === 0 ? { ...item, name: 'Updated' } : item
);
```

### 3. 在 production 程式碼中留下 `$inspect`

`$inspect` 在 production build 中會被移除，不會影響效能。但為了程式碼可讀性，debug 完畢後應移除 `$inspect` 呼叫：

```svelte
<script lang="ts">
  let count = $state(0);

  // 開發時使用，debug 完應移除
  $inspect(count);
  $inspect(count).with(console.trace);

  // 不要把 $inspect 當作正式的 logging 方案
</script>
```

### 4. 未善用 SvelteKit 的自動 code splitting

SvelteKit 已自動為每個路由生成獨立的 JS chunk。不需要手動合併或分割路由程式碼：

```
src/routes/
  +page.svelte         → 自動產生獨立 chunk
  about/+page.svelte   → 自動產生獨立 chunk
  blog/+page.svelte    → 自動產生獨立 chunk
```

**常見錯誤**：在根 layout 中 import 所有頁面需要的大型套件，導致 initial bundle 過大。應該讓每個頁面自行 import 所需的套件。

```svelte
<!-- 錯誤：在 +layout.svelte 中 import 大型套件 -->
<script lang="ts">
  import { Chart } from 'chart.js'; // 所有頁面都會載入 Chart.js！
</script>

<!-- 正確：只在需要的頁面 import -->
<!-- src/routes/analytics/+page.svelte -->
<script lang="ts">
  import { Chart } from 'chart.js'; // 只有 /analytics 頁面會載入
</script>
```

### 5. 渲染大量 DOM 節點而不分頁或虛擬化

```svelte
<!-- 錯誤：一次渲染 10,000 個 DOM 節點 -->
{#each items as item (item.id)}
  <li>{item.name}</li>
{/each}

<!-- 正確：限制渲染數量 -->
{#each items.slice(0, 100) as item (item.id)}
  <li>{item.name}</li>
{/each}
{#if items.length > 100}
  <p>Showing 100 of {items.length} items</p>
{/if}

<!-- 更好：實作分頁或虛擬滾動 -->
```

無論 Svelte 的 reactivity 多快，大量 DOM 節點本身就會造成瀏覽器的 layout 和 paint 變慢。

## Checklist

- [ ] 能解釋為何 Svelte 不需要像 React 那樣的 memoization（`useMemo`、`useCallback`）
- [ ] 能對大型資料集使用 `$state.raw` 並搭配正確的 immutable update patterns
- [ ] 能使用 `$inspect` 和 `$inspect().with()` debug reactivity 問題
- [ ] 能使用 `$effect.tracking()` 確認 reactive tracking context
- [ ] 能安裝和使用 `vite-plugin-visualizer` 分析 bundle 大小
- [ ] 能使用 dynamic import 和 `<svelte:component>` 實作 lazy loading
- [ ] 能最佳化圖片載入（`loading="lazy"`、明確的 `width`/`height`）
- [ ] `npx svelte-check` 通過，無型別錯誤

## Further Reading

- [$state — Svelte](https://svelte.dev/docs/svelte/$state)
- [$state.raw — Svelte](https://svelte.dev/docs/svelte/$state#$state.raw)
- [$derived — Svelte](https://svelte.dev/docs/svelte/$derived)
- [$inspect — Svelte](https://svelte.dev/docs/svelte/$inspect)
- [$effect.tracking — Svelte](https://svelte.dev/docs/svelte/$effect#$effect.tracking)
- [Performance — SvelteKit](https://svelte.dev/docs/kit/performance)
- [Images — SvelteKit](https://svelte.dev/docs/kit/images)
- [Svelte 5 source — GitHub](https://github.com/sveltejs/svelte)
