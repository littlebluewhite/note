---
title: "Stores, Context, and State Patterns / 狀態管理模式"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "07"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [06_effects_and_lifecycle]
---
# Stores, Context, and State Patterns / 狀態管理模式

## Goal

理解 Svelte 的多種狀態管理策略，學會根據場景選擇最合適的方案。

當應用規模增長，元件之間的狀態共享成為核心挑戰。本章涵蓋 Svelte stores、Context API 與 Svelte 5 的 module-level `$state` 三種模式，幫助你在不同場景下做出正確的架構決策。掌握這些模式後，你將能自信地設計從簡單 UI 到複雜多頁應用的狀態管理架構。

- **銜接上一章**：Ch06 學會了 `$effect` 副作用處理，現在要解決跨元件狀態共享的問題。
- **下一章預告**：Ch08 將學習 Svelte 5 的 snippets 與元件組合模式。

## Prerequisites

- 已完成第 06 章（Effects & Lifecycle）。
- 熟悉 `$state`、`$derived`、`$effect` 等 runes 的基本用法。
- 理解 Svelte 元件的生命週期與響應式更新機制。

## Core Concepts

### 1. Svelte Stores — `writable` / `readable` / `derived`

Svelte 內建的 store 機制來自 `svelte/store` 模組，提供 subscribe/unsubscribe 語義的響應式狀態容器。

- **`writable(initialValue)`**：可讀可寫，提供 `set()`、`update()`、`subscribe()` 方法。
- **`readable(initialValue, startFn)`**：唯讀，外部只能 subscribe，值由 `startFn` 內部控制。
- **`derived(stores, fn)`**：從一個或多個 store 衍生計算值，類似 `$derived` 但作用於 store 層級。

```ts
import { writable, readable, derived } from 'svelte/store';

// writable：可讀可寫
const count = writable(0);
count.set(10);
count.update(n => n + 1);

// readable：唯讀，值由內部控制
const time = readable(new Date(), (set) => {
  const interval = setInterval(() => set(new Date()), 1000);
  return () => clearInterval(interval); // cleanup
});

// derived：從其他 store 衍生
const doubled = derived(count, ($count) => $count * 2);
```

| 何時用 Svelte stores | 何時不用 |
|---|---|
| 跨元件共享狀態 | 元件內部狀態（直接用 `$state`） |
| 與第三方庫整合（非 Svelte 程式碼需要 subscribe） | 在 Svelte 5 中 runes 通常已足夠 |
| 需要 subscribe/unsubscribe 語義 | 僅在單一元件內使用的簡單值 |
| 維護既有 Svelte 4 codebase | 新專案且不需要與非 Svelte 程式碼互動 |

### 2. `$` Auto-Subscription Syntax

在 `.svelte` 檔案中，可以在 store 變數前加 `$` 前綴自動訂閱與取消訂閱：

```svelte
<script lang="ts">
  import { count } from '$lib/stores/counter';

  // $count 自動訂閱 count store
  // 元件銷毀時自動取消訂閱
</script>

<!-- 讀取：直接用 $count -->
<p>Count: {$count}</p>

<!-- 寫入：對 $count 賦值等同呼叫 count.set() -->
<button onclick={() => $count++}>+1</button>
```

| 何時用 `$` auto-subscription | 何時不用 |
|---|---|
| 在 `.svelte` 檔案中讀/寫 store | 在 `.ts` 檔案中（需手動 `subscribe`） |
| 需要自動 cleanup（避免 memory leak） | 需要精細控制訂閱時機 |
| 大多數元件內的 store 互動 | 在 `onMount` callback 中條件式訂閱 |

> **注意**：`$` 前綴是 Svelte 編譯器語法糖，僅在 `.svelte` 檔案中有效。在 `.ts` 或 `.js` 檔案中必須手動呼叫 `store.subscribe()` 並在適當時機取消訂閱。

### 3. `setContext` / `getContext` — Dependency Injection

Context API 提供元件樹層級的依賴注入機制，避免 prop drilling：

```svelte
<!-- Parent.svelte -->
<script lang="ts">
  import { setContext } from 'svelte';

  const theme = $state({ mode: 'light' as 'light' | 'dark' });
  setContext('theme', theme);
</script>

<!-- DeepChild.svelte（任意深度的子元件） -->
<script lang="ts">
  import { getContext } from 'svelte';

  const theme = getContext<{ mode: 'light' | 'dark' }>('theme');
</script>

<p>Current theme: {theme.mode}</p>
```

