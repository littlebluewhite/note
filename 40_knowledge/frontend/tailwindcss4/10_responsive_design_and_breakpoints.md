---
title: "Responsive Design and Breakpoints / 響應式設計與斷點"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "10"
level: intermediate
stack: Tailwind CSS 4.1.x
prerequisites: [09_positioning_z_index_and_overflow]
---

# Responsive Design and Breakpoints / 響應式設計與斷點

## Goal

在前一章 [[09_positioning_z_index_and_overflow]] 中，我們學會了定位、z-index 與溢位控制。但那些佈局技巧在不同螢幕尺寸下可能需要截然不同的表現方式 --- 導覽列在手機上可能要收成漢堡選單，側邊欄在平板上要隱藏，三欄佈局在桌面才展開。本章將深入探討 Tailwind CSS v4 的響應式設計系統。

Tailwind CSS 採用 Mobile-first（行動優先）策略，意味著沒有任何前綴的工具類別是套用在所有尺寸上的，而 `sm:`、`md:`、`lg:`、`xl:`、`2xl:` 前綴則是從該斷點「向上」生效。Tailwind CSS v4 的一大革新是將斷點定義為 CSS custom properties，可以透過 `@theme` 指令在 CSS 中直接自訂，不再需要 JavaScript 設定檔。此外，v4 引入了 `min-*` 和 `max-*` 變體，讓範圍查詢更加靈活。我們也會預覽 Container Queries（容器查詢）的概念，這將在 [[15_container_queries_and_modern_layout_patterns]] 中詳細展開。

## Prerequisites

- 已完成 [[09_positioning_z_index_and_overflow]]。
- 理解 CSS media query 的基本語法 `@media (min-width: ...)`。
- 知道 viewport 的概念以及行動裝置的螢幕尺寸差異。
- 已安裝 Tailwind CSS v4 開發環境。

## Core Concepts

### 1. Mobile-first Breakpoint System / 行動優先斷點系統

Tailwind CSS v4 的預設斷點：

| 前綴 | 最小寬度 | 典型裝置 | 何時使用 | 何時不使用 |
|------|---------|---------|----------|------------|
| （無前綴） | 0px | 所有裝置 | 定義基礎樣式，適用於最小螢幕 | 不適用（這是預設） |
| `sm:` | 640px | 大型手機橫向 | 小幅調整間距、字體大小 | 不需要在此斷點變化時 |
| `md:` | 768px | 平板直向 | 從單欄切換為雙欄、顯示側邊欄 | 與 sm 差異不大的情況 |
| `lg:` | 1024px | 平板橫向 / 小筆電 | 展開完整導覽列、三欄佈局 | 手機和平板已有足夠空間時 |
| `xl:` | 1280px | 桌面螢幕 | 增加 max-width 限制、加大間距 | 僅有少量裝飾性調整時 |
| `2xl:` | 1536px | 大螢幕 / 外接螢幕 | 超寬螢幕特殊佈局 | 大部分專案不需要 |

### 2. min-* and max-* Variants / 範圍變體

Tailwind CSS v4 新增了更靈活的範圍查詢語法：

| 變體 | 說明 | 何時使用 | 何時不使用 |
|------|------|----------|------------|
| `sm:` ~ `2xl:` | `min-width` 查詢（向上生效） | 行動優先漸進增強 | 需要精確範圍控制時 |
| `max-sm:` | `max-width: 639px`（小於 sm） | 只在手機上顯示的元素 | 可用無前綴 + sm:hidden 替代時 |
| `max-md:` | `max-width: 767px`（小於 md） | 只在手機和小平板上的樣式 | 行動優先設計能覆蓋時 |
| `min-[800px]:` | 任意最小寬度 | 需要非標準斷點的精確控制 | 標準斷點已足夠時（保持一致性） |
| `max-[600px]:` | 任意最大寬度 | 特殊的精確範圍需求 | 能用標準斷點組合達成時 |

### 3. Custom Breakpoints via @theme / 自訂斷點

在 Tailwind CSS v4 中，斷點透過 `@theme` 指令以 CSS custom properties 定義：

