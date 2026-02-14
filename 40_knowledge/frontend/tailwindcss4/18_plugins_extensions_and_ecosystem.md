---
title: "Plugins, Extensions, and Ecosystem / 插件、擴展與生態系"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "18"
level: advanced
stack: Tailwind CSS 4.1.x
prerequisites: [17_custom_utilities_and_variants_with_at_utility]
---

# Plugins, Extensions, and Ecosystem / 插件、擴展與生態系

## Goal

在前一章 [[17_custom_utilities_and_variants_with_at_utility]] 中，我們學會了使用 `@utility` 和 `@custom-variant` 從零開始定義自訂工具類和變體。但在大多數實際專案中，許多常見需求已經有現成的插件可以使用。Tailwind CSS 擁有豐富的官方插件和活躍的社群生態系。本章將深入介紹官方插件（`@tailwindcss/typography`、`@tailwindcss/forms`、`@tailwindcss/container-queries`）、社群工具（`tailwind-merge`、`clsx`、`cva`、DaisyUI、shadcn/ui），以及如何在 v4 中撰寫相容的插件。

值得注意的是，Tailwind CSS v4 將許多過去需要插件才能使用的功能內建化了。例如 container queries 現在已是核心功能的一部分，不再需要額外安裝插件。理解哪些功能已經內建、哪些仍需插件，是 v4 時代的重要知識。學完本章後，你將能評估並整合適當的插件來加速開發。在下一章 [[19_performance_optimization_and_production_build]] 中，我們將探討如何最佳化包含這些插件的 CSS 輸出，確保生產環境的效能。

## Prerequisites

- 已完成第 17 章，理解 `@utility` 和 `@custom-variant` 自訂機制。
- 熟悉 npm/pnpm 套件安裝與管理。
- 理解 Tailwind CSS v4 的 CSS-first 配置方式（`@import "tailwindcss"`）。
- 具備基礎 HTML/CSS 排版能力。
- 開發環境已設定 Tailwind CSS v4 + Vite。

## Core Concepts

### 1. Official Plugins vs Built-in Features / 官方插件與內建功能

Tailwind CSS v4 大幅擴展了核心功能，過去許多需要插件的功能現在已內建。理解這個區別對正確選用插件至關重要。

**v4 已內建（不需要插件）：**
- Container queries（`@container`、`@min-*`、`@max-*`）— 過去需要 `@tailwindcss/container-queries`。
- `aspect-ratio` 工具類。
- 更靈活的 grid 和 spacing 數值。

**仍需插件：**
- `@tailwindcss/typography` — prose 排版樣式。
- `@tailwindcss/forms` — 表單元素基礎樣式重置。

**何時使用官方插件：**
- 需要在 CMS 或 Markdown 產生的 HTML 中套用優美排版（typography）。
- 需要統一跨瀏覽器的表單元素基礎樣式（forms）。

**何時不使用官方插件：**
- 已經使用 UI 框架（如 shadcn/ui）處理了排版和表單樣式。
- 專案非常簡單，手寫少量樣式更輕量。
- container queries 等功能已內建，不需再安裝舊版插件。

### 2. Community Ecosystem Tools / 社群生態系工具

Tailwind CSS 社群提供了大量工具來解決常見的開發痛點。

**何時使用社群工具：**
- `tailwind-merge`：在 React/Svelte 元件中需要合併和覆蓋 Tailwind class 時。
- `clsx` / `class-variance-authority (cva)`：需要條件式 class 管理和元件變體系統時。
- DaisyUI / shadcn/ui：需要快速建立 UI，願意接受預設元件樣式。
- Tailwind UI：需要高品質、無障礙的商業級 UI 元件。

**何時不使用社群工具：**
- `tailwind-merge`：不涉及動態 class 合併的靜態頁面。
- `clsx` / `cva`：class 邏輯簡單，用三元運算子即可處理。
- DaisyUI：需要完全自訂的設計，不想被預設主題限制。
- shadcn/ui：不使用 React 的專案。

### 3. Writing v4-Compatible Plugins / 撰寫 v4 相容插件

v4 的插件 API 有重大變更。過去在 `tailwind.config.js` 中透過 JavaScript 定義的插件邏輯，現在優先使用 CSS-first 方式（`@utility`、`@custom-variant`）。

