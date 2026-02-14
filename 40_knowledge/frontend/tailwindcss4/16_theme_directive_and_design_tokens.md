---
title: "@theme Directive and Design Tokens / @theme 指令與設計令牌"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "16"
level: advanced
stack: Tailwind CSS 4.1.x
prerequisites: [15_container_queries_and_modern_layout_patterns]
---

# @theme Directive and Design Tokens / @theme 指令與設計令牌

## Goal

在前面的章節中，我們多次使用 `@theme` 來自訂斷點（[[10_responsive_design_and_breakpoints]]）、z-index（[[09_positioning_z_index_and_overflow]]）、動畫（[[13_transitions_animations_and_motion]]）和顏色令牌（[[12_dark_mode_and_multi_theme_system]]）。本章將對 `@theme` 指令進行深度剖析，完整理解它在 Tailwind CSS v4 設計令牌系統中的核心角色。

`@theme` 是 Tailwind CSS v4 最重要的革新之一。它取代了 v3 的 `tailwind.config.js` 中的 `theme` 物件，讓所有設計令牌（Design Tokens）直接在 CSS 中定義。每個 `@theme` 中定義的 CSS custom property 都會自動生成對應的 utility class。例如 `--color-brand: #3b82f6` 會自動產生 `bg-brand`、`text-brand`、`border-brand` 等工具類別。同時，這些值以標準 CSS custom properties 的形式存在於 `:root` 上，可以被任何 CSS 或 JavaScript 讀取和操作。本章將教你如何設計一套完整的設計令牌系統，涵蓋顏色、間距、字型、斷點和動畫等所有命名空間，並對比 v3 的 JavaScript 配置方式，幫助你順利遷移到 v4 的 CSS-first 方法。

## Prerequisites

- 已完成 [[15_container_queries_and_modern_layout_patterns]]。
- 理解 CSS custom properties（`var(--name)`）的語法與繼承行為。
- 對 Tailwind CSS v3 的 `tailwind.config.js` 結構有基本認識。
- 理解設計系統（Design System）的基本概念（令牌、語義化命名）。

## Core Concepts

### 1. @theme Directive Basics / @theme 指令基礎

| 概念 | 說明 | 何時使用 | 何時不使用 |
|------|------|----------|------------|
| `@theme { ... }` | 定義設計令牌，自動產生 utility classes 和 CSS variables | 定義專案的設計系統基礎 | 一次性的任意值（用 `[]` 語法） |
| `@theme inline { ... }` | 定義令牌但不產生 CSS variables（只產生 utility classes） | 不需要在 JS 中讀取的內部令牌 | 需要在運行時動態讀取令牌值時 |
| Token namespace | `--color-*`、`--spacing-*` 等命名前綴 | 讓 Tailwind 知道令牌類型以產生正確的 utilities | 不使用 Tailwind 自動產生 utilities 時 |

### 2. Token Namespaces / 令牌命名空間

| 命名空間 | 產生的工具類別 | 說明 | 何時自訂 | 何時不自訂 |
|----------|-------------|------|----------|------------|
| `--color-*` | `bg-*`、`text-*`、`border-*`、`ring-*` 等 | 顏色系統 | 品牌色、語義色 | 預設色板已足夠時 |
| `--spacing-*` | `p-*`、`m-*`、`gap-*`、`w-*`、`h-*` 等 | 間距系統 | 需要非標準的間距刻度 | 預設 4px 基準足夠時 |
| `--font-*` | `font-*` | 字型家族 | 品牌字型、中文字型 | 使用系統字型時 |
| `--font-size-*` | `text-*` | 字型大小 | 需要非標準的文字大小刻度 | 預設刻度已足夠時 |
| `--font-weight-*` | `font-*` | 字型粗細 | 自訂權重名稱 | 使用標準權重名稱時 |
| `--tracking-*` | `tracking-*` | 字距 | 品牌排版需要特殊字距 | 預設值足夠時 |
| `--leading-*` | `leading-*` | 行高 | 品牌排版需要特殊行高 | 預設值足夠時 |
| `--breakpoint-*` | `sm:`、`md:` 等斷點前綴 | 響應式斷點 | 設計稿有非標準斷點 | 預設斷點足夠時 |
| `--radius-*` | `rounded-*` | 圓角 | 品牌有特定的圓角風格 | 預設刻度足夠時 |
| `--shadow-*` | `shadow-*` | 陰影 | 需要品牌化的陰影系統 | 預設陰影足夠時 |
| `--animate-*` | `animate-*` | 動畫 | 自訂動畫效果 | 內建動畫足夠時 |
| `--z-*` | `z-*` | Z-index | 專案有特定的堆疊分層 | 預設 z-index 刻度足夠時 |

### 3. Override vs Extend / 覆蓋 vs 擴展

