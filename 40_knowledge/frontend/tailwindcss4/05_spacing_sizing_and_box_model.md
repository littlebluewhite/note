---
title: "Spacing, Sizing, and the Box Model / 間距、尺寸與盒模型"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "05"
level: beginner
stack: Tailwind CSS 4.1.x
prerequisites: [04_typography_and_text_styling]
---
# Spacing, Sizing, and the Box Model / 間距、尺寸與盒模型

## Goal

在上一章 [04_typography_and_text_styling](04_typography_and_text_styling.md) 中，我們掌握了文字樣式的完整控制。現在要進入 UI 布局的基石——**間距（Spacing）與尺寸（Sizing）**。每個 UI 元素都是一個盒子（box），理解 padding、margin、width、height 以及它們在 Tailwind 中的對應 utility class，是做出精準排版的前提。v4 帶來的重要變革是：**間距數值不再受限於預設刻度**——例如 `w-103`、`p-17` 這類任意數值都可以直接使用，不需要額外設定，因為 v4 的 spacing scale 是動態生成的。

掌握間距與尺寸系統後，你就擁有了控制元素空間的完整能力。下一章 [06_borders_shadows_and_rings](06_borders_shadows_and_rings.md) 將探討邊框、陰影與環形框，為元素加上視覺邊界與層次感。

## Prerequisites

- 已完成第 04 章。
- 理解 CSS Box Model 概念（content、padding、border、margin）。
- 知道 `rem` 單位基於根字級（通常 1rem = 16px）。

## Core Concepts

### Padding (p-*) vs Margin (m-*)
- **何時用 Padding**：控制元素內容與邊界之間的距離。適合卡片內間距、按鈕內間距、區塊內間距。Padding 不會造成元素間的空間塌陷。
- **何時用 Margin**：控制元素與元素之間的距離。但在 Flexbox/Grid 佈局中，建議優先使用 `gap-*` 取代 margin，避免 margin 塌陷問題。

### Fixed Sizing vs Fluid Sizing
- **何時用固定尺寸（w-64, h-48）**：已知確切尺寸的元素，如 icon、avatar、固定寬度的側邊欄。
- **何時用流式尺寸（w-full, w-1/2, w-auto）**：響應式佈局中需要依據父容器動態調整的元素。大多數情況下應優先使用流式尺寸。

### gap-* vs space-* vs Individual Margins
- **何時用 gap-***：Flex 或 Grid 容器中子元素的間距。最推薦的方式，不會有 margin 塌陷問題，且第一個/最後一個子元素不會有多餘的間距。
- **何時用 space-***：非 Flex/Grid 容器中的子元素間距。`space-y-4` 會在每個子元素之間加上 margin-top。
- **何時用個別 margin**：只有特定元素需要特殊間距時。

### v4 Dynamic Spacing vs v3 Fixed Scale
- **何時用動態數值**：v4 允許任意整數值，如 `p-13`、`w-103`、`mt-7`，不需要在設定檔中定義。這大幅減少了 arbitrary value 的需求。
- **何時用 arbitrary value**：非整數或非 0.25rem 倍數的值，如 `p-[13px]`、`w-[calc(100%-2rem)]`。

## Step-by-step

### 1. Padding 方向控制

Tailwind 提供精確的方向控制：

```html
<div class="p-8 space-y-6">
  <!-- 全方向 padding -->
  <div class="p-6 bg-blue-100 border border-blue-300 rounded">
    <code>p-6</code> — 全方向 1.5rem padding
  </div>

  <!-- 水平/垂直 padding -->
  <div class="px-8 py-4 bg-green-100 border border-green-300 rounded">
    <code>px-8 py-4</code> — 水平 2rem，垂直 1rem
  </div>

  <!-- 單方向 padding -->
  <div class="pt-8 pr-4 pb-2 pl-12 bg-purple-100 border border-purple-300 rounded">
    <code>pt-8 pr-4 pb-2 pl-12</code> — 各方向不同
  </div>

  <!-- Inline/Block padding (邏輯方向) -->
  <div class="ps-6 pe-6 bg-orange-100 border border-orange-300 rounded">
    <code>ps-6 pe-6</code> — inline start/end（支援 RTL）
  </div>
</div>
```

### 2. Margin 方向控制與負值

