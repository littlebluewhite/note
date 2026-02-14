---
title: "Installation and CSS-First Configuration / 安裝與 CSS-First 設定"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "02"
level: beginner
stack: Tailwind CSS 4.1.x
prerequisites: [01_utility_first_philosophy_and_mental_model]
---
# Installation and CSS-First Configuration / 安裝與 CSS-First 設定

## Goal

在上一章 [01_utility_first_philosophy_and_mental_model](01_utility_first_philosophy_and_mental_model.md) 中，我們理解了 utility-first 的核心哲學。現在要深入探討 Tailwind CSS v4 的三種安裝方式（Vite plugin、PostCSS、CLI），以及 v4 最重要的變革之一：**CSS-first configuration**。在 v3 中，所有設定都寫在 `tailwind.config.js`；而 v4 徹底改變了這個模式，讓你直接在 CSS 中透過 `@theme`、`@import "tailwindcss"` 進行設定，不再需要 JavaScript 設定檔。

理解安裝方式與 CSS-first configuration 後，你將能在任何專案中正確設定 Tailwind CSS v4，並自訂基礎主題 token。下一章 [03_colors_backgrounds_and_opacity](03_colors_backgrounds_and_opacity.md) 將深入色彩系統，包括 oklch 色彩空間與自訂色彩的設定。

## Prerequisites

- 已完成第 01 章。
- 已安裝 Node.js 20+ 與 npm。
- 理解 CSS `@import` 語法的基本概念。
- 知道 Vite、PostCSS、CLI 分別是什麼（概念層級即可）。

## Core Concepts

### Vite Plugin vs PostCSS Plugin vs CLI
- **何時用 Vite Plugin（`@tailwindcss/vite`）**：專案使用 Vite 作為建構工具。這是最推薦的方式，速度最快，設定最簡單。
- **何時用 PostCSS Plugin（`@tailwindcss/postcss`）**：專案使用 Webpack、Parcel 或其他非 Vite 建構工具。
- **何時用 CLI（`@tailwindcss/cli`）**：不使用任何建構工具，或需要獨立的 CSS 建構指令。

### `@import "tailwindcss"` vs `@tailwind` directives
- **何時用 `@import "tailwindcss"`**：所有 v4 新專案。這一行取代了 v3 的三行 `@tailwind base; @tailwind components; @tailwind utilities;`。
- **何時不用**：如果你在維護 v3 專案且尚未遷移，仍然會看到舊的 `@tailwind` 指令。但新專案請一律使用 `@import "tailwindcss"`。

### Automatic Content Detection vs Manual `content: [...]`
- **何時依賴自動偵測**：所有 v4 專案。v4 會自動掃描你的專案檔案，偵測使用了哪些 utility class，不需要手動設定 `content` 路徑。
- **何時需要手動設定**：極少見的情況，例如 class 名稱是由伺服器端動態產生且完全不在任何靜態檔案中出現。

### @theme Customization vs tailwind.config.js
- **何時用 `@theme`**：所有 v4 新專案的主題自訂。直接在 CSS 中定義，語法直覺，與 CSS custom properties 整合。
- **何時不用 `@theme`**：v3 遷移過渡期可能暫時保留部分 JS config，但最終目標是完全遷移到 CSS-first。

## Step-by-step

### 1. 方法一：Vite Plugin 安裝（推薦）

```bash
npm create vite@latest my-project -- --template vanilla
cd my-project
npm install tailwindcss @tailwindcss/vite
```

設定 `vite.config.js`：

```js
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
});
```

設定 CSS 入口 `style.css`：

```css
@import "tailwindcss";
```

驗證：`npm run dev`，在 HTML 中加入 `class="text-red-500"`，確認文字變紅。

### 2. 方法二：PostCSS 安裝

```bash
npm install tailwindcss @tailwindcss/postcss postcss
```

建立 `postcss.config.js`：

```js
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

CSS 入口同樣使用 `@import "tailwindcss";`。

驗證：確認建構工具（Webpack/Parcel 等）正確載入 PostCSS 設定。

### 3. 方法三：CLI 安裝

```bash
npm install tailwindcss @tailwindcss/cli
```

建立 `src/input.css`：

```css
@import "tailwindcss";
```

建構命令：

```bash
npx @tailwindcss/cli -i src/input.css -o dist/output.css --watch
```

在 HTML 中引用 `dist/output.css`。

### 4. 理解 `@import "tailwindcss"` 的展開

這一行會展開為以下內容：

```css
@layer theme, base, components, utilities;

@import "tailwindcss/theme" layer(theme);
@import "tailwindcss/preflight" layer(base);
@import "tailwindcss/utilities" layer(utilities);
```

你也可以手動展開來精細控制各層的載入，例如排除 preflight：

```css
@layer theme, base, components, utilities;

@import "tailwindcss/theme" layer(theme);
/* 故意不載入 preflight */
@import "tailwindcss/utilities" layer(utilities);
```

### 5. 使用 @theme 自訂主題

在 `style.css` 中加入自訂色彩與間距：

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.72 0.19 250);
  --color-brand-light: oklch(0.85 0.12 250);
  --color-brand-dark: oklch(0.55 0.22 250);
  --font-family-display: "Inter", sans-serif;
  --spacing-18: 4.5rem;
}
```

