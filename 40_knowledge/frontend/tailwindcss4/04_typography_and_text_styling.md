---
title: "Typography and Text Styling / 字體排印與文字樣式"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "04"
level: beginner
stack: Tailwind CSS 4.1.x
prerequisites: [03_colors_backgrounds_and_opacity]
---
# Typography and Text Styling / 字體排印與文字樣式

## Goal

在上一章 [03_colors_backgrounds_and_opacity](03_colors_backgrounds_and_opacity.md) 中，我們掌握了 Tailwind 的色彩系統。現在要進入同樣頻繁使用的領域：**字體排印（Typography）**。良好的字體排印是 UI 品質的關鍵——字型選擇、字級、行高、字距、對齊方式，這些細節決定了文字的可讀性與視覺層次。Tailwind 提供了一套完整的 typography utilities，涵蓋 `font-*`、`text-*`、`leading-*`、`tracking-*` 等，並且在 v4 中支援了 `text-balance` 和 `text-pretty` 等現代 CSS 特性。

本章還會介紹如何透過 `@theme` 自訂字型 token，以及 `@tailwindcss/typography` 插件如何讓 Markdown/CMS 內容自動具備漂亮的排版。下一章 [05_spacing_sizing_and_box_model](05_spacing_sizing_and_box_model.md) 將探討間距與尺寸系統，完成 UI 元素的空間控制。

## Prerequisites

- 已完成第 03 章。
- 理解 CSS 的 `font-family`、`font-size`、`line-height` 屬性。
- 知道 `rem` 與 `px` 單位的差異。

## Core Concepts

### font-size Utilities (text-*) vs Arbitrary Font Sizes
- **何時用 text-* utilities**：大多數情況。Tailwind 的 `text-sm`、`text-base`、`text-lg`、`text-xl` 等預設值經過精心設計，每個尺寸都搭配了合適的 line-height，能確保視覺和諧。
- **何時用 arbitrary values**：設計稿要求極精確的字級（如 `text-[15px]`、`text-[1.375rem]`），且與預設值不匹配時。但應優先嘗試最接近的預設值。

### font-family Tokens vs System Fonts
- **何時自訂 font-family token**：品牌設計有指定字型（如 Inter、Noto Sans TC），或需要在 `@theme` 中統一管理。
- **何時用系統字型**：追求載入速度、不需要特定品牌字型。Tailwind 預設的 `font-sans` 已是優秀的系統字型堆疊。

### text-balance / text-pretty vs 手動排版
- **何時用 text-balance**：標題文字，需要每行長度盡量均等，避免最後一行只有幾個字的「寡行」問題。
- **何時用 text-pretty**：段落文字，啟用瀏覽器的段落最佳化演算法，減少不自然的斷行。
- **何時不用**：極短的文字（單行）或需要精確控制換行的場景。

### @tailwindcss/typography Plugin vs 手動設定
- **何時用 plugin**：需要渲染 Markdown、CMS 富文字內容、部落格文章等無法逐一加 utility class 的 HTML。
- **何時不用**：完全自行控制的 UI 元件，每個元素都有明確的 utility class。

## Step-by-step

### 1. 字級系統總覽

建立一個字級展示頁面：

```html
<div class="p-8 space-y-4">
  <p class="text-xs text-gray-500">text-xs — 0.75rem / 1rem</p>
  <p class="text-sm text-gray-600">text-sm — 0.875rem / 1.25rem</p>
  <p class="text-base text-gray-700">text-base — 1rem / 1.5rem</p>
  <p class="text-lg text-gray-700">text-lg — 1.125rem / 1.75rem</p>
  <p class="text-xl text-gray-800">text-xl — 1.25rem / 1.75rem</p>
  <p class="text-2xl text-gray-800">text-2xl — 1.5rem / 2rem</p>
  <p class="text-3xl text-gray-900">text-3xl — 1.875rem / 2.25rem</p>
  <p class="text-4xl text-gray-900 font-bold">text-4xl — 2.25rem / 2.5rem</p>
  <p class="text-5xl text-gray-900 font-bold">text-5xl — 3rem</p>
  <p class="text-6xl text-gray-900 font-extrabold">text-6xl — 3.75rem</p>
  <p class="text-7xl text-gray-900 font-extrabold">text-7xl — 4.5rem</p>
  <p class="text-8xl text-gray-900 font-black">text-8xl — 6rem</p>
  <p class="text-9xl text-gray-900 font-black">text-9xl — 8rem</p>
</div>
```

