---
title: "Design System Patterns and Token Architecture / 設計系統模式與令牌架構"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "22"
level: advanced
stack: Tailwind CSS 4.1.x
prerequisites: [21_tailwind_with_svelte_component_patterns]
---

# Design System Patterns and Token Architecture / 設計系統模式與令牌架構

## Goal

在前兩章（[[20_tailwind_with_react_component_patterns]] 和 [[21_tailwind_with_svelte_component_patterns]]）中，我們分別在 React 和 Svelte 中建立了 Button、Card、Dialog 等元件。但這些元件還只是「個別元件」，尚未形成一個有系統、有層次的「設計系統」。本章將把視野提升到設計系統的層級，探討如何使用 Tailwind CSS v4 的 `@theme` 建立一套完整的令牌（token）架構，從原始令牌（primitive tokens）到語義令牌（semantic tokens）再到元件令牌（component tokens），形成三層式的設計令牌體系。

設計系統的核心價值在於「一致性」和「可維護性」。當專案規模增長到數十個頁面、上百個元件時，沒有統一的令牌架構會導致色彩、間距、字型的不一致蔓延。本章將教你如何運用 Tailwind v4 的 CSS 變數系統建立令牌層次、何時該將工具類抽取為元件、如何用 CSS layers 組織設計系統，以及如何記錄和分享設計令牌配置。在下一章 [[23_migration_from_tailwind_v3_to_v4]] 中，我們將運用本章建立的設計系統知識，來指導從 v3 遷移到 v4 的策略。

## Prerequisites

- 已完成第 20-21 章，理解 React 和 Svelte 的元件模式。
- 熟悉 CSS 自訂屬性（custom properties / CSS variables）。
- 理解 `@theme` 指令的基礎用法（第 16 章）。
- 具備基礎的設計概念（色彩、排版、間距）。
- 理解 CSS cascade layers 的運作方式（第 19 章）。

## Core Concepts

### 1. Token Hierarchy / 令牌層次

設計令牌（design tokens）是設計系統的基礎，它們以三層架構組織：原始令牌（primitive）、語義令牌（semantic）、元件令牌（component）。

**何時建立三層令牌架構：**
- 專案有多個主題（品牌色、深色模式、客戶白標）。
- 團隊有 3 人以上的前端開發者，需要統一設計語言。
- 產品會持續迭代，設計需要可擴展性。

**何時用簡化的兩層架構（primitive + semantic）：**
- 小型專案或個人專案，只需要一套主題。
- 快速原型階段，不需要過度架構。
- 使用 DaisyUI 或 shadcn/ui 等已有令牌系統的元件庫。

### 2. Component Extraction Patterns / 元件抽取模式

決定何時將 Tailwind 工具類組合抽取為元件，是設計系統中最重要的判斷之一。

**何時抽取為元件：**
- 同一組工具類在 3 處以上重複使用。
- 元件有明確的語義（Button、Card 而非 BlueRoundedBox）。
- 需要統一修改時只改一處。
- 元件有變體（variant）需求。

**何時保持工具類直接使用：**
- 布局相關的樣式（flex、grid、padding、margin）。
- 只使用一次的頁面特定樣式。
- 工具類組合 < 5 個且無重複使用需求。
- 直接使用工具類更能清楚表達意圖。

### 3. Utility Balance / 工具類平衡

在設計系統中找到「工具類」和「元件」的平衡點。

**適合用工具類直接處理的場景：**
- 布局（`flex`, `grid`, `gap-*`, `justify-*`）。
- 間距（`p-*`, `m-*`, `space-*`）。
- 響應式調整（`md:flex-row`, `lg:grid-cols-3`）。
- 一次性的頁面級樣式。

**適合用元件封裝的場景：**
- 互動元素（Button、Input、Select、Dialog）。
- 資訊展示（Card、Badge、Alert、Toast）。
- 有業務語義的 UI 區塊（PricingCard、UserAvatar、NotificationBell）。
- 有多個變體或狀態的 UI 元素。

### 4. Design System as CSS Layers / 設計系統的 CSS Layer 架構

利用 CSS `@layer` 組織設計系統的不同層次。

**何時使用自訂 layer 架構：**
- 設計系統需要作為獨立套件分發。
- 需要確保設計系統樣式和應用程式樣式的優先權正確。
- 多個團隊共用設計系統但有各自的客製需求。

**何時使用 Tailwind 預設 layer 即可：**
- 單一專案、單一團隊使用。
- 不需要分發設計系統套件。
- Tailwind 的 base/components/utilities 三層已足夠。

## Step-by-step

### 步驟 1：定義 Primitive Tokens（原始令牌）

原始令牌是最基礎的設計值，不帶任何語義，類似於色票、刻度：

