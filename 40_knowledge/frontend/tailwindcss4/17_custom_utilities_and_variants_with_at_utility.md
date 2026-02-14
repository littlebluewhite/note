---
title: "Custom Utilities and Variants with @utility / 使用 @utility 自訂工具類與變體"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "17"
level: advanced
stack: Tailwind CSS 4.1.x
prerequisites: [16_theme_directive_and_design_tokens]
---

# Custom Utilities and Variants with @utility / 使用 @utility 自訂工具類與變體

## Goal

在前一章 [[16_theme_configuration]] 中，我們學會了使用 `@theme` 指令定義設計令牌（design tokens），建立了一套統一的色彩、間距、字型系統。但 `@theme` 只是定義「值」，真正讓 Tailwind CSS 發揮威力的是將這些值應用到「工具類」上。當內建的工具類無法滿足專案需求時，我們需要自訂工具類。本章將深入介紹 Tailwind CSS v4 的 `@utility` 指令，它允許你直接在 CSS 中定義自訂工具類，這是 v4 的全新方式，取代了 v3 時期必須透過 JavaScript `addUtilities()` plugin API 才能完成的功能。

除了 `@utility`，本章也會介紹 `@custom-variant` 指令，讓你能定義自訂變體（variant），例如針對特定 HTML 屬性狀態或瀏覽器特性的條件式樣式。學完本章後，你將能根據專案需求靈活擴展 Tailwind 的工具類系統，撰寫具有 responsive 和 stateful 能力的自訂工具類。在下一章 [[18_plugins_extensions_and_ecosystem]] 中，我們將進一步探討如何透過官方與社群插件擴展 Tailwind 的完整生態系。

## Prerequisites

- 已完成第 16 章，理解 `@theme` 指令與設計令牌配置。
- 熟悉 CSS 自訂屬性（custom properties）與 CSS cascade layers。
- 理解 Tailwind CSS 工具類的運作機制（class 名稱對應 CSS 屬性）。
- 具備基礎 CSS 選擇器知識（pseudo-classes, attribute selectors）。
- 開發環境已設定 Tailwind CSS v4 + Vite（參考第 02 章）。

## Core Concepts

### 1. @utility Directive / @utility 指令

`@utility` 是 Tailwind CSS v4 的核心新功能，讓你直接在 CSS 檔案中定義自訂工具類。定義後的工具類會自動獲得 Tailwind 的完整功能支援，包括 responsive 前綴（`md:`, `lg:` 等）、狀態變體（`hover:`, `focus:` 等），以及正確的 CSS cascade layer 排序。

**何時使用 @utility：**
- 需要一個可重用的單一用途工具類，且內建工具類不包含此功能。
- 需要自訂工具類支援 responsive 和 stateful 變體。
- 需要定義需要接受任意值（arbitrary value）的工具類。
- 專案有特殊的 CSS 效果需求（如 text-shadow、scrollbar 隱藏等）。

**何時不使用 @utility：**
- 內建工具類已能滿足需求時，避免重複定義。
- 需要組合多個屬性的複合樣式時，考慮使用 component extraction（元件抽取）。
- 只是在少數地方使用一次，直接寫 arbitrary values 如 `[text-shadow:0_2px_4px_rgba(0,0,0,0.3)]` 即可。

### 2. @utility vs @apply vs Component Extraction / 三種自訂方式比較

Tailwind CSS 提供多種方式讓你擴展或自訂樣式，理解三者的適用場景至關重要。

**何時使用 @utility：**
- 定義全新的單一用途工具類（一個 class 對應一到兩個 CSS 屬性）。
- 需要在整個專案中以工具類形式重複使用。
- 需要支援 responsive、hover 等變體。

**何時使用 @apply：**
- 在第三方元件或 CMS 產生的 HTML 中，無法直接修改 class 屬性。
- 在 Svelte scoped `<style>` 區塊中整合 Tailwind 工具類到傳統 CSS 選擇器。
- 注意：Tailwind 官方不建議過度使用 `@apply`，它會抵銷 utility-first 的優勢。