| 方式 | 語法 | 效果 | 何時使用 | 何時不使用 |
|------|------|------|----------|------------|
| 擴展（預設） | `@theme { --color-brand: #3b82f6; }` | 保留所有預設值，加入新令牌 | 在預設基礎上添加品牌顏色 | 需要完全自訂色彩系統時 |
| 覆蓋命名空間 | `@theme { --color-*: initial; --color-brand: #3b82f6; }` | 清除該命名空間的所有預設值，只保留自訂的 | 完全自訂某個設計維度 | 仍需要大部分預設值時 |
| 覆蓋單一值 | `@theme { --color-blue-500: #custom; }` | 修改特定預設令牌的值 | 微調預設色板 | 需要保留原始值時 |

### 4. @theme vs :root / 何時用哪個

| 方式 | 語法 | 效果 | 何時使用 | 何時不使用 |
|------|------|------|----------|------------|
| `@theme` | `@theme { --color-brand: ...; }` | 產生 utility classes + CSS variables | 需要 Tailwind 工具類別（如 `bg-brand`） | 不需要工具類別、只需要 CSS 變數時 |
| `:root` / `.dark` | `:root { --bg-main: ...; }` | 只產生 CSS variables（無工具類別） | 多主題覆蓋（`.dark { --color-surface: ... }`） | 需要 Tailwind 自動產生 utilities 時 |
| 兩者結合 | `@theme` 定義基礎 + `:root`/`.dark` 覆蓋值 | 工具類別 + 主題切換 | 完整的多主題設計系統 | 簡單專案不需要主題切換時 |

## Step-by-step

### Step 1: @theme 基礎語法

```css
/* app.css */
@import "tailwindcss";

@theme {
  /* 顏色令牌 → 產生 bg-brand, text-brand, border-brand 等 */
  --color-brand: #3b82f6;
  --color-brand-light: #93c5fd;
  --color-brand-dark: #1d4ed8;

  /* 間距令牌 → 產生 p-18, m-18, gap-18, w-18 等 */
  --spacing-18: 4.5rem;
  --spacing-128: 32rem;

  /* 字型令牌 → 產生 font-display, font-body */
  --font-display: "Cal Sans", "Inter", sans-serif;
  --font-body: "Inter", system-ui, sans-serif;
}
```

```html
<!-- 使用自訂令牌產生的工具類別 -->
<div class="bg-brand text-white p-18">
  <h1 class="font-display text-3xl font-bold">Brand Heading</h1>
  <p class="font-body mt-4">Body text with custom font.</p>
</div>

<button class="bg-brand hover:bg-brand-dark text-white rounded-lg px-6 py-3">
  Brand Button
</button>
```

### Step 2: 完整的顏色令牌系統

```css
@import "tailwindcss";

@theme {
  /* ===== 品牌色 ===== */
  --color-brand-50: #eff6ff;
  --color-brand-100: #dbeafe;
  --color-brand-200: #bfdbfe;
  --color-brand-300: #93c5fd;
  --color-brand-400: #60a5fa;
  --color-brand-500: #3b82f6;
  --color-brand-600: #2563eb;
  --color-brand-700: #1d4ed8;
  --color-brand-800: #1e40af;
  --color-brand-900: #1e3a8a;
  --color-brand-950: #172554;

  /* ===== 語義色 ===== */
  --color-surface: #ffffff;
  --color-surface-secondary: #f9fafb;
  --color-surface-tertiary: #f3f4f6;
  --color-on-surface: #111827;
  --color-on-surface-secondary: #6b7280;
  --color-on-surface-tertiary: #9ca3af;
  --color-border: #e5e7eb;
  --color-border-focus: #3b82f6;

  /* ===== 功能色 ===== */
  --color-success: #16a34a;
  --color-success-light: #dcfce7;
  --color-warning: #d97706;
  --color-warning-light: #fef3c7;
  --color-error: #dc2626;
  --color-error-light: #fee2e2;
  --color-info: #2563eb;
  --color-info-light: #dbeafe;
}

/* 深色模式覆蓋（使用 :root 選擇器，不用 @theme） */
.dark {
  --color-surface: #0f172a;
  --color-surface-secondary: #1e293b;
  --color-surface-tertiary: #334155;
  --color-on-surface: #f1f5f9;
  --color-on-surface-secondary: #94a3b8;
  --color-on-surface-tertiary: #64748b;
  --color-border: #334155;
  --color-border-focus: #60a5fa;
}
```

```html
<!-- 使用語義色（不需要 dark: 前綴，自動跟隨主題） -->
<div class="bg-surface text-on-surface">
  <div class="border-b border-border px-6 py-4">
    <h1 class="text-xl font-bold">Dashboard</h1>
  </div>
  <div class="p-6">
    <div class="rounded-lg bg-success-light p-4">
      <p class="text-success font-medium">Operation successful!</p>
    </div>
    <div class="mt-4 rounded-lg bg-error-light p-4">
      <p class="text-error font-medium">Something went wrong.</p>
    </div>
  </div>
</div>
```

### Step 3: 間距令牌系統

