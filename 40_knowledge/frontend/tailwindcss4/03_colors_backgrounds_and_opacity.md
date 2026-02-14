---
title: "Colors, Backgrounds, and Opacity / 色彩、背景與透明度"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "03"
level: beginner
stack: Tailwind CSS 4.1.x
prerequisites: [02_installation_and_css_first_configuration]
---
# Colors, Backgrounds, and Opacity / 色彩、背景與透明度

## Goal

在上一章 [02_installation_and_css_first_configuration](02_installation_and_css_first_configuration.md) 中，我們學會了 v4 的安裝方式與 CSS-first 設定。現在要深入 Tailwind 的色彩系統——這是你每天都會使用的核心功能。v4 最重大的色彩變革是預設使用 **oklch 色彩空間**，支援 P3 廣色域，讓色彩在不同螢幕上更加一致且鮮豔。你將學會使用 `bg-*`、`text-*`、`border-*` 色彩 utilities、opacity modifier 語法、arbitrary values，以及如何透過 `@theme` 自訂品牌色彩。

理解色彩系統後，你將能精確控制 UI 中每個元素的色彩表現。下一章 [04_typography_and_text_styling](04_typography_and_text_styling.md) 將探討字體排印系統，讓你的文字樣式同樣精準。

## Prerequisites

- 已完成第 02 章，理解 `@import "tailwindcss"` 與 `@theme` 設定。
- 基礎 CSS 色彩知識（知道 hex、rgb、hsl 格式）。
- 練習環境已可正常運作（`npm run dev`）。

## Core Concepts

### oklch vs sRGB (hex/rgb/hsl)
- **何時用 oklch**：v4 預設使用 oklch，所有主題色彩都基於此色彩空間。當你在 `@theme` 中自訂色彩時，建議使用 oklch 格式以確保色彩的感知一致性（相同 lightness 值看起來亮度一致）。
- **何時用 hex/rgb/hsl**：在 arbitrary values 中可以使用任何 CSS 支援的色彩格式（`bg-[#1da1f2]`、`bg-[rgb(29,161,242)]`）。但這些不會享有 oklch 的感知均勻性優勢。

### Opacity Modifier vs Separate Opacity Utility
- **何時用 Opacity Modifier（`/` 語法）**：需要對特定屬性設定透明度時，如 `bg-red-500/75`（75% opacity 的背景）。這是推薦方式，簡潔且精確。
- **何時用 `opacity-*` utility**：需要整個元素（包含所有子元素）一起改變透明度時。注意 `opacity-*` 影響整個元素，而 `/` modifier 只影響單一屬性。

### @theme Custom Colors vs Arbitrary Values
- **何時用 `@theme` 自訂色彩**：品牌色、語意色（success/warning/error）等在整個專案反覆使用的色彩。定義一次，到處使用。
- **何時用 Arbitrary Values**：一次性的色彩需求，如配合外部設計稿的特定 hex 值。不要為了只用一次的顏色去定義 `@theme` token。

### Background Color vs Background Gradient
- **何時用單色背景**：大多數情況，簡單明確。
- **何時用漸層背景**：Hero 區塊、裝飾性背景、需要視覺層次感的大面積區域。

## Step-by-step

### 1. 認識預設色彩調色盤

Tailwind 提供完整的色彩調色盤，每種顏色有 50-950 共 11 個色階。建立一個色板展示頁面：

```html
<div class="p-8 space-y-6">
  <h2 class="text-xl font-bold">Tailwind 預設調色盤（部分）</h2>

  <!-- Red -->
  <div>
    <p class="text-sm font-medium mb-2">Red</p>
    <div class="flex gap-1">
      <div class="w-12 h-12 bg-red-50 rounded"></div>
      <div class="w-12 h-12 bg-red-100 rounded"></div>
      <div class="w-12 h-12 bg-red-200 rounded"></div>
      <div class="w-12 h-12 bg-red-300 rounded"></div>
      <div class="w-12 h-12 bg-red-400 rounded"></div>
      <div class="w-12 h-12 bg-red-500 rounded"></div>
      <div class="w-12 h-12 bg-red-600 rounded"></div>
      <div class="w-12 h-12 bg-red-700 rounded"></div>
      <div class="w-12 h-12 bg-red-800 rounded"></div>
      <div class="w-12 h-12 bg-red-900 rounded"></div>
      <div class="w-12 h-12 bg-red-950 rounded"></div>
    </div>
  </div>

  <!-- Blue -->
  <div>
    <p class="text-sm font-medium mb-2">Blue</p>
    <div class="flex gap-1">
      <div class="w-12 h-12 bg-blue-50 rounded"></div>
      <div class="w-12 h-12 bg-blue-100 rounded"></div>
      <div class="w-12 h-12 bg-blue-200 rounded"></div>
      <div class="w-12 h-12 bg-blue-300 rounded"></div>
      <div class="w-12 h-12 bg-blue-400 rounded"></div>
      <div class="w-12 h-12 bg-blue-500 rounded"></div>
      <div class="w-12 h-12 bg-blue-600 rounded"></div>
      <div class="w-12 h-12 bg-blue-700 rounded"></div>
      <div class="w-12 h-12 bg-blue-800 rounded"></div>
      <div class="w-12 h-12 bg-blue-900 rounded"></div>
      <div class="w-12 h-12 bg-blue-950 rounded"></div>
    </div>
  </div>
</div>
```

