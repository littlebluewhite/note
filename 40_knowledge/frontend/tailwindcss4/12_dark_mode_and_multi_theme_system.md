---
title: "Dark Mode and Multi-Theme System / 深色模式與多主題系統"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "12"
level: intermediate
stack: Tailwind CSS 4.1.x
prerequisites: [11_state_variants_hover_focus_and_groups]
---

# Dark Mode and Multi-Theme System / 深色模式與多主題系統

## Goal

在前一章 [[11_state_variants_hover_focus_and_groups]] 中，我們學會了各種狀態變體 --- hover、focus、group、peer 等等。其中 `dark:` 變體我們只簡單帶過。本章將深入探討如何在 Tailwind CSS v4 中實現完整的深色模式支援，以及如何建立靈活的多主題系統。

深色模式已經從「錦上添花」變成了現代 Web 應用的基本需求。Tailwind CSS v4 提供了兩種深色模式策略：基於系統偏好的 `media` 策略和基於 CSS class/selector 的手動策略。v4 的革新之處在於引入了 `@custom-variant` 指令來自訂 `dark:` 變體的行為，以及透過 `@theme` 定義的 CSS custom properties 來建立主題令牌（design tokens），這讓多主題系統的實現變得更加直覺和強大。搭配 JavaScript 的主題切換邏輯，你可以建立支援 light/dark/system 三種模式甚至自訂品牌主題的完整系統。下一章 [[13_transitions_animations_and_motion]] 將教你如何為主題切換添加平滑的過渡動畫。

## Prerequisites

- 已完成 [[11_state_variants_hover_focus_and_groups]]，熟悉狀態變體的使用。
- 理解 CSS custom properties（CSS 變數）的基本語法 `var(--name)`。
- 知道 `prefers-color-scheme` media query 的概念。
- 已安裝 Tailwind CSS v4 開發環境。

## Core Concepts

### 1. Dark Mode Strategies / 深色模式策略

| 策略 | Tailwind v4 設定 | 切換方式 | 何時使用 | 何時不使用 |
|------|-----------------|---------|----------|------------|
| `media`（預設） | 無需額外設定 | 系統偏好自動切換 | MVP 快速開發、不需要手動控制 | 需要使用者手動切換或多主題時 |
| `selector`（class） | `@custom-variant dark (&:where(.dark, .dark *))` | JavaScript 控制 `.dark` class | 需要手動切換、支援 system/light/dark 三種模式 | 極簡專案且系統偏好已足夠時 |
| 自訂 selector | `@custom-variant dark (&:where([data-theme="dark"], [data-theme="dark"] *))` | JavaScript 控制 data attribute | 多主題系統、需要更多主題選項 | 只需要 light/dark 兩種時 |

### 2. Theme Token System / 主題令牌系統

| 方式 | 語法 | 何時使用 | 何時不使用 |
|------|------|----------|------------|
| 直接使用 `dark:` | `bg-white dark:bg-gray-900` | 簡單的顏色切換、少量元素 | 大量元素需要一致的主題色時（維護困難） |
| CSS custom properties | `bg-[var(--bg-primary)]` | 需要語義化顏色（如 primary/secondary） | 顏色只用一次的場景 |
| `@theme` + 語義變數 | `@theme { --color-surface: ...; }` + `bg-surface` | 完整的設計令牌系統、多主題 | 小型專案（過度工程） |

### 3. Theme Switching Approaches / 主題切換方式

| 方式 | 實作 | 何時使用 | 何時不使用 |
|------|------|----------|------------|
| System only | `prefers-color-scheme` | 最簡單，尊重使用者系統偏好 | 需要在應用內手動切換時 |
| Manual toggle | JS + `.dark` class on `<html>` | light/dark 雙模式手動控制 | 需要「跟隨系統」選項時 |
| Three-way | JS + localStorage + `matchMedia` | light/dark/system 完整方案 | 只需要兩種模式時 |
| Multi-theme | JS + `data-theme` attribute | 品牌主題、彩色主題 | 只需要 light/dark 時 |

## Step-by-step

### Step 1: 預設的 Media 策略

Tailwind CSS v4 預設使用 `prefers-color-scheme` media query，不需要任何額外設定。

