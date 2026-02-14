---
title: "Migration from Tailwind v3 to v4 / 從 Tailwind v3 遷移到 v4"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "23"
level: advanced
stack: Tailwind CSS 4.1.x
prerequisites: [22_design_system_patterns_and_token_architecture]
---

# Migration from Tailwind v3 to v4 / 從 Tailwind v3 遷移到 v4

## Goal

在前一章 [[22_design_system_patterns_and_token_architecture]] 中，我們建立了一套完整的設計系統令牌架構，從原始令牌到語義令牌到元件令牌。本章將聚焦於一個許多團隊面臨的實際挑戰：如何將現有的 Tailwind CSS v3 專案遷移到 v4。v4 是一次重大版本更新，帶來了配置方式、指令語法、插件 API、預設值等多方面的破壞性變更（breaking changes）。好消息是 Tailwind 團隊提供了自動化的升級工具 `npx @tailwindcss/upgrade`，可以處理大部分的機械式轉換。

本章將系統性地介紹所有需要注意的破壞性變更，提供一步步的遷移指南，解釋自動升級工具能處理和不能處理的範圍，並透過實際案例展示手動修復的方法。遷移不只是語法轉換，更是一次重新審視專案架構的機會。在下一章 [[24_upgrade_governance_security_and_maintenance]] 中，我們將建立一套持續的升級治理流程，確保未來的小版本更新能安全順暢地進行。

## Prerequisites

- 已完成第 22 章，理解 v4 的設計系統架構。
- 有一個基於 Tailwind CSS v3 的現有專案（或能建立一個範例專案）。
- 熟悉 npm/pnpm 套件管理和版本控制。
- 理解 `tailwind.config.js` 的基本結構（v3 配置方式）。
- 具備 Git 版本控制基礎（分支、提交、比較）。

## Core Concepts

### 1. Configuration Migration / 配置遷移

v3 和 v4 最根本的差異在於配置方式：從 JavaScript 配置檔轉為 CSS-first 配置。

**v3 方式 → v4 方式：**
- `tailwind.config.js` → `@theme` directive in CSS
- `@tailwind base/components/utilities` → `@import "tailwindcss"`
- `content: [...]` → automatic content detection
- `theme.extend.colors` → `@theme { --color-*: ... }`
- `plugins: [require(...)]` → `@plugin "..."`

**何時使用自動升級工具：**
- 專案主要使用標準的 Tailwind 配置，沒有高度客製化。
- 想要快速完成大部分機械式轉換。
- 專案有良好的測試覆蓋率，可以驗證升級後的結果。

**何時需要手動遷移：**
- 專案有複雜的自訂插件（JavaScript plugin API）。
- 使用了大量的 `theme()` 函式或 `screen()` 函式。
- 有嚴重依賴 v3 特定行為的邏輯。
- 第三方套件尚未支援 v4。

### 2. Breaking Changes Overview / 破壞性變更總覽

理解所有破壞性變更的範圍和影響程度。

**高影響（必須處理）：**
- 配置檔遷移（tailwind.config.js → CSS）。
- `@tailwind` 指令移除。
- PostCSS 插件變更（`tailwindcss` → `@tailwindcss/postcss`）。
- 預設色彩空間從 sRGB 變為 oklch。

**中影響（視專案而定）：**
- `addUtilities()` / `addComponents()` plugin API 變更。
- 部分工具類重新命名或移除。
- 預設 border color 變更。
- `ring-*` 預設寬度變更。

**低影響（少數專案受影響）：**
- CSS 變數命名空間變更（`--tw-*` 前綴調整）。
- 部分 arbitrary value 語法微調。
- Container 元件預設行為變更。

### 3. Upgrade Tool Capabilities / 升級工具能力範圍

`npx @tailwindcss/upgrade` 是官方的自動化升級工具。

