---
title: "Performance Optimization and Production Build / 效能最佳化與正式建置"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "19"
level: advanced
stack: Tailwind CSS 4.1.x + Vite 6.x
prerequisites: [18_plugins_extensions_and_ecosystem]
---

# Performance Optimization and Production Build / 效能最佳化與正式建置

## Goal

在前一章 [[18_plugins_extensions_and_ecosystem]] 中，我們學會了如何使用官方插件和社群工具擴展 Tailwind CSS 的功能。隨著專案規模增長、插件增加，CSS 輸出的大小和建置效能就成為關鍵議題。本章將深入探討 Tailwind CSS v4 的效能架構，包括全新的 Oxide 引擎、JIT 即時編譯、CSS cascade layers、以及生產環境的最佳化策略。

v4 在效能方面帶來了根本性的提升：Oxide 引擎用 Rust 重寫，完整建置速度提升 5 倍，增量建置速度提升 100 倍。JIT 不再是可選功能，而是唯一的運作模式。本章將教你如何分析 CSS 輸出大小、理解 layer 排序機制、實施 critical CSS 策略、使用 Lighthouse 檢測效能指標，並透過實際量測驗證最佳化效果。在下一章 [[20_tailwind_with_react_component_patterns]] 中，我們將把這些效能知識應用到 React 框架整合的實務場景中。

## Prerequisites

- 已完成第 18 章，理解 Tailwind 插件生態系。
- 熟悉 Vite 建置工具的基本配置和運作原理。
- 理解 CSS cascade 和 specificity 的基本概念。
- 知道瀏覽器 DevTools 的基本操作（Network、Performance 面板）。
- 具備 npm scripts 和 CLI 操作能力。

## Core Concepts

### 1. Oxide Engine / Oxide 引擎

v4 的 Oxide 引擎是用 Rust 撰寫的全新核心，取代了 v3 的 JavaScript 實作。這帶來了顯著的效能提升。

**何時關注 Oxide 引擎效能：**
- 大型專案（數百個元件檔案）建置時間過長。
- 開發時 hot reload 延遲明顯。
- CI/CD pipeline 建置時間是瓶頸。

**何時不需要額外最佳化：**
- 小型專案（< 50 個檔案），v4 預設效能已足夠。
- 使用 Vite 開發伺服器，增量建置已極快。
- CSS 輸出大小在合理範圍內（< 50KB gzipped）。

### 2. JIT Always-On / JIT 始終啟用

v4 的 JIT（Just-In-Time）引擎始終啟用，不需要任何配置。它按需生成 CSS，只輸出專案中實際使用的工具類。

**何時利用 JIT 特性：**
- 使用 arbitrary values（`w-[137px]`、`bg-[#1a2b3c]`）而不擔心 CSS 膨脹。
- 大量使用 responsive 和 stateful 變體組合。
- 需要在開發和生產環境保持一致的 CSS 輸出。

**何時注意 JIT 限制：**
- 動態組合 class 名稱（如 `bg-${color}-500`）時，JIT 無法偵測，需要用 safelist。
- 在 CMS 或資料庫儲存的 HTML 中使用 Tailwind class 時，需確保內容偵測能涵蓋。
- 使用 JavaScript 動態建立完整 class 名稱時，必須保持完整字串。

### 3. CSS Cascade Layers / CSS 級聯層

v4 使用真正的 CSS `@layer` 來組織輸出，這與 v3 的虛擬 layer 概念不同。真正的 CSS cascade layers 提供了更可預測的 specificity 行為。

**何時使用 layer 知識：**
- 自訂 CSS 與 Tailwind 工具類發生 specificity 衝突。
- 需要確保第三方 CSS 不會覆蓋 Tailwind 樣式。
- 需要在 base、components、utilities 三層之間正確放置自訂樣式。

**何時不需要手動管理 layers：**
- 純粹使用 Tailwind 工具類，沒有額外的自訂 CSS。
- 專案中沒有第三方 CSS 框架。
- `@utility` 和 `@layer components` 已滿足需求。

### 4. Critical CSS and Code Splitting / Critical CSS 與程式碼分割

Critical CSS 策略是將首屏渲染所需的最小 CSS 內聯到 HTML 中，其餘 CSS 非同步載入。

**何時實施 critical CSS：**
- Lighthouse Performance 分數中 FCP（First Contentful Paint）需要最佳化。
- 頁面有大量 above-the-fold 內容需要快速渲染。
- 專案是伺服器端渲染（SSR）或靜態站點生成（SSG）。