### 2. 字重與字型

```html
<div class="p-8 space-y-3">
  <p class="font-thin">font-thin (100)</p>
  <p class="font-extralight">font-extralight (200)</p>
  <p class="font-light">font-light (300)</p>
  <p class="font-normal">font-normal (400)</p>
  <p class="font-medium">font-medium (500)</p>
  <p class="font-semibold">font-semibold (600)</p>
  <p class="font-bold">font-bold (700)</p>
  <p class="font-extrabold">font-extrabold (800)</p>
  <p class="font-black">font-black (900)</p>
</div>

<div class="p-8 space-y-3">
  <p class="font-sans">font-sans — 預設無襯線字型</p>
  <p class="font-serif">font-serif — 襯線字型</p>
  <p class="font-mono">font-mono — 等寬字型</p>
</div>
```

### 3. 行高（Line Height）控制

```html
<div class="p-8 space-y-8 max-w-lg">
  <div>
    <p class="text-sm text-gray-400 mb-1">leading-none (1)</p>
    <p class="text-lg leading-none">
      行高為 1 的文字段落。這在多行時會讓文字緊密相連，通常只用於單行標題。
    </p>
  </div>
  <div>
    <p class="text-sm text-gray-400 mb-1">leading-tight (1.25)</p>
    <p class="text-lg leading-tight">
      行高為 1.25 的文字段落。適合標題和短段落，閱讀起來緊湊但仍清晰。
    </p>
  </div>
  <div>
    <p class="text-sm text-gray-400 mb-1">leading-normal (1.5)</p>
    <p class="text-lg leading-normal">
      行高為 1.5 的文字段落。這是大多數內文的理想行高，閱讀最為舒適。
    </p>
  </div>
  <div>
    <p class="text-sm text-gray-400 mb-1">leading-relaxed (1.625)</p>
    <p class="text-lg leading-relaxed">
      行高為 1.625 的文字段落。適合需要較寬鬆閱讀體驗的長篇文章。
    </p>
  </div>
  <div>
    <p class="text-sm text-gray-400 mb-1">leading-loose (2)</p>
    <p class="text-lg leading-loose">
      行高為 2 的文字段落。非常寬鬆的行距，適合特殊排版需求。
    </p>
  </div>
</div>
```

### 4. 字距（Letter Spacing）控制

```html
<div class="p-8 space-y-4">
  <p class="tracking-tighter text-xl">tracking-tighter — 字距緊縮 (-0.05em)</p>
  <p class="tracking-tight text-xl">tracking-tight — 字距稍緊 (-0.025em)</p>
  <p class="tracking-normal text-xl">tracking-normal — 預設字距 (0em)</p>
  <p class="tracking-wide text-xl">tracking-wide — 字距稍寬 (0.025em)</p>
  <p class="tracking-wider text-xl">tracking-wider — 字距寬 (0.05em)</p>
  <p class="tracking-widest text-xl">tracking-widest — 字距最寬 (0.1em)</p>
</div>
```

### 5. 文字對齊與裝飾

```html
<div class="p-8 space-y-4 max-w-md">
  <!-- 對齊 -->
  <p class="text-left">text-left — 靠左對齊</p>
  <p class="text-center">text-center — 置中對齊</p>
  <p class="text-right">text-right — 靠右對齊</p>
  <p class="text-justify">text-justify — 兩端對齊，適合長段落使用以確保左右對齊整齊。</p>

  <!-- 裝飾 -->
  <p class="underline">underline — 底線</p>
  <p class="overline">overline — 頂線</p>
  <p class="line-through">line-through — 刪除線</p>
  <p class="no-underline">no-underline — 無裝飾（取消連結預設底線時用）</p>

  <!-- 裝飾樣式 -->
  <p class="underline decoration-wavy decoration-red-500">wavy red underline</p>
  <p class="underline decoration-dotted decoration-blue-500 decoration-2">dotted blue underline (2px)</p>
  <p class="underline decoration-dashed underline-offset-4">dashed with offset</p>

  <!-- 大小寫轉換 -->
  <p class="uppercase tracking-wider text-sm font-semibold">uppercase with tracking</p>
  <p class="lowercase">LOWERCASE — 全部轉小寫</p>
  <p class="capitalize">capitalize — 首字母大寫</p>
</div>
```