```css
/* src/tokens/primitives.css */

/* 原始色彩令牌：使用 oklch 色彩空間（v4 預設） */
@theme {
  /* Blue 色階 */
  --color-blue-50: oklch(0.97 0.01 250);
  --color-blue-100: oklch(0.93 0.03 250);
  --color-blue-200: oklch(0.87 0.06 250);
  --color-blue-300: oklch(0.78 0.10 250);
  --color-blue-400: oklch(0.70 0.14 250);
  --color-blue-500: oklch(0.62 0.19 250);
  --color-blue-600: oklch(0.55 0.20 250);
  --color-blue-700: oklch(0.47 0.19 250);
  --color-blue-800: oklch(0.39 0.16 250);
  --color-blue-900: oklch(0.33 0.12 250);
  --color-blue-950: oklch(0.25 0.09 250);

  /* Neutral 色階 */
  --color-neutral-50: oklch(0.985 0 0);
  --color-neutral-100: oklch(0.965 0 0);
  --color-neutral-200: oklch(0.925 0 0);
  --color-neutral-300: oklch(0.87 0 0);
  --color-neutral-400: oklch(0.708 0 0);
  --color-neutral-500: oklch(0.556 0 0);
  --color-neutral-600: oklch(0.439 0 0);
  --color-neutral-700: oklch(0.371 0 0);
  --color-neutral-800: oklch(0.269 0 0);
  --color-neutral-900: oklch(0.205 0 0);
  --color-neutral-950: oklch(0.145 0 0);

  /* Green 色階 */
  --color-green-50: oklch(0.97 0.02 145);
  --color-green-500: oklch(0.60 0.18 145);
  --color-green-600: oklch(0.52 0.17 145);
  --color-green-700: oklch(0.44 0.15 145);

  /* Red 色階 */
  --color-red-50: oklch(0.97 0.02 25);
  --color-red-500: oklch(0.58 0.22 25);
  --color-red-600: oklch(0.50 0.20 25);
  --color-red-700: oklch(0.42 0.18 25);

  /* Yellow/Amber 色階 */
  --color-amber-50: oklch(0.98 0.02 85);
  --color-amber-500: oklch(0.77 0.16 75);
  --color-amber-600: oklch(0.70 0.16 60);

  /* 原始間距令牌 */
  --spacing-0: 0;
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-3: 0.75rem;
  --spacing-4: 1rem;
  --spacing-5: 1.25rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;
  --spacing-10: 2.5rem;
  --spacing-12: 3rem;
  --spacing-16: 4rem;
  --spacing-20: 5rem;
  --spacing-24: 6rem;

  /* 原始字型令牌 */
  --font-sans: "Inter", system-ui, -apple-system, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  /* 原始圓角令牌 */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-full: 9999px;
}
```

驗證：使用 `bg-blue-500`, `p-4`, `rounded-lg` 等工具類確認令牌正確生效。

### 步驟 2：定義 Semantic Tokens（語義令牌）

語義令牌引用原始令牌，賦予它們意義和上下文：

```css
/* src/tokens/semantic.css */

/* 語義色彩：透過 CSS 變數引用原始令牌 */
:root {
  /* 品牌色 */
  --ds-color-brand: var(--color-blue-600);
  --ds-color-brand-hover: var(--color-blue-700);
  --ds-color-brand-active: var(--color-blue-800);
  --ds-color-brand-subtle: var(--color-blue-50);

  /* 文字色 */
  --ds-color-text-primary: var(--color-neutral-900);
  --ds-color-text-secondary: var(--color-neutral-600);
  --ds-color-text-muted: var(--color-neutral-400);
  --ds-color-text-inverse: var(--color-neutral-50);
  --ds-color-text-brand: var(--color-blue-600);

  /* 背景色 */
  --ds-color-bg-primary: #ffffff;
  --ds-color-bg-secondary: var(--color-neutral-50);
  --ds-color-bg-tertiary: var(--color-neutral-100);
  --ds-color-bg-inverse: var(--color-neutral-900);

  /* 邊框色 */
  --ds-color-border-default: var(--color-neutral-200);
  --ds-color-border-strong: var(--color-neutral-300);
  --ds-color-border-focus: var(--color-blue-500);

  /* 狀態色 */
  --ds-color-success: var(--color-green-600);
  --ds-color-success-subtle: var(--color-green-50);
  --ds-color-warning: var(--color-amber-600);
  --ds-color-warning-subtle: var(--color-amber-50);
  --ds-color-error: var(--color-red-600);
  --ds-color-error-subtle: var(--color-red-50);

  /* 語義間距 */
  --ds-space-xs: var(--spacing-1);
  --ds-space-sm: var(--spacing-2);
  --ds-space-md: var(--spacing-4);
  --ds-space-lg: var(--spacing-6);
  --ds-space-xl: var(--spacing-8);
  --ds-space-2xl: var(--spacing-12);
  --ds-space-section: var(--spacing-16);
  --ds-space-page: var(--spacing-24);

  /* 語義圓角 */
  --ds-radius-button: var(--radius-lg);
  --ds-radius-card: var(--radius-xl);
  --ds-radius-dialog: var(--radius-2xl);
  --ds-radius-input: var(--radius-lg);
  --ds-radius-badge: var(--radius-full);

  /* 語義陰影 */
  --ds-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --ds-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --ds-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  --ds-shadow-overlay: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

/* 深色模式語義令牌 */
.dark {
  --ds-color-brand: var(--color-blue-400);
  --ds-color-brand-hover: var(--color-blue-300);
  --ds-color-brand-active: var(--color-blue-200);
  --ds-color-brand-subtle: var(--color-blue-950);

  --ds-color-text-primary: var(--color-neutral-50);
  --ds-color-text-secondary: var(--color-neutral-300);
  --ds-color-text-muted: var(--color-neutral-500);
  --ds-color-text-inverse: var(--color-neutral-900);
  --ds-color-text-brand: var(--color-blue-400);

  --ds-color-bg-primary: var(--color-neutral-950);
  --ds-color-bg-secondary: var(--color-neutral-900);
  --ds-color-bg-tertiary: var(--color-neutral-800);
  --ds-color-bg-inverse: var(--color-neutral-50);

  --ds-color-border-default: var(--color-neutral-800);
  --ds-color-border-strong: var(--color-neutral-700);
  --ds-color-border-focus: var(--color-blue-400);

  --ds-color-success: var(--color-green-500);
  --ds-color-success-subtle: oklch(0.2 0.05 145);
  --ds-color-warning: var(--color-amber-500);
  --ds-color-warning-subtle: oklch(0.2 0.05 85);
  --ds-color-error: var(--color-red-500);
  --ds-color-error-subtle: oklch(0.2 0.05 25);

  --ds-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --ds-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
  --ds-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  --ds-shadow-overlay: 0 20px 25px -5px rgba(0, 0, 0, 0.6);
}
```

