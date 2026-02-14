---
title: "Utility-First Philosophy and Mental Model / Utility-First 哲學與思維模型"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "01"
level: beginner
stack: Tailwind CSS 4.1.x
prerequisites: [00_series_overview]
---
# Utility-First Philosophy and Mental Model / Utility-First 哲學與思維模型

## Goal

在上一章 [00_series_overview](00_series_overview.md) 中，我們已經建立好 Tailwind CSS v4 的練習環境。現在我們要深入理解 Tailwind CSS 的核心設計哲學：**Utility-First**。這不只是一種寫 CSS 的方式，而是一種思維模型的轉變。許多初次接觸 Tailwind 的開發者會質疑「把 class 寫在 HTML 裡不就是 inline style 嗎？」——本章將解答這個疑問，並幫助你建立正確的心智模型。

理解 utility-first 的哲學後，你將能更有效率地寫出可維護的樣式，並知道何時應該使用 utility class、何時應該抽取為自訂元件 class。下一章 [02_installation_and_css_first_configuration](02_installation_and_css_first_configuration.md) 將深入探討 v4 的安裝方式與 CSS-first 設定，讓你能自訂主題與配置。

## Prerequisites

- 已完成第 00 章，練習環境可正常運作。
- 基礎 CSS 知識：瞭解選擇器、class、屬性與值。
- 曾經寫過至少一個帶有自訂 CSS 的網頁。

## Core Concepts

### Utility-First vs Semantic CSS
- **何時用 Utility-First**：快速開發 UI、不想維護獨立的 CSS 檔案、團隊希望統一設計語言。Utility-first 讓你在 HTML 中直接表達視覺意圖，不需要在 HTML 和 CSS 之間切換。
- **何時不用 Utility-First**：需要極度自訂的 CSS 動畫、第三方元件庫要求語意 class、團隊已有成熟的 CSS 架構且不打算遷移。

### Utility Classes vs Inline Styles
- **何時用 Utility Classes**：幾乎所有情況。Utility classes 提供了約束（design tokens）、響應式支援（`md:flex`）、狀態變體（`hover:bg-blue-600`）和偽元素支援（`before:content-['']`），這些都是 inline style 做不到的。
- **何時用 Inline Styles**：只有在需要動態計算值（如 JavaScript 動態設定位置）時才使用。

### Extract Components vs Keep Utilities
- **何時抽取元件**：同樣的 utility class 組合在 3 個以上地方重複出現，且語意相同（如按鈕、卡片）。此時可使用框架元件（React/Svelte component）或 Tailwind 的 `@apply` 來抽取。
- **何時保持 Utility**：每處的設計雖然相似但有細微差異、或者只出現 1-2 次。過早抽取反而增加抽象層的維護成本。

### BEM vs Utility-First
- **何時用 BEM**：與 Tailwind 無關的專案、需要嚴格的 CSS 命名規範、不使用建構工具。
- **何時用 Utility-First 取代 BEM**：有建構工具（Vite/PostCSS）、希望消除命名疲勞、希望設計與程式碼高度對齊。

## Step-by-step

### 1. 建立語意式 CSS 範例

先建立一個傳統的語意式 CSS 卡片，理解痛點。在專案中建立 `semantic-example.html`：

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Semantic CSS Example</title>
    <style>
      .card {
        background-color: white;
        border-radius: 0.75rem;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        padding: 2rem;
        max-width: 24rem;
        margin: 0 auto;
      }
      .card__title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.5rem;
      }
      .card__description {
        color: #6b7280;
        margin-bottom: 1rem;
      }
      .card__button {
        display: inline-block;
        background-color: #3b82f6;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-decoration: none;
        font-weight: 500;
      }
      .card__button:hover {
        background-color: #2563eb;
      }
    </style>
  </head>
  <body style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background-color: #f3f4f6;">
    <div class="card">
      <h2 class="card__title">語意式 CSS 卡片</h2>
      <p class="card__description">使用 BEM 命名的傳統方式。</p>
      <a href="#" class="card__button">了解更多</a>
    </div>
  </body>
</html>
```

### 2. 用 Utility-First 重寫同一張卡片

在 `index.html` 中，用 Tailwind utility classes 實現完全相同的設計：

```html
<body class="min-h-screen flex items-center justify-center bg-gray-100">
  <div class="bg-white rounded-xl shadow-lg p-8 max-w-sm mx-auto">
    <h2 class="text-2xl font-bold text-gray-900 mb-2">
      Utility-First 卡片
    </h2>
    <p class="text-gray-500 mb-4">使用 Tailwind utility classes。</p>
    <a
      href="#"
      class="inline-block bg-blue-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600"
    >
      了解更多
    </a>
  </div>
