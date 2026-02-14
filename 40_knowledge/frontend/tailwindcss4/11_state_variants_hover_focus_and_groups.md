---
title: "State Variants: Hover, Focus, and Groups / 狀態變體：Hover、Focus 與群組"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "11"
level: intermediate
stack: Tailwind CSS 4.1.x
prerequisites: [10_responsive_design_and_breakpoints]
---

# State Variants: Hover, Focus, and Groups / 狀態變體：Hover、Focus 與群組

## Goal

在前一章 [[10_responsive_design_and_breakpoints]] 中，我們學會了根據螢幕尺寸改變樣式。然而，使用者與介面的互動不僅僅是「觀看」--- 他們會 hover 按鈕、focus 輸入欄位、click 連結、navigate 表單。本章將深入探討 Tailwind CSS v4 的狀態變體系統，讓你能夠為每一種使用者互動狀態設計精確的視覺回饋。

Tailwind CSS 的狀態變體是其最強大的特性之一。透過 `hover:`、`focus:`、`active:` 等前綴，你可以在 HTML 中直接宣告不同狀態的樣式，不需要撰寫額外的 CSS。更進階的 `group-*` 和 `peer-*` 修飾符讓你能夠根據父元素或兄弟元素的狀態來改變當前元素的樣式。此外，`before:` 和 `after:` 偽元素變體讓你能夠創建裝飾性元素。這些變體還可以互相堆疊（如 `sm:hover:bg-blue-500`），實現高度精確的條件式樣式。下一章 [[12_dark_mode_and_multi_theme_system]] 將會利用這些狀態變體來建構深色模式與多主題切換系統。

## Prerequisites

- 已完成 [[10_responsive_design_and_breakpoints]]。
- 理解 CSS pseudo-classes（`:hover`、`:focus` 等）的基本概念。
- 理解 CSS pseudo-elements（`::before`、`::after`）的基本概念。
- 知道 HTML 表單元素的基本屬性（`disabled`、`required` 等）。

## Core Concepts

### 1. Interactive State Variants / 互動狀態變體

| 變體 | CSS 對應 | 何時使用 | 何時不使用 |
|------|---------|----------|------------|
| `hover:` | `:hover` | 滑鼠懸停時的視覺回饋（顏色、陰影、大小變化） | 觸控裝置為主的介面（hover 不可靠） |
| `focus:` | `:focus` | 鍵盤聚焦時的輸入框、按鈕外框樣式 | 不需要鍵盤導航的裝飾性元素 |
| `focus-visible:` | `:focus-visible` | 只在鍵盤聚焦時顯示外框（滑鼠點擊不顯示） | 需要所有聚焦方式都顯示回饋時 |
| `focus-within:` | `:focus-within` | 子元素獲得焦點時改變父容器樣式 | 不需要父元素回饋時 |
| `active:` | `:active` | 按下按鈕瞬間的壓縮/變色效果 | 不需要點擊回饋的靜態元素 |
| `disabled:` | `:disabled` | 禁用狀態的視覺暗示（灰色、低透明度） | 非表單元素 |
| `visited:` | `:visited` | 已訪問連結的顏色區分 | 不需要區分已訪問/未訪問的導覽連結 |

### 2. Structural Variants / 結構變體

| 變體 | CSS 對應 | 何時使用 | 何時不使用 |
|------|---------|----------|------------|
| `first:` | `:first-child` | 列表第一項移除上邊框或上間距 | 只有一個子元素時（無意義） |
| `last:` | `:last-child` | 列表最後一項移除下邊框或下間距 | 動態列表且需要所有項目一致時 |
| `odd:` | `:nth-child(odd)` | 表格斑馬紋背景色 | 行數很少無需區分時 |
| `even:` | `:nth-child(even)` | 搭配 odd 實現交替樣式 | 不需要交替效果時 |
| `only:` | `:only-child` | 唯一子元素時的特殊樣式 | 很少使用 |
| `empty:` | `:empty` | 內容為空時顯示佔位樣式 | 元素一定有內容時 |

### 3. Group and Peer Modifiers / 群組與同儕修飾符