```html
<div class="p-8 space-y-6">
  <!-- 全方向 margin -->
  <div class="m-4 p-4 bg-blue-100 border border-blue-300 rounded">
    <code>m-4</code> — 全方向 1rem margin
  </div>

  <!-- 水平置中 -->
  <div class="mx-auto max-w-md p-4 bg-green-100 border border-green-300 rounded text-center">
    <code>mx-auto max-w-md</code> — 水平置中
  </div>

  <!-- 負 margin（拉出容器） -->
  <div class="p-8 bg-gray-100 rounded-lg">
    <div class="-mx-4 p-4 bg-red-100 border border-red-300 rounded">
      <code>-mx-4</code> — 負 margin 讓元素超出父容器
    </div>
  </div>

  <!-- 單方向 margin -->
  <div class="mt-8 mb-4 ml-12 p-4 bg-yellow-100 border border-yellow-300 rounded">
    <code>mt-8 mb-4 ml-12</code>
  </div>
</div>
```

### 3. Spacing Scale 與 v4 動態值

```html
<div class="p-8">
  <h3 class="text-lg font-bold mb-4">v4 Spacing Scale（基於 0.25rem）</h3>

  <div class="space-y-2">
    <!-- 常用預設值 -->
    <div class="flex items-center gap-4">
      <div class="w-0 h-6 bg-blue-500"></div>
      <code class="text-sm">p-0 → 0</code>
    </div>
    <div class="flex items-center gap-4">
      <div class="w-1 h-6 bg-blue-500"></div>
      <code class="text-sm">p-1 → 0.25rem (4px)</code>
    </div>
    <div class="flex items-center gap-4">
      <div class="w-2 h-6 bg-blue-500"></div>
      <code class="text-sm">p-2 → 0.5rem (8px)</code>
    </div>
    <div class="flex items-center gap-4">
      <div class="w-4 h-6 bg-blue-500"></div>
      <code class="text-sm">p-4 → 1rem (16px)</code>
    </div>
    <div class="flex items-center gap-4">
      <div class="w-8 h-6 bg-blue-500"></div>
      <code class="text-sm">p-8 → 2rem (32px)</code>
    </div>
    <div class="flex items-center gap-4">
      <div class="w-16 h-6 bg-blue-500"></div>
      <code class="text-sm">p-16 → 4rem (64px)</code>
    </div>

    <!-- v4 動態值 — 不需要設定 -->
    <div class="flex items-center gap-4">
      <div class="w-13 h-6 bg-green-500"></div>
      <code class="text-sm text-green-700">p-13 → 3.25rem (52px) ✓ v4 新功能！</code>
    </div>
    <div class="flex items-center gap-4">
      <div class="w-17 h-6 bg-green-500"></div>
      <code class="text-sm text-green-700">p-17 → 4.25rem (68px) ✓ v4 新功能！</code>
    </div>
  </div>
</div>
```

### 4. Width 與 Height

```html
<div class="p-8 space-y-8">
  <!-- 固定寬度 -->
  <div class="space-y-2">
    <div class="w-24 h-10 bg-blue-200 rounded flex items-center justify-center text-sm">w-24</div>
    <div class="w-48 h-10 bg-blue-300 rounded flex items-center justify-center text-sm">w-48</div>
    <div class="w-64 h-10 bg-blue-400 rounded flex items-center justify-center text-sm text-white">w-64</div>
    <div class="w-96 h-10 bg-blue-500 rounded flex items-center justify-center text-sm text-white">w-96</div>
  </div>

  <!-- 百分比寬度 -->
  <div class="space-y-2">
    <div class="w-1/4 h-10 bg-green-300 rounded flex items-center justify-center text-sm">w-1/4</div>
    <div class="w-1/2 h-10 bg-green-400 rounded flex items-center justify-center text-sm">w-1/2</div>
    <div class="w-3/4 h-10 bg-green-500 rounded flex items-center justify-center text-sm text-white">w-3/4</div>
    <div class="w-full h-10 bg-green-600 rounded flex items-center justify-center text-sm text-white">w-full</div>
  </div>

  <!-- v4 動態寬度 -->
  <div class="w-103 h-10 bg-purple-500 rounded flex items-center justify-center text-sm text-white">
    w-103 → 25.75rem ✓ v4 直接使用！
  </div>

  <!-- size-* 同時設定寬高 -->
  <div class="flex gap-4">
    <div class="size-12 bg-rose-300 rounded flex items-center justify-center text-xs">size-12</div>
    <div class="size-16 bg-rose-400 rounded flex items-center justify-center text-xs text-white">size-16</div>
    <div class="size-20 bg-rose-500 rounded flex items-center justify-center text-xs text-white">size-20</div>
  </div>
</div>
```