| 何時用 context | 何時不用 |
|---|---|
| 需要在元件樹中向下傳遞共享狀態（避免 prop drilling） | 全域狀態（用 module-level state 或 stores） |
| 同一頁面需要多個獨立實例（如多個 form 各有自己的狀態） | 只需傳一兩層的 props（直接傳就好） |
| library / UI kit 內部狀態傳遞 | 非元件樹結構的狀態共享 |
| 需要 per-tree isolation（不同子樹各自獨立） | 需要在 `.ts` 檔案中存取（context 只在元件中可用） |

> **重要限制**：`setContext` 必須在元件初始化的頂層 `<script>` 中同步呼叫，不能放在 `onMount` 或非同步函式中。

### 4. Decision Guide — 狀態模式選擇指南

根據場景選擇最合適的狀態管理方案：

| 模式 | 適用場景 | 共享範圍 | 多實例隔離 |
|---|---|---|---|
| `$state` in component | 元件內部狀態 | 單一元件 | 每個實例獨立 |
| `$state` in `.svelte.ts` module | 跨元件共享，匯入者共享同一實例 | 全域（singleton） | 否 |
| `writable` store | 需要 subscribe 語義、與非 Svelte 程式碼整合 | 全域（singleton） | 否 |
| `setContext` / `getContext` | 元件樹局部共享、多實例隔離 | 子樹 | 是 |

```
元件內部狀態？ ─── 是 ──→ $state in component
       │
       否
       │
需要 per-tree 隔離？ ─── 是 ──→ setContext / getContext
       │
       否
       │
需要在非 Svelte 程式碼中 subscribe？ ─── 是 ──→ writable store
       │
       否
       │
$state in .svelte.ts module（最簡潔的全域共享）
```

### 5. Class-based Reactive State — 類別式響應式狀態（Svelte 5 推薦模式）

在 Svelte 5 中，使用 class 搭配 `$state` 欄位是建立共享狀態管理器的推薦模式。相較於 store 的 subscribe/update 語義，class-based 模式提供完整的 TypeScript 型別推導、封裝（private fields）、方法自動補全，並且不需要 `$` 前綴語法。這個模式在很多場景下取代了 writable store 的角色。

#### TodoManager 類別範例

```ts
// src/lib/state/todo-manager.svelte.ts
export interface Todo {
  id: string;
  text: string;
  done: boolean;
  createdAt: Date;
}

export class TodoManager {
  todos = $state<Todo[]>([]);
  filter = $state<'all' | 'active' | 'completed'>('all');

  // $derived 欄位自動追蹤依賴
  filtered = $derived.by(() => {
    switch (this.filter) {
      case 'active': return this.todos.filter(t => !t.done);
      case 'completed': return this.todos.filter(t => t.done);
      default: return this.todos;
    }
  });

  remaining = $derived(this.todos.filter(t => !t.done).length);
  allDone = $derived(this.todos.length > 0 && this.remaining === 0);

  add(text: string) {
    const trimmed = text.trim();
    if (!trimmed) return;
    this.todos.push({
      id: crypto.randomUUID(),
      text: trimmed,
      done: false,
      createdAt: new Date()
    });
  }

  remove(id: string) {
    const index = this.todos.findIndex(t => t.id === id);
    if (index !== -1) this.todos.splice(index, 1);
  }

  toggle(id: string) {
    const todo = this.todos.find(t => t.id === id);
    if (todo) todo.done = !todo.done;
  }

  toggleAll() {
    const target = !this.allDone;
    for (const todo of this.todos) {
      todo.done = target;
    }
  }

  clearCompleted() {
    this.todos = this.todos.filter(t => !t.done);
  }
}
```

#### Context + Class 模式：依賴注入

將 class instance 透過 context 注入元件樹，實現 per-tree 隔離與型別安全：

```ts
// src/lib/context/todo.ts
import { getContext, setContext } from 'svelte';
import { TodoManager } from '$lib/state/todo-manager.svelte';

const TODO_KEY = Symbol('todo-context');

export function setTodoContext(manager?: TodoManager) {
  const instance = manager ?? new TodoManager();
  setContext(TODO_KEY, instance);
  return instance;
}

export function getTodoContext(): TodoManager {
  return getContext<TodoManager>(TODO_KEY);
}
```

```svelte
<!-- TodoProvider.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { setTodoContext } from '$lib/context/todo';

  interface Props { children: Snippet; }
  let { children }: Props = $props();

  setTodoContext();
</script>

{@render children()}
```

