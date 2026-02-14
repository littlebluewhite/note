---
title: "Series Overview / 系列導讀"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "00"
level: beginner
stack: Tailwind CSS 4.1.x
prerequisites: [basic_computer_usage]
---
# Series Overview / 系列導讀

## Goal

本系列共 25 章，從零開始帶你掌握 Tailwind CSS v4 的完整知識體系。我們固定版本基準為 **Tailwind CSS 4.1.x**、**Vite 6.x**，框架整合部分使用 **React 19.2.x + Next.js 16** 與 **Svelte 5.50.x + SvelteKit 2.51.x**。Tailwind CSS v4 是一次重大改版，引入了 CSS-first 設定、`@theme` 指令、自動內容偵測、oklch 色彩空間等全新概念，與 v3 有根本性的差異。本章的目標是建立你的學習路徑，確認練習環境能正常運作，並為後續各章打下穩固基礎。

下一章 [01_utility_first_philosophy_and_mental_model](01_utility_first_philosophy_and_mental_model.md) 將深入探討 utility-first 的設計哲學與思維模型，幫助你理解為什麼 Tailwind 選擇這種方式來寫 CSS，以及它與傳統 CSS 方法論的核心差異。在進入各主題章節之前，請先確保本章的環境設定完成且可正常運作。

## Prerequisites

- 基本電腦操作能力（命令列、文字編輯器）。
- 已安裝 Node.js 20+ 與 npm 10+。
- 基礎 HTML 與 CSS 知識（知道 tag、class、選擇器的基本概念）。
- 一個文字編輯器（推薦 VS Code，並安裝 Tailwind CSS IntelliSense 擴充）。

## Core Concepts

### Tailwind CSS v4 vs v3 核心差異
- **何時選 v4**：新專案、想要更快的建構速度、希望用 CSS 原生語法設定。
- **何時不選 v4**：既有 v3 專案無迫切升級需求、依賴大量 v3 專用插件尚未遷移。

### CSS-first Configuration vs JavaScript Configuration
- **何時用 CSS-first**：v4 的預設方式，用 `@theme`、`@import "tailwindcss"` 直接在 CSS 中設定。所有新專案都應使用此方式。
- **何時不用 CSS-first**：只有在極特殊的向後相容情境（v3 遷移過渡期）才考慮保留 JS config。

### Vite Plugin vs PostCSS vs CLI
- **何時用 Vite Plugin**：使用 Vite 作為建構工具的專案（最推薦，速度最快）。
- **何時用 PostCSS**：非 Vite 建構工具（如 Webpack、Parcel）。
- **何時用 CLI**：不使用建構工具的簡單專案、快速原型。

### Play CDN vs 本地安裝
- **何時用 Play CDN**：快速測試概念、教學展示、不需要建構步驟的原型。
- **何時不用 Play CDN**：正式專案、需要自訂 @theme token、需要效能最佳化。

## Step-by-step

### 1. 確認 Node.js 版本

開啟終端機，執行以下命令確認版本。若版本低於 20，請先升級。

```bash
node -v
# 應顯示 v20.x.x 或更高
npm -v
# 應顯示 10.x.x 或更高
```

### 2. 建立 Vite 專案

使用 Vite 的 vanilla template 建立一個乾淨的練習專案。

```bash
npm create vite@latest tailwind-lab -- --template vanilla
cd tailwind-lab
```

### 3. 安裝 Tailwind CSS 與 Vite 插件

```bash
npm install tailwindcss @tailwindcss/vite
```

### 4. 設定 Vite 插件

開啟 `vite.config.js`，加入 Tailwind CSS 插件：

```js
// vite.config.js
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
});
```

### 5. 設定 CSS 入口

將 `style.css` 的內容替換為 Tailwind CSS 的 import 語句。這是 v4 的新方式，取代了 v3 的 `@tailwind base; @tailwind components; @tailwind utilities;`。

```css
/* style.css */
@import "tailwindcss";
```

### 6. 撰寫測試用 HTML

開啟 `index.html`，在 body 中加入測試用的 Tailwind utility class：

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Tailwind Lab</title>
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="bg-white p-8 rounded-xl shadow-lg text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">
        Tailwind CSS v4 Lab
      </h1>
      <p class="text-gray-600 mb-6">
        如果你看到這段文字有樣式，表示環境設定成功！
      </p>
      <span
        class="inline-block bg-blue-500 text-white px-4 py-2 rounded-lg font-medium"
      >
        環境就緒
      </span>
    </div>
  </body>
</html>
```

### 7. 啟動開發伺服器

```bash
npm run dev
```

打開瀏覽器，前往 `http://localhost:5173/`。你應該看到一個置中的白色卡片，帶有陰影和藍色按鈕。

### 8. 驗證 Hot Reload

在 `index.html` 中，將 `bg-blue-500` 改為 `bg-green-500`，存檔後確認瀏覽器自動更新顏色。

### 9. 安裝 VS Code 擴充

在 VS Code 中安裝 **Tailwind CSS IntelliSense** 擴充（`bradlc.vscode-tailwindcss`），確認 class 自動補全功能正常。

