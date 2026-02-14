---
title: "Borders, Shadows, and Rings / 邊框、陰影與環形框"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "06"
level: beginner
stack: Tailwind CSS 4.1.x
prerequisites: [05_spacing_sizing_and_box_model]
---
# Borders, Shadows, and Rings / 邊框、陰影與環形框

## Goal

在上一章 [05_spacing_sizing_and_box_model](05_spacing_sizing_and_box_model.md) 中，我們掌握了間距與尺寸的控制。現在要為元素加上視覺邊界與層次感：**邊框（Border）、陰影（Shadow）與環形框（Ring）**。這三者在 UI 設計中扮演著區分區域、傳達深度、指示焦點的角色。特別是 `ring-*` 系列，它是 Tailwind 為 focus 狀態設計的利器，能在不影響佈局的情況下加上外框效果。本章還會介紹 `divide-*` 用於列表分隔線、`outline-*` 用於 focus 指示。

掌握邊框、陰影與環形框後，你將能為 UI 元素建立精緻的視覺層次。下一章 [07_flexbox_layout](07_flexbox_layout.md) 將進入 Flexbox 排版，讓你開始建構真正的頁面佈局。

## Prerequisites

- 已完成第 05 章。
- 理解 CSS `border`、`box-shadow` 屬性的基本概念。
- 知道 `focus` 偽類的用途。

## Core Concepts

### Border vs Ring vs Outline
- **何時用 Border（`border-*`）**：元素需要可見的邊界線，如卡片邊框、輸入框邊框、表格邊框。Border 會佔據空間，影響元素的實際尺寸。
- **何時用 Ring（`ring-*`）**：Focus 狀態的外框指示，或不想影響佈局的裝飾性外框。Ring 使用 `box-shadow` 實現，不佔空間。
- **何時用 Outline（`outline-*`）**：原生的 focus 指示，或需要在 border 外再加一層框線。Outline 不佔空間且不影響佈局。

### Shadow Sizes vs Custom Shadows
- **何時用預設 shadow**：大多數情況。Tailwind 的 `shadow-sm` 到 `shadow-2xl` 涵蓋了卡片、按鈕、彈窗等常見場景。
- **何時自訂 shadow**：設計稿有特定的陰影規格，或需要彩色陰影（colored shadows）。

### divide-* vs Individual Borders
- **何時用 divide-***：列表或堆疊的子元素之間需要分隔線。`divide-y` 自動在子元素之間加上 border-top，不影響第一個元素。
- **何時用個別 border**：特定元素需要獨立的邊框設定。

## Step-by-step

### 1. Border 基礎

```html
<div class="p-8 space-y-6">
  <!-- 基本邊框 -->
  <div class="border p-4 rounded">
    <code>border</code> — 預設 1px solid 邊框
  </div>

  <!-- 邊框寬度 -->
  <div class="flex gap-4">
    <div class="border p-4 rounded">border (1px)</div>
    <div class="border-2 p-4 rounded">border-2 (2px)</div>
    <div class="border-4 p-4 rounded">border-4 (4px)</div>
    <div class="border-8 p-4 rounded">border-8 (8px)</div>
  </div>

  <!-- 單方向邊框 -->
  <div class="flex gap-4">
    <div class="border-t-4 border-blue-500 p-4 bg-gray-50">border-t-4</div>
    <div class="border-r-4 border-green-500 p-4 bg-gray-50">border-r-4</div>
    <div class="border-b-4 border-red-500 p-4 bg-gray-50">border-b-4</div>
    <div class="border-l-4 border-purple-500 p-4 bg-gray-50">border-l-4</div>
  </div>

  <!-- 邊框色彩 -->
  <div class="flex gap-4">
    <div class="border-2 border-blue-500 p-4 rounded">blue-500</div>
    <div class="border-2 border-red-500 p-4 rounded">red-500</div>
    <div class="border-2 border-green-500 p-4 rounded">green-500</div>
    <div class="border-2 border-gray-300 p-4 rounded">gray-300</div>
  </div>
</div>
```

### 2. Border Radius（圓角）