### 6. text-balance 與 text-pretty（現代 CSS）

```html
<div class="p-8 space-y-8 max-w-xl">
  <!-- text-balance：讓標題行寬盡量均等 -->
  <div>
    <p class="text-sm text-gray-400 mb-1">text-balance</p>
    <h2 class="text-3xl font-bold text-balance">
      這是一個較長的標題文字，使用 text-balance 可以讓每行的寬度盡量接近
    </h2>
  </div>

  <!-- 無 text-balance 的對比 -->
  <div>
    <p class="text-sm text-gray-400 mb-1">without text-balance</p>
    <h2 class="text-3xl font-bold">
      這是一個較長的標題文字，沒有使用 text-balance 最後一行可能只有幾個字
    </h2>
  </div>

  <!-- text-pretty：優化段落斷行 -->
  <div>
    <p class="text-sm text-gray-400 mb-1">text-pretty</p>
    <p class="text-lg text-pretty">
      text-pretty 會啟用瀏覽器的段落最佳化演算法，減少不自然的斷行位置，讓段落看起來更舒適自然。這個功能特別適合長篇文章和內容密集的頁面。
    </p>
  </div>
</div>
```

### 7. 使用 @theme 自訂字型 token

```css
/* style.css */
@import "tailwindcss";

@theme {
  --font-family-display: "Inter", "Noto Sans TC", system-ui, sans-serif;
  --font-family-body: "Noto Sans TC", "Inter", system-ui, sans-serif;
  --font-family-code: "JetBrains Mono", "Fira Code", ui-monospace, monospace;
}
```

使用自訂字型：

```html
<div class="p-8">
  <h1 class="font-display text-4xl font-bold mb-4">Display Font Title</h1>
  <p class="font-body text-lg leading-relaxed mb-4">
    Body font 用於內文段落，選用對中文友善的 Noto Sans TC。
  </p>
  <pre class="font-code bg-gray-100 p-4 rounded-lg text-sm">
const greeting = "Hello, Tailwind CSS v4!";
console.log(greeting);
  </pre>
</div>
```

### 8. 文字溢出與截斷

```html
<div class="p-8 space-y-6 max-w-sm">
  <!-- 單行截斷 -->
  <div>
    <p class="text-sm text-gray-400 mb-1">truncate (單行省略)</p>
    <p class="truncate">
      這是一段很長很長的文字，它會被截斷並顯示省略號，因為我們使用了 truncate utility class。
    </p>
  </div>

  <!-- 多行截斷 -->
  <div>
    <p class="text-sm text-gray-400 mb-1">line-clamp-3 (三行省略)</p>
    <p class="line-clamp-3">
      這是一段很長的文字，它只會顯示前三行，超過的部分會被截斷並顯示省略號。
      這是第二行的內容，繼續寫一些文字來展示效果。
      這是第三行的內容，到這裡為止。
      這行以及之後的文字應該不會被顯示出來。
    </p>
  </div>

  <!-- 文字換行控制 -->
  <div>
    <p class="text-sm text-gray-400 mb-1">break-words</p>
    <p class="break-words">
      superlongwordthatwontbreakwithoutthebreakwordsutilityappliedtothiselement
    </p>
  </div>
</div>
```

### 9. @tailwindcss/typography 插件

安裝插件：

```bash
npm install @tailwindcss/typography
```

在 CSS 中引入：

```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```

使用 `prose` class 渲染富文字內容：

```html
<article class="prose prose-lg mx-auto p-8">
  <h1>文章標題</h1>
  <p>這是一段普通的段落文字。<strong>粗體</strong>和<em>斜體</em>都會自動排版。</p>
  <h2>第二級標題</h2>
  <ul>
    <li>列表項目一</li>
    <li>列表項目二</li>
    <li>列表項目三</li>
  </ul>
  <blockquote>
    <p>這是一段引用文字，會自動有左邊的裝飾線。</p>
  </blockquote>
  <pre><code>const x = 42;</code></pre>
</article>
```