| 方式 | 語法 | 何時使用 | 何時不使用 |
|------|------|----------|------------|
| 預設斷點 | Tailwind 內建 sm/md/lg/xl/2xl | 大多數專案 | 設計稿有非標準斷點時 |
| 覆蓋斷點 | `@theme { --breakpoint-sm: 600px; }` | 設計規範要求不同數值 | 預設值已符合需求時 |
| 新增斷點 | `@theme { --breakpoint-3xl: 1800px; }` | 超寬螢幕有特殊佈局需求 | 會增加複雜度且無明確使用場景時 |
| 任意值 | `min-[1100px]:grid-cols-3` | 一次性的特殊需求 | 重複使用的斷點（應定義在 @theme） |

## Step-by-step

### Step 1: 理解 Mobile-first 思維

所有 Tailwind 類別預設套用在所有螢幕尺寸。加上斷點前綴表示「從此尺寸開始生效」。

```html
<!-- ✅ 正確的 Mobile-first 思維 -->
<div class="text-sm md:text-base lg:text-lg">
  <!-- 手機：text-sm（14px） -->
  <!-- 平板及以上：text-base（16px） -->
  <!-- 桌面及以上：text-lg（18px） -->
</div>

<!-- ❌ 常見錯誤：寫了多餘的無前綴類別 -->
<div class="text-sm sm:text-sm md:text-base lg:text-lg">
  <!-- sm:text-sm 是多餘的，因為無前綴的 text-sm 已經覆蓋所有尺寸 -->
</div>
```

### Step 2: 響應式佈局切換

最常見的響應式模式：手機單欄、平板雙欄、桌面三欄。

```html
<!-- 手機：單欄堆疊 | 平板：雙欄 | 桌面：三欄 -->
<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
  <div class="rounded-lg bg-white p-6 shadow">卡片 1</div>
  <div class="rounded-lg bg-white p-6 shadow">卡片 2</div>
  <div class="rounded-lg bg-white p-6 shadow">卡片 3</div>
  <div class="rounded-lg bg-white p-6 shadow">卡片 4</div>
  <div class="rounded-lg bg-white p-6 shadow">卡片 5</div>
  <div class="rounded-lg bg-white p-6 shadow">卡片 6</div>
</div>
```

### Step 3: 響應式顯示/隱藏元素

使用 `hidden` 配合斷點前綴控制元素的可見性。

```html
<!-- 手機：漢堡選單按鈕可見，完整導覽列隱藏 -->
<!-- 桌面：漢堡選單按鈕隱藏，完整導覽列可見 -->
<header class="flex items-center justify-between px-6 py-4">
  <a href="/" class="text-xl font-bold">Logo</a>

  <!-- 完整導覽列（桌面才顯示） -->
  <nav class="hidden gap-6 lg:flex">
    <a href="#" class="text-gray-600 hover:text-gray-900">Home</a>
    <a href="#" class="text-gray-600 hover:text-gray-900">About</a>
    <a href="#" class="text-gray-600 hover:text-gray-900">Contact</a>
  </nav>

  <!-- 漢堡選單按鈕（手機才顯示） -->
  <button class="lg:hidden">
    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  </button>
</header>
```

### Step 4: 響應式間距與字體

間距和字體大小通常需要隨螢幕尺寸遞增。

```html
<!-- 響應式間距 -->
<section class="px-4 py-8 sm:px-6 sm:py-12 md:px-8 md:py-16 lg:px-12 lg:py-20">
  <!-- 響應式標題 -->
  <h1 class="text-2xl font-bold sm:text-3xl md:text-4xl lg:text-5xl">
    Build amazing websites
  </h1>

  <!-- 響應式段落寬度 -->
  <p class="mt-4 text-base text-gray-600 sm:text-lg md:max-w-2xl lg:max-w-3xl">
    Tailwind CSS v4 讓響應式設計變得直觀。你只需要思考「在這個斷點需要什麼改變」。
  </p>
</section>
```

### Step 5: 使用 max-* 變體（v4 新功能）

`max-*` 讓你可以指定「在此尺寸以下」的樣式，適合需要精確範圍控制的場景。

```html
<!-- 只在手機上顯示的提示訊息 -->
<div class="rounded-lg bg-yellow-50 p-4 text-sm text-yellow-800 max-md:block md:hidden">
  請旋轉裝置以獲得更好的體驗
</div>

<!-- 在 md 到 lg 之間的特殊樣式（範圍查詢） -->
<div class="md:max-lg:bg-blue-100 md:max-lg:p-8">
  這個區塊只在平板尺寸有藍色背景和額外內距
</div>

<!-- 任意值斷點 -->
<div class="min-[600px]:grid-cols-2 min-[900px]:grid-cols-3 min-[1200px]:grid-cols-4">
  精確控制斷點
</div>
```

