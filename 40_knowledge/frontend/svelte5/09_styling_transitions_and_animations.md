---
title: "Styling, Transitions, and Animations / 樣式、過渡與動畫"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-17
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "09"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [08_snippets_and_component_composition]
---
# Styling, Transitions, and Animations / 樣式、過渡與動畫

## Goal

掌握 Svelte 的 scoped styling、內建 transition/animation 指令，以及 action 機制。

視覺表現與互動回饋是優秀使用者體驗的關鍵。Svelte 提供零設定的 scoped CSS、宣告式的 transition/animation 系統，以及可重用的 `use:action` 指令，讓你無需依賴外部動畫庫即可為元件加入流暢的視覺效果。學完本章後，你將能為任何 Svelte 元件添加專業級的樣式與動態效果。

- **銜接上一章**：Ch08 學會了元件組合模式，現在要讓元件在視覺上更完善。
- **下一章預告**：Ch10 將進入 SvelteKit 專案架構與路由系統。

## Prerequisites

- 已完成第 08 章（Snippets & Component Composition）。
- 熟悉 `$state`、`$derived`、`$effect` 的用法（Ch03、Ch06）。
- 理解 `{#if}` / `{#each}` 模板語法（Ch04）。
- 熟悉元件 props 與 snippet 傳遞（Ch08）。

## Core Concepts

### 1. Scoped `<style>` / `:global()` / CSS custom properties

Svelte 的 `<style>` 預設為 scoped，編譯時會自動加上唯一的 class hash，確保樣式只影響當前元件，不會洩漏到其他元件：

```svelte
<p>This paragraph is styled.</p>

<style>
  /* 只影響這個元件內的 <p>，不影響其他元件 */
  p {
    color: steelblue;
    font-weight: bold;
  }
</style>
```

使用 `:global()` 設定全域樣式，影響範圍擴展到整個應用：

```svelte
<style>
  /* 只影響當前元件的 div */
  div { padding: 1rem; }

  /* 全域樣式：影響所有 .highlight 元素 */
  :global(.highlight) {
    background: yellow;
  }

  /* 限定在當前元件下的全域選擇器 */
  div :global(strong) {
    color: red;
  }
</style>
```

CSS custom properties（自訂屬性）可從父元件傳入子元件，作為主題化手段：

```svelte
<!-- Parent.svelte -->
<Card --card-bg="aliceblue" --card-radius="12px">
  <p>Card content here</p>
</Card>

<!-- Card.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  let { children }: { children: Snippet } = $props();
</script>

<div class="card">
  {@render children()}
</div>

<style>
  .card {
    background: var(--card-bg, white);
    border-radius: var(--card-radius, 8px);
  }
</style>
```

| 何時用 scoped style | 何時用全域 CSS 框架（Tailwind 等） |
|---|---|
| 元件內部樣式，不需要跨元件共享 | 專案需要統一的 utility-first 設計系統 |
| 想要樣式與元件共存、好維護 | 團隊已有 Tailwind / UnoCSS 工作流 |
| 小型專案或原型開發 | 大型專案需要一致的設計語言 |
| 需要精細控制 CSS specificity | 需要快速開發、減少手寫 CSS |

### 2. Built-in transitions: `transition:fade|fly|slide|scale|blur|draw`

Svelte 提供多個內建 transition 函式，在元素透過 `{#if}` 或 `{#each}` 掛載 / 卸載時觸發動畫：

```svelte
<script lang="ts">
  import { fade, fly, slide, scale, blur, draw } from 'svelte/transition';

  let visible = $state(true);
</script>

<button onclick={() => (visible = !visible)}>Toggle</button>

{#if visible}
  <!-- transition: 進出都套用同一個 transition -->
  <p transition:fade={{ duration: 300 }}>Fade in and out</p>
{/if}
```

使用 `in:` / `out:` 分別控制進場與離場 transition：