```svelte
<!-- TodoList.svelte — 任意深度的子元件 -->
<script lang="ts">
  import { getTodoContext } from '$lib/context/todo';
  const manager = getTodoContext();
</script>

<p>Remaining: {manager.remaining}</p>
<ul>
  {#each manager.filtered as todo (todo.id)}
    <li>
      <input type="checkbox" checked={todo.done} onchange={() => manager.toggle(todo.id)} />
      <span style:text-decoration={todo.done ? 'line-through' : 'none'}>{todo.text}</span>
      <button onclick={() => manager.remove(todo.id)}>x</button>
    </li>
  {/each}
</ul>
```

#### 狀態模式決策矩陣

| 模式 | 適用場景 | 共享範圍 | TypeScript 體驗 | 多實例隔離 |
|---|---|---|---|---|
| `$state` in component | 元件內部 UI 狀態 | 單一元件 | 完整推導 | 每個實例獨立 |
| Context + class（`$state` 欄位） | 元件樹共享、需要 per-tree 隔離 | 子樹 | 完整推導 + 方法自動補全 | 是 |
| Module-level class / `$state` | 全域 singleton 共享 | 全域 | 完整推導 + 方法自動補全 | 否 |
| `writable` store | 跨框架整合、需要 subscribe 語義 | 全域 | 需手動標註 `Readable<T>` | 否 |

- **何時用 class + `$state`**：需要多個相關狀態和方法的封裝（如 TodoManager、CartManager）；需要完整的 TypeScript 自動補全和型別安全；新專案的共享狀態管理。
- **何時不用 class + `$state`**：非常簡單的狀態（一個 boolean toggle）直接用 `$state` 即可；需要與非 Svelte 程式碼整合（如 vanilla JS library 訂閱狀態變化）時，store 的 `subscribe` 語義更通用。

## Step-by-step

### Step 1：建立 `writable` store 管理主題設定

建立 `src/lib/stores/theme.ts`：

```ts
// src/lib/stores/theme.ts
import { writable, derived } from 'svelte/store';

export type Theme = 'light' | 'dark';

export const theme = writable<Theme>('light');

export const themeClass = derived(theme, ($theme) =>
  $theme === 'dark' ? 'dark-mode' : 'light-mode'
);

export function toggleTheme() {
  theme.update(t => t === 'light' ? 'dark' : 'light');
}
```

重點：`writable` 接受泛型參數指定值的型別，`derived` 自動推斷衍生型別。

### Step 2：在元件中使用 `$` 前綴讀寫 store

建立 `src/lib/components/ThemeToggle.svelte`：

```svelte
<script lang="ts">
  import { theme, themeClass, toggleTheme } from '$lib/stores/theme';
</script>

<div class={$themeClass}>
  <p>Current theme: {$theme}</p>
  <button onclick={toggleTheme}>Toggle Theme</button>
</div>
```

重點：`$theme` 自動訂閱 `theme` store，元件銷毀時自動取消訂閱。`$themeClass` 同理，會隨 `theme` 變化自動更新。

### Step 3：建立 `derived` store 計算 CSS class

擴充 `src/lib/stores/theme.ts`，增加更多衍生狀態：

```ts
// 衍生：當前主題的 CSS 自訂屬性
export const themeVars = derived(theme, ($theme) => ({
  '--bg-color': $theme === 'dark' ? '#1a1a2e' : '#ffffff',
  '--text-color': $theme === 'dark' ? '#e0e0e0' : '#333333',
  '--accent-color': $theme === 'dark' ? '#e94560' : '#ff3e00',
}));

// 衍生：是否為深色模式（布林值）
export const isDarkMode = derived(theme, ($theme) => $theme === 'dark');
```

在元件中使用：

```svelte
<script lang="ts">
  import { themeVars, isDarkMode } from '$lib/stores/theme';
</script>

<div
  style="background: {$themeVars['--bg-color']}; color: {$themeVars['--text-color']}"
>
  <p>{$isDarkMode ? 'Dark mode is ON' : 'Light mode is ON'}</p>
</div>
```

### Step 4：使用 `setContext` / `getContext` 建立 form context

建立 `src/lib/components/FormProvider.svelte`：

```svelte
<script lang="ts">
  import { setContext } from 'svelte';
  import type { Snippet } from 'svelte';

  interface FormContext {
    values: Record<string, string>;
    errors: Record<string, string>;
    setValue(key: string, value: string): void;
    setError(key: string, error: string): void;
    clearError(key: string): void;
    reset(): void;
  }

  let values = $state<Record<string, string>>({});
  let errors = $state<Record<string, string>>({});

  const ctx: FormContext = {
    get values() { return values; },
    get errors() { return errors; },
    setValue(key, value) { values[key] = value; },
    setError(key, error) { errors[key] = error; },
    clearError(key) { delete errors[key]; },
    reset() {
      values = {};
      errors = {};
    }
  };

  setContext('form', ctx);

  interface Props {
    children: Snippet;
  }

  let { children }: Props = $props();
</script>

{@render children()}
```