驗證：切換 `<html class="dark">` 時，所有語義令牌正確切換色彩。

### 步驟 3：定義 Component Tokens（元件令牌）

元件令牌是最具體的層級，為特定元件定義專屬的設計值：

```css
/* src/tokens/components.css */

:root {
  /* Button 元件令牌 */
  --ds-button-height-sm: 2rem;
  --ds-button-height-md: 2.5rem;
  --ds-button-height-lg: 3rem;
  --ds-button-padding-sm: var(--ds-space-sm) var(--ds-space-sm);
  --ds-button-padding-md: var(--ds-space-sm) var(--ds-space-md);
  --ds-button-padding-lg: var(--ds-space-md) var(--ds-space-lg);
  --ds-button-radius: var(--ds-radius-button);
  --ds-button-font-weight: 500;
  --ds-button-transition: color 150ms, background-color 150ms, border-color 150ms;

  /* Card 元件令牌 */
  --ds-card-padding: var(--ds-space-lg);
  --ds-card-radius: var(--ds-radius-card);
  --ds-card-bg: var(--ds-color-bg-primary);
  --ds-card-border: var(--ds-color-border-default);
  --ds-card-shadow: var(--ds-shadow-sm);

  /* Input 元件令牌 */
  --ds-input-height: 2.5rem;
  --ds-input-padding: var(--ds-space-sm) var(--ds-space-sm);
  --ds-input-radius: var(--ds-radius-input);
  --ds-input-border: var(--ds-color-border-default);
  --ds-input-border-focus: var(--ds-color-border-focus);
  --ds-input-bg: var(--ds-color-bg-primary);

  /* Dialog 元件令牌 */
  --ds-dialog-radius: var(--ds-radius-dialog);
  --ds-dialog-padding: var(--ds-space-lg);
  --ds-dialog-shadow: var(--ds-shadow-overlay);
  --ds-dialog-max-width: 28rem;

  /* Badge 元件令牌 */
  --ds-badge-padding: var(--ds-space-xs) var(--ds-space-sm);
  --ds-badge-radius: var(--ds-radius-badge);
  --ds-badge-font-size: 0.75rem;
}
```

驗證：元件令牌引用鏈條完整：component -> semantic -> primitive。

### 步驟 4：整合令牌到 Tailwind @theme

將三層令牌整合到 Tailwind 的 `@theme` 系統中，讓工具類可以使用：

```css
/* src/app.css */
@import "tailwindcss";

/* 引入三層令牌 */
@import "./tokens/primitives.css";
@import "./tokens/semantic.css";
@import "./tokens/components.css";

/* 將語義令牌註冊為 Tailwind 可用的工具類 */
@theme {
  /* 清除預設色彩，使用自訂色彩系統 */
  --color-*: initial;

  /* 註冊語義色為可用的色彩工具類 */
  --color-brand: var(--ds-color-brand);
  --color-brand-hover: var(--ds-color-brand-hover);
  --color-brand-subtle: var(--ds-color-brand-subtle);

  --color-surface: var(--ds-color-bg-primary);
  --color-surface-alt: var(--ds-color-bg-secondary);
  --color-surface-strong: var(--ds-color-bg-tertiary);

  --color-fg: var(--ds-color-text-primary);
  --color-fg-muted: var(--ds-color-text-secondary);
  --color-fg-subtle: var(--ds-color-text-muted);
  --color-fg-inverse: var(--ds-color-text-inverse);

  --color-border: var(--ds-color-border-default);
  --color-border-strong: var(--ds-color-border-strong);

  --color-success: var(--ds-color-success);
  --color-success-subtle: var(--ds-color-success-subtle);
  --color-warning: var(--ds-color-warning);
  --color-warning-subtle: var(--ds-color-warning-subtle);
  --color-error: var(--ds-color-error);
  --color-error-subtle: var(--ds-color-error-subtle);

  --color-white: #ffffff;
  --color-black: #000000;
}
```