```css
@import "tailwindcss";

@theme {
  /* 擴展預設間距系統（保留 0, 1, 2, 3, 4, ... 等預設值） */

  /* 新增品牌間距 */
  --spacing-4.5: 1.125rem;  /* 18px */
  --spacing-13: 3.25rem;    /* 52px */
  --spacing-15: 3.75rem;    /* 60px */
  --spacing-18: 4.5rem;     /* 72px */
  --spacing-88: 22rem;      /* 352px */
  --spacing-128: 32rem;     /* 512px */

  /* 語義化間距 */
  --spacing-page-x: 1.5rem;
  --spacing-page-y: 2rem;
  --spacing-section: 4rem;
  --spacing-card: 1.5rem;
}
```

```html
<!-- 使用自訂間距 -->
<main class="px-page-x py-page-y">
  <section class="mb-section">
    <div class="rounded-xl border p-card">
      <h2 class="text-xl font-bold">Card with semantic spacing</h2>
      <p class="mt-4.5">Custom 18px gap</p>
    </div>
  </section>
</main>
```

### Step 4: 字型令牌系統

```css
@import "tailwindcss";

@theme {
  /* 字型家族 */
  --font-display: "Cal Sans", "Inter var", system-ui, sans-serif;
  --font-body: "Inter var", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", monospace;
  --font-chinese: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;

  /* 字型大小（完全自訂） */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  --font-size-5xl: 3rem;
  --font-size-hero: 4.5rem;

  /* 行高 */
  --leading-tight: 1.2;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* 字距 */
  --tracking-tight: -0.025em;
  --tracking-normal: 0em;
  --tracking-wide: 0.025em;
}
```

```html
<h1 class="font-display text-hero leading-tight tracking-tight">
  Hero Heading
</h1>
<p class="font-body text-lg leading-relaxed">
  Body text with custom typography tokens.
</p>
<code class="font-mono text-sm">
  const code = "monospace";
</code>
<p class="font-chinese text-base">
  這是使用自訂中文字型的段落。
</p>
```

### Step 5: 圓角、陰影和 Z-index 令牌

```css
@import "tailwindcss";

@theme {
  /* 圓角系統 */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  --radius-pill: 9999px;

  /* 陰影系統（品牌化的柔和陰影） */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.04);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.06), 0 2px 4px -2px rgb(0 0 0 / 0.06);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.06), 0 4px 6px -4px rgb(0 0 0 / 0.06);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.06), 0 8px 10px -6px rgb(0 0 0 / 0.06);
  --shadow-glow: 0 0 20px rgb(59 130 246 / 0.3);

  /* Z-index 分層系統 */
  --z-base: 0;
  --z-dropdown: 10;
  --z-sticky: 20;
  --z-overlay: 30;
  --z-modal: 40;
  --z-toast: 50;
  --z-tooltip: 60;
}
```

```html
<header class="sticky top-0 z-sticky bg-white shadow-sm">Navigation</header>
<div class="z-modal fixed inset-0 bg-black/50">
  <div class="rounded-2xl bg-white p-6 shadow-xl">Modal</div>
</div>
<div class="z-toast fixed right-4 top-4">
  <div class="rounded-lg bg-white p-4 shadow-glow">Toast</div>
</div>
```

### Step 6: 覆蓋 vs 擴展預設值

```css
/* ===== 方式一：擴展（保留預設值） ===== */
@theme {
  /* 保留預設的 blue-500, red-500 等，額外加入 brand */
  --color-brand: #3b82f6;
}

/* ===== 方式二：覆蓋整個命名空間 ===== */
@theme {
  /* 清除所有預設顏色，只使用自訂的 */
  --color-*: initial;

  /* 只保留需要的顏色 */
  --color-white: #ffffff;
  --color-black: #000000;
  --color-brand-50: #eff6ff;
  --color-brand-100: #dbeafe;
  --color-brand-500: #3b82f6;
  --color-brand-900: #1e3a8a;
  --color-neutral-50: #fafafa;
  --color-neutral-100: #f5f5f5;
  --color-neutral-500: #737373;
  --color-neutral-900: #171717;
  --color-success: #16a34a;
  --color-error: #dc2626;
}

/* ===== 方式三：覆蓋單一預設值 ===== */
@theme {
  /* 只修改 blue-500 的值，其他所有預設顏色保持不變 */
  --color-blue-500: #4f86f7;
}
```

### Step 7: @theme inline --- 不產生 CSS Variables

```css
/* 某些令牌不需要暴露為 CSS variables */
@theme inline {
  /* 這些只產生 utility classes，不會出現在 :root 的 CSS variables 中 */
  /* 適合不需要在 JS 中讀取的內部設計令牌 */
  --breakpoint-xs: 475px;
  --animate-wiggle: wiggle 0.3s ease-in-out;
}

/* 對比：普通 @theme 會同時產生 */
@theme {
  /* 這個會產生 utility classes AND CSS variable */
  --color-brand: #3b82f6;
  /* 等同於自動在 :root 加入 --color-brand: #3b82f6 */
}
```

### Step 8: v3 tailwind.config.js vs v4 @theme 完整對照