**何時撰寫 JavaScript 插件：**
- 需要動態計算大量工具類值（無法用靜態 CSS 表達）。
- 需要分發可安裝的 npm 套件給團隊或社群使用。
- 需要讀取外部配置來生成樣式。

**何時使用 CSS-first 方式取代插件：**
- 自訂工具類是靜態或基於 theme tokens 的。
- 只在單一專案使用，不需要發布為 npm 套件。
- 使用 `@utility` 和 `@custom-variant` 就能滿足需求。

### 4. UI Component Libraries / UI 元件庫

從 Tailwind CSS 生態系中選擇 UI 元件庫時，需要考量多個面向。

**何時使用元件庫（DaisyUI, shadcn/ui）：**
- 快速原型開發，需要立即可用的 UI 元件。
- 團隊沒有設計師，需要一致的設計語言。
- 內部工具或管理後台，設計客製化需求低。

**何時不使用元件庫：**
- 品牌設計高度客製化，元件庫的預設樣式反而是阻礙。
- 專案只需少量元件，引入整個元件庫造成不必要的依賴。
- 需要極致效能控制，第三方元件庫的 CSS 輸出可能過大。

## Step-by-step

### 步驟 1：安裝 @tailwindcss/typography 插件

```bash
npm install @tailwindcss/typography
```

在主 CSS 檔案中引入插件：

```css
/* src/app.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```

驗證：執行 `npm run dev`，確認無錯誤訊息。

### 步驟 2：使用 typography 插件的 prose 排版

建立一個部落格文章頁面：

```html
<!-- blog-post.html -->
<article class="prose prose-lg mx-auto max-w-3xl p-8">
  <h1>Tailwind CSS v4 的全新架構</h1>
  <p class="lead">
    Tailwind CSS v4 帶來了革命性的改變，包括 CSS-first 配置、Oxide 引擎，以及大幅簡化的開發體驗。
  </p>
  <h2>CSS-first 配置</h2>
  <p>
    v4 最大的改變是從 <code>tailwind.config.js</code> 遷移到純 CSS 配置。
    使用 <code>@theme</code> 指令定義設計令牌，使用 <code>@utility</code> 定義自訂工具類。
  </p>
  <blockquote>
    <p>「最好的配置方式就是用你已經熟悉的語言 — CSS。」</p>
  </blockquote>
  <h2>程式碼範例</h2>
  <pre><code>@import "tailwindcss";

@theme {
  --color-brand: oklch(0.7 0.15 250);
}</code></pre>
  <ul>
    <li>自動內容偵測，不再需要 <code>content: [...]</code></li>
    <li>Oxide 引擎帶來 5 倍建置速度提升</li>
    <li>原生 CSS cascade layers 支援</li>
  </ul>
  <h2>結論</h2>
  <p>
    想了解更多，請參考
    <a href="https://tailwindcss.com/docs">官方文件</a>。
  </p>
</article>
```

驗證：文章應自動套用優美的排版樣式，包含標題層級、段落間距、引用區塊樣式、清單縮排、連結色彩。

### 步驟 3：自訂 typography 插件的主題色彩

透過 CSS 變數覆寫 typography 的預設色彩：

```css
/* src/app.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";

@theme {
  --color-prose-headings: var(--color-slate-900);
  --color-prose-links: var(--color-blue-600);
  --color-prose-bold: var(--color-slate-800);
}
```

使用修飾前綴控制 prose 樣式：

```html
<!-- 深色模式支援 -->
<article class="prose prose-slate dark:prose-invert mx-auto max-w-3xl p-8">
  <h1>深色模式也能優美排版</h1>
  <p>使用 <code>dark:prose-invert</code> 自動切換深色排版。</p>
</article>

<!-- 不同尺寸 -->
<article class="prose prose-sm md:prose-base lg:prose-lg mx-auto">
  <h1>響應式排版尺寸</h1>
  <p>根據螢幕大小自動調整排版密度。</p>
</article>
```

驗證：深色模式下文字和背景色應正確反轉。不同螢幕尺寸下排版大小應有所不同。

### 步驟 4：安裝並使用 @tailwindcss/forms

```bash
npm install @tailwindcss/forms
```

```css
/* src/app.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
```

建立表單頁面：

