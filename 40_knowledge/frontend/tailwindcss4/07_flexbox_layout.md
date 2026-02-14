---
title: "Flexbox Layout / Flexbox 排版"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "07"
level: beginner
stack: Tailwind CSS 4.1.x
prerequisites: [06_borders_shadows_and_rings]
---
# Flexbox Layout / Flexbox 排版

## Goal

在上一章 [06_borders_shadows_and_rings](06_borders_shadows_and_rings.md) 中，我們學會了為元素加上視覺邊界與層次。現在要進入頁面佈局的核心工具之一：**Flexbox**。Flexbox 是一維佈局模型（在一個方向上排列子元素），它是建構導覽列、卡片列、按鈕群組等水平/垂直排列元素的最佳工具。Tailwind 將 Flexbox 的所有屬性都對應為 utility class，讓你可以在 HTML 中直覺地建構彈性佈局。

掌握 Flexbox 後，你就能建構大多數常見的 UI 排版需求。下一章 [08_grid_layout](08_grid_layout.md) 將介紹 CSS Grid，它是二維佈局的利器，適合更複雜的網格式佈局如 Dashboard。

## Prerequisites

- 已完成第 06 章。
- 理解 CSS `display: flex` 的基本概念。
- 知道主軸（main axis）與交叉軸（cross axis）的概念。

## Core Concepts

### Flexbox vs Grid
- **何時用 Flexbox**：一維佈局（一行或一列），如導覽列、按鈕群組、卡片水平排列、垂直堆疊的表單欄位。當你只需要控制一個方向的排列時，Flexbox 是最直覺的選擇。
- **何時用 Grid**：二維佈局（同時控制行和列），如 Dashboard 面板、產品網格、複雜的表單佈局。下一章會詳細介紹。

### flex vs inline-flex
- **何時用 flex**：大多數情況。`flex` 讓容器成為 block-level flex container，佔據整行寬度。
- **何時用 inline-flex**：需要 flex container 以 inline 方式存在（不佔整行），如按鈕內的 icon + text 組合。

### gap-* vs justify/items
- **何時用 gap-***：控制子元素之間的間距，不影響首尾元素。這是現代 Flexbox 的最佳間距方式。
- **何時用 justify-between / justify-around**：控制子元素在主軸上的分布方式，如導覽列的 logo 和選單分居兩側。
- **何時用 items-***：控制子元素在交叉軸上的對齊，如垂直置中 `items-center`。

### flex-wrap vs overflow
- **何時用 flex-wrap**：允許子元素在空間不足時自動換行，如可變數量的標籤列表。
- **何時用 overflow-hidden/scroll**：限制容器大小，用捲軸或隱藏處理溢出內容。

## Step-by-step

### 1. Flex 基礎：方向與對齊

```html
<div class="p-8 space-y-8">
  <!-- 水平排列（預設）-->
  <div>
    <p class="text-sm text-gray-500 mb-2">flex (row, default)</p>
    <div class="flex gap-4">
      <div class="bg-blue-200 px-4 py-2 rounded">Item 1</div>
      <div class="bg-blue-300 px-4 py-2 rounded">Item 2</div>
      <div class="bg-blue-400 px-4 py-2 rounded text-white">Item 3</div>
    </div>
  </div>

  <!-- 垂直排列 -->
  <div>
    <p class="text-sm text-gray-500 mb-2">flex flex-col</p>
    <div class="flex flex-col gap-4 max-w-xs">
      <div class="bg-green-200 px-4 py-2 rounded">Item 1</div>
      <div class="bg-green-300 px-4 py-2 rounded">Item 2</div>
      <div class="bg-green-400 px-4 py-2 rounded">Item 3</div>
    </div>
  </div>

  <!-- 反向排列 -->
  <div>
    <p class="text-sm text-gray-500 mb-2">flex flex-row-reverse</p>
    <div class="flex flex-row-reverse gap-4">
      <div class="bg-purple-200 px-4 py-2 rounded">Item 1</div>
      <div class="bg-purple-300 px-4 py-2 rounded">Item 2</div>
      <div class="bg-purple-400 px-4 py-2 rounded text-white">Item 3</div>
    </div>
  </div>
</div>
```

### 2. 主軸對齊（justify-*）

