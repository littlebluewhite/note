---
title: "Accessibility Patterns / 無障礙設計模式"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "23"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [08_snippets_and_component_composition]
---
# Accessibility Patterns / 無障礙設計模式

## Goal

學會在 Svelte 5 中建立符合 WCAG 標準的無障礙元件，善用 Svelte 編譯器的 a11y 警告系統，並掌握 focus 管理與鍵盤導航的實作模式。

無障礙（Accessibility / a11y）不只是合規要求，更是良好使用者體驗的基礎。Svelte 編譯器內建了 a11y 靜態分析，能在開發階段就捕捉常見的無障礙問題。搭配正確的 ARIA 模式、focus 管理與鍵盤導航，你可以建立所有人都能使用的介面元件。

- 銜接上一章：Ch08 學會了元件組合模式（snippets、children、named snippets），現在要確保這些組合出來的元件是 accessible 的。
- 下一章預告：Ch24 將學習國際化（Internationalization），讓應用支援多語系。

## Prerequisites

- 已完成 Ch08（Snippets and Component Composition），理解 snippet、children、元件組合模式。
- 能建立含有互動行為（onclick、bind）的 Svelte 5 元件。
- `svelte5-lab` 專案可正常執行 `npm run dev`。
- 對 HTML 語意標籤（`<button>`、`<nav>`、`<main>`、`<label>`）有基本認識。

## Core Concepts

### 1. Svelte 內建 a11y 警告 — 編譯器靜態分析

Svelte 編譯器內建了一系列 a11y 檢查規則，會在編譯階段對模板中的無障礙問題發出警告。這些警告基於 WAI-ARIA 規範與 HTML 語意最佳實踐，幫助開發者在寫 code 時就捕捉常見錯誤。

主要的 a11y 警告規則：

| 規則 | 說明 |
|---|---|
| `a11y-click-events-have-key-events` | 有 `onclick` 的非互動元素必須也有 `onkeydown`/`onkeyup` |
| `a11y-missing-attribute` | `<img>` 缺少 `alt`、`<input>` 缺少 `id` 對應的 `<label>` |
| `a11y-no-noninteractive-element-interactions` | 非互動元素（`<div>`、`<span>`）不應有事件處理器 |
| `a11y-no-static-element-interactions` | 靜態元素加了互動事件但沒有 ARIA role |
| `a11y-role-has-required-aria-props` | 使用了 ARIA role 但缺少該 role 的必要屬性 |
| `a11y-label-has-associated-control` | `<label>` 沒有正確關聯到表單控制項 |

觸發警告的程式碼範例：

```svelte
<!-- BAD: 會觸發 a11y-click-events-have-key-events -->
<div onclick={() => doSomething()}>Click me</div>

<!-- BAD: 會觸發 a11y-missing-attribute -->
<img src="/photo.jpg" />

<!-- BAD: 會觸發 a11y-no-static-element-interactions -->
<span onclick={() => toggle()}>Toggle</span>
```

修正後的程式碼：

```svelte
<!-- GOOD: 使用語意化的 <button> 元素 -->
<button onclick={() => doSomething()}>Click me</button>

<!-- GOOD: 加上 alt 屬性 -->
<img src="/photo.jpg" alt="A scenic mountain view" />

<!-- GOOD: 使用 <button> 或加上 role + keyboard handler -->
<button onclick={() => toggle()}>Toggle</button>
```

在 `svelte.config.js` 中可以自訂 a11y 警告行為（但建議盡量修正而非忽略）：

```js
// svelte.config.js
/** @type {import('@sveltejs/kit').Config} */
const config = {
  compilerOptions: {
    // 不建議全域關閉，但可在特定情境下使用
  },
  onwarn: (warning, handler) => {
    // 忽略特定的 a11y 警告（僅在有正當理由時）
    if (warning.code === 'a11y-click-events-have-key-events') return;
    // 其餘警告照常處理
    handler(warning);
  },
};

export default config;
```

- **何時用**：永遠開啟。a11y 警告是 Svelte 最有價值的編譯器功能之一，應視為開發時期的強制檢查。
- **何時不用**：僅在極少數情況下可忽略特定警告，例如使用第三方套件產生的已知安全標記、或自訂元件內部已有完整的 a11y 處理但編譯器無法靜態分析到。

### 2. ARIA Patterns for Common Components — 常見元件的 ARIA 模式

正確的 ARIA 屬性讓輔助技術（如螢幕閱讀器）能理解元件的語意與狀態。以下是四種最常見的互動元件的 ARIA 模式，搭配 Svelte 5 runes 實作。

**Modal / Dialog**

```svelte
<!-- src/lib/components/A11yModal.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    open: boolean;
    onclose: () => void;
    title: string;
    children: Snippet;
  }

  let { open, onclose, title, children }: Props = $props();

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      onclose();
    }
  }
</script>

{#if open}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="overlay" onclick={onclose} onkeydown={handleKeydown}>
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      onclick={(e) => e.stopPropagation()}
    >
      <h2 id="modal-title">{title}</h2>
      {@render children()}
      <button onclick={onclose} aria-label="Close dialog">X</button>
    </div>
  </div>
{/if}
```

**Tabs**