| 變體 | 說明 | 何時使用 | 何時不使用 |
|------|------|----------|------------|
| `group` + `group-hover:` | 父元素 hover 時改變子元素樣式 | 卡片 hover 時改變內部文字/圖示顏色 | 子元素需要獨立的 hover 行為時 |
| `group/{name}` + `group-hover/{name}:` | 命名群組，避免巢狀衝突 | 有多層巢狀群組時 | 只有單一群組層級時 |
| `peer` + `peer-checked:` | 兄弟元素狀態影響另一個兄弟 | 自訂 checkbox/radio 樣式、表單驗證訊息 | 元素不是 DOM 兄弟時（peer 必須在前） |
| `peer/{name}` | 命名同儕 | 多個 peer 需要獨立控制時 | 只有單一 peer 時 |

### 4. Pseudo-element Variants / 偽元素變體

| 變體 | CSS 對應 | 何時使用 | 何時不使用 |
|------|---------|----------|------------|
| `before:` | `::before` | 裝飾性元素（圖示、分隔線、標記符號） | 有語義內容時（應使用真實元素） |
| `after:` | `::after` | 裝飾性元素、清除浮動 | 需要互動的元素（偽元素無法被直接選取） |
| `placeholder:` | `::placeholder` | 自訂輸入框佔位文字的顏色與字型 | 不需要自訂佔位文字時 |
| `selection:` | `::selection` | 自訂使用者選取文字時的背景色與文字色 | 不需要品牌化選取效果時 |
| `marker:` | `::marker` | 自訂列表項目符號的顏色與大小 | 使用自訂圖示替代項目符號時 |
| `file:` | `::file-selector-button` | 自訂檔案上傳按鈕樣式 | 使用自訂上傳元件時 |

## Step-by-step

### Step 1: 基礎 Hover 與 Focus 效果

按鈕是最常見需要 hover 和 focus 效果的元素。

```html
<!-- 基礎按鈕 hover + focus + active 效果 -->
<button class="rounded-lg bg-blue-600 px-6 py-3 text-white
               hover:bg-blue-700
               focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
               active:bg-blue-800 active:scale-95
               transition-all duration-150">
  Click me
</button>

<!-- focus-visible：只在鍵盤聚焦時顯示 ring -->
<button class="rounded-lg bg-gray-900 px-6 py-3 text-white
               hover:bg-gray-800
               focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-500 focus-visible:ring-offset-2
               active:scale-95
               transition-all duration-150">
  Keyboard-only focus ring
</button>

<!-- disabled 狀態 -->
<button disabled class="rounded-lg bg-blue-600 px-6 py-3 text-white
                         disabled:cursor-not-allowed disabled:opacity-50
                         hover:bg-blue-700 disabled:hover:bg-blue-600">
  Disabled
</button>
```

### Step 2: 連結與表單輸入的狀態

```html
<!-- 連結：hover + visited -->
<a href="https://tailwindcss.com"
   class="text-blue-600 underline decoration-blue-300
          hover:text-blue-800 hover:decoration-blue-500
          visited:text-purple-600 visited:decoration-purple-300">
  Visit Tailwind CSS
</a>

<!-- 表單輸入：focus + placeholder + invalid -->
<div class="space-y-4">
  <input
    type="email"
    placeholder="your@email.com"
    required
    class="w-full rounded-lg border border-gray-300 px-4 py-3
           placeholder:text-gray-400
           focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200
           invalid:border-red-500 invalid:focus:ring-red-200"
  />

  <!-- focus-within：子元素聚焦時父容器高亮 -->
  <div class="rounded-lg border border-gray-300 p-4
              focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200">
    <label class="block text-sm font-medium text-gray-700">Search</label>
    <input
      type="text"
      class="mt-1 w-full border-none bg-transparent focus:outline-none"
      placeholder="Type to search..."
    />
  </div>
</div>
```

### Step 3: 結構變體（first / last / odd / even）

