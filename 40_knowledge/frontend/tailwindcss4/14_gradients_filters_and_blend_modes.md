---
title: "Gradients, Filters, and Blend Modes / 漸層、濾鏡與混合模式"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "14"
level: intermediate
stack: Tailwind CSS 4.1.x
prerequisites: [13_transitions_animations_and_motion]
---

# Gradients, Filters, and Blend Modes / 漸層、濾鏡與混合模式

## Goal

在前一章 [[13_transitions_animations_and_motion]] 中，我們學會了讓 UI 元素動起來。現在，讓我們為這些元素加上更豐富的視覺效果。本章將深入探討 Tailwind CSS v4 的漸層（Gradients）、濾鏡（Filters）和混合模式（Blend Modes）系統。

漸層、濾鏡和混合模式是創造視覺層次和氛圍的關鍵工具。Tailwind CSS v4 在此領域有重大突破：除了延續 v3 的線性漸層（linear gradients）支援外，**v4 新增了原生的放射漸層（radial gradients，`bg-radial-*`）和錐形漸層（conic gradients，`bg-conic-*`）支援**。搭配 `blur-*`、`brightness-*`、`contrast-*` 等濾鏡工具和 `backdrop-blur-*` 等背景濾鏡，以及 `mix-blend-*` 混合模式，你可以在不離開 HTML 的情況下創建令人驚艷的視覺效果。下一章 [[15_container_queries_and_modern_layout_patterns]] 將運用這些視覺效果技巧來建立自適應的元件。

## Prerequisites

- 已完成 [[13_transitions_animations_and_motion]]，熟悉過渡與動畫。
- 理解 CSS `linear-gradient`、`radial-gradient`、`conic-gradient` 的基本概念。
- 知道 CSS `filter` 和 `backdrop-filter` 屬性的基本用法。
- 理解色彩模型的基礎概念（RGB、HSL）。

## Core Concepts

### 1. Gradient Types / 漸層類型

| 類型 | Tailwind 工具 | CSS 對應 | 何時使用 | 何時不使用 |
|------|--------------|---------|----------|------------|
| 線性漸層 | `bg-gradient-to-r` | `linear-gradient(to right, ...)` | 按鈕背景、Hero 區域、分隔線 | 需要從中心擴散的效果時 |
| 放射漸層（v4 新增） | `bg-radial` | `radial-gradient(...)` | 光暈效果、聚焦視覺、背景裝飾 | 需要方向性漸層時 |
| 錐形漸層（v4 新增） | `bg-conic` | `conic-gradient(...)` | 圓餅圖、色輪、旋轉載入指示器 | 不需要角度變化的場景 |

### 2. Filter Utilities / 濾鏡工具

| 工具類別 | CSS 效果 | 何時使用 | 何時不使用 |
|----------|---------|----------|------------|
| `blur-sm` ~ `blur-3xl` | 高斯模糊 | 背景模糊、禁用狀態、隱私遮罩 | 文字需要清晰可讀時 |
| `brightness-50` ~ `brightness-200` | 亮度調整 | 深色模式圖片降亮、hover 提亮 | 已有合適亮度時 |
| `contrast-50` ~ `contrast-200` | 對比度調整 | 增強圖片對比、特殊視覺效果 | 內容需要柔和色調時 |
| `grayscale` | 灰度化 | disabled 狀態、hover 前的預覽 | 彩色是重要資訊時 |
| `saturate-0` ~ `saturate-200` | 飽和度調整 | 深色模式降低飽和度、hover 增飽和 | 顏色已是設計重點時 |
| `drop-shadow-*` | 物件陰影 | 非矩形元素的陰影（如 PNG 圖片） | 矩形元素（用 `shadow-*` 更高效） |

### 3. Backdrop Filter / 背景濾鏡

| 工具類別 | 說明 | 何時使用 | 何時不使用 |
|----------|------|----------|------------|
| `backdrop-blur-*` | 元素背後的模糊 | 毛玻璃 header、Modal 背景 | 不需要透視效果時 |
| `backdrop-brightness-*` | 元素背後的亮度 | 搭配 blur 增強毛玻璃效果 | 獨立使用效果不明顯 |
| `backdrop-saturate-*` | 元素背後的飽和度 | 毛玻璃的色彩加強 | 需要忠實呈現背景時 |