**何時不需要 critical CSS：**
- 單頁應用（SPA）初始載入後不再重新載入 CSS。
- Tailwind CSS 輸出已非常小（< 15KB gzipped）。
- 使用 HTTP/2 Server Push 或預載入策略。

## Step-by-step

### 步驟 1：量測基準 CSS 輸出大小

首先建立量測基準，了解目前的 CSS 輸出狀況：

```bash
# 建置生產版本
npx vite build

# 檢查 CSS 輸出檔案大小
ls -lh dist/assets/*.css

# 使用 gzip 測試壓縮後大小
gzip -k dist/assets/*.css
ls -lh dist/assets/*.css.gz
```

也可以在 `vite.config.ts` 中配置建置報告：

```ts
// vite.config.ts
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    // 啟用 CSS 壓縮（預設已開啟）
    cssMinify: true,
    // 顯示建置大小報告
    reportCompressedSize: true,
  },
});
```

驗證：記錄未壓縮和 gzipped 後的 CSS 大小作為基準值。

### 步驟 2：理解 v4 的自動內容偵測

v4 不再需要手動設定 `content: [...]`，而是自動偵測專案中的模板檔案。了解偵測機制和限制：

```css
/* src/app.css */
@import "tailwindcss";

/* v4 自動偵測同目錄及子目錄的所有模板檔案 */
/* 支援的副檔名：.html, .js, .jsx, .ts, .tsx, .svelte, .vue, .md 等 */

/* 如需排除特定路徑，使用 @source 指令 */
@source "../node_modules/my-ui-lib/src/**/*.tsx";
/* 上方指令會額外掃描 node_modules 中的特定路徑 */
```

處理動態 class 名稱：

```tsx
// 錯誤：JIT 無法偵測動態組合的 class
const color = "blue";
const bgClass = `bg-${color}-500`; // JIT 無法追蹤

// 正確：使用完整的 class 字串
const bgClass = color === "blue" ? "bg-blue-500" : "bg-red-500";

// 正確：使用物件映射
const colorMap: Record<string, string> = {
  blue: "bg-blue-500",
  red: "bg-red-500",
  green: "bg-green-500",
};
const bgClass = colorMap[color];
```

驗證：建置後確認 CSS 輸出只包含實際使用的工具類。

### 步驟 3：分析 CSS Cascade Layers 結構

v4 的 CSS 輸出使用真正的 CSS `@layer`：

```css
/* v4 產生的 CSS 結構（簡化示意） */
@layer theme, base, components, utilities;

@layer theme {
  :root {
    --color-blue-500: oklch(0.62 0.19 250);
    /* ... theme tokens ... */
  }
}

@layer base {
  *, ::before, ::after {
    box-sizing: border-box;
    /* ... base resets ... */
  }
}

@layer components {
  /* 你的 @layer components 中的自訂樣式 */
}

@layer utilities {
  /* 所有使用的 Tailwind 工具類 */
  .flex { display: flex; }
  .p-4 { padding: 1rem; }
  /* ... */
}
```

理解 layer 優先權（由低到高）：`theme` < `base` < `components` < `utilities`

```css
/* 自訂 CSS 應放在正確的 layer 中 */

/* 全域重置和基礎樣式 */
@layer base {
  body {
    font-family: var(--font-sans);
    line-height: 1.6;
  }
  h1, h2, h3 {
    line-height: 1.2;
  }
}

/* 可重用的元件樣式 */
@layer components {
  .card {
    border-radius: 0.75rem;
    padding: 1.5rem;
    background: white;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }
}

/* 單一用途工具類（優先權最高） */
/* 使用 @utility 自動放在 utilities layer */
```

驗證：在 DevTools 中檢查 CSS layer 結構，確認自訂樣式位於正確的 layer。

### 步驟 4：最佳化 CSS 輸出大小

識別並消除不必要的 CSS 輸出：