現在你可以使用 `bg-brand`、`text-brand-dark`、`font-display`、`p-18` 等 utility class。

### 6. 驗證自訂 token 生效

在 HTML 中使用自訂 token：

```html
<div class="bg-brand text-white p-18 font-display">
  <h1 class="text-2xl font-bold">自訂主題測試</h1>
  <p class="text-brand-light">這段文字使用自訂品牌色的淡色版本。</p>
</div>
```

在瀏覽器 DevTools 中檢查元素，確認 CSS custom properties 已正確設定。

### 7. 理解自動內容偵測

在 v4 中，你不需要設定 `content: ["./src/**/*.html"]`。Tailwind 會自動偵測專案中所有檔案中的 class 名稱。

驗證方式：
1. 建立新的 HTML 檔案 `pages/test.html`。
2. 在其中使用一個新的 utility class（如 `text-emerald-600`）。
3. 不需要任何額外設定，該 class 就會被自動偵測並產生。

### 8. 在 @theme 中覆寫預設值

你可以覆寫 Tailwind 的預設主題值：

```css
@import "tailwindcss";

@theme {
  /* 覆寫預設的 sans 字型 */
  --font-family-sans: "Noto Sans TC", "Inter", system-ui, sans-serif;

  /* 覆寫預設的圓角 */
  --radius-lg: 1rem;

  /* 新增自訂斷點 */
  --breakpoint-3xl: 120rem;
}
```

### 9. 使用 @source 指定額外掃描路徑

某些情況下（如 monorepo），自動偵測可能遺漏特定路徑。使用 `@source` 指令明確指定：

```css
@import "tailwindcss";
@source "../shared-ui/components";
```

### 10. 完整設定檔範例

一個實際專案的完整 `style.css`：

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.72 0.19 250);
  --color-brand-light: oklch(0.85 0.12 250);
  --color-brand-dark: oklch(0.55 0.22 250);

  --color-surface: oklch(0.99 0 0);
  --color-surface-dim: oklch(0.95 0 0);

  --font-family-sans: "Noto Sans TC", "Inter", system-ui, sans-serif;
  --font-family-mono: "JetBrains Mono", ui-monospace, monospace;

  --radius-card: 0.75rem;
}

@layer components {
  .btn-primary {
    @apply bg-brand text-white px-4 py-2 rounded-card font-medium hover:bg-brand-dark transition-colors;
  }
}
```

## Hands-on Lab

### Foundation

用 Vite plugin 方式建立一個新專案，設定 `@theme` 自訂至少 3 個色彩 token 和 1 個字型 token，並建立一個展示頁面使用這些 token。

**驗收清單：**
- [ ] `@import "tailwindcss"` 正確放在 CSS 入口。
- [ ] `@theme` 中定義了至少 3 個色彩和 1 個字型。
- [ ] HTML 中使用了自訂 token 的 utility class（如 `bg-brand`）。
- [ ] 瀏覽器 DevTools 可看到對應的 CSS custom properties。

### Advanced

在 Foundation 的專案中，同時建立 PostCSS 方式的設定（可以是新的 `postcss.config.js`），並用 CLI 方式建立獨立的建構指令。比較三種方式的建構速度與設定複雜度。

**驗收清單：**
- [ ] 三種安裝方式的設定檔都存在且正確。
- [ ] 記錄了三種方式的 cold start 建構時間。
- [ ] 寫出一段比較摘要，說明各方式的適用場景。

### Challenge

建立一個不載入 preflight 的客製化設定，並自訂完整的品牌色彩系統（primary、secondary、neutral 各 5 個色階），模擬實際專案的主題設定。

**驗收清單：**
- [ ] CSS 中手動展開 `@import "tailwindcss"` 且排除 preflight。
- [ ] `@theme` 中定義了 primary/secondary/neutral 各 5 個色階。
- [ ] 所有色彩使用 oklch 色彩空間。
- [ ] 展示頁面使用了所有 15 個自訂色彩。

## Reference Solution

```css
/* style.css - Challenge 完整解答 */
@layer theme, base, components, utilities;

@import "tailwindcss/theme" layer(theme);
/* 故意不載入 preflight，使用自訂 base styles */
@import "tailwindcss/utilities" layer(utilities);

@theme {
  /* Primary - 藍色系 */
  --color-primary-100: oklch(0.95 0.05 250);
  --color-primary-300: oklch(0.82 0.12 250);
  --color-primary-500: oklch(0.65 0.19 250);
  --color-primary-700: oklch(0.50 0.20 250);
  --color-primary-900: oklch(0.35 0.15 250);

  /* Secondary - 紫色系 */
  --color-secondary-100: oklch(0.95 0.05 300);
  --color-secondary-300: oklch(0.82 0.12 300);
  --color-secondary-500: oklch(0.65 0.17 300);
  --color-secondary-700: oklch(0.50 0.18 300);
  --color-secondary-900: oklch(0.35 0.13 300);

  /* Neutral - 灰色系 */
  --color-neutral-100: oklch(0.96 0 0);
  --color-neutral-300: oklch(0.85 0 0);
  --color-neutral-500: oklch(0.65 0 0);
  --color-neutral-700: oklch(0.45 0 0);
  --color-neutral-900: oklch(0.20 0 0);

  --font-family-sans: "Noto Sans TC", "Inter", system-ui, sans-serif;
  --font-family-mono: "JetBrains Mono", ui-monospace, monospace;
}

