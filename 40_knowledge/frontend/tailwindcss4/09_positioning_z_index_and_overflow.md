---
title: "Positioning, Z-Index, and Overflow / 定位、Z-Index 與溢位"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "09"
level: intermediate
stack: Tailwind CSS 4.1.x
prerequisites: [08_grid_layout]
---

# Positioning, Z-Index, and Overflow / 定位、Z-Index 與溢位

## Goal

在前一章 [[08_grid_layout]] 中，我們學會了使用 Grid 進行二維佈局。然而，真實的介面不只需要排列元素，還需要讓元素能夠脫離文件流、堆疊在其他元素之上，或是控制內容溢出時的行為。本章將深入探討 CSS 定位機制在 Tailwind CSS v4 中的實踐方式。

定位（Positioning）是 CSS 佈局系統中最強大也最容易誤用的功能之一。我們會依序學習 `static`、`relative`、`absolute`、`fixed`、`sticky` 五種定位模式，搭配 `inset-*`、`top-*`、`right-*`、`bottom-*`、`left-*` 偏移工具類別，以及 `z-*` 堆疊層級控制和 `overflow-*` 溢位管理。掌握這些之後，你將能夠構建如固定導覽列、浮動按鈕、黏性標頭、彈出視窗等常見 UI 模式。下一章 [[10_responsive_design_and_breakpoints]] 將進入響應式設計，屆時會結合本章的定位技巧來處理不同螢幕尺寸的佈局。

## Prerequisites

- 已完成 [[08_grid_layout]]，熟悉 Tailwind CSS v4 的 Flexbox 與 Grid 佈局。
- 理解 CSS Box Model（盒模型）基本概念。
- 知道 HTML 元素的文件流（Document Flow）概念。
- 已安裝 Tailwind CSS v4 開發環境。

## Core Concepts

### 1. Position Modes / 定位模式

五種定位模式各有不同的脫離文件流行為與定位參照：

| 工具類別 | CSS 值 | 是否脫離文件流 | 定位參照 | 何時使用 | 何時不使用 |
|----------|--------|---------------|----------|----------|------------|
| `static` | `position: static` | 否 | 無（預設） | 大多數元素的預設狀態，不需要特殊定位時 | 需要偏移或堆疊控制時 |
| `relative` | `position: relative` | 否（保留空間） | 自身原本位置 | 作為 absolute 子元素的定位容器；需要微調偏移但保留佈局空間 | 不需要任何定位功能時（多餘的宣告） |
| `absolute` | `position: absolute` | 是 | 最近的非 static 祖先 | 浮動標籤、Badge、下拉選單、Tooltip 等需要脫離文件流的元素 | 需要佔據佈局空間時；大面積區塊佈局 |
| `fixed` | `position: fixed` | 是 | 瀏覽器視窗（viewport） | 固定導覽列、浮動操作按鈕、全螢幕 Modal 背景遮罩 | 內容會在可捲動容器內時（改用 sticky） |
| `sticky` | `position: sticky` | 否（直到觸發閾值） | 最近的可捲動祖先 | 黏性標頭、側邊欄目錄、表格凍結行列 | 父容器高度與元素相同時（無捲動空間） |

### 2. Inset and Offset Utilities / 偏移工具類別

Tailwind CSS v4 提供完整的偏移工具類別，用於控制定位元素的位置：

| 工具類別 | 說明 | 何時使用 | 何時不使用 |
|----------|------|----------|------------|
| `inset-0` | 同時設定 top/right/bottom/left 為 0 | 需要元素填滿定位容器時（如遮罩層） | 只需單一方向偏移時 |
| `inset-x-0` | 同時設定 left 與 right 為 0 | 水平方向填滿（如固定寬度的 bar） | 不需要水平全展時 |
| `inset-y-0` | 同時設定 top 與 bottom 為 0 | 垂直方向填滿（如側邊欄） | 不需要垂直全展時 |
| `top-4`, `right-2` 等 | 個別方向偏移 | 精確控制單一方向位置 | 需要多方向一次設定時（改用 inset） |
| `-top-2` | 負值偏移 | 元素需要超出容器邊界時（如 Badge） | 一般定位場景 |

