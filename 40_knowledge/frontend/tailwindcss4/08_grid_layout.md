---
title: "Grid Layout / Grid 排版"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "08"
level: beginner
stack: Tailwind CSS 4.1.x
prerequisites: [07_flexbox_layout]
---
# Grid Layout / Grid 排版

## Goal

在上一章 [07_flexbox_layout](07_flexbox_layout.md) 中，我們掌握了 Flexbox 這個一維佈局工具。現在要學習 CSS 的另一個強大佈局系統：**Grid**。Grid 是一個二維佈局模型，它能同時控制行和列，非常適合 Dashboard 面板、產品網格、圖片畫廊、複雜表單等需要精確行列控制的場景。Tailwind 提供了完整的 Grid utilities，包括 `grid-cols-*`、`grid-rows-*`、`col-span-*`、`row-span-*` 等。v4 的一大亮點是 **Grid 欄數值可以動態使用**——例如 `grid-cols-15` 直接可用，不需要在設定檔中定義。

掌握 Grid 佈局後，你將擁有完整的 CSS 佈局能力（Flex + Grid），可以建構任何複雜度的頁面佈局。下一章 [09_positioning_and_z_index](09_positioning_z_index_and_overflow.md) 將探討定位與 z-index，處理疊加層級和絕對定位的場景。

## Prerequisites

- 已完成第 07 章。
- 理解 CSS Grid 的基本概念（grid container、grid item、tracks）。
- 知道 `fr` 單位（fractional unit）的概念。

## Core Concepts

### Grid vs Flexbox
- **何時用 Grid**：需要同時控制行和列的二維佈局，如 Dashboard 面板、產品網格、圖片畫廊。或是需要子元素在指定的格子中精確定位（`col-span`、`row-span`）。
- **何時用 Flexbox**：一維佈局（一行或一列），如導覽列、按鈕群組、垂直堆疊。或是子元素的數量不固定，需要自動換行（`flex-wrap`）。

### Explicit Grid vs Implicit Grid
- **何時用 explicit grid（`grid-cols-*`、`grid-rows-*`）**：知道確切的行列數量，如固定的 3 欄佈局、4x4 網格。
- **何時用 implicit grid（`auto-rows-*`、`auto-cols-*`）**：不知道確切的項目數量，讓 Grid 自動產生所需的行列，如動態列表。

### Template Columns vs Auto-fill/Auto-fit
- **何時用 `grid-cols-N`**：固定欄數，如 `grid-cols-3` 始終 3 欄。
- **何時用 auto-fill / auto-fit**：希望欄數依據容器寬度自動調整（響應式網格），不需要媒體查詢。這是用 arbitrary values 搭配 `repeat(auto-fill, minmax(...))` 實現。

### Subgrid vs Nested Grid
- **何時用 Subgrid**：子 grid 需要對齊父 grid 的 track lines。CSS Subgrid 已有良好的瀏覽器支援，v4 支援 `grid-rows-subgrid` 和 `grid-cols-subgrid`。
- **何時用 Nested Grid**：子 grid 需要完全獨立的 track 定義。

## Step-by-step

### 1. Grid 基礎：定義欄數

