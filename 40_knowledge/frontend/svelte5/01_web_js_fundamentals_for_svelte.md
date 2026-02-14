---
title: "Web/JS Fundamentals for Svelte / Svelte 所需的 Web 與 JS 基礎"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "01"
level: beginner
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [00_series_overview]
---
# Web/JS Fundamentals for Svelte / Svelte 所需的 Web 與 JS 基礎

## Goal

確保學習者具備 Svelte 開發所需的 JavaScript 與 Web 基礎知識。本章不涉及 Svelte 語法細節，而是建立正確的底層心智模型，讓後續章節可以專注在框架特有概念上。

掌握 value vs reference types、array methods、async/await、destructuring 等 JavaScript 核心概念，對於理解 Svelte 5 的 `$state` Proxy 追蹤機制、`$props()` 解構語法以及 SvelteKit `load` 函式至關重要。本章打下的基礎將貫穿整個系列，是寫出正確且高效 Svelte 程式碼的先決條件。

- 銜接上一章：Ch00 建立了學習工作區（SvelteKit 專案、TypeScript 設定、編輯器與 dev server），本章補齊進入 Svelte 前需要的 JS/Web 基礎。
- 下一章預告：Ch02 將正式進入 Svelte 元件的 `.svelte` 檔案結構，包含 `$props()`、markup 語法與 scoped style。

## Prerequisites

- 已完成 `00_series_overview`，專案可執行 `npm run dev`。
- 具備基本程式設計概念（變數、函式、迴圈、條件判斷）。
- Node.js >= 22 已安裝，可在終端機執行 `node` 與 `npx` 指令。

## Core Concepts

### 1. Value vs Reference Types — 值與參考型別

JavaScript 的 primitive（`string`, `number`, `boolean`, `null`, `undefined`, `bigint`, `symbol`）是 **by value**，物件與陣列是 **by reference**。

**何時用 spread / `structuredClone` 做 immutable update：**
- 當你需要保留原始資料不被改動時（例如：undo/redo、比較前後差異、傳遞給其他元件的 props）。
- 淺層物件用 spread operator `{ ...obj, key: newValue }` 即可。
- 巢狀物件需要 `structuredClone(obj)` 或逐層 spread。

**何時直接 mutate：**
- Svelte 5 的 `$state` 允許直接 mutation 並自動追蹤變更（與 Svelte 4 assignment-based reactivity 不同）。
- 在 local scope 的暫時運算（例如 sort 一份已複製的陣列），直接 mutate 更簡潔。

```ts
// immutable update — 建立新物件
const user = { name: "Alice", age: 30 };
const updated = { ...user, age: 31 }; // user 不變

// deep clone — 巢狀結構
const nested = { profile: { scores: [90, 85] } };
const cloned = structuredClone(nested);
cloned.profile.scores.push(100); // nested 不受影響

// direct mutation — Svelte 5 $state 場景
// let items = $state([1, 2, 3]);
// items.push(4); // Svelte 5 可追蹤此變更
```

### 2. Array APIs — 陣列宣告式方法

`map`, `filter`, `reduce`, `find`, `findIndex` 是 Svelte template 與邏輯層最常用的工具。

**何時用 declarative array methods：**
- 資料轉換、篩選、聚合 — 可讀性高，適合 one-liner 或 chain。
- 在 Svelte markup 的 `{#each}` 之前做資料前處理。

**何時用 for loop：**
- 需要 `break` / `continue` 的提早跳出邏輯。
- 單次迭代需要同時產出多個 side-effect。
- 效能敏感的大量資料處理（避免多次遍歷）。

```ts
type Task = { id: number; text: string; done: boolean };

const tasks: Task[] = [
  { id: 1, text: "learn Svelte", done: false },
  { id: 2, text: "setup project", done: true },
  { id: 3, text: "write tests", done: false },
];

// map — 轉換
const labels = tasks.map((t) => t.text.toUpperCase());

// filter — 篩選
const pending = tasks.filter((t) => !t.done);

// reduce — 聚合
const doneCount = tasks.reduce((acc, t) => acc + (t.done ? 1 : 0), 0);

// find — 查找單筆
const target = tasks.find((t) => t.id === 2);

// findIndex — 查找索引
const idx = tasks.findIndex((t) => t.id === 3); // 2
```