### 3. Z-Index Scale / Z-Index 堆疊層級

Tailwind CSS v4 提供預設的 z-index 刻度：

| 工具類別 | CSS 值 | 何時使用 | 何時不使用 |
|----------|--------|----------|------------|
| `z-0` | `z-index: 0` | 明確宣告基礎層 | 不需要堆疊控制時 |
| `z-10` ~ `z-50` | `z-index: 10` ~ `50` | 根據元素重要程度分層（下拉選單 z-10、Modal z-40、Toast z-50） | 隨意使用不考慮系統性分層 |
| `z-auto` | `z-index: auto` | 重置回瀏覽器預設堆疊行為 | 需要明確堆疊順序時 |
| `z-[999]` | 任意值 | 與第三方元件整合需要超高 z-index | 自己的專案內（應使用預設刻度保持一致） |

### 4. Overflow Control / 溢位控制

| 工具類別 | 說明 | 何時使用 | 何時不使用 |
|----------|------|----------|------------|
| `overflow-auto` | 內容溢出時顯示捲軸 | 固定高度容器需要可捲動（如聊天視窗） | 容器不限高度時 |
| `overflow-hidden` | 隱藏溢出內容 | 圓角容器裁切子元素、防止佈局破版 | 使用者需要看到所有內容時 |
| `overflow-scroll` | 永遠顯示捲軸 | 需要保留捲軸空間避免佈局跳動 | 內容確定不會溢出時（浪費空間） |
| `overflow-visible` | 允許溢出（預設） | 下拉選單、Tooltip 等需要超出容器邊界 | 容器有固定尺寸且不希望破版時 |
| `overflow-x-auto` | 僅水平方向可捲動 | 水平捲動的表格、程式碼區塊 | 不需要獨立控制單軸時 |
| `overflow-y-hidden` | 僅垂直方向隱藏 | 水平輪播圖不需要垂直捲動 | 需要垂直捲動時 |

## Step-by-step

### Step 1: 理解定位上下文（Positioning Context）

建立一個基礎的定位容器，讓子元素可以相對於它來定位。`relative` 是最常用的定位容器宣告。

```html
<!-- 定位容器：relative 不會改變元素本身位置，但建立了定位上下文 -->
<div class="relative h-64 w-full rounded-lg border-2 border-dashed border-gray-300 bg-gray-50">
  <p class="p-4 text-gray-500">我是定位容器（positioning context）</p>

  <!-- absolute 子元素：參照 relative 父元素來定位 -->
  <span class="absolute right-2 top-2 rounded-full bg-red-500 px-2 py-1 text-xs text-white">
    Badge
  </span>
</div>
```

**關鍵觀察：** 如果移除父元素的 `relative`，`absolute` 子元素會參照更上層的定位祖先（最終是 `<html>`）。

### Step 2: 使用 inset 快速填滿容器

`inset-0` 同時設定四個方向為 0，常用於遮罩層或背景填充。

```html
<!-- Modal 遮罩：fixed + inset-0 填滿整個視窗 -->
<div class="fixed inset-0 z-40 bg-black/50">
  <!-- Modal 內容：置中顯示 -->
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-2xl">
      <h2 class="text-xl font-bold">Modal 標題</h2>
      <p class="mt-2 text-gray-600">這是一個全螢幕遮罩 + 置中 Modal 的範例。</p>
      <button class="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-white">關閉</button>
    </div>
  </div>
</div>
```

### Step 3: 建立 Sticky Header

`sticky` 元素在捲動到指定閾值前表現如 `relative`，之後變為固定。必須搭配偏移值（如 `top-0`）才能生效。

```html
<header class="sticky top-0 z-30 border-b border-gray-200 bg-white/80 px-6 py-4 backdrop-blur-md">
  <nav class="flex items-center justify-between">
    <a href="/" class="text-xl font-bold text-gray-900">MyApp</a>
    <ul class="flex gap-6">
      <li><a href="#features" class="text-gray-600 hover:text-gray-900">Features</a></li>
      <li><a href="#pricing" class="text-gray-600 hover:text-gray-900">Pricing</a></li>
      <li><a href="#contact" class="text-gray-600 hover:text-gray-900">Contact</a></li>
    </ul>
  </nav>
</header>
```