**何時使用 Component Extraction（元件抽取）：**
- 一組工具類組合需要在多處重複使用（如 Button、Card 元件）。
- 組合涉及 3 個以上的 CSS 屬性。
- 在 React/Svelte 等框架中，用元件封裝是更好的抽象層級。

### 3. @custom-variant Directive / @custom-variant 指令

`@custom-variant` 讓你定義自訂變體，以便在工具類前方使用條件式前綴。這在需要針對特定 HTML 屬性、瀏覽器狀態、或容器狀態套用樣式時非常有用。

**何時使用 @custom-variant：**
- 需要針對自訂 data 屬性（如 `data-state="open"`）套用樣式。
- 需要針對瀏覽器特定功能（如 `@supports`）建立變體。
- 需要為第三方套件的 HTML 結構建立條件式樣式。
- 需要複合變體（combining selectors）。

**何時不使用 @custom-variant：**
- Tailwind 內建變體已涵蓋的情況（`hover:`, `focus:`, `group-hover:`, `data-[state=open]:` 等）。
- 只在一個地方使用，使用 arbitrary variant `[&[data-active]]:` 更直接。
- 過於複雜的選擇器邏輯，應考慮在 JavaScript/框架層級處理。

### 4. Functional Utilities with Values / 函式型工具類（接受值的工具類）

`@utility` 不僅可以定義靜態工具類，還能定義接受動態值的函式型工具類。透過 `--value()` 函式，你的工具類可以從 theme 取值或接受任意值。

**何時使用函式型 @utility：**
- 需要一組同名但不同級距的工具類（如 `text-shadow-sm`, `text-shadow-md`, `text-shadow-lg`）。
- 需要工具類能接受 arbitrary values（如 `text-shadow-[0_4px_8px_red]`）。
- 需要與 `@theme` 定義的 design tokens 整合。

**何時不使用函式型 @utility：**
- 工具類只有一種固定效果（如 `scrollbar-hide`），使用靜態 `@utility` 即可。
- 已有內建工具類提供相同功能（如 `shadow-*` 系列）。

## Step-by-step

### 步驟 1：建立專案結構

確認你有一個 Tailwind CSS v4 + Vite 專案。在主要 CSS 檔案中確認已有正確的 import：

```css
/* src/app.css */
@import "tailwindcss";
```

建立一個獨立的自訂工具類檔案：

```css
/* src/custom-utilities.css */
/* 我們將在此檔案定義所有自訂工具類 */
```

在主 CSS 檔案中引入：

```css
/* src/app.css */
@import "tailwindcss";
@import "./custom-utilities.css";
```

驗證：開啟瀏覽器 DevTools，確認 Tailwind 樣式正常載入。

### 步驟 2：定義第一個靜態 @utility

在 `custom-utilities.css` 中定義一個隱藏 scrollbar 的工具類：

```css
/* src/custom-utilities.css */
@utility scrollbar-hide {
  -ms-overflow-style: none;     /* IE, Edge */
  scrollbar-width: none;        /* Firefox */
  &::-webkit-scrollbar {
    display: none;              /* Chrome, Safari, Opera */
  }
}
```

在 HTML 中使用：

```html
<div class="h-64 overflow-y-auto scrollbar-hide">
  <p>這個容器可以捲動，但看不到捲軸。</p>
  <!-- 加入足夠多的內容使其可捲動 -->
</div>
```

驗證：容器應可捲動但不顯示捲軸。打開 DevTools 確認 CSS 規則已正確生成。

### 步驟 3：定義 text-shadow 靜態工具類系列

定義一組不同強度的 text-shadow 工具類：

```css
/* src/custom-utilities.css */
@utility text-shadow-sm {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

@utility text-shadow-md {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

@utility text-shadow-lg {
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3),
               0 2px 4px rgba(0, 0, 0, 0.2);
}

@utility text-shadow-none {
  text-shadow: none;
}
```

在 HTML 中使用：

```html
<h1 class="text-4xl font-bold text-shadow-lg text-white">
  Hero 標題帶有陰影效果
</h1>
<p class="text-shadow-sm text-gray-700">
  副標題帶有輕微陰影
</p>
```