### 2. 使用 text-*、bg-*、border-* 色彩 utilities

```html
<div class="p-6 bg-slate-50 border border-slate-200 rounded-lg">
  <h3 class="text-indigo-700 font-bold text-lg mb-2">色彩應用範例</h3>
  <p class="text-slate-600 mb-4">
    文字色彩用 <code class="text-pink-600 bg-pink-50 px-1 rounded">text-*</code>，
    背景用 <code class="text-pink-600 bg-pink-50 px-1 rounded">bg-*</code>，
    邊框用 <code class="text-pink-600 bg-pink-50 px-1 rounded">border-*</code>。
  </p>
  <button class="bg-indigo-600 text-white border-2 border-indigo-700 px-4 py-2 rounded-lg">
    按鈕範例
  </button>
</div>
```

### 3. 使用 Opacity Modifier 語法

在色彩值後加上 `/` 加上 opacity 百分比：

```html
<div class="space-y-4 p-8">
  <!-- 背景透明度 -->
  <div class="bg-blue-500/100 text-white p-4 rounded">100% opacity</div>
  <div class="bg-blue-500/75 text-white p-4 rounded">75% opacity</div>
  <div class="bg-blue-500/50 text-white p-4 rounded">50% opacity</div>
  <div class="bg-blue-500/25 p-4 rounded">25% opacity</div>

  <!-- 文字透明度 -->
  <p class="text-red-600/100">100% text opacity</p>
  <p class="text-red-600/75">75% text opacity</p>
  <p class="text-red-600/50">50% text opacity</p>

  <!-- 邊框透明度 -->
  <div class="border-4 border-green-500/50 p-4 rounded">50% border opacity</div>

  <!-- 任意值 opacity -->
  <div class="bg-purple-600/[0.33] text-white p-4 rounded">33% opacity (arbitrary)</div>
</div>
```

### 4. Opacity Modifier vs opacity-* 的差異

```html
<div class="flex gap-8 p-8">
  <!-- bg opacity modifier：只有背景透明，文字不受影響 -->
  <div class="bg-blue-600/50 text-white p-6 rounded-lg">
    <p class="font-bold">bg-blue-600/50</p>
    <p>文字保持不透明</p>
  </div>

  <!-- opacity utility：整個元素（含子元素）都變透明 -->
  <div class="bg-blue-600 text-white p-6 rounded-lg opacity-50">
    <p class="font-bold">opacity-50</p>
    <p>文字也變透明了</p>
  </div>
</div>
```

### 5. 使用 Arbitrary Color Values

當設計稿給了特定 hex 值，可用方括號語法：

```html
<div class="space-y-4 p-8">
  <!-- Hex -->
  <div class="bg-[#1da1f2] text-white p-4 rounded">Twitter Blue (#1da1f2)</div>

  <!-- RGB -->
  <div class="bg-[rgb(255,69,0)] text-white p-4 rounded">Reddit Orange</div>

  <!-- HSL -->
  <div class="bg-[hsl(262,52%,47%)] text-white p-4 rounded">Twitch Purple</div>

  <!-- oklch -->
  <div class="bg-[oklch(0.65_0.25_30)] text-white p-4 rounded">oklch Red</div>

  <!-- 搭配 opacity modifier -->
  <div class="bg-[#1da1f2]/75 text-white p-4 rounded">Twitter Blue at 75%</div>
</div>
```

### 6. 使用 @theme 自訂品牌色彩

在 `style.css` 中定義品牌色彩系統：