**v4 備註：** `bg-white/80` 使用 Tailwind CSS v4 的色彩透明度語法，搭配 `backdrop-blur-md` 實現毛玻璃效果。

### Step 4: 精確控制偏移值

Tailwind CSS v4 的偏移值對應 spacing scale。可使用分數值或任意值。

```html
<div class="relative h-48 w-48 bg-gray-100">
  <!-- spacing scale 值 -->
  <div class="absolute left-4 top-4 h-8 w-8 rounded bg-blue-500"></div>

  <!-- 百分比值 -->
  <div class="absolute left-1/2 top-1/2 h-8 w-8 -translate-x-1/2 -translate-y-1/2 rounded bg-red-500"></div>

  <!-- 任意值（Arbitrary values） -->
  <div class="absolute bottom-[10px] right-[10px] h-8 w-8 rounded bg-green-500"></div>

  <!-- 負值偏移：元素超出容器 -->
  <div class="absolute -right-2 -top-2 h-6 w-6 rounded-full bg-orange-500"></div>
</div>
```

### Step 5: Z-Index 系統性分層

建立一致的 z-index 分層策略，避免混亂的堆疊問題。

```html
<!--
  建議的 z-index 分層策略：
  z-0  : 基礎內容層
  z-10 : 浮動元素（Dropdown, Popover）
  z-20 : 固定導覽列（Sticky/Fixed header）
  z-30 : 側邊欄（Sidebar overlay）
  z-40 : Modal 遮罩（Modal backdrop）
  z-50 : Toast / Notification
-->

<div class="relative">
  <!-- 基礎內容 -->
  <main class="z-0">
    <p>頁面主要內容</p>
  </main>

  <!-- 固定導覽列 -->
  <header class="fixed top-0 z-20 w-full bg-white shadow-sm">
    <nav class="px-6 py-4">導覽列</nav>
  </header>

  <!-- Dropdown（出現在導覽列上方的內容） -->
  <div class="absolute z-10 mt-2 w-48 rounded-md bg-white shadow-lg ring-1 ring-black/5">
    <a href="#" class="block px-4 py-2 text-sm text-gray-700">選項一</a>
    <a href="#" class="block px-4 py-2 text-sm text-gray-700">選項二</a>
  </div>

  <!-- Modal -->
  <div class="fixed inset-0 z-40 bg-black/50"></div>
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="rounded-xl bg-white p-8 shadow-2xl">Modal 內容</div>
  </div>
</div>
```

### Step 6: Overflow 實戰模式

```html
<!-- 固定高度可捲動容器 -->
<div class="h-64 overflow-y-auto rounded-lg border border-gray-200">
  <ul class="divide-y divide-gray-100">
    <li class="px-4 py-3">項目 1</li>
    <li class="px-4 py-3">項目 2</li>
    <li class="px-4 py-3">項目 3</li>
    <!-- ... 更多項目 -->
    <li class="px-4 py-3">項目 20</li>
  </ul>
</div>

<!-- 水平捲動表格 -->
<div class="overflow-x-auto rounded-lg border border-gray-200">
  <table class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-50">
      <tr>
        <th class="whitespace-nowrap px-6 py-3 text-left text-sm font-medium text-gray-500">Name</th>
        <th class="whitespace-nowrap px-6 py-3 text-left text-sm font-medium text-gray-500">Email</th>
        <th class="whitespace-nowrap px-6 py-3 text-left text-sm font-medium text-gray-500">Role</th>
        <th class="whitespace-nowrap px-6 py-3 text-left text-sm font-medium text-gray-500">Status</th>
        <th class="whitespace-nowrap px-6 py-3 text-left text-sm font-medium text-gray-500">Actions</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-200 bg-white">
      <tr>
        <td class="whitespace-nowrap px-6 py-4 text-sm">Alice</td>
        <td class="whitespace-nowrap px-6 py-4 text-sm">alice@example.com</td>
        <td class="whitespace-nowrap px-6 py-4 text-sm">Admin</td>
        <td class="whitespace-nowrap px-6 py-4 text-sm">Active</td>
        <td class="whitespace-nowrap px-6 py-4 text-sm">Edit | Delete</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- overflow-hidden 裁切圓角 -->
<div class="overflow-hidden rounded-2xl">
  <img src="/hero.jpg" alt="Hero" class="h-64 w-full object-cover" />
</div>
```