```html
<div class="p-8">
  <div class="flex flex-wrap gap-6">
    <div class="size-20 bg-blue-500 rounded-none flex items-center justify-center text-white text-xs">none</div>
    <div class="size-20 bg-blue-500 rounded-sm flex items-center justify-center text-white text-xs">sm</div>
    <div class="size-20 bg-blue-500 rounded flex items-center justify-center text-white text-xs">default</div>
    <div class="size-20 bg-blue-500 rounded-md flex items-center justify-center text-white text-xs">md</div>
    <div class="size-20 bg-blue-500 rounded-lg flex items-center justify-center text-white text-xs">lg</div>
    <div class="size-20 bg-blue-500 rounded-xl flex items-center justify-center text-white text-xs">xl</div>
    <div class="size-20 bg-blue-500 rounded-2xl flex items-center justify-center text-white text-xs">2xl</div>
    <div class="size-20 bg-blue-500 rounded-3xl flex items-center justify-center text-white text-xs">3xl</div>
    <div class="size-20 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs">full</div>
  </div>

  <!-- 單角圓角 -->
  <div class="flex gap-4 mt-8">
    <div class="size-20 bg-green-500 rounded-tl-2xl flex items-center justify-center text-white text-xs">tl-2xl</div>
    <div class="size-20 bg-green-500 rounded-tr-2xl flex items-center justify-center text-white text-xs">tr-2xl</div>
    <div class="size-20 bg-green-500 rounded-bl-2xl flex items-center justify-center text-white text-xs">bl-2xl</div>
    <div class="size-20 bg-green-500 rounded-br-2xl flex items-center justify-center text-white text-xs">br-2xl</div>
  </div>
</div>
```

### 3. Box Shadow

```html
<div class="p-8 bg-gray-100">
  <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
    <div class="bg-white p-6 rounded-lg shadow-sm text-center">
      <p class="text-sm text-gray-600">shadow-sm</p>
    </div>
    <div class="bg-white p-6 rounded-lg shadow text-center">
      <p class="text-sm text-gray-600">shadow</p>
    </div>
    <div class="bg-white p-6 rounded-lg shadow-md text-center">
      <p class="text-sm text-gray-600">shadow-md</p>
    </div>
    <div class="bg-white p-6 rounded-lg shadow-lg text-center">
      <p class="text-sm text-gray-600">shadow-lg</p>
    </div>
    <div class="bg-white p-6 rounded-lg shadow-xl text-center">
      <p class="text-sm text-gray-600">shadow-xl</p>
    </div>
    <div class="bg-white p-6 rounded-lg shadow-2xl text-center">
      <p class="text-sm text-gray-600">shadow-2xl</p>
    </div>
    <div class="bg-white p-6 rounded-lg shadow-inner text-center">
      <p class="text-sm text-gray-600">shadow-inner</p>
    </div>
    <div class="bg-white p-6 rounded-lg shadow-none text-center">
      <p class="text-sm text-gray-600">shadow-none</p>
    </div>
  </div>
</div>
```

### 4. Ring（環形框）

```html
<div class="p-8 space-y-6">
  <!-- Ring 寬度 -->
  <div class="flex gap-6">
    <div class="p-4 bg-white rounded-lg ring-1 ring-gray-300">ring-1</div>
    <div class="p-4 bg-white rounded-lg ring-2 ring-blue-500">ring-2</div>
    <div class="p-4 bg-white rounded-lg ring-4 ring-purple-500">ring-4</div>
    <div class="p-4 bg-white rounded-lg ring-8 ring-green-500">ring-8</div>
  </div>

  <!-- Ring offset（間隔） -->
  <div class="flex gap-6">
    <div class="p-4 bg-white rounded-lg ring-2 ring-blue-500 ring-offset-0">offset-0</div>
    <div class="p-4 bg-white rounded-lg ring-2 ring-blue-500 ring-offset-2">offset-2</div>
    <div class="p-4 bg-white rounded-lg ring-2 ring-blue-500 ring-offset-4">offset-4</div>
    <div class="p-4 bg-white rounded-lg ring-2 ring-blue-500 ring-offset-8">offset-8</div>
  </div>

  <!-- Focus 狀態的 Ring（最常見用法）-->
  <div>
    <p class="text-sm text-gray-500 mb-2">用 Tab 鍵聚焦下方按鈕：</p>
    <button class="px-4 py-2 bg-blue-500 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
      Focus me
    </button>
  </div>
</div>
```