```js
// ===== v3: tailwind.config.js =====
module.exports = {
  darkMode: 'class',
  theme: {
    // 覆蓋預設值
    screens: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
    },
    // 擴展預設值
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        surface: 'var(--color-surface)',
      },
      spacing: {
        '18': '4.5rem',
        '128': '32rem',
      },
      fontFamily: {
        display: ['Cal Sans', 'Inter', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '4xl': '2rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      zIndex: {
        modal: '100',
        toast: '200',
      },
    },
  },
  plugins: [
    require('@tailwindcss/container-queries'),
  ],
};
```

```css
/* ===== v4: app.css ===== */
@import "tailwindcss";

/* darkMode: 'class' 的對應 */
@custom-variant dark (&:where(.dark, .dark *));

@theme {
  /* screens (breakpoints) */
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;

  /* colors - extend */
  --color-brand-50: #eff6ff;
  --color-brand-500: #3b82f6;
  --color-brand-900: #1e3a8a;
  --color-surface: var(--surface-color, #ffffff);

  /* spacing - extend */
  --spacing-18: 4.5rem;
  --spacing-128: 32rem;

  /* font-family - extend */
  --font-display: "Cal Sans", "Inter", sans-serif;
  --font-body: "Inter", system-ui, sans-serif;

  /* border-radius - extend */
  --radius-4xl: 2rem;

  /* animation - extend */
  --animate-fade-in: fade-in 0.5s ease-out;

  /* z-index - extend */
  --z-modal: 100;
  --z-toast: 200;
}

/* keyframes（在 @theme 之外） */
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Container Queries: v4 內建，不需要 plugin */
```

### Step 9: 在 JavaScript 中讀取設計令牌

`@theme` 產生的 CSS variables 可以在 JavaScript 中讀取，實現設計令牌的跨語言共享。

```typescript
// design-tokens.ts - 讀取 CSS custom properties

/**
 * 從 CSS custom properties 讀取設計令牌值
 */
function getToken(name: string): string {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
}

// 使用範例
const brandColor = getToken('--color-brand-500');    // "#3b82f6"
const spacing18 = getToken('--spacing-18');           // "4.5rem"
const fontDisplay = getToken('--font-display');       // "Cal Sans, Inter, sans-serif"

// 在 Chart.js 等套件中使用
const chartConfig = {
  borderColor: getToken('--color-brand-500'),
  backgroundColor: getToken('--color-brand-50'),
  fontFamily: getToken('--font-body'),
};

// React hook
function useDesignToken(tokenName: string): string {
  const [value, setValue] = React.useState('');

  React.useEffect(() => {
    const computedValue = getComputedStyle(document.documentElement)
      .getPropertyValue(tokenName)
      .trim();
    setValue(computedValue);

    // 監聽主題變化
    const observer = new MutationObserver(() => {
      const newValue = getComputedStyle(document.documentElement)
        .getPropertyValue(tokenName)
        .trim();
      setValue(newValue);
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class', 'data-theme'],
    });

    return () => observer.disconnect();
  }, [tokenName]);

  return value;
}
```

### Step 10: 建立完整的設計令牌文件

一個完整的設計令牌系統應該有清晰的結構和文件。