```svelte
{#if visible}
  <div
    in:fly={{ y: -20, duration: 400 }}
    out:fade={{ duration: 200 }}
  >
    Fly in, fade out
  </div>
{/if}
```

常用參數：

| 參數 | 型別 | 說明 |
|---|---|---|
| `duration` | `number` | 動畫持續時間（ms） |
| `delay` | `number` | 延遲開始時間（ms） |
| `easing` | `(t: number) => number` | 緩動函式（從 `svelte/easing` 匯入） |
| `x` / `y` | `number` | fly 專用，位移量（px） |
| `start` | `number` | scale 專用，起始縮放比例（0-1） |
| `amount` | `number` | blur 專用，模糊量（px） |

| 何時用內建 transition | 何時用 CSS animation |
|---|---|
| 元素的掛載 / 卸載動畫 | 持續播放的迴圈動畫（如 loading spinner） |
| 需要程式化控制 duration / delay | 純裝飾性動畫，不依賴元素的掛載狀態 |
| 需要 transition 事件（`introstart`、`outroend`） | 用 `@keyframes` 就能解決的簡單動畫 |
| 與 Svelte 的條件渲染整合 | 需要 CSS 硬體加速的複雜動畫 |

### 3. `animate:flip` in `{#each}` -- list animations

FLIP 是 **F**irst, **L**ast, **I**nvert, **P**lay 的縮寫，是一種高效能的列表動畫技術。Svelte 透過 `animate:flip` 指令讓 `{#each}` 中的項目在位置變動時平滑移動：

```svelte
<script lang="ts">
  import { flip } from 'svelte/animate';

  let items = $state([
    { id: 1, name: 'Apple' },
    { id: 2, name: 'Banana' },
    { id: 3, name: 'Cherry' },
  ]);

  function shuffle() {
    items = items.sort(() => Math.random() - 0.5);
  }
</script>

<button onclick={shuffle}>Shuffle</button>

<ul>
  {#each items as item (item.id)}
    <li animate:flip={{ duration: 300 }}>{item.name}</li>
  {/each}
</ul>
```

> **重要**：`animate:flip` **必須**在 keyed `{#each}` 中使用。沒有 key 的 `{#each}` 無法追蹤項目的身份，FLIP 動畫不會生效。

| 何時用 `animate:flip` | 何時不用 |
|---|---|
| 列表重排序（排序按鈕、拖拉排序） | 靜態列表，項目順序不會改變 |
| 項目的新增 / 移除導致其他項目位移 | 列表沒有唯一 key 可用 |
| 需要視覺連續性，讓使用者追蹤項目 | 效能敏感場景下有大量項目（>100） |

### 4. `use:action` directive -- custom element behavior

Action 是附加到 DOM 元素的函式，在元素掛載時執行，可回傳 `update` 和 `destroy` 方法處理參數更新與清理：

```ts
// src/lib/actions/clickOutside.ts
export function clickOutside(node: HTMLElement, callback: () => void) {
  function handleClick(event: MouseEvent) {
    if (!node.contains(event.target as Node)) {
      callback();
    }
  }

  document.addEventListener('click', handleClick, true);

  return {
    destroy() {
      document.removeEventListener('click', handleClick, true);
    }
  };
}
```

在元件中使用：

```svelte
<script lang="ts">
  import { clickOutside } from '$lib/actions/clickOutside';

  let open = $state(false);
</script>

{#if open}
  <div class="dropdown" use:clickOutside={() => (open = false)}>
    Dropdown content
  </div>
{/if}
```

Action 也可以接收參數並在參數變化時更新：