### 5. Ring vs Border 在 Focus 狀態的比較

```html
<div class="p-8 space-y-6">
  <div>
    <p class="text-sm text-gray-500 mb-2">用 border 做 focus（會導致版面跳動）：</p>
    <input
      type="text"
      placeholder="Border focus"
      class="w-64 px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
    />
  </div>

  <div>
    <p class="text-sm text-gray-500 mb-2">用 ring 做 focus（不影響版面）：</p>
    <input
      type="text"
      placeholder="Ring focus"
      class="w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
    />
  </div>
</div>
```

### 6. divide-* 列表分隔線

```html
<div class="p-8">
  <!-- 垂直分隔線 -->
  <div class="divide-y divide-gray-200 max-w-sm bg-white rounded-lg shadow-sm overflow-hidden">
    <div class="p-4">
      <p class="font-medium">Item 1</p>
      <p class="text-sm text-gray-500">Description for item 1</p>
    </div>
    <div class="p-4">
      <p class="font-medium">Item 2</p>
      <p class="text-sm text-gray-500">Description for item 2</p>
    </div>
    <div class="p-4">
      <p class="font-medium">Item 3</p>
      <p class="text-sm text-gray-500">Description for item 3</p>
    </div>
  </div>

  <!-- 水平分隔線 -->
  <div class="flex divide-x divide-gray-200 bg-white rounded-lg shadow-sm overflow-hidden mt-8">
    <div class="flex-1 p-4 text-center">
      <p class="text-2xl font-bold">128</p>
      <p class="text-sm text-gray-500">Posts</p>
    </div>
    <div class="flex-1 p-4 text-center">
      <p class="text-2xl font-bold">1.2k</p>
      <p class="text-sm text-gray-500">Followers</p>
    </div>
    <div class="flex-1 p-4 text-center">
      <p class="text-2xl font-bold">256</p>
      <p class="text-sm text-gray-500">Following</p>
    </div>
  </div>
</div>
```

### 7. Outline Utilities

```html
<div class="p-8 space-y-4">
  <button class="px-4 py-2 bg-white border border-gray-300 rounded-lg outline-2 outline-offset-2 outline-blue-500 focus:outline">
    Outline on focus
  </button>

  <button class="px-4 py-2 bg-blue-500 text-white rounded-lg outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2">
    Ring instead of outline
  </button>
</div>
```

### 8. Colored Shadows

```html
<div class="p-8 bg-gray-100">
  <div class="grid grid-cols-3 gap-8">
    <div class="bg-white p-6 rounded-xl shadow-lg shadow-blue-500/25 text-center">
      <p class="font-medium text-blue-600">Blue shadow</p>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-lg shadow-rose-500/25 text-center">
      <p class="font-medium text-rose-600">Rose shadow</p>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-lg shadow-green-500/25 text-center">
      <p class="font-medium text-green-600">Green shadow</p>
    </div>
  </div>
</div>
```

### 9. 表單輸入框完整樣式

```html
<div class="p-8 max-w-md space-y-4">
  <!-- 預設輸入框 -->
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
    <input
      type="email"
      placeholder="you@example.com"
      class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm
             focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
             placeholder:text-gray-400"
    />
  </div>

  <!-- 錯誤狀態 -->
  <div>
    <label class="block text-sm font-medium text-red-700 mb-1">Password</label>
    <input
      type="password"
      placeholder="Enter password"
      class="w-full px-4 py-2 border-2 border-red-300 rounded-lg shadow-sm
             focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500
             text-red-900 placeholder:text-red-300"
    />
    <p class="mt-1 text-sm text-red-600">Password must be at least 8 characters.</p>
  </div>

  <!-- 成功狀態 -->
  <div>
    <label class="block text-sm font-medium text-green-700 mb-1">Username</label>
    <input
      type="text"
      value="wilson08"
      class="w-full px-4 py-2 border-2 border-green-300 rounded-lg shadow-sm
             focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500
             text-green-900"
    />
    <p class="mt-1 text-sm text-green-600">Username is available!</p>
  </div>
</div>
```