建立 `src/lib/components/FormField.svelte`：

```svelte
<script lang="ts">
  import { getContext } from 'svelte';

  interface FormContext {
    values: Record<string, string>;
    errors: Record<string, string>;
    setValue(key: string, value: string): void;
    clearError(key: string): void;
  }

  interface Props {
    name: string;
    label: string;
  }

  let { name, label }: Props = $props();
  const form = getContext<FormContext>('form');
</script>

<div class="form-field">
  <label for={name}>{label}</label>
  <input
    id={name}
    type="text"
    value={form.values[name] ?? ''}
    oninput={(e) => {
      form.setValue(name, e.currentTarget.value);
      form.clearError(name);
    }}
  />
  {#if form.errors[name]}
    <span class="error">{form.errors[name]}</span>
  {/if}
</div>

<style>
  .form-field {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-bottom: 1rem;
  }

  .error {
    color: #dc2626;
    font-size: 0.8rem;
  }
</style>
```

重點：`FormProvider` 透過 `setContext` 注入表單狀態，`FormField` 透過 `getContext` 取得。即使 `FormField` 被嵌套在多層元件之下，仍然能正確取得最近的 `FormProvider` context。

### Step 5：在 `.svelte.ts` module 中建立共享狀態

建立 `src/lib/theme.svelte.ts`：

```ts
// src/lib/theme.svelte.ts
// Svelte 5 runes alternative — module-level shared state

export type Theme = 'light' | 'dark';

export function createTheme(initial: Theme = 'light') {
  let current = $state(initial);
  let cssClass = $derived(current === 'dark' ? 'dark-mode' : 'light-mode');
  let isDark = $derived(current === 'dark');

  return {
    get current() { return current; },
    get cssClass() { return cssClass; },
    get isDark() { return isDark; },
    toggle() { current = current === 'light' ? 'dark' : 'light'; },
    set(value: Theme) { current = value; }
  };
}

// Singleton instance — 所有匯入者共享同一個
export const theme = createTheme();
```

在元件中使用：

```svelte
<script lang="ts">
  import { theme } from '$lib/theme.svelte';
</script>

<div class={theme.cssClass}>
  <p>Theme: {theme.current}</p>
  <button onclick={() => theme.toggle()}>Toggle</button>
</div>
```

重點：`.svelte.ts` 副檔名讓 Svelte 編譯器處理 runes 語法。匯出的 `theme` 是 module-level singleton，所有匯入此模組的元件共享同一份狀態。

### Step 6：比較四種模式傳遞 theme

以下對比不同方案傳遞 theme 給 `Header` 和 `Footer`：

**方案 A：Props（直接傳遞）**

```svelte
<!-- +page.svelte -->
<script lang="ts">
  let currentTheme = $state<'light' | 'dark'>('light');
</script>

<Header theme={currentTheme} />
<main>
  <Sidebar theme={currentTheme} />
</main>
<Footer theme={currentTheme} />
```

缺點：每個需要 theme 的元件都必須接收 prop，層級深時造成 prop drilling。

**方案 B：Context（樹狀範圍共享）**

```svelte
<!-- ThemeProvider.svelte -->
<script lang="ts">
  import { setContext } from 'svelte';
  let theme = $state<'light' | 'dark'>('light');
  setContext('theme', { get current() { return theme; } });
</script>

{@render children()}
```

優點：子樹內任何元件可直接取得，無需逐層傳遞。多個 `ThemeProvider` 可提供不同主題。

**方案 C：Store（全域訂閱）**

```ts
// theme-store.ts
import { writable } from 'svelte/store';
export const theme = writable<'light' | 'dark'>('light');
```

優點：任何 `.svelte` 或 `.ts` 檔案都能存取。缺點：全域 singleton，無法 per-tree 隔離。

**方案 D：Module-level `$state`（Svelte 5 推薦）**

```ts
// theme.svelte.ts
let current = $state<'light' | 'dark'>('light');
export const theme = {
  get current() { return current; },
  toggle() { current = current === 'light' ? 'dark' : 'light'; }
};
```

優點：最簡潔，不需要 subscribe/unsubscribe，型別安全。缺點：同 store 為全域 singleton。

### Step 7：實作通知系統（writable store + custom methods）

建立 `src/lib/stores/notifications.ts`：