```css
/* ===================================================
 * Design Token System
 * Project: MyApp
 * Version: 1.0.0
 *
 * Token Categories:
 * 1. Colors (brand, semantic, functional)
 * 2. Typography (font family, size, weight, leading, tracking)
 * 3. Spacing (layout, component)
 * 4. Border (radius, width)
 * 5. Shadow (elevation system)
 * 6. Motion (duration, easing, animation)
 * 7. Layout (breakpoints, z-index, container)
 * =================================================== */

@import "tailwindcss";

@custom-variant dark (&:where(.dark, .dark *));

@theme {
  /* ---------------------------------------------------
   * 1. COLORS
   * --------------------------------------------------- */

  /* Brand Primary */
  --color-brand-50: #eef2ff;
  --color-brand-100: #e0e7ff;
  --color-brand-200: #c7d2fe;
  --color-brand-300: #a5b4fc;
  --color-brand-400: #818cf8;
  --color-brand-500: #6366f1;
  --color-brand-600: #4f46e5;
  --color-brand-700: #4338ca;
  --color-brand-800: #3730a3;
  --color-brand-900: #312e81;
  --color-brand-950: #1e1b4b;

  /* Semantic Colors (base values for light mode) */
  --color-surface: #ffffff;
  --color-surface-raised: #f9fafb;
  --color-surface-sunken: #f3f4f6;
  --color-on-surface: #111827;
  --color-on-surface-muted: #6b7280;
  --color-border: #e5e7eb;
  --color-border-strong: #d1d5db;

  /* Functional Colors */
  --color-success: #059669;
  --color-success-bg: #ecfdf5;
  --color-warning: #d97706;
  --color-warning-bg: #fffbeb;
  --color-error: #dc2626;
  --color-error-bg: #fef2f2;
  --color-info: #2563eb;
  --color-info-bg: #eff6ff;

  /* ---------------------------------------------------
   * 2. TYPOGRAPHY
   * --------------------------------------------------- */

  --font-sans: "Inter var", system-ui, -apple-system, sans-serif;
  --font-display: "Cal Sans", "Inter var", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", ui-monospace, monospace;

  --font-size-hero: 4.5rem;

  --leading-heading: 1.2;
  --leading-body: 1.6;

  --tracking-heading: -0.02em;

  /* ---------------------------------------------------
   * 3. SPACING
   * --------------------------------------------------- */

  --spacing-page: 1.5rem;
  --spacing-section: 5rem;
  --spacing-card: 1.5rem;

  /* ---------------------------------------------------
   * 4. BORDER
   * --------------------------------------------------- */

  --radius-card: 0.75rem;
  --radius-button: 0.5rem;
  --radius-input: 0.5rem;
  --radius-badge: 9999px;
  --radius-modal: 1rem;

  /* ---------------------------------------------------
   * 5. SHADOWS (Elevation System)
   * --------------------------------------------------- */

  --shadow-xs: 0 1px 2px rgb(0 0 0 / 0.04);
  --shadow-sm: 0 1px 3px rgb(0 0 0 / 0.06), 0 1px 2px rgb(0 0 0 / 0.04);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.06), 0 2px 4px -2px rgb(0 0 0 / 0.04);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.06), 0 4px 6px -4px rgb(0 0 0 / 0.04);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.06), 0 8px 10px -6px rgb(0 0 0 / 0.04);
  --shadow-brand: 0 4px 14px rgb(99 102 241 / 0.25);

  /* ---------------------------------------------------
   * 6. MOTION
   * --------------------------------------------------- */

  --animate-fade-in: fade-in 0.3s ease-out;
  --animate-slide-up: slide-up 0.4s ease-out;
  --animate-scale-in: scale-in 0.2s ease-out;

  /* ---------------------------------------------------
   * 7. LAYOUT
   * --------------------------------------------------- */

  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;

  --z-base: 0;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-overlay: 300;
  --z-modal: 400;
  --z-toast: 500;
  --z-tooltip: 600;
}

/* Keyframes */
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

/* ---------------------------------------------------
 * DARK MODE OVERRIDES
 * --------------------------------------------------- */

.dark {
  --color-surface: #0f172a;
  --color-surface-raised: #1e293b;
  --color-surface-sunken: #0c1322;
  --color-on-surface: #f1f5f9;
  --color-on-surface-muted: #94a3b8;
  --color-border: #334155;
  --color-border-strong: #475569;

  --color-success-bg: #052e16;
  --color-warning-bg: #451a03;
  --color-error-bg: #450a0a;
  --color-info-bg: #172554;

  --shadow-xs: 0 1px 2px rgb(0 0 0 / 0.2);
  --shadow-sm: 0 1px 3px rgb(0 0 0 / 0.3), 0 1px 2px rgb(0 0 0 / 0.2);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.2);
  --shadow-brand: 0 4px 14px rgb(99 102 241 / 0.4);
}
```

## Hands-on Lab

### Foundation 基礎練習

**任務：** 使用 `@theme` 定義品牌顏色和字型。

需求：
- 定義一組品牌色（brand-50 到 brand-950，共 11 階）
- 定義兩種字型（display 和 body）
- 定義自訂間距（page padding 和 section gap）
- 用這些令牌建立一個簡單的品牌頁面

**驗收清單：**
- [ ] `@theme` 正確定義品牌色、字型和間距
- [ ] `bg-brand-500`、`text-brand-700` 等工具類別正常運作
- [ ] `font-display` 和 `font-body` 正確套用
- [ ] 自訂間距令牌（如 `px-page`）正常運作

### Advanced 進階練習

**任務：** 建立完整的語義化設計令牌系統。

需求：
- 定義語義色（surface、on-surface、border、success、error、warning、info）
- 深色模式覆蓋（使用 `.dark` 選擇器覆蓋語義色）
- 定義圓角、陰影和 z-index 系統
- 建立 v3 vs v4 對照表（如何從 tailwind.config.js 遷移）
- 建立品牌化的元件（按鈕、卡片、輸入框）使用語義色

**驗收清單：**
- [ ] 語義色系統在 light 和 dark 模式下正確切換
- [ ] 無需在 HTML 中使用 `dark:` 前綴（顏色透過 CSS variables 自動切換）
- [ ] 圓角和陰影令牌產生正確的工具類別
- [ ] z-index 分層系統一致且可預測
- [ ] 元件使用語義色且在兩種模式下美觀

### Challenge 挑戰練習

**任務：** 建立一個多品牌設計令牌系統。

需求：
- 3 個品牌主題（default、forest、ocean）
- 每個主題有完整的顏色、字型、圓角風格
- 使用 `@theme` 定義基礎令牌
- 使用 `[data-theme]` 選擇器覆蓋品牌令牌
- 建立主題切換器展示三種品牌
- 在 JavaScript 中讀取設計令牌用於圖表配置
- 提供完整的令牌文件（包含命名規則和使用指南）