### 4. Blend Modes / 混合模式

| 工具類別 | 效果 | 何時使用 | 何時不使用 |
|----------|------|----------|------------|
| `mix-blend-multiply` | 正片疊底（深色融合） | 文字與背景圖片融合 | 需要明確邊界時 |
| `mix-blend-screen` | 濾色（亮色融合） | 光效疊加 | 深色背景上效果不佳 |
| `mix-blend-overlay` | 覆蓋（對比增強） | 紋理疊加、圖片效果 | 需要自然色彩時 |
| `mix-blend-difference` | 差值（反轉色） | 藝術效果、確保文字在任何背景可見 | 一般 UI 場景 |

## Step-by-step

### Step 1: 線性漸層基礎

```html
<!-- 基礎線性漸層：從左到右 -->
<div class="h-20 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600"></div>

<!-- 所有方向 -->
<div class="grid grid-cols-2 gap-4 md:grid-cols-4">
  <div class="h-20 rounded-lg bg-gradient-to-t from-blue-500 to-cyan-400 p-4 text-sm text-white">to-t</div>
  <div class="h-20 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 p-4 text-sm text-white">to-r</div>
  <div class="h-20 rounded-lg bg-gradient-to-b from-blue-500 to-indigo-600 p-4 text-sm text-white">to-b</div>
  <div class="h-20 rounded-lg bg-gradient-to-l from-pink-500 to-rose-500 p-4 text-sm text-white">to-l</div>
  <div class="h-20 rounded-lg bg-gradient-to-tr from-green-400 to-cyan-500 p-4 text-sm text-white">to-tr</div>
  <div class="h-20 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 p-4 text-sm text-white">to-br</div>
  <div class="h-20 rounded-lg bg-gradient-to-bl from-amber-400 to-orange-500 p-4 text-sm text-white">to-bl</div>
  <div class="h-20 rounded-lg bg-gradient-to-tl from-emerald-400 to-teal-500 p-4 text-sm text-white">to-tl</div>
</div>
```

### Step 2: Via 中間色與色標位置

`via-*` 加入第三個顏色，創建更豐富的漸層。

```html
<!-- 三色漸層 -->
<div class="h-20 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>

<!-- 多段漸層（使用任意值控制色標位置） -->
<div class="h-20 rounded-xl bg-gradient-to-r from-blue-600 from-10% via-sky-400 via-50% to-emerald-400 to-90%"></div>

<!-- 漸層文字 -->
<h1 class="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-4xl font-extrabold text-transparent">
  Gradient Text Effect
</h1>

<!-- 漸層邊框（技巧：使用背景 + padding） -->
<div class="rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 p-[2px]">
  <div class="rounded-[10px] bg-white p-6">
    <p class="text-gray-700">漸層邊框效果</p>
  </div>
</div>
```

### Step 3: 放射漸層（v4 新增）

Tailwind CSS v4 原生支援放射漸層，不再需要任意值。

```html
<!-- 基礎放射漸層 -->
<div class="h-48 rounded-xl bg-radial from-blue-400 to-blue-800"></div>

<!-- 放射漸層位置控制 -->
<div class="h-48 rounded-xl bg-radial-[at_top_left] from-purple-400 to-transparent"></div>

<!-- 橢圓放射漸層 -->
<div class="h-48 rounded-xl bg-radial-[ellipse_at_center] from-yellow-200 via-yellow-400 to-orange-500"></div>

<!-- 光暈效果 -->
<div class="relative h-64 overflow-hidden rounded-xl bg-gray-900">
  <div class="absolute inset-0 bg-radial from-blue-500/30 to-transparent"></div>
  <div class="relative z-10 flex h-full items-center justify-center">
    <h2 class="text-3xl font-bold text-white">Glow Effect</h2>
  </div>
</div>
```

### Step 4: 錐形漸層（v4 新增）