```css
/* src/app.css */
@import "tailwindcss";

/* 策略 1：停用不需要的 Tailwind 預設主題值 */
@theme {
  /* 清除所有預設色彩，只保留專案使用的色彩 */
  --color-*: initial;

  /* 重新定義專案色彩 */
  --color-primary: oklch(0.62 0.19 250);
  --color-secondary: oklch(0.55 0.15 280);
  --color-neutral-50: oklch(0.98 0 0);
  --color-neutral-100: oklch(0.96 0 0);
  --color-neutral-200: oklch(0.92 0 0);
  --color-neutral-300: oklch(0.87 0 0);
  --color-neutral-400: oklch(0.7 0 0);
  --color-neutral-500: oklch(0.55 0 0);
  --color-neutral-600: oklch(0.44 0 0);
  --color-neutral-700: oklch(0.37 0 0);
  --color-neutral-800: oklch(0.27 0 0);
  --color-neutral-900: oklch(0.2 0 0);
  --color-neutral-950: oklch(0.14 0 0);

  --color-white: #ffffff;
  --color-black: #000000;
}
```

```css
/* 策略 2：避免過度使用 arbitrary values */
/* 每個唯一的 arbitrary value 都會生成一條新的 CSS 規則 */

/* 不佳：大量一次性的 arbitrary values */
/* class="w-[137px] h-[89px] mt-[13px] ml-[27px]" */

/* 較好：使用 theme tokens 定義重複使用的值 */
@theme {
  --spacing-card-width: 137px;
  --spacing-card-height: 89px;
}
/* class="w-(--card-width) h-(--card-height) mt-3 ml-7" */
```

驗證：重新建置後比較 CSS 大小，確認有明顯減少。

### 步驟 5：設定 CSS 壓縮和最小化

Vite 在生產建置時預設會最小化 CSS。確認配置正確：

```ts
// vite.config.ts
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    cssMinify: true, // 預設為 true，使用 esbuild 最小化
    // 或使用 lightningcss 進行更進階的最小化
    // cssMinify: 'lightningcss',
    rollupOptions: {
      output: {
        // CSS 分割：按入口點分割 CSS
        assetFileNames: "assets/[name]-[hash][extname]",
      },
    },
  },
  css: {
    // lightningcss 可提供更好的壓縮和現代 CSS 轉換
    transformer: "lightningcss",
    lightningcss: {
      drafts: {
        customMedia: true, // 支援 @custom-media
      },
    },
  },
});
```

驗證：比較 `cssMinify: true` 和不壓縮的 CSS 大小差異。

### 步驟 6：實施 Critical CSS 策略

對於 SSR/SSG 應用，可以使用 `critters` 或類似工具提取 critical CSS：

```bash
npm install critters --save-dev
```

在 Vite 專案中手動實施簡易的 critical CSS 策略：

```html
<!-- index.html -->
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <!-- Critical CSS：內聯首屏所需的最小樣式 -->
  <style>
    /* 這些樣式確保首屏渲染不被 CSS 阻塞 */
    body {
      margin: 0;
      font-family: system-ui, -apple-system, sans-serif;
      background-color: #ffffff;
    }
    .hero {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  </style>

  <!-- 非 critical CSS：非同步載入 -->
  <link
    rel="preload"
    href="/src/app.css"
    as="style"
    onload="this.onload=null;this.rel='stylesheet'"
  />
  <noscript>
    <link rel="stylesheet" href="/src/app.css" />
  </noscript>
</head>
<body>
  <div class="hero">
    <h1 class="text-4xl font-bold">快速渲染</h1>
  </div>
  <!-- 下方內容不在首屏，CSS 可非同步載入 -->
</body>
</html>
```

在 Next.js 中，critical CSS 由框架自動處理：

```tsx
// app/layout.tsx (Next.js App Router)
// Next.js 自動進行 CSS 最佳化，包括：
// - 自動內聯小型 CSS
// - 按頁面分割 CSS
// - 移除未使用的 CSS
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-Hant">
      <body>{children}</body>
    </html>
  );
}
```

驗證：使用 Lighthouse 檢查 FCP 指標，確認 critical CSS 策略有效。

### 步驟 7：使用 Lighthouse 檢測 CSS 效能

在 Chrome DevTools 中執行 Lighthouse 審計：

```
1. 開啟 Chrome DevTools (F12)
2. 切換到 Lighthouse 面板
3. 選擇 "Performance" 和 "Best Practices" 類別
4. 選擇 "Mobile" 模式（更嚴格的標準）
5. 點擊 "Analyze page load"
```

關注以下 CSS 相關指標：

```
- FCP (First Contentful Paint)：< 1.8s (Good)
- LCP (Largest Contentful Paint)：< 2.5s (Good)
- CLS (Cumulative Layout Shift)：< 0.1 (Good)
- "Reduce unused CSS" 建議
- "Eliminate render-blocking resources" 建議
```