**驗收清單：**
- [ ] 三個品牌主題各自正確顯示
- [ ] 切換主題時所有元件自動更新（無需修改 HTML）
- [ ] JavaScript 能正確讀取 CSS variables
- [ ] 圖表配色與當前主題一致
- [ ] 令牌文件清晰描述每個命名空間的用途
- [ ] 完整的 v3 遷移對照表

## Reference Solution

```html
<!DOCTYPE html>
<html lang="zh-Hant" data-theme="default">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ch16 Lab - Design Token System</title>
  <script>
    (function() {
      const theme = localStorage.getItem('brand-theme') || 'default';
      document.documentElement.setAttribute('data-theme', theme);
      const colorMode = localStorage.getItem('color-mode') || 'light';
      if (colorMode === 'dark') document.documentElement.classList.add('dark');
    })();
  </script>
  <style>
    @import "tailwindcss";

    @custom-variant dark (&:where(.dark, .dark *));

    @theme {
      --font-sans: "Inter var", system-ui, sans-serif;
      --font-display: "Cal Sans", "Inter var", sans-serif;
      --font-mono: "JetBrains Mono", ui-monospace, monospace;

      --color-brand: #6366f1;
      --color-brand-light: #e0e7ff;
      --color-brand-dark: #4338ca;

      --color-surface: #ffffff;
      --color-surface-raised: #f9fafb;
      --color-on-surface: #111827;
      --color-on-surface-muted: #6b7280;
      --color-border: #e5e7eb;

      --color-success: #059669;
      --color-error: #dc2626;
      --color-warning: #d97706;

      --radius-card: 0.75rem;
      --radius-button: 0.5rem;
      --radius-badge: 9999px;

      --shadow-card: 0 1px 3px rgb(0 0 0 / 0.06), 0 1px 2px rgb(0 0 0 / 0.04);
      --shadow-card-hover: 0 10px 15px -3px rgb(0 0 0 / 0.06), 0 4px 6px -4px rgb(0 0 0 / 0.04);
      --shadow-brand: 0 4px 14px rgb(99 102 241 / 0.25);

      --spacing-page: 1.5rem;
      --spacing-section: 4rem;

      --z-sticky: 20;
      --z-modal: 40;
      --z-toast: 50;

      --animate-fade-in: fade-in 0.3s ease-out forwards;
    }

    @keyframes fade-in {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Dark mode overrides */
    .dark {
      --color-surface: #0f172a;
      --color-surface-raised: #1e293b;
      --color-on-surface: #f1f5f9;
      --color-on-surface-muted: #94a3b8;
      --color-border: #334155;
      --shadow-card: 0 1px 3px rgb(0 0 0 / 0.3);
      --shadow-card-hover: 0 10px 15px -3px rgb(0 0 0 / 0.3);
    }

    /* Forest theme */
    [data-theme="forest"] {
      --color-brand: #16a34a;
      --color-brand-light: #dcfce7;
      --color-brand-dark: #15803d;
      --shadow-brand: 0 4px 14px rgb(22 163 74 / 0.25);
    }
    [data-theme="forest"].dark {
      --color-brand: #22c55e;
      --color-brand-light: #052e16;
      --color-brand-dark: #16a34a;
    }

    /* Ocean theme */
    [data-theme="ocean"] {
      --color-brand: #0284c7;
      --color-brand-light: #e0f2fe;
      --color-brand-dark: #0369a1;
      --shadow-brand: 0 4px 14px rgb(2 132 199 / 0.25);
    }
    [data-theme="ocean"].dark {
      --color-brand: #38bdf8;
      --color-brand-light: #082f49;
      --color-brand-dark: #0284c7;
    }
  </style>
</head>
<body class="min-h-screen bg-surface text-on-surface transition-colors duration-300">

  <div class="mx-auto max-w-4xl px-page py-12">

    <!-- ====== Header ====== -->
    <header class="flex items-center justify-between">
      <h1 class="font-display text-2xl font-bold">Design Tokens</h1>

      <div class="flex items-center gap-4">
        <!-- Brand Theme Switcher -->
        <div class="flex gap-1 rounded-lg border border-border bg-surface-raised p-1">
          <button data-brand="default"
                  class="rounded-button px-3 py-1.5 text-xs font-medium transition-colors">
            Default
          </button>
          <button data-brand="forest"
                  class="rounded-button px-3 py-1.5 text-xs font-medium transition-colors">
            Forest
          </button>
          <button data-brand="ocean"
                  class="rounded-button px-3 py-1.5 text-xs font-medium transition-colors">
            Ocean
          </button>
        </div>

        <!-- Color Mode Toggle -->
        <button id="dark-toggle"
                class="rounded-button border border-border bg-surface-raised px-3 py-1.5 text-xs font-medium
                       transition-colors hover:bg-surface">
          Toggle Dark
        </button>
      </div>
    </header>

    <!-- ====== Token Preview ====== -->
    <section class="mt-section animate-fade-in space-y-12">

      <!-- Color Tokens -->
      <div>
        <h2 class="text-lg font-semibold">Color Tokens</h2>
        <div class="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div class="space-y-2">
            <div class="h-16 rounded-card bg-brand"></div>
            <p class="text-xs text-on-surface-muted">brand</p>
          </div>
          <div class="space-y-2">
            <div class="h-16 rounded-card bg-brand-light"></div>
            <p class="text-xs text-on-surface-muted">brand-light</p>
          </div>
          <div class="space-y-2">
            <div class="h-16 rounded-card bg-brand-dark"></div>
            <p class="text-xs text-on-surface-muted">brand-dark</p>
          </div>
          <div class="space-y-2">
            <div class="h-16 rounded-card border border-border bg-surface-raised"></div>
            <p class="text-xs text-on-surface-muted">surface-raised</p>
          </div>
        </div>
      </div>

      <!-- Typography Tokens -->
      <div>
        <h2 class="text-lg font-semibold">Typography Tokens</h2>
        <div class="mt-4 space-y-4 rounded-card border border-border bg-surface-raised p-6">
          <p class="font-display text-3xl font-bold">font-display: Cal Sans</p>
          <p class="font-sans text-lg">font-sans: Inter (default body text)</p>
          <p class="font-mono text-sm">font-mono: JetBrains Mono</p>
        </div>
      </div>

      <!-- Component Preview -->
      <div>
        <h2 class="text-lg font-semibold">Components with Tokens</h2>
        <div class="mt-4 grid gap-6 sm:grid-cols-2">
          <!-- Card -->
          <div class="rounded-card border border-border bg-surface p-6 shadow-card
                      transition-shadow hover:shadow-card-hover">
            <h3 class="font-semibold">Token-based Card</h3>
            <p class="mt-2 text-sm text-on-surface-muted">
              This card uses semantic design tokens for all visual properties.
            </p>
            <button class="mt-4 rounded-button bg-brand px-4 py-2 text-sm font-medium text-white
                           shadow-brand
                           transition-all hover:bg-brand-dark hover:shadow-lg">
              Brand Action
            </button>
          </div>

          <!-- Form -->
          <div class="rounded-card border border-border bg-surface p-6 shadow-card">
            <h3 class="font-semibold">Token-based Form</h3>
            <div class="mt-4 space-y-3">
              <input
                type="text"
                placeholder="Input field"
                class="w-full rounded-button border border-border bg-surface px-3 py-2 text-sm text-on-surface
                       placeholder:text-on-surface-muted/50
                       focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20
                       transition-all"
              />
              <div class="flex gap-3">
                <button class="flex-1 rounded-button bg-brand px-4 py-2 text-sm font-medium text-white
                               transition-colors hover:bg-brand-dark">
                  Submit
                </button>
                <button class="flex-1 rounded-button border border-border px-4 py-2 text-sm font-medium text-on-surface
                               transition-colors hover:bg-surface-raised">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Badges -->
      <div>
        <h2 class="text-lg font-semibold">Functional Colors</h2>
        <div class="mt-4 flex flex-wrap gap-3">
          <span class="rounded-badge bg-brand-light px-3 py-1 text-xs font-medium text-brand">
            Brand
          </span>
          <span class="rounded-badge bg-green-100 px-3 py-1 text-xs font-medium text-success dark:bg-green-900/30">
            Success
          </span>
          <span class="rounded-badge bg-yellow-100 px-3 py-1 text-xs font-medium text-warning dark:bg-yellow-900/30">
            Warning
          </span>
          <span class="rounded-badge bg-red-100 px-3 py-1 text-xs font-medium text-error dark:bg-red-900/30">
            Error
          </span>
        </div>
      </div>

    </section>

    <!-- Token Values (for reference) -->
    <section class="mt-section">
      <h2 class="text-lg font-semibold">Current Token Values</h2>
      <div id="token-values" class="mt-4 rounded-card border border-border bg-surface-raised p-6 font-mono text-xs">
        <p class="text-on-surface-muted">Click "Read Tokens" to display current CSS variable values.</p>
      </div>
      <button id="read-tokens"
              class="mt-3 rounded-button bg-brand px-4 py-2 text-sm font-medium text-white
                     transition-colors hover:bg-brand-dark">
        Read Tokens
      </button>
    </section>
  </div>

  <script>
    // Brand theme switcher
    document.querySelectorAll('[data-brand]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var theme = btn.getAttribute('data-brand');
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('brand-theme', theme);
        updateActiveButton();
      });
    });

    // Dark mode toggle
    document.getElementById('dark-toggle').addEventListener('click', function() {
      var isDark = document.documentElement.classList.toggle('dark');
      localStorage.setItem('color-mode', isDark ? 'dark' : 'light');
    });

    // Active button indicator
    function updateActiveButton() {
      var current = document.documentElement.getAttribute('data-theme') || 'default';
      document.querySelectorAll('[data-brand]').forEach(function(btn) {
        if (btn.getAttribute('data-brand') === current) {
          btn.classList.add('bg-brand', 'text-white');
          btn.classList.remove('text-on-surface-muted');
        } else {
          btn.classList.remove('bg-brand', 'text-white');
          btn.classList.add('text-on-surface-muted');
        }
      });
    }
    updateActiveButton();

    // Read token values
    document.getElementById('read-tokens').addEventListener('click', function() {
      var tokens = [
        '--color-brand',
        '--color-brand-light',
        '--color-brand-dark',
        '--color-surface',
        '--color-on-surface',
        '--color-border',
        '--font-display',
        '--font-sans',
      ];
      var container = document.getElementById('token-values');
      // Clear existing content safely
      while (container.firstChild) {
        container.removeChild(container.firstChild);
      }
      var style = getComputedStyle(document.documentElement);
      tokens.forEach(function(token) {
        var value = style.getPropertyValue(token).trim();
        var line = document.createElement('p');
        line.className = 'py-1 border-b border-border last:border-0';
        var nameSpan = document.createElement('span');
        nameSpan.className = 'text-brand';
        nameSpan.textContent = token;
        var valueSpan = document.createElement('span');
        valueSpan.className = 'text-on-surface-muted';
        valueSpan.textContent = ': ' + value;
        line.appendChild(nameSpan);
        line.appendChild(valueSpan);
        container.appendChild(line);
      });
    });
  </script>

</body>
</html>
```