### 10. 組合應用：文章排版實例

```html
<article class="max-w-2xl mx-auto p-8">
  <header class="mb-8">
    <p class="text-sm font-semibold text-indigo-600 uppercase tracking-wider mb-2">教學文章</p>
    <h1 class="text-4xl font-extrabold text-gray-900 leading-tight text-balance mb-4">
      如何用 Tailwind CSS v4 打造完美的字體排印
    </h1>
    <p class="text-xl text-gray-500 text-pretty">
      掌握字型、字級、行高、字距的最佳實踐，讓你的 UI 文字呈現專業水準。
    </p>
  </header>

  <div class="text-gray-700 leading-relaxed space-y-4 font-body">
    <p>
      字體排印是 UI 設計中最容易被忽略卻影響最深遠的環節。好的排版讓使用者能輕鬆閱讀、快速掃描，壞的排版則讓人不想繼續看下去。
    </p>
    <p>
      Tailwind CSS 的 typography utilities 讓你在不離開 HTML 的情況下，精確控制每一個文字元素的視覺表現。
    </p>
  </div>
</article>
```

## Hands-on Lab

### Foundation

建立一個 Typography 展示頁面，展示所有字級（text-xs 到 text-9xl）、所有字重（thin 到 black）、所有行高變化。

**驗收清單：**
- [ ] 字級展示涵蓋 text-xs 到 text-9xl。
- [ ] 字重展示涵蓋 font-thin 到 font-black（9 種）。
- [ ] 行高展示至少 5 種（leading-none 到 leading-loose）。
- [ ] 每個展示項目有標籤說明對應的 utility class 名稱。

### Advanced

設計一個部落格文章頁面，包含：標題（text-balance）、副標題、作者資訊、文章內容（text-pretty）、引用區塊、程式碼區塊。使用 `@theme` 自訂 display 和 body 字型。

**驗收清單：**
- [ ] 標題使用 text-balance。
- [ ] 內文使用 text-pretty。
- [ ] `@theme` 中定義了至少 2 個自訂字型 token。
- [ ] 頁面有清楚的視覺層次（標題 > 副標題 > 內文 > 輔助文字）。

### Challenge

安裝 `@tailwindcss/typography` 插件，用 `prose` class 渲染一篇完整的 Markdown 風格文章（包含 h1-h4、段落、列表、引用、程式碼、表格、圖片），並自訂 prose 的色彩方案為品牌色。

**驗收清單：**
- [ ] @tailwindcss/typography 已安裝並在 CSS 中引入。
- [ ] prose 渲染的文章包含至少 6 種 HTML 元素。
- [ ] 使用 `prose-indigo` 或自訂色彩方案。
- [ ] 文章在 mobile 和 desktop 都可閱讀。

## Reference Solution