使用 Coverage 面板分析 CSS 使用率：

```
1. 開啟 DevTools
2. Cmd+Shift+P → 輸入 "Coverage"
3. 點擊 "Start instrumenting coverage and reload page"
4. 查看 CSS 檔案的使用百分比
5. 紅色部分表示首頁載入時未使用的 CSS
```

驗證：Lighthouse Performance 分數 >= 90，且無 CSS 相關的嚴重警告。

### 步驟 8：Tree-shaking 和 Purging 驗證

v4 的 JIT 引擎天然具備 tree-shaking 能力。驗證它的效果：

```bash
# 步驟 1：建置前記錄
npx vite build 2>&1 | tee build-before.log

# 步驟 2：在 HTML 中加入大量不同的 Tailwind class
# 例如使用所有 breakpoint + 所有 state 的組合

# 步驟 3：再次建置
npx vite build 2>&1 | tee build-after.log

# 步驟 4：比較差異
diff build-before.log build-after.log
```

建立一個測試頁面，驗證未使用的 class 不會出現在輸出中：

```html
<!-- test-treeshake.html -->
<!-- 只使用了少量工具類 -->
<div class="flex items-center gap-4 p-8 bg-white rounded-lg shadow-md">
  <h1 class="text-2xl font-bold text-gray-900">Tree-shaking 測試</h1>
  <p class="text-gray-600">只有這些 class 應該出現在 CSS 輸出中。</p>
</div>
```

```bash
# 建置後搜尋 CSS 輸出中是否包含未使用的 class
# 例如 grid-cols-12 不應該出現
grep "grid-cols-12" dist/assets/*.css
# 如果沒有結果，表示 tree-shaking 正常運作
```

驗證：確認 CSS 輸出只包含 HTML 中實際使用的工具類。

### 步驟 9：多頁面 CSS 分割策略

對於多頁面專案，使用 Vite 的 code splitting 分割 CSS：

```ts
// vite.config.ts
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    rollupOptions: {
      input: {
        main: "index.html",
        about: "about.html",
        blog: "blog.html",
      },
      output: {
        // 每個入口點生成獨立的 CSS
        assetFileNames: "assets/[name]-[hash][extname]",
      },
    },
    // 設定 CSS code splitting
    cssCodeSplit: true,
  },
});
```

驗證：建置後確認每個頁面有獨立的 CSS 檔案，大小不同。

### 步驟 10：建立效能監控流程

建立持續的 CSS 效能監控：

```json
// package.json
{
  "scripts": {
    "build": "vite build",
    "build:analyze": "vite build && node scripts/analyze-css.mjs",
    "lighthouse": "npx lighthouse http://localhost:4173 --output=json --output-path=./lighthouse-report.json --only-categories=performance"
  }
}
```

```js
// scripts/analyze-css.mjs
import { readdir, stat } from "node:fs/promises";
import { join } from "node:path";
import { createReadStream } from "node:fs";
import { createGzip } from "node:zlib";

const distDir = "dist/assets";

async function analyzeCss() {
  const files = await readdir(distDir);
  const cssFiles = files.filter((f) => f.endsWith(".css"));

  console.log("\n=== CSS Output Analysis ===\n");

  for (const file of cssFiles) {
    const filePath = join(distDir, file);
    const stats = await stat(filePath);
    const sizeKB = (stats.size / 1024).toFixed(2);

    // 估算 gzip 大小
    const gzipSize = await getGzipSize(filePath);
    const gzipKB = (gzipSize / 1024).toFixed(2);

    console.log(`File: ${file}`);
    console.log(`  Raw:  ${sizeKB} KB`);
    console.log(`  Gzip: ${gzipKB} KB`);

    // 閾值警告
    if (gzipSize > 50 * 1024) {
      console.log("  WARNING: Gzipped CSS > 50KB, consider optimization");
    } else if (gzipSize > 30 * 1024) {
      console.log("  INFO: Gzipped CSS > 30KB, monitor growth");
    } else {
      console.log("  OK: CSS size is within acceptable range");
    }
    console.log();
  }
}

function getGzipSize(filePath) {
  return new Promise((resolve) => {
    let size = 0;
    createReadStream(filePath)
      .pipe(createGzip())
      .on("data", (chunk) => {
        size += chunk.length;
      })
      .on("end", () => resolve(size));
  });
}

analyzeCss().catch(console.error);
```