錐形漸層圍繞中心點旋轉，適合創建圓餅圖、色輪等效果。

```html
<!-- 基礎錐形漸層 -->
<div class="h-48 w-48 rounded-full bg-conic from-blue-500 via-purple-500 to-blue-500"></div>

<!-- 色輪 -->
<div class="h-48 w-48 rounded-full bg-conic from-red-500 via-yellow-500 via-green-500 via-blue-500 to-red-500"></div>

<!-- 進度環（搭配漸層角度） -->
<div class="relative h-32 w-32">
  <div class="h-full w-full rounded-full bg-conic from-blue-600 from-[75%] to-gray-200 to-[75%]"></div>
  <div class="absolute inset-2 flex items-center justify-center rounded-full bg-white">
    <span class="text-2xl font-bold text-gray-900">75%</span>
  </div>
</div>

<!-- 裝飾性旋轉漸層 -->
<div class="h-64 w-64 animate-spin rounded-full bg-conic from-transparent via-blue-500 to-transparent"
     style="animation-duration: 3s;"></div>
```

### Step 5: Filter 濾鏡效果

```html
<!-- Blur 模糊 -->
<div class="grid grid-cols-3 gap-4 md:grid-cols-6">
  <div>
    <img src="/photo.jpg" alt="" class="rounded-lg" />
    <p class="mt-1 text-center text-xs">none</p>
  </div>
  <div>
    <img src="/photo.jpg" alt="" class="rounded-lg blur-sm" />
    <p class="mt-1 text-center text-xs">blur-sm</p>
  </div>
  <div>
    <img src="/photo.jpg" alt="" class="rounded-lg blur" />
    <p class="mt-1 text-center text-xs">blur</p>
  </div>
  <div>
    <img src="/photo.jpg" alt="" class="rounded-lg blur-md" />
    <p class="mt-1 text-center text-xs">blur-md</p>
  </div>
  <div>
    <img src="/photo.jpg" alt="" class="rounded-lg blur-lg" />
    <p class="mt-1 text-center text-xs">blur-lg</p>
  </div>
  <div>
    <img src="/photo.jpg" alt="" class="rounded-lg blur-xl" />
    <p class="mt-1 text-center text-xs">blur-xl</p>
  </div>
</div>

<!-- Brightness and Contrast -->
<div class="grid grid-cols-2 gap-4 md:grid-cols-4">
  <img src="/photo.jpg" alt="" class="rounded-lg brightness-50" />
  <img src="/photo.jpg" alt="" class="rounded-lg brightness-75" />
  <img src="/photo.jpg" alt="" class="rounded-lg brightness-125" />
  <img src="/photo.jpg" alt="" class="rounded-lg contrast-150" />
</div>

<!-- Grayscale + Hover 恢復彩色 -->
<img src="/photo.jpg" alt=""
     class="rounded-lg grayscale transition-[filter] duration-500 hover:grayscale-0" />

<!-- Saturate 飽和度 -->
<img src="/photo.jpg" alt=""
     class="rounded-lg saturate-50 transition-[filter] duration-300 hover:saturate-150" />

<!-- 組合濾鏡 -->
<img src="/photo.jpg" alt=""
     class="rounded-lg brightness-110 contrast-125 saturate-150" />
```

### Step 6: Backdrop Filter 背景濾鏡

```html
<!-- 毛玻璃導覽列（最常見用法） -->
<header class="sticky top-0 z-20 border-b border-white/10 bg-white/70 backdrop-blur-lg backdrop-saturate-150">
  <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
    <span class="text-xl font-bold">MyApp</span>
    <nav class="flex gap-6 text-sm">
      <a href="#">Home</a>
      <a href="#">About</a>
    </nav>
  </div>
</header>

<!-- Modal 毛玻璃遮罩 -->
<div class="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm">
  <div class="flex h-full items-center justify-center">
    <div class="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
      <h2 class="text-xl font-bold">Modal Content</h2>
    </div>
  </div>
</div>

<!-- 毛玻璃卡片 -->
<div class="relative overflow-hidden rounded-2xl">
  <img src="/bg.jpg" alt="" class="h-64 w-full object-cover" />
  <div class="absolute inset-0 flex items-end p-6">
    <div class="w-full rounded-xl border border-white/20 bg-white/20 p-4 backdrop-blur-md">
      <h3 class="font-semibold text-white">Frosted Glass Card</h3>
      <p class="mt-1 text-sm text-white/80">Elegant glassmorphism effect.</p>
    </div>
  </div>
</div>
```