```html
<!-- 自動跟隨系統深色模式偏好 -->
<div class="bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100">
  <h1 class="text-2xl font-bold">Hello, Dark Mode!</h1>
  <p class="text-gray-600 dark:text-gray-400">
    此內容會自動跟隨你的作業系統深色模式設定。
  </p>
</div>

<!-- 卡片：深色模式完整樣式 -->
<div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm
            dark:border-gray-700 dark:bg-gray-800 dark:shadow-gray-900/20">
  <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Card Title</h2>
  <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Card description text.</p>
  <button class="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700
                 dark:bg-blue-500 dark:hover:bg-blue-400">
    Action
  </button>
</div>
```

### Step 2: 切換到 Selector 策略（手動控制）

在 Tailwind CSS v4 中，使用 `@custom-variant` 指令將 `dark:` 改為 class-based。

```css
/* app.css */
@import "tailwindcss";

/* 將 dark 模式從 media 策略改為 selector 策略 */
@custom-variant dark (&:where(.dark, .dark *));
```

```html
<!-- 在 <html> 或 <body> 上加 .dark class 來啟用深色模式 -->
<html class="dark">
  <body class="bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
    <!-- 所有 dark: 變體現在由 .dark class 控制 -->
  </body>
</html>
```

### Step 3: 建立 Light/Dark/System 三模式切換

```html
<!-- Theme Switcher UI -->
<div class="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-100 p-1
            dark:border-gray-700 dark:bg-gray-800">
  <button
    data-theme-value="light"
    class="rounded-md px-3 py-1.5 text-sm font-medium text-gray-600
           hover:text-gray-900 data-[active]:bg-white data-[active]:text-gray-900 data-[active]:shadow-sm
           dark:text-gray-400 dark:hover:text-gray-200 dark:data-[active]:bg-gray-700 dark:data-[active]:text-white
           transition-all"
  >
    &#9728; Light
  </button>
  <button
    data-theme-value="dark"
    class="rounded-md px-3 py-1.5 text-sm font-medium text-gray-600
           hover:text-gray-900 data-[active]:bg-white data-[active]:text-gray-900 data-[active]:shadow-sm
           dark:text-gray-400 dark:hover:text-gray-200 dark:data-[active]:bg-gray-700 dark:data-[active]:text-white
           transition-all"
  >
    &#9790; Dark
  </button>
  <button
    data-theme-value="system"
    class="rounded-md px-3 py-1.5 text-sm font-medium text-gray-600
           hover:text-gray-900 data-[active]:bg-white data-[active]:text-gray-900 data-[active]:shadow-sm
           dark:text-gray-400 dark:hover:text-gray-200 dark:data-[active]:bg-gray-700 dark:data-[active]:text-white
           transition-all"
  >
    &#128187; System
  </button>
</div>
```

```javascript
// theme-switcher.js
function getSystemTheme() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme) {
  const root = document.documentElement;
  const resolved = theme === 'system' ? getSystemTheme() : theme;

  if (resolved === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }

  // 更新 UI 指示器
  document.querySelectorAll('[data-theme-value]').forEach(btn => {
    btn.toggleAttribute('data-active', btn.dataset.themeValue === theme);
  });

  // 持久化選擇
  localStorage.setItem('theme', theme);
}

// 初始化
const savedTheme = localStorage.getItem('theme') || 'system';
applyTheme(savedTheme);

// 監聽系統偏好變化（僅在 system 模式下生效）
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  if (localStorage.getItem('theme') === 'system') {
    applyTheme('system');
  }
});

// 綁定按鈕
document.querySelectorAll('[data-theme-value]').forEach(btn => {
  btn.addEventListener('click', () => applyTheme(btn.dataset.themeValue));
});
```

### Step 4: 防止主題閃爍（Flash of Unstyled Content）

在 `<head>` 中加入內嵌腳本，在頁面渲染前套用主題。

```html
<head>
  <script>
    // 在 DOM 解析前立即執行，防止主題閃爍
    (function() {
      const theme = localStorage.getItem('theme') || 'system';
      const isDark = theme === 'dark' ||
        (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
      if (isDark) {
        document.documentElement.classList.add('dark');
      }
    })();
  </script>
</head>
```

### Step 5: 使用 CSS Custom Properties 建立語義化顏色