```css
@import "tailwindcss";

@theme {
  --color-brand-50: oklch(0.97 0.02 250);
  --color-brand-100: oklch(0.93 0.05 250);
  --color-brand-200: oklch(0.88 0.08 250);
  --color-brand-300: oklch(0.80 0.12 250);
  --color-brand-400: oklch(0.72 0.16 250);
  --color-brand-500: oklch(0.65 0.19 250);
  --color-brand-600: oklch(0.55 0.19 250);
  --color-brand-700: oklch(0.48 0.17 250);
  --color-brand-800: oklch(0.40 0.14 250);
  --color-brand-900: oklch(0.32 0.10 250);
  --color-brand-950: oklch(0.25 0.07 250);

  --color-success: oklch(0.72 0.19 145);
  --color-warning: oklch(0.80 0.18 80);
  --color-danger: oklch(0.65 0.22 25);
}
```

使用自訂色彩：

```html
<div class="space-y-4 p-8">
  <div class="bg-brand-500 text-white p-4 rounded-lg">Brand Primary</div>
  <div class="bg-brand-100 text-brand-900 p-4 rounded-lg">Brand Light</div>
  <div class="text-success font-bold">操作成功！</div>
  <div class="text-warning font-bold">請注意！</div>
  <div class="text-danger font-bold">發生錯誤！</div>
</div>
```

### 7. oklch 色彩空間的優勢

理解為什麼 v4 選擇 oklch：

```html
<!-- 同 lightness 的不同色相，視覺亮度一致 -->
<div class="flex gap-2 p-8">
  <div class="w-16 h-16 bg-[oklch(0.7_0.15_0)] rounded" title="Red L=0.7"></div>
  <div class="w-16 h-16 bg-[oklch(0.7_0.15_60)] rounded" title="Yellow L=0.7"></div>
  <div class="w-16 h-16 bg-[oklch(0.7_0.15_120)] rounded" title="Green L=0.7"></div>
  <div class="w-16 h-16 bg-[oklch(0.7_0.15_180)] rounded" title="Cyan L=0.7"></div>
  <div class="w-16 h-16 bg-[oklch(0.7_0.15_240)] rounded" title="Blue L=0.7"></div>
  <div class="w-16 h-16 bg-[oklch(0.7_0.15_300)] rounded" title="Purple L=0.7"></div>
</div>
<!-- 所有色塊看起來亮度相同，這在 HSL 中不可能做到 -->
```

### 8. 使用 currentColor 與 inherit

```html
<div class="text-indigo-600 p-6">
  <!-- 子元素繼承文字色 -->
  <h3 class="font-bold text-lg">父元素色彩</h3>
  <p>這段文字繼承了 indigo-600。</p>

  <!-- 使用 border-current 讓邊框跟隨文字色 -->
  <div class="border-2 border-current p-4 rounded mt-4">
    邊框色彩跟隨 text-indigo-600
  </div>

  <!-- 覆寫子元素色彩 -->
  <p class="text-gray-500 mt-4">這段文字覆寫為 gray-500。</p>
</div>
```

### 9. 背景漸層基礎

```html
<div class="space-y-4 p-8">
  <!-- 線性漸層 -->
  <div class="h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg"></div>

  <!-- 三色漸層 -->
  <div class="h-24 bg-gradient-to-r from-green-400 via-blue-500 to-purple-600 rounded-lg"></div>

  <!-- 帶透明度的漸層 -->
  <div class="h-24 bg-gradient-to-b from-black/80 to-transparent rounded-lg"></div>

  <!-- 不同方向 -->
  <div class="h-24 bg-gradient-to-br from-rose-400 to-orange-300 rounded-lg"></div>
</div>
```

### 10. 組合應用：完整卡片色彩設計

```html
<div class="max-w-sm mx-auto bg-white rounded-xl shadow-lg overflow-hidden">
  <!-- 漸層頭部 -->
  <div class="h-32 bg-gradient-to-br from-brand-400 to-brand-600"></div>

  <!-- 內容區 -->
  <div class="p-6">
    <span class="inline-block bg-success/10 text-success text-sm font-medium px-2 py-1 rounded-full mb-3">
      Active
    </span>
    <h3 class="text-gray-900 font-bold text-xl mb-2">專案名稱</h3>
    <p class="text-gray-500 mb-4">這是一個展示色彩系統應用的卡片範例。</p>
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 bg-brand-500 rounded-full"></div>
      <span class="text-gray-700 font-medium">使用者名稱</span>
    </div>
  </div>
</div>
```