### Step 7: Mix Blend Modes 混合模式

```html
<!-- Multiply：文字與背景融合 -->
<div class="relative h-64 overflow-hidden rounded-xl">
  <img src="/photo.jpg" alt="" class="h-full w-full object-cover" />
  <div class="absolute inset-0 bg-blue-600 mix-blend-multiply"></div>
  <div class="absolute inset-0 flex items-center justify-center">
    <h2 class="text-4xl font-bold text-white">Duotone Effect</h2>
  </div>
</div>

<!-- Screen：亮色融合 -->
<div class="relative h-64 overflow-hidden rounded-xl bg-gray-900">
  <img src="/photo.jpg" alt="" class="h-full w-full object-cover mix-blend-screen opacity-60" />
  <div class="absolute inset-0 flex items-center justify-center">
    <h2 class="text-4xl font-bold text-white">Screen Blend</h2>
  </div>
</div>

<!-- Overlay：紋理疊加 -->
<div class="relative h-64 overflow-hidden rounded-xl">
  <div class="absolute inset-0 bg-gradient-to-br from-purple-600 to-blue-600"></div>
  <div class="absolute inset-0 bg-[url('/noise.png')] mix-blend-overlay opacity-50"></div>
  <div class="relative flex h-full items-center justify-center">
    <h2 class="text-4xl font-bold text-white">Textured Background</h2>
  </div>
</div>
```

### Step 8: Hero Section 實戰

```html
<!-- 完整的 Hero Section：漸層覆蓋 + 圖片 + 文字 -->
<section class="relative overflow-hidden">
  <!-- 背景圖片 -->
  <img src="/hero-bg.jpg" alt=""
       class="absolute inset-0 h-full w-full object-cover" />

  <!-- 漸層覆蓋層 -->
  <div class="absolute inset-0 bg-gradient-to-r from-gray-900/90 via-gray-900/70 to-transparent"></div>

  <!-- 裝飾性放射漸層（v4） -->
  <div class="absolute right-0 top-0 h-full w-1/2 bg-radial-[at_center_right] from-blue-500/20 to-transparent"></div>

  <!-- 內容 -->
  <div class="relative mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:py-40">
    <div class="max-w-xl">
      <h1 class="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">
        Build the future
        <span class="block bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
          with modern tools
        </span>
      </h1>
      <p class="mt-6 text-lg text-gray-300">
        Create stunning visual effects with Tailwind CSS v4 gradient,
        filter, and blend mode utilities.
      </p>
      <div class="mt-10 flex gap-4">
        <a href="#"
           class="rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 px-8 py-3 font-medium text-white
                  shadow-lg shadow-blue-500/30
                  transition-all duration-300
                  hover:shadow-xl hover:shadow-blue-500/40 hover:brightness-110">
          Get Started
        </a>
        <a href="#"
           class="rounded-lg border border-white/20 bg-white/10 px-8 py-3 font-medium text-white
                  backdrop-blur-sm
                  transition-all duration-300
                  hover:bg-white/20">
          Learn More
        </a>
      </div>
    </div>
  </div>
</section>
```

### Step 9: React 圖片效果畫廊元件