### 3. Async/Await and Promises — 非同步基礎

SvelteKit 的 `load` 函式、API routes、client-side fetch 全部建立在 Promise 上。

**何時用 async/await：**
- 大多數情況 — 語法線性，錯誤處理用 `try/catch`，可讀性最佳。

**何時用 `.then()` chain：**
- 需要同時啟動多個 Promise 並用 `Promise.all()` 等待。
- 在不支援 top-level await 的 context 中（少見，SvelteKit module scripts 支援）。

```ts
// async/await — 推薦寫法
async function fetchUser(id: number): Promise<{ name: string }> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// Promise.all — 並行請求
async function fetchDashboard() {
  const [user, tasks] = await Promise.all([
    fetchUser(1),
    fetch("/api/tasks").then((r) => r.json()),
  ]);
  return { user, tasks };
}

// setTimeout 包成 Promise — 練習用
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
```

### 4. Destructuring and Rest/Spread — 解構與展開

Svelte 元件的 `$props()` 回傳物件，解構是取 props 的標準方式。

**何時用解構取值：**
- 從函式參數或回傳值中取出已知欄位。
- 在 Svelte 元件中取 props：`let { title, count } = $props();`。
- 用 rest syntax 收集剩餘屬性：`let { class: className, ...rest } = $props();`。

**何時保留完整物件：**
- 屬性名稱是動態的，需要用 `obj[key]` 存取。
- 需要將整個物件傳遞給子元件或函式。

```ts
// 物件解構
const config = { host: "localhost", port: 3000, debug: true };
const { host, port, ...others } = config;
// host = "localhost", port = 3000, others = { debug: true }

// 陣列解構
const [first, second, ...remaining] = [10, 20, 30, 40];
// first = 10, second = 20, remaining = [30, 40]

// 函式參數解構（模擬 Svelte props 模式）
function greet({ name, greeting = "Hello" }: { name: string; greeting?: string }) {
  return `${greeting}, ${name}!`;
}

// spread 合併物件
const defaults = { theme: "light", lang: "zh-TW" };
const userPrefs = { theme: "dark" };
const merged = { ...defaults, ...userPrefs }; // { theme: "dark", lang: "zh-TW" }
```

### 5. Svelte-Specific Fundamentals — Svelte 特有基礎

**Svelte 是 compile-time framework：**
- 沒有 virtual DOM。Svelte 在 build time 將 `.svelte` 檔案編譯成高效的原生 JavaScript，直接操作 DOM。
- 與 React（runtime diffing）和 Vue（runtime reactivity + virtual DOM）不同，Svelte 的反應式邏輯在編譯時就已確定。

**`.svelte` 檔案格式概覽：**

```svelte
<script lang="ts">
  // 邏輯區：TypeScript，runes ($state, $derived, $effect) 在此宣告
  let count = $state(0);
</script>

<!-- 標記區：HTML + Svelte 語法 -->
<button onclick={() => count++}>
  Clicked {count} times
</button>

<style>
  /* 樣式區：自動 scoped，只影響此元件 */
  button {
    font-size: 1.2rem;
  }
</style>
```

**何時使用 TypeScript `lang="ts"`：**
- 所有 `.svelte` 檔案的 `<script>` 區塊建議加上 `lang="ts"`，享受型別檢查與自動補全。
- 純 `.ts` 模組（如 `src/lib/` 下的 utility）直接使用 TypeScript。

**何時不需要理解編譯細節：**
- 日常開發時，把 `.svelte` 當成「增強版 HTML」即可。
- 效能調校或除錯 hydration 問題時，才需深入了解編譯產出。

## Step-by-step

### Step 1 — 建立練習資料夾

```bash
mkdir -p src/lib/practice
```

在專案的 `src/lib/practice/` 資料夾中建立本章所有練習檔案，避免與正式程式碼混淆。

### Step 2 — 練習 value vs reference

建立 `src/lib/practice/01-value-ref.ts`：

```ts
// 1. primitive — by value
let a = 10;
let b = a;
b = 20;
console.log(a, b); // 10 20

// 2. object — by reference (shallow copy)
const original = { name: "Alice", scores: [90, 85] };
const shallow = { ...original };
shallow.name = "Bob";
console.log(original.name); // "Alice" — 第一層安全

shallow.scores.push(100);
console.log(original.scores); // [90, 85, 100] — 第二層被改到！

// 3. deep clone
const deep = structuredClone(original);
deep.scores.push(200);
console.log(original.scores.length); // 3 — 不受影響
```