```css
/* app.css */
@import "tailwindcss";

@custom-variant dark (&:where(.dark, .dark *));

/* 在 @theme 中定義語義化顏色令牌 */
@theme {
  --color-surface: #ffffff;
  --color-surface-secondary: #f9fafb;
  --color-on-surface: #111827;
  --color-on-surface-secondary: #6b7280;
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-border: #e5e7eb;
  --color-border-focus: #2563eb;
}

/* 深色模式覆蓋（使用 :root.dark 或 .dark 選擇器） */
.dark {
  --color-surface: #0f172a;
  --color-surface-secondary: #1e293b;
  --color-on-surface: #f1f5f9;
  --color-on-surface-secondary: #94a3b8;
  --color-primary: #3b82f6;
  --color-primary-hover: #60a5fa;
  --color-border: #334155;
  --color-border-focus: #3b82f6;
}
```

```html
<!-- 使用語義化顏色：不再需要 dark: 前綴 -->
<div class="bg-surface text-on-surface">
  <div class="rounded-xl border border-border bg-surface-secondary p-6">
    <h2 class="text-lg font-semibold">Semantic Colors</h2>
    <p class="mt-2 text-on-surface-secondary">
      使用語義化顏色名稱，深色模式自動跟隨 CSS custom properties。
    </p>
    <button class="mt-4 rounded-lg bg-primary px-4 py-2 text-white hover:bg-primary-hover">
      Primary Action
    </button>
  </div>
</div>
```

### Step 6: 多主題系統（超越 light/dark）

```css
/* app.css */
@import "tailwindcss";

/* 使用 data-theme attribute 管理多主題 */
@custom-variant dark (&:where([data-theme="dark"], [data-theme="dark"] *));

@theme {
  --color-surface: #ffffff;
  --color-primary: #2563eb;
  --color-accent: #8b5cf6;
}

/* 深色主題 */
[data-theme="dark"] {
  --color-surface: #0f172a;
  --color-primary: #3b82f6;
  --color-accent: #a78bfa;
}

/* 品牌主題：森林綠 */
[data-theme="forest"] {
  --color-surface: #f0fdf4;
  --color-primary: #16a34a;
  --color-accent: #65a30d;
}

/* 品牌主題：海洋藍 */
[data-theme="ocean"] {
  --color-surface: #f0f9ff;
  --color-primary: #0284c7;
  --color-accent: #0891b2;
}

/* 深色森林主題 */
[data-theme="forest-dark"] {
  --color-surface: #052e16;
  --color-primary: #22c55e;
  --color-accent: #84cc16;
}
```

```html
<html data-theme="forest">
  <body class="bg-surface text-on-surface">
    <!-- 所有語義化顏色會自動對應到 forest 主題 -->
  </body>
</html>
```

```javascript
// 多主題切換
function setTheme(themeName) {
  document.documentElement.setAttribute('data-theme', themeName);
  localStorage.setItem('theme', themeName);
}
```

### Step 7: v3 vs v4 深色模式設定對比

```js
// v3: tailwind.config.js
module.exports = {
  darkMode: 'class',          // 或 'media'
  // darkMode: ['class', '.dark-mode'],  // 自訂 class 名稱
  theme: {
    extend: {
      colors: {
        surface: 'var(--color-surface)',
      },
    },
  },
};
```

```css
/* v4: 全部在 CSS 中完成 */
@import "tailwindcss";

/* 等同於 v3 的 darkMode: 'class' */
@custom-variant dark (&:where(.dark, .dark *));

/* 等同於 v3 的自訂 class 名稱 */
/* @custom-variant dark (&:where(.dark-mode, .dark-mode *)); */

/* 等同於 v3 的 theme.extend.colors */
@theme {
  --color-surface: #ffffff;
}
```

### Step 8: React 中的主題切換器

```tsx
// ThemeSwitcher.tsx
import { useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem('theme') as Theme) || 'system';
    }
    return 'system';
  });

  useEffect(() => {
    const root = document.documentElement;
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    function applyTheme() {
      const resolved = theme === 'system'
        ? (mediaQuery.matches ? 'dark' : 'light')
        : theme;

      root.classList.toggle('dark', resolved === 'dark');
      localStorage.setItem('theme', theme);
    }

    applyTheme();

    // 監聽系統偏好變化
    if (theme === 'system') {
      mediaQuery.addEventListener('change', applyTheme);
      return () => mediaQuery.removeEventListener('change', applyTheme);
    }
  }, [theme]);

  return { theme, setTheme };
}

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();

  const options: { value: Theme; label: string }[] = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'system', label: 'System' },
  ];

  return (
    <div className="flex items-center gap-1 rounded-lg border border-border bg-surface-secondary p-1">
      {options.map(opt => (
        <button
          key={opt.value}
          onClick={() => setTheme(opt.value)}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-all
            ${theme === opt.value
              ? 'bg-surface text-on-surface shadow-sm'
              : 'text-on-surface-secondary hover:text-on-surface'
            }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
```