## Common Pitfalls

1. **在 @theme 內寫 @keyframes：** `@keyframes` 必須在 `@theme` 區塊之外定義。`@theme` 只能包含 CSS custom property 定義（`--name: value`），把 `@keyframes` 放進去會被忽略且不會報錯。

2. **命名空間前綴錯誤：** Tailwind v4 要求特定的命名空間前綴來產生對應的工具類別。例如 `--color-brand` 產生顏色類別，`--spacing-18` 產生間距類別。如果寫成 `--brand-color: ...`（前綴不對），Tailwind 不會產生任何工具類別。

3. **覆蓋 vs 擴展搞混：** `@theme { --color-brand: ...; }` 是**擴展**（保留所有預設顏色）。如果想**覆蓋**整個顏色系統，需要先用 `--color-*: initial;` 清除預設值。忘記加 `initial` 會導致預設的 red、blue 等顏色仍然存在。

4. **v4 特定 --- @theme 中的 CSS variable 引用：** 在 `@theme` 中可以引用其他 CSS variables，但要注意 `@theme` 定義的值會在編譯時解析為靜態值並設定到 `:root`。如果在 `.dark` 選擇器中覆蓋變數，應該使用標準 CSS 選擇器而非 `@theme`。`@theme` 定義基礎值，選擇器覆蓋主題值。