### Step 7: 組合 Fixed + Absolute 建立浮動操作按鈕

```html
<!-- 固定在右下角的 FAB（Floating Action Button） -->
<button class="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700">
  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
  </svg>
</button>
```

### Step 8: Sticky 側邊欄目錄

```html
<div class="flex gap-8">
  <!-- 主要內容 -->
  <main class="flex-1">
    <section id="section-1" class="mb-16">
      <h2 class="text-2xl font-bold">Section 1</h2>
      <p class="mt-4 leading-relaxed text-gray-600">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt
        ut labore et dolore magna aliqua. Ut enim ad minim veniam...
      </p>
    </section>
    <section id="section-2" class="mb-16">
      <h2 class="text-2xl font-bold">Section 2</h2>
      <p class="mt-4 leading-relaxed text-gray-600">內容...</p>
    </section>
    <section id="section-3" class="mb-16">
      <h2 class="text-2xl font-bold">Section 3</h2>
      <p class="mt-4 leading-relaxed text-gray-600">內容...</p>
    </section>
  </main>

  <!-- Sticky 側邊目錄 -->
  <aside class="sticky top-20 hidden h-fit w-56 lg:block">
    <h3 class="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
      On this page
    </h3>
    <nav class="space-y-2">
      <a href="#section-1" class="block text-sm text-gray-600 hover:text-blue-600">Section 1</a>
      <a href="#section-2" class="block text-sm text-gray-600 hover:text-blue-600">Section 2</a>
      <a href="#section-3" class="block text-sm text-gray-600 hover:text-blue-600">Section 3</a>
    </nav>
  </aside>
</div>
```

### Step 9: 進階置中技巧

除了 Flexbox 置中以外，定位也能實現精確置中。

```html
<!-- 方法一：absolute + inset-0 + margin auto（需要固定尺寸） -->
<div class="relative h-64 bg-gray-100">
  <div class="absolute inset-0 m-auto h-24 w-24 rounded-lg bg-blue-500"></div>
</div>

<!-- 方法二：absolute + translate（不需要固定尺寸） -->
<div class="relative h-64 bg-gray-100">
  <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-lg bg-red-500 px-6 py-3">
    任意尺寸內容
  </div>
</div>

<!-- 方法三（推薦）：Flexbox 置中 -->
<div class="flex h-64 items-center justify-center bg-gray-100">
  <div class="rounded-lg bg-green-500 px-6 py-3">最簡潔</div>
</div>
```

### Step 10: Tailwind CSS v4 中的定位相關變化

在 Tailwind CSS v4 中，定位工具類別的核心用法保持一致，但有幾個值得注意的改進：

```css
/* v4: 可透過 @theme 自訂 z-index 刻度 */
@theme {
  --z-modal: 100;
  --z-toast: 200;
  --z-tooltip: 300;
}
```

```html
<!-- 使用自訂 z-index -->
<div class="z-modal">Modal Layer</div>
<div class="z-toast">Toast Layer</div>
<div class="z-tooltip">Tooltip Layer</div>
```

```css
/* v4: 所有工具類別都透過 CSS 層級（@layer）管理，定位類別在 utilities 層 */
/* 這意味著自訂 CSS 可以更容易覆蓋 Tailwind 的定位樣式 */
@layer utilities {
  /* Tailwind 自動生成的定位類別在此層 */
}
```

## Hands-on Lab

### Foundation 基礎練習

**任務：** 建立一個黏性導覽列（Sticky Header）。

需求：
- 導覽列使用 `sticky top-0` 固定在頁面頂部
- 背景使用半透明白色 + `backdrop-blur` 毛玻璃效果
- 包含 Logo（左側）和導覽連結（右側）
- 下方放置足夠長的內容讓頁面可捲動
- 設定合理的 z-index

**驗收清單：**
- [ ] 導覽列在捲動時固定在頂部
- [ ] 毛玻璃效果正常顯示
- [ ] Logo 與連結排列正確
- [ ] z-index 確保導覽列在內容之上