</body>
```

### 3. 比較兩種方式的維護成本

觀察以下差異：
- **語意式**：需要 25 行 CSS + 在 HTML 和 CSS 之間切換。
- **Utility-First**：0 行自訂 CSS，所有視覺資訊都在 HTML 中。
- **修改圓角**：語意式需要找到 `.card` 並修改；utility 直接改 `rounded-xl` 為 `rounded-2xl`。

### 4. 體驗響應式 Utility 的威力

在卡片的 `div` 上加入響應式 class：

```html
<div class="bg-white rounded-xl shadow-lg p-4 md:p-8 max-w-sm md:max-w-lg mx-auto">
```

縮放瀏覽器視窗，觀察 padding 和最大寬度在不同尺寸的變化。注意：這在 inline style 中是做不到的。

### 5. 體驗狀態變體

為連結加入更多狀態：

```html
<a
  href="#"
  class="inline-block bg-blue-500 text-white px-4 py-2 rounded-lg font-medium
         hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
         active:bg-blue-700 transition-colors"
>
  了解更多
</a>
```

用滑鼠 hover、tab 鍵 focus、點擊 active 測試各狀態。

### 6. 理解設計約束（Design Tokens）

Tailwind 的 utility class 不是隨意的值，而是基於設計系統的 token。例如：
- `text-gray-500` 對應 oklch 色彩空間中的灰色。
- `p-8` 對應 `2rem`（8 * 0.25rem）。
- `rounded-xl` 對應 `0.75rem`。

```html
<!-- 受約束的設計 token -->
<div class="p-4 text-gray-700 bg-blue-50 rounded-lg">Good</div>

<!-- 任意值（逃生口） -->
<div class="p-[13px] text-[#1a2b3c] bg-[rgb(200,220,255)] rounded-[7px]">Escape hatch</div>
```

### 7. 判斷何時抽取元件

建立一個按鈕重複出現的場景：

```html
<div class="space-y-4">
  <button class="bg-blue-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600">
    儲存
  </button>
  <button class="bg-blue-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600">
    送出
  </button>
  <button class="bg-blue-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600">
    確認
  </button>
</div>
```

當這種重複出現 3 次以上時，就應考慮抽取。在純 HTML 專案中可以使用 `@apply`（但要節制）；在 React/Svelte 專案中應該抽取為 component。

### 8. 使用 @apply 的正確時機（謹慎使用）

```css
/* style.css */
@import "tailwindcss";