```svelte
<script lang="ts">
  interface Tab {
    id: string;
    label: string;
  }

  let { tabs }: { tabs: Tab[] } = $props();
  let activeTab = $state(tabs[0]?.id ?? '');
</script>

<div role="tablist" aria-label="Content tabs">
  {#each tabs as tab (tab.id)}
    <button
      role="tab"
      id={`tab-${tab.id}`}
      aria-selected={activeTab === tab.id}
      aria-controls={`panel-${tab.id}`}
      tabindex={activeTab === tab.id ? 0 : -1}
      onclick={() => activeTab = tab.id}
    >
      {tab.label}
    </button>
  {/each}
</div>

{#each tabs as tab (tab.id)}
  <div
    role="tabpanel"
    id={`panel-${tab.id}`}
    aria-labelledby={`tab-${tab.id}`}
    hidden={activeTab !== tab.id}
  >
    <!-- panel content -->
  </div>
{/each}
```

**Dropdown / Menu**

```svelte
<script lang="ts">
  let expanded = $state(false);
</script>

<div class="dropdown">
  <button
    aria-expanded={expanded}
    aria-haspopup="menu"
    onclick={() => expanded = !expanded}
  >
    Options
  </button>

  {#if expanded}
    <ul role="menu">
      <li role="menuitem" tabindex={-1}>Edit</li>
      <li role="menuitem" tabindex={-1}>Duplicate</li>
      <li role="menuitem" tabindex={-1}>Delete</li>
    </ul>
  {/if}
</div>
```

**Toast / Alert**

```svelte
<script lang="ts">
  let messages = $state<string[]>([]);

  function addToast(msg: string) {
    messages = [...messages, msg];
    setTimeout(() => {
      messages = messages.slice(1);
    }, 3000);
  }
</script>

<div role="alert" aria-live="polite" aria-atomic="true">
  {#each messages as msg}
    <div class="toast">{msg}</div>
  {/each}
</div>
```

- **何時用**：所有客製化的互動元件都需要正確的 ARIA 屬性，特別是 modal、tabs、dropdown、tooltip、alert 等沒有原生 HTML 對應的模式。
- **何時不用**：當原生 HTML 元素已經提供完整的語意時（如 `<dialog>`、`<details>`、`<select>`），優先使用原生元素而非 ARIA 模擬。原生元素自帶正確的鍵盤行為與輔助技術支援。

### 3. Focus Management with `$effect` — 使用 `$effect` 管理焦點

焦點管理是無障礙的核心，確保鍵盤使用者能在正確的時機聚焦到正確的元素。Svelte 5 的 `$effect` rune 提供了在 DOM 更新後執行焦點操作的理想時機。

**Auto-focus on mount（掛載時自動聚焦）**

```svelte
<script lang="ts">
  let inputRef = $state<HTMLInputElement | null>(null);

  $effect(() => {
    // 元件掛載後自動聚焦到輸入框
    inputRef?.focus();
  });
</script>

<input bind:this={inputRef} type="text" placeholder="Auto-focused on mount" />
```

**Focus trap（焦點陷阱）**

Modal 開啟時必須將焦點限制在 modal 內部，避免鍵盤使用者 Tab 到背景元素。

```svelte
<script lang="ts">
  interface Props {
    open: boolean;
    onclose: () => void;
  }

  let { open, onclose }: Props = $props();

  let modalRef = $state<HTMLDivElement | null>(null);
  let previousActiveElement: Element | null = null;

  $effect(() => {
    if (open && modalRef) {
      // 記住開啟前的焦點位置
      previousActiveElement = document.activeElement;

      // 聚焦到 modal 內第一個可聚焦元素
      const firstFocusable = modalRef.querySelector<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      firstFocusable?.focus();

      return () => {
        // 關閉時恢復焦點
        if (previousActiveElement instanceof HTMLElement) {
          previousActiveElement.focus();
        }
      };
    }
  });

  function trapFocus(e: KeyboardEvent) {
    if (e.key !== 'Tab' || !modalRef) return;

    const focusableEls = modalRef.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstEl = focusableEls[0];
    const lastEl = focusableEls[focusableEls.length - 1];

    if (e.shiftKey && document.activeElement === firstEl) {
      e.preventDefault();
      lastEl?.focus();
    } else if (!e.shiftKey && document.activeElement === lastEl) {
      e.preventDefault();
      firstEl?.focus();
    }
  }
</script>
```

- **何時用**：Modal、dialog、drawer 等覆蓋式元件必須使用 focus trap。任何在路由切換或內容動態更新後需要引導使用者注意力的場景。
- **何時不用**：普通的頁面內容不應攔截焦點流。非覆蓋式的元件（如 inline alert、accordion）不需要 focus trap。

### 4. Keyboard Navigation — 鍵盤導航

鍵盤使用者需要能透過按鍵操作所有互動元件。核心模式包含方向鍵導航、Tab/Shift+Tab 切換、Escape 關閉、以及 roving tabindex 模式。

**Roving tabindex 模式**

在一組相關元素中（如 tab list、toolbar），只有一個元素在 Tab 順序中（`tabindex="0"`），其餘為 `tabindex="-1"`。使用方向鍵在群組內移動焦點。