### 10. 建立版本快照記錄

在專案根目錄建立 `VERSION_SNAPSHOT.md` 記錄當前版本：

```bash
node -e "const p=require('./package.json'); console.log('tailwindcss:', p.dependencies.tailwindcss); console.log('@tailwindcss/vite:', p.dependencies['@tailwindcss/vite']);"
```

記錄輸出到 `VERSION_SNAPSHOT.md`：

```md
# Version Snapshot (2026-02-14)
- Node.js: v20.x.x
- Tailwind CSS: 4.1.x
- @tailwindcss/vite: 4.1.x
- Vite: 6.x.x
```

## Hands-on Lab

### Foundation

用上述步驟建立一個完整的 Tailwind CSS v4 + Vite 練習專案。

**驗收清單：**
- [ ] `npm run dev` 可正常啟動。
- [ ] 瀏覽器頁面可看到帶樣式的卡片。
- [ ] `style.css` 只有一行 `@import "tailwindcss";`。
- [ ] 修改 class 後瀏覽器自動更新。

### Advanced

在同一個專案中，建立第二個頁面 `about.html`，包含一個導覽列和內容區塊，使用至少 10 個不同的 utility class。

**驗收清單：**
- [ ] `about.html` 可在瀏覽器正常顯示。
- [ ] 使用了至少 10 種不同功能的 utility class（色彩、間距、字型、圓角、陰影等）。
- [ ] 導覽列有連結回首頁。

### Challenge

用 Tailwind Play CDN 方式建立一個獨立的 HTML 檔案（不需要 Node.js 環境），展示相同的卡片效果，並比較兩種方式的差異。

**驗收清單：**
- [ ] 純 HTML 檔案可在瀏覽器直接開啟。
- [ ] Play CDN script tag 正確載入。
- [ ] 能列出 Play CDN 與 Vite 安裝的至少 3 個差異。

Play CDN 方式：

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Tailwind Play CDN</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="bg-white p-8 rounded-xl shadow-lg text-center">
      <h1 class="text-3xl font-bold text-gray-900">Play CDN 版本</h1>
    </div>
  </body>
</html>
```

## Reference Solution

完整的專案結構與檔案內容：

```
tailwind-lab/
  index.html
  style.css
  vite.config.js
  package.json
```

**vite.config.js:**

```js
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
});
```

**style.css:**

```css
@import "tailwindcss";
```

**index.html:**

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Tailwind Lab</title>
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="bg-white p-8 rounded-xl shadow-lg text-center max-w-md">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">
        Tailwind CSS v4 Lab
      </h1>
      <p class="text-gray-600 mb-6">
        如果你看到這段文字有樣式，表示環境設定成功！
      </p>
      <span
        class="inline-block bg-blue-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600 transition-colors"
      >
        環境就緒
      </span>
    </div>
  </body>
</html>
```

## Common Pitfalls

1. **使用 v3 的 `@tailwind` 指令（v4 陷阱）**：在 v4 中，`@tailwind base; @tailwind components; @tailwind utilities;` 已被 `@import "tailwindcss";` 取代。如果你看到舊教學仍使用 `@tailwind` 指令，請忽略，這在 v4 中不再適用。

2. **Node.js 版本過低**：Tailwind CSS v4 需要 Node.js 20 以上。若使用較舊版本，安裝過程可能不會報錯，但執行時可能出現意外行為。

3. **忘記設定 Vite 插件**：只安裝 `tailwindcss` 但沒有在 `vite.config.js` 中加入 `@tailwindcss/vite` 插件，導致 utility class 完全不生效。

4. **CSS 檔案未被 HTML 引用**：在 `index.html` 中忘記加上 `<link rel="stylesheet" href="/style.css" />`，導致頁面沒有任何樣式。

5. **混淆 Play CDN 與正式安裝**：Play CDN 適合快速測試，但不支援 `@theme` 自訂、不支援 CSS-first configuration、效能較差。正式專案務必使用 Vite 或 PostCSS 安裝。

## Checklist

- [ ] Node.js >= 20 已安裝且可在終端確認。
- [ ] `npm create vite@latest` 可正常執行。
- [ ] `tailwindcss` 與 `@tailwindcss/vite` 已安裝在 `dependencies`。
- [ ] `vite.config.js` 已正確設定 Tailwind CSS 插件。
- [ ] `style.css` 使用 `@import "tailwindcss";` 而非舊版 `@tailwind` 指令。
- [ ] `npm run dev` 後瀏覽器可看到帶樣式的頁面。
- [ ] 修改 HTML 中的 utility class 後，瀏覽器自動 Hot Reload。
- [ ] VS Code Tailwind CSS IntelliSense 擴充已安裝且可自動補全。

## Further Reading (official links only)

- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
- [Installing with Vite](https://tailwindcss.com/docs/installation/vite)
- [Tailwind CSS GitHub Repository](https://github.com/tailwindlabs/tailwindcss)
- [Tailwind CSS Releases](https://github.com/tailwindlabs/tailwindcss/releases)