## Hands-on Lab

### Foundation

建立一個調色盤展示頁面，顯示 Tailwind 預設的 5 種色系（red、blue、green、yellow、purple），每種顯示 50-950 所有色階。

**驗收清單：**
- [ ] 5 種色系各顯示 11 個色階。
- [ ] 每個色塊有色彩名稱標註（如 `red-500`）。
- [ ] 色塊排列整齊，使用 flex 或 grid 排版。
- [ ] 頁面有標題和說明文字。

### Advanced

在 Foundation 基礎上，使用 `@theme` 定義一套完整的品牌色系（10 個色階），並為以下語意角色建立色彩：
- success（成功）
- warning（警告）
- danger（危險）
- info（資訊）

展示一組使用語意色彩的通知訊息卡片。

**驗收清單：**
- [ ] `@theme` 中定義了 10 個品牌色階（50-950）。
- [ ] 4 個語意色彩各有對應的 utility class。
- [ ] 4 張通知卡片分別使用不同的語意色彩。
- [ ] 所有自訂色彩使用 oklch 格式。

### Challenge

建立一個「色彩對比度檢測器」頁面，展示不同文字色/背景色組合，並手動標註哪些組合符合 WCAG AA（對比度 >= 4.5:1）標準。使用 opacity modifier 展示半透明色彩疊加效果。

**驗收清單：**
- [ ] 至少 12 種文字/背景色組合。
- [ ] 每種組合標註「PASS」或「FAIL」。
- [ ] 使用 opacity modifier 展示色彩疊加效果。
- [ ] 包含至少一段說明 oklch 如何幫助無障礙設計。

## Reference Solution

```html
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Color System Demo</title>
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-6xl mx-auto">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">色彩系統展示</h1>
      <p class="text-gray-500 mb-8">Tailwind CSS v4 oklch 調色盤</p>

      <!-- Red Palette -->
      <section class="mb-8">
        <h2 class="text-lg font-semibold text-gray-700 mb-3">Red</h2>
        <div class="flex gap-2">
          <div class="flex-1 text-center">
            <div class="h-16 bg-red-50 rounded-t-lg"></div>
            <span class="text-xs text-gray-500">50</span>
          </div>
          <div class="flex-1 text-center">
            <div class="h-16 bg-red-100 rounded-t-lg"></div>
            <span class="text-xs text-gray-500">100</span>
          </div>
          <div class="flex-1 text-center">
            <div class="h-16 bg-red-200 rounded-t-lg"></div>
            <span class="text-xs text-gray-500">200</span>
          </div>
          <div class="flex-1 text-center">
            <div class="h-16 bg-red-300 rounded-t-lg"></div>
            <span class="text-xs text-gray-500">300</span>
          </div>
          <div class="flex-1 text-center">
            <div class="h-16 bg-red-400 rounded-t-lg"></div>
            <span class="text-xs text-gray-500">400</span>
          </div>
          <div class="flex-1 text-center">
            <div class="h-16 bg-red-500 rounded-t-lg"></div>
            <span class="text-xs text-gray-500">500</span>
          </div>
          <div class="flex-1 text-center">
            <div class="h-16 bg-red-600 rounded-t-lg"></div>
            <span class="text-xs text-gray-500">600</span>
          </div>
          <div class="flex-1 text-center">
            <div class="h-16 bg-red-700 rounded-t-lg"></div>
            <span class="text-xs text-gray-500">700</span>
          </div>
          <div class="flex-1 text-center">
            <div class="h-16 bg-red-800 rounded-t-lg"></div>
            <span class="text-xs text-gray-500">800</span>
          </div>
          <div class="flex-1 text-center">
            <div class="h-16 bg-red-900 rounded-t-lg"></div>
            <span class="text-xs text-gray-500">900</span>
          </div>
          <div class="flex-1 text-center">
            <div class="h-16 bg-red-950 rounded-t-lg"></div>
            <span class="text-xs text-gray-500">950</span>
          </div>
        </div>
      </section>

      <!-- Notification Cards -->
      <section class="mb-8">
        <h2 class="text-lg font-semibold text-gray-700 mb-3">語意色彩通知卡片</h2>
        <div class="space-y-4">
          <div class="flex items-start gap-3 bg-success/10 border border-success/30 p-4 rounded-lg">
            <span class="text-success text-xl">&#10003;</span>
            <div>
              <p class="text-success font-semibold">操作成功</p>
              <p class="text-gray-600 text-sm">您的變更已成功儲存。</p>
            </div>
          </div>

          <div class="flex items-start gap-3 bg-warning/10 border border-warning/30 p-4 rounded-lg">
            <span class="text-warning text-xl">&#9888;</span>
            <div>
              <p class="text-warning font-semibold">請注意</p>
              <p class="text-gray-600 text-sm">此操作將影響所有使用者。</p>
            </div>
          </div>

          <div class="flex items-start gap-3 bg-danger/10 border border-danger/30 p-4 rounded-lg">
            <span class="text-danger text-xl">&#10007;</span>
            <div>
              <p class="text-danger font-semibold">發生錯誤</p>
              <p class="text-gray-600 text-sm">請稍後再試或聯絡客服。</p>
            </div>
          </div>

          <div class="flex items-start gap-3 bg-blue-500/10 border border-blue-500/30 p-4 rounded-lg">
            <span class="text-blue-500 text-xl">&#8505;</span>
            <div>
              <p class="text-blue-600 font-semibold">提示資訊</p>
              <p class="text-gray-600 text-sm">您可以在設定中修改偏好。</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Opacity Comparison -->
      <section class="mb-8">
        <h2 class="text-lg font-semibold text-gray-700 mb-3">Opacity Modifier 對比</h2>
        <div class="grid grid-cols-2 gap-6">
          <div>
            <p class="text-sm font-medium mb-2">bg-blue-600/50（僅背景透明）</p>
            <div class="bg-blue-600/50 text-white p-6 rounded-lg">
              <p class="font-bold text-lg">標題文字不透明</p>
              <p>內容文字也不透明</p>
            </div>
          </div>
          <div>
            <p class="text-sm font-medium mb-2">opacity-50（整個元素透明）</p>
            <div class="bg-blue-600 text-white p-6 rounded-lg opacity-50">
              <p class="font-bold text-lg">標題文字也變透明</p>
              <p>內容文字也變透明</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </body>
</html>
```