**升級工具能自動處理的：**
- `tailwind.config.js` 轉換為 CSS `@theme` 配置。
- `@tailwind` 指令替換為 `@import "tailwindcss"`。
- `postcss.config.js` 中的插件名稱更新。
- 大部分已重新命名的工具類更新。
- `content` 配置移除。
- 插件引入方式更新（`require()` → `@plugin`）。

**升級工具無法自動處理的：**
- 複雜的自訂 JavaScript 插件邏輯轉換。
- `theme()` CSS 函式的所有使用場景。
- 第三方套件的相容性問題。
- 視覺回歸（色彩空間變更導致的微妙色差）。
- 業務邏輯中的條件式 class 名稱更新。

### 4. Migration Strategy / 遷移策略

根據專案規模選擇適合的遷移策略。

**何時使用 Big Bang（一次性遷移）：**
- 小型專案（< 20 個頁面/元件）。
- 團隊有充足的測試覆蓋率。
- 可以分配專門的時間進行遷移。

**何時使用漸進式遷移：**
- 大型專案（50+ 個頁面/元件）。
- 無法一次性停止功能開發。
- 需要分階段驗證和回滾。
- 有多個團隊共同維護的 monorepo。

## Step-by-step

### 步驟 1：建立 v3 範例專案（遷移前基準）

建立一個典型的 v3 專案結構，作為遷移練習的起點：

```js
// tailwind.config.js (v3)
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,js,jsx,ts,tsx}",
    "./index.html",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
        surface: "#ffffff",
        "surface-dark": "#0f172a",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      spacing: {
        18: "4.5rem",
        22: "5.5rem",
      },
      borderRadius: {
        "4xl": "2rem",
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
    require("@tailwindcss/forms"),
  ],
};
```

```js
// postcss.config.js (v3)
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

```css
/* src/styles.css (v3) */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-surface text-gray-900 dark:bg-surface-dark dark:text-gray-100;
  }
}