### Step 6: 透過 @theme 自訂斷點

在 Tailwind CSS v4 中，斷點是 CSS custom properties，可以直接在 CSS 中自訂。

```css
/* app.css */
@import "tailwindcss";

@theme {
  /* 覆蓋預設斷點 */
  --breakpoint-sm: 600px;
  --breakpoint-md: 900px;
  --breakpoint-lg: 1200px;
  --breakpoint-xl: 1440px;
  --breakpoint-2xl: 1920px;

  /* 新增自訂斷點 */
  --breakpoint-3xl: 2560px;
}
```

```html
<!-- 使用自訂斷點 -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 3xl:grid-cols-4">
  <!-- 在 2560px 以上的超寬螢幕顯示四欄 -->
</div>
```

**v3 vs v4 對比：**

```js
// v3: tailwind.config.js
module.exports = {
  theme: {
    screens: {
      sm: '600px',
      md: '900px',
      lg: '1200px',
    },
  },
};
```

```css
/* v4: 直接在 CSS 中定義 */
@theme {
  --breakpoint-sm: 600px;
  --breakpoint-md: 900px;
  --breakpoint-lg: 1200px;
}
```

### Step 7: 響應式 Flexbox 方向切換

在手機上垂直堆疊，桌面上水平排列是最常見的響應式模式之一。

```html
<!-- 手機：垂直堆疊 | 桌面：水平排列 -->
<div class="flex flex-col gap-6 lg:flex-row">
  <!-- 主要內容（桌面佔 2/3） -->
  <main class="lg:w-2/3">
    <article class="rounded-lg bg-white p-6 shadow">
      <h2 class="text-xl font-bold">Article Title</h2>
      <p class="mt-4 text-gray-600">Article content goes here...</p>
    </article>
  </main>

  <!-- 側邊欄（桌面佔 1/3） -->
  <aside class="lg:w-1/3">
    <div class="rounded-lg bg-gray-50 p-6">
      <h3 class="font-bold">Related Links</h3>
      <ul class="mt-4 space-y-2 text-sm text-gray-600">
        <li><a href="#">Link 1</a></li>
        <li><a href="#">Link 2</a></li>
      </ul>
    </div>
  </aside>
</div>
```

### Step 8: 響應式圖片與物件適應

```html
<!-- 響應式 Hero 圖片 -->
<div class="relative">
  <img
    src="/hero.jpg"
    alt="Hero"
    class="h-48 w-full object-cover sm:h-64 md:h-80 lg:h-96"
  />
  <!-- 響應式文字覆蓋層 -->
  <div class="absolute inset-0 flex items-center justify-center bg-black/40">
    <div class="px-4 text-center">
      <h1 class="text-2xl font-bold text-white sm:text-3xl md:text-5xl">
        Hero Title
      </h1>
      <p class="mt-2 text-sm text-white/80 sm:text-base md:text-lg">
        Subtitle goes here
      </p>
    </div>
  </div>
</div>

<!-- 響應式圖片網格 -->
<div class="columns-2 gap-4 sm:columns-3 lg:columns-4">
  <img src="/img-1.jpg" alt="" class="mb-4 w-full rounded-lg" />
  <img src="/img-2.jpg" alt="" class="mb-4 w-full rounded-lg" />
  <img src="/img-3.jpg" alt="" class="mb-4 w-full rounded-lg" />
  <img src="/img-4.jpg" alt="" class="mb-4 w-full rounded-lg" />
  <img src="/img-5.jpg" alt="" class="mb-4 w-full rounded-lg" />
  <img src="/img-6.jpg" alt="" class="mb-4 w-full rounded-lg" />
</div>
```

### Step 9: Container Queries 預覽

Tailwind CSS v4 內建支援 Container Queries，這是一種根據父容器寬度（而非視窗寬度）來調整樣式的技術。詳細內容在 [[15_container_queries_and_modern_layout_patterns]]，這裡先做概念預覽。