### 5. Min/Max Width 與 Height

```html
<div class="p-8 space-y-6">
  <!-- min-width -->
  <div class="min-w-[200px] w-1/3 p-4 bg-blue-100 rounded">
    <code>min-w-[200px] w-1/3</code> — 最小 200px，否則佔 1/3
  </div>

  <!-- max-width -->
  <div class="max-w-md mx-auto p-4 bg-green-100 rounded text-center">
    <code>max-w-md</code> — 最大 28rem，常用於內容容器
  </div>

  <!-- 常用 max-width 值 -->
  <div class="space-y-2">
    <div class="max-w-xs p-2 bg-gray-200 rounded text-sm">max-w-xs (20rem)</div>
    <div class="max-w-sm p-2 bg-gray-200 rounded text-sm">max-w-sm (24rem)</div>
    <div class="max-w-md p-2 bg-gray-200 rounded text-sm">max-w-md (28rem)</div>
    <div class="max-w-lg p-2 bg-gray-200 rounded text-sm">max-w-lg (32rem)</div>
    <div class="max-w-xl p-2 bg-gray-200 rounded text-sm">max-w-xl (36rem)</div>
    <div class="max-w-2xl p-2 bg-gray-200 rounded text-sm">max-w-2xl (42rem)</div>
  </div>

  <!-- min-height / max-height -->
  <div class="min-h-[200px] max-h-[400px] overflow-auto p-4 bg-yellow-100 rounded">
    <code>min-h-[200px] max-h-[400px]</code> — 高度範圍控制
  </div>

  <!-- 全螢幕高 -->
  <div class="h-screen bg-gray-50">
    <code>h-screen</code> — 100vh
  </div>
</div>
```

### 6. gap-* 用於 Flex/Grid 間距

```html
<div class="p-8 space-y-8">
  <!-- Flex + gap -->
  <div>
    <p class="text-sm text-gray-500 mb-2">flex + gap-4</p>
    <div class="flex gap-4">
      <div class="w-20 h-20 bg-blue-300 rounded"></div>
      <div class="w-20 h-20 bg-blue-400 rounded"></div>
      <div class="w-20 h-20 bg-blue-500 rounded"></div>
    </div>
  </div>

  <!-- 不同方向的 gap -->
  <div>
    <p class="text-sm text-gray-500 mb-2">flex flex-wrap + gap-x-8 gap-y-4</p>
    <div class="flex flex-wrap gap-x-8 gap-y-4">
      <div class="w-24 h-16 bg-green-300 rounded"></div>
      <div class="w-24 h-16 bg-green-400 rounded"></div>
      <div class="w-24 h-16 bg-green-500 rounded"></div>
      <div class="w-24 h-16 bg-green-300 rounded"></div>
      <div class="w-24 h-16 bg-green-400 rounded"></div>
    </div>
  </div>
</div>
```

### 7. space-* 用於非 Flex/Grid 間距

```html
<div class="p-8">
  <!-- space-y-* 垂直間距 -->
  <div class="space-y-4 max-w-sm">
    <div class="p-4 bg-purple-100 rounded">第一個區塊</div>
    <div class="p-4 bg-purple-200 rounded">第二個區塊</div>
    <div class="p-4 bg-purple-300 rounded">第三個區塊</div>
  </div>

  <!-- space-x-* 水平間距 -->
  <div class="flex space-x-4 mt-8">
    <div class="p-4 bg-orange-100 rounded">A</div>
    <div class="p-4 bg-orange-200 rounded">B</div>
    <div class="p-4 bg-orange-300 rounded">C</div>
  </div>
</div>
```

注意：`space-*` 的原理是對除了第一個以外的子元素加上 margin。在 Flex/Grid 中，優先使用 `gap-*`。

### 8. Box Model 視覺化