@layer base {
  *,
  *::before,
  *::after {
    box-sizing: border-box;
    margin: 0;
  }
  body {
    font-family: var(--font-family-sans);
    color: var(--color-neutral-900);
    line-height: 1.6;
  }
}
```

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Brand Color System</title>
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body class="min-h-screen bg-neutral-100 p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold text-neutral-900 mb-8">品牌色彩系統</h1>

      <h2 class="text-xl font-semibold mb-4">Primary</h2>
      <div class="flex gap-4 mb-8">
        <div class="w-20 h-20 bg-primary-100 rounded-lg"></div>
        <div class="w-20 h-20 bg-primary-300 rounded-lg"></div>
        <div class="w-20 h-20 bg-primary-500 rounded-lg"></div>
        <div class="w-20 h-20 bg-primary-700 rounded-lg"></div>
        <div class="w-20 h-20 bg-primary-900 rounded-lg"></div>
      </div>

      <h2 class="text-xl font-semibold mb-4">Secondary</h2>
      <div class="flex gap-4 mb-8">
        <div class="w-20 h-20 bg-secondary-100 rounded-lg"></div>
        <div class="w-20 h-20 bg-secondary-300 rounded-lg"></div>
        <div class="w-20 h-20 bg-secondary-500 rounded-lg"></div>
        <div class="w-20 h-20 bg-secondary-700 rounded-lg"></div>
        <div class="w-20 h-20 bg-secondary-900 rounded-lg"></div>
      </div>

      <h2 class="text-xl font-semibold mb-4">Neutral</h2>
      <div class="flex gap-4 mb-8">
        <div class="w-20 h-20 bg-neutral-100 rounded-lg border border-neutral-300"></div>
        <div class="w-20 h-20 bg-neutral-300 rounded-lg"></div>
        <div class="w-20 h-20 bg-neutral-500 rounded-lg"></div>
        <div class="w-20 h-20 bg-neutral-700 rounded-lg"></div>
        <div class="w-20 h-20 bg-neutral-900 rounded-lg"></div>
      </div>
    </div>
  </body>
</html>
```

## Common Pitfalls

1. **嘗試建立 `tailwind.config.js`（v4 陷阱）**：這是 v3 使用者最常犯的錯誤。在 v4 中，所有主題設定都應該寫在 CSS 的 `@theme` 區塊中，不再需要 JavaScript 設定檔。如果你發現自己在建立 `tailwind.config.js`，請停下來改用 `@theme`。

2. **使用舊版 `@tailwind` 指令（v4 陷阱）**：`@tailwind base; @tailwind components; @tailwind utilities;` 是 v3 語法。v4 中請使用 `@import "tailwindcss";`。

3. **手動設定 `content` 路徑（v4 陷阱）**：v4 使用自動內容偵測，不需要在任何設定檔中指定 `content: ["./src/**/*.html"]`。如果你看到教學要求你設定 content，那可能是 v3 的教學。

4. **@theme 中的 CSS 變數命名錯誤**：`@theme` 中的命名必須遵循 Tailwind 的 namespace 規範。例如色彩用 `--color-*`，字型用 `--font-family-*`，間距用 `--spacing-*`。命名錯誤不會報錯但 utility class 不會生成。

5. **忘記安裝對應的整合套件**：只安裝 `tailwindcss` 但沒有安裝 `@tailwindcss/vite`（或 `@tailwindcss/postcss`），導致 CSS 完全不被處理。

## Checklist

- [ ] 能說出 Vite plugin、PostCSS、CLI 三種安裝方式的差異與適用場景。
- [ ] CSS 入口檔使用 `@import "tailwindcss";` 而非舊版 `@tailwind` 指令。
- [ ] 會使用 `@theme` 自訂色彩、字型、間距等 token。
- [ ] 理解 v4 的自動內容偵測機制，不手動設定 `content`。
- [ ] 知道如何手動展開 `@import "tailwindcss"` 以精細控制各層。
- [ ] 會使用 `@source` 指定額外的掃描路徑。
- [ ] 在瀏覽器 DevTools 中確認 CSS custom properties 正確生成。

## Further Reading (official links only)

- [Installing Tailwind CSS](https://tailwindcss.com/docs/installation)
- [Installing with Vite](https://tailwindcss.com/docs/installation/vite)
- [Installing with PostCSS](https://tailwindcss.com/docs/installation/post-css)
- [Using the CLI](https://tailwindcss.com/docs/installation/tailwindcss-cli)
- [Theme Configuration](https://tailwindcss.com/docs/theme)
- [Detecting Content Sources](https://tailwindcss.com/docs/detecting-classes-in-source-files)