### Step 9: 深色模式下的圖片與媒體處理

```html
<!-- 方法一：根據主題顯示不同圖片 -->
<picture>
  <source srcset="/logo-dark.svg" media="(prefers-color-scheme: dark)" />
  <img src="/logo-light.svg" alt="Logo" class="h-8" />
</picture>

<!-- 方法二：使用 dark: 切換圖片（selector 策略） -->
<img src="/logo-light.svg" alt="Logo" class="h-8 dark:hidden" />
<img src="/logo-dark.svg" alt="Logo" class="hidden h-8 dark:block" />

<!-- 方法三：使用 CSS filter 反轉（簡單圖標適用） -->
<img src="/icon.svg" alt="Icon" class="h-6 dark:invert" />

<!-- 方法四：降低深色模式圖片亮度（照片適用） -->
<img src="/photo.jpg" alt="Photo" class="dark:brightness-90 dark:contrast-105" />
```

### Step 10: 設計深色模式的最佳實踐

```html
<!--
  深色模式設計原則：

  1. 不要簡單反轉黑白
     ❌ bg-white -> bg-black
     ✅ bg-white -> bg-gray-900 (柔和的深色)

  2. 降低文字對比度
     ❌ text-gray-900 -> text-white
     ✅ text-gray-900 -> text-gray-100 (稍微降低)

  3. 降低彩色的飽和度
     ❌ bg-blue-600 -> bg-blue-600 (保持不變太亮)
     ✅ bg-blue-600 -> bg-blue-500 (稍微提亮以補償背景)

  4. 陰影改用減淡的顏色
     ❌ shadow-lg (同一個黑色陰影在深色背景上不明顯)
     ✅ dark:shadow-gray-900/30 (更深的陰影)

  5. 邊框要微妙
     ❌ border-gray-200 -> border-gray-200 (太亮)
     ✅ border-gray-200 -> border-gray-700 (深色但可見)
-->

<!-- 實際示範 -->
<div class="rounded-xl border border-gray-200 bg-white p-6 shadow-md
            dark:border-gray-700 dark:bg-gray-800 dark:shadow-gray-900/30">
  <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">
    Well-designed Dark Mode
  </h2>
  <p class="mt-2 text-gray-600 dark:text-gray-400">
    注意邊框、陰影、文字顏色在深色模式的細微調整。
  </p>
  <button class="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-white
                 hover:bg-blue-700
                 dark:bg-blue-500 dark:hover:bg-blue-400">
    Action
  </button>
</div>
```

## Hands-on Lab

### Foundation 基礎練習

**任務：** 實現一個深色模式的卡片元件。

需求：
- 卡片有標題、描述、圖片、按鈕
- 使用 `dark:` 變體為每個元素設定深色模式顏色
- 使用 media 策略（預設），跟隨系統偏好
- 在系統偏好切換時自動變更

**驗收清單：**
- [ ] 亮色模式下卡片樣式正確（白色背景、深色文字）
- [ ] 深色模式下卡片樣式正確（深色背景、淺色文字）
- [ ] 按鈕在兩種模式下都有正確的 hover 效果
- [ ] 邊框和陰影在深色模式有適當調整

### Advanced 進階練習

**任務：** 建立一個 Light/Dark/System 三模式主題切換器。

需求：
- 切換到 selector 策略（`@custom-variant dark`）
- 三個按鈕：Light、Dark、System
- 選擇持久化到 localStorage
- System 模式隨系統偏好動態更新
- 防止頁面載入時的主題閃爍（inline script）
- 切換器本身也要支援深色模式樣式

**驗收清單：**
- [ ] 三個模式都能正確切換
- [ ] 重新整理頁面後保持選擇
- [ ] System 模式下改變系統偏好會即時更新
- [ ] 無主題閃爍（FOUC）
- [ ] 切換器 UI 在兩種模式下都美觀

### Challenge 挑戰練習

**任務：** 建立完整的多主題設計令牌系統。

需求：
- 定義語義化 CSS custom properties（surface、on-surface、primary、accent、border）
- 至少 4 種主題：Light、Dark、Forest、Ocean
- 透過 `@theme` 定義基礎令牌
- 透過 CSS 選擇器覆蓋不同主題的值
- 提供主題預覽面板
- 提供 React 版本的 `useTheme` hook