```html
<div class="p-8 space-y-6">
  <div>
    <p class="text-sm text-gray-500 mb-2">justify-start (default)</p>
    <div class="flex justify-start gap-2 bg-gray-100 p-4 rounded-lg">
      <div class="size-12 bg-blue-400 rounded flex items-center justify-center text-white text-sm">1</div>
      <div class="size-12 bg-blue-500 rounded flex items-center justify-center text-white text-sm">2</div>
      <div class="size-12 bg-blue-600 rounded flex items-center justify-center text-white text-sm">3</div>
    </div>
  </div>

  <div>
    <p class="text-sm text-gray-500 mb-2">justify-center</p>
    <div class="flex justify-center gap-2 bg-gray-100 p-4 rounded-lg">
      <div class="size-12 bg-green-400 rounded flex items-center justify-center text-white text-sm">1</div>
      <div class="size-12 bg-green-500 rounded flex items-center justify-center text-white text-sm">2</div>
      <div class="size-12 bg-green-600 rounded flex items-center justify-center text-white text-sm">3</div>
    </div>
  </div>

  <div>
    <p class="text-sm text-gray-500 mb-2">justify-between</p>
    <div class="flex justify-between bg-gray-100 p-4 rounded-lg">
      <div class="size-12 bg-red-400 rounded flex items-center justify-center text-white text-sm">1</div>
      <div class="size-12 bg-red-500 rounded flex items-center justify-center text-white text-sm">2</div>
      <div class="size-12 bg-red-600 rounded flex items-center justify-center text-white text-sm">3</div>
    </div>
  </div>

  <div>
    <p class="text-sm text-gray-500 mb-2">justify-around</p>
    <div class="flex justify-around bg-gray-100 p-4 rounded-lg">
      <div class="size-12 bg-purple-400 rounded flex items-center justify-center text-white text-sm">1</div>
      <div class="size-12 bg-purple-500 rounded flex items-center justify-center text-white text-sm">2</div>
      <div class="size-12 bg-purple-600 rounded flex items-center justify-center text-white text-sm">3</div>
    </div>
  </div>

  <div>
    <p class="text-sm text-gray-500 mb-2">justify-evenly</p>
    <div class="flex justify-evenly bg-gray-100 p-4 rounded-lg">
      <div class="size-12 bg-orange-400 rounded flex items-center justify-center text-white text-sm">1</div>
      <div class="size-12 bg-orange-500 rounded flex items-center justify-center text-white text-sm">2</div>
      <div class="size-12 bg-orange-600 rounded flex items-center justify-center text-white text-sm">3</div>
    </div>
  </div>
</div>
```

### 3. 交叉軸對齊（items-*）

```html
<div class="p-8 space-y-6">
  <div>
    <p class="text-sm text-gray-500 mb-2">items-start</p>
    <div class="flex items-start gap-4 bg-gray-100 p-4 rounded-lg h-32">
      <div class="bg-blue-400 px-4 py-2 rounded text-white">Short</div>
      <div class="bg-blue-500 px-4 py-6 rounded text-white">Taller</div>
      <div class="bg-blue-600 px-4 py-10 rounded text-white">Tallest</div>
    </div>
  </div>

  <div>
    <p class="text-sm text-gray-500 mb-2">items-center</p>
    <div class="flex items-center gap-4 bg-gray-100 p-4 rounded-lg h-32">
      <div class="bg-green-400 px-4 py-2 rounded text-white">Short</div>
      <div class="bg-green-500 px-4 py-6 rounded text-white">Taller</div>
      <div class="bg-green-600 px-4 py-10 rounded text-white">Tallest</div>
    </div>
  </div>

  <div>
    <p class="text-sm text-gray-500 mb-2">items-end</p>
    <div class="flex items-end gap-4 bg-gray-100 p-4 rounded-lg h-32">
      <div class="bg-red-400 px-4 py-2 rounded text-white">Short</div>
      <div class="bg-red-500 px-4 py-6 rounded text-white">Taller</div>
      <div class="bg-red-600 px-4 py-10 rounded text-white">Tallest</div>
    </div>
  </div>

  <div>
    <p class="text-sm text-gray-500 mb-2">items-stretch (default)</p>
    <div class="flex items-stretch gap-4 bg-gray-100 p-4 rounded-lg h-32">
      <div class="bg-purple-400 px-4 rounded text-white flex items-center">Stretched</div>
      <div class="bg-purple-500 px-4 rounded text-white flex items-center">Stretched</div>
      <div class="bg-purple-600 px-4 rounded text-white flex items-center">Stretched</div>
    </div>
  </div>
</div>
```