```html
<form class="max-w-md mx-auto space-y-6 p-8">
  <div>
    <label for="name" class="block text-sm font-medium text-gray-700">姓名</label>
    <input
      type="text"
      id="name"
      class="mt-1 block w-full rounded-md border-gray-300
             shadow-sm focus:border-blue-500 focus:ring-blue-500"
    />
  </div>
  <div>
    <label for="email" class="block text-sm font-medium text-gray-700">電子郵件</label>
    <input
      type="email"
      id="email"
      class="mt-1 block w-full rounded-md border-gray-300
             shadow-sm focus:border-blue-500 focus:ring-blue-500"
    />
  </div>
  <div>
    <label for="category" class="block text-sm font-medium text-gray-700">分類</label>
    <select
      id="category"
      class="mt-1 block w-full rounded-md border-gray-300
             shadow-sm focus:border-blue-500 focus:ring-blue-500"
    >
      <option>技術</option>
      <option>設計</option>
      <option>管理</option>
    </select>
  </div>
  <div class="flex items-center gap-2">
    <input
      type="checkbox"
      id="agree"
      class="rounded border-gray-300 text-blue-600
             focus:ring-blue-500"
    />
    <label for="agree" class="text-sm text-gray-700">我同意服務條款</label>
  </div>
  <button
    type="submit"
    class="w-full rounded-md bg-blue-600 px-4 py-2 text-white
           hover:bg-blue-700 focus:outline-none focus:ring-2
           focus:ring-blue-500 focus:ring-offset-2"
  >
    送出
  </button>
</form>
```

驗證：表單元素應有統一的基礎樣式，input 的 focus 狀態應有藍色 ring。

### 步驟 5：安裝和使用 tailwind-merge

```bash
npm install tailwind-merge
```

tailwind-merge 用於在元件中智慧合併 Tailwind class，自動處理衝突：

```tsx
// utils/cn.ts
import { twMerge } from "tailwind-merge";

export function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(inputs.filter(Boolean).join(" "));
}
```

```tsx
// 使用範例：元件接受外部 className 時自動合併
type ButtonProps = {
  className?: string;
  children: React.ReactNode;
};

function Button({ className, children }: ButtonProps) {
  return (
    <button
      className={cn(
        "rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700",
        className // 外部傳入的 class 會覆蓋衝突的內部 class
      )}
    >
      {children}
    </button>
  );
}

// 使用時：bg-red-600 會覆蓋 bg-blue-600
<Button className="bg-red-600">紅色按鈕</Button>
```

驗證：`bg-red-600` 應成功覆蓋 `bg-blue-600`，而非兩者並存導致衝突。

### 步驟 6：使用 clsx 進行條件式 class 管理

```bash
npm install clsx
```

```tsx
// utils/cn.ts（升級版：clsx + tailwind-merge）
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

```tsx
// 條件式 class 使用範例
type AlertProps = {
  variant: "info" | "success" | "warning" | "error";
  children: React.ReactNode;
};

function Alert({ variant, children }: AlertProps) {
  return (
    <div
      className={cn(
        "rounded-lg border px-4 py-3 text-sm",
        {
          "border-blue-200 bg-blue-50 text-blue-800": variant === "info",
          "border-green-200 bg-green-50 text-green-800": variant === "success",
          "border-yellow-200 bg-yellow-50 text-yellow-800": variant === "warning",
          "border-red-200 bg-red-50 text-red-800": variant === "error",
        }
      )}
    >
      {children}
    </div>
  );
}
```

驗證：傳入不同 variant 應顯示對應顏色的警告框。

### 步驟 7：使用 Class Variance Authority (cva) 建立元件變體

```bash
npm install class-variance-authority
```

```tsx
// components/Button.tsx
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../utils/cn";