**驗收清單：**
- [ ] 4 種主題各自正確套用語義化顏色
- [ ] 切換主題不需要修改 HTML 中的 class（只改 data-theme）
- [ ] 主題預覽面板顯示每種主題的色彩方案
- [ ] React hook 正確管理主題狀態
- [ ] localStorage 持久化且無閃爍

## Reference Solution

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ch12 Lab - Dark Mode & Multi-Theme</title>
  <!-- 防止主題閃爍 -->
  <script>
    (function() {
      const theme = localStorage.getItem('theme') || 'system';
      const isDark = theme === 'dark' ||
        (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
      if (isDark) document.documentElement.classList.add('dark');
    })();
  </script>
  <style>
    @import "tailwindcss";

    @custom-variant dark (&:where(.dark, .dark *));

    @theme {
      --color-surface: #ffffff;
      --color-surface-alt: #f9fafb;
      --color-on-surface: #111827;
      --color-on-surface-muted: #6b7280;
      --color-primary: #2563eb;
      --color-primary-hover: #1d4ed8;
      --color-accent: #8b5cf6;
      --color-border: #e5e7eb;
    }

    .dark {
      --color-surface: #0f172a;
      --color-surface-alt: #1e293b;
      --color-on-surface: #f1f5f9;
      --color-on-surface-muted: #94a3b8;
      --color-primary: #3b82f6;
      --color-primary-hover: #60a5fa;
      --color-accent: #a78bfa;
      --color-border: #334155;
    }
  </style>
</head>
<body class="min-h-screen bg-surface text-on-surface transition-colors duration-300">

  <div class="mx-auto max-w-4xl px-4 py-12 sm:px-6">

    <!-- ====== Header with Theme Switcher ====== -->
    <header class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Dark Mode Demo</h1>

      <div class="flex items-center gap-1 rounded-lg border border-border bg-surface-alt p-1">
        <button data-theme-value="light"
                class="rounded-md px-3 py-1.5 text-sm font-medium text-on-surface-muted
                       hover:text-on-surface transition-all"
                id="btn-light">
          Light
        </button>
        <button data-theme-value="dark"
                class="rounded-md px-3 py-1.5 text-sm font-medium text-on-surface-muted
                       hover:text-on-surface transition-all"
                id="btn-dark">
          Dark
        </button>
        <button data-theme-value="system"
                class="rounded-md px-3 py-1.5 text-sm font-medium text-on-surface-muted
                       hover:text-on-surface transition-all"
                id="btn-system">
          System
        </button>
      </div>
    </header>

    <!-- ====== Card Grid ====== -->
    <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <!-- Card 1 -->
      <div class="group rounded-xl border border-border bg-surface p-6 shadow-sm transition-shadow hover:shadow-md">
        <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h3 class="mt-4 font-semibold text-on-surface">Performance</h3>
        <p class="mt-2 text-sm text-on-surface-muted">Built on the new Oxide engine for maximum speed.</p>
      </div>

      <!-- Card 2 -->
      <div class="group rounded-xl border border-border bg-surface p-6 shadow-sm transition-shadow hover:shadow-md">
        <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10 text-accent">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343" />
          </svg>
        </div>
        <h3 class="mt-4 font-semibold text-on-surface">Theming</h3>
        <p class="mt-2 text-sm text-on-surface-muted">CSS-first design tokens with @theme directive.</p>
      </div>

      <!-- Card 3 -->
      <div class="group rounded-xl border border-border bg-surface p-6 shadow-sm transition-shadow hover:shadow-md">
        <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-green-500/10 text-green-600 dark:text-green-400">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="mt-4 font-semibold text-on-surface">Accessible</h3>
        <p class="mt-2 text-sm text-on-surface-muted">Proper contrast ratios in all themes.</p>
      </div>
    </div>

    <!-- ====== Sample Form ====== -->
    <div class="mt-12 rounded-xl border border-border bg-surface p-8">
      <h2 class="text-lg font-semibold text-on-surface">Sample Form</h2>
      <div class="mt-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-on-surface">Name</label>
          <input
            type="text"
            placeholder="Enter your name"
            class="mt-1 w-full rounded-lg border border-border bg-surface px-4 py-2.5 text-on-surface
                   placeholder:text-on-surface-muted/60
                   focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20
                   transition-all"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-on-surface">Email</label>
          <input
            type="email"
            placeholder="your@email.com"
            class="mt-1 w-full rounded-lg border border-border bg-surface px-4 py-2.5 text-on-surface
                   placeholder:text-on-surface-muted/60
                   focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20
                   transition-all"
          />
        </div>
        <button class="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-white
                       hover:bg-primary-hover
                       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-surface
                       transition-colors">
          Submit
        </button>
      </div>
    </div>

  </div>

  <script>
    function getSystemTheme() {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function applyTheme(theme) {
      const root = document.documentElement;
      const resolved = theme === 'system' ? getSystemTheme() : theme;
      root.classList.toggle('dark', resolved === 'dark');
      localStorage.setItem('theme', theme);

      // Update active button styles
      document.querySelectorAll('[data-theme-value]').forEach(btn => {
        if (btn.dataset.themeValue === theme) {
          btn.classList.add('bg-surface', 'text-on-surface', 'shadow-sm');
          btn.classList.remove('text-on-surface-muted');
        } else {
          btn.classList.remove('bg-surface', 'text-on-surface', 'shadow-sm');
          btn.classList.add('text-on-surface-muted');
        }
      });
    }

    // Initialize
    const saved = localStorage.getItem('theme') || 'system';
    applyTheme(saved);

    // Listen for system changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (localStorage.getItem('theme') === 'system') applyTheme('system');
    });

    // Bind buttons
    document.querySelectorAll('[data-theme-value]').forEach(btn => {
      btn.addEventListener('click', () => applyTheme(btn.dataset.themeValue));
    });
  </script>