使用方式：

```html
<!-- 使用語義色彩工具類 -->
<div class="bg-surface text-fg border border-border rounded-xl p-6">
  <h2 class="text-xl font-semibold">語義色彩</h2>
  <p class="text-fg-muted">使用語義令牌而非硬編碼色值。</p>
  <span class="text-brand font-medium">品牌色文字</span>
</div>

<!-- 狀態色 -->
<div class="bg-success-subtle text-success border border-success/20 rounded-lg p-4">
  操作成功！
</div>
<div class="bg-error-subtle text-error border border-error/20 rounded-lg p-4">
  發生錯誤。
</div>
```

驗證：使用 `bg-brand`, `text-fg`, `border-border` 等語義工具類正確渲染。深色模式下自動切換。

### 步驟 5：建立 Typography Scale（排版級距）

```css
/* 在 src/tokens/primitives.css 中加入 */
@theme {
  /* 排版級距 */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;

  /* 行高 */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;

  /* 字重 */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;
}
```

```css
/* 在 src/tokens/semantic.css 中加入 */
:root {
  /* 語義排版令牌 */
  --ds-text-heading-1: var(--text-4xl);
  --ds-text-heading-2: var(--text-3xl);
  --ds-text-heading-3: var(--text-2xl);
  --ds-text-heading-4: var(--text-xl);
  --ds-text-body: var(--text-base);
  --ds-text-body-sm: var(--text-sm);
  --ds-text-caption: var(--text-xs);

  --ds-leading-heading: var(--leading-tight);
  --ds-leading-body: var(--leading-normal);
}
```

建立排版元件（HTML + 任何框架皆可使用）：

```html
<!-- 排版預覽 -->
<div class="space-y-6 p-8">
  <h1 class="text-4xl font-extrabold leading-tight text-fg">Heading 1</h1>
  <h2 class="text-3xl font-bold leading-tight text-fg">Heading 2</h2>
  <h3 class="text-2xl font-semibold leading-tight text-fg">Heading 3</h3>
  <h4 class="text-xl font-semibold text-fg">Heading 4</h4>
  <p class="text-base leading-normal text-fg-muted">
    Body text - 這是正文文字大小，使用正常行高。適合長段落閱讀。
  </p>
  <p class="text-sm leading-normal text-fg-subtle">
    Small body - 這是較小的正文，用於次要資訊。
  </p>
  <p class="text-xs text-fg-subtle">Caption - 標題或附註文字。</p>
</div>
```

驗證：排版級距視覺上有明確的層次感和節奏感。

### 步驟 6：建立 Spacing Scale（間距級距）

```html
<!-- 間距預覽頁面 -->
<div class="p-8 space-y-8">
  <h2 class="text-2xl font-bold">Spacing Scale</h2>

  <div class="space-y-3">
    <div class="flex items-center gap-4">
      <span class="w-16 text-sm text-fg-muted font-mono">4px</span>
      <div class="h-4 bg-brand rounded" style="width: 4px;"></div>
      <span class="text-sm text-fg-subtle">--spacing-1 / space-xs</span>
    </div>
    <div class="flex items-center gap-4">
      <span class="w-16 text-sm text-fg-muted font-mono">8px</span>
      <div class="h-4 bg-brand rounded" style="width: 8px;"></div>
      <span class="text-sm text-fg-subtle">--spacing-2 / space-sm</span>
    </div>
    <div class="flex items-center gap-4">
      <span class="w-16 text-sm text-fg-muted font-mono">16px</span>
      <div class="h-4 bg-brand rounded" style="width: 16px;"></div>
      <span class="text-sm text-fg-subtle">--spacing-4 / space-md</span>
    </div>
    <div class="flex items-center gap-4">
      <span class="w-16 text-sm text-fg-muted font-mono">24px</span>
      <div class="h-4 bg-brand rounded" style="width: 24px;"></div>
      <span class="text-sm text-fg-subtle">--spacing-6 / space-lg</span>
    </div>
    <div class="flex items-center gap-4">
      <span class="w-16 text-sm text-fg-muted font-mono">32px</span>
      <div class="h-4 bg-brand rounded" style="width: 32px;"></div>
      <span class="text-sm text-fg-subtle">--spacing-8 / space-xl</span>
    </div>
    <div class="flex items-center gap-4">
      <span class="w-16 text-sm text-fg-muted font-mono">48px</span>
      <div class="h-4 bg-brand rounded" style="width: 48px;"></div>
      <span class="text-sm text-fg-subtle">--spacing-12 / space-2xl</span>
    </div>
  </div>
</div>
```