```html
<!-- 列表：first/last 移除邊框 -->
<ul class="divide-y divide-gray-200 rounded-lg border border-gray-200">
  <li class="px-4 py-3 first:rounded-t-lg last:rounded-b-lg hover:bg-gray-50">
    Item 1
  </li>
  <li class="px-4 py-3 first:rounded-t-lg last:rounded-b-lg hover:bg-gray-50">
    Item 2
  </li>
  <li class="px-4 py-3 first:rounded-t-lg last:rounded-b-lg hover:bg-gray-50">
    Item 3
  </li>
</ul>

<!-- 表格：odd/even 斑馬紋 -->
<table class="w-full">
  <thead>
    <tr class="border-b border-gray-200 bg-gray-50">
      <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Name</th>
      <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Role</th>
    </tr>
  </thead>
  <tbody>
    <tr class="odd:bg-white even:bg-gray-50 hover:bg-blue-50">
      <td class="px-4 py-3 text-sm">Alice</td>
      <td class="px-4 py-3 text-sm">Engineer</td>
    </tr>
    <tr class="odd:bg-white even:bg-gray-50 hover:bg-blue-50">
      <td class="px-4 py-3 text-sm">Bob</td>
      <td class="px-4 py-3 text-sm">Designer</td>
    </tr>
    <tr class="odd:bg-white even:bg-gray-50 hover:bg-blue-50">
      <td class="px-4 py-3 text-sm">Charlie</td>
      <td class="px-4 py-3 text-sm">Manager</td>
    </tr>
    <tr class="odd:bg-white even:bg-gray-50 hover:bg-blue-50">
      <td class="px-4 py-3 text-sm">Diana</td>
      <td class="px-4 py-3 text-sm">Analyst</td>
    </tr>
  </tbody>
</table>
```

### Step 4: Group 修飾符 --- 父元素狀態影響子元素

在父元素加上 `group`，子元素使用 `group-hover:` 等變體。

```html
<!-- 卡片：hover 時整體變化 -->
<a href="#" class="group block rounded-xl border border-gray-200 p-6 transition-shadow hover:shadow-lg">
  <div class="flex items-center gap-4">
    <!-- 圖示：父 hover 時顏色變化 -->
    <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100 text-blue-600
                group-hover:bg-blue-600 group-hover:text-white transition-colors">
      <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
      </svg>
    </div>
    <div>
      <!-- 標題：父 hover 時顏色變化 -->
      <h3 class="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
        Feature Title
      </h3>
      <p class="mt-1 text-sm text-gray-500">Click to learn more about this feature.</p>
    </div>
  </div>
  <!-- 箭頭：父 hover 時位移 -->
  <span class="mt-4 inline-flex items-center text-sm font-medium text-blue-600 opacity-0
               group-hover:opacity-100 group-hover:translate-x-1 transition-all">
    Learn more &rarr;
  </span>
</a>
```

### Step 5: Named Groups 命名群組（避免巢狀衝突）

```html
<!-- 命名群組：解決巢狀 group 的作用域問題 -->
<div class="group/card rounded-xl border p-6 hover:shadow-lg">
  <h3 class="font-bold group-hover/card:text-blue-600">Card Title</h3>

  <div class="mt-4 space-y-2">
    <!-- 內層有自己的 group 命名 -->
    <a href="#" class="group/link flex items-center gap-2 text-sm text-gray-600">
      <span class="group-hover/link:text-blue-600 group-hover/link:underline">
        Link inside card
      </span>
      <span class="opacity-0 group-hover/link:opacity-100 transition-opacity">
        &rarr;
      </span>
    </a>

    <a href="#" class="group/link flex items-center gap-2 text-sm text-gray-600">
      <span class="group-hover/link:text-blue-600 group-hover/link:underline">
        Another link
      </span>
      <span class="opacity-0 group-hover/link:opacity-100 transition-opacity">
        &rarr;
      </span>
    </a>
  </div>
</div>
```

### Step 6: Peer 修飾符 --- 兄弟元素狀態影響

`peer` 必須是 DOM 中的前一個兄弟元素。