```svelte
<script lang="ts">
  interface MenuItem {
    id: string;
    label: string;
    action: () => void;
  }

  let { items }: { items: MenuItem[] } = $props();
  let activeIndex = $state(0);
  let itemRefs = $state<HTMLButtonElement[]>([]);

  function handleKeydown(e: KeyboardEvent) {
    let newIndex = activeIndex;

    switch (e.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        e.preventDefault();
        newIndex = (activeIndex + 1) % items.length;
        break;
      case 'ArrowUp':
      case 'ArrowLeft':
        e.preventDefault();
        newIndex = (activeIndex - 1 + items.length) % items.length;
        break;
      case 'Home':
        e.preventDefault();
        newIndex = 0;
        break;
      case 'End':
        e.preventDefault();
        newIndex = items.length - 1;
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        items[activeIndex]?.action();
        return;
    }

    if (newIndex !== activeIndex) {
      activeIndex = newIndex;
      itemRefs[activeIndex]?.focus();
    }
  }

  function setRef(el: HTMLButtonElement, index: number) {
    itemRefs[index] = el;
  }
</script>

<div role="menu" onkeydown={handleKeydown}>
  {#each items as item, i (item.id)}
    <button
      role="menuitem"
      tabindex={i === activeIndex ? 0 : -1}
      bind:this={itemRefs[i]}
      onclick={() => item.action()}
    >
      {item.label}
    </button>
  {/each}
</div>
```

**Escape 關閉覆蓋層**

```svelte
<script lang="ts">
  let open = $state(false);

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && open) {
      open = false;
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />
```

- **何時用**：所有客製化的互動元件（menus、tabs、toolbars、tree views、listboxes）都需要實作鍵盤導航。任何替代原生控制項的元件都必須提供等效的鍵盤操作。
- **何時不用**：使用原生 HTML 元素（`<select>`、`<input type="radio">`）時，瀏覽器已內建完整的鍵盤行為，不需要重複實作。

### 5. Screen Reader Testing Workflow — 螢幕閱讀器測試流程

自動化測試可以捕捉技術層面的 a11y 問題，但完整的無障礙測試需要搭配螢幕閱讀器手動驗證。

**VoiceOver（macOS）基本指令**

| 操作 | 快捷鍵 |
|---|---|
| 開啟/關閉 VoiceOver | `Cmd + F5` |
| 下一個元素 | `VO + Right Arrow`（`VO = Ctrl + Option`） |
| 上一個元素 | `VO + Left Arrow` |
| 啟動/點擊 | `VO + Space` |
| 讀取目前元素 | `VO + A` |
| 網頁轉子（快速導航） | `VO + U` |

**axe-core 自動化測試設定**

```ts
// src/tests/a11y.test.ts
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import { axe, toHaveNoViolations } from 'jest-axe';
import MyComponent from '$lib/components/MyComponent.svelte';

expect.extend(toHaveNoViolations);

describe('MyComponent a11y', () => {
  it('should have no a11y violations', async () => {
    const { container } = render(MyComponent, {
      props: { title: 'Test' },
    });

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

```bash
# 安裝 axe-core 測試依賴
npm install -D jest-axe @types/jest-axe @testing-library/svelte
```

**螢幕閱讀器測試檢查清單**

1. 所有互動元素是否都能用 Tab 到達？
2. 按下 Enter/Space 是否能啟動互動元素？
3. Modal 開啟時，焦點是否正確移入？關閉後是否回到觸發按鈕？
4. 動態更新的內容（如 toast）是否被螢幕閱讀器朗讀？
5. 表單錯誤訊息是否被正確關聯到對應的欄位？

- **何時用**：每次建立新的互動元件或修改現有元件的結構時，都應執行自動化 a11y 測試。螢幕閱讀器手動測試建議在功能開發完成後、上線前執行。
- **何時不用**：純靜態內容頁面在自動化測試通過後，通常不需要額外的螢幕閱讀器測試。

## Step-by-step

### Step 1：修正常見的 a11y 警告

從一段包含多個 a11y 問題的程式碼開始，逐一修正 Svelte 編譯器的警告。

```svelte
<!-- 修正前：src/routes/ch23/step1-before/+page.svelte -->
<script lang="ts">
  let count = $state(0);
  let isOpen = $state(false);
</script>

<!-- BAD: a11y 問題滿滿 -->
<div onclick={() => count++}>Click to increment: {count}</div>
<img src="/logo.png" />
<span onclick={() => isOpen = !isOpen}>Toggle Menu</span>
```

```svelte
<!-- 修正後：src/routes/ch23/step1-after/+page.svelte -->
<script lang="ts">
  let count = $state(0);
  let isOpen = $state(false);
</script>

<!-- GOOD: 使用語意化元素 -->
<button onclick={() => count++}>Click to increment: {count}</button>
<img src="/logo.png" alt="Application logo" />
<button onclick={() => isOpen = !isOpen} aria-expanded={isOpen}>
  Toggle Menu
</button>
```

所有 Svelte a11y 警告的修正原則：優先使用語意化的 HTML 元素，而非為 `<div>` 和 `<span>` 加上 ARIA role。

### Step 2：建立 accessible Button 元件

建立一個處理 focus visible 和 disabled 狀態的按鈕元件。

```svelte
<!-- src/lib/components/A11yButton.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    children: Snippet;
    onclick?: () => void;
    disabled?: boolean;
    variant?: 'primary' | 'secondary' | 'danger';
    ariaLabel?: string;
  }

  let {
    children,
    onclick,
    disabled = false,
    variant = 'primary',
    ariaLabel,
  }: Props = $props();