### Advanced 進階練習

**任務：** 建立一個帶有 Overlay Modal 的頁面。

需求：
- 頁面有固定導覽列（sticky）
- 點擊按鈕時顯示 Modal
- Modal 包含半透明黑色遮罩層（`fixed inset-0`）
- Modal 內容置中顯示
- z-index 分層正確（導覽列 < 遮罩 < Modal 內容）
- Modal 內部有可捲動的長內容

**驗收清單：**
- [ ] Modal 遮罩填滿整個視窗
- [ ] Modal 內容水平垂直置中
- [ ] z-index 層級正確，Modal 在導覽列之上
- [ ] Modal 內部內容可捲動（`overflow-y-auto`）
- [ ] 遮罩使用 `bg-black/50` 半透明效果

### Challenge 挑戰練習

**任務：** 建立一個完整的頁面佈局，包含：
- Sticky header
- Fixed sidebar（桌面版）
- Floating action button（右下角）
- Toast notification area（右上角）
- 主內容區域有黏性子導覽

需求：
- 所有元素的 z-index 遵循統一分層策略
- 側邊欄使用 `fixed left-0 top-16`（避開 header 高度）
- Toast 區域使用 `fixed top-4 right-4` 並有最高 z-index
- 主內容區域使用 `overflow-y-auto` 且有獨立捲動

**驗收清單：**
- [ ] 五個定位元素各自正確顯示
- [ ] z-index 分層清晰且無衝突
- [ ] 側邊欄不遮擋 header
- [ ] Toast 在所有元素之上
- [ ] 主內容區域獨立捲動

## Reference Solution

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ch09 Lab - Positioning Demo</title>
  <link rel="stylesheet" href="/src/output.css" />