```html
<!-- 傳統 media query：根據「視窗寬度」響應 -->
<div class="grid grid-cols-1 md:grid-cols-2">視窗響應</div>

<!-- Container query：根據「父容器寬度」響應 -->
<div class="@container">
  <div class="grid grid-cols-1 @md:grid-cols-2">容器響應</div>
</div>
```

**何時用 Media Query vs Container Query：**
- **Media Query（`md:` 等）：** 頁面級佈局變化，如整體頁面欄數、導覽列模式
- **Container Query（`@md:` 等）：** 元件級自適應，如卡片在不同寬度的側邊欄中自動調整

### Step 10: 測試響應式設計的方法

```html
<!-- 開發輔助：顯示當前斷點的指示器 -->
<div class="fixed bottom-4 left-4 z-50 rounded-full bg-gray-900 px-3 py-1 text-xs font-mono text-white">
  <span class="sm:hidden">xs</span>
  <span class="hidden sm:inline md:hidden">sm</span>
  <span class="hidden md:inline lg:hidden">md</span>
  <span class="hidden lg:inline xl:hidden">lg</span>
  <span class="hidden xl:inline 2xl:hidden">xl</span>
  <span class="hidden 2xl:inline">2xl</span>
</div>
```

**測試清單：**
1. 使用 Chrome DevTools 的 Device Toolbar（Cmd+Shift+M）模擬不同裝置
2. 拖動瀏覽器視窗寬度觀察斷點切換
3. 在真實手機和平板上測試
4. 檢查旋轉裝置時的佈局變化（portrait vs landscape）

## Hands-on Lab

### Foundation 基礎練習

**任務：** 建立一個響應式卡片網格。

需求：
- 手機（< 640px）：單欄堆疊
- 平板（>= 768px）：雙欄
- 桌面（>= 1024px）：三欄
- 每張卡片包含圖片、標題、描述
- 間距隨螢幕尺寸遞增：`gap-4 md:gap-6 lg:gap-8`

**驗收清單：**
- [ ] 三個斷點各自正確切換欄數
- [ ] 圖片使用 `object-cover` 保持比例
- [ ] 間距在不同螢幕尺寸有差異
- [ ] 在 Chrome DevTools 中拖動寬度可觀察平滑切換

### Advanced 進階練習

**任務：** 建立一個完整的響應式 Landing Page。

需求：
- 響應式導覽列：手機漢堡選單、桌面完整連結
- Hero 區域：響應式圖片高度、響應式文字大小
- Features 區域：響應式網格（1/2/3 欄）
- Footer：響應式多欄佈局（手機堆疊、桌面四欄）
- 自訂斷點：使用 `@theme` 定義一個 `--breakpoint-3xl: 1800px`

**驗收清單：**
- [ ] 導覽列在手機和桌面有不同展示模式
- [ ] Hero 標題字體大小從 `text-2xl` 遞增到 `text-5xl`
- [ ] Features 網格正確響應
- [ ] Footer 在手機堆疊、桌面水平排列
- [ ] 自訂斷點 `3xl:` 正常運作

### Challenge 挑戰練習

**任務：** 建立一個響應式儀表板佈局（Dashboard Layout）。

需求：
- 手機：底部 Tab Bar 導覽、單欄內容
- 平板：左側折疊側邊欄（只顯示圖示）、雙欄內容
- 桌面：左側展開側邊欄（圖示 + 文字）、主內容區域 + 右側面板
- 使用 `max-*` 變體處理特定範圍的樣式
- 加入斷點指示器輔助開發

**驗收清單：**
- [ ] 三個佈局模式正確切換
- [ ] 側邊欄在平板折疊、桌面展開
- [ ] 底部 Tab Bar 只在手機出現
- [ ] 右側面板只在桌面出現
- [ ] 使用 `max-md:` 限制手機特定樣式
- [ ] 斷點指示器正確顯示當前尺寸

## Reference Solution

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ch10 Lab - Responsive Landing Page</title>
  <link rel="stylesheet" href="/src/output.css" />
  <style>
    /* v4 自訂斷點 */
    @theme {
      --breakpoint-3xl: 1800px;
    }
  </style>