```html
<!-- 自訂 Checkbox -->
<label class="flex cursor-pointer items-center gap-3">
  <input type="checkbox" class="peer sr-only" />
  <div class="h-5 w-5 rounded border-2 border-gray-300
              peer-checked:border-blue-600 peer-checked:bg-blue-600
              transition-colors">
    <!-- Checkmark icon (hidden by default, shown when checked) -->
    <svg class="hidden h-full w-full text-white peer-checked:block" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
    </svg>
  </div>
  <span class="text-sm text-gray-700 peer-checked:text-blue-700 peer-checked:font-medium">
    I agree to the terms
  </span>
</label>

<!-- 表單驗證：peer-invalid 顯示錯誤訊息 -->
<div class="space-y-1">
  <input
    type="email"
    required
    placeholder="your@email.com"
    class="peer w-full rounded-lg border border-gray-300 px-4 py-2
           focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200
           invalid:border-red-500 invalid:focus:ring-red-200"
  />
  <p class="hidden text-sm text-red-500 peer-invalid:block">
    Please enter a valid email address.
  </p>
</div>
```

### Step 7: 堆疊變體（Stacking Variants）

多個變體可以堆疊，從左到右依序表示條件。

```html
<!-- 響應式 + 狀態：在 md 以上 hover 時才變色 -->
<button class="bg-gray-200 md:bg-gray-100 md:hover:bg-blue-500 md:hover:text-white
               transition-colors rounded-lg px-4 py-2">
  Responsive + Hover
</button>

<!-- 群組 + 響應式：在 lg 以上且父 hover 時才顯示 -->
<div class="group">
  <span class="hidden lg:group-hover:inline-block transition-all">
    Desktop hover only
  </span>
</div>

<!-- dark + hover：深色模式的 hover 效果 -->
<button class="bg-white text-gray-900
               hover:bg-gray-100
               dark:bg-gray-800 dark:text-white
               dark:hover:bg-gray-700
               transition-colors rounded-lg px-4 py-2">
  Dark + Hover
</button>
```

### Step 8: before: 和 after: 偽元素

```html
<!-- before: 裝飾性標記 -->
<h2 class="relative pl-4 text-xl font-bold
           before:absolute before:left-0 before:top-0 before:h-full before:w-1
           before:rounded-full before:bg-blue-600 before:content-['']">
  Section Title
</h2>

<!-- after: 必填星號 -->
<label class="text-sm font-medium text-gray-700
              after:ml-0.5 after:text-red-500 after:content-['*']">
  Email Address
</label>

<!-- before + after 組合：引號裝飾 -->
<blockquote class="relative px-8 py-4 text-lg italic text-gray-600
                   before:absolute before:left-0 before:top-0 before:text-5xl
                   before:leading-none before:text-gray-300 before:content-['\201C']
                   after:absolute after:bottom-0 after:right-0 after:text-5xl
                   after:leading-none after:text-gray-300 after:content-['\201D']">
  Design is not just what it looks like. Design is how it works.
</blockquote>
```

### Step 9: 在 React 中使用狀態變體

Tailwind 的狀態變體在 React/JSX 中同樣適用，且可以結合 React 的狀態管理。

```tsx
// React: InteractiveCard component
function InteractiveCard({ title, description, href }: {
  title: string;
  description: string;
  href: string;
}) {
  return (
    <a
      href={href}
      className="group block rounded-xl border border-gray-200 p-6
                 hover:border-blue-300 hover:shadow-lg
                 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
                 transition-all duration-200"
    >
      <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
        {title}
      </h3>
      <p className="mt-2 text-sm text-gray-500">{description}</p>
      <span className="mt-4 inline-flex items-center text-sm font-medium text-blue-600
                       opacity-0 group-hover:opacity-100 group-hover:translate-x-1
                       transition-all duration-200">
        Learn more &rarr;
      </span>
    </a>
  );
}
```

```svelte
<!-- Svelte: InteractiveCard component -->
<script>
  export let title;
  export let description;
  export let href;
</script>

<a
  {href}
  class="group block rounded-xl border border-gray-200 p-6
         hover:border-blue-300 hover:shadow-lg
         focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
         transition-all duration-200"
>
  <h3 class="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
    {title}
  </h3>
  <p class="mt-2 text-sm text-gray-500">{description}</p>
  <span class="mt-4 inline-flex items-center text-sm font-medium text-blue-600
               opacity-0 group-hover:opacity-100 group-hover:translate-x-1
               transition-all duration-200">
    Learn more &rarr;
  </span>
</a>
```