驗證：文字應顯示對應強度的陰影效果。

### 步驟 4：使用函式型 @utility 接受動態值

將 text-shadow 改為函式型工具類，接受自訂 theme 值：

```css
/* src/app.css */
@import "tailwindcss";
@import "./custom-utilities.css";

@theme {
  --text-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
  --text-shadow-md: 0 2px 4px rgba(0, 0, 0, 0.3);
  --text-shadow-lg: 0 4px 8px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(0, 0, 0, 0.2);
  --text-shadow-xl: 0 8px 16px rgba(0, 0, 0, 0.4), 0 4px 8px rgba(0, 0, 0, 0.2);
}
```

```css
/* src/custom-utilities.css */
@utility text-shadow-* {
  text-shadow: --value(--text-shadow-*);
}

@utility text-shadow-none {
  text-shadow: none;
}
```

使用方式：

```html
<!-- 使用 theme 定義的值 -->
<h1 class="text-shadow-lg">大陰影</h1>
<h2 class="text-shadow-sm">小陰影</h2>

<!-- 使用 arbitrary value -->
<h3 class="text-shadow-[0_2px_8px_blue]">藍色陰影</h3>
```

驗證：`text-shadow-sm`, `text-shadow-md`, `text-shadow-lg`, `text-shadow-xl` 都應正常運作，且 arbitrary value 也能使用。

### 步驟 5：確認 responsive 和 stateful 變體自動支援

`@utility` 定義的工具類自動支援所有 Tailwind 變體：

```html
<!-- responsive：只在 md 以上顯示陰影 -->
<h1 class="md:text-shadow-lg">
  中螢幕以上才有陰影
</h1>

<!-- stateful：hover 時顯示陰影 -->
<button class="hover:text-shadow-md transition-all duration-200">
  滑鼠移入時出現陰影
</button>

<!-- dark mode：深色模式下使用不同陰影 -->
<h2 class="text-shadow-md dark:text-shadow-[0_2px_8px_rgba(255,255,255,0.3)]">
  亮暗模式不同陰影
</h2>

<!-- 組合：responsive + stateful -->
<p class="lg:hover:text-shadow-lg">
  大螢幕且 hover 時才有陰影
</p>
```

驗證：調整瀏覽器視窗大小確認 responsive 行為，滑鼠移入確認 hover 行為。

### 步驟 6：定義 @custom-variant

建立自訂變體，針對 `data-state` 屬性：

```css
/* src/custom-utilities.css */

/* 單一選擇器變體 */
@custom-variant data-open (&[data-state="open"]);

/* 使用區塊語法的複合變體 */
@custom-variant hocus {
  &:hover,
  &:focus-visible {
    @slot;
  }
}

/* 針對列印的變體 */
@custom-variant print {
  @media print {
    @slot;
  }
}
```

在 HTML 中使用：

```html
<!-- data-open 變體 -->
<details data-state="open">
  <summary class="data-open:bg-blue-100 data-open:text-blue-900 p-4 rounded">
    點擊展開
  </summary>
  <div class="p-4">展開的內容</div>
</details>

<!-- hocus 變體（hover + focus 合併） -->
<button class="bg-blue-500 text-white px-4 py-2 rounded hocus:bg-blue-700 hocus:ring-2">
  Hover 或 Focus 都會觸發
</button>

<!-- print 變體 -->
<nav class="print:hidden">導航列（列印時隱藏）</nav>
<article class="print:text-black print:bg-white">
  文章內容（列印時黑字白底）
</article>
```

驗證：透過 JavaScript 切換 `data-state` 屬性確認變體生效。使用瀏覽器列印預覽確認 print 變體。

### 步驟 7：建立進階自訂工具類 - CSS 漸層文字

定義一個漸層文字效果的工具類：

```css
/* src/custom-utilities.css */
@utility text-gradient {
  background: linear-gradient(135deg, var(--color-blue-500), var(--color-purple-600));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

@utility text-gradient-warm {
  background: linear-gradient(135deg, var(--color-orange-500), var(--color-red-600));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

```html
<h1 class="text-5xl font-extrabold text-gradient">
  漸層文字效果