```ts
// src/lib/stores/notifications.ts
import { writable } from 'svelte/store';

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
}

function createNotificationStore() {
  const { subscribe, update } = writable<Notification[]>([]);

  function add(type: Notification['type'], message: string) {
    const id = crypto.randomUUID();
    update(items => [...items, { id, type, message }]);

    // 5 秒後自動移除
    setTimeout(() => remove(id), 5000);

    return id;
  }

  function remove(id: string) {
    update(items => items.filter(item => item.id !== id));
  }

  function clear() {
    update(() => []);
  }

  return {
    subscribe,
    add,
    remove,
    clear,
    info: (msg: string) => add('info', msg),
    success: (msg: string) => add('success', msg),
    warning: (msg: string) => add('warning', msg),
    error: (msg: string) => add('error', msg),
  };
}

export const notifications = createNotificationStore();
```

在元件中使用：

```svelte
<!-- NotificationList.svelte -->
<script lang="ts">
  import { notifications } from '$lib/stores/notifications';
</script>

<div class="notification-container">
  {#each $notifications as notif (notif.id)}
    <div class="notification notification-{notif.type}">
      <span>{notif.message}</span>
      <button onclick={() => notifications.remove(notif.id)}>x</button>
    </div>
  {/each}
</div>

<!-- 任何元件都能發送通知 -->
<!-- <button onclick={() => notifications.success('Saved!')}>Save</button> -->
```

重點：透過 `createNotificationStore()` 封裝 writable store，對外暴露語義化的 `info` / `success` / `warning` / `error` 方法，同時保留標準的 `subscribe` 介面（讓 `$` 前綴語法可用）。

### Step 8：為所有模式加上 TypeScript 型別

為 context 建立型別安全的工具函式：

```ts
// src/lib/context/form.ts
import { getContext, setContext } from 'svelte';

// 使用 Symbol 作為 context key 避免字串衝突
const FORM_KEY = Symbol('form-context');

export interface FormContext {
  values: Record<string, string>;
  errors: Record<string, string>;
  setValue(key: string, value: string): void;
  setError(key: string, error: string): void;
  clearError(key: string): void;
  reset(): void;
}

export function setFormContext(ctx: FormContext) {
  setContext(FORM_KEY, ctx);
}

export function getFormContext(): FormContext {
  return getContext<FormContext>(FORM_KEY);
}
```

為 store 加上完整型別：

```ts
// src/lib/stores/theme.ts（完整型別版本）
import { writable, derived, type Readable } from 'svelte/store';

export type Theme = 'light' | 'dark';

export const theme = writable<Theme>('light');

export const themeClass: Readable<string> = derived(
  theme,
  ($theme) => ($theme === 'dark' ? 'dark-mode' : 'light-mode')
);

export const isDarkMode: Readable<boolean> = derived(
  theme,
  ($theme) => $theme === 'dark'
);

export function toggleTheme(): void {
  theme.update(t => (t === 'light' ? 'dark' : 'light'));
}
```

重點：使用 `Symbol` 作為 context key 可以避免字串 key 衝突的問題。為 `derived` store 明確標註 `Readable<T>` 型別，讓 IDE 自動補全更精確。

### Step 9：建立 Class-based 狀態管理器並透過 Context 注入

建立 `src/lib/state/counter-manager.svelte.ts`：

```ts
// src/lib/state/counter-manager.svelte.ts
export class CounterManager {
  count = $state(0);
  doubled = $derived(this.count * 2);
  history = $state<number[]>([0]);

  constructor(initial = 0) {
    this.count = initial;
    this.history = [initial];
  }

  increment() {
    this.count++;
    this.history.push(this.count);
  }

  decrement() {
    this.count--;
    this.history.push(this.count);
  }

  reset() {
    this.count = 0;
    this.history = [0];
  }
}
```

建立 context 工具函式 `src/lib/context/counter.ts`：

```ts
// src/lib/context/counter.ts
import { getContext, setContext } from 'svelte';
import { CounterManager } from '$lib/state/counter-manager.svelte';

const COUNTER_KEY = Symbol('counter-context');

export function setCounterContext(initial = 0) {
  const manager = new CounterManager(initial);
  setContext(COUNTER_KEY, manager);
  return manager;
}

export function getCounterContext(): CounterManager {
  return getContext<CounterManager>(COUNTER_KEY);
}
```

在頁面中使用：