### Step 10: selection: 和 marker: 微調

```html
<!-- 自訂文字選取顏色 -->
<div class="selection:bg-blue-200 selection:text-blue-900">
  <p>選取這段文字，會看到藍色的選取背景色。</p>
  <p>整個區塊的所有子元素都會繼承這個選取樣式。</p>
</div>

<!-- 自訂列表項目符號 -->
<ul class="list-disc space-y-2 pl-6 marker:text-blue-600">
  <li>第一個項目 --- 藍色圓點</li>
  <li>第二個項目 --- 藍色圓點</li>
  <li>第三個項目 --- 藍色圓點</li>
</ul>

<!-- 自訂 file input 按鈕 -->
<input
  type="file"
  class="text-sm text-gray-500
         file:mr-4 file:rounded-lg file:border-0
         file:bg-blue-50 file:px-4 file:py-2
         file:text-sm file:font-medium file:text-blue-700
         hover:file:bg-blue-100
         file:transition-colors file:cursor-pointer"
/>
```

## Hands-on Lab

### Foundation 基礎練習

**任務：** 建立一組互動按鈕，展示不同的狀態效果。

需求：
- Primary 按鈕：hover 變深、active 縮小、focus 顯示 ring
- Secondary 按鈕：hover 背景出現、active 變色
- Disabled 按鈕：降低透明度、cursor-not-allowed
- 危險按鈕（紅色系列）：hover 加深、focus ring 用紅色

**驗收清單：**
- [ ] 四個按鈕各有正確的 hover / active / focus 效果
- [ ] Disabled 按鈕的 hover 不會改變顏色
- [ ] focus-visible 只在鍵盤 Tab 時顯示
- [ ] 所有狀態變化有平滑的 transition

### Advanced 進階練習

**任務：** 建立一個互動式卡片列表和表單。

需求：
- 3 張 group hover 卡片：hover 時圖示變色、標題變色、箭頭出現
- 使用命名群組（`group/card`）避免巢狀衝突
- 表格使用 odd/even 斑馬紋 + hover 高亮行
- 表單包含 focus-within 高亮的搜尋欄位和 peer-invalid 錯誤提示

**驗收清單：**
- [ ] 卡片 hover 效果流暢，箭頭從透明到可見
- [ ] 命名群組正確隔離巢狀 hover 範圍
- [ ] 表格斑馬紋 + hover 高亮正常
- [ ] 輸入無效值時錯誤訊息正確顯示
- [ ] 所有互動均有 transition 過渡效果

### Challenge 挑戰練習

**任務：** 建立一個完整的自訂表單系統（不使用 JavaScript 切換樣式）。

需求：
- 自訂 checkbox（peer + peer-checked）
- 自訂 radio button（peer + peer-checked）
- 自訂 toggle switch（peer + peer-checked + before: 偽元素）
- 使用 peer-invalid 的即時驗證回饋
- 所有自訂控件需支援 focus-visible
- 提供 React 和純 HTML 兩種實作

**驗收清單：**
- [ ] 自訂 checkbox 點擊可勾選/取消
- [ ] 自訂 radio button 同組互斥
- [ ] Toggle switch 有平滑動畫
- [ ] 表單驗證錯誤即時顯示
- [ ] Tab 鍵盤導航正確且顯示 focus ring
- [ ] React 版本功能一致

## Reference Solution

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ch11 Lab - State Variants Demo</title>
  <link rel="stylesheet" href="/src/output.css" />