### 10. 組合應用：Pricing Card

```html
<div class="max-w-sm mx-auto">
  <div class="bg-white rounded-2xl shadow-xl ring-1 ring-gray-900/5 overflow-hidden">
    <div class="p-8">
      <h3 class="text-lg font-semibold text-gray-900">Pro Plan</h3>
      <p class="mt-2 text-sm text-gray-500">Everything you need to get started.</p>
      <p class="mt-6">
        <span class="text-4xl font-bold text-gray-900">$29</span>
        <span class="text-gray-500">/month</span>
      </p>
    </div>
    <div class="border-t border-gray-100 p-8">
      <ul class="space-y-3">
        <li class="flex items-center gap-3 text-sm text-gray-600">
          <span class="size-5 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs">&#10003;</span>
          Unlimited projects
        </li>
        <li class="flex items-center gap-3 text-sm text-gray-600">
          <span class="size-5 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs">&#10003;</span>
          Priority support
        </li>
        <li class="flex items-center gap-3 text-sm text-gray-600">
          <span class="size-5 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs">&#10003;</span>
          Custom domain
        </li>
      </ul>
      <button class="mt-8 w-full py-3 bg-blue-600 text-white rounded-lg font-medium
                     hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                     transition-colors">
        Get started
      </button>
    </div>
  </div>
</div>
```

## Hands-on Lab

### Foundation

建立一個邊框/陰影/環形框展示頁面，分別展示：
- 所有邊框寬度（border 到 border-8）
- 所有圓角級距（rounded-none 到 rounded-full）
- 所有陰影級距（shadow-sm 到 shadow-2xl）

**驗收清單：**
- [ ] 邊框展示至少 5 種寬度。
- [ ] 圓角展示至少 8 種級距。
- [ ] 陰影展示至少 7 種級距。
- [ ] 每個展示項有標籤標註 utility class 名稱。

### Advanced

設計一組表單輸入框元件，包含 4 種狀態：default、focus、error、success。每種狀態使用不同的 border/ring/shadow 組合。

**驗收清單：**
- [ ] 四種輸入框狀態視覺上清楚可區分。
- [ ] Focus 狀態使用 ring-* 而非 border 變化。
- [ ] Error 狀態有紅色提示文字。
- [ ] Success 狀態有綠色確認文字。

### Challenge

建立一組 Pricing Cards（Free / Pro / Enterprise），使用 ring 突顯推薦方案，使用 colored shadows 增加品牌感，使用 divide-* 分隔功能列表。

**驗收清單：**
- [ ] 三張卡片並排展示。
- [ ] 推薦方案有 ring-2 突顯效果。
- [ ] 至少一張卡片使用 colored shadow。
- [ ] 功能列表使用 divide-y 分隔。