const buttonVariants = cva(
  // 基礎樣式
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
        secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-400",
        destructive: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
        outline: "border border-gray-300 bg-transparent hover:bg-gray-50 focus:ring-gray-400",
        ghost: "bg-transparent hover:bg-gray-100 focus:ring-gray-400",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-base",
        lg: "h-12 px-6 text-lg",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & {
    className?: string;
  };

export function Button({ variant, size, className, ...props }: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  );
}
```

使用方式：

```tsx
<Button variant="primary" size="lg">主要按鈕</Button>
<Button variant="destructive" size="sm">刪除</Button>
<Button variant="outline">外框按鈕</Button>
<Button variant="ghost" className="text-blue-600">幽靈按鈕</Button>
```

驗證：每個變體和尺寸組合應產生正確的視覺效果。外部 className 應能正確覆蓋。

### 步驟 8：了解 DaisyUI 和 shadcn/ui 的定位

**DaisyUI** — 基於 Tailwind 的 CSS-only 元件庫：

```bash
npm install daisyui
```

```css
/* src/app.css */
@import "tailwindcss";
@plugin "daisyui";
```

```html
<!-- DaisyUI 元件範例 -->
<button class="btn btn-primary">Primary</button>
<div class="card bg-base-100 shadow-xl w-96">
  <div class="card-body">
    <h2 class="card-title">DaisyUI 卡片</h2>
    <p>自動套用主題化樣式。</p>
    <div class="card-actions justify-end">
      <button class="btn btn-primary">了解更多</button>
    </div>
  </div>
</div>
```

**shadcn/ui** — 複製到專案中的 React 元件集合（非 npm 套件）：

```bash
# 在 Next.js 專案中初始化 shadcn/ui
npx shadcn@latest init
npx shadcn@latest add button card dialog
```

shadcn/ui 的元件會直接複製到你的 `components/ui/` 目錄中，你擁有完全的控制權。

驗證：安裝後確認元件可以正常渲染，且主題色彩與專案一致。

### 步驟 9：撰寫 v4 相容的 JavaScript 插件

雖然 v4 推薦 CSS-first 方式，但 JavaScript 插件仍然受支援：

```js
// plugins/text-stroke.js
import plugin from "tailwindcss/plugin";

export default plugin(function ({ matchUtilities, theme }) {
  matchUtilities(
    {
      "text-stroke": (value) => ({
        "-webkit-text-stroke-width": value,
      }),
    },
    {
      values: theme("textStrokeWidth", {
        thin: "1px",
        medium: "2px",
        thick: "4px",
      }),
    }
  );

  matchUtilities(
    {
      "text-stroke": (value) => ({
        "-webkit-text-stroke-color": value,
      }),
    },
    {
      values: theme("colors"),
      type: "color",
    }
  );
});
```

在 CSS 中引入：

```css
/* src/app.css */
@import "tailwindcss";
@plugin "./plugins/text-stroke.js";
```

```html
<h1 class="text-6xl font-bold text-stroke-thick text-stroke-blue-500 text-transparent">
  描邊文字效果
</h1>
```

驗證：文字應只顯示描邊而無填充色。

### 步驟 10：建立插件選用決策清單

在實際專案中，使用以下決策流程選用插件：

```
1. 需求確認
   └─ 此功能 Tailwind v4 是否已內建？
      ├─ 是 → 直接使用，不安裝插件
      └─ 否 → 繼續

2. 自訂 vs 插件
   └─ 用 @utility / @custom-variant 能否實現？
      ├─ 是 → 使用 CSS-first 方式
      └─ 否 → 尋找插件

3. 插件來源
   └─ 官方插件是否可用？
      ├─ 是 → 優先使用官方插件
      └─ 否 → 評估社群插件

4. 社群插件評估標準
   ├─ v4 相容性（是否標明支援 v4）
   ├─ 維護活躍度（最近更新時間、issue 回應速度）
   ├─ 下載量和星星數
   ├─ 打包體積影響
   └─ TypeScript 支援