### 4. flex-grow、flex-shrink、flex-basis

```html
<div class="p-8 space-y-6">
  <!-- flex-1：均分空間 -->
  <div>
    <p class="text-sm text-gray-500 mb-2">flex-1 (均分)</p>
    <div class="flex gap-4">
      <div class="flex-1 bg-blue-300 p-4 rounded text-center">flex-1</div>
      <div class="flex-1 bg-blue-400 p-4 rounded text-center">flex-1</div>
      <div class="flex-1 bg-blue-500 p-4 rounded text-center text-white">flex-1</div>
    </div>
  </div>

  <!-- flex-none：不伸縮 -->
  <div>
    <p class="text-sm text-gray-500 mb-2">flex-none vs flex-1</p>
    <div class="flex gap-4">
      <div class="flex-none w-32 bg-green-300 p-4 rounded text-center">flex-none w-32</div>
      <div class="flex-1 bg-green-500 p-4 rounded text-center text-white">flex-1 (takes remaining)</div>
    </div>
  </div>

  <!-- grow / shrink -->
  <div>
    <p class="text-sm text-gray-500 mb-2">grow-0 vs grow</p>
    <div class="flex gap-4">
      <div class="grow-0 w-24 bg-purple-300 p-4 rounded text-center text-sm">grow-0</div>
      <div class="grow bg-purple-500 p-4 rounded text-center text-white">grow</div>
    </div>
  </div>

  <!-- shrink-0：禁止壓縮 -->
  <div>
    <p class="text-sm text-gray-500 mb-2">shrink-0 (sidebar pattern)</p>
    <div class="flex gap-4">
      <div class="shrink-0 w-48 bg-orange-300 p-4 rounded">shrink-0 w-48</div>
      <div class="flex-1 min-w-0 bg-orange-500 p-4 rounded text-white truncate">
        flex-1 min-w-0: this long text will truncate instead of pushing the sidebar
      </div>
    </div>
  </div>
</div>
```

### 5. flex-wrap

```html
<div class="p-8">
  <p class="text-sm text-gray-500 mb-2">flex flex-wrap gap-4</p>
  <div class="flex flex-wrap gap-4">
    <span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">JavaScript</span>
    <span class="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">TypeScript</span>
    <span class="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm font-medium">React</span>
    <span class="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-medium">Svelte</span>
    <span class="bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-sm font-medium">Tailwind CSS</span>
    <span class="bg-cyan-100 text-cyan-700 px-3 py-1 rounded-full text-sm font-medium">Node.js</span>
    <span class="bg-pink-100 text-pink-700 px-3 py-1 rounded-full text-sm font-medium">GraphQL</span>
    <span class="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full text-sm font-medium">PostgreSQL</span>
    <span class="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm font-medium">Docker</span>
  </div>
</div>
```

### 6. order-*

```html
<div class="p-8">
  <p class="text-sm text-gray-500 mb-2">order-* 調整顯示順序（不影響 DOM 順序）</p>
  <div class="flex gap-4">
    <div class="order-3 bg-blue-300 px-6 py-4 rounded">DOM: 1, Order: 3</div>
    <div class="order-1 bg-blue-500 px-6 py-4 rounded text-white">DOM: 2, Order: 1</div>
    <div class="order-2 bg-blue-700 px-6 py-4 rounded text-white">DOM: 3, Order: 2</div>
  </div>
</div>
```

### 7. 水平垂直完美置中

```html
<div class="p-8">
  <p class="text-sm text-gray-500 mb-2">flex items-center justify-center（完美置中）</p>
  <div class="flex items-center justify-center h-64 bg-gray-100 rounded-lg">
    <div class="bg-white p-8 rounded-xl shadow-lg text-center">
      <h3 class="text-xl font-bold text-gray-900">完美置中</h3>
      <p class="text-gray-500">flex + items-center + justify-center</p>
    </div>
  </div>
</div>
```