</head>
<body class="min-h-screen bg-white text-gray-900">

  <!-- ====== Breakpoint Indicator (dev only) ====== -->
  <div class="fixed bottom-4 left-4 z-50 rounded-full bg-gray-900 px-3 py-1 font-mono text-xs text-white">
    <span class="sm:hidden">xs</span>
    <span class="hidden sm:inline md:hidden">sm</span>
    <span class="hidden md:inline lg:hidden">md</span>
    <span class="hidden lg:inline xl:hidden">lg</span>
    <span class="hidden xl:inline 2xl:hidden">xl</span>
    <span class="hidden 2xl:inline 3xl:hidden">2xl</span>
    <span class="hidden 3xl:inline">3xl</span>
  </div>

  <!-- ====== Navigation ====== -->
  <header class="sticky top-0 z-20 border-b border-gray-100 bg-white/90 backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
      <a href="/" class="text-xl font-bold text-blue-600 sm:text-2xl">
        LandingApp
      </a>

      <!-- Desktop Navigation -->
      <nav class="hidden items-center gap-8 lg:flex">
        <a href="#features" class="text-sm text-gray-600 hover:text-gray-900">Features</a>
        <a href="#pricing" class="text-sm text-gray-600 hover:text-gray-900">Pricing</a>
        <a href="#testimonials" class="text-sm text-gray-600 hover:text-gray-900">Testimonials</a>
        <a href="#faq" class="text-sm text-gray-600 hover:text-gray-900">FAQ</a>
        <a href="#" class="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700">
          Get Started
        </a>
      </nav>

      <!-- Mobile Hamburger -->
      <button class="rounded-lg p-2 hover:bg-gray-100 lg:hidden">
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    </div>
  </header>

  <!-- ====== Hero Section ====== -->
  <section class="relative overflow-hidden">
    <div class="mx-auto max-w-7xl px-4 py-16 sm:px-6 sm:py-24 md:py-32 lg:px-8 lg:py-40">
      <div class="max-w-3xl">
        <h1 class="text-3xl font-extrabold tracking-tight sm:text-4xl md:text-5xl lg:text-6xl 3xl:text-7xl">
          Build better products
          <span class="block text-blue-600">with modern tools</span>
        </h1>
        <p class="mt-4 text-base text-gray-600 sm:mt-6 sm:text-lg md:text-xl lg:max-w-xl">
          Tailwind CSS v4 讓你能夠快速建立響應式、美觀的使用者介面。
          從行動裝置到超寬螢幕，一套 utility classes 全搞定。
        </p>
        <div class="mt-8 flex flex-col gap-3 sm:mt-10 sm:flex-row sm:gap-4">
          <a href="#" class="rounded-lg bg-blue-600 px-6 py-3 text-center text-sm font-medium text-white hover:bg-blue-700 sm:px-8 sm:py-4 sm:text-base">
            Start Free Trial
          </a>
          <a href="#" class="rounded-lg border border-gray-300 px-6 py-3 text-center text-sm font-medium text-gray-700 hover:bg-gray-50 sm:px-8 sm:py-4 sm:text-base">
            Watch Demo
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- ====== Features Section ====== -->
  <section id="features" class="bg-gray-50 py-16 sm:py-24">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="text-center">
        <h2 class="text-2xl font-bold sm:text-3xl lg:text-4xl">Features</h2>
        <p class="mt-3 text-gray-600 sm:text-lg">Everything you need to build modern web apps.</p>
      </div>

      <div class="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 lg:gap-8">
        <div class="rounded-xl bg-white p-6 shadow-sm sm:p-8">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100 text-blue-600">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3 class="mt-4 text-lg font-semibold">Lightning Fast</h3>
          <p class="mt-2 text-sm text-gray-600">
            Tailwind v4 的全新引擎讓編譯速度提升 10 倍，開發體驗前所未有的流暢。
          </p>
        </div>

        <div class="rounded-xl bg-white p-6 shadow-sm sm:p-8">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100 text-green-600">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
          </div>
          <h3 class="mt-4 text-lg font-semibold">Responsive by Default</h3>
          <p class="mt-2 text-sm text-gray-600">
            行動優先的斷點系統，搭配全新的 max-* 變體和 Container Queries 支援。
          </p>
        </div>

        <div class="rounded-xl bg-white p-6 shadow-sm sm:p-8">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100 text-purple-600">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
            </svg>
          </div>
          <h3 class="mt-4 text-lg font-semibold">CSS-first Config</h3>
          <p class="mt-2 text-sm text-gray-600">
            v4 使用 @theme 指令在 CSS 中直接配置，不再需要 JavaScript 設定檔。
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- ====== Footer ====== -->
  <footer class="border-t border-gray-200 bg-gray-50 py-12 sm:py-16">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-2 gap-8 md:grid-cols-4">
        <div>
          <h4 class="text-sm font-semibold uppercase tracking-wider text-gray-900">Product</h4>
          <ul class="mt-4 space-y-3">
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">Features</a></li>
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">Pricing</a></li>
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">Changelog</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-sm font-semibold uppercase tracking-wider text-gray-900">Company</h4>
          <ul class="mt-4 space-y-3">
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">About</a></li>
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">Blog</a></li>
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">Careers</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-sm font-semibold uppercase tracking-wider text-gray-900">Resources</h4>
          <ul class="mt-4 space-y-3">
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">Documentation</a></li>
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">Guides</a></li>
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">API Reference</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-sm font-semibold uppercase tracking-wider text-gray-900">Legal</h4>
          <ul class="mt-4 space-y-3">
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">Privacy</a></li>
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">Terms</a></li>
            <li><a href="#" class="text-sm text-gray-600 hover:text-gray-900">License</a></li>
          </ul>
        </div>
      </div>

      <div class="mt-12 border-t border-gray-200 pt-8">
        <p class="text-center text-sm text-gray-500">
          &copy; 2026 LandingApp. All rights reserved.
        </p>
      </div>
    </div>
  </footer>