```css
/* style.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";

@theme {
  --font-family-display: "Inter", "Noto Sans TC", system-ui, sans-serif;
  --font-family-body: "Noto Sans TC", "Inter", system-ui, sans-serif;
  --font-family-code: "JetBrains Mono", ui-monospace, monospace;
}
```

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Typography Demo</title>
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body class="min-h-screen bg-gray-50">
    <article class="max-w-2xl mx-auto py-12 px-6">
      <!-- Header -->
      <header class="mb-10">
        <p class="text-sm font-semibold text-indigo-600 uppercase tracking-wider mb-3">
          Tutorial
        </p>
        <h1 class="font-display text-4xl md:text-5xl font-extrabold text-gray-900 leading-tight text-balance mb-4">
          Typography in Tailwind CSS v4: A Complete Guide
        </h1>
        <p class="text-xl text-gray-500 text-pretty leading-relaxed">
          Master font families, sizes, weights, line heights, and letter spacing
          to create beautiful, readable interfaces.
        </p>
        <div class="flex items-center gap-3 mt-6">
          <div class="w-10 h-10 bg-indigo-500 rounded-full"></div>
          <div>
            <p class="font-medium text-gray-900">Author Name</p>
            <p class="text-sm text-gray-500">2026-02-14 &middot; 10 min read</p>
          </div>
        </div>
      </header>

      <!-- Article Body with prose -->
      <div class="prose prose-lg prose-indigo max-w-none font-body">
        <h2>Why Typography Matters</h2>
        <p>
          Good typography is invisible. When done right, readers focus on the content,
          not the presentation. Tailwind CSS provides all the tools needed to achieve
          professional-grade typography without writing a single line of custom CSS.
        </p>

        <h3>Key Principles</h3>
        <ul>
          <li>Use a consistent type scale</li>
          <li>Maintain comfortable line heights for body text (1.5-1.75)</li>
          <li>Limit line width to 60-80 characters for readability</li>
          <li>Create visual hierarchy through size, weight, and color</li>
        </ul>

        <blockquote>
          <p>Typography is the craft of endowing human language with a durable visual form.</p>
        </blockquote>

        <h3>Code Example</h3>
        <pre><code>@theme {
  --font-family-display: "Inter", system-ui, sans-serif;
  --font-family-body: "Noto Sans TC", system-ui, sans-serif;
}</code></pre>

        <table>
          <thead>
            <tr><th>Utility</th><th>Size</th><th>Line Height</th></tr>
          </thead>
          <tbody>
            <tr><td>text-sm</td><td>0.875rem</td><td>1.25rem</td></tr>
            <tr><td>text-base</td><td>1rem</td><td>1.5rem</td></tr>
            <tr><td>text-lg</td><td>1.125rem</td><td>1.75rem</td></tr>
            <tr><td>text-xl</td><td>1.25rem</td><td>1.75rem</td></tr>
          </tbody>
        </table>
      </div>
    </article>
  </body>
</html>
```

## Common Pitfalls

1. **在 v4 中使用 `@plugin` 而非舊的 `require()` 引入 typography（v4 陷阱）**：v4 中插件使用 `@plugin "@tailwindcss/typography";` 在 CSS 中引入，而非在 `tailwind.config.js` 中 `require("@tailwindcss/typography")`。使用舊方式不會有任何效果。

2. **忽略 text-* 自帶的 line-height**：Tailwind 的 `text-lg` 不只設定 font-size，還設定了對應的 line-height。如果你在同一個元素上同時使用 `text-xl leading-none`，leading-none 會覆蓋 text-xl 預設的 line-height。要確認這是你想要的效果。

3. **中文排版行高太小**：中文字型通常需要比英文更大的行高。`leading-normal`（1.5）對中文來說可能略嫌緊湊，建議中文內文使用 `leading-relaxed`（1.625）或 `leading-loose`（2）。

4. **濫用 @apply 抽取文字樣式**：初學者常將一組 typography utilities 用 `@apply` 抽成 `.heading-1`，但這通常不必要。直接在 HTML 中使用 utility class 更靈活。

5. **忘記載入自訂字型檔案**：在 `@theme` 中設定了 `--font-family-display: "Inter"` 但沒有實際載入 Inter 字型（透過 Google Fonts 或本地字型檔），導致 fallback 到系統字型。

## Checklist

- [ ] 能使用 text-xs 到 text-9xl 設定字級。
- [ ] 能使用 font-thin 到 font-black 設定字重。
- [ ] 能使用 leading-* 調整行高。
- [ ] 能使用 tracking-* 調整字距。
- [ ] 會使用 text-balance 和 text-pretty。
- [ ] 能在 `@theme` 中自訂字型 token。
- [ ] 知道如何安裝與使用 @tailwindcss/typography 插件。
- [ ] 會使用 truncate 和 line-clamp-* 處理文字溢出。

## Further Reading (official links only)

- [Font Size](https://tailwindcss.com/docs/font-size)
- [Font Weight](https://tailwindcss.com/docs/font-weight)
- [Font Family](https://tailwindcss.com/docs/font-family)
- [Line Height](https://tailwindcss.com/docs/line-height)
- [Letter Spacing](https://tailwindcss.com/docs/letter-spacing)
- [Text Wrap](https://tailwindcss.com/docs/text-wrap)
- [Tailwind CSS Typography Plugin](https://github.com/tailwindlabs/tailwindcss-typography)
