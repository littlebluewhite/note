---
title: "Container Queries and Modern Layout Patterns / 容器查詢與現代排版模式"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "15"
level: intermediate
stack: Tailwind CSS 4.1.x
prerequisites: [14_gradients_filters_and_blend_modes]
---

# Container Queries and Modern Layout Patterns / 容器查詢與現代排版模式

## Goal

在前一章 [[14_gradients_filters_and_blend_modes]] 中，我們學會了漸層、濾鏡和混合模式等視覺效果。但你可能已經發現一個問題：當一個元件被放在不同寬度的容器中時（例如同一張卡片放在主內容區 vs 窄側邊欄），使用 media query 的響應式設計無法讓元件根據**自身容器**的寬度來調整佈局。這正是 Container Queries 要解決的問題。

Container Queries 是 CSS 多年來最重要的佈局革新之一，而 **Tailwind CSS v4 內建了完整的 Container Query 支援，不需要任何額外 plugin**。這是 v4 相對於 v3 的一個重大升級（v3 需要 `@tailwindcss/container-queries` plugin）。透過在父元素加上 `@container`，子元素就可以使用 `@sm:`、`@md:`、`@lg:` 等容器查詢變體來根據容器寬度調整樣式。本章將深入探討 Container Queries 的完整用法，並對比 media queries 來建立最佳實踐。搭配前幾章學到的佈局、狀態和動畫技巧，你將能夠建立真正可重用、自適應的 UI 元件。下一章 [[16_theme_directive_and_design_tokens]] 將帶你深入 `@theme` 指令，打造完整的設計令牌系統。

## Prerequisites

- 已完成 [[14_gradients_filters_and_blend_modes]]。
- 理解 CSS media queries 和響應式設計（Ch10）。
- 熟悉 Flexbox 和 Grid 佈局。
- 理解 CSS `container-type` 和 `@container` 的基本概念（可從本章學習）。

## Core Concepts

### 1. Container Queries vs Media Queries / 容器查詢 vs 媒體查詢

| 特性 | Media Query (`md:`) | Container Query (`@md:`) |
|------|---------------------|--------------------------|
| 參照對象 | 瀏覽器視窗（viewport）寬度 | 父容器寬度 |
| 適用場景 | 頁面級佈局（導覽列、欄數） | 元件級自適應（卡片、Widget） |
| 可重用性 | 低（同一元件在不同容器表現一致） | 高（同一元件根據容器自動調整） |
| 何時使用 | 整體頁面結構變化 | 元件放在不同寬度的容器中需要不同佈局 |
| 何時不使用 | 需要元件自適應容器寬度時 | 只需根據視窗寬度調整時 |

### 2. Container Query Variants / 容器查詢變體

Tailwind CSS v4 提供的容器查詢斷點：

| 變體 | 最小容器寬度 | 何時使用 | 何時不使用 |
|------|------------|----------|------------|
| `@xs:` | 320px（20rem） | 極窄容器的微調 | 容器通常大於此寬度時 |
| `@sm:` | 384px（24rem） | 小型 widget、窄側邊欄 | 容器通常寬於 sm 時 |
| `@md:` | 448px（28rem） | 中等容器（如 2/3 寬的主內容） | 不需要在此寬度變化時 |
| `@lg:` | 512px（32rem） | 較寬容器的完整佈局 | 容器很少達到此寬度時 |
| `@xl:` | 576px（36rem） | 寬容器的多欄佈局 | 極少使用到此寬度時 |
| `@2xl:` ~ `@7xl:` | 672px ~ 1280px | 超寬容器 | 大多數場景不需要 |
| `@[500px]:` | 任意值 500px | 非標準斷點的精確控制 | 標準斷點已足夠時 |

### 3. Named Containers / 命名容器

| 功能 | 語法 | 何時使用 | 何時不使用 |
|------|------|----------|------------|
| 匿名容器 | `@container` | 查詢直接父容器 | 需要查詢非直接父元素的容器時 |
| 命名容器 | `@container/sidebar` | 多層巢狀容器需要指定查詢對象 | 只有單一容器層級時 |
| 查詢命名容器 | `@lg/sidebar:flex-row` | 根據特定命名容器的寬度調整 | 沒有多層容器的場景 |