驗證：間距級距呈現清晰的遞增視覺。

### 步驟 7：建立 5 個基礎元件（使用設計令牌）

建立使用語義令牌的元件。以下以 HTML + CSS 變數展示（可直接轉換為 React/Svelte）：

```css
/* src/design-system/components.css */

/* Button - 使用元件令牌 */
@layer components {
  .ds-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--ds-space-sm);
    height: var(--ds-button-height-md);
    padding: var(--ds-button-padding-md);
    border-radius: var(--ds-button-radius);
    font-weight: var(--ds-button-font-weight);
    font-size: var(--ds-text-body-sm);
    transition: var(--ds-button-transition);
    cursor: pointer;
    border: none;
  }
  .ds-button--primary {
    background: var(--ds-color-brand);
    color: var(--ds-color-text-inverse);
  }
  .ds-button--primary:hover {
    background: var(--ds-color-brand-hover);
  }
  .ds-button--secondary {
    background: var(--ds-color-bg-secondary);
    color: var(--ds-color-text-primary);
  }
  .ds-button--secondary:hover {
    background: var(--ds-color-bg-tertiary);
  }

  /* Card - 使用元件令牌 */
  .ds-card {
    background: var(--ds-card-bg);
    border: 1px solid var(--ds-card-border);
    border-radius: var(--ds-card-radius);
    box-shadow: var(--ds-card-shadow);
    overflow: hidden;
  }
  .ds-card__header {
    padding: var(--ds-card-padding);
    padding-bottom: 0;
  }
  .ds-card__content {
    padding: var(--ds-card-padding);
  }
  .ds-card__footer {
    padding: var(--ds-card-padding);
    padding-top: 0;
    display: flex;
    align-items: center;
    gap: var(--ds-space-sm);
  }

  /* Input */
  .ds-input {
    height: var(--ds-input-height);
    padding: var(--ds-input-padding);
    border: 1px solid var(--ds-input-border);
    border-radius: var(--ds-input-radius);
    background: var(--ds-input-bg);
    color: var(--ds-color-text-primary);
    font-size: var(--ds-text-body-sm);
    width: 100%;
    outline: none;
    transition: border-color 150ms, box-shadow 150ms;
  }
  .ds-input:focus {
    border-color: var(--ds-input-border-focus);
    box-shadow: 0 0 0 3px oklch(from var(--ds-input-border-focus) l c h / 0.2);
  }
  .ds-input--error {
    border-color: var(--ds-color-error);
  }
  .ds-input--error:focus {
    box-shadow: 0 0 0 3px oklch(from var(--ds-color-error) l c h / 0.2);
  }

  /* Badge */
  .ds-badge {
    display: inline-flex;
    align-items: center;
    padding: var(--ds-badge-padding);
    border-radius: var(--ds-badge-radius);
    font-size: var(--ds-badge-font-size);
    font-weight: 500;
    line-height: 1;
  }
  .ds-badge--success {
    background: var(--ds-color-success-subtle);
    color: var(--ds-color-success);
  }
  .ds-badge--warning {
    background: var(--ds-color-warning-subtle);
    color: var(--ds-color-warning);
  }
  .ds-badge--error {
    background: var(--ds-color-error-subtle);
    color: var(--ds-color-error);
  }

  /* Alert */
  .ds-alert {
    display: flex;
    gap: var(--ds-space-sm);
    padding: var(--ds-space-md);
    border-radius: var(--ds-radius-lg);
    border: 1px solid;
    font-size: var(--ds-text-body-sm);
  }
  .ds-alert--success {
    background: var(--ds-color-success-subtle);
    border-color: var(--ds-color-success);
    color: var(--ds-color-success);
  }
  .ds-alert--warning {
    background: var(--ds-color-warning-subtle);
    border-color: var(--ds-color-warning);
    color: var(--ds-color-warning);
  }
  .ds-alert--error {
    background: var(--ds-color-error-subtle);
    border-color: var(--ds-color-error);
    color: var(--ds-color-error);
  }
}
```