```html
<div class="p-8 space-y-8">
  <!-- 3 欄 grid -->
  <div>
    <p class="text-sm text-gray-500 mb-2">grid grid-cols-3 gap-4</p>
    <div class="grid grid-cols-3 gap-4">
      <div class="bg-blue-200 p-4 rounded text-center">1</div>
      <div class="bg-blue-300 p-4 rounded text-center">2</div>
      <div class="bg-blue-400 p-4 rounded text-center text-white">3</div>
      <div class="bg-blue-500 p-4 rounded text-center text-white">4</div>
      <div class="bg-blue-600 p-4 rounded text-center text-white">5</div>
      <div class="bg-blue-700 p-4 rounded text-center text-white">6</div>
    </div>
  </div>

  <!-- 4 欄 grid -->
  <div>
    <p class="text-sm text-gray-500 mb-2">grid grid-cols-4 gap-4</p>
    <div class="grid grid-cols-4 gap-4">
      <div class="bg-green-200 p-4 rounded text-center">1</div>
      <div class="bg-green-300 p-4 rounded text-center">2</div>
      <div class="bg-green-400 p-4 rounded text-center">3</div>
      <div class="bg-green-500 p-4 rounded text-center text-white">4</div>
    </div>
  </div>

  <!-- v4 動態欄數 -->
  <div>
    <p class="text-sm text-gray-500 mb-2">grid grid-cols-7 gap-2 (v4: 任意整數可用)</p>
    <div class="grid grid-cols-7 gap-2">
      <div class="bg-purple-200 p-2 rounded text-center text-sm">Mon</div>
      <div class="bg-purple-200 p-2 rounded text-center text-sm">Tue</div>
      <div class="bg-purple-200 p-2 rounded text-center text-sm">Wed</div>
      <div class="bg-purple-200 p-2 rounded text-center text-sm">Thu</div>
      <div class="bg-purple-200 p-2 rounded text-center text-sm">Fri</div>
      <div class="bg-purple-300 p-2 rounded text-center text-sm">Sat</div>
      <div class="bg-purple-300 p-2 rounded text-center text-sm">Sun</div>
    </div>
  </div>
</div>
```

### 2. Grid Rows

```html
<div class="p-8">
  <p class="text-sm text-gray-500 mb-2">grid grid-rows-3 grid-flow-col gap-4</p>
  <div class="grid grid-rows-3 grid-flow-col gap-4">
    <div class="bg-rose-200 p-4 rounded text-center">1</div>
    <div class="bg-rose-300 p-4 rounded text-center">2</div>
    <div class="bg-rose-400 p-4 rounded text-center">3</div>
    <div class="bg-rose-500 p-4 rounded text-center text-white">4</div>
    <div class="bg-rose-600 p-4 rounded text-center text-white">5</div>
    <div class="bg-rose-700 p-4 rounded text-center text-white">6</div>
  </div>
</div>
```

### 3. col-span 與 row-span

```html
<div class="p-8">
  <p class="text-sm text-gray-500 mb-2">跨欄與跨行</p>
  <div class="grid grid-cols-4 grid-rows-3 gap-4">
    <!-- 跨 2 欄 -->
    <div class="col-span-2 bg-blue-400 p-4 rounded text-white text-center">
      col-span-2
    </div>
    <div class="bg-blue-300 p-4 rounded text-center">3</div>
    <div class="bg-blue-300 p-4 rounded text-center">4</div>

    <!-- 跨 2 行 -->
    <div class="row-span-2 bg-green-400 p-4 rounded text-white text-center flex items-center justify-center">
      row-span-2
    </div>
    <div class="bg-green-300 p-4 rounded text-center">6</div>
    <div class="col-span-2 bg-green-300 p-4 rounded text-center">col-span-2</div>

    <div class="bg-purple-300 p-4 rounded text-center">9</div>
    <div class="col-span-2 bg-purple-400 p-4 rounded text-white text-center">
      col-span-2
    </div>
  </div>
</div>
```

### 4. col-start / col-end 精確定位

```html
<div class="p-8">
  <p class="text-sm text-gray-500 mb-2">col-start / col-end 精確定位</p>
  <div class="grid grid-cols-6 gap-4">
    <div class="col-start-1 col-end-3 bg-blue-400 p-4 rounded text-white text-center">
      col 1-2
    </div>
    <div class="col-start-3 col-end-7 bg-green-400 p-4 rounded text-white text-center">
      col 3-6
    </div>
    <div class="col-start-2 col-end-5 bg-purple-400 p-4 rounded text-white text-center">
      col 2-4
    </div>
    <div class="col-start-5 col-end-7 bg-rose-400 p-4 rounded text-white text-center">
      col 5-6
    </div>
  </div>
</div>
```

### 5. gap-x 與 gap-y 分開控制