### 4. Container vs Responsive Patterns / 使用模式比較

| 模式 | 實作方式 | 何時使用 | 何時不使用 |
|------|---------|----------|------------|
| 頁面佈局 | `md:grid-cols-2 lg:grid-cols-3` | 頁面欄數、導覽列結構 | 元件需要在不同容器中自適應 |
| 元件自適應 | `@container` + `@md:grid-cols-2` | 可重用卡片、Widget | 元件只出現在固定寬度位置 |
| 混合使用 | Media + Container | 頁面用 media 佈局，元件用 container 自適應 | 增加過多複雜度時 |

## Step-by-step

### Step 1: 設定 Container Query 上下文

在父元素加上 `@container` 即可建立容器查詢上下文。

```html
<!-- 設定容器查詢上下文 -->
<div class="@container">
  <!-- 子元素可以使用 @sm:, @md:, @lg: 等變體 -->
  <div class="flex flex-col @md:flex-row @md:items-center gap-4">
    <img src="/avatar.jpg" alt="" class="h-16 w-16 rounded-full @md:h-20 @md:w-20" />
    <div>
      <h3 class="text-lg font-semibold @md:text-xl">User Name</h3>
      <p class="text-sm text-gray-500">user@example.com</p>
    </div>
  </div>
</div>
```

**關鍵觀念：** `@container` 在 CSS 底層會設定 `container-type: inline-size`，讓瀏覽器追蹤該元素的寬度變化。

### Step 2: 自適應卡片元件

同一個卡片元件，放在不同寬度的容器中會自動調整佈局。

```html
<!-- 卡片元件（可重用） -->
<article class="@container">
  <div class="flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white
              @sm:flex-row">
    <!-- 圖片：窄容器全寬、寬容器固定寬度 -->
    <img src="/card-image.jpg" alt=""
         class="h-48 w-full object-cover @sm:h-auto @sm:w-48 @md:w-64" />

    <div class="flex flex-1 flex-col p-4 @sm:p-6">
      <h3 class="text-lg font-semibold @md:text-xl">Card Title</h3>
      <p class="mt-2 text-sm text-gray-600 @md:text-base">
        This card adapts its layout based on the container width,
        not the viewport width.
      </p>
      <div class="mt-4 flex items-center gap-2">
        <span class="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
          Tag
        </span>
        <span class="text-xs text-gray-400">3 min read</span>
      </div>
    </div>
  </div>
</article>
```

```html
<!-- 展示同一卡片在不同寬度容器中的效果 -->
<div class="space-y-8">
  <!-- 窄容器（如側邊欄） -->
  <div class="mx-auto w-72 rounded-lg border-2 border-dashed border-gray-300 p-4">
    <p class="mb-2 text-xs text-gray-400">Container: 288px (w-72)</p>
    <!-- 這裡放上面的卡片元件 -->
  </div>

  <!-- 中等容器 -->
  <div class="mx-auto w-[500px] rounded-lg border-2 border-dashed border-gray-300 p-4">
    <p class="mb-2 text-xs text-gray-400">Container: 500px</p>
    <!-- 同一個卡片元件，自動切換為水平佈局 -->
  </div>

  <!-- 寬容器（如主內容區域） -->
  <div class="mx-auto w-[700px] rounded-lg border-2 border-dashed border-gray-300 p-4">
    <p class="mb-2 text-xs text-gray-400">Container: 700px</p>
    <!-- 同一個卡片元件，更寬的圖片和文字 -->
  </div>
</div>
```

### Step 3: @min-* 和 @max-* 容器變體

類似 media query 的 `min-*` 和 `max-*`，容器查詢也支援範圍變體。

```html
<div class="@container">
  <!-- 只在容器寬度小於 sm 時顯示 -->
  <p class="@max-sm:block @sm:hidden text-sm text-gray-500">
    Compact view
  </p>

  <!-- 只在容器寬度 sm 到 md 之間 -->
  <div class="hidden @sm:@max-md:block">
    Medium container content
  </div>

  <!-- 任意值範圍 -->
  <div class="@min-[400px]:grid-cols-2 @min-[600px]:grid-cols-3">
    Precise breakpoints
  </div>
</div>
```

### Step 4: Named Containers 命名容器

當有巢狀容器時，使用命名容器指定要查詢哪一層。