```ts
export function tooltip(node: HTMLElement, text: string) {
  let tooltipEl: HTMLDivElement;

  function show() {
    tooltipEl = document.createElement('div');
    tooltipEl.textContent = text;
    tooltipEl.className = 'tooltip';
    document.body.appendChild(tooltipEl);
  }

  function hide() {
    tooltipEl?.remove();
  }

  node.addEventListener('mouseenter', show);
  node.addEventListener('mouseleave', hide);

  return {
    update(newText: string) {
      text = newText;
    },
    destroy() {
      hide();
      node.removeEventListener('mouseenter', show);
      node.removeEventListener('mouseleave', hide);
    }
  };
}
```

| 何時用 `use:action` | 何時不用 |
|---|---|
| tooltip、click-outside、intersection observer | 可以用 `bind:this` + `$effect` 解決的簡單 DOM 操作 |
| focus trap、drag-and-drop | 邏輯屬於元件狀態管理而非 DOM 操作 |
| 需要在多個元件間複用的 DOM 行為 | 只需要一次性使用的 DOM 操作 |
| 整合第三方 DOM 函式庫 | 可以用 Svelte 內建功能（bind: / transition:）替代 |

### 5. Custom transition functions

當內建 transition 無法滿足需求時，可以撰寫自定義 transition function。Transition function 接收 `node` 和 `params`，回傳一個包含 `duration`、`delay`、`easing`、`css` 或 `tick` 的物件：

```ts
// 使用 css 回傳值（效能較好，由瀏覽器在獨立線程執行）
function typewriter(node: HTMLElement, { speed = 30 }: { speed?: number } = {}) {
  const text = node.textContent ?? '';
  const duration = text.length * speed;

  return {
    duration,
    tick(t: number) {
      const i = Math.trunc(text.length * t);
      node.textContent = text.slice(0, i);
    }
  };
}
```

使用自定義 transition：

```svelte
{#if visible}
  <p transition:typewriter={{ speed: 50 }}>Hello, world!</p>
{/if}
```

也可以使用 `css` 回傳函式，產生 CSS animation keyframes，效能更好（不阻塞主線程）：

```ts
function whoosh(node: HTMLElement, { duration = 400 }: { duration?: number } = {}) {
  const existingTransform = getComputedStyle(node).transform.replace('none', '');

  return {
    duration,
    css(t: number, u: number) {
      return `
        transform: ${existingTransform} scale(${t}) rotate(${u * 360}deg);
        opacity: ${t};
      `;
    }
  };
}
```

| 何時用 custom transition | 何時不用 |
|---|---|
| 內建 transition 無法實現的效果 | fade / fly / slide 等已夠用 |
| 需要精細控制每個 frame | 簡單的進出場動畫 |
| 需要基於元素內容的動畫（如 typewriter） | 可用 CSS `@keyframes` 解決 |
| 需要 JavaScript 計算的動畫邏輯 | 效能敏感且可用 CSS 硬體加速替代 |

### 6. `parseCss` — 編譯器 CSS AST 解析器

> **Svelte 5.48.0+** 新增。`svelte/compiler` 模組匯出 `parseCss` 函式，提供輕量的 CSS AST 解析能力。

`parseCss` 將 CSS 樣式表字串解析為抽象語法樹（AST），適合用於需要程式化分析或轉換 CSS 的工具鏈場景。這與 `parse` 函式解析 `.svelte` 元件的功能互補——`parse` 處理完整的 Svelte 元件，`parseCss` 則專門處理純 CSS。

#### 基本用法

```typescript
import { parseCss } from 'svelte/compiler';

const css = `
  .card {
    background: white;
    border-radius: 8px;
    padding: 1rem;
  }

  .card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const ast = parseCss(css);