```html
<div class="p-12 bg-gray-50">
  <div class="max-w-md mx-auto">
    <p class="text-sm text-gray-500 mb-4">Box Model 視覺化</p>

    <!-- Margin (外層) -->
    <div class="bg-orange-100 p-4 rounded-lg">
      <p class="text-xs text-orange-600 mb-2">Margin (m-4)</p>

      <!-- Border -->
      <div class="border-4 border-yellow-400 rounded-lg">
        <p class="text-xs text-yellow-700 px-2 pt-1">Border (border-4)</p>

        <!-- Padding -->
        <div class="bg-green-100 m-0 p-6 rounded">
          <p class="text-xs text-green-600 mb-2">Padding (p-6)</p>

          <!-- Content -->
          <div class="bg-blue-200 p-4 rounded text-center">
            <p class="text-blue-800 font-medium">Content</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 9. Aspect Ratio

```html
<div class="p-8">
  <div class="grid grid-cols-3 gap-6">
    <div>
      <p class="text-sm text-gray-500 mb-2">aspect-square (1:1)</p>
      <div class="aspect-square bg-blue-300 rounded-lg"></div>
    </div>
    <div>
      <p class="text-sm text-gray-500 mb-2">aspect-video (16:9)</p>
      <div class="aspect-video bg-green-300 rounded-lg"></div>
    </div>
    <div>
      <p class="text-sm text-gray-500 mb-2">aspect-[4/3]</p>
      <div class="aspect-[4/3] bg-purple-300 rounded-lg"></div>
    </div>
  </div>
</div>
```

### 10. 組合應用：Profile Card

```html
<div class="max-w-sm mx-auto bg-white rounded-xl shadow-md overflow-hidden">
  <div class="aspect-[3/1] bg-gradient-to-r from-blue-500 to-purple-500"></div>
  <div class="px-6 pb-6">
    <div class="-mt-12 mb-4">
      <div class="size-24 bg-white rounded-full border-4 border-white shadow-md overflow-hidden">
        <div class="size-full bg-gray-300 rounded-full"></div>
      </div>
    </div>
    <h3 class="text-xl font-bold text-gray-900 mb-1">使用者名稱</h3>
    <p class="text-gray-500 mb-4">Full Stack Developer</p>
    <div class="flex gap-3">
      <span class="px-3 py-1 bg-blue-50 text-blue-600 text-sm rounded-full">React</span>
      <span class="px-3 py-1 bg-green-50 text-green-600 text-sm rounded-full">Tailwind</span>
      <span class="px-3 py-1 bg-purple-50 text-purple-600 text-sm rounded-full">TypeScript</span>
    </div>
  </div>
</div>
```

## Hands-on Lab

### Foundation

建立一個 Spacing 視覺化展示頁面，用色塊展示 padding（p-1 到 p-16）和 margin（m-1 到 m-16）的大小差異。

**驗收清單：**
- [ ] Padding 展示至少 8 個不同級距。
- [ ] Margin 展示至少 8 個不同級距。
- [ ] 每個級距都有標籤標註 utility class 名稱和實際值。
- [ ] 有方向性 padding 展示（pt/pr/pb/pl 或 px/py）。

### Advanced

設計一張名片（Business Card）元件，要求：
- 3:5 長寬比。
- 左側有色彩條紋裝飾（負 margin 技巧）。
- 內容區使用精確的 padding 層次（外框 p-6、內部區塊 p-4）。
- 使用 `gap-*` 管理按鈕列間距。

**驗收清單：**
- [ ] 長寬比接近 3:5（可用 aspect-[3/5]）。
- [ ] 使用了負 margin 技巧。
- [ ] padding 層次至少 2 層。
- [ ] 按鈕列使用 gap-* 而非 margin。

### Challenge

建立一個 Dashboard 頁面骨架，包含：
- 頂部導覽列（h-16, px-6）
- 左側邊欄（w-64, py-4）
- 主內容區（flex-1, p-6）
- 底部狀態列（h-10）

所有間距必須使用 Tailwind spacing scale（不使用 arbitrary values），且在視窗縮小時保持合理的最小尺寸。

**驗收清單：**
- [ ] 四個區域都存在且佈局正確。
- [ ] 沒有使用任何 arbitrary spacing values。
- [ ] 使用了 min-w-* 或 min-h-* 確保最小尺寸。
- [ ] 主內容區域的高度填滿剩餘空間（h-screen + flex 佈局）。

## Reference Solution

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Dashboard Layout</title>
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body class="h-screen flex flex-col bg-gray-100">
    <!-- Top Nav -->
    <nav class="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between shrink-0">
      <h1 class="text-xl font-bold text-gray-900">Dashboard</h1>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-500">User</span>
        <div class="size-8 bg-blue-500 rounded-full"></div>
      </div>
    </nav>

    <!-- Main Area -->
    <div class="flex flex-1 min-h-0">
      <!-- Sidebar -->
      <aside class="w-64 bg-white border-r border-gray-200 py-4 shrink-0 overflow-y-auto">
        <nav class="space-y-1 px-3">
          <a href="#" class="block px-3 py-2 bg-blue-50 text-blue-700 rounded-lg font-medium text-sm">
            首頁
          </a>
          <a href="#" class="block px-3 py-2 text-gray-600 hover:bg-gray-50 rounded-lg text-sm">
            專案
          </a>
          <a href="#" class="block px-3 py-2 text-gray-600 hover:bg-gray-50 rounded-lg text-sm">
            設定
          </a>
        </nav>
      </aside>

      <!-- Content -->
      <main class="flex-1 p-6 overflow-y-auto">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Overview</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div class="bg-white p-6 rounded-xl shadow-sm">
            <p class="text-sm text-gray-500 mb-1">Total Users</p>
            <p class="text-3xl font-bold text-gray-900">12,345</p>
          </div>
          <div class="bg-white p-6 rounded-xl shadow-sm">
            <p class="text-sm text-gray-500 mb-1">Revenue</p>
            <p class="text-3xl font-bold text-gray-900">$67,890</p>
          </div>
          <div class="bg-white p-6 rounded-xl shadow-sm">
            <p class="text-sm text-gray-500 mb-1">Orders</p>
            <p class="text-3xl font-bold text-gray-900">2,345</p>
          </div>
        </div>
      </main>
    </div>

    <!-- Status Bar -->
    <footer class="h-10 bg-white border-t border-gray-200 px-6 flex items-center shrink-0">
      <p class="text-xs text-gray-400">Status: Online | v4.1.x</p>
    </footer>
  </body>
</html>
```