```html
<div class="p-8">
  <p class="text-sm text-gray-500 mb-2">gap-x-8 gap-y-4（水平間距大於垂直）</p>
  <div class="grid grid-cols-3 gap-x-8 gap-y-4">
    <div class="bg-cyan-200 p-4 rounded text-center">1</div>
    <div class="bg-cyan-300 p-4 rounded text-center">2</div>
    <div class="bg-cyan-400 p-4 rounded text-center">3</div>
    <div class="bg-cyan-200 p-4 rounded text-center">4</div>
    <div class="bg-cyan-300 p-4 rounded text-center">5</div>
    <div class="bg-cyan-400 p-4 rounded text-center">6</div>
  </div>
</div>
```

### 6. auto-rows 與 auto-flow

```html
<div class="p-8">
  <p class="text-sm text-gray-500 mb-2">grid-cols-3 auto-rows-min (高度依內容)</p>
  <div class="grid grid-cols-3 auto-rows-min gap-4">
    <div class="bg-orange-200 p-4 rounded">Short content</div>
    <div class="bg-orange-300 p-8 rounded">Taller content with more padding</div>
    <div class="bg-orange-400 p-4 rounded">Short</div>
    <div class="bg-orange-200 p-12 rounded">Very tall content</div>
    <div class="bg-orange-300 p-4 rounded">Short</div>
    <div class="bg-orange-400 p-4 rounded">Short</div>
  </div>

  <p class="text-sm text-gray-500 mb-2 mt-8">grid-flow-dense (自動填滿空隙)</p>
  <div class="grid grid-cols-3 grid-flow-dense gap-4">
    <div class="col-span-2 bg-teal-300 p-4 rounded text-center">col-span-2</div>
    <div class="bg-teal-200 p-4 rounded text-center">1</div>
    <div class="bg-teal-200 p-4 rounded text-center">2</div>
    <div class="col-span-2 bg-teal-400 p-4 rounded text-center">col-span-2</div>
    <div class="bg-teal-200 p-4 rounded text-center">3 (fills gap)</div>
  </div>
</div>
```

### 7. place-items 與 place-content

```html
<div class="p-8 space-y-8">
  <!-- place-items-center：每個 cell 內容置中 -->
  <div>
    <p class="text-sm text-gray-500 mb-2">place-items-center</p>
    <div class="grid grid-cols-3 gap-4 place-items-center h-48 bg-gray-100 rounded-lg">
      <div class="size-12 bg-blue-400 rounded flex items-center justify-center text-white">1</div>
      <div class="size-12 bg-blue-500 rounded flex items-center justify-center text-white">2</div>
      <div class="size-12 bg-blue-600 rounded flex items-center justify-center text-white">3</div>
    </div>
  </div>

  <!-- place-content-center：整個 grid 置中 -->
  <div>
    <p class="text-sm text-gray-500 mb-2">place-content-center</p>
    <div class="grid grid-cols-3 gap-4 place-content-center h-48 bg-gray-100 rounded-lg">
      <div class="size-12 bg-green-400 rounded flex items-center justify-center text-white">1</div>
      <div class="size-12 bg-green-500 rounded flex items-center justify-center text-white">2</div>
      <div class="size-12 bg-green-600 rounded flex items-center justify-center text-white">3</div>
    </div>
  </div>
</div>
```

### 8. 響應式 Grid

```html
<div class="p-8">
  <p class="text-sm text-gray-500 mb-2">
    grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4
  </p>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    <div class="bg-white p-6 rounded-xl shadow-sm">
      <div class="h-32 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg mb-4"></div>
      <h3 class="font-bold text-gray-900">Product 1</h3>
      <p class="text-sm text-gray-500 mt-1">$29.99</p>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-sm">
      <div class="h-32 bg-gradient-to-br from-green-400 to-green-600 rounded-lg mb-4"></div>
      <h3 class="font-bold text-gray-900">Product 2</h3>
      <p class="text-sm text-gray-500 mt-1">$49.99</p>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-sm">
      <div class="h-32 bg-gradient-to-br from-purple-400 to-purple-600 rounded-lg mb-4"></div>
      <h3 class="font-bold text-gray-900">Product 3</h3>
      <p class="text-sm text-gray-500 mt-1">$19.99</p>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-sm">
      <div class="h-32 bg-gradient-to-br from-rose-400 to-rose-600 rounded-lg mb-4"></div>
      <h3 class="font-bold text-gray-900">Product 4</h3>
      <p class="text-sm text-gray-500 mt-1">$39.99</p>
    </div>
  </div>
</div>
```