驗證：執行 `npm run build:analyze`，確認 CSS 大小報告正確輸出，並附帶閾值警告。

## Hands-on Lab

### Foundation / 基礎練習

**任務：量測並記錄專案 CSS 輸出大小**

1. 建置 Vite + Tailwind v4 專案的生產版本。
2. 記錄 CSS 檔案的未壓縮大小和 gzipped 大小。
3. 使用 Chrome DevTools Coverage 面板檢查 CSS 使用率。
4. 在 Lighthouse 中執行 Performance 審計。

**驗收清單：**
- [ ] 記錄了 CSS raw size 和 gzip size（單位 KB）。
- [ ] Coverage 面板顯示 CSS 使用率百分比。
- [ ] Lighthouse Performance 分數已記錄。
- [ ] 確認無 "Reduce unused CSS" 警告（或已了解原因）。
- [ ] 建置時間已記錄（秒為單位）。

### Advanced / 進階練習

**任務：使用 @theme 重置減少 CSS 輸出大小**

1. 記錄目前 CSS 輸出大小（基準值）。
2. 使用 `--color-*: initial` 清除預設色彩。
3. 只定義專案實際使用的色彩（5-10 個語義色）。
4. 重新建置並比較大小差異。
5. 確認所有頁面視覺效果不受影響。

**驗收清單：**
- [ ] 基準值和最佳化後的 CSS 大小都已記錄。
- [ ] 色彩 token 從全套預設值減少到 5-10 個語義色。
- [ ] CSS 輸出大小減少了（記錄百分比）。
- [ ] 所有頁面功能和視覺效果正常。
- [ ] `npm run dev` 開發伺服器無錯誤。

### Challenge / 挑戰練習

**任務：建立多頁面專案的完整效能最佳化流程**

1. 建立一個包含首頁、關於頁、部落格列表頁、部落格文章頁的多頁面專案。
2. 為每個頁面配置獨立的 CSS code splitting。
3. 實施 critical CSS 策略（首屏 CSS 內聯）。
4. 建立 `scripts/analyze-css.mjs` 效能分析腳本。
5. 在 package.json 中加入 `build:analyze` 和 `lighthouse` 腳本。
6. 執行完整的最佳化流程並記錄前後對比數據。

**驗收清單：**
- [ ] 4 個頁面各自有獨立的 CSS 輸出。
- [ ] 首頁的 critical CSS 已內聯到 `<style>` 標籤。
- [ ] `npm run build:analyze` 輸出每個 CSS 檔案的大小報告。
- [ ] 每個 CSS 檔案的 gzipped 大小 < 30KB。
- [ ] Lighthouse Performance 分數 >= 90。
- [ ] 所有頁面在 3G 模擬網路下 FCP < 2 秒。

## Reference Solution

完整的多頁面效能最佳化專案：

```ts
// vite.config.ts
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    cssMinify: true,
    reportCompressedSize: true,
    cssCodeSplit: true,
    rollupOptions: {
      input: {
        main: "index.html",
        about: "about.html",
        blog: "blog/index.html",
        "blog-post": "blog/post.html",
      },
      output: {
        assetFileNames: "assets/[name]-[hash][extname]",
      },
    },
  },
});
```

```css
/* src/app.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";

/* 重置預設 theme，只保留專案需要的值 */
@theme {
  /* 清除所有預設色彩 */
  --color-*: initial;

  /* 語義色系統 */
  --color-primary: oklch(0.62 0.19 250);
  --color-primary-light: oklch(0.72 0.15 250);
  --color-primary-dark: oklch(0.52 0.22 250);

  --color-surface: oklch(0.99 0 0);
  --color-surface-alt: oklch(0.96 0 0);
  --color-surface-dark: oklch(0.15 0 0);

  --color-text: oklch(0.2 0 0);
  --color-text-muted: oklch(0.55 0 0);
  --color-text-inverse: oklch(0.98 0 0);

  --color-border: oklch(0.87 0 0);
  --color-border-focus: oklch(0.62 0.19 250);

  --color-success: oklch(0.6 0.18 145);
  --color-warning: oklch(0.75 0.15 85);
  --color-error: oklch(0.58 0.22 25);

  --color-white: #ffffff;
  --color-black: #000000;

  /* 清除不需要的字型 */
  --font-*: initial;
  --font-sans: system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
}
```