```html
<!-- 外層命名容器 -->
<div class="@container/main">
  <div class="flex flex-col @lg/main:flex-row gap-8">

    <!-- 主內容區域（也是一個容器） -->
    <main class="@container/content flex-1">
      <h1 class="text-xl @lg/content:text-3xl font-bold">
        Article Title
      </h1>
      <p class="mt-4 text-gray-600">
        Content that responds to the content area width...
      </p>

      <!-- 內嵌卡片查詢自己的容器（content） -->
      <div class="mt-8 grid grid-cols-1 @md/content:grid-cols-2 gap-4">
        <div class="rounded-lg bg-gray-50 p-4">Card A</div>
        <div class="rounded-lg bg-gray-50 p-4">Card B</div>
      </div>
    </main>

    <!-- 側邊欄（也是一個容器） -->
    <aside class="@container/sidebar w-full @lg/main:w-80">
      <!-- 查詢 sidebar 容器的寬度 -->
      <div class="rounded-lg border p-4">
        <h2 class="text-lg font-semibold @sm/sidebar:text-xl">Sidebar</h2>
        <nav class="mt-4 space-y-2">
          <a href="#" class="block text-sm text-gray-600 hover:text-blue-600">Link 1</a>
          <a href="#" class="block text-sm text-gray-600 hover:text-blue-600">Link 2</a>
        </nav>
      </div>
    </aside>
  </div>
</div>
```

### Step 5: 任意容器查詢值

使用 `@[value]:` 語法設定精確的容器查詢斷點。

```html
<div class="@container">
  <div class="grid grid-cols-1
              @[350px]:grid-cols-2
              @[500px]:grid-cols-3
              @[700px]:grid-cols-4
              gap-4">
    <div class="rounded-lg bg-blue-100 p-4 text-center text-sm">1</div>
    <div class="rounded-lg bg-blue-100 p-4 text-center text-sm">2</div>
    <div class="rounded-lg bg-blue-100 p-4 text-center text-sm">3</div>
    <div class="rounded-lg bg-blue-100 p-4 text-center text-sm">4</div>
  </div>
</div>
```

### Step 6: Container Query 在 React 中的使用

```tsx
// AdaptiveCard.tsx - 可重用的自適應卡片元件
interface AdaptiveCardProps {
  image: string;
  title: string;
  description: string;
  tags: string[];
}

export function AdaptiveCard({ image, title, description, tags }: AdaptiveCardProps) {
  return (
    <article className="@container">
      <div className="flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white
                      shadow-sm transition-shadow hover:shadow-md
                      @sm:flex-row">
        <img
          src={image}
          alt={title}
          className="h-48 w-full object-cover
                     @sm:h-auto @sm:w-40
                     @md:w-56
                     @lg:w-72"
        />
        <div className="flex flex-1 flex-col p-4 @sm:p-5 @md:p-6">
          <h3 className="text-lg font-semibold text-gray-900
                         @md:text-xl @lg:text-2xl">
            {title}
          </h3>
          <p className="mt-2 line-clamp-2 text-sm text-gray-600
                        @md:line-clamp-3 @md:text-base">
            {description}
          </p>
          <div className="mt-auto flex flex-wrap gap-2 pt-4">
            {tags.map(tag => (
              <span
                key={tag}
                className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </article>
  );
}

// 使用：放在任何寬度的容器中，自動適應
export function PageLayout() {
  const card = {
    image: '/card.jpg',
    title: 'Adaptive Card',
    description: 'This card adapts to its container width automatically.',
    tags: ['Tailwind', 'v4', 'Container Queries'],
  };

  return (
    <div className="flex gap-8">
      {/* 主內容區域 - 卡片會較寬 */}
      <main className="flex-1">
        <AdaptiveCard {...card} />
      </main>

      {/* 側邊欄 - 同一個卡片會自動變窄 */}
      <aside className="w-72">
        <AdaptiveCard {...card} />
      </aside>
    </div>
  );
}
```

### Step 7: Svelte 中的 Container Query 元件