</head>
<body class="min-h-screen bg-gray-50 p-8 text-gray-900 selection:bg-blue-200 selection:text-blue-900">

  <div class="mx-auto max-w-4xl space-y-16">

    <!-- ====== Section 1: Buttons ====== -->
    <section>
      <h2 class="relative mb-8 pl-4 text-2xl font-bold
                 before:absolute before:left-0 before:top-0 before:h-full before:w-1
                 before:rounded-full before:bg-blue-600 before:content-['']">
        Interactive Buttons
      </h2>
      <div class="flex flex-wrap gap-4">
        <!-- Primary -->
        <button class="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white
                       hover:bg-blue-700
                       active:scale-95 active:bg-blue-800
                       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
                       transition-all duration-150">
          Primary
        </button>
        <!-- Secondary -->
        <button class="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700
                       hover:bg-gray-50 hover:border-gray-400
                       active:bg-gray-100
                       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 focus-visible:ring-offset-2
                       transition-all duration-150">
          Secondary
        </button>
        <!-- Danger -->
        <button class="rounded-lg bg-red-600 px-6 py-3 text-sm font-medium text-white
                       hover:bg-red-700
                       active:scale-95 active:bg-red-800
                       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2
                       transition-all duration-150">
          Danger
        </button>
        <!-- Disabled -->
        <button disabled class="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white
                                disabled:cursor-not-allowed disabled:opacity-50
                                disabled:hover:bg-blue-600
                                transition-all duration-150">
          Disabled
        </button>
      </div>
    </section>

    <!-- ====== Section 2: Group Hover Cards ====== -->
    <section>
      <h2 class="relative mb-8 pl-4 text-2xl font-bold
                 before:absolute before:left-0 before:top-0 before:h-full before:w-1
                 before:rounded-full before:bg-green-600 before:content-['']">
        Group Hover Cards
      </h2>
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <!-- Card 1 -->
        <a href="#" class="group/card block rounded-xl border border-gray-200 bg-white p-6 transition-all hover:shadow-lg hover:border-blue-200">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100 text-blue-600
                      group-hover/card:bg-blue-600 group-hover/card:text-white transition-colors">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3 class="mt-4 font-semibold text-gray-900 group-hover/card:text-blue-600 transition-colors">
            Performance
          </h3>
          <p class="mt-2 text-sm text-gray-500">Lightning fast builds with the new Oxide engine.</p>
          <span class="mt-4 inline-flex items-center gap-1 text-sm font-medium text-blue-600
                       opacity-0 translate-x-0 group-hover/card:opacity-100 group-hover/card:translate-x-1
                       transition-all duration-200">
            Learn more &rarr;
          </span>
        </a>

        <!-- Card 2 -->
        <a href="#" class="group/card block rounded-xl border border-gray-200 bg-white p-6 transition-all hover:shadow-lg hover:border-green-200">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100 text-green-600
                      group-hover/card:bg-green-600 group-hover/card:text-white transition-colors">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="mt-4 font-semibold text-gray-900 group-hover/card:text-green-600 transition-colors">
            Reliability
          </h3>
          <p class="mt-2 text-sm text-gray-500">Battle-tested in production across thousands of projects.</p>
          <span class="mt-4 inline-flex items-center gap-1 text-sm font-medium text-green-600
                       opacity-0 group-hover/card:opacity-100 group-hover/card:translate-x-1
                       transition-all duration-200">
            Learn more &rarr;
          </span>
        </a>

        <!-- Card 3 -->
        <a href="#" class="group/card block rounded-xl border border-gray-200 bg-white p-6 transition-all hover:shadow-lg hover:border-purple-200">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100 text-purple-600
                      group-hover/card:bg-purple-600 group-hover/card:text-white transition-colors">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
            </svg>
          </div>
          <h3 class="mt-4 font-semibold text-gray-900 group-hover/card:text-purple-600 transition-colors">
            Customizable
          </h3>
          <p class="mt-2 text-sm text-gray-500">@theme directive makes design token management effortless.</p>
          <span class="mt-4 inline-flex items-center gap-1 text-sm font-medium text-purple-600
                       opacity-0 group-hover/card:opacity-100 group-hover/card:translate-x-1
                       transition-all duration-200">
            Learn more &rarr;
          </span>
        </a>
      </div>
    </section>

    <!-- ====== Section 3: Zebra Stripe Table ====== -->
    <section>
      <h2 class="relative mb-8 pl-4 text-2xl font-bold
                 before:absolute before:left-0 before:top-0 before:h-full before:w-1
                 before:rounded-full before:bg-orange-600 before:content-['']">
        Zebra Table with Hover
      </h2>
      <div class="overflow-hidden rounded-xl border border-gray-200">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-200 bg-gray-50">
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Name</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Role</th>
              <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr class="odd:bg-white even:bg-gray-50 hover:bg-blue-50 transition-colors">
              <td class="px-6 py-4 text-sm font-medium">Alice Chen</td>
              <td class="px-6 py-4 text-sm text-gray-600">Frontend Engineer</td>
              <td class="px-6 py-4"><span class="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">Active</span></td>
            </tr>
            <tr class="odd:bg-white even:bg-gray-50 hover:bg-blue-50 transition-colors">
              <td class="px-6 py-4 text-sm font-medium">Bob Wang</td>
              <td class="px-6 py-4 text-sm text-gray-600">Backend Engineer</td>
              <td class="px-6 py-4"><span class="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">Active</span></td>
            </tr>
            <tr class="odd:bg-white even:bg-gray-50 hover:bg-blue-50 transition-colors">
              <td class="px-6 py-4 text-sm font-medium">Charlie Liu</td>
              <td class="px-6 py-4 text-sm text-gray-600">Designer</td>
              <td class="px-6 py-4"><span class="rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-700">Away</span></td>
            </tr>
            <tr class="odd:bg-white even:bg-gray-50 hover:bg-blue-50 transition-colors">
              <td class="px-6 py-4 text-sm font-medium">Diana Huang</td>
              <td class="px-6 py-4 text-sm text-gray-600">Product Manager</td>
              <td class="px-6 py-4"><span class="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">Active</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- ====== Section 4: Custom Form Controls ====== -->
    <section>
      <h2 class="relative mb-8 pl-4 text-2xl font-bold
                 before:absolute before:left-0 before:top-0 before:h-full before:w-1
                 before:rounded-full before:bg-purple-600 before:content-['']">
        Custom Form Controls (peer)
      </h2>

      <div class="space-y-6 rounded-xl bg-white p-8 shadow-sm">
        <!-- Custom Checkbox -->
        <fieldset class="space-y-3">
          <legend class="text-sm font-semibold text-gray-700">Interests</legend>

          <label class="flex cursor-pointer items-center gap-3">
            <input type="checkbox" class="peer sr-only" />
            <div class="flex h-5 w-5 items-center justify-center rounded border-2 border-gray-300
                        peer-checked:border-blue-600 peer-checked:bg-blue-600
                        peer-focus-visible:ring-2 peer-focus-visible:ring-blue-300 peer-focus-visible:ring-offset-1
                        transition-colors">
              <svg class="hidden h-3 w-3 text-white peer-checked:group-[]:block" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span class="text-sm text-gray-700">Frontend Development</span>
          </label>

          <label class="flex cursor-pointer items-center gap-3">
            <input type="checkbox" class="peer sr-only" />
            <div class="flex h-5 w-5 items-center justify-center rounded border-2 border-gray-300
                        peer-checked:border-blue-600 peer-checked:bg-blue-600
                        peer-focus-visible:ring-2 peer-focus-visible:ring-blue-300 peer-focus-visible:ring-offset-1
                        transition-colors">
            </div>
            <span class="text-sm text-gray-700">Backend Development</span>
          </label>

          <label class="flex cursor-pointer items-center gap-3">
            <input type="checkbox" class="peer sr-only" />
            <div class="flex h-5 w-5 items-center justify-center rounded border-2 border-gray-300
                        peer-checked:border-blue-600 peer-checked:bg-blue-600
                        peer-focus-visible:ring-2 peer-focus-visible:ring-blue-300 peer-focus-visible:ring-offset-1
                        transition-colors">
            </div>
            <span class="text-sm text-gray-700">DevOps</span>
          </label>
        </fieldset>

        <!-- Custom Toggle Switch -->
        <div>
          <label class="flex cursor-pointer items-center gap-3">
            <input type="checkbox" class="peer sr-only" />
            <div class="relative h-6 w-11 rounded-full bg-gray-300
                        peer-checked:bg-blue-600
                        peer-focus-visible:ring-2 peer-focus-visible:ring-blue-300 peer-focus-visible:ring-offset-2
                        transition-colors
                        after:absolute after:left-0.5 after:top-0.5 after:h-5 after:w-5
                        after:rounded-full after:bg-white after:shadow-sm after:transition-transform
                        after:content-['']
                        peer-checked:after:translate-x-5">
            </div>
            <span class="text-sm font-medium text-gray-700">Enable notifications</span>
          </label>
        </div>

        <!-- Validated Input -->
        <div>
          <label class="block text-sm font-medium text-gray-700
                        after:ml-0.5 after:text-red-500 after:content-['*']">
            Email
          </label>
          <input
            type="email"
            required
            placeholder="your@email.com"
            class="peer mt-1 w-full rounded-lg border border-gray-300 px-4 py-2.5
                   placeholder:text-gray-400
                   focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200
                   invalid:border-red-400 invalid:focus:border-red-500 invalid:focus:ring-red-200
                   transition-all"
          />
          <p class="mt-1 hidden text-sm text-red-500 peer-[&:not(:placeholder-shown):invalid]:block">
            Please enter a valid email address.
          </p>
        </div>
      </div>
    </section>

  </div>