## Common Pitfalls

1. **不知道 v4 支援任意整數 spacing 值（v4 陷阱）**：在 v3 中，`p-13` 不存在（預設 scale 跳過 13），你必須用 `p-[3.25rem]`。但在 v4 中，`p-13`、`w-103`、`mt-7` 等任意整數值都直接可用，不需要任何設定。如果你習慣性地使用 arbitrary values（`p-[52px]`），請先嘗試對應的整數值。

2. **在 Flex/Grid 中使用 space-* 而非 gap-***：`space-y-4` 的原理是 `> * + * { margin-top: 1rem; }`，在 Flex/Grid 中可能與 `flex-wrap` 等屬性衝突。優先使用 `gap-4`。

3. **忘記 mx-auto 需要搭配 max-width**：單獨使用 `mx-auto` 只有在元素有明確寬度（如 `max-w-md`）時才有效。對 `w-full` 的元素使用 `mx-auto` 沒有任何效果。

4. **混淆 w-screen 與 w-full**：`w-full` 是 100% 父容器寬度；`w-screen` 是 100vw 視窗寬度。在有捲軸的頁面中，`w-screen` 會包含捲軸寬度，可能導致水平溢出。

5. **忽略 shrink-0 在固定元素上的重要性**：在 flex 佈局中，固定尺寸的元素（如側邊欄 `w-64`）可能被壓縮。加上 `shrink-0` 確保它不會被壓縮。

## Checklist

- [ ] 能使用 p-*、px-*、py-*、pt/pr/pb/pl-* 設定 padding。
- [ ] 能使用 m-*、mx-*、my-*、mt/mr/mb/ml-* 設定 margin（含負值）。
- [ ] 能使用 w-*、h-*、size-* 設定尺寸。
- [ ] 能使用 min-w-*、max-w-*、min-h-*、max-h-* 限制尺寸。
- [ ] 知道 gap-* 與 space-* 的差異及適用場景。
- [ ] 理解 v4 動態 spacing scale（任意整數值可直接使用）。
- [ ] 會使用 aspect-* 控制長寬比。

## Further Reading (official links only)

- [Padding](https://tailwindcss.com/docs/padding)
- [Margin](https://tailwindcss.com/docs/margin)
- [Width](https://tailwindcss.com/docs/width)
- [Height](https://tailwindcss.com/docs/height)
- [Size](https://tailwindcss.com/docs/size)
- [Gap](https://tailwindcss.com/docs/gap)
- [Space Between](https://tailwindcss.com/docs/space)