</head>
<body class="min-h-screen bg-gray-50 text-gray-900">

  <!-- ====== Sticky Header (z-20) ====== -->
  <header class="sticky top-0 z-20 border-b border-gray-200 bg-white/80 backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
      <a href="/" class="text-xl font-bold text-blue-600">MyApp</a>
      <nav class="hidden gap-6 md:flex">
        <a href="#features" class="text-sm text-gray-600 hover:text-gray-900">Features</a>
        <a href="#pricing" class="text-sm text-gray-600 hover:text-gray-900">Pricing</a>
        <a href="#about" class="text-sm text-gray-600 hover:text-gray-900">About</a>
      </nav>
      <button
        id="modal-trigger"
        class="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
      >
        Open Modal
      </button>
    </div>
  </header>

  <!-- ====== Fixed Sidebar (z-10, desktop only) ====== -->
  <aside class="fixed bottom-0 left-0 top-16 z-10 hidden w-56 overflow-y-auto border-r border-gray-200 bg-white px-4 py-6 lg:block">
    <h3 class="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">Menu</h3>
    <nav class="space-y-1">
      <a href="#" class="block rounded-lg bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700">Dashboard</a>
      <a href="#" class="block rounded-lg px-3 py-2 text-sm text-gray-600 hover:bg-gray-50">Projects</a>
      <a href="#" class="block rounded-lg px-3 py-2 text-sm text-gray-600 hover:bg-gray-50">Team</a>
      <a href="#" class="block rounded-lg px-3 py-2 text-sm text-gray-600 hover:bg-gray-50">Settings</a>
    </nav>
  </aside>

  <!-- ====== Main Content ====== -->
  <main class="mx-auto max-w-4xl px-6 py-12 lg:ml-56">
    <!-- Sticky Sub-navigation -->
    <nav class="sticky top-16 z-10 -mx-6 mb-8 border-b border-gray-200 bg-gray-50/90 px-6 py-3 backdrop-blur-sm">
      <ul class="flex gap-4 text-sm">
        <li><a href="#section-1" class="font-medium text-blue-600">Section 1</a></li>
        <li><a href="#section-2" class="text-gray-500 hover:text-gray-900">Section 2</a></li>
        <li><a href="#section-3" class="text-gray-500 hover:text-gray-900">Section 3</a></li>
      </ul>
    </nav>

    <section id="section-1" class="mb-24">
      <h2 class="text-3xl font-bold">Section 1: Features</h2>
      <p class="mt-4 leading-relaxed text-gray-600">
        本區塊展示了定位系統的各種應用場景。Tailwind CSS v4 的定位工具類別讓我們能夠
        快速建立複雜的佈局結構，而不需要撰寫自訂 CSS。透過 utility-first 的方式，
        每個定位行為都是透明的、可讀的。
      </p>
      <p class="mt-4 leading-relaxed text-gray-600">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus lacinia odio vitae
        vestibulum vestibulum. Cras porta malesuada magna, ut vehicula nisi. Donec maximus
        ultricies erat, sit amet efficitur est placerat id. Nullam auctor, nisi eu aliquam
        hendrerit, nunc nunc tincidunt urna, sit amet interdum nibh magna non lorem.
      </p>
    </section>

    <section id="section-2" class="mb-24">
      <h2 class="text-3xl font-bold">Section 2: Pricing</h2>
      <p class="mt-4 leading-relaxed text-gray-600">
        在定價方案卡片中，我們常使用 relative + absolute 來放置「推薦」標籤。
        這是定位系統的典型應用場景之一。
      </p>
      <!-- 定價卡片範例 -->
      <div class="relative mt-8 rounded-2xl border-2 border-blue-500 bg-white p-8 shadow-lg">
        <span class="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-blue-500 px-4 py-1 text-xs font-semibold text-white">
          Most Popular
        </span>
        <h3 class="text-xl font-bold">Pro Plan</h3>
        <p class="mt-2 text-3xl font-bold">$29<span class="text-base font-normal text-gray-500">/mo</span></p>
        <ul class="mt-6 space-y-2 text-sm text-gray-600">
          <li>Unlimited projects</li>
          <li>Priority support</li>
          <li>Advanced analytics</li>
        </ul>
      </div>
    </section>

    <section id="section-3" class="mb-24">
      <h2 class="text-3xl font-bold">Section 3: About</h2>
      <p class="mt-4 leading-relaxed text-gray-600">
        關於我們的介紹段落。這裡的內容足夠長，以確保頁面可以捲動，
        讓你體驗 sticky header 和 sticky sub-navigation 的效果。
      </p>
      <p class="mt-4 leading-relaxed text-gray-600">
        Proin sagittis nisl rhoncus mattis rhoncus urna neque. Maecenas pharetra convallis
        posuere morbi. Amet consectetur adipiscing elit duis tristique. Nulla facilisi cras
        fermentum odio eu feugiat pretium nibh ipsum.
      </p>
    </section>
  </main>

  <!-- ====== Modal Overlay (z-40 backdrop, z-50 content) ====== -->
  <div id="modal" class="pointer-events-none fixed inset-0 z-40 opacity-0 transition-opacity duration-300">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/50"></div>
    <!-- Modal Content -->
    <div class="absolute inset-0 flex items-center justify-center p-4">
      <div class="relative z-50 max-h-[80vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-white p-8 shadow-2xl">
        <h2 class="text-2xl font-bold">Modal Title</h2>
        <p class="mt-4 text-gray-600">
          這是一個 Modal 範例。注意 z-index 分層：backdrop (z-40) 在導覽列 (z-20) 之上，
          Modal 內容 (z-50) 在 backdrop 之上。
        </p>
        <p class="mt-4 text-gray-600">
          Modal 內部使用 overflow-y-auto 和 max-h-[80vh] 來確保長內容也能正常捲動。
        </p>
        <div class="mt-4 space-y-4 text-gray-600">
          <p>額外內容段落 1...</p>
          <p>額外內容段落 2...</p>
          <p>額外內容段落 3...</p>
        </div>
        <button
          id="modal-close"
          class="mt-6 w-full rounded-lg bg-gray-900 px-4 py-2 text-white hover:bg-gray-800"
        >
          Close Modal
        </button>
      </div>
    </div>
  </div>

  <!-- ====== Floating Action Button (z-30) ====== -->
  <button class="fixed bottom-6 right-6 z-30 flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-transform hover:scale-110 hover:bg-blue-700">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
    </svg>
  </button>

  <!-- ====== Toast Notification Area (z-50) ====== -->
  <div class="fixed right-4 top-20 z-50 w-80 space-y-3">
    <div class="flex items-start gap-3 rounded-lg border border-green-200 bg-green-50 p-4 shadow-md">
      <span class="text-green-600">&#10003;</span>
      <div>
        <p class="text-sm font-medium text-green-800">Success!</p>
        <p class="text-xs text-green-600">Your changes have been saved.</p>
      </div>
    </div>
  </div>

  <script>
    const trigger = document.getElementById('modal-trigger');
    const modal = document.getElementById('modal');
    const close = document.getElementById('modal-close');

    trigger.addEventListener('click', () => {
      modal.classList.remove('pointer-events-none', 'opacity-0');
      modal.classList.add('pointer-events-auto', 'opacity-100');
    });

    close.addEventListener('click', () => {
      modal.classList.add('pointer-events-none', 'opacity-0');
      modal.classList.remove('pointer-events-auto', 'opacity-100');
    });
  </script>