### 9. Auto-fill/Auto-fit 響應式網格（無斷點）

使用 arbitrary values 搭配 `repeat(auto-fill, minmax())` 實現自動響應式網格，不需要任何斷點：

```html
<div class="p-8">
  <p class="text-sm text-gray-500 mb-2">
    auto-fill + minmax: 自動調整欄數（無斷點）
  </p>
  <div class="grid grid-cols-[repeat(auto-fill,minmax(250px,1fr))] gap-6">
    <div class="bg-white p-6 rounded-xl shadow-sm">
      <div class="h-24 bg-amber-200 rounded-lg mb-3"></div>
      <h3 class="font-medium text-gray-900">Auto Card 1</h3>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-sm">
      <div class="h-24 bg-amber-300 rounded-lg mb-3"></div>
      <h3 class="font-medium text-gray-900">Auto Card 2</h3>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-sm">
      <div class="h-24 bg-amber-400 rounded-lg mb-3"></div>
      <h3 class="font-medium text-gray-900">Auto Card 3</h3>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-sm">
      <div class="h-24 bg-amber-500 rounded-lg mb-3"></div>
      <h3 class="font-medium text-gray-900">Auto Card 4</h3>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-sm">
      <div class="h-24 bg-amber-600 rounded-lg mb-3"></div>
      <h3 class="font-medium text-gray-900">Auto Card 5</h3>
    </div>
  </div>
</div>
```

### 10. 實戰：Dashboard Grid 佈局

```html
<div class="p-6 bg-gray-100 min-h-screen">
  <h1 class="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

  <div class="grid grid-cols-12 gap-6">
    <!-- Stats Row: 4 cards -->
    <div class="col-span-12 sm:col-span-6 lg:col-span-3 bg-white p-6 rounded-xl shadow-sm">
      <p class="text-sm text-gray-500">Total Revenue</p>
      <p class="text-2xl font-bold text-gray-900 mt-1">$45,231</p>
      <p class="text-xs text-green-600 mt-2">+20.1% from last month</p>
    </div>
    <div class="col-span-12 sm:col-span-6 lg:col-span-3 bg-white p-6 rounded-xl shadow-sm">
      <p class="text-sm text-gray-500">Subscriptions</p>
      <p class="text-2xl font-bold text-gray-900 mt-1">+2,350</p>
      <p class="text-xs text-green-600 mt-2">+180.1% from last month</p>
    </div>
    <div class="col-span-12 sm:col-span-6 lg:col-span-3 bg-white p-6 rounded-xl shadow-sm">
      <p class="text-sm text-gray-500">Sales</p>
      <p class="text-2xl font-bold text-gray-900 mt-1">+12,234</p>
      <p class="text-xs text-green-600 mt-2">+19% from last month</p>
    </div>
    <div class="col-span-12 sm:col-span-6 lg:col-span-3 bg-white p-6 rounded-xl shadow-sm">
      <p class="text-sm text-gray-500">Active Now</p>
      <p class="text-2xl font-bold text-gray-900 mt-1">+573</p>
      <p class="text-xs text-red-600 mt-2">-201 since last hour</p>
    </div>

    <!-- Main Chart: 8 cols -->
    <div class="col-span-12 lg:col-span-8 bg-white p-6 rounded-xl shadow-sm">
      <h2 class="font-semibold text-gray-900 mb-4">Overview</h2>
      <div class="h-64 bg-gray-50 rounded-lg flex items-center justify-center text-gray-400">
        Chart Placeholder
      </div>
    </div>

    <!-- Sidebar: 4 cols -->
    <div class="col-span-12 lg:col-span-4 bg-white p-6 rounded-xl shadow-sm">
      <h2 class="font-semibold text-gray-900 mb-4">Recent Sales</h2>
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="size-10 bg-blue-100 rounded-full shrink-0"></div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 truncate">Customer A</p>
            <p class="text-xs text-gray-500">customer@example.com</p>
          </div>
          <span class="text-sm font-medium text-gray-900">+$1,999</span>
        </div>
        <div class="flex items-center gap-3">
          <div class="size-10 bg-green-100 rounded-full shrink-0"></div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 truncate">Customer B</p>
            <p class="text-xs text-gray-500">b@example.com</p>
          </div>
          <span class="text-sm font-medium text-gray-900">+$39</span>
        </div>
        <div class="flex items-center gap-3">
          <div class="size-10 bg-purple-100 rounded-full shrink-0"></div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 truncate">Customer C</p>
            <p class="text-xs text-gray-500">c@example.com</p>
          </div>
          <span class="text-sm font-medium text-gray-900">+$299</span>
        </div>
      </div>
    </div>

    <!-- Data Table: Full width -->
    <div class="col-span-12 bg-white rounded-xl shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100">
        <h2 class="font-semibold text-gray-900">Recent Orders</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100">
              <th class="text-left p-4 font-medium text-gray-500">Order</th>
              <th class="text-left p-4 font-medium text-gray-500">Customer</th>
              <th class="text-left p-4 font-medium text-gray-500">Status</th>
              <th class="text-right p-4 font-medium text-gray-500">Amount</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b border-gray-50">
              <td class="p-4 font-medium text-gray-900">#3210</td>
              <td class="p-4 text-gray-600">Alice Wang</td>
              <td class="p-4">
                <span class="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">Completed</span>
              </td>
              <td class="p-4 text-right text-gray-900">$250.00</td>
            </tr>
            <tr class="border-b border-gray-50">
              <td class="p-4 font-medium text-gray-900">#3209</td>
              <td class="p-4 text-gray-600">Bob Chen</td>
              <td class="p-4">
                <span class="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium">Pending</span>
              </td>
              <td class="p-4 text-right text-gray-900">$150.00</td>
            </tr>
            <tr>
              <td class="p-4 font-medium text-gray-900">#3208</td>
              <td class="p-4 text-gray-600">Carol Lin</td>
              <td class="p-4">
                <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">Processing</span>
              </td>
              <td class="p-4 text-right text-gray-900">$350.00</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
```