### 8. 實戰：響應式導覽列

```html
<nav class="bg-white shadow-sm">
  <div class="max-w-6xl mx-auto px-6">
    <div class="flex items-center justify-between h-16">
      <!-- Logo -->
      <div class="flex items-center gap-2">
        <div class="size-8 bg-blue-500 rounded-lg"></div>
        <span class="font-bold text-gray-900 text-lg">Brand</span>
      </div>

      <!-- Navigation Links -->
      <div class="flex items-center gap-8">
        <a href="#" class="text-gray-900 font-medium hover:text-blue-600 transition-colors">Home</a>
        <a href="#" class="text-gray-500 hover:text-blue-600 transition-colors">Products</a>
        <a href="#" class="text-gray-500 hover:text-blue-600 transition-colors">About</a>
        <a href="#" class="text-gray-500 hover:text-blue-600 transition-colors">Contact</a>
      </div>

      <!-- CTA Button -->
      <div class="flex items-center gap-4">
        <button class="px-4 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors">
          Sign Up
        </button>
      </div>
    </div>
  </div>
</nav>
```

### 9. 實戰：Card 水平排列

```html
<div class="p-8">
  <div class="flex gap-6 overflow-x-auto pb-4">
    <div class="flex-none w-72 bg-white rounded-xl shadow-sm p-6">
      <div class="h-40 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg mb-4"></div>
      <h3 class="font-bold text-gray-900 mb-1">Card Title 1</h3>
      <p class="text-gray-500 text-sm">A brief description of this card's content.</p>
    </div>
    <div class="flex-none w-72 bg-white rounded-xl shadow-sm p-6">
      <div class="h-40 bg-gradient-to-br from-green-400 to-green-600 rounded-lg mb-4"></div>
      <h3 class="font-bold text-gray-900 mb-1">Card Title 2</h3>
      <p class="text-gray-500 text-sm">A brief description of this card's content.</p>
    </div>
    <div class="flex-none w-72 bg-white rounded-xl shadow-sm p-6">
      <div class="h-40 bg-gradient-to-br from-purple-400 to-purple-600 rounded-lg mb-4"></div>
      <h3 class="font-bold text-gray-900 mb-1">Card Title 3</h3>
      <p class="text-gray-500 text-sm">A brief description of this card's content.</p>
    </div>
    <div class="flex-none w-72 bg-white rounded-xl shadow-sm p-6">
      <div class="h-40 bg-gradient-to-br from-rose-400 to-rose-600 rounded-lg mb-4"></div>
      <h3 class="font-bold text-gray-900 mb-1">Card Title 4</h3>
      <p class="text-gray-500 text-sm">A brief description of this card's content.</p>
    </div>
  </div>
</div>
```

### 10. 實戰：Footer 多欄佈局

```html
<footer class="bg-gray-900 text-gray-300">
  <div class="max-w-6xl mx-auto px-6 py-12">
    <div class="flex flex-wrap gap-12">
      <!-- Company Info -->
      <div class="flex-1 min-w-[200px]">
        <h4 class="text-white font-bold text-lg mb-4">Company</h4>
        <p class="text-sm leading-relaxed">
          Building the future of web development with modern CSS tools.
        </p>
      </div>

      <!-- Links -->
      <div class="flex-1 min-w-[150px]">
        <h4 class="text-white font-bold mb-4">Product</h4>
        <ul class="space-y-2 text-sm">
          <li><a href="#" class="hover:text-white transition-colors">Features</a></li>
          <li><a href="#" class="hover:text-white transition-colors">Pricing</a></li>
          <li><a href="#" class="hover:text-white transition-colors">Documentation</a></li>
        </ul>
      </div>

      <div class="flex-1 min-w-[150px]">
        <h4 class="text-white font-bold mb-4">Company</h4>
        <ul class="space-y-2 text-sm">
          <li><a href="#" class="hover:text-white transition-colors">About</a></li>
          <li><a href="#" class="hover:text-white transition-colors">Blog</a></li>
          <li><a href="#" class="hover:text-white transition-colors">Careers</a></li>
        </ul>
      </div>

      <div class="flex-1 min-w-[150px]">
        <h4 class="text-white font-bold mb-4">Legal</h4>
        <ul class="space-y-2 text-sm">
          <li><a href="#" class="hover:text-white transition-colors">Privacy</a></li>
          <li><a href="#" class="hover:text-white transition-colors">Terms</a></li>
          <li><a href="#" class="hover:text-white transition-colors">License</a></li>
        </ul>
      </div>
    </div>

    <div class="border-t border-gray-800 mt-12 pt-8 text-sm text-gray-500">
      <p>&copy; 2026 Company. All rights reserved.</p>
    </div>
  </div>
</footer>
```