驗證：用 `npx tsx src/lib/practice/01-value-ref.ts` 執行，觀察輸出。

### Step 3 — 練習 array methods

建立 `src/lib/practice/02-array-methods.ts`：

```ts
type Product = { id: number; name: string; price: number; inStock: boolean };

const products: Product[] = [
  { id: 1, name: "Keyboard", price: 2500, inStock: true },
  { id: 2, name: "Mouse", price: 800, inStock: false },
  { id: 3, name: "Monitor", price: 12000, inStock: true },
  { id: 4, name: "Webcam", price: 1500, inStock: true },
];

// map: 取出名稱清單
const names = products.map((p) => p.name);

// filter: 只要有庫存的
const available = products.filter((p) => p.inStock);

// reduce: 計算有庫存商品的總價
const totalPrice = available.reduce((sum, p) => sum + p.price, 0);

// find: 找特定商品
const monitor = products.find((p) => p.name === "Monitor");

// findIndex: 找索引
const mouseIdx = products.findIndex((p) => p.id === 2);

console.log({ names, available, totalPrice, monitor, mouseIdx });
```

### Step 4 — 練習 destructuring

建立 `src/lib/practice/03-destructuring.ts`：

```ts
// 模擬 Svelte $props() 的使用模式
type ButtonProps = {
  label: string;
  variant?: "primary" | "secondary";
  disabled?: boolean;
  class?: string;
};

function createButton(props: ButtonProps) {
  const { label, variant = "primary", disabled = false, ...rest } = props;
  return { label, variant, disabled, extra: rest };
}

console.log(createButton({ label: "Submit" }));
console.log(createButton({ label: "Cancel", variant: "secondary", class: "ml-2" }));

// 陣列解構
const [head, ...tail] = [1, 2, 3, 4, 5];
console.log(head, tail); // 1 [2, 3, 4, 5]

// 巢狀解構
const response = { data: { user: { name: "Alice", role: "admin" } } };
const {
  data: {
    user: { name, role },
  },
} = response;
console.log(name, role); // "Alice" "admin"
```

### Step 5 — 練習 async/await

建立 `src/lib/practice/04-async-await.ts`：

```ts
function delay(ms: number): Promise<string> {
  return new Promise((resolve) => setTimeout(() => resolve(`waited ${ms}ms`), ms));
}

async function sequential() {
  console.log("sequential start");
  const a = await delay(500);
  const b = await delay(300);
  console.log("sequential done:", a, b);
}

async function parallel() {
  console.log("parallel start");
  const [a, b] = await Promise.all([delay(500), delay(300)]);
  console.log("parallel done:", a, b); // 總時間 ~500ms，非 800ms
}

async function withErrorHandling() {
  try {
    const result = await Promise.reject(new Error("network failure"));
    console.log(result);
  } catch (err) {
    console.error("caught:", (err as Error).message);
  }
}

sequential()
  .then(() => parallel())
  .then(() => withErrorHandling());
```

### Step 6 — 理解 `.svelte` 檔案結構

建立 `src/lib/practice/05-SvelteFileDemo.svelte`：

```svelte
<script lang="ts">
  // 1. Script block — 邏輯區
  //    - 使用 TypeScript（lang="ts"）
  //    - Svelte 5 runes 在此宣告
  //    - import 其他模組
  let message = $state("Hello from Svelte!");

  function handleClick() {
    message = "You clicked the button!";
  }
</script>

<!-- 2. Markup block — 標記區 -->
<!--    - HTML + Svelte 模板語法 -->
<!--    - 用 {} 嵌入 JavaScript 表達式 -->
<div class="demo">
  <p>{message}</p>
  <button onclick={handleClick}>Click me</button>
</div>

<!-- 3. Style block — 樣式區 -->
<!--    - 自動 scoped：只影響此元件 -->
<!--    - 不需要 CSS Modules 或 BEM -->
<style>
  .demo {
    padding: 1rem;
    border: 1px solid #ccc;
    border-radius: 8px;
  }

  button {
    cursor: pointer;
    padding: 0.5rem 1rem;
  }
</style>
```