</body>
</html>
```

## Common Pitfalls

1. **Desktop-first 思維：** 先寫桌面版樣式再用 `max-*` 往下覆蓋。Tailwind 的設計是 Mobile-first，應該先寫最小螢幕的樣式（無前綴），然後用 `sm:`、`md:` 等向上增強。Desktop-first 會導致大量冗餘的覆蓋類別。

2. **過度使用斷點：** 不是每個屬性都需要響應式變化。如果某個元素在所有尺寸看起來都不錯，就不需要加斷點前綴。過度使用會讓 HTML 難以閱讀。

3. **忘記 viewport meta tag：** 如果 HTML 中缺少 `<meta name="viewport" content="width=device-width, initial-scale=1.0">`，行動裝置會使用預設的 980px 視窗寬度，導致媒體查詢完全失效。

4. **v4 特定 --- 混淆 @theme 斷點語法：** 在 Tailwind CSS v4 中，自訂斷點必須使用 `--breakpoint-*` 格式定義在 `@theme` 中。如果錯誤地使用 v3 的 `screens` config 方式或直接寫 CSS custom properties 到 `:root`，斷點前綴不會生效。必須用 `@theme { --breakpoint-tablet: 800px; }` 才能產生 `tablet:` 前綴。

5. **Container Query 與 Media Query 混用：** Container Queries（`@md:`）和 Media Queries（`md:`）的前綴很像但行為完全不同。`@md:` 參照的是父容器寬度，`md:` 參照的是視窗寬度。混淆兩者會導致非預期的佈局行為。

## Checklist

- [ ] 理解 Mobile-first 策略：無前綴 = 所有尺寸，`sm:` = 640px 以上。
- [ ] 能使用 `hidden` + 斷點前綴控制元素在不同螢幕尺寸的顯示/隱藏。
- [ ] 能建立響應式網格佈局（1 欄 -> 2 欄 -> 3 欄）。
- [ ] 能使用 `max-*` 變體限定特定範圍的樣式。
- [ ] 能透過 `@theme { --breakpoint-*: ... }` 自訂斷點值。
- [ ] 知道 Container Query（`@md:`）與 Media Query（`md:`）的差異。
- [ ] 能建立斷點指示器輔助開發測試。

## Further Reading (official links only)

- [Responsive Design - Tailwind CSS](https://tailwindcss.com/docs/responsive-design)
- [Customizing Screens - Tailwind CSS](https://tailwindcss.com/docs/screens)
- [Container Queries - Tailwind CSS](https://tailwindcss.com/docs/container-queries)
- [Tailwind CSS v4.0 - tailwindcss.com](https://tailwindcss.com/blog/tailwindcss-v4)
- [GitHub - tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss)