</h1>
<h2 class="text-3xl font-bold text-gradient-warm">
  暖色漸層文字
</h2>
```

驗證：文字應呈現漸層色彩效果，而非純色。

### 步驟 8：建立帶有巢狀選擇器的自訂工具類

定義一個可以套用在父容器上的 prose-like 工具類：

```css
/* src/custom-utilities.css */
@utility content-links-styled {
  & a {
    color: var(--color-blue-600);
    text-decoration: underline;
    text-underline-offset: 2px;
  }
  & a:hover {
    color: var(--color-blue-800);
  }
}

@utility content-lists-styled {
  & ul {
    list-style-type: disc;
    padding-left: 1.5rem;
  }
  & ol {
    list-style-type: decimal;
    padding-left: 1.5rem;
  }
  & li {
    margin-bottom: 0.5rem;
  }
}
```

```html
<div class="content-links-styled content-lists-styled">
  <p>請參考 <a href="#">官方文件</a> 了解更多。</p>
  <ul>
    <li>第一項</li>
    <li>第二項，包含 <a href="#">連結</a></li>
    <li>第三項</li>
  </ul>
</div>
```

驗證：連結應自動帶有藍色和底線，清單應有正確的項目符號和縮排。

### 步驟 9：組合 @theme + @utility + @custom-variant 建立完整系統

將所有概念整合，建立一個完整的自訂工具類系統：

```css
/* src/app.css */
@import "tailwindcss";
@import "./custom-utilities.css";

@theme {
  --text-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.15);
  --text-shadow-md: 0 2px 4px rgba(0, 0, 0, 0.25);
  --text-shadow-lg: 0 4px 8px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(0, 0, 0, 0.15);

  --glass-blur: 12px;
  --glass-opacity: 0.15;
}
```

```css
/* src/custom-utilities.css */

/* 函式型工具類 */
@utility text-shadow-* {
  text-shadow: --value(--text-shadow-*);
}
@utility text-shadow-none {
  text-shadow: none;
}

/* 靜態工具類 */
@utility scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}

@utility glass {
  backdrop-filter: blur(var(--glass-blur));
  background: rgba(255, 255, 255, var(--glass-opacity));
  border: 1px solid rgba(255, 255, 255, 0.2);
}