```svelte
<!-- AdaptiveCard.svelte -->
<script>
  export let image;
  export let title;
  export let description;
  export let tags = [];
</script>

<article class="@container">
  <div class="flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white
              shadow-sm transition-shadow hover:shadow-md
              @sm:flex-row">
    <img
      src={image}
      alt={title}
      class="h-48 w-full object-cover @sm:h-auto @sm:w-40 @md:w-56"
    />
    <div class="flex flex-1 flex-col p-4 @sm:p-5 @md:p-6">
      <h3 class="text-lg font-semibold text-gray-900 @md:text-xl">
        {title}
      </h3>
      <p class="mt-2 line-clamp-2 text-sm text-gray-600 @md:line-clamp-3 @md:text-base">
        {description}
      </p>
      <div class="mt-auto flex flex-wrap gap-2 pt-4">
        {#each tags as tag}
          <span class="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
            {tag}
          </span>
        {/each}
      </div>
    </div>
  </div>
</article>
```

### Step 8: Container Query + Media Query 混合策略

最佳實踐：頁面級佈局用 media query，元件級自適應用 container query。

```html
<!-- 頁面佈局用 media query -->
<div class="flex flex-col lg:flex-row gap-8">

  <!-- 主內容：media query 控制寬度 -->
  <main class="flex-1">
    <!-- 元件用 container query 自適應 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 每個格子是一個容器 -->
      <div class="@container">
        <article class="flex flex-col @sm:flex-row gap-4 rounded-xl border p-4">
          <img src="/img1.jpg" alt="" class="h-32 w-full rounded-lg object-cover @sm:h-auto @sm:w-32" />
          <div>
            <h3 class="font-semibold @sm:text-lg">Title</h3>
            <p class="mt-1 text-sm text-gray-500">Description</p>
          </div>
        </article>
      </div>
    </div>
  </main>

  <!-- 側邊欄：media query 控制顯示 -->
  <aside class="hidden w-72 lg:block">
    <!-- 側邊欄中的元件用 container query -->
    <div class="@container">
      <div class="flex flex-col gap-3 @xs:gap-4">
        <div class="rounded-lg bg-gray-50 p-3 @xs:p-4">Widget A</div>
        <div class="rounded-lg bg-gray-50 p-3 @xs:p-4">Widget B</div>
      </div>
    </div>
  </aside>
</div>
```

### Step 9: 實戰 --- Dashboard Widget 系統

```html
<!-- Dashboard Grid：每個 widget 是一個容器 -->
<div class="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">

  <!-- Stats Widget -->
  <div class="@container rounded-xl border border-gray-200 bg-white p-6">
    <div class="flex flex-col gap-4 @sm:flex-row @sm:items-center @sm:justify-between">
      <div>
        <p class="text-sm text-gray-500">Total Revenue</p>
        <p class="text-2xl font-bold @sm:text-3xl">$45,231</p>
      </div>
      <div class="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700
                  @sm:self-start">
        +12.5%
      </div>
    </div>
    <div class="mt-4 h-16 rounded bg-gray-100 @md:h-24">
      <!-- Chart placeholder -->
    </div>
  </div>

  <!-- User List Widget -->
  <div class="@container rounded-xl border border-gray-200 bg-white p-6">
    <h3 class="text-lg font-semibold">Recent Users</h3>
    <ul class="mt-4 space-y-3">
      <li class="flex items-center gap-3">
        <div class="h-8 w-8 rounded-full bg-blue-100 @sm:h-10 @sm:w-10"></div>
        <div class="flex-1">
          <p class="text-sm font-medium">Alice</p>
          <p class="hidden text-xs text-gray-500 @sm:block">alice@example.com</p>
        </div>
        <span class="hidden rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700 @md:inline">
          Active
        </span>
      </li>
      <li class="flex items-center gap-3">
        <div class="h-8 w-8 rounded-full bg-purple-100 @sm:h-10 @sm:w-10"></div>
        <div class="flex-1">
          <p class="text-sm font-medium">Bob</p>
          <p class="hidden text-xs text-gray-500 @sm:block">bob@example.com</p>
        </div>
        <span class="hidden rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700 @md:inline">
          Away
        </span>
      </li>
    </ul>
  </div>

  <!-- Activity Feed Widget -->
  <div class="@container rounded-xl border border-gray-200 bg-white p-6 md:col-span-2 xl:col-span-1">
    <h3 class="text-lg font-semibold">Activity Feed</h3>
    <div class="mt-4 space-y-4">
      <div class="flex gap-3">
        <div class="mt-1 h-2 w-2 shrink-0 rounded-full bg-blue-500"></div>
        <div>
          <p class="text-sm">New user registered</p>
          <p class="text-xs text-gray-400">2 minutes ago</p>
        </div>
      </div>
      <div class="flex gap-3">
        <div class="mt-1 h-2 w-2 shrink-0 rounded-full bg-green-500"></div>
        <div>
          <p class="text-sm">Payment processed</p>
          <p class="text-xs text-gray-400">15 minutes ago</p>
        </div>
      </div>
    </div>
  </div>
</div>
```