// ast 的型別為 AST.CSS.StyleSheetFile
// 包含完整的 CSS 結構資訊：選擇器、屬性、值等
console.log(ast);
```

#### 函式簽名

```typescript
function parseCss(source: string): AST.CSS.StyleSheetFile;
```

- **`source`**：CSS 樣式表內容字串。
- **回傳值**：`AST.CSS.StyleSheetFile`，代表解析後的 CSS 抽象語法樹。

#### 搭配其他 compiler API

`parseCss` 是 `svelte/compiler` 模組中的工具之一，與其他匯出配合使用：

```typescript
import {
  VERSION,
  compile,       // 編譯 .svelte 元件
  compileModule,  // 編譯 .svelte.ts 模組
  parse,         // 解析 .svelte 元件為 AST
  parseCss,      // 解析 CSS 為 AST
  preprocess,    // 預處理 .svelte 元件
  walk,          // 走訪 AST 節點
} from 'svelte/compiler';
```

#### 實際應用場景

```typescript
import { parseCss, walk } from 'svelte/compiler';

// 場景：提取 CSS 中所有使用的 class 名稱
function extractClassNames(cssSource: string): string[] {
  const ast = parseCss(cssSource);
  const classNames: string[] = [];

  walk(ast, {
    enter(node) {
      // 走訪 AST 節點，尋找 class 選擇器
      if (node.type === 'ClassSelector') {
        classNames.push(node.name);
      }
    }
  });

  return classNames;
}

const classes = extractClassNames('.card { color: red; } .btn { color: blue; }');
console.log(classes); // ['card', 'btn']
```

| 何時用 `parseCss` | 何時不用 |
|---|---|
| 建立 CSS 分析工具（如 unused CSS 偵測） | 只是撰寫一般的 Svelte 元件樣式 |
| 開發 Svelte 相關的編譯器插件或 preprocessor | 使用 PostCSS、Tailwind 等已有 CSS 處理方案 |
| 需要程式化讀取 / 轉換 CSS 結構 | 不需要操作 CSS AST 的一般開發 |
| 建立自定義的 CSS 檢查或重構工具 | 只需要基礎的 CSS-in-JS 功能 |

> **注意**：`parseCss` 是 Svelte 編譯器內部使用的 CSS 解析器的公開匯出。它專注於 CSS 解析，不包含 Svelte 特有的 scoped style 處理邏輯。如果你需要分析完整的 `.svelte` 元件（含 `<style>` 區塊），應使用 `parse` 函式。

## Step-by-step

### Step 1：建立元件並示範 scoped styles 不會洩漏

建立 `src/lib/components/ScopedDemo.svelte`，證明 scoped style 只影響當前元件：

```svelte
<!-- ScopedDemo.svelte -->
<p>I am styled by ScopedDemo.</p>

<style>
  p {
    color: tomato;
    font-size: 1.25rem;
    border: 2px dashed tomato;
    padding: 0.5rem;
  }
</style>
```

```svelte
<!-- +page.svelte -->
<script lang="ts">
  import ScopedDemo from '$lib/components/ScopedDemo.svelte';
</script>

<p>I am NOT styled by ScopedDemo.</p>
<ScopedDemo />
```

頁面上的 `<p>` 不會受到 `ScopedDemo` 內部 `p` 樣式影響。檢查 DevTools 可以看到 Svelte 為 `ScopedDemo` 的 `p` 加上了類似 `.svelte-1abc123` 的 hash class。

### Step 2：使用 `:global()` 設定子元件根元素的樣式

有時需要從父元件調整子元件的外觀。使用 `:global()` 配合上下文選擇器：

```svelte
<!-- Parent.svelte -->
<script lang="ts">
  import ScopedDemo from '$lib/components/ScopedDemo.svelte';
</script>

<div class="wrapper">
  <ScopedDemo />
</div>

<style>
  .wrapper :global(p) {
    /* 僅影響 .wrapper 內部所有 <p>，包含子元件的 */
    margin-bottom: 1rem;
    font-style: italic;
  }
</style>
```

### Step 3：透過 CSS custom property 從父元件傳入主題色

利用 Svelte 的 `--css-var` 語法，在元件標籤上直接傳入 CSS 自訂屬性：

```svelte
<!-- ThemedCard.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  let { children }: { children: Snippet } = $props();
</script>

<div class="card">
  {@render children()}