5. **忘記 @theme inline 的用途：** 某些令牌（如斷點、動畫）不需要作為 CSS variable 暴露。使用 `@theme inline { ... }` 可以只產生 utility classes 而不污染 `:root` 的 CSS variables。不使用 `inline` 會導致不必要的 CSS variables 輸出。

6. **在 @theme 中使用不支援的 CSS 語法：** `@theme` 只接受 `--name: value;` 格式的宣告。不能在裡面寫選擇器、巢狀規則或其他 CSS 語法。如果需要條件式的令牌值（如深色模式），應該在 `@theme` 外使用標準 CSS 選擇器覆蓋。

## Checklist

- [ ] 理解 `@theme` 指令的作用：定義設計令牌並自動產生 utility classes 和 CSS variables。
- [ ] 知道各個令牌命名空間（`--color-*`、`--spacing-*`、`--font-*` 等）對應產生的工具類別。
- [ ] 能區分擴展（新增令牌）和覆蓋（`--color-*: initial` 清除後重建）兩種模式。
- [ ] 理解 `@theme` vs `:root` 的差異：前者產生 utilities + variables，後者只產生 variables。
- [ ] 能結合 `@theme`（基礎令牌）和 CSS 選擇器（`.dark`、`[data-theme]`）建立多主題系統。
- [ ] 能從 v3 的 `tailwind.config.js` theme 物件遷移到 v4 的 `@theme` 指令。
- [ ] 知道 `@theme inline` 的用途：只產生 utilities 不產生 CSS variables。
- [ ] 能在 JavaScript 中讀取 `@theme` 定義的 CSS variables。

## Further Reading (official links only)

- [Theme Configuration - Tailwind CSS](https://tailwindcss.com/docs/theme)
- [Customizing Colors - Tailwind CSS](https://tailwindcss.com/docs/customizing-colors)
- [Customizing Spacing - Tailwind CSS](https://tailwindcss.com/docs/customizing-spacing)
- [Adding Custom Styles - Tailwind CSS](https://tailwindcss.com/docs/adding-custom-styles)
- [Tailwind CSS v4.0 - tailwindcss.com](https://tailwindcss.com/blog/tailwindcss-v4)
- [GitHub - tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss)