### Step 10: v3 vs v4 Container Query 對比

```js
// v3: 需要安裝 plugin
// npm install @tailwindcss/container-queries

// tailwind.config.js
module.exports = {
  plugins: [
    require('@tailwindcss/container-queries'),
  ],
};
```

```html
<!-- v3 語法（需要 plugin） -->
<div class="@container">
  <div class="@lg:flex-row flex flex-col">...</div>
</div>
```

```css
/* v4: 內建支援，不需要任何 plugin */
@import "tailwindcss";
/* 直接使用，無需額外設定 */
```

```html
<!-- v4 語法（完全相同，但不需要 plugin） -->
<div class="@container">
  <div class="flex flex-col @lg:flex-row">...</div>
</div>

<!-- v4 新增功能：命名容器 -->
<div class="@container/sidebar">
  <div class="@sm/sidebar:flex-row">...</div>
</div>
```

## Hands-on Lab

### Foundation 基礎練習

**任務：** 建立一個自適應卡片元件。

需求：
- 使用 `@container` 建立容器查詢上下文
- 窄容器（< 384px）：垂直堆疊佈局（圖片在上、文字在下）
- 寬容器（>= 384px）：水平並排佈局（圖片在左、文字在右）
- 圖片在窄容器全寬，在寬容器固定寬度
- 文字大小根據容器寬度調整

**驗收清單：**
- [ ] 卡片在 300px 寬容器中垂直堆疊
- [ ] 卡片在 500px 寬容器中水平排列
- [ ] 圖片大小正確響應
- [ ] 無需 JavaScript，純 CSS 實現

### Advanced 進階練習

**任務：** 建立一個 Dashboard Widget 系統。

需求：
- 3 個不同類型的 Widget（統計、列表、圖表佔位）
- 每個 Widget 都是一個 `@container`
- Widget 在窄容器中精簡顯示，在寬容器中完整顯示
- 使用命名容器區分不同層級
- 結合 media query（頁面欄數）和 container query（Widget 內部）

**驗收清單：**
- [ ] 三個 Widget 各自根據容器寬度調整內部佈局
- [ ] 命名容器正確隔離不同查詢上下文
- [ ] Media query 控制頁面級佈局（1/2/3 欄）
- [ ] Container query 控制 Widget 內部佈局
- [ ] 拖動瀏覽器寬度時兩層響應獨立運作

### Challenge 挑戰練習

**任務：** 建立一個完全可重用的元件庫展示頁面。

需求：
- 至少 4 種自適應元件（卡片、統計數字、使用者列表、活動 Feed）
- 每個元件展示在 3 種不同寬度的容器中
- 使用 React 或 Svelte 實作可重用元件
- 每個元件的 props 介面清晰且有 TypeScript 型別
- 使用 `@[value]:` 任意值處理至少一個精確斷點

**驗收清單：**
- [ ] 四種元件各自在不同容器寬度正確自適應
- [ ] 展示頁面清楚對比三種容器寬度的效果
- [ ] React/Svelte 元件可重用且 props 完整
- [ ] TypeScript 型別正確定義
- [ ] 使用了任意值容器斷點
- [ ] 所有元件同時支援深色模式（`dark:` 變體）

## Reference Solution

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ch15 Lab - Container Queries Demo</title>
  <link rel="stylesheet" href="/src/output.css" />