@layer components {
  .btn-primary {
    @apply inline-flex items-center px-4 py-2 rounded-lg bg-brand-600 text-white
           hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500
           focus:ring-offset-2 transition-colors;
  }
  .card {
    @apply rounded-xl bg-white shadow-md border border-gray-200 p-6
           dark:bg-gray-800 dark:border-gray-700;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

```html
<!-- index.html (v3) -->
<!doctype html>
<html lang="zh-Hant" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>V3 Project</title>
  <link rel="stylesheet" href="/src/styles.css" />
</head>
<body>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-4xl font-bold text-brand-600 dark:text-brand-500 mb-6">
      Tailwind v3 專案
    </h1>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div class="card">
        <h2 class="text-xl font-semibold mb-2">Card 1</h2>
        <p class="text-gray-600 dark:text-gray-300">卡片內容。</p>
        <button class="btn-primary mt-4">Action</button>
      </div>
      <div class="card">
        <h2 class="text-xl font-semibold mb-2">Card 2</h2>
        <p class="text-gray-600 dark:text-gray-300">卡片內容。</p>
      </div>
    </div>
    <article class="prose dark:prose-invert mt-12 max-w-none">
      <h2>Typography 插件內容</h2>
      <p>這段文字使用 <code>@tailwindcss/typography</code> 排版。</p>
    </article>
  </div>
</body>
</html>
```

驗證：v3 專案能正常執行，所有樣式正確顯示。截圖保存作為遷移前基準。

### 步驟 2：建立遷移分支和備份

```bash
# 確認目前狀態
git status
git add -A
git commit -m "Pre-migration: v3 project baseline"

# 建立遷移分支
git checkout -b feat/tailwind-v4-migration

# 記錄 v3 的建置產物大小
npx vite build 2>&1 | tee v3-build-output.txt
ls -lh dist/assets/*.css > v3-css-sizes.txt
```

驗證：遷移分支已建立，v3 建置記錄已保存。

### 步驟 3：執行自動升級工具

```bash
# 執行官方升級工具
npx @tailwindcss/upgrade

# 升級工具會自動：
# 1. 更新 package.json 中的 tailwindcss 版本
# 2. 安裝新的依賴（@tailwindcss/postcss, @tailwindcss/vite 等）
# 3. 轉換 tailwind.config.js → CSS @theme
# 4. 更新 @tailwind 指令 → @import "tailwindcss"
# 5. 更新 postcss.config.js
# 6. 更新已重新命名的工具類
```

升級後查看變更：

```bash
# 查看所有變更的檔案
git diff --stat

# 詳細查看每個檔案的變更
git diff

# 安裝更新的依賴
npm install
```

驗證：升級工具無錯誤完成。`git diff` 顯示合理的變更範圍。

### 步驟 4：檢查並修正自動轉換結果

升級工具轉換後的 CSS 應類似以下結構：

```css
/* src/styles.css (v4 - 自動轉換後) */
@import "tailwindcss";

@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";

@theme {
  --color-brand-50: #eff6ff;
  --color-brand-100: #dbeafe;
  --color-brand-500: #3b82f6;
  --color-brand-600: #2563eb;
  --color-brand-700: #1d4ed8;

  --color-surface: #ffffff;
  --color-surface-dark: #0f172a;

  --font-sans: "Inter", system-ui, sans-serif;

  --spacing-18: 4.5rem;
  --spacing-22: 5.5rem;

  --radius-4xl: 2rem;
}

@layer base {
  body {
    @apply bg-surface text-gray-900 dark:bg-surface-dark dark:text-gray-100;
  }
}

@layer components {
  .btn-primary {
    @apply inline-flex items-center px-4 py-2 rounded-lg bg-brand-600 text-white
           hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500
           focus:ring-offset-2 transition-colors;
  }
  .card {
    @apply rounded-xl bg-white shadow-md border border-gray-200 p-6
           dark:bg-gray-800 dark:border-gray-700;
  }
}
```

手動檢查並修正可能的問題：

```css
/* 問題 1：v3 的 sRGB hex 色值可以轉換為 oklch */
/* 手動最佳化（可選但建議） */
@theme {
  --color-brand-50: oklch(0.97 0.01 250);
  --color-brand-100: oklch(0.93 0.03 250);
  --color-brand-500: oklch(0.62 0.19 250);
  --color-brand-600: oklch(0.55 0.20 250);
  --color-brand-700: oklch(0.47 0.19 250);

  --color-surface: #ffffff;
  --color-surface-dark: oklch(0.15 0.02 260);

  --font-sans: "Inter", system-ui, sans-serif;
  --spacing-18: 4.5rem;
  --spacing-22: 5.5rem;
  --radius-4xl: 2rem;
}
```

驗證：`npm run dev` 啟動無錯誤，頁面樣式與 v3 基準截圖視覺一致。

### 步驟 5：處理 PostCSS 配置變更

v4 的 PostCSS 配置也需要更新：

```js
// postcss.config.js (v3)
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};

// postcss.config.js (v4)
// 方案 1：使用 @tailwindcss/postcss（如果繼續使用 PostCSS）
module.exports = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

```ts
// 方案 2（推薦）：使用 @tailwindcss/vite（如果使用 Vite）
// vite.config.ts
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
  // 不再需要 postcss.config.js 中的 tailwindcss 插件
});
```

```bash
# 安裝新的依賴
npm install @tailwindcss/vite
# 如果選擇 PostCSS 方案
npm install @tailwindcss/postcss
# 移除不再需要的 autoprefixer（v4 內建）
npm uninstall autoprefixer
```

驗證：建置流程正常運作，無 PostCSS 相關錯誤。

### 步驟 6：處理已移除和重新命名的工具類

v4 中部分工具類被移除或重新命名：

```html
<!-- 重新命名的工具類 -->

<!-- v3: shadow-sm → v4: shadow-sm（不變）-->
<!-- v3: shadow → v4: shadow-md（預設 shadow 的語義改變）-->
<div class="shadow-md">...</div>