```

驗證：在新增任何插件前，用此清單評估一次，並記錄決策理由。

## Hands-on Lab

### Foundation / 基礎練習

**任務：安裝 @tailwindcss/typography 並建立部落格文章頁面**

1. 安裝 `@tailwindcss/typography` 插件。
2. 在 CSS 中使用 `@plugin` 引入。
3. 建立一個包含標題、段落、引用、程式碼區塊、清單的部落格文章頁面。
4. 套用 `prose` class 並確認排版效果。
5. 加入 `dark:prose-invert` 深色模式支援。

**驗收清單：**
- [ ] `npm ls @tailwindcss/typography` 確認安裝成功。
- [ ] 文章標題有正確的層級大小和間距。
- [ ] 引用區塊有左側邊線和斜體樣式。
- [ ] 程式碼區塊有背景色和等寬字型。
- [ ] 深色模式下 `prose-invert` 正確反轉色彩。

### Advanced / 進階練習

**任務：整合 clsx + tailwind-merge 建立 cn() 工具函式**

1. 安裝 `clsx` 和 `tailwind-merge`。
2. 建立 `utils/cn.ts` 工具函式。
3. 建立一個 `Alert` 元件，支援 `info`、`success`、`warning`、`error` 四種變體。
4. 元件接受外部 `className` 並正確合併。
5. 建立一個展示頁面顯示四種 Alert 變體。

**驗收清單：**
- [ ] `cn("bg-red-500", "bg-blue-500")` 回傳 `"bg-blue-500"`（後者覆蓋前者）。
- [ ] `cn("px-4", false && "hidden")` 正確忽略 false 值。
- [ ] 四種 Alert 變體各自顯示正確的顏色和圖示。
- [ ] 外部傳入 `className="mt-8"` 能正確附加到元件上。
- [ ] TypeScript 型別無錯誤。

### Challenge / 挑戰練習

**任務：使用 cva 建立完整的 Button 元件變體系統**

1. 安裝 `class-variance-authority`。
2. 使用 `cva` 定義 Button，支援 5 種 variant 和 3 種 size。
3. 支援 `disabled` 狀態自動套用對應樣式。
4. 支援 `loading` 狀態（顯示 spinner 並禁用互動）。
5. 支援 `asChild` 模式（渲染為 `<a>` 而非 `<button>`）。
6. 建立展示頁面，展示所有變體 x 尺寸的排列組合。

**驗收清單：**
- [ ] 5 variant x 3 size = 15 種組合全部正確顯示。
- [ ] `disabled` 狀態有半透明和禁用游標效果。
- [ ] `loading` 狀態顯示 spinner 動畫且不可點擊。
- [ ] `asChild` 模式渲染為 `<a>` 標籤但保留 Button 樣式。
- [ ] 外部 `className` 能覆蓋預設樣式（如自訂背景色）。
- [ ] 所有元件通過 TypeScript 型別檢查。

## Reference Solution

以下是 Foundation 練習的完整參考解答：

```css
/* src/app.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```

```html
<!-- blog.html -->
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Blog - Tailwind Typography Demo</title>
  <link rel="stylesheet" href="/src/app.css" />
</head>
<body class="bg-white dark:bg-gray-950 min-h-screen py-12">

  <article class="prose prose-lg prose-slate dark:prose-invert mx-auto max-w-3xl px-6">

    <header>
      <p class="text-sm text-gray-500 dark:text-gray-400">2026-02-14 ・ 技術文章</p>
      <h1>深入理解 Tailwind CSS v4 的 CSS-first 架構</h1>
      <p class="lead">
        Tailwind CSS v4 從根本上重新設計了配置方式。
        本文將從哲學、實作、效能三個面向分析這次改變的意義。
      </p>
    </header>

    <h2>為什麼要 CSS-first？</h2>
    <p>
      在 v3 以前，Tailwind 的配置全部寫在 <code>tailwind.config.js</code>，
      這意味著 CSS 框架的配置用 JavaScript 撰寫。v4 的創新在於：
      <strong>用 CSS 配置 CSS 工具</strong>。
    </p>

    <blockquote>
      <p>
        「開發者不應該為了修改一個顏色而去編輯 JavaScript 檔案。」
        — Tailwind CSS 團隊
      </p>
    </blockquote>

    <h2>核心改變一覽</h2>
    <ol>
      <li><code>@import "tailwindcss"</code> 取代三行 <code>@tailwind</code> 指令。</li>
      <li><code>@theme</code> 取代 <code>theme.extend</code> 配置。</li>
      <li><code>@utility</code> 取代 <code>addUtilities()</code> 插件 API。</li>
      <li>自動內容偵測取代 <code>content: [...]</code> 配置。</li>
    </ol>

    <h2>程式碼範例</h2>
    <pre><code>/* v3 的方式 */
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: '#3b82f6',
      },
    },
  },
  content: ['./src/**/*.{html,js}'],
};

/* v4 的方式 */
/* app.css */
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.62 0.19 250);
}</code></pre>

    <h2>效能提升</h2>
    <p>
      v4 使用 Rust 撰寫的 Oxide 引擎：
    </p>
    <ul>
      <li>完整建置速度提升 <strong>5 倍</strong>。</li>
      <li>增量建置速度提升 <strong>100 倍</strong>。</li>
      <li>JIT 引擎始終開啟，無需手動啟用。</li>
    </ul>

    <h2>結論</h2>
    <p>
      CSS-first 不只是語法改變，更是開發哲學的轉換。
      詳細遷移指南請參考 <a href="https://tailwindcss.com/docs/upgrade-guide">官方升級指南</a>。
    </p>

    <hr />

    <footer class="not-prose text-sm text-gray-500 dark:text-gray-400 mt-8">
      <p>作者：前端開發團隊 ・ 最後更新 2026-02-14</p>
    </footer>

  </article>