## Hands-on Lab

### Foundation

建立一個響應式導覽列，包含 logo（左側）、導覽連結（中間）、CTA 按鈕（右側）。

**驗收清單：**
- [ ] Logo 靠左、連結居中或靠右、按鈕靠右。
- [ ] 使用 `flex` + `items-center` + `justify-between`。
- [ ] 導覽列高度固定（h-16 或 h-14）。
- [ ] 連結有 hover 效果。

### Advanced

在導覽列下方建立一個卡片列表頁面，使用 `flex-wrap` 實現：
- Desktop：一行顯示 3 張卡片。
- Tablet：一行顯示 2 張卡片。
- Mobile：一行顯示 1 張卡片。

每張卡片包含圖片區、標題、描述和按鈕。

**驗收清單：**
- [ ] 三個斷點各有正確的卡片數量。
- [ ] 使用 flex-wrap 和百分比寬度（或搭配 responsive w-*）。
- [ ] 卡片等高（items-stretch 或 flex-col）。
- [ ] 卡片間距使用 gap-*。

### Challenge

建立一個完整的頁面骨架（Header + Sidebar + Main + Footer），使用巢狀 Flexbox 實現。Sidebar 在 Desktop 可見，在 Mobile 隱藏。Main 區域填滿剩餘空間。

**驗收清單：**
- [ ] Header 固定高度，sticky 置頂。
- [ ] Sidebar 使用 `shrink-0 w-64`。
- [ ] Main 使用 `flex-1 min-w-0`。
- [ ] Sidebar 在小螢幕用 `hidden md:block` 隱藏。
- [ ] 整體佈局不超過 viewport 高度（no scroll on body）。

## Reference Solution

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Flexbox Layout Demo</title>
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body class="h-screen flex flex-col bg-gray-100">
    <!-- Header -->
    <header class="h-14 bg-white border-b border-gray-200 px-6 flex items-center justify-between shrink-0 sticky top-0 z-10">
      <div class="flex items-center gap-3">
        <div class="size-8 bg-indigo-500 rounded-lg"></div>
        <span class="font-bold text-lg text-gray-900">MyApp</span>
      </div>
      <nav class="hidden md:flex items-center gap-6">
        <a href="#" class="text-sm text-gray-600 hover:text-gray-900 transition-colors">Dashboard</a>
        <a href="#" class="text-sm text-gray-600 hover:text-gray-900 transition-colors">Projects</a>
        <a href="#" class="text-sm text-gray-600 hover:text-gray-900 transition-colors">Settings</a>
      </nav>
      <div class="size-8 bg-gray-300 rounded-full"></div>
    </header>

    <!-- Body -->
    <div class="flex flex-1 min-h-0">
      <!-- Sidebar -->
      <aside class="hidden md:flex flex-col shrink-0 w-64 bg-white border-r border-gray-200 py-4 overflow-y-auto">
        <nav class="flex-1 px-3 space-y-1">
          <a href="#" class="flex items-center gap-3 px-3 py-2.5 bg-indigo-50 text-indigo-700 rounded-lg text-sm font-medium">
            <span class="size-5 bg-indigo-200 rounded"></span>
            Dashboard
          </a>
          <a href="#" class="flex items-center gap-3 px-3 py-2.5 text-gray-600 hover:bg-gray-50 rounded-lg text-sm">
            <span class="size-5 bg-gray-200 rounded"></span>
            Analytics
          </a>
          <a href="#" class="flex items-center gap-3 px-3 py-2.5 text-gray-600 hover:bg-gray-50 rounded-lg text-sm">
            <span class="size-5 bg-gray-200 rounded"></span>
            Reports
          </a>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 min-w-0 p-6 overflow-y-auto">
        <h1 class="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

        <!-- Stats Cards -->
        <div class="flex flex-wrap gap-6 mb-8">
          <div class="flex-1 min-w-[200px] bg-white p-6 rounded-xl shadow-sm">
            <p class="text-sm text-gray-500">Total Users</p>
            <p class="text-3xl font-bold text-gray-900 mt-1">12,345</p>
          </div>
          <div class="flex-1 min-w-[200px] bg-white p-6 rounded-xl shadow-sm">
            <p class="text-sm text-gray-500">Revenue</p>
            <p class="text-3xl font-bold text-gray-900 mt-1">$67,890</p>
          </div>
          <div class="flex-1 min-w-[200px] bg-white p-6 rounded-xl shadow-sm">
            <p class="text-sm text-gray-500">Active Now</p>
            <p class="text-3xl font-bold text-gray-900 mt-1">573</p>
          </div>
        </div>

        <!-- Activity List -->
        <div class="bg-white rounded-xl shadow-sm">
          <div class="px-6 py-4 border-b border-gray-100">
            <h2 class="font-semibold text-gray-900">Recent Activity</h2>
          </div>
          <div class="divide-y divide-gray-100">
            <div class="flex items-center gap-4 px-6 py-4">
              <div class="size-10 bg-blue-100 rounded-full shrink-0"></div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">New user registered</p>
                <p class="text-xs text-gray-500">2 minutes ago</p>
              </div>
            </div>
            <div class="flex items-center gap-4 px-6 py-4">
              <div class="size-10 bg-green-100 rounded-full shrink-0"></div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">Payment received</p>
                <p class="text-xs text-gray-500">15 minutes ago</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </body>