</head>
<body class="min-h-screen bg-gray-100 p-8 text-gray-900">

  <div class="mx-auto max-w-6xl space-y-12">
    <h1 class="text-3xl font-bold">Container Queries Demo</h1>
    <p class="text-gray-600">
      同一個卡片元件放在不同寬度的容器中，自動調整佈局。
    </p>

    <!-- ====== Adaptive Card in Different Containers ====== -->
    <section class="space-y-8">
      <h2 class="text-xl font-semibold">Adaptive Card Component</h2>

      <!-- Narrow container (sidebar-like) -->
      <div>
        <p class="mb-2 text-sm font-medium text-gray-400">Container: 280px (narrow sidebar)</p>
        <div class="w-70 rounded-lg border-2 border-dashed border-gray-300 p-4">
          <div class="@container">
            <div class="flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white @sm:flex-row">
              <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400"
                   alt="" class="h-40 w-full object-cover @sm:h-auto @sm:w-40" />
              <div class="p-4 @sm:p-5">
                <h3 class="font-semibold @md:text-lg">Mountain Vista</h3>
                <p class="mt-1 text-sm text-gray-500">A breathtaking view of the valley below.</p>
                <span class="mt-3 inline-block rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">Nature</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Medium container -->
      <div>
        <p class="mb-2 text-sm font-medium text-gray-400">Container: 500px (medium panel)</p>
        <div class="w-[500px] rounded-lg border-2 border-dashed border-gray-300 p-4">
          <div class="@container">
            <div class="flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white @sm:flex-row">
              <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400"
                   alt="" class="h-40 w-full object-cover @sm:h-auto @sm:w-40 @md:w-56" />
              <div class="p-4 @sm:p-5 @md:p-6">
                <h3 class="font-semibold @md:text-lg @lg:text-xl">Mountain Vista</h3>
                <p class="mt-1 text-sm text-gray-500 @md:text-base">A breathtaking view of the valley below. The mountains stretch endlessly.</p>
                <span class="mt-3 inline-block rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">Nature</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Wide container -->
      <div>
        <p class="mb-2 text-sm font-medium text-gray-400">Container: 100% (full width)</p>
        <div class="rounded-lg border-2 border-dashed border-gray-300 p-4">
          <div class="@container">
            <div class="flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white @sm:flex-row">
              <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400"
                   alt="" class="h-40 w-full object-cover @sm:h-auto @sm:w-40 @md:w-56 @lg:w-72" />
              <div class="p-4 @sm:p-5 @md:p-6">
                <h3 class="font-semibold @md:text-lg @lg:text-xl @xl:text-2xl">Mountain Vista</h3>
                <p class="mt-1 text-sm text-gray-500 @md:text-base">A breathtaking view of the valley below. The mountains stretch endlessly across the horizon, inviting exploration and wonder.</p>
                <div class="mt-3 flex gap-2">
                  <span class="rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">Nature</span>
                  <span class="hidden rounded-full bg-green-50 px-2 py-0.5 text-xs text-green-700 @md:inline">Photography</span>
                  <span class="hidden rounded-full bg-purple-50 px-2 py-0.5 text-xs text-purple-700 @lg:inline">Landscape</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ====== Dashboard Widgets ====== -->
    <section>
      <h2 class="mb-6 text-xl font-semibold">Dashboard Widgets (Container + Media)</h2>

      <div class="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">

        <!-- Stats Widget -->
        <div class="@container rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-4 @xs:flex-row @xs:items-center @xs:justify-between">
            <div>
              <p class="text-sm text-gray-500">Total Revenue</p>
              <p class="text-2xl font-bold text-gray-900 @sm:text-3xl">$45,231</p>
            </div>
            <span class="self-start rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
              +12.5%
            </span>
          </div>
          <div class="mt-4 h-16 rounded-lg bg-gradient-to-r from-blue-50 to-blue-100 @md:h-24">
            <!-- Chart placeholder -->
          </div>
        </div>

        <!-- User List Widget -->
        <div class="@container rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h3 class="text-lg font-semibold text-gray-900">Recent Users</h3>
          <ul class="mt-4 space-y-3">
            <li class="flex items-center gap-3">
              <div class="h-8 w-8 rounded-full bg-blue-200 @sm:h-10 @sm:w-10"></div>
              <div class="flex-1 min-w-0">
                <p class="truncate text-sm font-medium text-gray-900">Alice Chen</p>
                <p class="hidden truncate text-xs text-gray-500 @xs:block">alice@example.com</p>
              </div>
              <span class="hidden rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700 @sm:inline">
                Active
              </span>
            </li>
            <li class="flex items-center gap-3">
              <div class="h-8 w-8 rounded-full bg-purple-200 @sm:h-10 @sm:w-10"></div>
              <div class="flex-1 min-w-0">
                <p class="truncate text-sm font-medium text-gray-900">Bob Wang</p>
                <p class="hidden truncate text-xs text-gray-500 @xs:block">bob@example.com</p>
              </div>
              <span class="hidden rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700 @sm:inline">
                Away
              </span>
            </li>
          </ul>
        </div>

        <!-- Activity Widget -->
        <div class="@container rounded-xl border border-gray-200 bg-white p-6 shadow-sm md:col-span-2 xl:col-span-1">
          <h3 class="text-lg font-semibold text-gray-900">Activity</h3>
          <div class="mt-4 space-y-3">
            <div class="flex gap-3">
              <div class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-blue-500"></div>
              <div>
                <p class="text-sm text-gray-700">New user registered</p>
                <p class="text-xs text-gray-400">2 minutes ago</p>
              </div>
            </div>
            <div class="flex gap-3">
              <div class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-green-500"></div>
              <div>
                <p class="text-sm text-gray-700">Payment received</p>
                <p class="text-xs text-gray-400">15 minutes ago</p>
              </div>
            </div>
            <div class="flex gap-3">
              <div class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-orange-500"></div>
              <div>
                <p class="text-sm text-gray-700">Server warning resolved</p>
                <p class="text-xs text-gray-400">1 hour ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

  </div>