</script>

<button
  class="btn btn-{variant}"
  {onclick}
  {disabled}
  aria-label={ariaLabel}
  aria-disabled={disabled}
>
  {@render children()}
</button>

<style>
  .btn {
    padding: 0.5rem 1rem;
    border: 2px solid transparent;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  .btn:focus-visible {
    outline: 3px solid #4A90D9;
    outline-offset: 2px;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-primary { background: #0066cc; color: white; }
  .btn-secondary { background: #6c757d; color: white; }
  .btn-danger { background: #dc3545; color: white; }
</style>
```

### Step 3：建立 accessible Modal 元件（含 focus trap）

實作完整的 focus trap，包含 ESC 關閉、焦點恢復。

```svelte
<!-- src/lib/components/A11yModal.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    open: boolean;
    onclose: () => void;
    title: string;
    children: Snippet;
  }

  let { open, onclose, title, children }: Props = $props();

  let modalRef = $state<HTMLDivElement | null>(null);
  let previousActiveElement: Element | null = null;

  const FOCUSABLE_SELECTOR =
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

  $effect(() => {
    if (open && modalRef) {
      previousActiveElement = document.activeElement;

      const firstFocusable = modalRef.querySelector<HTMLElement>(FOCUSABLE_SELECTOR);
      firstFocusable?.focus();

      return () => {
        if (previousActiveElement instanceof HTMLElement) {
          previousActiveElement.focus();
        }
      };
    }
  });

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      onclose();
      return;
    }

    if (e.key === 'Tab' && modalRef) {
      const focusableEls = modalRef.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR);
      const firstEl = focusableEls[0];
      const lastEl = focusableEls[focusableEls.length - 1];

      if (e.shiftKey && document.activeElement === firstEl) {
        e.preventDefault();
        lastEl?.focus();
      } else if (!e.shiftKey && document.activeElement === lastEl) {
        e.preventDefault();
        firstEl?.focus();
      }
    }
  }
</script>

{#if open}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="overlay" onclick={onclose} onkeydown={handleKeydown}>
    <div
      bind:this={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      onclick={(e) => e.stopPropagation()}
    >
      <header>
        <h2 id="modal-title">{title}</h2>
        <button onclick={onclose} aria-label="Close dialog">X</button>
      </header>
      <div class="modal-body">
        {@render children()}
      </div>
    </div>
  </div>
{/if}
```

### Step 4：實作鍵盤導航的 Tabs 元件

使用 roving tabindex 模式讓方向鍵在 tab 之間移動焦點。

```svelte
<!-- src/lib/components/A11yTabs.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Tab {
    id: string;
    label: string;
  }

  interface Props {
    tabs: Tab[];
    panel: Snippet<[string]>;
    label?: string;
  }

  let { tabs, panel, label = 'Tabs' }: Props = $props();

  let activeTab = $state(tabs[0]?.id ?? '');
  let tabRefs = $state<HTMLButtonElement[]>([]);

  function handleKeydown(e: KeyboardEvent) {
    const currentIndex = tabs.findIndex((t) => t.id === activeTab);
    let newIndex = currentIndex;

    switch (e.key) {
      case 'ArrowRight':
        e.preventDefault();
        newIndex = (currentIndex + 1) % tabs.length;
        break;
      case 'ArrowLeft':
        e.preventDefault();
        newIndex = (currentIndex - 1 + tabs.length) % tabs.length;
        break;
      case 'Home':
        e.preventDefault();
        newIndex = 0;
        break;
      case 'End':
        e.preventDefault();
        newIndex = tabs.length - 1;
        break;
      default:
        return;
    }

    activeTab = tabs[newIndex]!.id;
    tabRefs[newIndex]?.focus();
  }
</script>

<div role="tablist" aria-label={label} onkeydown={handleKeydown}>
  {#each tabs as tab, i (tab.id)}
    <button
      role="tab"
      id={`tab-${tab.id}`}
      aria-selected={activeTab === tab.id}
      aria-controls={`panel-${tab.id}`}
      tabindex={activeTab === tab.id ? 0 : -1}
      bind:this={tabRefs[i]}
      onclick={() => activeTab = tab.id}
    >
      {tab.label}
    </button>
  {/each}
</div>

{#each tabs as tab (tab.id)}
  <div
    role="tabpanel"
    id={`panel-${tab.id}`}
    aria-labelledby={`tab-${tab.id}`}
    hidden={activeTab !== tab.id}
    tabindex={0}
  >
    {@render panel(tab.id)}
  </div>
{/each}
```

### Step 5：建立 accessible Dropdown 元件（含 roving tabindex）

```svelte
<!-- src/lib/components/A11yDropdown.svelte -->
<script lang="ts">
  interface DropdownItem {
    id: string;
    label: string;
    onselect: () => void;
  }

  interface Props {
    label: string;
    items: DropdownItem[];
  }

  let { label, items }: Props = $props();

  let expanded = $state(false);
  let activeIndex = $state(0);
  let menuRef = $state<HTMLUListElement | null>(null);
  let itemRefs = $state<HTMLLIElement[]>([]);
  let triggerRef = $state<HTMLButtonElement | null>(null);

  function openMenu() {
    expanded = true;
    activeIndex = 0;
    // $effect 會在 DOM 更新後自動聚焦
  }

  function closeMenu() {
    expanded = false;
    triggerRef?.focus();
  }

  $effect(() => {
    if (expanded && itemRefs[activeIndex]) {
      itemRefs[activeIndex]?.focus();
    }
  });

  function handleMenuKeydown(e: KeyboardEvent) {
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
        items[activeIndex]?.onselect();
        closeMenu();
        break;
      case 'Escape':
        e.preventDefault();
        closeMenu();
        break;
      case 'Home':
        e.preventDefault();
        activeIndex = 0;
        break;
      case 'End':
        e.preventDefault();
        activeIndex = items.length - 1;
        break;
    }
  }

  function handleTriggerKeydown(e: KeyboardEvent) {
    if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      openMenu();
    }
  }
</script>

<div class="dropdown">
  <button
    bind:this={triggerRef}
    aria-expanded={expanded}
    aria-haspopup="menu"
    onclick={() => expanded ? closeMenu() : openMenu()}
    onkeydown={handleTriggerKeydown}
  >
    {label}
  </button>

  {#if expanded}
    <ul
      bind:this={menuRef}
      role="menu"
      onkeydown={handleMenuKeydown}
    >
      {#each items as item, i (item.id)}
        <li
          role="menuitem"
          tabindex={i === activeIndex ? 0 : -1}
          bind:this={itemRefs[i]}
          onclick={() => { item.onselect(); closeMenu(); }}
        >
          {item.label}
        </li>
      {/each}
    </ul>
  {/if}
</div>
```

### Step 6：加入 aria-live 區域的 Toast 通知

```svelte
<!-- src/lib/components/A11yToast.svelte -->
<script lang="ts">
  interface ToastMessage {
    id: number;
    text: string;
    type: 'info' | 'success' | 'error';
  }

  let messages = $state<ToastMessage[]>([]);
  let nextId = $state(0);

  export function addToast(text: string, type: ToastMessage['type'] = 'info') {
    const id = nextId++;
    messages = [...messages, { id, text, type }];

    setTimeout(() => {
      messages = messages.filter((m) => m.id !== id);
    }, 5000);
  }
</script>

<!-- aria-live="polite" 讓螢幕閱讀器在目前內容讀完後朗讀新增的通知 -->
<!-- aria-live="assertive" 會立刻打斷目前的朗讀，僅用於緊急錯誤 -->
<div
  aria-live="polite"
  aria-atomic="false"
  class="toast-container"
>
  {#each messages as msg (msg.id)}
    <div class="toast toast-{msg.type}" role="status">
      <span>{msg.text}</span>
      <button
        onclick={() => messages = messages.filter((m) => m.id !== msg.id)}
        aria-label="Dismiss notification"
      >
        X
      </button>
    </div>
  {/each}
</div>
```

使用方式：

```svelte
<!-- src/routes/ch23/toast-demo/+page.svelte -->
<script lang="ts">
  import A11yToast from '$lib/components/A11yToast.svelte';

  let toastComponent = $state<{ addToast: (text: string, type: string) => void } | null>(null);
</script>

<button onclick={() => toastComponent?.addToast('Item saved!', 'success')}>
  Save Item
</button>
<button onclick={() => toastComponent?.addToast('Something went wrong', 'error')}>
  Trigger Error
</button>

<A11yToast bind:this={toastComponent} />
```

### Step 7：設定 axe-core 搭配 Vitest 的自動化 a11y 測試

```ts
// src/tests/a11y/modal.test.ts
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import { axe, toHaveNoViolations } from 'jest-axe';
import A11yModal from '$lib/components/A11yModal.svelte';

expect.extend(toHaveNoViolations);

describe('A11yModal', () => {
  it('should have no a11y violations when open', async () => {
    const { container } = render(A11yModal, {
      props: {
        open: true,
        onclose: () => {},
        title: 'Test Modal',
      },
    });

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have dialog role and aria-modal', () => {
    const { container } = render(A11yModal, {
      props: {
        open: true,
        onclose: () => {},
        title: 'Test Modal',
      },
    });

    const dialog = container.querySelector('[role="dialog"]');
    expect(dialog).not.toBeNull();
    expect(dialog?.getAttribute('aria-modal')).toBe('true');
    expect(dialog?.getAttribute('aria-labelledby')).toBe('modal-title');
  });
});
```

```ts
// src/tests/a11y/tabs.test.ts
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import { axe, toHaveNoViolations } from 'jest-axe';
import A11yTabs from '$lib/components/A11yTabs.svelte';

expect.extend(toHaveNoViolations);

describe('A11yTabs', () => {
  const tabs = [
    { id: 'one', label: 'Tab One' },
    { id: 'two', label: 'Tab Two' },
  ];

  it('should have no a11y violations', async () => {
    const { container } = render(A11yTabs, {
      props: { tabs, panel: () => {} },
    });

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should use correct tablist/tab/tabpanel roles', () => {
    const { container } = render(A11yTabs, {
      props: { tabs, panel: () => {} },
    });

    expect(container.querySelector('[role="tablist"]')).not.toBeNull();
    expect(container.querySelectorAll('[role="tab"]').length).toBe(2);
    expect(container.querySelectorAll('[role="tabpanel"]').length).toBe(2);
  });
});
```

### Step 8：使用 VoiceOver 測試元件

以下是使用 VoiceOver 測試 Modal 元件的步驟流程：

1. 開啟終端機執行 `npm run dev`，在瀏覽器載入頁面。
2. 按下 `Cmd + F5` 開啟 VoiceOver。
3. 使用 `Tab` 移動到「Open Modal」按鈕，VoiceOver 應朗讀按鈕的文字。
4. 按下 `Enter` 開啟 Modal，確認 VoiceOver 朗讀 dialog 的 title。
5. 按 `Tab` 確認焦點在 Modal 內循環，不會跑到背景。
6. 按 `Escape` 關閉 Modal，確認焦點回到原本的「Open Modal」按鈕。
7. 測試 Tabs 元件：確認方向鍵可以在 tab 之間移動，VoiceOver 朗讀 `aria-selected` 狀態。
8. 測試 Toast：觸發通知後，確認 VoiceOver 自動朗讀新出現的訊息文字。

## Hands-on Lab

任務：運用 a11y 模式，建立符合 WCAG 標準的無障礙元件。

### Foundation 基礎層

建立一個 accessible 表單，包含正確的 label 關聯與錯誤提示：

- 使用 `<label for="...">` 正確關聯每個表單欄位。
- 必填欄位加上 `aria-required="true"`。
- 驗證失敗時使用 `aria-invalid="true"` 和 `aria-describedby` 關聯錯誤訊息。
- 表單送出按鈕在載入中時使用 `aria-busy="true"`。

**驗收條件：**
- [ ] 所有 `<label>` 正確關聯到對應的 `<input>`。
- [ ] Svelte 編譯器不產生任何 a11y 警告。
- [ ] 錯誤訊息透過 `aria-describedby` 關聯到欄位。
- [ ] `npx svelte-check` 通過，無型別錯誤。

### Advanced 進階層

建立一個包含 focus trap 的 Modal 元件：

- 使用 `role="dialog"`、`aria-modal="true"`、`aria-labelledby`。
- 開啟時自動聚焦到第一個互動元素。
- Tab/Shift+Tab 焦點在 Modal 內循環。
- ESC 鍵關閉 Modal。
- 關閉後焦點回到觸發按鈕。
- 使用 axe-core 測試驗證無違規。

**驗收條件：**
- [ ] Modal 開啟時焦點正確移入第一個可聚焦元素。
- [ ] Tab 鍵焦點在 Modal 內循環，不會跑到背景。
- [ ] ESC 鍵可關閉 Modal。
- [ ] 關閉後焦點回到觸發按鈕。
- [ ] axe-core 測試通過，無 a11y 違規。

### Challenge 挑戰層

建立一個完整的鍵盤導航選單，含子選單展開：

- 頂層選單使用方向鍵（左右）導航。
- Enter/Space 展開子選單。
- 子選單使用方向鍵（上下）導航。
- ESC 關閉子選單，焦點回到父項目。
- 正確使用 `role="menubar"`、`role="menu"`、`role="menuitem"`、`aria-expanded`、`aria-haspopup`。
- 支援巢狀子選單。

**驗收條件：**
- [ ] 左右方向鍵可在頂層選單項目間移動。
- [ ] Enter/Space 可展開子選單。
- [ ] 上下方向鍵可在子選單項目間移動。
- [ ] ESC 關閉子選單並恢復焦點到父項目。
- [ ] 所有 ARIA 屬性正確設定。
- [ ] VoiceOver 測試可正確朗讀選單結構。

## Reference Solution

完整的 accessible Modal 元件（含 focus trap、ESC 關閉、焦點恢復）：

```svelte
<!-- src/lib/components/A11yModal.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    open: boolean;
    onclose: () => void;
    title: string;
    children: Snippet;
    footer?: Snippet;
  }

  let { open, onclose, title, children, footer }: Props = $props();

  let modalRef = $state<HTMLDivElement | null>(null);
  let previousActiveElement: Element | null = null;

  const FOCUSABLE_SELECTOR =
    'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

  $effect(() => {
    if (open && modalRef) {
      previousActiveElement = document.activeElement;

      // 使用 requestAnimationFrame 確保 DOM 已更新
      requestAnimationFrame(() => {
        const firstFocusable = modalRef?.querySelector<HTMLElement>(FOCUSABLE_SELECTOR);
        firstFocusable?.focus();
      });

      return () => {
        if (previousActiveElement instanceof HTMLElement) {
          previousActiveElement.focus();
        }
      };
    }
  });

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      e.stopPropagation();
      onclose();
      return;
    }

    if (e.key === 'Tab' && modalRef) {
      const focusableEls = Array.from(
        modalRef.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)
      );

      if (focusableEls.length === 0) return;

      const firstEl = focusableEls[0]!;
      const lastEl = focusableEls[focusableEls.length - 1]!;

      if (e.shiftKey && document.activeElement === firstEl) {
        e.preventDefault();
        lastEl.focus();
      } else if (!e.shiftKey && document.activeElement === lastEl) {
        e.preventDefault();
        firstEl.focus();
      }
    }
  }
</script>

{#if open}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="modal-overlay" onclick={onclose} onkeydown={handleKeydown}>
    <div
      bind:this={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      class="modal-container"
      onclick={(e) => e.stopPropagation()}
    >
      <header class="modal-header">
        <h2 id="modal-title">{title}</h2>
        <button
          onclick={onclose}
          aria-label="Close dialog"
          class="modal-close"
        >
          X
        </button>
      </header>

      <div class="modal-body">
        {@render children()}
      </div>

      {#if footer}
        <footer class="modal-footer">
          {@render footer()}
        </footer>
      {/if}
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-container {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 1.25rem;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
  }

  .modal-close:focus-visible {
    outline: 3px solid #4A90D9;
    outline-offset: 2px;
  }

  .modal-footer {
    margin-top: 1rem;
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
  }
</style>
```

完整的 accessible Tabs 元件（含鍵盤導航）：

```svelte
<!-- src/lib/components/A11yTabs.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Tab {
    id: string;
    label: string;
  }

  interface Props {
    tabs: Tab[];
    panel: Snippet<[string]>;
    label?: string;
  }

  let { tabs, panel, label = 'Tabs' }: Props = $props();

  let activeTab = $state(tabs[0]?.id ?? '');
  let tabRefs = $state<HTMLButtonElement[]>([]);

  function activateTab(index: number) {
    const tab = tabs[index];
    if (tab) {
      activeTab = tab.id;
      tabRefs[index]?.focus();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    const currentIndex = tabs.findIndex((t) => t.id === activeTab);
    let newIndex = currentIndex;

    switch (e.key) {
      case 'ArrowRight':
        e.preventDefault();
        newIndex = (currentIndex + 1) % tabs.length;
        break;
      case 'ArrowLeft':
        e.preventDefault();
        newIndex = (currentIndex - 1 + tabs.length) % tabs.length;
        break;
      case 'Home':
        e.preventDefault();
        newIndex = 0;
        break;
      case 'End':
        e.preventDefault();
        newIndex = tabs.length - 1;
        break;
      default:
        return;
    }

    activateTab(newIndex);
  }
</script>

<div class="tabs-container">
  <div role="tablist" aria-label={label} onkeydown={handleKeydown}>
    {#each tabs as tab, i (tab.id)}
      <button
        role="tab"
        id={`tab-${tab.id}`}
        aria-selected={activeTab === tab.id}
        aria-controls={`panel-${tab.id}`}
        tabindex={activeTab === tab.id ? 0 : -1}
        bind:this={tabRefs[i]}
        onclick={() => activateTab(i)}
        class="tab-button"
        class:active={activeTab === tab.id}
      >
        {tab.label}
      </button>
    {/each}
  </div>

  {#each tabs as tab (tab.id)}
    <div
      role="tabpanel"
      id={`panel-${tab.id}`}
      aria-labelledby={`tab-${tab.id}`}
      hidden={activeTab !== tab.id}
      tabindex={0}
      class="tab-panel"
    >
      {@render panel(tab.id)}
    </div>
  {/each}
</div>

<style>
  .tabs-container {
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  [role="tablist"] {
    display: flex;
    border-bottom: 1px solid #ddd;
  }

  .tab-button {
    padding: 0.75rem 1rem;
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 1rem;
    border-bottom: 2px solid transparent;
  }

  .tab-button.active {
    border-bottom-color: #0066cc;
    color: #0066cc;
  }

  .tab-button:focus-visible {
    outline: 3px solid #4A90D9;
    outline-offset: -3px;
  }

  .tab-panel {
    padding: 1rem;
  }

  .tab-panel:focus-visible {
    outline: 3px solid #4A90D9;
    outline-offset: -3px;
  }
</style>
```

完整的 Toast 元件（含 aria-live）：

```svelte
<!-- src/lib/components/A11yToastManager.svelte -->
<script lang="ts" module>
  export interface ToastMessage {
    id: number;
    text: string;
    type: 'info' | 'success' | 'error';
  }
</script>

<script lang="ts">
  interface Props {
    position?: 'top-right' | 'bottom-right' | 'top-left' | 'bottom-left';
  }

  let { position = 'bottom-right' }: Props = $props();

  let messages = $state<ToastMessage[]>([]);
  let nextId = 0;

  export function addToast(text: string, type: ToastMessage['type'] = 'info') {
    const id = nextId++;
    messages = [...messages, { id, text, type }];

    setTimeout(() => {
      messages = messages.filter((m) => m.id !== id);
    }, 5000);
  }

  function dismiss(id: number) {
    messages = messages.filter((m) => m.id !== id);
  }
</script>

<div
  class="toast-container toast-{position}"
  aria-live="polite"
  aria-atomic="false"
>
  {#each messages as msg (msg.id)}
    <div class="toast toast-{msg.type}" role="status">
      <span class="toast-text">{msg.text}</span>
      <button
        onclick={() => dismiss(msg.id)}
        aria-label="Dismiss notification"
        class="toast-dismiss"
      >
        X
      </button>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    z-index: 2000;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
  }

  .toast-bottom-right { bottom: 0; right: 0; }
  .toast-top-right { top: 0; right: 0; }
  .toast-bottom-left { bottom: 0; left: 0; }
  .toast-top-left { top: 0; left: 0; }

  .toast {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    color: white;
    min-width: 250px;
  }

  .toast-info { background: #0066cc; }
  .toast-success { background: #28a745; }
  .toast-error { background: #dc3545; }

  .toast-text { flex: 1; }

  .toast-dismiss {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    font-size: 1rem;
    padding: 0.25rem;
  }

  .toast-dismiss:focus-visible {
    outline: 2px solid white;
    outline-offset: 2px;
  }
</style>
```

## Common Pitfalls

1. **在 `<div>` 上使用 `onclick` 而不加 role 與 keyboard handler**：`<div>` 是非互動元素，螢幕閱讀器不會將它視為可操作的。修正方式是改用 `<button>`，或加上 `role="button"` 與 `onkeydown`（但 `<button>` 永遠是更好的選擇）。

   ```svelte
   <!-- BAD -->
   <div onclick={() => handleClick()}>Click me</div>

   <!-- GOOD -->
   <button onclick={() => handleClick()}>Click me</button>
   ```

2. **圖片缺少 `alt` 屬性或使用不當的 alt 文字**：所有 `<img>` 都需要 `alt` 屬性。裝飾性圖片使用 `alt=""`（空字串），而非省略 `alt`。避免在 alt 中寫「圖片」或「image of」，螢幕閱讀器已經知道這是圖片。

   ```svelte
   <!-- BAD -->
   <img src="/photo.jpg" />
   <img src="/photo.jpg" alt="Image of a cat" />

   <!-- GOOD -->
   <img src="/photo.jpg" alt="Orange tabby cat sleeping on a cushion" />
   <img src="/decorative-line.svg" alt="" />
   ```

3. **使用 `tabindex` 大於 0 的值**：`tabindex="1"` 或更大的值會打亂自然的 Tab 順序，造成不可預測的焦點行為。應只使用 `tabindex="0"`（加入自然 Tab 順序）或 `tabindex="-1"`（程式化聚焦但不在 Tab 順序中）。

   ```svelte
   <!-- BAD -->
   <div tabindex="5">First?</div>
   <div tabindex="1">Or this?</div>

   <!-- GOOD: 依 DOM 順序使用 tabindex="0" -->
   <div tabindex="0">First in DOM order</div>
   <div tabindex="0">Second in DOM order</div>
   ```

4. **將 ARIA 屬性放在錯誤的元素上**：`aria-expanded` 應放在觸發按鈕上，而不是展開的內容上。`aria-labelledby` 應放在被標記的元素上，而不是標記本身。

   ```svelte
   <!-- BAD -->
   <button>Toggle</button>
   <div aria-expanded={expanded}>Content</div>

   <!-- GOOD -->
   <button aria-expanded={expanded} aria-controls="content">Toggle</button>
   <div id="content">{expanded ? 'Content' : ''}</div>
   ```

5. **透過設定忽略 a11y 警告而非修正問題**：在 `svelte.config.js` 的 `onwarn` 中直接忽略所有 a11y 警告是最糟糕的做法。如果確實需要忽略，應在模板中使用 `<!-- svelte-ignore a11y_specific_warning -->` 並附上註解說明理由，限定範圍而非全域忽略。

   ```js
   // BAD: 全域忽略所有 a11y 警告
   onwarn: (warning, handler) => {
     if (warning.code.startsWith('a11y-')) return;
     handler(warning);
   }

   // GOOD: 在模板中針對特定情境忽略，並說明理由
   ```

   ```svelte
   <!-- svelte-ignore a11y_no_static_element_interactions -->
   <!-- 理由：overlay 的 click 已由內部 dialog 的 keyboard handler 處理 -->
   <div class="overlay" onclick={onclose}>...</div>
   ```

## Checklist

- [ ] 能辨識並修正 Svelte 編譯器的 a11y 警告。
- [ ] 能為 Modal/Dialog 實作正確的 ARIA 屬性（`role="dialog"`、`aria-modal`、`aria-labelledby`）。
- [ ] 能使用 `$effect` 實作 focus trap，開啟時聚焦、關閉時恢復焦點。
- [ ] 能使用 roving tabindex 模式為 Tabs 和 Menu 實作鍵盤導航。
- [ ] 能使用 `aria-live` 區域讓螢幕閱讀器朗讀動態更新的通知。
- [ ] 能設定 axe-core 搭配 Vitest 執行自動化 a11y 測試。
- [ ] 能使用 VoiceOver 手動測試元件的螢幕閱讀器相容性。

## Further Reading

- [Svelte Docs — Accessibility warnings](https://svelte.dev/docs/svelte/compiler-warnings#a11y_warnings)
- [WAI-ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [WAI-ARIA Practices — Dialog Modal](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)
- [WAI-ARIA Practices — Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)
- [WAI-ARIA Practices — Menu](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/)
- [axe-core — GitHub](https://github.com/dequelabs/axe-core)
- [jest-axe — GitHub](https://github.com/nickcolley/jest-axe)
- [MDN — ARIA](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA)
- [WebAIM — Keyboard Accessibility](https://webaim.org/techniques/keyboard/)