</html>
```

## Common Pitfalls

1. **在 v4 中 flex utilities 預設行為一致，但注意 gap 的瀏覽器支援（v4 陷阱）**：v4 移除了一些 v3 的 polyfill 行為。`gap` 在 Flexbox 中的瀏覽器支援已經非常好（所有現代瀏覽器），但如果你的專案需要支援非常舊的瀏覽器（如 Safari 14 以下），`gap` 在 flex 中可能不生效。v4 假設你使用現代瀏覽器。

2. **flex-1 子元素的內容溢出**：`flex-1` 讓元素佔據剩餘空間，但如果子元素內容太長（如長文字），可能會撐破容器。解決方式：加上 `min-w-0` 讓 flex 子元素可以被壓縮到小於其內容寬度。

3. **在 flex 容器中忘記 shrink-0**：固定寬度的元素（如 sidebar `w-64`）在 flex 容器中可能被壓縮。加上 `shrink-0` 確保不被壓縮。

4. **使用 space-* 而非 gap-* 在 flex 容器中**：`space-x-4` 在 `flex-wrap` 時會出問題（換行的第一個元素仍有左 margin）。在 flex 容器中始終使用 `gap-*`。

5. **justify-between 在只有一個子元素時的行為**：當容器只有一個子元素時，`justify-between` 會把元素推到左上角（等於 `justify-start`）。如果你期望單個元素置中，請使用 `justify-center`。

## Checklist

- [ ] 能使用 flex、flex-col、flex-row-reverse 控制排列方向。
- [ ] 能使用 justify-* 控制主軸對齊。
- [ ] 能使用 items-* 控制交叉軸對齊。
- [ ] 能使用 flex-1、flex-none、grow、shrink 控制伸縮行為。
- [ ] 能使用 flex-wrap 實現換行佈局。
- [ ] 能使用 gap-* 設定子元素間距。
- [ ] 能建構響應式導覽列。
- [ ] 能建構 Sidebar + Main Content 佈局。

## Further Reading (official links only)

- [Flex](https://tailwindcss.com/docs/flex)
- [Flex Direction](https://tailwindcss.com/docs/flex-direction)
- [Flex Wrap](https://tailwindcss.com/docs/flex-wrap)
- [Justify Content](https://tailwindcss.com/docs/justify-content)
- [Align Items](https://tailwindcss.com/docs/align-items)
- [Flex Grow](https://tailwindcss.com/docs/flex-grow)
- [Flex Shrink](https://tailwindcss.com/docs/flex-shrink)
- [Gap](https://tailwindcss.com/docs/gap)