## Hands-on Lab

### Foundation

建立一個產品網格頁面，展示 6 個產品卡片，使用 `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` 實現響應式排列。

**驗收清單：**
- [ ] 6 張產品卡片包含圖片佔位、產品名稱、價格。
- [ ] Mobile 單欄、Tablet 雙欄、Desktop 三欄。
- [ ] 使用 `gap-6` 管理卡片間距。
- [ ] 卡片有 hover 效果（如陰影加深）。

### Advanced

建立一個 12 欄的 Dashboard 佈局，包含：
- 頂部 4 個統計卡片（各佔 3 欄）。
- 中間主要圖表區（佔 8 欄）+ 側邊資訊（佔 4 欄）。
- 底部全寬資料表格（佔 12 欄）。

使用 `col-span-*` 和響應式斷點調整。

**驗收清單：**
- [ ] 使用 12 欄 grid 系統。
- [ ] 統計卡片在 Desktop 各佔 3 欄，在 Mobile 各佔 12 欄。
- [ ] 圖表區和側邊資訊在 Desktop 分別佔 8 和 4 欄。
- [ ] 資料表格在所有尺寸佔 12 欄。

### Challenge

建立一個圖片畫廊（Masonry-like），使用 `col-span-*` 和 `row-span-*` 混合使用，讓部分圖片佔據更大的格子（如英雄圖佔 2x2），模擬 Pinterest 風格的瀑布流佈局。

**驗收清單：**
- [ ] 至少 8 張圖片（佔位色塊即可）。
- [ ] 至少 2 張使用 col-span-2。
- [ ] 至少 1 張使用 row-span-2。
- [ ] 使用 grid-flow-dense 填滿空隙。
- [ ] 佈局在不同視窗大小下保持美觀。