## Common Pitfalls

1. **不知道 v4 預設使用 oklch 色彩空間（v4 陷阱）**：v4 的所有預設色彩都是 oklch 格式。如果你在 `@theme` 中用 hex 定義色彩，雖然可以運作，但會失去 oklch 的感知均勻性優勢。此外，oklch 支援 P3 廣色域，能顯示比 sRGB 更鮮豔的色彩。

2. **混淆 opacity modifier 與 opacity utility**：`bg-red-500/50` 只讓背景色半透明，子元素不受影響；`opacity-50` 則讓整個元素及其所有子元素都變半透明。這是最常見的色彩透明度錯誤。

3. **Arbitrary value 忘記方括號**：寫成 `bg-#1da1f2` 而不是 `bg-[#1da1f2]`，導致 class 不生效。任意值必須用方括號包裹。

4. **@theme 色彩變數命名不符規範**：在 `@theme` 中命名為 `--brand-color` 而非 `--color-brand`，導致 utility class `bg-brand` 無法自動產生。Tailwind v4 的 `@theme` 需要遵循 `--color-*` 命名空間。

5. **在深色背景上使用低對比度文字**：例如 `bg-gray-800 text-gray-700`，導致文字幾乎不可見。始終注意文字與背景的對比度，WCAG AA 要求至少 4.5:1。

## Checklist

- [ ] 能使用 `bg-*`、`text-*`、`border-*` 設定色彩。
- [ ] 會使用 opacity modifier 語法（`/75`、`/50`）。
- [ ] 能區分 opacity modifier 與 `opacity-*` utility 的差異。
- [ ] 會使用 arbitrary color values（`bg-[#hex]`）。
- [ ] 能在 `@theme` 中定義自訂色彩 token（使用 oklch 格式）。
- [ ] 理解 oklch 色彩空間的優勢。
- [ ] 會使用基礎漸層 utility（`bg-gradient-to-*`、`from-*`、`to-*`）。

## Further Reading (official links only)

- [Text Color](https://tailwindcss.com/docs/text-color)
- [Background Color](https://tailwindcss.com/docs/background-color)
- [Border Color](https://tailwindcss.com/docs/border-color)
- [Opacity](https://tailwindcss.com/docs/opacity)
- [Customizing Colors](https://tailwindcss.com/docs/customizing-colors)
- [Background Gradient](https://tailwindcss.com/docs/background-image)