```tsx
// ImageEffectGallery.tsx
const filters = [
  { name: 'Original', className: '' },
  { name: 'Grayscale', className: 'grayscale' },
  { name: 'Sepia', className: 'sepia' },
  { name: 'Blur', className: 'blur-sm' },
  { name: 'Bright', className: 'brightness-125' },
  { name: 'Contrast', className: 'contrast-125' },
  { name: 'Saturate', className: 'saturate-200' },
  { name: 'Invert', className: 'invert' },
] as const;

export function ImageEffectGallery({ src, alt }: { src: string; alt: string }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      {filters.map((filter) => (
        <div key={filter.name} className="group overflow-hidden rounded-xl">
          <div className="relative">
            <img
              src={src}
              alt={alt}
              className={`aspect-square w-full object-cover transition-[filter] duration-500
                         group-hover:scale-105 ${filter.className}`}
            />
            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-3">
              <p className="text-sm font-medium text-white">{filter.name}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

```svelte
<!-- ImageEffectGallery.svelte -->
<script>
  export let src;
  export let alt;

  const filters = [
    { name: 'Original', className: '' },
    { name: 'Grayscale', className: 'grayscale' },
    { name: 'Sepia', className: 'sepia' },
    { name: 'Blur', className: 'blur-sm' },
    { name: 'Bright', className: 'brightness-125' },
    { name: 'Contrast', className: 'contrast-125' },
    { name: 'Saturate', className: 'saturate-200' },
    { name: 'Invert', className: 'invert' },
  ];
</script>