閱讀此檔案，理解三個區塊的職責。此時不需要在瀏覽器中執行，Ch02 會正式教元件使用方式。

### Step 7 — 理解 Svelte compilation model

Svelte 的核心流程：

```
  .svelte 原始碼
       │
  ┌────▼────┐
  │ Svelte  │  build time（vite build / dev server）
  │ Compiler│
  └────┬────┘
       │
  optimized vanilla JS
  （直接操作 DOM，無 virtual DOM overhead）
```

關鍵觀念：
1. **No virtual DOM** — React 在 runtime 做 diffing；Svelte 在 compile time 就產出精確的 DOM 更新指令。
2. **Smaller bundle** — 只打包用到的 Svelte runtime code，未使用的功能會被 tree-shaken。
3. **Runes 是編譯器指令** — `$state`, `$derived`, `$effect` 看似函式呼叫，實際由編譯器轉換為追蹤邏輯。

### Step 8 — 執行 `svelte-check` 驗證

```bash
npx svelte-check --tsconfig ./tsconfig.json
```

確認輸出中沒有 error。若有 warning 可暫時忽略，但 error 必須修復後才進入下一章。

常見修復方向：
- 缺少型別宣告 → 補上 TypeScript type。
- import 路徑錯誤 → 確認 `$lib` alias 正確指向 `src/lib`。
- 未知的 rune → 確認 `svelte` 版本 >= 5.0。

## Hands-on Lab

### Foundation（基礎）

**任務：建立 TypeScript utility module。**

建立 `src/lib/practice/utils.ts`，匯出以下函式：

```ts
type Item = { id: number; text: string; done: boolean };

/** 切換指定 id 項目的 done 狀態，回傳新陣列（不可 mutate 原陣列） */
export function toggleById(items: Item[], id: number): Item[];

/** 回傳 done === true 的項目數量 */
export function completedCount(items: Item[]): number;

/** 以 keyword 篩選 text 欄位（不分大小寫），空字串回傳全部 */
export function filterByKeyword(items: Item[], keyword: string): Item[];

/** 以 text 欄位字母排序，回傳新陣列（不可 mutate 原陣列） */
export function sortByText(items: Item[]): Item[];
```

**驗收條件：**
- 所有函式具備完整 TypeScript 型別註記。
- `toggleById` 與 `sortByText` 不改變原始陣列。
- 準備至少 3 筆測試資料，在 `console.log` 中驗證輸出。

### Advanced（進階）

**任務：建立 async data fetcher module。**

建立 `src/lib/practice/fetcher.ts`，匯出以下函式：

```ts
type FetchResult<T> = { ok: true; data: T } | { ok: false; error: string };

/** 通用 fetch wrapper，自動處理 JSON 解析與錯誤 */
export async function safeFetch<T>(url: string): Promise<FetchResult<T>>;

/** 帶有 timeout 的 fetch，超時回傳錯誤 */
export async function fetchWithTimeout<T>(
  url: string,
  timeoutMs: number,
): Promise<FetchResult<T>>;

/** 批次 fetch 多個 URL，回傳所有結果（settled，不因單一失敗中斷） */
export async function fetchAll<T>(urls: string[]): Promise<FetchResult<T>[]>;
```

**驗收條件：**
- `safeFetch` 在 HTTP error 時回傳 `{ ok: false, error: "..." }` 而非拋出例外。
- `fetchWithTimeout` 使用 `AbortController` 實作 timeout。
- `fetchAll` 使用 `Promise.allSettled`，即使部分 URL 失敗仍回傳所有結果。
- 所有函式具備完整泛型型別。

### Challenge（挑戰）

**任務：建立 `.svelte` 元件整合 utility module。**

建立 `src/lib/practice/06-UtilsDemo.svelte`：

```svelte
<script lang="ts">
  import { toggleById, completedCount, filterByKeyword, sortByText } from "./utils";
  // 使用 $state 管理項目清單與搜尋關鍵字
  // 使用 $derived 計算篩選後的清單與完成數量
  // 提供按鈕觸發 toggle、排序等操作
</script>
```

**驗收條件：**
- 元件使用 `$state` 與 `$derived` runes。
- import 來自 Foundation 階段完成的 `utils.ts`。
- 至少展示 `toggleById` 和 `filterByKeyword` 的互動效果。
- `<script>` 標籤包含 `lang="ts"`。
- `npx svelte-check` 通過，無 error。