```svelte
<!-- src/routes/class-state-demo/+page.svelte -->
<script lang="ts">
  import { setCounterContext } from '$lib/context/counter';
  import CounterDisplay from '$lib/components/CounterDisplay.svelte';
  import CounterControls from '$lib/components/CounterControls.svelte';

  const manager = setCounterContext(0);
</script>

<h1>Class-based State Demo</h1>
<CounterDisplay />
<CounterControls />
<p>History: {manager.history.join(' → ')}</p>
```

重點：`CounterManager` class 的 `$state` 和 `$derived` 欄位在 `.svelte.ts` 檔案中完全正常運作。子元件透過 `getCounterContext()` 取得同一個 manager 實例，無需 prop drilling 也無需 store 訂閱。

## Hands-on Lab

### Foundation：Theme Switcher（主題切換器）

**任務：建立使用 writable store 的主題切換系統。**

1. 建立 `src/lib/stores/theme.ts`，匯出 `writable<'light' | 'dark'>` store 與 `toggleTheme` 函式。
2. 建立 `src/lib/components/Header.svelte`，顯示目前主題名稱與切換按鈕。
3. 建立 `src/lib/components/Footer.svelte`，根據 `$theme` 動態切換文字顏色。
4. 在 `+page.svelte` 中同時使用 Header 和 Footer，確認兩者共享同一份 theme 狀態。

**驗收條件：**
- 點擊 Header 的按鈕，Header 和 Footer 同時反映主題變更。
- 使用 `derived` store 產生 CSS class。
- TypeScript 型別完整，無 `any`。

### Advanced：Form Context（表單上下文管理）

**任務：建立使用 context 的表單狀態管理系統。**

1. 建立 `FormProvider.svelte`，使用 `setContext` 注入表單狀態（values、errors、setValue、setError、clearError、reset）。
2. 建立 `FormField.svelte`，使用 `getContext` 讀取表單狀態，渲染 label + input + error message。
3. 建立 `FormActions.svelte`，提供 Submit 和 Reset 按鈕，Submit 時驗證必填欄位。
4. 在 `+page.svelte` 中組合：一個 `FormProvider` 包裹兩個 `FormField`（name、email）和一個 `FormActions`。

**驗收條件：**
- FormField 元件不需要接收 form state 作為 prop（透過 context 取得）。
- Submit 時若欄位為空，顯示錯誤訊息。
- Reset 清除所有值與錯誤。
- 可在同一頁放兩個獨立的 `FormProvider`，各自管理自己的狀態。

### Challenge：Module-level `$state` 重構

**任務：將 Foundation 的 store-based theme 重構為 `.svelte.ts` module-level `$state`。**

1. 建立 `src/lib/theme.svelte.ts`，使用 `createTheme()` 工廠函式搭配 `$state` 與 `$derived`。
2. 匯出 singleton `theme` 實例。
3. 修改 Header 和 Footer 元件，改為從 `.svelte.ts` 匯入。
4. 比較兩種方案的程式碼行數、可讀性、TypeScript 體驗。

**驗收條件：**
- 功能與 Foundation 完全相同（主題切換、Header/Footer 同步更新）。
- 不再使用 `svelte/store` 的任何匯入。
- 不再使用 `$` 前綴語法（因為不是 store）。
- 撰寫簡短比較筆記：列出 store vs module `$state` 的優缺點。
- `npx svelte-check` 通過。

### Challenge+：Class-based 狀態管理器重構

**任務：將 Notification store 重構為 class-based 模式。**

1. 建立 `src/lib/state/notification-manager.svelte.ts`，以 class 封裝通知邏輯。
2. class 中使用 `$state<Notification[]>([])` 作為通知列表、`$derived` 計算未讀數量。
3. 提供 `add()`、`remove()`、`clear()`、`info()`、`success()`、`warning()`、`error()` 方法。
4. 建立 context 工具函式，讓子元件可透過 `getNotificationContext()` 取得 manager。
5. 在頁面中比較 store 版本和 class 版本的程式碼差異。

**驗收條件：**
- 功能與 store 版本完全相同（新增、移除、自動消失）。
- 使用 class + `$state`，不使用 `svelte/store`。
- TypeScript 型別完整，方法有自動補全。
- 可透過 context 在不同子元件中使用同一個 manager 實例。
- `npx svelte-check` 通過。

## Reference Solution

### theme.ts — Store 版本

```ts
// src/lib/stores/theme.ts
import { writable, derived } from 'svelte/store';

export type Theme = 'light' | 'dark';

export const theme = writable<Theme>('light');

export const themeClass = derived(theme, ($theme) =>
  $theme === 'dark' ? 'dark-mode' : 'light-mode'
);

export function toggleTheme() {
  theme.update(t => t === 'light' ? 'dark' : 'light');
}
```