<div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
  {#each filters as filter}
    <div class="group overflow-hidden rounded-xl">
      <div class="relative">
        <img
          {src}
          {alt}
          class="aspect-square w-full object-cover transition-[filter] duration-500
                 group-hover:scale-105 {filter.className}"
        />
        <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-3">
          <p class="text-sm font-medium text-white">{filter.name}</p>
        </div>
      </div>
    </div>
  {/each}
</div>
```

### Step 10: Gradient Color Interpolation（漸層色彩插值）

Tailwind CSS v4 支援現代 CSS 的色彩插值方法。

```html
<!-- 預設色彩插值（sRGB） -->
<div class="h-16 rounded-lg bg-gradient-to-r from-blue-500 to-red-500"></div>

<!-- oklch 色彩空間插值（更自然的過渡） -->
<div class="h-16 rounded-lg bg-linear-to-r/oklch from-blue-500 to-red-500"></div>

<!-- 在 oklch 中，漸層不會經過灰色調（muddy middle） -->
<!-- 這對於跨越色相環的漸層特別有用 -->

<!-- 比較：sRGB vs oklch -->
<div class="space-y-2">
  <div class="h-8 rounded bg-gradient-to-r from-blue-500 to-yellow-500"></div>
  <p class="text-xs text-gray-500">sRGB（中間會出現灰濁色）</p>
  <div class="h-8 rounded bg-linear-to-r/oklch from-blue-500 to-yellow-500"></div>
  <p class="text-xs text-gray-500">oklch（中間保持鮮豔）</p>
</div>
```

## Hands-on Lab

### Foundation 基礎練習

**任務：** 建立一個漸層按鈕集合和漸層文字效果。

需求：
- 4 種漸層按鈕（不同方向和顏色組合）
- 漸層文字標題（`bg-clip-text text-transparent`）
- 漸層邊框卡片
- 每個按鈕有 hover 效果（brightness 或 shadow 變化）

**驗收清單：**
- [ ] 四種按鈕各有不同方向的漸層
- [ ] 漸層文字清晰可見
- [ ] 漸層邊框效果正確（使用 padding + 內層背景技巧）
- [ ] hover 效果有 transition 過渡

### Advanced 進階練習

**任務：** 建立一個 Hero Section 加上圖片效果畫廊。

需求：
- Hero 區域：背景圖片 + 漸層覆蓋 + 放射漸層裝飾（v4）
- 毛玻璃按鈕（`backdrop-blur`）
- 圖片畫廊：每張圖片 hover 時從灰度變為彩色
- 至少一個 duotone 效果（`mix-blend-multiply`）
- 使用 `from-*` / `via-*` / `to-*` 控制色標位置

**驗收清單：**
- [ ] Hero 區域漸層覆蓋正確
- [ ] 放射漸層裝飾在背景可見
- [ ] 毛玻璃按鈕效果正常
- [ ] 圖片 hover 時 grayscale 到彩色的過渡流暢
- [ ] Duotone 混合效果正確
- [ ] 色標位置控制精確

### Challenge 挑戰練習

**任務：** 建立一個視覺效果展示頁面，包含 v4 新功能。

需求：
- 線性、放射、錐形三種漸層的對比展示
- 錐形漸層進度環元件（可傳入百分比）
- 完整的 filter 調整面板（亮度、對比、飽和度、模糊滑桿）
- Glassmorphism 卡片設計
- oklch vs sRGB 色彩插值對比
- 提供 React 和純 HTML 版本

**驗收清單：**
- [ ] 三種漸層類型各有展示
- [ ] 錐形漸層進度環可動態調整
- [ ] Filter 面板的滑桿即時預覽效果
- [ ] Glassmorphism 卡片毛玻璃效果正確
- [ ] oklch 與 sRGB 對比清晰
- [ ] React 和 HTML 版本功能一致

## Reference Solution

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ch14 Lab - Gradients, Filters and Blend Modes</title>
  <link rel="stylesheet" href="/src/output.css" />
</head>
<body class="min-h-screen bg-gray-950 text-white">

  <!-- ====== Hero Section ====== -->
  <section class="relative overflow-hidden">
    <img src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920"
         alt="Hero background"
         class="absolute inset-0 h-full w-full object-cover" />

    <!-- Gradient overlay -->
    <div class="absolute inset-0 bg-gradient-to-r from-gray-900/95 via-gray-900/70 to-gray-900/30"></div>

    <!-- Radial glow (v4) -->
    <div class="absolute -right-20 top-1/2 h-96 w-96 -translate-y-1/2 bg-radial from-blue-500/30 to-transparent"></div>

    <div class="relative mx-auto max-w-7xl px-6 py-32">
      <h1 class="text-5xl font-extrabold tracking-tight lg:text-7xl">
        Visual Effects
        <span class="block bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          in Tailwind v4
        </span>
      </h1>
      <p class="mt-6 max-w-lg text-lg text-gray-300">
        探索線性、放射與錐形漸層、濾鏡效果和混合模式。
      </p>
      <div class="mt-10 flex gap-4">
        <button class="rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-3 font-medium
                       shadow-lg shadow-blue-500/25
                       transition-all duration-300
                       hover:shadow-xl hover:shadow-blue-500/40 hover:brightness-110">
          Explore
        </button>
        <button class="rounded-xl border border-white/20 bg-white/10 px-8 py-3 font-medium
                       backdrop-blur-md
                       transition-all duration-300
                       hover:bg-white/20">
          Learn More
        </button>
      </div>
    </div>
  </section>

  <div class="mx-auto max-w-6xl px-6 py-20 space-y-24">

    <!-- ====== Gradient Buttons ====== -->
    <section>
      <h2 class="mb-8 text-2xl font-bold">Gradient Buttons</h2>
      <div class="flex flex-wrap gap-4">
        <button class="rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 px-6 py-3 font-medium
                       transition-all hover:brightness-110 hover:shadow-lg hover:shadow-blue-500/30">
          Blue to Cyan
        </button>
        <button class="rounded-lg bg-gradient-to-r from-purple-600 to-pink-500 px-6 py-3 font-medium
                       transition-all hover:brightness-110 hover:shadow-lg hover:shadow-purple-500/30">
          Purple to Pink
        </button>
        <button class="rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 px-6 py-3 font-medium
                       transition-all hover:brightness-110 hover:shadow-lg hover:shadow-amber-500/30">
          Amber to Orange
        </button>
        <button class="rounded-lg bg-gradient-to-r from-emerald-500 to-teal-600 px-6 py-3 font-medium
                       transition-all hover:brightness-110 hover:shadow-lg hover:shadow-emerald-500/30">
          Emerald to Teal
        </button>
      </div>
    </section>

    <!-- ====== Gradient Text ====== -->
    <section>
      <h2 class="mb-8 text-2xl font-bold">Gradient Text</h2>
      <h3 class="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-6xl font-extrabold text-transparent">
        Stunning Typography
      </h3>
    </section>

    <!-- ====== Gradient Types Comparison ====== -->
    <section>
      <h2 class="mb-8 text-2xl font-bold">Gradient Types (v4)</h2>
      <div class="grid gap-6 md:grid-cols-3">
        <div>
          <div class="h-48 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600"></div>
          <p class="mt-2 text-sm text-gray-400">Linear (bg-gradient-to-br)</p>
        </div>
        <div>
          <div class="h-48 rounded-xl bg-radial from-blue-400 to-purple-800"></div>
          <p class="mt-2 text-sm text-gray-400">Radial (bg-radial) - v4 new</p>
        </div>
        <div>
          <div class="mx-auto h-48 w-48 rounded-full bg-conic from-blue-500 via-purple-500 to-blue-500"></div>
          <p class="mt-2 text-sm text-gray-400">Conic (bg-conic) - v4 new</p>
        </div>
      </div>
    </section>

    <!-- ====== Conic Gradient Progress Ring ====== -->
    <section>
      <h2 class="mb-8 text-2xl font-bold">Progress Ring (Conic Gradient)</h2>
      <div class="flex gap-8">
        <div class="relative h-32 w-32">
          <div class="h-full w-full rounded-full bg-conic from-blue-500 from-[25%] to-gray-700 to-[25%]"></div>
          <div class="absolute inset-2 flex items-center justify-center rounded-full bg-gray-950">
            <span class="text-2xl font-bold">25%</span>
          </div>
        </div>
        <div class="relative h-32 w-32">
          <div class="h-full w-full rounded-full bg-conic from-emerald-500 from-[50%] to-gray-700 to-[50%]"></div>
          <div class="absolute inset-2 flex items-center justify-center rounded-full bg-gray-950">
            <span class="text-2xl font-bold">50%</span>
          </div>
        </div>
        <div class="relative h-32 w-32">
          <div class="h-full w-full rounded-full bg-conic from-purple-500 from-[75%] to-gray-700 to-[75%]"></div>
          <div class="absolute inset-2 flex items-center justify-center rounded-full bg-gray-950">
            <span class="text-2xl font-bold">75%</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ====== Filter Gallery ====== -->
    <section>
      <h2 class="mb-8 text-2xl font-bold">Filter Effects</h2>
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        <div class="overflow-hidden rounded-xl">
          <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400" alt="" class="aspect-square w-full object-cover" />
          <p class="mt-2 text-center text-xs text-gray-400">Original</p>
        </div>
        <div class="overflow-hidden rounded-xl">
          <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400" alt="" class="aspect-square w-full object-cover grayscale transition-[filter] duration-500 hover:grayscale-0" />
          <p class="mt-2 text-center text-xs text-gray-400">Grayscale (hover to color)</p>
        </div>
        <div class="overflow-hidden rounded-xl">
          <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400" alt="" class="aspect-square w-full object-cover sepia" />
          <p class="mt-2 text-center text-xs text-gray-400">Sepia</p>
        </div>
        <div class="overflow-hidden rounded-xl">
          <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400" alt="" class="aspect-square w-full object-cover brightness-125 contrast-110 saturate-150" />
          <p class="mt-2 text-center text-xs text-gray-400">Vivid</p>
        </div>
      </div>
    </section>

    <!-- ====== Duotone Effect ====== -->
    <section>
      <h2 class="mb-8 text-2xl font-bold">Duotone (mix-blend-multiply)</h2>
      <div class="relative h-64 overflow-hidden rounded-2xl">
        <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200" alt=""
             class="h-full w-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 mix-blend-multiply"></div>
        <div class="absolute inset-0 flex items-center justify-center">
          <h3 class="text-4xl font-bold text-white drop-shadow-lg">Duotone Hero</h3>
        </div>
      </div>
    </section>

    <!-- ====== Glassmorphism Cards ====== -->
    <section>
      <h2 class="mb-8 text-2xl font-bold">Glassmorphism</h2>
      <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-purple-600 to-blue-600 p-12">
        <!-- Decorative circles -->
        <div class="absolute -left-10 -top-10 h-40 w-40 rounded-full bg-pink-500/40"></div>
        <div class="absolute -bottom-10 -right-10 h-52 w-52 rounded-full bg-blue-400/40"></div>

        <div class="relative grid gap-6 md:grid-cols-2">
          <div class="rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur-lg">
            <h3 class="text-lg font-semibold">Glass Card 1</h3>
            <p class="mt-2 text-sm text-white/70">
              使用 backdrop-blur-lg 和半透明背景實現毛玻璃效果。
            </p>
          </div>
          <div class="rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur-lg">
            <h3 class="text-lg font-semibold">Glass Card 2</h3>
            <p class="mt-2 text-sm text-white/70">
              搭配 border-white/20 增加邊緣的層次感。
            </p>
          </div>
        </div>
      </div>
    </section>

  </div>

</body>
</html>
```

## Common Pitfalls

1. **漸層方向與 from/to 搞混：** `bg-gradient-to-r` 表示漸層方向是「向右」，`from-*` 是起始色（左側），`to-*` 是結束色（右側）。常見錯誤是把 `from-*` 當成結束色。

2. **Backdrop-filter 不透明背景無效：** `backdrop-blur-*` 只有在元素背景是半透明時才有效。如果使用 `bg-white`（完全不透明），背景濾鏡不會產生任何效果。**解法：** 使用 `bg-white/80` 或 `bg-white/70` 等半透明背景。

3. **Filter 效能問題：** 大面積的 `blur-*` 或 `backdrop-blur-*` 會消耗 GPU 資源，在低端裝置上可能造成卡頓。**解法：** 限制模糊元素的尺寸，或使用 `will-change-[filter]` 提示瀏覽器優化。在行動裝置上考慮降低模糊程度或使用靜態背景替代。

4. **v4 特定 --- bg-radial 和 bg-conic 語法：** Tailwind CSS v4 的放射和錐形漸層是全新的工具類別。常見錯誤是嘗試使用 v3 的 `bg-[radial-gradient(...)]` 任意值語法，而不是 v4 原生的 `bg-radial`。另外，放射漸層的位置控制使用 `bg-radial-[at_top_left]` 格式（下劃線代替空格）。

5. **Drop-shadow vs Box-shadow 混淆：** `drop-shadow-*`（CSS `filter: drop-shadow()`）會追蹤元素的實際形狀（包括透明區域），而 `shadow-*`（CSS `box-shadow`）永遠是矩形。對於有透明背景的 PNG 圖片或使用 `clip-path` 的元素，應該使用 `drop-shadow-*`。

## Checklist

- [ ] 能使用 `bg-gradient-to-*` + `from-*` / `via-*` / `to-*` 建立線性漸層。
- [ ] 能使用 `bg-radial` 建立放射漸層（v4 新功能）。
- [ ] 能使用 `bg-conic` 建立錐形漸層（v4 新功能）。
- [ ] 能使用 `bg-clip-text text-transparent` 建立漸層文字。
- [ ] 能使用 `blur-*`、`brightness-*`、`grayscale` 等濾鏡處理圖片。
- [ ] 能使用 `backdrop-blur-*` 建立毛玻璃（Glassmorphism）效果。
- [ ] 能使用 `mix-blend-*` 建立 duotone 或紋理疊加效果。
- [ ] 理解 `drop-shadow-*` 和 `shadow-*` 的差異。

## Further Reading (official links only)

- [Background Gradients - Tailwind CSS](https://tailwindcss.com/docs/background-image)
- [Gradient Color Stops - Tailwind CSS](https://tailwindcss.com/docs/gradient-color-stops)
- [Blur - Tailwind CSS](https://tailwindcss.com/docs/blur)
- [Brightness - Tailwind CSS](https://tailwindcss.com/docs/brightness)
- [Backdrop Blur - Tailwind CSS](https://tailwindcss.com/docs/backdrop-blur)
- [Mix Blend Mode - Tailwind CSS](https://tailwindcss.com/docs/mix-blend-mode)
- [Tailwind CSS v4.0 - tailwindcss.com](https://tailwindcss.com/blog/tailwindcss-v4)