<!-- v3: ring → v4: ring（寬度預設值從 3px 改為 1px）-->
<!-- 如果依賴 v3 的 3px 預設 ring，需要明確指定 -->
<div class="ring-3 ring-blue-500">...</div>

<!-- v3: decoration-slice → v4: box-decoration-slice -->
<span class="box-decoration-slice bg-gradient-to-r from-blue-500 to-purple-500">
  跨行文字
</span>

<!-- v3: blur → v4: blur-sm（blur 工具類的預設值改變）-->
<div class="blur-sm">...</div>

<!-- v3: border 預設顏色是 gray-200 → v4: border 預設是 currentColor -->
<!-- 需要明確指定邊框顏色 -->
<div class="border border-gray-200">...</div>

<!-- v3: container 預設無 mx-auto → v4: container 行為可能不同 -->
<div class="container mx-auto">...</div>
```

建立一個檢查腳本幫助識別需要更新的 class：

```bash
# 搜尋可能需要更新的 v3 class
# 搜尋使用了 border 但沒有指定顏色的地方
grep -rn 'class=.*\bborder\b' --include="*.html" --include="*.tsx" --include="*.svelte" src/

# 搜尋使用了預設 ring 的地方
grep -rn 'class=.*\bring\b' --include="*.html" --include="*.tsx" --include="*.svelte" src/

# 搜尋 decoration-slice（需要改為 box-decoration-slice）
grep -rn 'decoration-slice' --include="*.html" --include="*.tsx" --include="*.svelte" src/
```

驗證：所有已移除/重新命名的工具類都已更新。

### 步驟 7：處理自訂插件遷移

如果專案有自訂的 JavaScript 插件，需要手動遷移：

```js
// v3: plugins/custom-utilities.js
const plugin = require("tailwindcss/plugin");

module.exports = plugin(function ({ addUtilities, theme }) {
  addUtilities({
    ".text-shadow-sm": {
      "text-shadow": "0 1px 2px rgba(0,0,0,0.2)",
    },
    ".text-shadow-md": {
      "text-shadow": "0 2px 4px rgba(0,0,0,0.3)",
    },
    ".scrollbar-hide": {
      "-ms-overflow-style": "none",
      "scrollbar-width": "none",
      "&::-webkit-scrollbar": {
        display: "none",
      },
    },
  });
});
```

遷移為 v4 的 CSS-first 方式：

```css
/* v4: 直接在 CSS 中使用 @utility */
/* src/custom-utilities.css */