@utility text-gradient {
  background: linear-gradient(135deg, var(--color-blue-500), var(--color-purple-600));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 自訂變體 */
@custom-variant hocus {
  &:hover,
  &:focus-visible {
    @slot;
  }
}
@custom-variant data-open (&[data-state="open"]);
@custom-variant print {
  @media print {
    @slot;
  }
}
```

驗證：啟動開發伺服器，確認所有自訂工具類和變體在 HTML 中正常運作。

### 步驟 10：在 DevTools 中驗證 CSS 輸出

開啟瀏覽器 DevTools，檢查以下項目：

1. 自訂工具類被正確放置在 `@layer utilities` 中。
2. 使用 responsive 前綴（如 `md:text-shadow-lg`）時，media query 正確包裹。
3. 使用 stateful 前綴（如 `hover:glass`）時，pseudo-class 正確套用。
4. 自訂變體（如 `data-open:bg-blue-100`）產生正確的選擇器。
5. 未使用的自訂工具類不會出現在最終 CSS 輸出中（JIT 按需生成）。

驗證：在 DevTools Elements 面板中檢視元素，確認 CSS 規則來源為正確的 layer。

## Hands-on Lab

### Foundation / 基礎練習

**任務：建立 text-shadow 工具類系統**

1. 在 `@theme` 中定義 `--text-shadow-sm`, `--text-shadow-md`, `--text-shadow-lg` 三個 token。
2. 使用 `@utility text-shadow-*` 建立函式型工具類。
3. 另外定義 `@utility text-shadow-none` 重置陰影。
4. 建立一個展示頁面，使用不同的 text-shadow 工具類。

**驗收清單：**
- [ ] `text-shadow-sm`, `text-shadow-md`, `text-shadow-lg` 三個 class 都能正確顯示陰影。
- [ ] `text-shadow-none` 能清除陰影。
- [ ] `hover:text-shadow-md` 變體正常運作。
- [ ] `md:text-shadow-lg` responsive 前綴正常運作。
- [ ] 在 DevTools 中確認工具類位於 `@layer utilities`。

### Advanced / 進階練習

**任務：建立 scrollbar-hide 工具類與 hocus 變體**

1. 定義 `@utility scrollbar-hide`，支援 Chrome/Firefox/Edge 三大瀏覽器。
2. 定義 `@custom-variant hocus`，合併 hover 與 focus-visible。
3. 建立一個帶有隱藏捲軸的水平捲動列表。
4. 建立一組按鈕，使用 `hocus:` 變體統一 hover 和 focus 樣式。

**驗收清單：**
- [ ] 捲動列表在 Chrome、Firefox 中都看不到捲軸但可捲動。
- [ ] `hocus:bg-blue-700` 在 hover 和 keyboard focus 時都會觸發。
- [ ] scrollbar-hide 支援 `md:scrollbar-hide`（responsive）。
- [ ] 在 DevTools 中確認 `hocus` 變體產生 `:hover, :focus-visible` 選擇器。

### Challenge / 挑戰練習

**任務：建立完整的 glassmorphism 工具類系統**

1. 在 `@theme` 中定義 glass 相關 tokens（blur 值、opacity 值、邊框色）。
2. 使用 `@utility glass-*` 建立函式型工具類，支援 `glass-sm`, `glass-md`, `glass-lg`。
3. 定義 `@custom-variant data-open` 和 `@custom-variant data-active`。
4. 建立一個 glassmorphism 卡片元件展示頁，包含：
   - 不同模糊強度的 glass 卡片。
   - 點擊時透過 JavaScript 切換 `data-state`，使用自訂變體改變樣式。
   - 深色模式下不同的 glass 效果。
5. 加入 `print:` 自訂變體，列印時移除 glass 效果。

**驗收清單：**
- [ ] `glass-sm`, `glass-md`, `glass-lg` 分別呈現不同模糊程度。
- [ ] `glass-[20px]` arbitrary value 正常運作。
- [ ] `data-open:glass-lg` 在 `data-state="open"` 時觸發。
- [ ] `dark:glass-md` 在深色模式下呈現不同效果。
- [ ] `print:bg-white` 在列印預覽中正確顯示。
- [ ] 所有自訂工具類都在 `@layer utilities` 中。

## Reference Solution

以下是完整的 Challenge 練習參考解答：

```css
/* src/app.css */
@import "tailwindcss";
@import "./custom-utilities.css";

@theme {
  /* text-shadow tokens */
  --text-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.15);
  --text-shadow-md: 0 2px 4px rgba(0, 0, 0, 0.25);
  --text-shadow-lg: 0 4px 8px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(0, 0, 0, 0.15);

  /* glass tokens */
  --glass-sm: 4px;
  --glass-md: 12px;
  --glass-lg: 24px;
}
```

```css
/* src/custom-utilities.css */

/* ---- Text Shadow 工具類 ---- */
@utility text-shadow-* {
  text-shadow: --value(--text-shadow-*);
}

@utility text-shadow-none {
  text-shadow: none;
}

/* ---- Scrollbar 工具類 ---- */
@utility scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}