### theme.svelte.ts — Runes 版本

```ts
// src/lib/theme.svelte.ts
export type Theme = 'light' | 'dark';

export function createTheme(initial: Theme = 'light') {
  let current = $state(initial);
  let cssClass = $derived(current === 'dark' ? 'dark-mode' : 'light-mode');

  return {
    get current() { return current; },
    get cssClass() { return cssClass; },
    toggle() { current = current === 'light' ? 'dark' : 'light'; }
  };
}

export const theme = createTheme();
```

### FormProvider.svelte — Context 版本

```svelte
<!-- src/lib/components/FormProvider.svelte -->
<script lang="ts">
  import { setContext } from 'svelte';
  import type { Snippet } from 'svelte';

  export interface FormContext {
    values: Record<string, string>;
    errors: Record<string, string>;
    setValue(key: string, value: string): void;
    setError(key: string, error: string): void;
    clearError(key: string): void;
    reset(): void;
  }

  let values = $state<Record<string, string>>({});
  let errors = $state<Record<string, string>>({});

  const ctx: FormContext = {
    get values() { return values; },
    get errors() { return errors; },
    setValue(key, value) { values[key] = value; },
    setError(key, error) { errors[key] = error; },
    clearError(key) { delete errors[key]; },
    reset() {
      values = {};
      errors = {};
    }
  };

  setContext('form', ctx);

  interface Props {
    children: Snippet;
  }

  let { children }: Props = $props();
</script>

{@render children()}
```

### FormField.svelte — Context Consumer

```svelte
<!-- src/lib/components/FormField.svelte -->
<script lang="ts">
  import { getContext } from 'svelte';
  import type { FormContext } from './FormProvider.svelte';

  interface Props {
    name: string;
    label: string;
  }

  let { name, label }: Props = $props();
  const form = getContext<FormContext>('form');
</script>

<div class="form-field">
  <label for={name}>{label}</label>
  <input
    id={name}
    type="text"
    value={form.values[name] ?? ''}
    oninput={(e) => {
      form.setValue(name, e.currentTarget.value);
      form.clearError(name);
    }}
  />
  {#if form.errors[name]}
    <span class="error">{form.errors[name]}</span>
  {/if}
</div>

<style>
  .form-field {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-bottom: 1rem;
  }

  label {
    font-weight: 600;
    font-size: 0.875rem;
  }

  input {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
  }

  .error {
    color: #dc2626;
    font-size: 0.8rem;
  }
</style>
```

### notifications.ts — Custom Store

```ts
// src/lib/stores/notifications.ts
import { writable } from 'svelte/store';

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
}

function createNotificationStore() {
  const { subscribe, update } = writable<Notification[]>([]);

  function add(type: Notification['type'], message: string) {
    const id = crypto.randomUUID();
    update(items => [...items, { id, type, message }]);
    setTimeout(() => remove(id), 5000);
    return id;
  }

  function remove(id: string) {
    update(items => items.filter(item => item.id !== id));
  }

  function clear() {
    update(() => []);
  }

  return {
    subscribe,
    add,
    remove,
    clear,
    info: (msg: string) => add('info', msg),
    success: (msg: string) => add('success', msg),
    warning: (msg: string) => add('warning', msg),
    error: (msg: string) => add('error', msg),
  };
}

export const notifications = createNotificationStore();
```

### 在 +page.svelte 中組合使用

```svelte
<script lang="ts">
  import { theme, themeClass, toggleTheme } from '$lib/stores/theme';
  import { notifications } from '$lib/stores/notifications';
  import FormProvider from '$lib/components/FormProvider.svelte';
  import FormField from '$lib/components/FormField.svelte';
</script>

<div class={$themeClass}>
  <header>
    <h1>State Patterns Demo</h1>
    <p>Theme: {$theme}</p>
    <button onclick={toggleTheme}>Toggle Theme</button>
    <button onclick={() => notifications.success('Theme toggled!')}>
      Notify
    </button>
  </header>

  <section>
    <h2>Form with Context</h2>
    <FormProvider>
      <FormField name="username" label="Username" />
      <FormField name="email" label="Email" />
    </FormProvider>
  </section>

  <section>
    <h2>Independent Form</h2>
    <FormProvider>
      <FormField name="search" label="Search" />
    </FormProvider>
  </section>

  <div class="notification-container">
    {#each $notifications as notif (notif.id)}
      <div class="notification notification-{notif.type}">
        <span>{notif.message}</span>
        <button onclick={() => notifications.remove(notif.id)}>x</button>
      </div>
    {/each}
  </div>
</div>
```