</body>
</html>
```

## Common Pitfalls

1. **主題閃爍（FOUC）：** 如果主題切換邏輯放在 `DOMContentLoaded` 或外部 JS 檔案，頁面會先以預設亮色渲染再閃爍切換。**解法：** 在 `<head>` 中使用阻塞式 `<script>` 在 DOM 渲染前設定 `.dark` class。

2. **忘記深色模式的 hover/focus 狀態：** 只設定 `dark:bg-gray-800` 但忘了 `dark:hover:bg-gray-700`，導致深色模式下互動回饋消失。**解法：** 每個有 `hover:` 的元素都需要對應的 `dark:hover:` 樣式。使用語義化 CSS custom properties 可以避免這個問題。

3. **CSS Custom Properties 未繼承：** 在 `:root` 定義的變數可以繼承到所有子元素，但如果在非根元素定義，只有子元素能存取。**解法：** 主題變數應該定義在 `:root` 或 `html` 選擇器上。

4. **v4 特定 --- @custom-variant 語法錯誤：** Tailwind CSS v4 的 `@custom-variant` 語法需要使用 `&:where()` 選擇器。常見錯誤是忘了 `&` 前綴或忘了包含後代選擇器（`.dark *` 部分）。正確語法是 `@custom-variant dark (&:where(.dark, .dark *));`。缺少 `.dark *` 會導致深色模式只套用在直接有 `.dark` class 的元素上。

5. **深色模式對比度不足：** 深色背景上使用太淺的文字（如 `dark:text-gray-600`），或深色背景色不夠深（如 `dark:bg-gray-300`），導致可讀性差。**解法：** 使用對比度檢查工具（如 Chrome DevTools 的對比度指示器）確保至少達到 WCAG AA 標準（4.5:1）。

## Checklist

- [ ] 理解 `media` 和 `selector` 兩種深色模式策略的差異。
- [ ] 能使用 `@custom-variant dark` 在 Tailwind CSS v4 中切換到手動控制策略。
- [ ] 能實現 Light/Dark/System 三模式主題切換器。
- [ ] 知道如何防止主題閃爍（在 `<head>` 加入 inline script）。
- [ ] 能使用 `@theme` + CSS custom properties 建立語義化顏色系統。
- [ ] 能透過 data attribute 實現多主題系統。
- [ ] 理解 v3 `darkMode: 'class'` 與 v4 `@custom-variant dark` 的對應關係。

## Further Reading (official links only)

- [Dark Mode - Tailwind CSS](https://tailwindcss.com/docs/dark-mode)
- [Customizing Colors - Tailwind CSS](https://tailwindcss.com/docs/customizing-colors)
- [Custom Variants - Tailwind CSS](https://tailwindcss.com/docs/adding-custom-styles#adding-custom-variants)
- [Tailwind CSS v4.0 - tailwindcss.com](https://tailwindcss.com/blog/tailwindcss-v4)
- [GitHub - tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss)