@utility text-shadow-sm {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

@utility text-shadow-md {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

@utility scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}
```

```css
/* 在主 CSS 中引入 */
@import "tailwindcss";
@import "./custom-utilities.css";
```

如果插件有動態邏輯無法用 CSS 表達，則需要更新 plugin API：

```js
// v4: plugins/dynamic-plugin.js
// 使用 ESM 語法
import plugin from "tailwindcss/plugin";

export default plugin(function ({ matchUtilities, theme }) {
  matchUtilities(
    {
      "text-stroke": (value) => ({
        "-webkit-text-stroke-width": value,
      }),
    },
    {
      values: {
        thin: "1px",
        medium: "2px",
        thick: "4px",
      },
    }
  );
});
```

```css
/* 在 CSS 中引入 JS 插件 */
@plugin "./plugins/dynamic-plugin.js";
```

驗證：自訂工具類在遷移後功能與 v3 完全一致。

### 步驟 8：處理 theme() 和 screen() 函式

v4 中 `theme()` 函式的使用方式有變更：

```css
/* v3: 使用 theme() 函式 */
.custom-element {
  color: theme("colors.brand.500");
  padding: theme("spacing.4");
  border-radius: theme("borderRadius.lg");
}

@media (min-width: theme("screens.md")) {
  .custom-element {
    padding: theme("spacing.8");
  }
}

/* v4: 使用 CSS 變數取代 theme() */
.custom-element {
  color: var(--color-brand-500);
  padding: var(--spacing-4);
  border-radius: var(--radius-lg);
}

@media (width >= 48rem) {
  .custom-element {
    padding: var(--spacing-8);
  }
}
```

```css
/* v3: screen() 函式 */
@media screen(md) {
  /* ... */
}

/* v4: 使用標準 CSS media query */
@media (width >= 48rem) {
  /* ... */
}

/* 或使用 Tailwind 的 breakpoint 變數 */
@media (width >= var(--breakpoint-md)) {
  /* ... */
}
```

驗證：所有 `theme()` 和 `screen()` 呼叫都已替換為 CSS 變數或標準語法。

### 步驟 9：執行視覺回歸測試

建立簡易的視覺回歸測試流程：

```bash
# 步驟 1：切回 v3 分支截取基準截圖
git stash
git checkout main
npm run build && npm run preview &
# 使用瀏覽器截取各頁面的截圖
# 儲存為 screenshots/v3-home.png, screenshots/v3-about.png 等

# 步驟 2：切回 v4 分支截取遷移後截圖
git checkout feat/tailwind-v4-migration
git stash pop
npm run build && npm run preview &
# 截取相同頁面的截圖
# 儲存為 screenshots/v4-home.png, screenshots/v4-about.png 等

# 步驟 3：使用 diff 工具比較
# 可使用 pixelmatch, reg-suit, 或簡單的肉眼比較
```

需要特別注意的視覺差異：

```
1. 色彩微調：oklch 色彩空間可能導致色彩略有差異
   → 如果色差明顯，手動調整 oklch 值

2. border 預設顏色：v4 預設是 currentColor
   → 所有 border 都需要明確指定顏色

3. ring 寬度：v3 預設 3px → v4 預設 1px
   → 使用 ring-3 恢復 v3 行為

4. shadow 級距：v4 調整了部分 shadow 值
   → 比較 shadow 效果，必要時使用 arbitrary values

5. 字型渲染：oklch 色彩可能影響文字對比度
   → 特別檢查深色模式下的文字可讀性
```

驗證：v4 遷移後的視覺效果與 v3 基準可接受地一致（允許微小的 oklch 色差）。

### 步驟 10：完成遷移並記錄

```bash
# 建置 v4 版本並比較大小
npm run build 2>&1 | tee v4-build-output.txt
ls -lh dist/assets/*.css > v4-css-sizes.txt

# 比較 v3 和 v4 的建置結果
echo "=== Build Size Comparison ==="
echo "V3:"
cat v3-css-sizes.txt
echo "V4:"
cat v4-css-sizes.txt

# 提交遷移結果
git add -A
git commit -m "feat: migrate from Tailwind CSS v3 to v4

- Replaced tailwind.config.js with CSS @theme configuration
- Updated @tailwind directives to @import 'tailwindcss'
- Migrated plugins to @plugin directive
- Converted custom plugins to @utility CSS-first approach
- Updated renamed utility classes
- Replaced theme()/screen() with CSS variables
- Verified visual regression"
```

建立遷移記錄文件：

```
# Tailwind v3 → v4 Migration Log

## Date: YYYY-MM-DD

## Changes Made
- [ ] Configuration: tailwind.config.js → @theme in CSS
- [ ] Directives: @tailwind → @import "tailwindcss"
- [ ] PostCSS: tailwindcss → @tailwindcss/vite
- [ ] Plugins: require() → @plugin
- [ ] Custom utilities: addUtilities() → @utility
- [ ] theme() → var(--*)
- [ ] screen() → @media (width >= *)
- [ ] Renamed classes: (list specific changes)
- [ ] Border color: added explicit colors
- [ ] Ring width: updated to ring-3 where needed

## Build Size
- V3: XX KB (gzipped)
- V4: XX KB (gzipped)
- Difference: ±XX%

## Visual Differences
- (list any intentional or accepted differences)

## Known Issues
- (list any remaining issues)
```

驗證：遷移記錄完整，所有變更都已記錄。

## Hands-on Lab

### Foundation / 基礎練習

**任務：執行自動升級工具並驗證結果**

1. 建立一個簡單的 Tailwind v3 專案（index.html + tailwind.config.js）。
2. 執行 `npx @tailwindcss/upgrade`。
3. 檢查自動轉換的結果。
4. 修正任何自動轉換未處理的問題。
5. 確認頁面視覺效果與 v3 一致。

**驗收清單：**
- [ ] v3 專案能正常執行作為基準。
- [ ] `npx @tailwindcss/upgrade` 成功完成無錯誤。
- [ ] `tailwind.config.js` 已被轉換為 CSS `@theme`。
- [ ] `@tailwind` 指令已被替換為 `@import "tailwindcss"`。
- [ ] 頁面視覺效果與 v3 基準一致。

### Advanced / 進階練習

**任務：遷移包含自訂插件和 @layer 的專案**

1. 建立一個 v3 專案，包含：自訂 JavaScript 插件、@layer components 中的自訂 class、使用 theme() 函式的自訂 CSS。
2. 執行自動升級。
3. 手動遷移自訂插件為 `@utility`。
4. 替換 `theme()` 為 CSS 變數。
5. 驗證所有功能。

**驗收清單：**
- [ ] 自訂 JavaScript 插件成功轉換為 `@utility` CSS 定義。
- [ ] @layer components 中的自訂 class 遷移後功能正常。
- [ ] 所有 `theme()` 呼叫已替換為 `var(--*)`。
- [ ] 所有 `screen()` 呼叫已替換為標準 media query。
- [ ] `npm run build` 無錯誤且 CSS 輸出合理。

### Challenge / 挑戰練習

**任務：完整遷移一個多頁面 v3 專案並執行視覺回歸**

1. 建立一個包含 4+ 頁面的 v3 專案（含 typography 插件、forms 插件、自訂插件、dark mode）。
2. 截取所有頁面的 v3 基準截圖。
3. 執行自動升級 + 手動修正。
4. 處理所有重新命名/移除的工具類。
5. 遷移所有自訂插件。
6. 截取 v4 截圖並與 v3 比較。
7. 建立完整的遷移記錄文件。
8. 比較 v3 和 v4 的建置大小和建置速度。

**驗收清單：**
- [ ] 4+ 頁面全部成功遷移。
- [ ] v3 和 v4 截圖比對通過（允許微小的 oklch 色差）。
- [ ] typography 和 forms 插件在 v4 正常運作。
- [ ] 深色模式切換正常。
- [ ] 遷移記錄文件包含所有變更和決策理由。
- [ ] v4 的建置速度 >= v3（通常快 3-5 倍）。
- [ ] 所有自訂工具類功能不變。

## Reference Solution

以下是遷移前後的完整對照：

**遷移前（v3）：**

```js
// tailwind.config.js (v3)
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js,tsx}", "./index.html"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: { 500: "#3b82f6", 600: "#2563eb", 700: "#1d4ed8" },
        surface: "#ffffff",
        "surface-dark": "#0f172a",
      },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
    require("@tailwindcss/forms"),
  ],
};
```

```css
/* src/styles.css (v3) */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn-primary {
    @apply inline-flex items-center px-4 py-2 rounded-lg bg-brand-600 text-white hover:bg-brand-700 focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 transition-colors;
  }
}
```

**遷移後（v4）：**

```css
/* src/styles.css (v4) */
@import "tailwindcss";