@layer components {
  .btn-primary {
    @apply bg-blue-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600;
  }
}
```

```html
<button class="btn-primary">儲存</button>
<button class="btn-primary">送出</button>
```

注意：Tailwind 官方建議優先使用框架元件而非 `@apply`，因為 `@apply` 會失去 utility-first 的許多優勢。

## Hands-on Lab

### Foundation

將以下語意式 CSS 頁面完整重寫為 utility-first：

```html
<!-- 原始語意式版本 -->
<style>
  .hero { text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
  .hero__title { font-size: 2.25rem; font-weight: 800; margin-bottom: 1rem; }
  .hero__subtitle { font-size: 1.125rem; opacity: 0.9; margin-bottom: 2rem; }
  .hero__cta { display: inline-block; background: white; color: #667eea; padding: 0.75rem 2rem; border-radius: 9999px; font-weight: 600; }
  .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; padding: 4rem 2rem; max-width: 64rem; margin: 0 auto; }
  .feature-card { background: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 1px 3px rgb(0 0 0 / 0.1); }
  .feature-card__title { font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; }
  .feature-card__desc { color: #6b7280; }
</style>
```

**驗收清單：**
- [ ] 不使用任何 `<style>` 標籤或自訂 CSS（`@apply` 也不使用）。
- [ ] 視覺效果與語意式版本完全一致。
- [ ] 使用了至少 15 個不同的 utility class。
- [ ] Hero 區塊的漸層背景使用 Tailwind gradient utilities。

### Advanced

在 Foundation 的基礎上，加入響應式設計：
- Mobile（< 768px）：features 改為單欄。
- Tablet（768px-1024px）：features 改為雙欄。
- Desktop（> 1024px）：features 三欄。

並加入互動狀態：
- CTA 按鈕 hover 時有放大效果。
- Feature card hover 時有陰影加深效果。

**驗收清單：**
- [ ] 三個斷點各有對應的網格欄數。
- [ ] CTA 按鈕 hover 有 `scale` 效果。
- [ ] Feature card hover 陰影變化可見。
- [ ] 使用了 `transition` 相關 utility。

### Challenge

撰寫一份 500 字左右的比較文件（Markdown），比較 utility-first、semantic CSS、BEM、CSS-in-JS 四種方式在以下面向的優劣：
- 開發速度
- 可維護性
- 團隊協作
- 效能
- 學習曲線

**驗收清單：**
- [ ] 涵蓋四種方式。
- [ ] 每個面向都有具體比較。
- [ ] 結論明確指出各方式的最佳適用場景。

## Reference Solution

Foundation 完整解答：

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Utility-First Landing Page</title>
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body class="min-h-screen bg-gray-50">
    <!-- Hero Section -->
    <section
      class="text-center py-16 px-8 bg-gradient-to-br from-indigo-500 to-purple-600 text-white"
    >
      <h1 class="text-4xl font-extrabold mb-4">歡迎使用 Tailwind CSS</h1>
      <p class="text-lg opacity-90 mb-8">
        用 utility-first 方式打造現代化 UI
      </p>
      <a
        href="#features"
        class="inline-block bg-white text-indigo-500 px-8 py-3 rounded-full font-semibold hover:scale-105 transition-transform"
      >
        開始探索
      </a>
    </section>

    <!-- Features Section -->
    <section
      id="features"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 py-16 px-8 max-w-5xl mx-auto"
    >
      <div
        class="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 class="text-xl font-semibold mb-2">快速開發</h3>
        <p class="text-gray-500">不用離開 HTML 就能完成所有樣式。</p>
      </div>
      <div
        class="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 class="text-xl font-semibold mb-2">設計一致</h3>
        <p class="text-gray-500">基於設計 token 的約束系統。</p>
      </div>
      <div
        class="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 class="text-xl font-semibold mb-2">檔案更小</h3>
        <p class="text-gray-500">只產生你用到的 CSS。</p>
      </div>
    </section>
  </body>
</html>
```

## Common Pitfalls

1. **把 utility-first 等同於 inline styles（觀念錯誤）**：Utility classes 提供設計約束、響應式變體、狀態變體、偽元素支援，這些都是 inline style 做不到的。不要因為「class 很長」就否定這個方法。

2. **過早使用 @apply 抽取（v4 陷阱）**：在 v4 中 `@apply` 仍然可用，但官方更推薦使用框架元件。初學者常在只重複 2 次時就急著抽取，造成不必要的抽象。遵循「重複 3 次以上」原則。

3. **混用多種 CSS 方法論**：在同一個專案中同時使用 BEM class 和 Tailwind utility，造成維護混亂。選定一種方式後盡量統一。

4. **忽略 Tailwind 的設計約束**：大量使用任意值（`text-[17px]`、`p-[13px]`）而不用 token（`text-lg`、`p-3`），失去了設計系統的一致性優勢。

5. **class 順序混亂**：建議遵循一致的排列順序：布局 > 尺寸 > 間距 > 字型 > 色彩 > 邊框 > 效果 > 狀態。可使用 Prettier 的 `prettier-plugin-tailwindcss` 自動排序。

## Checklist

- [ ] 能解釋 utility-first 與 inline style 的 3 個以上差異。
- [ ] 能用 Tailwind utility classes 重寫一個語意式 CSS 元件。
- [ ] 知道何時使用 utility class、何時抽取為元件。
- [ ] 理解設計 token 的約束作用。
- [ ] 會使用響應式變體（如 `md:flex`）。
- [ ] 會使用狀態變體（如 `hover:bg-blue-600`）。

## Further Reading (official links only)

- [Utility-First Fundamentals](https://tailwindcss.com/docs/utility-first)
- [Reusing Styles](https://tailwindcss.com/docs/reusing-styles)
- [Adding Custom Styles](https://tailwindcss.com/docs/adding-custom-styles)
- [Tailwind CSS Blog - CSS Utility Classes and Separation of Concerns](https://tailwindcss.com/blog/css-utility-classes-and-separation-of-concerns)