## Reference Solution

### utils.ts — 完整實作

```ts
// src/lib/practice/utils.ts
export type Item = { id: number; text: string; done: boolean };

export function toggleById(items: Item[], id: number): Item[] {
  return items.map((item) =>
    item.id === id ? { ...item, done: !item.done } : item
  );
}

export function completedCount(items: Item[]): number {
  return items.filter((item) => item.done).length;
}

export function filterByKeyword(items: Item[], keyword: string): Item[] {
  const k = keyword.trim().toLowerCase();
  if (!k) return items;
  return items.filter((item) => item.text.toLowerCase().includes(k));
}

export function sortByText(items: Item[]): Item[] {
  return [...items].sort((a, b) => a.text.localeCompare(b.text));
}
```

### fetcher.ts — 完整實作

```ts
// src/lib/practice/fetcher.ts
export type FetchResult<T> = { ok: true; data: T } | { ok: false; error: string };

export async function safeFetch<T>(url: string): Promise<FetchResult<T>> {
  try {
    const res = await fetch(url);
    if (!res.ok) return { ok: false, error: `HTTP ${res.status}: ${res.statusText}` };
    const data: T = await res.json();
    return { ok: true, data };
  } catch (err) {
    return { ok: false, error: (err as Error).message };
  }
}

export async function fetchWithTimeout<T>(
  url: string,
  timeoutMs: number,
): Promise<FetchResult<T>> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(url, { signal: controller.signal });
    clearTimeout(timer);
    if (!res.ok) return { ok: false, error: `HTTP ${res.status}: ${res.statusText}` };
    const data: T = await res.json();
    return { ok: true, data };
  } catch (err) {
    clearTimeout(timer);
    if ((err as Error).name === "AbortError") {
      return { ok: false, error: `Request timed out after ${timeoutMs}ms` };
    }
    return { ok: false, error: (err as Error).message };
  }
}

export async function fetchAll<T>(urls: string[]): Promise<FetchResult<T>[]> {
  const settled = await Promise.allSettled(
    urls.map((url) => safeFetch<T>(url)),
  );

  return settled.map((result) => {
    if (result.status === "fulfilled") return result.value;
    return { ok: false as const, error: result.reason?.message ?? "Unknown error" };
  });
}
```

### UtilsDemo.svelte — 元件實作

```svelte
<!-- src/lib/practice/06-UtilsDemo.svelte -->
<script lang="ts">
  import {
    toggleById,
    completedCount,
    filterByKeyword,
    sortByText,
    type Item,
  } from "./utils";

  let items: Item[] = $state([
    { id: 1, text: "Learn TypeScript", done: true },
    { id: 2, text: "Setup SvelteKit", done: false },
    { id: 3, text: "Read Svelte docs", done: false },
    { id: 4, text: "Build first component", done: false },
  ]);

  let keyword = $state("");
  let sorted = $state(false);

  let visibleItems = $derived(() => {
    const filtered = filterByKeyword(items, keyword);
    return sorted ? sortByText(filtered) : filtered;
  });

  let doneCount = $derived(completedCount(items));

  function handleToggle(id: number) {
    items = toggleById(items, id);
  }
</script>

<div class="utils-demo">
  <h2>Todo Practice</h2>
  <p>Completed: {doneCount} / {items.length}</p>

  <input type="text" placeholder="Filter..." bind:value={keyword} />
  <button onclick={() => (sorted = !sorted)}>
    {sorted ? "Unsort" : "Sort A-Z"}
  </button>

  <ul>
    {#each visibleItems() as item (item.id)}
      <li>
        <label>
          <input
            type="checkbox"
            checked={item.done}
            onchange={() => handleToggle(item.id)}
          />
          <span class:done={item.done}>{item.text}</span>
        </label>
      </li>
    {/each}
  </ul>
</div>

<style>
  .utils-demo {
    max-width: 480px;
    padding: 1rem;
    font-family: system-ui, sans-serif;
  }

  input[type="text"] {
    padding: 0.4rem;
    margin-right: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  ul {
    list-style: none;
    padding: 0;
  }

  li {
    padding: 0.3rem 0;
  }

  .done {
    text-decoration: line-through;
    opacity: 0.6;
  }
</style>
```