</div>

<style>
  .card {
    background: var(--card-bg, #f8f8f8);
    color: var(--card-text, #333);
    border-radius: var(--card-radius, 8px);
    padding: 1.5rem;
    border: 1px solid #ddd;
  }
</style>
```

```svelte
<!-- 使用端 -->
<ThemedCard --card-bg="aliceblue" --card-text="darkblue" --card-radius="16px">
  <h2>Themed content</h2>
  <p>This card uses custom theme colors.</p>
</ThemedCard>

<ThemedCard --card-bg="#fef3c7" --card-text="#92400e">
  <h2>Warm theme</h2>
  <p>Different theme, same component.</p>
</ThemedCard>
```

### Step 4：為條件渲染的元素加入 `transition:fade`

```svelte
<script lang="ts">
  import { fade } from 'svelte/transition';

  let show = $state(true);
</script>

<button onclick={() => (show = !show)}>
  {show ? 'Hide' : 'Show'}
</button>

{#if show}
  <div transition:fade={{ duration: 300 }}>
    <p>This content fades in and out.</p>
  </div>
{/if}
```

> **注意**：`transition:` 只有在元素透過 `{#if}` 或 `{#each}` 掛載 / 卸載時才會觸發。對始終存在的元素使用 `transition:` 不會有任何效果。

### Step 5：使用 `in:fly` 和 `out:fade` 分別控制進出場

```svelte
<script lang="ts">
  import { fly, fade } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';

  let visible = $state(true);
</script>

<button onclick={() => (visible = !visible)}>Toggle</button>

{#if visible}
  <div
    in:fly={{ y: -30, duration: 500, easing: quintOut }}
    out:fade={{ duration: 200 }}
  >
    <p>I fly in from above and fade out.</p>
  </div>
{/if}
```

使用不同的 `in:` / `out:` 可以讓進場和離場有不同的視覺效果，例如通知從上方飛入、淡出消失。

### Step 6：在 keyed `{#each}` 中使用 `animate:flip` 建立可排序列表

```svelte
<script lang="ts">
  import { flip } from 'svelte/animate';
  import { quintOut } from 'svelte/easing';

  let items = $state([
    { id: 1, name: 'TypeScript' },
    { id: 2, name: 'Svelte' },
    { id: 3, name: 'Vite' },
    { id: 4, name: 'SvelteKit' },
  ]);

  function moveUp(index: number) {
    if (index === 0) return;
    const newItems = [...items];
    [newItems[index - 1], newItems[index]] = [newItems[index], newItems[index - 1]];
    items = newItems;
  }

  function moveDown(index: number) {
    if (index === items.length - 1) return;
    const newItems = [...items];
    [newItems[index], newItems[index + 1]] = [newItems[index + 1], newItems[index]];
    items = newItems;
  }
</script>

<ul>
  {#each items as item, i (item.id)}
    <li animate:flip={{ duration: 300, easing: quintOut }}>
      {item.name}
      <button onclick={() => moveUp(i)} disabled={i === 0}>Up</button>
      <button onclick={() => moveDown(i)} disabled={i === items.length - 1}>Down</button>
    </li>
  {/each}
</ul>
```

### Step 7：撰寫 `use:clickOutside` action 用於關閉下拉選單

建立 `src/lib/actions/clickOutside.ts`：

```ts
export function clickOutside(node: HTMLElement, callback: () => void) {
  function handleClick(event: MouseEvent) {
    if (!node.contains(event.target as Node)) {
      callback();
    }
  }

  document.addEventListener('click', handleClick, true);

  return {
    destroy() {
      document.removeEventListener('click', handleClick, true);
    }
  };
}
```

在元件中使用：

```svelte
<script lang="ts">
  import { clickOutside } from '$lib/actions/clickOutside';
  import { slide } from 'svelte/transition';

  let open = $state(false);
</script>

<div class="dropdown-wrapper">
  <button onclick={() => (open = !open)}>
    {open ? 'Close' : 'Open'} Menu
  </button>

  {#if open}
    <div
      class="dropdown"
      use:clickOutside={() => (open = false)}
      transition:slide={{ duration: 200 }}
    >
      <a href="/profile">Profile</a>
      <a href="/settings">Settings</a>
      <a href="/logout">Logout</a>
    </div>
  {/if}
</div>
```

### Step 8：撰寫自定義 typewriter transition function

建立 `src/lib/transitions/typewriter.ts`：

```ts
export function typewriter(
  node: HTMLElement,
  { speed = 30, delay = 0 }: { speed?: number; delay?: number } = {}
) {
  const valid = node.childNodes.length === 1 && node.childNodes[0].nodeType === Node.TEXT_NODE;

  if (!valid) {
    throw new Error('typewriter transition can only be used on elements with a single text node');
  }

  const text = node.textContent ?? '';
  const duration = text.length * speed;

  return {
    delay,
    duration,
    tick(t: number) {
      const i = Math.trunc(text.length * t);
      node.textContent = text.slice(0, i);
    }
  };
}
```

在元件中使用：

```svelte
<script lang="ts">
  import { typewriter } from '$lib/transitions/typewriter';

  let show = $state(false);
</script>

<button onclick={() => (show = !show)}>Toggle Typewriter</button>

{#if show}
  <p in:typewriter={{ speed: 40 }}>
    The quick brown fox jumps over the lazy dog.
  </p>
{/if}
```

## Hands-on Lab

### Foundation：通知 Toast 系統

建立 `src/lib/components/ToastContainer.svelte`，實作通知 toast 系統：

- 使用 `$state` 管理 toast 列表。
- 新增 toast 時以 `in:fly` 從右側飛入。
- 移除 toast 時以 `out:fade` 淡出。
- toast 在 3 秒後自動消失。
- 支援三種類型：`success`、`error`、`info`。

**驗收標準**：
- [ ] 點擊按鈕可新增不同類型的 toast。
- [ ] toast 從右方飛入，消失時淡出。
- [ ] 3 秒後自動移除。
- [ ] 手動點擊關閉按鈕可立即移除。

### Advanced：可排序列表

建立 `src/routes/sortable/+page.svelte`，實作可排序列表：

- 使用 keyed `{#each}` 渲染列表。
- 每個項目有 "Move Up" / "Move Down" 按鈕。
- 使用 `animate:flip` 讓移動有平滑動畫。
- 新增項目時以 `transition:slide` 滑入。
- 移除項目時以 `transition:fade` 淡出。

**驗收標準**：
- [ ] 點擊 Up / Down 按鈕時，項目平滑移動到新位置。
- [ ] 第一個項目的 Up 按鈕與最後一個項目的 Down 按鈕為 disabled。
- [ ] 新增項目時有滑入動畫。
- [ ] 移除項目時有淡出動畫。

### Challenge：`use:tooltip` Action

建立 `src/lib/actions/tooltip.ts`，實作可配置的 tooltip action：

- 滑鼠 hover 時顯示 tooltip，離開時隱藏。
- 支援配置：`text`（內容）、`position`（top / bottom / left / right）、`delay`（延遲顯示 ms）。
- tooltip 的定位使用 `getBoundingClientRect()` 計算。
- 支援 `update` 方法，當參數變化時更新 tooltip 內容。
- 確保 `destroy` 正確清理，無記憶體洩漏。

**驗收標準**：
- [ ] hover 時 tooltip 出現在正確位置。
- [ ] 可透過參數設定 tooltip 出現在元素的上、下、左、右。
- [ ] 設定 delay 時，hover 後延遲指定毫秒數才顯示。
- [ ] 動態改變 tooltip 文字時，顯示內容即時更新。
- [ ] 元素移除時 tooltip 被正確清理。

## Reference Solution

### Toast.svelte

```svelte
<!-- Toast.svelte -->
<script lang="ts">
  import { fly, fade } from 'svelte/transition';
  import { flip } from 'svelte/animate';

  interface Toast {
    id: number;
    message: string;
    type: 'success' | 'error' | 'info';
  }

  let toasts = $state<Toast[]>([]);
  let nextId = $state(0);

  function addToast(message: string, type: Toast['type'] = 'info') {
    const id = nextId++;
    toasts.push({ id, message, type });
    setTimeout(() => removeToast(id), 3000);
  }

  function removeToast(id: number) {
    toasts = toasts.filter(t => t.id !== id);
  }
</script>

<div class="toast-container">
  {#each toasts as toast (toast.id)}
    <div
      class="toast {toast.type}"
      in:fly={{ x: 300, duration: 300 }}
      out:fade={{ duration: 200 }}
      animate:flip={{ duration: 300 }}
    >
      {toast.message}
      <button onclick={() => removeToast(toast.id)}>×</button>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .toast {
    padding: 0.75rem 1rem;
    border-radius: 8px;
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    min-width: 250px;
  }
  .toast button {
    background: none;
    border: none;
    color: white;
    font-size: 1.25rem;
    cursor: pointer;
  }
  .success { background: #22c55e; }
  .error { background: #ef4444; }
  .info { background: #3b82f6; }
</style>
```

### clickOutside.ts

```ts
// src/lib/actions/clickOutside.ts
export function clickOutside(node: HTMLElement, callback: () => void) {
  function handleClick(event: MouseEvent) {
    if (!node.contains(event.target as Node)) {
      callback();
    }
  }

  document.addEventListener('click', handleClick, true);

  return {
    destroy() {
      document.removeEventListener('click', handleClick, true);
    }
  };
}
```

**重點解析**：

- `$state<Toast[]>` 管理 toast 列表，搭配 keyed `{#each}` 讓 Svelte 追蹤每個 toast 的身份。
- `in:fly={{ x: 300 }}` 讓 toast 從右側 300px 處飛入。
- `out:fade={{ duration: 200 }}` 讓 toast 淡出消失。
- `animate:flip={{ duration: 300 }}` 讓其他 toast 在某個 toast 被移除時平滑調整位置。
- `clickOutside` action 使用 capture phase（`true` 作為第三個參數）確保事件在冒泡前被攔截。
- `destroy()` 回傳函式負責移除事件監聽器，防止記憶體洩漏。

## Common Pitfalls

### 1. 忘記 Svelte 樣式是 scoped -- 動態注入的 HTML 不受影響

```svelte
<!-- 錯誤：innerHTML 注入的內容不會套用 scoped style -->
<script lang="ts">
  let html = $state('<p class="highlight">Dynamic content</p>');
</script>
{@html html}

<style>
  /* 這個樣式不會影響 {@html} 注入的 <p>，因為它沒有 Svelte 的 hash class */
  .highlight { color: red; }
</style>
```

```svelte
<!-- 修正：使用 :global() 針對動態內容設樣式 -->
<style>
  :global(.highlight) { color: red; }
  /* 或限定範圍 */
  .container :global(.highlight) { color: red; }
</style>
```

### 2. 在始終存在的元素上使用 `transition:`（不會觸發）

```svelte
<!-- 錯誤：div 始終存在，transition 永遠不會觸發 -->
<div transition:fade>Always here</div>

<!-- 正確：搭配 {#if} 使用，元素掛載/卸載時觸發 transition -->
{#if visible}
  <div transition:fade>Conditionally rendered</div>
{/if}
```

`transition:` 只在元素被 `{#if}` / `{#each}` 加入或移除 DOM 時觸發。如果元素始終存在，應改用 CSS transition 或 CSS animation。

### 3. 在沒有 key 的 `{#each}` 中使用 `animate:flip`

```svelte
<!-- 錯誤：沒有 key，animate:flip 無法追蹤項目，會報錯 -->
{#each items as item}
  <li animate:flip>{item.name}</li>
{/each}

<!-- 正確：提供唯一 key -->
{#each items as item (item.id)}
  <li animate:flip={{ duration: 300 }}>{item.name}</li>
{/each}
```

`animate:` 指令**必須**用在 keyed `{#each}` 區塊中。沒有 key，Svelte 無法知道哪個項目是哪個，自然無法計算 FLIP 動畫。

### 4. Action 忘記回傳 `destroy`，造成記憶體洩漏

```ts
// 錯誤：沒有 destroy，事件監聽器永遠不會被移除
export function trackMouse(node: HTMLElement) {
  function handleMove(e: MouseEvent) {
    console.log(e.clientX, e.clientY);
  }
  window.addEventListener('mousemove', handleMove);
  // 缺少 return { destroy() { ... } }
}

// 正確：回傳 destroy 清理函式
export function trackMouse(node: HTMLElement) {
  function handleMove(e: MouseEvent) {
    console.log(e.clientX, e.clientY);
  }
  window.addEventListener('mousemove', handleMove);
  return {
    destroy() {
      window.removeEventListener('mousemove', handleMove);
    }
  };
}
```

每當 action 註冊了外部事件監聽器、定時器或 MutationObserver，都**必須**在 `destroy` 中清理。

### 5. `:global()` 使用範圍過大，意外影響其他元件

```svelte
<!-- 危險：所有 <button> 都會被影響 -->
<style>
  :global(button) {
    background: red;
    color: white;
  }
</style>

<!-- 安全：限定在當前元件的容器內 -->
<style>
  .my-component :global(button) {
    background: red;
    color: white;
  }
</style>
```

使用 `:global()` 時，永遠搭配一個 scoped 的父選擇器來限制影響範圍，避免意外覆蓋其他元件的樣式。

## Checklist

- [ ] 能撰寫 scoped styles 並在需要時正確使用 `:global()`
- [ ] 能套用內建 transition（fade, fly, slide, scale）
- [ ] 能使用分離的 `in:` 和 `out:` transition
- [ ] 能在 keyed `{#each}` 區塊中使用 `animate:flip`
- [ ] 能撰寫自定義 `use:action` 並正確實作 `destroy` 清理
- [ ] 能透過 CSS custom properties 從父元件傳入主題樣式
- [ ] 了解 `parseCss` 的用途，能在工具鏈場景中使用 CSS AST 解析
- [ ] `npx svelte-check` 通過

## Further Reading

- [Scoped styles -- Svelte docs](https://svelte.dev/docs/svelte/scoped-styles)
- [:global -- Svelte docs](https://svelte.dev/docs/svelte/global-styles)
- [Custom properties -- Svelte docs](https://svelte.dev/docs/svelte/custom-properties)
- [transition: -- Svelte docs](https://svelte.dev/docs/svelte/transition)
- [in: and out: -- Svelte docs](https://svelte.dev/docs/svelte/in-and-out)
- [animate: -- Svelte docs](https://svelte.dev/docs/svelte/animate)
- [use: -- Svelte docs](https://svelte.dev/docs/svelte/use)
- [svelte/compiler -- API reference](https://svelte.dev/docs/svelte/svelte-compiler)
- [svelte/transition -- API reference](https://svelte.dev/docs/svelte/svelte-transition)
- [svelte/animate -- API reference](https://svelte.dev/docs/svelte/svelte-animate)
- [svelte/easing -- API reference](https://svelte.dev/docs/svelte/svelte-easing)
- [Svelte Tutorial: Transitions](https://svelte.dev/tutorial/svelte/transition)
- [Svelte Tutorial: Animations](https://svelte.dev/tutorial/svelte/animate)
- [Svelte Tutorial: Actions](https://svelte.dev/tutorial/svelte/actions)