/* ---- Glass（毛玻璃）工具類 ---- */
@utility glass-* {
  backdrop-filter: blur(--value(--glass-*));
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

@utility glass-none {
  backdrop-filter: none;
  background: transparent;
  border: none;
  box-shadow: none;
}

/* ---- Text Gradient 工具類 ---- */
@utility text-gradient {
  background: linear-gradient(135deg, var(--color-blue-500), var(--color-purple-600));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ---- 自訂變體 ---- */
@custom-variant hocus {
  &:hover,
  &:focus-visible {
    @slot;
  }
}

@custom-variant data-open (&[data-state="open"]);

@custom-variant data-active (&[data-state="active"]);

@custom-variant print {
  @media print {
    @slot;
  }
}
```

```html
<!-- index.html -->
<!doctype html>
<html lang="zh-Hant" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Custom Utilities Demo</title>
  <link rel="stylesheet" href="/src/app.css" />
</head>
<body class="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 p-8">

  <!-- Text Shadow 展示 -->
  <section class="mb-12">
    <h1 class="text-5xl font-extrabold text-white text-shadow-lg mb-4">
      Text Shadow 工具類展示
    </h1>
    <p class="text-xl text-white/80 text-shadow-sm">
      使用 @utility 定義的自訂文字陰影。
    </p>
    <p class="text-lg text-white/70 hover:text-shadow-md transition-all duration-300">
      Hover 時陰影加深。
    </p>
  </section>

  <!-- Glass 卡片展示 -->
  <section class="mb-12 grid grid-cols-1 md:grid-cols-3 gap-6">
    <div class="glass-sm rounded-2xl p-6 text-white">
      <h3 class="text-lg font-semibold mb-2">Glass Small</h3>
      <p class="text-white/70">blur 4px 的毛玻璃效果。</p>
    </div>
    <div class="glass-md rounded-2xl p-6 text-white">
      <h3 class="text-lg font-semibold mb-2">Glass Medium</h3>
      <p class="text-white/70">blur 12px 的毛玻璃效果。</p>
    </div>
    <div class="glass-lg rounded-2xl p-6 text-white">
      <h3 class="text-lg font-semibold mb-2">Glass Large</h3>
      <p class="text-white/70">blur 24px 的毛玻璃效果。</p>
    </div>
  </section>

  <!-- data-state 變體展示 -->
  <section class="mb-12">
    <div
      id="accordion"
      data-state="closed"
      class="glass-md rounded-2xl overflow-hidden text-white cursor-pointer
             data-open:glass-lg data-open:ring-2 data-open:ring-white/30"
      onclick="this.dataset.state = this.dataset.state === 'open' ? 'closed' : 'open'"
    >
      <div class="p-4 font-semibold">
        點擊切換 data-state（目前使用 data-open 變體）
      </div>
      <div class="p-4 hidden data-open:block border-t border-white/10">
        <p>展開後的內容。glass 效果從 md 變為 lg，並加上 ring。</p>
      </div>
    </div>
  </section>

  <!-- hocus 變體展示 -->
  <section class="mb-12 flex gap-4">
    <button class="bg-blue-600 text-white px-6 py-3 rounded-lg
                   hocus:bg-blue-800 hocus:ring-2 hocus:ring-blue-400
                   transition-all duration-200 text-shadow-sm">
      Hocus 按鈕
    </button>
    <button class="glass-md text-white px-6 py-3 rounded-lg
                   hocus:glass-lg hocus:text-shadow-md
                   transition-all duration-200">
      Glass Hocus 按鈕
    </button>
  </section>

  <!-- Scrollbar Hide 展示 -->
  <section class="mb-12">
    <h2 class="text-2xl font-bold text-white text-shadow-md mb-4">
      水平捲動列表（隱藏捲軸）
    </h2>
    <div class="flex gap-4 overflow-x-auto scrollbar-hide pb-4">
      <div class="glass-sm rounded-xl p-6 min-w-64 text-white shrink-0">卡片 1</div>
      <div class="glass-sm rounded-xl p-6 min-w-64 text-white shrink-0">卡片 2</div>
      <div class="glass-sm rounded-xl p-6 min-w-64 text-white shrink-0">卡片 3</div>
      <div class="glass-sm rounded-xl p-6 min-w-64 text-white shrink-0">卡片 4</div>
      <div class="glass-sm rounded-xl p-6 min-w-64 text-white shrink-0">卡片 5</div>
      <div class="glass-sm rounded-xl p-6 min-w-64 text-white shrink-0">卡片 6</div>
    </div>
  </section>

  <!-- Print 變體展示 -->
  <section class="print:bg-white print:text-black">
    <p class="text-white print:text-black">
      這段文字在螢幕上是白色，列印時是黑色。
    </p>
    <nav class="print:hidden glass-sm p-4 rounded-lg text-white">
      <p>此導航列在列印時會隱藏。</p>
    </nav>
  </section>

</body>
</html>
```

## Common Pitfalls

### 1. @utility 名稱與內建工具類衝突

如果你定義的 `@utility` 名稱與 Tailwind 內建工具類相同（如 `@utility flex`），你的定義會覆蓋內建行為，導致不可預期的結果。

```css
/* 錯誤：覆蓋了內建的 flex 工具類 */
@utility flex {
  display: flex;
  gap: 1rem; /* 這會改變 flex 的行為 */
}

/* 正確：使用獨特的名稱 */
@utility flex-gapped {
  display: flex;
  gap: 1rem;
}
```

### 2. v4 特有：忘記 @utility 中不支援 @apply

在 `@utility` 定義內部不能使用 `@apply`。這是 v4 的限制，因為工具類本身就是最小單位。

```css
/* 錯誤：@utility 內部不支援 @apply */
@utility card-base {
  @apply rounded-lg p-4 shadow-md; /* 會報錯 */
}

/* 正確：直接寫 CSS 屬性 */
@utility card-base {
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* 更好：這類多屬性組合應用元件抽取，而非 @utility */
```

### 3. @custom-variant 忘記 @slot 佔位符

使用區塊語法定義 `@custom-variant` 時，必須包含 `@slot`，否則工具類的樣式不會被注入。

```css
/* 錯誤：缺少 @slot */
@custom-variant hocus {
  &:hover,
  &:focus-visible {
    /* 工具類樣式不會出現在這裡 */
  }
}

/* 正確：使用 @slot 標記樣式注入點 */
@custom-variant hocus {
  &:hover,
  &:focus-visible {
    @slot;
  }
}
```

### 4. 函式型 @utility 的 * 位置錯誤

函式型工具類的 `*` 必須在名稱末尾，且只能有一個 `*`。

```css
/* 錯誤：* 不在末尾 */
@utility *-shadow {
  text-shadow: --value(--text-shadow-*);
}

/* 錯誤：多個 * */
@utility text-*-shadow-* {
  text-shadow: --value(--text-shadow-*);
}

/* 正確：* 在末尾 */
@utility text-shadow-* {
  text-shadow: --value(--text-shadow-*);
}
```

### 5. 混淆 @utility 與 @layer components

`@utility` 自動放在 utilities layer 中。如果你的自訂 class 更像是一個「元件」（多屬性組合），不要用 `@utility`，而應在 `@layer components` 中定義。

```css
/* 不建議：card 是元件級別的抽象 */
@utility card {
  border-radius: 0.75rem;
  padding: 1.5rem;
  background: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* 建議：放在 components layer */
@layer components {
  .card {
    border-radius: 0.75rem;
    padding: 1.5rem;
    background: white;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }
}
```

## Checklist

- [ ] 能使用 `@utility` 定義靜態自訂工具類（如 `scrollbar-hide`）。
- [ ] 能使用 `@utility name-*` 搭配 `--value()` 定義函式型工具類（如 `text-shadow-*`）。
- [ ] 能使用 `@custom-variant` 定義自訂變體，並正確使用 `@slot`。
- [ ] 理解 `@utility` vs `@apply` vs component extraction 的使用時機。
- [ ] 確認自訂工具類自動支援 responsive（`md:`）和 stateful（`hover:`）變體。
- [ ] 在 DevTools 中驗證自訂工具類位於正確的 CSS layer。
- [ ] 能將 `@theme` tokens 與 `@utility` 函式型工具類整合使用。

## Further Reading (official links only)

- [Adding Custom Utilities](https://tailwindcss.com/docs/adding-custom-styles#adding-custom-utilities)
- [Custom Variants](https://tailwindcss.com/docs/adding-custom-styles#adding-custom-variants)
- [Functions and Directives - @utility](https://tailwindcss.com/docs/functions-and-directives#utility-directive)
- [Functions and Directives - @custom-variant](https://tailwindcss.com/docs/functions-and-directives#custom-variant-directive)
- [Tailwind CSS v4.0 Release Notes](https://tailwindcss.com/blog/tailwindcss-v4)
- [Tailwind CSS GitHub Repository](https://github.com/tailwindlabs/tailwindcss)