</body>
</html>
```

以下是 Challenge 練習（cva Button）的完整參考解答：

```tsx
// utils/cn.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

```tsx
// components/Button.tsx
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../utils/cn";
import { forwardRef, type ButtonHTMLAttributes, type AnchorHTMLAttributes } from "react";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
        secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-400",
        destructive: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
        outline:
          "border border-gray-300 bg-transparent text-gray-700 hover:bg-gray-50 focus:ring-gray-400",
        ghost: "bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-400",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-base",
        lg: "h-12 px-6 text-lg",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

function Spinner() {
  return (
    <svg
      className="h-4 w-4 animate-spin"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  );
}

type ButtonBaseProps = VariantProps<typeof buttonVariants> & {
  loading?: boolean;
  className?: string;
};

type ButtonAsButton = ButtonBaseProps &
  ButtonHTMLAttributes<HTMLButtonElement> & {
    asChild?: false;
    href?: never;
  };

type ButtonAsLink = ButtonBaseProps &
  AnchorHTMLAttributes<HTMLAnchorElement> & {
    asChild: true;
    href: string;
  };

type ButtonProps = ButtonAsButton | ButtonAsLink;

export const Button = forwardRef<HTMLButtonElement | HTMLAnchorElement, ButtonProps>(
  function Button(props, ref) {
    const { variant, size, loading, className, asChild, ...rest } = props;
    const classes = cn(
      buttonVariants({ variant, size }),
      loading && "cursor-wait",
      className
    );

    if (asChild && "href" in rest) {
      const { href, children, ...anchorProps } = rest as ButtonAsLink;
      return (
        <a
          ref={ref as React.Ref<HTMLAnchorElement>}
          href={href}
          className={classes}
          {...anchorProps}
        >
          {loading && <Spinner />}
          {children}
        </a>
      );
    }

    const { children, disabled, ...buttonProps } = rest as ButtonAsButton;
    return (
      <button
        ref={ref as React.Ref<HTMLButtonElement>}
        className={classes}
        disabled={disabled || loading}
        {...buttonProps}
      >
        {loading && <Spinner />}
        {children}
      </button>
    );
  }
);

export { buttonVariants };
```

```tsx
// app/demo/page.tsx - 展示頁面
import { Button } from "../../components/Button";

const variants = ["primary", "secondary", "destructive", "outline", "ghost"] as const;
const sizes = ["sm", "md", "lg"] as const;

export default function ButtonDemoPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-12 p-8">
      <h1 className="text-3xl font-bold">Button 元件變體展示</h1>

      {/* 所有 variant x size 組合 */}
      <section className="space-y-6">
        <h2 className="text-xl font-semibold">Variant x Size 矩陣</h2>
        <div className="space-y-4">
          {variants.map((variant) => (
            <div key={variant} className="flex items-center gap-4">
              <span className="w-24 text-sm font-mono text-gray-500">{variant}</span>
              {sizes.map((size) => (
                <Button key={size} variant={variant} size={size}>
                  {size.toUpperCase()}
                </Button>
              ))}
            </div>
          ))}
        </div>
      </section>

      {/* 特殊狀態 */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">特殊狀態</h2>
        <div className="flex items-center gap-4">
          <Button disabled>Disabled</Button>
          <Button loading>Loading</Button>
          <Button variant="destructive" loading>
            刪除中
          </Button>
          <Button asChild href="/docs" variant="outline">
            連結按鈕
          </Button>
        </div>
      </section>

      {/* className 覆蓋 */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">className 覆蓋</h2>
        <div className="flex items-center gap-4">
          <Button className="bg-emerald-600 hover:bg-emerald-700">
            自訂綠色
          </Button>
          <Button className="rounded-full">
            圓形按鈕
          </Button>
        </div>
      </section>
    </div>
  );
}
```

## Common Pitfalls