@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";

@theme {
  --color-brand-500: oklch(0.62 0.19 250);
  --color-brand-600: oklch(0.55 0.20 250);
  --color-brand-700: oklch(0.47 0.19 250);

  --color-surface: #ffffff;
  --color-surface-dark: oklch(0.15 0.02 260);

  --font-sans: "Inter", system-ui, sans-serif;
}

@layer components {
  .btn-primary {
    @apply inline-flex items-center px-4 py-2 rounded-lg bg-brand-600 text-white hover:bg-brand-700 focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 transition-colors;
  }
}
```

```ts
// vite.config.ts (v4)
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
});
```

```json
// package.json 依賴變更
{
  "devDependencies": {
    "tailwindcss": "^4.1.0",
    "@tailwindcss/vite": "^4.1.0",
    "vite": "^6.0.0"
  },
  "dependencies": {
    "@tailwindcss/typography": "^0.5.0",
    "@tailwindcss/forms": "^0.5.0"
  }
}
```

## Common Pitfalls

### 1. v4 特有：遷移後忘記移除 tailwind.config.js

自動升級工具會將 `tailwind.config.js` 的內容遷移到 CSS 中，但可能不會刪除原始檔案。殘留的 `tailwind.config.js` 可能被 v4 引擎忽略（因為 v4 不再讀取它），但會讓其他開發者誤以為它仍在生效。

```bash
# 升級後確認並移除
rm tailwind.config.js
# 或如果仍需要 JS 配置（少數情況），確認它被 @config 引用
```

### 2. content 配置殘留導致困惑

v4 自動偵測模板檔案，但如果專案根目錄仍有 `tailwind.config.js` 且包含 `content` 設定，可能導致困惑（v4 忽略它，但開發者誤以為它在生效）。

```css
/* v4 不需要 content 配置 */
/* 如需擴展偵測範圍，使用 @source */
@source "../packages/ui/src/**/*.tsx";
```

### 3. 漸進式遷移中 v3 和 v4 共存的問題

在 monorepo 中，不同套件可能使用不同版本的 Tailwind。這需要仔細管理。

```
/* 不建議：同一個 CSS bundle 中混合 v3 和 v4 工具類 */
/* 這會導致不可預期的 specificity 和 layer 衝突 */