## Reference Solution

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Grid Gallery</title>
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body class="min-h-screen bg-gray-100 p-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">Photo Gallery</h1>

    <div class="grid grid-cols-2 md:grid-cols-4 grid-flow-dense gap-4 auto-rows-[200px]">
      <!-- Hero image: 2x2 -->
      <div class="col-span-2 row-span-2 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl overflow-hidden relative group">
        <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-end p-6">
          <p class="text-white font-bold text-lg opacity-0 group-hover:opacity-100 transition-opacity">Featured Photo</p>
        </div>
      </div>

      <!-- Regular images -->
      <div class="bg-gradient-to-br from-green-400 to-green-600 rounded-xl"></div>
      <div class="bg-gradient-to-br from-purple-400 to-purple-600 rounded-xl"></div>

      <!-- Wide image: 2 cols -->
      <div class="col-span-2 bg-gradient-to-br from-rose-400 to-rose-600 rounded-xl"></div>

      <!-- Tall image: 2 rows -->
      <div class="row-span-2 bg-gradient-to-br from-amber-400 to-amber-600 rounded-xl"></div>

      <div class="bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-xl"></div>
      <div class="bg-gradient-to-br from-indigo-400 to-indigo-600 rounded-xl"></div>

      <!-- Another wide image -->
      <div class="col-span-2 bg-gradient-to-br from-teal-400 to-teal-600 rounded-xl"></div>

      <div class="bg-gradient-to-br from-pink-400 to-pink-600 rounded-xl"></div>
      <div class="bg-gradient-to-br from-orange-400 to-orange-600 rounded-xl"></div>
    </div>
  </body>
</html>
```

## Common Pitfalls

1. **不知道 v4 的 grid-cols 可以使用任意整數值（v4 陷阱）**：在 v3 中，`grid-cols-13` 或 `grid-cols-15` 不存在於預設值中，需要在 `tailwind.config.js` 中擴充。但在 v4 中，任意整數值都直接可用——`grid-cols-7`、`grid-cols-15` 都可以直接使用，不需要額外設定。如果你習慣性地用 `grid-cols-[repeat(7,1fr)]` 這種 arbitrary value，請改用簡潔的 `grid-cols-7`。

2. **col-span 超過 grid-cols 的欄數**：使用 `grid-cols-3` 但某個子元素用了 `col-span-4`，導致佈局溢出。確保 `col-span` 不超過 `grid-cols` 的數值。

3. **忘記 grid 子元素的預設是 stretch**：Grid 子元素預設會被拉伸填滿整個 cell。如果你不想要這個行為，使用 `place-self-start` 或 `self-start`。

4. **responsive grid 忘記設定 col-span**：在 `grid-cols-1 md:grid-cols-4` 的場景中，如果子元素有 `col-span-2`，在 mobile（grid-cols-1）時，`col-span-2` 會導致子元素嘗試跨 2 欄但只有 1 欄，造成溢出。解決方式：加上 `col-span-1 md:col-span-2`。

5. **混淆 auto-fill 和 auto-fit**：`auto-fill` 會保留空的 track（即使沒有足夠的子元素填滿）；`auto-fit` 會折疊空的 track，讓子元素拉伸填滿空間。大多數情況下你想要的是 `auto-fill`。

## Checklist

- [ ] 能使用 grid-cols-* 定義欄數。
- [ ] 能使用 col-span-* 和 row-span-* 跨欄跨行。
- [ ] 能使用 col-start / col-end 精確定位。
- [ ] 能使用 gap-*、gap-x-*、gap-y-* 控制間距。
- [ ] 能使用 place-items-*、place-content-* 控制對齊。
- [ ] 能建構響應式 grid（grid-cols-1 sm:grid-cols-2 lg:grid-cols-3）。
- [ ] 理解 auto-fill/auto-fit 搭配 minmax 的用法。
- [ ] 能建構 12 欄 Dashboard 佈局。

## Further Reading (official links only)

- [Grid Template Columns](https://tailwindcss.com/docs/grid-template-columns)
- [Grid Template Rows](https://tailwindcss.com/docs/grid-template-rows)
- [Grid Column Span](https://tailwindcss.com/docs/grid-column)
- [Grid Row Span](https://tailwindcss.com/docs/grid-row)
- [Grid Auto Flow](https://tailwindcss.com/docs/grid-auto-flow)
- [Gap](https://tailwindcss.com/docs/gap)
- [Place Items](https://tailwindcss.com/docs/place-items)
- [Place Content](https://tailwindcss.com/docs/place-content)