```html
<!-- 元件展示 -->
<div class="space-y-8 p-8 bg-surface min-h-screen">
  <h1 class="text-4xl font-extrabold text-fg">Design System Components</h1>

  <!-- Buttons -->
  <section class="space-y-4">
    <h2 class="text-2xl font-bold text-fg">Button</h2>
    <div class="flex gap-4">
      <button class="ds-button ds-button--primary">Primary</button>
      <button class="ds-button ds-button--secondary">Secondary</button>
    </div>
  </section>

  <!-- Cards -->
  <section class="space-y-4">
    <h2 class="text-2xl font-bold text-fg">Card</h2>
    <div class="ds-card max-w-md">
      <div class="ds-card__header">
        <h3 class="text-xl font-semibold text-fg">Card Title</h3>
        <p class="text-sm text-fg-muted">Card description.</p>
      </div>
      <div class="ds-card__content">
        <p class="text-fg-muted">Card content goes here.</p>
      </div>
      <div class="ds-card__footer">
        <button class="ds-button ds-button--primary">Action</button>
      </div>
    </div>
  </section>

  <!-- Badges -->
  <section class="space-y-4">
    <h2 class="text-2xl font-bold text-fg">Badge</h2>
    <div class="flex gap-3">
      <span class="ds-badge ds-badge--success">Success</span>
      <span class="ds-badge ds-badge--warning">Warning</span>
      <span class="ds-badge ds-badge--error">Error</span>
    </div>
  </section>

  <!-- Input -->
  <section class="space-y-4 max-w-md">
    <h2 class="text-2xl font-bold text-fg">Input</h2>
    <input class="ds-input" placeholder="Normal input" />
    <input class="ds-input ds-input--error" placeholder="Error input" />
  </section>

  <!-- Alert -->
  <section class="space-y-4 max-w-lg">
    <h2 class="text-2xl font-bold text-fg">Alert</h2>
    <div class="ds-alert ds-alert--success">Operation completed successfully.</div>
    <div class="ds-alert ds-alert--warning">Please review before proceeding.</div>
    <div class="ds-alert ds-alert--error">An error occurred.</div>
  </section>
</div>
```

驗證：所有元件使用設計令牌，深色模式下自動切換外觀。

### 步驟 8：設計系統的文件化

建立令牌參考文件：

```css
/* src/tokens/_docs.css */
/* 此檔案僅供文件參考，不引入到專案中 */

/*
 * Token Architecture Documentation
 * =================================
 *
 * Layer 1: Primitive Tokens (原始令牌)
 * ------------------------------------
 * 命名規則: --color-{hue}-{shade}, --spacing-{value}
 * 範例: --color-blue-500, --spacing-4
 * 用途: 不帶語義的基礎設計值
 * 修改影響: 全面性的，會影響所有引用它的語義令牌
 *
 * Layer 2: Semantic Tokens (語義令牌)
 * ------------------------------------
 * 命名規則: --ds-color-{role}, --ds-space-{size}
 * 範例: --ds-color-brand, --ds-space-md
 * 用途: 帶有上下文意義的設計值
 * 修改影響: 類別性的，影響所有同一語義的元件
 *
 * Layer 3: Component Tokens (元件令牌)
 * ------------------------------------
 * 命名規則: --ds-{component}-{property}
 * 範例: --ds-button-height-md, --ds-card-radius
 * 用途: 特定元件的設計值
 * 修改影響: 隔離的，只影響特定元件
 *
 * Theme Switching (主題切換)
 * ------------------------------------
 * 透過 CSS 選擇器（如 .dark）切換語義令牌的值，
 * 原始令牌和元件令牌結構不變。
 */
```

驗證：文件清楚描述三層架構的命名規則、用途和修改影響範圍。

### 步驟 9：建立設計令牌的色彩預覽頁面

```html
<!-- design-system.html -->
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Design System Token Reference</title>
  <link rel="stylesheet" href="/src/app.css" />
</head>
<body class="bg-surface text-fg p-8">

  <header class="mb-12">
    <h1 class="text-5xl font-extrabold">Design System</h1>
    <p class="text-xl text-fg-muted mt-2">Token Reference & Component Library</p>
    <button
      id="themeToggle"
      class="mt-4 ds-button ds-button--secondary"
      onclick="document.documentElement.classList.toggle('dark')"
    >
      Toggle Dark Mode
    </button>
  </header>

  <!-- Color Palette -->
  <section class="mb-16">
    <h2 class="text-3xl font-bold mb-6">Color Palette</h2>

    <h3 class="text-lg font-semibold mb-3 text-fg-muted">Brand</h3>
    <div class="flex gap-3 mb-6">
      <div class="space-y-1">
        <div class="w-20 h-20 rounded-lg bg-brand"></div>
        <p class="text-xs text-fg-subtle">brand</p>
      </div>
      <div class="space-y-1">
        <div class="w-20 h-20 rounded-lg bg-brand-hover"></div>
        <p class="text-xs text-fg-subtle">hover</p>
      </div>
      <div class="space-y-1">
        <div class="w-20 h-20 rounded-lg bg-brand-subtle"></div>
        <p class="text-xs text-fg-subtle">subtle</p>
      </div>
    </div>

    <h3 class="text-lg font-semibold mb-3 text-fg-muted">Surfaces</h3>
    <div class="flex gap-3 mb-6">
      <div class="space-y-1">
        <div class="w-20 h-20 rounded-lg bg-surface border border-border"></div>
        <p class="text-xs text-fg-subtle">surface</p>
      </div>
      <div class="space-y-1">
        <div class="w-20 h-20 rounded-lg bg-surface-alt border border-border"></div>
        <p class="text-xs text-fg-subtle">alt</p>
      </div>
      <div class="space-y-1">
        <div class="w-20 h-20 rounded-lg bg-surface-strong border border-border"></div>
        <p class="text-xs text-fg-subtle">strong</p>
      </div>
    </div>

    <h3 class="text-lg font-semibold mb-3 text-fg-muted">Status</h3>
    <div class="flex gap-3">
      <div class="space-y-1">
        <div class="w-20 h-20 rounded-lg bg-success"></div>
        <p class="text-xs text-fg-subtle">success</p>
      </div>
      <div class="space-y-1">
        <div class="w-20 h-20 rounded-lg bg-warning"></div>
        <p class="text-xs text-fg-subtle">warning</p>
      </div>
      <div class="space-y-1">
        <div class="w-20 h-20 rounded-lg bg-error"></div>
        <p class="text-xs text-fg-subtle">error</p>
      </div>
    </div>
  </section>

</body>
</html>
```