## Common Pitfalls

### 1. 元件內部狀態使用 store（過度設計）

在 Svelte 5 中，元件內部狀態直接用 `$state` 即可，不需要為每個值建立 store。

```ts
// 錯誤：為元件內部的 input 值建立 store
import { writable } from 'svelte/store';
const inputValue = writable('');

// 正確：直接用 $state
let inputValue = $state('');
```

store 適用於跨元件共享或與非 Svelte 程式碼整合的場景。對於單一元件內的狀態，`$state` 更簡潔且效能更好。

### 2. 在 `.ts` 檔案中忘記取消訂閱 store

在 `.svelte` 檔案中，`$` 前綴會自動處理 subscribe/unsubscribe。但在純 `.ts` 檔案中必須手動管理。

```ts
// 錯誤：忘記 unsubscribe — 造成 memory leak
import { theme } from '$lib/stores/theme';
theme.subscribe(value => {
  console.log('theme changed:', value);
});

// 正確：保存 unsubscribe 函式並在適當時機呼叫
const unsubscribe = theme.subscribe(value => {
  console.log('theme changed:', value);
});
// 在不再需要時呼叫
unsubscribe();
```

### 3. 在 `onMount` 中設定 context（時機錯誤）

`setContext` 必須在元件初始化的頂層同步程式碼中呼叫，不能放在 `onMount`、`$effect` 或任何非同步函式中。

```svelte
<script lang="ts">
  import { setContext, onMount } from 'svelte';

  // 錯誤：在 onMount 中呼叫 — 子元件取不到 context
  onMount(() => {
    setContext('data', { value: 42 }); // 太晚了！
  });

  // 正確：在頂層同步呼叫
  setContext('data', { value: 42 });
</script>
```

### 4. Module-level `$state` 卻期待 per-instance 隔離

`.svelte.ts` 中的 module-level state 是 singleton，所有匯入者共享同一份。若需要每個元件樹各自獨立的狀態，應使用 context。

```ts
// theme.svelte.ts — singleton，全域共享
export const theme = createTheme(); // 所有匯入者看到同一個 theme

// 如果需要 per-tree 隔離，改用 context：
// ParentA 設定 setContext('theme', createTheme('light'))
// ParentB 設定 setContext('theme', createTheme('dark'))
// 各自子樹中的元件會拿到不同的 theme 實例
```

### 5. 混用 Svelte 4 store 模式與 Svelte 5 runes 而不理解取捨

兩者可以共存，但要清楚各自的適用場景：

```svelte
<script lang="ts">
  // 混用是合法的，但要有明確理由
  import { count } from '$lib/stores/counter';   // Svelte store
  import { theme } from '$lib/theme.svelte';      // Runes module state

  // $count 使用 $ 前綴（store 語法）
  // theme.current 直接存取（runes 語法，不需要 $ 前綴）
</script>

<p>Count: {$count}</p>
<p>Theme: {theme.current}</p>
```

經驗法則：新程式碼優先使用 runes（`.svelte.ts` module state），既有 store 程式碼不需急著遷移，但避免在同一功能模組中混用兩種模式增加認知負擔。

## Checklist

- [ ] 能建立並使用 `writable` / `readable` / `derived` stores
- [ ] 能在 `.svelte` 檔案中使用 `$` 前綴自動訂閱 store
- [ ] 能使用 `setContext` / `getContext` 實現元件樹範圍的狀態共享
- [ ] 能在 `.svelte.ts` 模組中建立 module-level 共享狀態
- [ ] 能解釋何時該用 `$state` / store / context / module state，並說明理由
- [ ] 能使用 class + `$state` 建立型別安全的共享狀態管理器
- [ ] `npx svelte-check` 通過，無型別錯誤

## Further Reading

- [Svelte Stores](https://svelte.dev/docs/svelte/svelte-store) -- `writable`、`readable`、`derived` API 參考。
- [Context API — setContext / getContext](https://svelte.dev/docs/svelte/svelte#setContext) -- 官方 context API 說明。
- [$state — Svelte 5 Runes](https://svelte.dev/docs/svelte/$state) -- Svelte 5 響應式狀態核心。
- [$derived — Svelte 5 Runes](https://svelte.dev/docs/svelte/$derived) -- 衍生狀態 rune。
- [.svelte.js and .svelte.ts files](https://svelte.dev/docs/svelte/svelte-js-files) -- 在非元件檔案中使用 runes。
- [Svelte Tutorial — Stores](https://svelte.dev/tutorial/svelte/writable-stores) -- 官方互動教學。