/* 建議：以套件/應用為單位完整遷移 */
```

### 4. 第三方元件庫尚未支援 v4

有些社群元件庫可能尚未更新到 v4 相容版本。在遷移前需要確認所有依賴的相容性。

```bash
# 檢查依賴的 Tailwind 版本要求
npm ls tailwindcss
# 查看依賴的 GitHub issues 確認 v4 支援狀態
```

### 5. oklch 色彩空間導致色差

v4 預設使用 oklch 色彩空間，而 v3 使用 sRGB。直接將 hex 色值搬到 v4 不會有問題（hex 仍然受支援），但如果你選擇轉換為 oklch，可能會有微小的色差。

```css
/* 安全做法：保留原始 hex 值 */
@theme {
  --color-brand-500: #3b82f6; /* 與 v3 完全一致 */
}

/* 進階做法：轉換為 oklch（可能有微小色差） */
@theme {
  --color-brand-500: oklch(0.62 0.19 250); /* 近似但非完全相同 */
}
```

## Checklist

- [ ] 能執行 `npx @tailwindcss/upgrade` 並理解其輸出。
- [ ] 能手動將 `tailwind.config.js` 轉換為 CSS `@theme` 配置。
- [ ] 能將 `@tailwind` 指令替換為 `@import "tailwindcss"`。
- [ ] 能將 v3 的 `require()` 插件引入改為 v4 的 `@plugin` 引入。
- [ ] 能將自訂 JavaScript 插件（addUtilities）轉換為 CSS `@utility`。
- [ ] 能識別和修正已重新命名/移除的工具類。
- [ ] 能執行視覺回歸比對確認遷移結果。

## Further Reading (official links only)

- [Tailwind CSS v4 Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide)
- [Tailwind CSS v4.0 Announcement](https://tailwindcss.com/blog/tailwindcss-v4)
- [Tailwind CSS - @tailwindcss/upgrade](https://github.com/tailwindlabs/tailwindcss/tree/main/packages/%40tailwindcss/upgrade)
- [Tailwind CSS - Functions and Directives](https://tailwindcss.com/docs/functions-and-directives)
- [Tailwind CSS GitHub Repository](https://github.com/tailwindlabs/tailwindcss)