驗證：色彩預覽頁面在亮/暗模式切換時正確顯示對應色彩。

### 步驟 10：建立令牌導入結構和最終整合

```css
/* src/app.css - 最終完整結構 */
@import "tailwindcss";

/* Layer 1: Primitive Tokens */
@import "./tokens/primitives.css";

/* Layer 2: Semantic Tokens */
@import "./tokens/semantic.css";

/* Layer 3: Component Tokens */
@import "./tokens/components.css";

/* Design System Components */
@import "./design-system/components.css";

/* Theme registration */
@theme {
  --color-*: initial;
  --color-brand: var(--ds-color-brand);
  --color-brand-hover: var(--ds-color-brand-hover);
  --color-brand-subtle: var(--ds-color-brand-subtle);
  --color-surface: var(--ds-color-bg-primary);
  --color-surface-alt: var(--ds-color-bg-secondary);
  --color-surface-strong: var(--ds-color-bg-tertiary);
  --color-fg: var(--ds-color-text-primary);
  --color-fg-muted: var(--ds-color-text-secondary);
  --color-fg-subtle: var(--ds-color-text-muted);
  --color-fg-inverse: var(--ds-color-text-inverse);
  --color-border: var(--ds-color-border-default);
  --color-border-strong: var(--ds-color-border-strong);
  --color-success: var(--ds-color-success);
  --color-success-subtle: var(--ds-color-success-subtle);
  --color-warning: var(--ds-color-warning);
  --color-warning-subtle: var(--ds-color-warning-subtle);
  --color-error: var(--ds-color-error);
  --color-error-subtle: var(--ds-color-error-subtle);
  --color-white: #ffffff;
  --color-black: #000000;
}
```

驗證：完整導入結構無循環引用，所有令牌正確解析。建置無錯誤。

## Hands-on Lab

### Foundation / 基礎練習

**任務：建立三層令牌架構**

1. 建立 `tokens/primitives.css` — 定義 2 個色階（品牌色 + 中性色）。
2. 建立 `tokens/semantic.css` — 定義品牌色、文字色、背景色、邊框色。
3. 在 `@theme` 中註冊語義色為 Tailwind 工具類。
4. 建立一個頁面驗證色彩系統。

**驗收清單：**
- [ ] primitive tokens 使用 oklch 色彩空間。
- [ ] semantic tokens 引用 primitive tokens（使用 `var()`）。
- [ ] `bg-brand`, `text-fg`, `border-border` 等語義工具類正常運作。
- [ ] 深色模式下色彩正確切換。
- [ ] 令牌命名一致且有意義。

### Advanced / 進階練習

**任務：建立排版級距和間距級距**

1. 在 primitives 中定義完整的 font-size 和 spacing scale。
2. 在 semantic 中建立 heading/body/caption 排版令牌和 xs/sm/md/lg/xl 間距令牌。
3. 建立排版預覽頁面和間距預覽頁面。
4. 確保所有令牌與 Tailwind 工具類整合。

**驗收清單：**
- [ ] 排版級距有 7 個以上的大小層級。
- [ ] 間距級距有 8 個以上的間距值。
- [ ] 排版預覽頁面展示所有層級。
- [ ] 間距預覽頁面有視覺對照。
- [ ] 所有值都能透過 Tailwind 工具類使用。

### Challenge / 挑戰練習

**任務：建立完整的迷你設計系統**

1. 建立三層令牌架構（primitive + semantic + component）。
2. 定義完整的色彩調色盤（品牌色 + 中性色 + 狀態色）。
3. 定義排版級距（7+ 層級）和間距級距（8+ 值）。
4. 建立 5 個基礎元件（Button, Card, Input, Badge, Alert）。
5. 支援深色模式（語義令牌自動切換）。
6. 建立設計系統文件頁面（色彩預覽 + 排版預覽 + 元件展示）。

**驗收清單：**
- [ ] 三層令牌檔案結構清晰（primitives.css, semantic.css, components.css）。
- [ ] 色彩調色盤包含 3+ 色調，每色調有 5+ 階。
- [ ] 深色模式切換時所有元件正確變色。
- [ ] 5 個元件全部使用元件令牌（非硬編碼值）。
- [ ] 修改一個 primitive token 能正確級聯影響所有引用它的語義和元件令牌。
- [ ] 設計系統文件頁面完整且可導航。