```html
<!-- index.html -->
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>效能最佳化 Demo</title>

  <!-- Critical CSS -->
  <style>
    body { margin: 0; font-family: system-ui, -apple-system, sans-serif; }
    .hero { min-height: 100vh; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 1rem; }
    .hero h1 { font-size: 3rem; font-weight: 800; }
    .nav { display: flex; gap: 2rem; padding: 1rem 2rem; }
  </style>

  <!-- Async CSS -->
  <link rel="preload" href="/src/app.css" as="style" onload="this.onload=null;this.rel='stylesheet'" />
  <noscript><link rel="stylesheet" href="/src/app.css" /></noscript>
</head>
<body class="bg-surface text-text">

  <nav class="nav border-b border-border">
    <a href="/" class="font-semibold text-primary">首頁</a>
    <a href="/about.html" class="text-text-muted hover:text-primary transition-colors">關於</a>
    <a href="/blog/" class="text-text-muted hover:text-primary transition-colors">部落格</a>
  </nav>

  <section class="hero">
    <h1 class="text-5xl font-extrabold text-primary">
      效能最佳化
    </h1>
    <p class="text-xl text-text-muted max-w-2xl text-center px-4">
      Tailwind CSS v4 + Vite 的生產建置最佳化實踐。
      CSS 輸出精簡、載入快速、效能卓越。
    </p>
    <div class="flex gap-4 mt-8">
      <a
        href="/blog/"
        class="bg-primary text-text-inverse px-6 py-3 rounded-lg font-semibold
               hover:bg-primary-dark transition-colors"
      >
        開始閱讀
      </a>
      <a
        href="/about.html"
        class="border border-border px-6 py-3 rounded-lg font-semibold
               hover:bg-surface-alt transition-colors"
      >
        了解更多
      </a>
    </div>
  </section>

  <section class="max-w-5xl mx-auto px-6 py-16 grid grid-cols-1 md:grid-cols-3 gap-8">
    <div class="p-6 rounded-xl bg-surface-alt border border-border">
      <h3 class="text-lg font-semibold mb-2">Oxide 引擎</h3>
      <p class="text-text-muted">Rust 驅動，建置速度提升 5 倍。</p>
    </div>
    <div class="p-6 rounded-xl bg-surface-alt border border-border">
      <h3 class="text-lg font-semibold mb-2">JIT 始終開啟</h3>
      <p class="text-text-muted">按需生成，零冗餘 CSS。</p>
    </div>
    <div class="p-6 rounded-xl bg-surface-alt border border-border">
      <h3 class="text-lg font-semibold mb-2">CSS Layers</h3>
      <p class="text-text-muted">真正的 CSS cascade layers。</p>
    </div>
  </section>

</body>
</html>
```

```json
{
  "name": "tailwind-perf-demo",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "build:analyze": "vite build && node scripts/analyze-css.mjs",
    "lighthouse": "vite build && vite preview & sleep 3 && npx lighthouse http://localhost:4173 --output=html --output-path=./lighthouse-report.html --only-categories=performance && kill %1"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.1.0",
    "tailwindcss": "^4.1.0",
    "vite": "^6.0.0"
  },
  "dependencies": {
    "@tailwindcss/typography": "^0.5.0"
  }
}
```

```js
// scripts/analyze-css.mjs
import { readdir, stat, readFile } from "node:fs/promises";
import { join } from "node:path";
import { gzipSync } from "node:zlib";

const distDir = "dist/assets";
const WARN_THRESHOLD_KB = 50;
const INFO_THRESHOLD_KB = 30;

async function analyzeCss() {
  const files = await readdir(distDir);
  const cssFiles = files.filter((f) => f.endsWith(".css"));

  console.log("\n========================================");
  console.log("  CSS Output Analysis Report");
  console.log("  Generated: " + new Date().toISOString());
  console.log("========================================\n");

  let totalRaw = 0;
  let totalGzip = 0;

  for (const file of cssFiles) {
    const filePath = join(distDir, file);
    const content = await readFile(filePath);
    const rawSize = content.length;
    const gzipSize = gzipSync(content).length;

    totalRaw += rawSize;
    totalGzip += gzipSize;

    const rawKB = (rawSize / 1024).toFixed(2);
    const gzipKB = (gzipSize / 1024).toFixed(2);
    const ratio = ((gzipSize / rawSize) * 100).toFixed(1);

    console.log(`  ${file}`);
    console.log(`    Raw:        ${rawKB} KB`);
    console.log(`    Gzipped:    ${gzipKB} KB (${ratio}% of raw)`);

    const gzipKBNum = gzipSize / 1024;
    if (gzipKBNum > WARN_THRESHOLD_KB) {
      console.log(`    Status:     WARN - exceeds ${WARN_THRESHOLD_KB}KB threshold`);
    } else if (gzipKBNum > INFO_THRESHOLD_KB) {
      console.log(`    Status:     INFO - approaching ${WARN_THRESHOLD_KB}KB threshold`);
    } else {
      console.log(`    Status:     OK`);
    }
    console.log();
  }

  console.log("----------------------------------------");
  console.log(`  Total Raw:    ${(totalRaw / 1024).toFixed(2)} KB`);
  console.log(`  Total Gzip:   ${(totalGzip / 1024).toFixed(2)} KB`);
  console.log("========================================\n");
}

analyzeCss().catch(console.error);
```