</body>
</html>
```

## Common Pitfalls

1. **忘記設定定位容器：** 使用 `absolute` 的元素會向上尋找第一個非 `static` 的祖先。如果沒有任何祖先設定 `relative`、`absolute` 或 `fixed`，元素會相對於 `<html>` 定位，導致意料之外的結果。**解法：** 確保定位子元素的父容器加上 `relative`。

2. **Sticky 不生效：** `sticky` 必須同時指定偏移方向（如 `top-0`），且其父容器必須有足夠的高度讓捲動發生。如果父容器高度等於 sticky 元素高度，sticky 不會有任何效果。另外，`overflow: hidden` 或 `overflow: auto` 在祖先元素上會破壞 sticky 行為。

3. **Z-index 戰爭（Z-index Wars）：** 隨意使用 `z-[9999]` 等巨大值來解決堆疊問題是反模式。應該建立系統性的 z-index 分層策略（如本章 Step 5 所示），並在專案中統一遵守。

4. **v4 特定：忽略 CSS 層級對覆蓋順序的影響：** Tailwind CSS v4 使用 `@layer` 管理樣式層級。定位工具類別位於 `utilities` 層，如果你在自訂 CSS 中不使用 `@layer`，可能會因為 CSS 層級優先順序而無法覆蓋 Tailwind 的定位樣式。**解法：** 自訂 CSS 也使用 `@layer utilities { ... }` 或 `@layer components { ... }` 來保持一致。

5. **Fixed 元素在 transform 容器中失效：** 如果 `fixed` 元素的某個祖先有 `transform`、`filter` 或 `will-change` 屬性，`fixed` 會變成類似 `absolute` 的行為。這是 CSS 規範本身的限制，不是 Tailwind 的問題。**解法：** 將 fixed 元素移到沒有 transform 的祖先之外。

## Checklist

- [ ] 能區分 `static`、`relative`、`absolute`、`fixed`、`sticky` 五種定位模式的行為差異。
- [ ] 理解定位上下文（positioning context）的概念，知道 `absolute` 元素如何尋找定位參照。
- [ ] 能使用 `inset-*`、`top-*`、`right-*`、`bottom-*`、`left-*` 控制偏移位置。
- [ ] 能建立系統性的 z-index 分層策略並在專案中一致使用。
- [ ] 能使用 `overflow-auto`、`overflow-hidden`、`overflow-x-auto` 等工具管理溢位內容。
- [ ] 能組合 `sticky top-0` + `backdrop-blur` 建立毛玻璃黏性導覽列。
- [ ] 能使用 `fixed inset-0` 建立全螢幕 Modal 遮罩並正確分層。

## Further Reading (official links only)

- [Position - Tailwind CSS](https://tailwindcss.com/docs/position)
- [Top / Right / Bottom / Left - Tailwind CSS](https://tailwindcss.com/docs/top-right-bottom-left)
- [Z-Index - Tailwind CSS](https://tailwindcss.com/docs/z-index)
- [Overflow - Tailwind CSS](https://tailwindcss.com/docs/overflow)
- [Tailwind CSS v4.0 - tailwindcss.com](https://tailwindcss.com/blog/tailwindcss-v4)