## Reference Solution

本章 Step-by-step 中的所有程式碼片段合在一起就是完整的 Reference Solution。關鍵檔案清單：

- `src/tokens/primitives.css` — 原始令牌（步驟 1）
- `src/tokens/semantic.css` — 語義令牌 + 深色模式（步驟 2）
- `src/tokens/components.css` — 元件令牌（步驟 3）
- `src/app.css` — 令牌整合與 @theme 註冊（步驟 4 + 步驟 10）
- `src/design-system/components.css` — 5 個基礎元件（步驟 7）
- `design-system.html` — 設計系統文件頁面（步驟 9）

所有程式碼都已在步驟中完整提供，可直接複製使用。

## Common Pitfalls

### 1. v4 特有：@theme 中使用 var() 引用語義令牌的時機

在 `@theme` 中使用 `var()` 引用其他 CSS 變數時，需要確保那些變數在 `:root` 或更早的位置已定義。如果 CSS 導入順序不對，`var()` 可能引用到未定義的變數。

```css
/* 正確的導入順序 */
@import "tailwindcss";
@import "./tokens/primitives.css";  /* 先定義 primitive */
@import "./tokens/semantic.css";    /* 再定義 semantic（引用 primitive） */

@theme {
  --color-brand: var(--ds-color-brand); /* semantic 已定義 */
}

/* 錯誤：順序反了 */
@import "tailwindcss";
@import "./tokens/semantic.css";    /* semantic 引用了未定義的 primitive */
@import "./tokens/primitives.css";  /* primitive 太晚定義 */
```

### 2. 過度建立令牌層次

不是所有設計值都需要三層。對於只有一個主題的小型專案，兩層甚至一層就足夠。

```css
/* 過度設計：一個只有亮色主題的小專案 */
/* primitives.css: --color-blue-500: ... */
/* semantic.css: --ds-color-brand: var(--color-blue-500) */
/* components.css: --ds-button-bg: var(--ds-color-brand) */
/* 三層 var() 嵌套，增加了偵錯難度 */

/* 適當簡化：直接在 @theme 中定義 */
@theme {
  --color-brand: oklch(0.62 0.19 250);
}
```

### 3. 語義令牌命名不一致

混合使用不同的命名慣例會造成混淆。

```css
/* 不一致的命名 */
--ds-color-brand: ...;
--ds-bg-primary: ...;        /* 為何不是 --ds-color-bg-primary？ */
--ds-textColor-muted: ...;   /* camelCase 混入 */
--ds-border: ...;             /* 缺少 color 分類 */

/* 一致的命名 */
--ds-color-brand: ...;
--ds-color-bg-primary: ...;
--ds-color-text-muted: ...;
--ds-color-border-default: ...;
```

### 4. 深色模式令牌遺漏導致元素「消失」

定義亮色語義令牌但忘記定義深色模式對應值，可能導致元素在深色模式下不可見。

```css
:root {
  --ds-color-bg-primary: #ffffff;
  --ds-color-text-primary: var(--color-neutral-900);
}

/* 忘記定義 .dark 中的值 */
/* .dark { --ds-color-bg-primary: ???; } */

/* 結果：深色模式下背景仍是白色，或繼承了不正確的值 */
```

### 5. 在元件 CSS 中硬編碼值而非使用令牌

```css
/* 不良：硬編碼值，無法透過令牌統一修改 */
.ds-button {
  border-radius: 8px;
  padding: 8px 16px;
  background: #3b82f6;
}

/* 良好：使用令牌 */
.ds-button {
  border-radius: var(--ds-button-radius);
  padding: var(--ds-button-padding-md);
  background: var(--ds-color-brand);
}
```

## Checklist

- [ ] 能建立三層令牌架構（primitive → semantic → component）。
- [ ] 能使用 oklch 色彩空間定義原始色彩令牌。
- [ ] 能在 `@theme` 中註冊語義令牌為 Tailwind 工具類。
- [ ] 能建立支援深色模式的語義令牌系統。
- [ ] 能判斷何時將工具類抽取為元件、何時保持直接使用。
- [ ] 能建立排版級距和間距級距。
- [ ] 能建立使用令牌的基礎元件（Button, Card, Input, Badge, Alert）。

## Further Reading (official links only)

- [Tailwind CSS - Theme Configuration](https://tailwindcss.com/docs/theme)
- [Tailwind CSS - @theme Directive](https://tailwindcss.com/docs/functions-and-directives#theme-directive)
- [Tailwind CSS - Customizing Colors](https://tailwindcss.com/docs/customizing-colors)
- [Tailwind CSS - Reusing Styles](https://tailwindcss.com/docs/reusing-styles)
- [Tailwind CSS v4.0 Release](https://tailwindcss.com/blog/tailwindcss-v4)
- [Tailwind CSS GitHub Repository](https://github.com/tailwindlabs/tailwindcss)