</body>
</html>
```

## Common Pitfalls

1. **Peer 元素順序錯誤：** `peer` 修飾符只能影響 DOM 中在其**之後**的兄弟元素。如果目標元素在 `peer` 之前，樣式不會生效。這是因為 CSS 的 `~` 選擇器只能選取後面的兄弟。**解法：** 確保帶有 `peer` class 的元素在 DOM 順序中排在受影響元素之前。

2. **Group 巢狀衝突：** 當多層巢狀都使用 `group` 時，內層的 `group-hover:` 會同時響應外層的 hover。**解法：** 使用命名群組 `group/name` 和 `group-hover/name:` 來明確指定作用域。

3. **Hover 在觸控裝置上的黏滯問題：** 在觸控裝置上，`hover:` 狀態可能在點擊後「黏住」不消失。**解法：** 對關鍵互動使用 `@media (hover: hover)` 或搭配 `active:` 提供替代回饋。Tailwind v4 中可以考慮使用 `@custom-variant` 來定義僅限指標裝置的 hover。

4. **v4 特定 --- 忽視 focus-visible 與 focus 的差異：** Tailwind CSS v4 鼓勵使用 `focus-visible:` 而非 `focus:`，因為 `focus-visible` 只在鍵盤導航時觸發，滑鼠點擊不會顯示焦點框。如果同時使用 `focus:` 和 `focus-visible:`，可能出現重複或衝突的焦點樣式。**解法：** 統一使用 `focus-visible:` 處理焦點輪廓，用 `focus:` 處理不影響視覺的邏輯（如 `focus:outline-none`）。

5. **Before/After 忘記 content：** 使用 `before:` 或 `after:` 偽元素時，必須加上 `content-['']`（即使內容為空），否則偽元素不會渲染。Tailwind v4 不會自動添加 `content: ''`。

## Checklist

- [ ] 能使用 `hover:`、`focus:`、`active:`、`disabled:` 為互動元素添加狀態回饋。
- [ ] 理解 `focus` 與 `focus-visible` 的差異，並知道何時使用哪一個。
- [ ] 能使用 `first:`、`last:`、`odd:`、`even:` 為列表和表格添加結構性樣式。
- [ ] 能使用 `group` + `group-hover:` 實現父子元素聯動效果。
- [ ] 能使用命名群組 `group/{name}` 解決巢狀衝突。
- [ ] 能使用 `peer` + `peer-checked:` / `peer-invalid:` 建立自訂表單控件。
- [ ] 能堆疊多個變體（如 `sm:hover:bg-blue-500`）實現精確的條件式樣式。
- [ ] 能使用 `before:` 和 `after:` 偽元素添加裝飾性內容。

## Further Reading (official links only)

- [Hover, Focus, and Other States - Tailwind CSS](https://tailwindcss.com/docs/hover-focus-and-other-states)
- [Handling Hover, Focus, and Other States - Tailwind CSS](https://tailwindcss.com/docs/hover-focus-and-other-states#pseudo-elements)
- [Tailwind CSS v4.0 - tailwindcss.com](https://tailwindcss.com/blog/tailwindcss-v4)
- [GitHub - tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss)