</body>
</html>
```

## Common Pitfalls

1. **忘記在父元素加 `@container`：** Container query 變體（`@md:` 等）必須要有一個帶有 `@container` 的祖先元素。如果忘了加，`@md:` 變體不會有任何效果（不會報錯，只是靜默忽略）。

2. **Container 與 Overflow 衝突：** `@container` 會在元素上設定 `container-type: inline-size`，這會建立新的 containing block，可能影響子元素的 `position: absolute` 定位參照。同時，它也暗含 `overflow: hidden` 的某些行為（實際上是 `contain: inline-size`）。

3. **混淆 `@md:` 和 `md:` 前綴：** `@md:` 是容器查詢（參照父容器寬度），`md:` 是媒體查詢（參照視窗寬度）。它們的語法非常相似但行為完全不同。**建議：** 在程式碼審查中特別注意 `@` 前綴，確保使用正確的查詢類型。

4. **v4 特定 --- 嘗試安裝已不需要的 plugin：** Tailwind CSS v4 原生內建 Container Queries，不需要安裝 `@tailwindcss/container-queries` plugin。如果同時安裝 plugin 和使用 v4 原生功能，可能產生衝突。**解法：** 升級到 v4 後移除 `@tailwindcss/container-queries` 依賴。

5. **Container 查詢斷點值與 Media 查詢斷點值不同：** Tailwind 的 `@sm:` 容器查詢斷點（384px）與 `sm:` 媒體查詢斷點（640px）數值不同。這是因為容器通常比視窗小，斷點值需要相應調整。不要假設 `@sm:` 等於 `sm:`。

## Checklist

- [ ] 能在父元素使用 `@container` 建立容器查詢上下文。
- [ ] 能使用 `@sm:`、`@md:`、`@lg:` 等變體根據容器寬度調整樣式。
- [ ] 理解 Container Query（`@md:`）與 Media Query（`md:`）的差異和各自適用場景。
- [ ] 能使用命名容器（`@container/name` + `@md/name:`）解決巢狀容器問題。
- [ ] 能使用 `@[value]:` 任意值設定精確的容器查詢斷點。
- [ ] 能設計可重用的自適應元件（卡片、Widget）並在不同寬度容器中正確顯示。
- [ ] 知道 v4 內建 Container Queries，不需要安裝額外 plugin。

## Further Reading (official links only)

- [Container Queries - Tailwind CSS](https://tailwindcss.com/docs/container-queries)
- [Responsive Design - Tailwind CSS](https://tailwindcss.com/docs/responsive-design)
- [Tailwind CSS v4.0 - tailwindcss.com](https://tailwindcss.com/blog/tailwindcss-v4)
- [GitHub - tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss)