## Common Pitfalls

### 1. 把 Svelte 當作 runtime framework 理解

Svelte 是 compiler，不是 library。不要期待在 browser DevTools 中看到 Svelte runtime 在做 virtual DOM diffing — 它根本沒有 virtual DOM。若用 React 或 Vue 的心智模型來理解 Svelte，會在效能分析、bundle 分析、reactivity 除錯時產生錯誤判斷。

### 2. 使用 `var` 而非 `let` / `const`

`var` 有 hoisting 與 function scope 的行為，容易導致難以追蹤的 bug。在現代 JavaScript 與 TypeScript 中，一律使用 `const`（預設）或 `let`（需要重新賦值時）。Svelte 5 的 `$state` 搭配 `let` 使用。

```ts
// Bad
var count = 0;

// Good
let count = $state(0);
const MAX_COUNT = 100;
```

### 3. 忘記 `Array.prototype.sort()` 會 mutate 原始陣列

這是常見的 immutability 錯誤來源。在需要保留原陣列的場景中，務必先複製再排序。

```ts
const original = [3, 1, 2];

// Bad — mutates original
original.sort(); // original 變成 [1, 2, 3]

// Good — 建立新陣列再排序
const sorted = [...original].sort();
// 或使用 toSorted()（ES2023）
const sorted2 = original.toSorted();
```

### 4. 混淆 Svelte 5 `$state` 追蹤機制與 Svelte 4 的 assignment-based reactivity

Svelte 4 要求「重新賦值」才能觸發更新（`items = items` 技巧），Svelte 5 的 `$state` 使用 Proxy-based fine-grained tracking，允許直接 mutation（如 `items.push(x)`）。若你從 Svelte 4 遷移，需要卸下「必須 reassign」的習慣；若你從 React 過來，注意 Svelte 5 允許 mutation，不要硬套 immutable 模式。

```ts
// Svelte 4 寫法（不再需要）
// items = [...items, newItem];

// Svelte 5 寫法（直接 mutate 即可）
// items.push(newItem); // $state proxy 會自動追蹤
```

### 5. 在 `map` callback 中忘記 `return`

使用大括號 `{}` 的 arrow function 必須明確 `return`。這是初學者最常遇到的 undefined 結果來源。

```ts
// Bad — 回傳 undefined[]
const result = items.map((item) => {
  item.text.toUpperCase();
});

// Good — 明確 return
const result = items.map((item) => {
  return item.text.toUpperCase();
});

// Good — 簡潔寫法（無大括號，自動 return）
const result = items.map((item) => item.text.toUpperCase());
```

## Checklist

- [ ] 能解釋 value type 與 reference type 的差異，知道何時需要 shallow copy / deep clone。
- [ ] 能使用 `map` / `filter` / `reduce` 對陣列做宣告式轉換。
- [ ] 能寫出 `async/await` 函式，並用 `try/catch` 處理錯誤。
- [ ] 能對物件與陣列做 destructuring，包含 rest syntax。
- [ ] 能解釋為什麼 Svelte 是 compiler 而非 runtime library，以及這對 bundle size 和效能的影響。
- [ ] 能描述 `.svelte` 檔案的三個區塊（script / markup / style）各自的職責。
- [ ] `npx svelte-check` 通過，無 error。

## Further Reading

- [Svelte Tutorial — Introduction](https://svelte.dev/tutorial/svelte/welcome-to-svelte) — 官方互動教學，從零開始理解 Svelte 編譯模型。
- [Svelte Documentation — .svelte files](https://svelte.dev/docs/svelte/svelte-files) — `.svelte` 檔案結構的官方說明。
- [Svelte Documentation — $state](https://svelte.dev/docs/svelte/$state) — Svelte 5 reactivity 的核心 rune，包含 value/reference 在響應式系統中的行為。
- [Svelte Tutorial — Reactivity fundamentals](https://svelte.dev/tutorial/svelte/state) — 透過互動練習理解 Svelte 5 狀態管理，涵蓋 destructuring、陣列操作等 JS 基礎的實際應用。
- [Svelte Tutorial — Await blocks](https://svelte.dev/tutorial/svelte/await-blocks) — 展示 Svelte 如何處理 Promise 與 async 資料流，銜接本章 async/await 知識。