## Reference Solution

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Pricing Cards</title>
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body class="min-h-screen bg-gray-50 flex items-center justify-center p-8">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl">
      <!-- Free -->
      <div class="bg-white rounded-2xl shadow-md p-8">
        <h3 class="text-lg font-semibold text-gray-900">Free</h3>
        <p class="mt-4 text-4xl font-bold text-gray-900">$0<span class="text-base font-normal text-gray-500">/mo</span></p>
        <ul class="mt-8 divide-y divide-gray-100">
          <li class="py-3 text-sm text-gray-600">3 projects</li>
          <li class="py-3 text-sm text-gray-600">Community support</li>
          <li class="py-3 text-sm text-gray-600">1 GB storage</li>
        </ul>
        <button class="mt-8 w-full py-2.5 border-2 border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors">
          Get started
        </button>
      </div>

      <!-- Pro (Recommended) -->
      <div class="bg-white rounded-2xl shadow-xl shadow-blue-500/10 ring-2 ring-blue-500 p-8 relative">
        <span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-full">
          RECOMMENDED
        </span>
        <h3 class="text-lg font-semibold text-gray-900">Pro</h3>
        <p class="mt-4 text-4xl font-bold text-gray-900">$29<span class="text-base font-normal text-gray-500">/mo</span></p>
        <ul class="mt-8 divide-y divide-gray-100">
          <li class="py-3 text-sm text-gray-600">Unlimited projects</li>
          <li class="py-3 text-sm text-gray-600">Priority support</li>
          <li class="py-3 text-sm text-gray-600">50 GB storage</li>
          <li class="py-3 text-sm text-gray-600">Custom domain</li>
        </ul>
        <button class="mt-8 w-full py-2.5 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors">
          Upgrade to Pro
        </button>
      </div>

      <!-- Enterprise -->
      <div class="bg-white rounded-2xl shadow-md p-8">
        <h3 class="text-lg font-semibold text-gray-900">Enterprise</h3>
        <p class="mt-4 text-4xl font-bold text-gray-900">$99<span class="text-base font-normal text-gray-500">/mo</span></p>
        <ul class="mt-8 divide-y divide-gray-100">
          <li class="py-3 text-sm text-gray-600">Everything in Pro</li>
          <li class="py-3 text-sm text-gray-600">SLA guarantee</li>
          <li class="py-3 text-sm text-gray-600">Unlimited storage</li>
          <li class="py-3 text-sm text-gray-600">Dedicated support</li>
        </ul>
        <button class="mt-8 w-full py-2.5 border-2 border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors">
          Contact sales
        </button>
      </div>
    </div>
  </body>
</html>
```

## Common Pitfalls

1. **v4 的 ring 預設行為變化（v4 陷阱）**：在 v3 中 `ring` 預設寬度為 3px 且色彩為 `ring-blue-500/50`。在 v4 中，`ring` 的預設值可能不同，建議始終明確指定寬度和顏色，如 `ring-2 ring-blue-500`，避免依賴隱含預設值。

2. **border 不生效**：只寫 `border-blue-500` 而沒有寫 `border`（設定寬度），邊框不會顯示。必須同時設定寬度和顏色：`border border-blue-500` 或 `border-2 border-blue-500`。

3. **shadow 在 border-radius 很大時看起來不自然**：`rounded-full` 搭配 `shadow-2xl` 會產生大面積的圓形陰影。考慮使用較小的陰影級距，或使用 `shadow-lg` 搭配 opacity 修飾符。

4. **divide-* 在動態列表中的陷阱**：如果列表項目是動態渲染的，且第一項可能被條件隱藏，`divide-y` 不會正確跳過隱藏項目。此時考慮用個別 border 替代。

5. **ring-offset-color 忘記設定**：`ring-offset-2` 的間隔預設是白色。如果元素背景不是白色（如深色模式），需要明確設定 `ring-offset-gray-900` 等。

## Checklist

- [ ] 能使用 border、border-2 到 border-8 設定邊框寬度。
- [ ] 能使用 border-t/r/b/l 設定單方向邊框。
- [ ] 能使用 rounded-* 設定圓角。
- [ ] 能使用 shadow-sm 到 shadow-2xl 設定陰影。
- [ ] 能使用 ring-* 設定環形框（特別是 focus 狀態）。
- [ ] 知道 ring vs border 在 focus 狀態的差異。
- [ ] 能使用 divide-y / divide-x 設定列表分隔線。
- [ ] 會使用 colored shadows（shadow-blue-500/25）。

## Further Reading (official links only)

- [Border Width](https://tailwindcss.com/docs/border-width)
- [Border Color](https://tailwindcss.com/docs/border-color)
- [Border Radius](https://tailwindcss.com/docs/border-radius)
- [Box Shadow](https://tailwindcss.com/docs/box-shadow)
- [Ring Width](https://tailwindcss.com/docs/ring-width)
- [Ring Color](https://tailwindcss.com/docs/ring-color)
- [Divide Width](https://tailwindcss.com/docs/divide-width)
- [Outline](https://tailwindcss.com/docs/outline-width)