## Common Pitfalls

### 1. v4 特有：仍在設定 content 路徑

v4 自動偵測模板檔案，不需要手動設定 `content`。如果你發現某些 class 沒有生成，問題通常不是 content 配置，而是動態 class 名稱或檔案不在偵測範圍內。

```css
/* 不需要：v4 自動偵測 */
/* content: ['./src/**/*.{html,js,ts,tsx}'] */

/* 如需擴展偵測範圍，使用 @source */
@source "../node_modules/some-lib/dist/**/*.js";
```

### 2. 動態 class 名稱導致 JIT 無法生成

JIT 透過靜態分析文字來偵測 class 名稱，動態字串拼接會導致遺漏。

```tsx
// 錯誤：JIT 無法追蹤
const sizes = ["sm", "md", "lg"];
sizes.map(s => `text-${s}`); // text-sm, text-md 等不會被生成

// 正確：使用完整字串
const sizeClasses = {
  sm: "text-sm",
  md: "text-base",
  lg: "text-lg",
};
```

### 3. 過度使用 @layer 導致 specificity 問題

將自訂 CSS 放在錯誤的 layer 中會導致意想不到的覆蓋行為。

```css
/* 錯誤：把需要高優先權的樣式放在 base layer */
@layer base {
  .important-override {
    color: red !important; /* 不得不用 !important */
  }
}

/* 正確：根據用途選擇正確的 layer */
@layer utilities {
  /* 使用 @utility 定義，自動在 utilities layer */
}
```

### 4. 未壓縮部署 CSS 到生產環境

Vite 建置時預設最小化 CSS，但伺服器端的 gzip/brotli 壓縮需要另外配置。

```nginx
# Nginx 配置範例
gzip on;
gzip_types text/css application/javascript;
gzip_min_length 256;

# 或使用 Brotli（更好的壓縮率）
brotli on;
brotli_types text/css application/javascript;
```

### 5. 在 CI/CD 中未快取 Tailwind 建置產物

v4 的增量建置很快，但 CI 環境每次都是全新建置。確保快取 `node_modules` 和建置快取。

```yaml
# GitHub Actions 範例
- uses: actions/cache@v4
  with:
    path: |
      node_modules
      .vite
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

## Checklist

- [ ] 能執行生產建置並量測 CSS 輸出大小（raw + gzipped）。
- [ ] 理解 v4 的 JIT 始終開啟機制，不需要額外配置。
- [ ] 理解 CSS cascade layers 結構（theme < base < components < utilities）。
- [ ] 能使用 `--color-*: initial` 等重置語法減少預設 theme 的 CSS 輸出。
- [ ] 能使用 Lighthouse 和 Coverage 面板分析 CSS 效能。
- [ ] 避免動態 class 名稱拼接，使用完整字串或物件映射。
- [ ] 能建立 CSS 大小分析腳本，納入 CI/CD 流程。

## Further Reading (official links only)

- [Tailwind CSS v4.0 - Performance](https://tailwindcss.com/blog/tailwindcss-v4#performance)
- [Tailwind CSS - Detecting Classes in Source Files](https://tailwindcss.com/docs/detecting-classes-in-source-files)
- [Tailwind CSS - Using CSS Layers](https://tailwindcss.com/docs/adding-custom-styles#using-css-layers)
- [Tailwind CSS - Functions and Directives](https://tailwindcss.com/docs/functions-and-directives)
- [Tailwind CSS GitHub Repository](https://github.com/tailwindlabs/tailwindcss)