### 1. v4 特有：使用 v3 的 require() 方式引入插件

v4 使用 `@plugin` 指令引入插件，而非 v3 的 `require()` + `tailwind.config.js`。

```css
/* 錯誤：v3 方式，在 v4 中不適用 */
/* tailwind.config.js */
/* plugins: [require('@tailwindcss/typography')] */

/* 正確：v4 方式，在 CSS 中使用 @plugin */
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```

### 2. 安裝已內建的 container-queries 插件

v4 已將 container queries 內建。安裝 `@tailwindcss/container-queries` 是多餘的。

```bash
# 不需要安裝
# npm install @tailwindcss/container-queries

# 直接使用即可
```

```html
<!-- v4 原生支援，不需要插件 -->
<div class="@container">
  <div class="@sm:flex @lg:grid @lg:grid-cols-2">
    原生 container query 支援
  </div>
</div>
```

### 3. tailwind-merge 未正確處理自訂工具類

`tailwind-merge` 預設只認識 Tailwind 內建工具類。自訂的 `@utility` 可能不會被正確合併。

```tsx
import { extendTailwindMerge } from "tailwind-merge";

// 錯誤：預設 twMerge 不認識 glass-* 自訂工具類
// twMerge("glass-sm glass-lg") 可能保留兩者

// 正確：擴展 tailwind-merge 配置
const customTwMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      "glass": [{ "glass": ["sm", "md", "lg", "none"] }],
      "text-shadow": [{ "text-shadow": ["sm", "md", "lg", "xl", "none"] }],
    },
  },
});
```

### 4. cva 元件中忘記傳遞 defaultVariants

未設定 `defaultVariants` 時，不傳 variant prop 的元件可能沒有任何樣式。

```tsx
// 錯誤：缺少 defaultVariants
const buttonVariants = cva("rounded-md font-medium", {
  variants: {
    variant: {
      primary: "bg-blue-600 text-white",
      secondary: "bg-gray-200 text-gray-900",
    },
  },
  // 沒有 defaultVariants，<Button /> 不會有 variant 樣式
});

// 正確：設定 defaultVariants
const buttonVariants = cva("rounded-md font-medium", {
  variants: {
    variant: {
      primary: "bg-blue-600 text-white",
      secondary: "bg-gray-200 text-gray-900",
    },
  },
  defaultVariants: {
    variant: "primary", // 未傳 variant 時使用 primary
  },
});
```

### 5. prose 與 Tailwind 工具類衝突

`prose` class 會為子元素設定樣式，可能與直接使用的 Tailwind 工具類衝突。使用 `not-prose` class 來排除特定區塊。

```html
<!-- 錯誤：prose 的連結色會覆蓋自訂色 -->
<article class="prose">
  <a class="text-red-500" href="#">這可能不是紅色</a>
</article>

<!-- 正確：使用 not-prose 排除 -->
<article class="prose">
  <p>這段文字受 prose 控制。</p>
  <div class="not-prose">
    <a class="text-red-500" href="#">這段不受 prose 影響，保證是紅色</a>
  </div>
</article>
```

## Checklist

- [ ] 能使用 `@plugin` 在 CSS 中引入官方插件（typography, forms）。
- [ ] 能使用 `prose` class 建立優美的文章排版，支援 `dark:prose-invert`。
- [ ] 能使用 `clsx` + `tailwind-merge` 建立 `cn()` 工具函式。
- [ ] 能使用 `cva` 定義元件變體系統（variant + size + defaultVariants）。
- [ ] 理解哪些功能在 v4 已內建（container queries），不需安裝插件。
- [ ] 能評估社群插件的品質和 v4 相容性。
- [ ] 能在需要時使用 `not-prose` 排除 typography 插件的影響。

## Further Reading (official links only)

- [Tailwind CSS Plugins](https://tailwindcss.com/docs/plugins)
- [@tailwindcss/typography](https://tailwindcss.com/docs/typography-plugin)
- [@tailwindcss/forms](https://github.com/tailwindlabs/tailwindcss-forms)
- [Tailwind CSS v4.0 Release - Plugin Changes](https://tailwindcss.com/blog/tailwindcss-v4)
- [Tailwind CSS GitHub Repository](https://github.com/tailwindlabs/tailwindcss)
- [Tailwind CSS Container Queries (Built-in)](https://tailwindcss.com/docs/container-queries)
