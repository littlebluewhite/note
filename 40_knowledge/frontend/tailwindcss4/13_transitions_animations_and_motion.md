---
title: "Transitions, Animations, and Motion / 過渡、動畫與動態效果"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "13"
level: intermediate
stack: Tailwind CSS 4.1.x
prerequisites: [12_dark_mode_and_multi_theme_system]
---

# Transitions, Animations, and Motion / 過渡、動畫與動態效果

## Goal

在前一章 [[12_dark_mode_and_multi_theme_system]] 中，我們提到了主題切換時使用 `transition-colors` 來讓顏色變化更平滑。本章將全面深入 Tailwind CSS v4 的動態效果系統，涵蓋 CSS Transitions（過渡）、CSS Animations（動畫）、以及 Motion 偏好（無障礙動態控制）。

動態效果在現代 UI 中扮演著關鍵角色 --- 它們提供操作回饋、引導使用者注意力、傳達狀態變化、以及增添介面的精緻感。Tailwind CSS v4 提供了完整的 transition 和 animation 工具類別，讓你可以直接在 HTML 中宣告動態行為。內建的 `animate-spin`、`animate-ping`、`animate-pulse`、`animate-bounce` 涵蓋了最常見的動畫場景，而透過 `@theme` 中的 `--animate-*` 自訂屬性，你可以定義任何自訂 keyframe 動畫。此外，`motion-safe:` 和 `motion-reduce:` 變體確保你的動畫對有前庭障礙或偏好減少動態的使用者友善。下一章 [[14_gradients_filters_and_blend_modes]] 將在這些動態效果的基礎上，加入漸層和濾鏡來創建更豐富的視覺效果。

## Prerequisites

- 已完成 [[12_dark_mode_and_multi_theme_system]]，熟悉 `dark:` 變體與主題切換。
- 理解 CSS `transition` 屬性的基本概念（property、duration、timing-function、delay）。
- 知道 CSS `@keyframes` 動畫的基本語法。
- 理解 `transform` 屬性（translate、scale、rotate）的概念。

## Core Concepts

### 1. Transition Utilities / 過渡工具類別

Transition 用於在兩個狀態之間平滑過渡（例如 hover 前後的顏色變化）。

| 工具類別 | CSS 屬性 | 何時使用 | 何時不使用 |
|----------|---------|----------|------------|
| `transition` | `transition: all` | 需要過渡多個屬性時 | 效能敏感場景（all 過於廣泛） |
| `transition-colors` | `transition: color, background-color, border-color, ...` | hover 變色、主題切換 | 需要動畫尺寸或位移時 |
| `transition-opacity` | `transition: opacity` | 淡入淡出效果 | 不涉及透明度變化時 |
| `transition-shadow` | `transition: box-shadow` | hover 陰影變化 | 不涉及陰影時 |
| `transition-transform` | `transition: transform` | 移動、縮放、旋轉動畫 | 不涉及 transform 時 |
| `transition-none` | `transition: none` | 明確停用過渡 | 需要動態效果時 |

### 2. Duration, Timing, and Delay / 時間控制

| 類別 | 效果 | 何時使用 | 何時不使用 |
|------|------|----------|------------|
| `duration-75` ~ `duration-1000` | 過渡持續時間 | 根據動畫複雜度選擇：簡單 hover 用 150ms，複雜動畫用 300-500ms | 不適當的超長或超短時間 |
| `ease-linear` | 等速 | 進度條、旋轉動畫 | 大多數 UI 互動（感覺不自然） |
| `ease-in` | 慢啟動 | 元素「離開」的動畫（配合 ease-out 的進入動畫） | 元素進入視野的動畫 |
| `ease-out` | 慢停止 | 元素「進入」的動畫（最常用） | 需要等速或彈性效果時 |
| `ease-in-out` | 慢啟動慢停止 | 往返動畫、需要優雅感的過渡 | 快速的微互動 |
| `delay-100` ~ `delay-1000` | 延遲啟動 | 錯開多個元素的動畫順序 | 單一元素互動（延遲會感覺遲鈍） |

### 3. Built-in Animations / 內建動畫

| 工具類別 | 效果 | 何時使用 | 何時不使用 |
|----------|------|----------|------------|
| `animate-spin` | 無限旋轉 | Loading spinner | 非載入狀態 |
| `animate-ping` | 向外擴散脈衝 | 通知指示燈、狀態指示器 | 持續顯示會分散注意力的場景 |
| `animate-pulse` | 透明度脈動 | 骨架屏（skeleton loading） | 互動元素（誤導使用者以為可點擊） |
| `animate-bounce` | 上下彈跳 | 向下捲動指示箭頭 | 長時間顯示會令人煩躁的場景 |

### 4. Motion Preferences / 動態偏好（無障礙）

| 變體 | 說明 | 何時使用 | 何時不使用 |
|------|------|----------|------------|
| `motion-safe:` | 僅在使用者**未**要求減少動態時套用 | 裝飾性動畫（不影響功能的過渡效果） | 關鍵的狀態變化提示 |
| `motion-reduce:` | 僅在使用者要求減少動態時套用 | 提供替代回饋（如瞬間切換、縮短動畫） | 完全移除所有回饋 |

## Step-by-step

### Step 1: 基礎 Transition 效果

```html
<!-- 按鈕 hover 過渡 -->
<button class="rounded-lg bg-blue-600 px-6 py-3 text-white
               transition-colors duration-200 ease-out
               hover:bg-blue-700">
  Smooth Hover
</button>

<!-- 多屬性過渡：顏色 + 陰影 + 位移 -->
<div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm
            transition-all duration-300 ease-out
            hover:-translate-y-1 hover:shadow-lg hover:border-blue-200">
  <h3 class="font-semibold">Hover to Elevate</h3>
  <p class="mt-2 text-sm text-gray-500">卡片向上浮動 + 陰影加深</p>
</div>

<!-- 指定過渡屬性（效能更好） -->
<button class="rounded-lg bg-gray-100 px-4 py-2 text-gray-700
               transition-[background-color,transform] duration-150
               hover:bg-gray-200 active:scale-95">
  Specific Properties
</button>
```

### Step 2: Duration 和 Timing Function 選擇

```html
<div class="space-y-4">
  <!-- 快速微互動（150ms） -->
  <button class="rounded bg-blue-600 px-4 py-2 text-white
                 transition-colors duration-150 ease-out
                 hover:bg-blue-700">
    Fast (150ms)
  </button>

  <!-- 標準互動（200-300ms） -->
  <div class="rounded-lg border p-4
              transition-shadow duration-300 ease-out
              hover:shadow-lg">
    Standard (300ms)
  </div>

  <!-- 複雜動畫（500ms） -->
  <div class="origin-center rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 p-4 text-white
              transition-transform duration-500 ease-in-out
              hover:scale-105 hover:rotate-1">
    Complex (500ms)
  </div>

  <!-- 自訂 cubic-bezier -->
  <div class="rounded-lg bg-gray-900 p-4 text-white
              transition-transform duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)]
              hover:scale-110">
    Bouncy easing
  </div>
</div>
```

### Step 3: 使用 Delay 錯開動畫

```html
<!-- 錯開列表項目的進入動畫 -->
<div class="space-y-3">
  <div class="translate-y-0 rounded-lg border p-4 opacity-100
              transition-all duration-500 delay-0">
    Item 1 (no delay)
  </div>
  <div class="translate-y-0 rounded-lg border p-4 opacity-100
              transition-all duration-500 delay-100">
    Item 2 (100ms delay)
  </div>
  <div class="translate-y-0 rounded-lg border p-4 opacity-100
              transition-all duration-500 delay-200">
    Item 3 (200ms delay)
  </div>
  <div class="translate-y-0 rounded-lg border p-4 opacity-100
              transition-all duration-500 delay-300">
    Item 4 (300ms delay)
  </div>
</div>
```

### Step 4: 內建 Animations

```html
<!-- animate-spin: Loading spinner -->
<div class="flex items-center gap-3">
  <svg class="h-5 w-5 animate-spin text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
  </svg>
  <span class="text-sm text-gray-600">Loading...</span>
</div>

<!-- animate-ping: 通知指示燈 -->
<div class="relative">
  <button class="rounded-lg bg-gray-100 px-4 py-2">
    Notifications
  </button>
  <span class="absolute -right-1 -top-1 flex h-3 w-3">
    <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75"></span>
    <span class="relative inline-flex h-3 w-3 rounded-full bg-red-500"></span>
  </span>
</div>

<!-- animate-pulse: Skeleton Loading -->
<div class="space-y-4 rounded-xl border border-gray-200 p-6">
  <div class="flex items-center gap-4">
    <div class="h-12 w-12 animate-pulse rounded-full bg-gray-200"></div>
    <div class="flex-1 space-y-2">
      <div class="h-4 w-3/4 animate-pulse rounded bg-gray-200"></div>
      <div class="h-3 w-1/2 animate-pulse rounded bg-gray-200"></div>
    </div>
  </div>
  <div class="space-y-2">
    <div class="h-3 animate-pulse rounded bg-gray-200"></div>
    <div class="h-3 w-5/6 animate-pulse rounded bg-gray-200"></div>
    <div class="h-3 w-4/6 animate-pulse rounded bg-gray-200"></div>
  </div>
</div>

<!-- animate-bounce: 向下捲動指示 -->
<div class="flex flex-col items-center gap-2 text-gray-400">
  <span class="text-sm">Scroll down</span>
  <svg class="h-6 w-6 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
  </svg>
</div>
```

### Step 5: 自訂 Keyframe 動畫（v4 @theme）

在 Tailwind CSS v4 中，透過 `@theme` 的 `--animate-*` 屬性定義自訂動畫。

```css
/* app.css */
@import "tailwindcss";

@theme {
  /* 定義自訂動畫 */
  --animate-fade-in: fade-in 0.5s ease-out;
  --animate-slide-up: slide-up 0.5s ease-out;
  --animate-slide-down: slide-down 0.3s ease-out;
  --animate-scale-in: scale-in 0.2s ease-out;
  --animate-shake: shake 0.5s ease-in-out;
}

/* 定義 keyframes（必須在 @theme 區塊之外） */
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-down {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
  20%, 40%, 60%, 80% { transform: translateX(4px); }
}
```

```html
<!-- 使用自訂動畫 -->
<div class="animate-fade-in">Fade In</div>
<div class="animate-slide-up">Slide Up</div>
<div class="animate-scale-in">Scale In</div>

<!-- 搭配狀態變體 -->
<div class="opacity-0 hover:animate-slide-up hover:opacity-100">
  Hover to animate
</div>
```

### Step 6: Motion Preferences（無障礙）

尊重使用者的 `prefers-reduced-motion` 系統偏好設定。

```html
<!-- motion-safe：只在使用者允許動態時顯示動畫 -->
<div class="motion-safe:animate-slide-up motion-reduce:opacity-100">
  這個元素只在使用者允許動態時才有滑入動畫。
</div>

<!-- motion-reduce：在使用者偏好減少動態時提供替代方案 -->
<button class="rounded-lg bg-blue-600 px-4 py-2 text-white
               transition-all duration-200
               hover:-translate-y-0.5 hover:shadow-lg
               motion-reduce:transform-none motion-reduce:transition-none
               motion-reduce:hover:translate-y-0 motion-reduce:hover:shadow-none">
  Accessible Button
</button>

<!-- 完整範例：Loading spinner 的無障礙替代 -->
<div class="flex items-center gap-3">
  <!-- 有動畫的 spinner -->
  <svg class="h-5 w-5 animate-spin motion-reduce:hidden text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
  </svg>
  <!-- 減少動態時的替代指示 -->
  <span class="hidden text-sm text-blue-600 motion-reduce:inline">Loading...</span>
  <span class="text-sm text-gray-600 motion-reduce:hidden">Processing your request...</span>
</div>
```

### Step 7: 組合實例 --- Toast Notification

```html
<!-- Toast Notification with animation -->
<div id="toast-container" class="fixed right-4 top-4 z-50 space-y-3">
  <!-- Success Toast -->
  <div class="flex items-start gap-3 rounded-lg border border-green-200 bg-white p-4 shadow-lg
              animate-slide-down
              motion-reduce:animate-none">
    <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-green-100">
      <svg class="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
    </div>
    <div class="flex-1">
      <p class="text-sm font-semibold text-gray-900">Success!</p>
      <p class="mt-1 text-sm text-gray-500">Your changes have been saved.</p>
    </div>
    <button class="text-gray-400 transition-colors hover:text-gray-600">
      <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>

  <!-- Error Toast -->
  <div class="flex items-start gap-3 rounded-lg border border-red-200 bg-white p-4 shadow-lg
              animate-slide-down
              motion-reduce:animate-none"
       style="animation-delay: 150ms;">
    <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-red-100">
      <svg class="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </div>
    <div class="flex-1">
      <p class="text-sm font-semibold text-gray-900">Error</p>
      <p class="mt-1 text-sm text-gray-500">Something went wrong. Please try again.</p>
    </div>
    <button class="text-gray-400 transition-colors hover:text-gray-600">
      <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</div>
```

### Step 8: React 中的動畫元件

```tsx
// AnimatedToast.tsx
import { useEffect, useState, useCallback } from 'react';

type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: number;
  type: ToastType;
  title: string;
  message: string;
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: (id: number) => void }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger enter animation
    requestAnimationFrame(() => setIsVisible(true));

    // Auto-dismiss after 5 seconds
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => onDismiss(toast.id), 300);
    }, 5000);

    return () => clearTimeout(timer);
  }, [toast.id, onDismiss]);

  const borderColor = {
    success: 'border-green-200',
    error: 'border-red-200',
    info: 'border-blue-200',
  }[toast.type];

  return (
    <div
      className={`flex items-start gap-3 rounded-lg border ${borderColor} bg-white p-4 shadow-lg
                  transition-all duration-300 ease-out
                  motion-reduce:transition-none
                  ${isVisible
                    ? 'translate-y-0 opacity-100'
                    : '-translate-y-2 opacity-0'}`}
    >
      <div className="flex-1">
        <p className="text-sm font-semibold text-gray-900">{toast.title}</p>
        <p className="mt-1 text-sm text-gray-500">{toast.message}</p>
      </div>
      <button
        onClick={() => {
          setIsVisible(false);
          setTimeout(() => onDismiss(toast.id), 300);
        }}
        className="text-gray-400 transition-colors hover:text-gray-600"
        aria-label="Dismiss"
      >
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (type: ToastType, title: string, message: string) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, type, title, message }]);
  };

  const removeToast = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <>
      <div className="fixed right-4 top-4 z-50 w-80 space-y-3">
        {toasts.map(toast => (
          <ToastItem key={toast.id} toast={toast} onDismiss={removeToast} />
        ))}
      </div>

      {/* Demo buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => addToast('success', 'Success!', 'Operation completed.')}
          className="rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 transition-colors"
        >
          Show Success
        </button>
        <button
          onClick={() => addToast('error', 'Error', 'Something went wrong.')}
          className="rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700 transition-colors"
        >
          Show Error
        </button>
      </div>
    </>
  );
}
```

### Step 9: 進階 Loading Spinner 變體

```html
<!-- 簡約點狀 Loading -->
<div class="flex items-center gap-1">
  <div class="h-2 w-2 animate-bounce rounded-full bg-blue-600" style="animation-delay: 0ms;"></div>
  <div class="h-2 w-2 animate-bounce rounded-full bg-blue-600" style="animation-delay: 150ms;"></div>
  <div class="h-2 w-2 animate-bounce rounded-full bg-blue-600" style="animation-delay: 300ms;"></div>
</div>

<!-- 旋轉環狀 Loading -->
<div class="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>

<!-- 脈動條狀 Loading -->
<div class="flex items-end gap-1">
  <div class="h-4 w-1 animate-pulse rounded bg-blue-600" style="animation-delay: 0ms;"></div>
  <div class="h-6 w-1 animate-pulse rounded bg-blue-600" style="animation-delay: 100ms;"></div>
  <div class="h-8 w-1 animate-pulse rounded bg-blue-600" style="animation-delay: 200ms;"></div>
  <div class="h-6 w-1 animate-pulse rounded bg-blue-600" style="animation-delay: 300ms;"></div>
  <div class="h-4 w-1 animate-pulse rounded bg-blue-600" style="animation-delay: 400ms;"></div>
</div>

<!-- 全頁 Loading Overlay -->
<div class="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm">
  <div class="flex flex-col items-center gap-4">
    <div class="h-12 w-12 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600"></div>
    <p class="text-sm font-medium text-gray-600 animate-pulse">Loading...</p>
  </div>
</div>
```

### Step 10: v3 vs v4 動畫自訂對比

```js
// v3: tailwind.config.js
module.exports = {
  theme: {
    extend: {
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
};
```

```css
/* v4: CSS-first，更直觀 */
@import "tailwindcss";

@theme {
  --animate-fade-in: fade-in 0.5s ease-out;
  --animate-slide-up: slide-up 0.5s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
```

## Hands-on Lab

### Foundation 基礎練習

**任務：** 建立一組帶有過渡效果的按鈕和卡片。

需求：
- 3 種按鈕樣式，各有不同的 hover transition（顏色過渡、縮放過渡、陰影過渡）
- 每個按鈕的 duration 和 easing 不同
- 一張卡片在 hover 時有向上位移 + 陰影加深的過渡
- 所有動畫都要有 `motion-reduce:` 替代方案

**驗收清單：**
- [ ] 三種按鈕各有正確的 hover 過渡效果
- [ ] 卡片 hover 時平滑上移並加深陰影
- [ ] `motion-reduce` 使用者不會看到任何移動動畫
- [ ] Duration 在 100ms-500ms 的合理範圍內

### Advanced 進階練習

**任務：** 建立一個 Toast 通知系統 + Skeleton Loading 畫面。

需求：
- Toast 從右上角滑入（自訂 keyframe 動畫）
- Toast 分為 success / error / info 三種類型
- Toast 5 秒後自動消失（淡出）
- Skeleton loading 包含頭像、標題、段落的骨架
- 自訂動畫透過 `@theme` 的 `--animate-*` 定義

**驗收清單：**
- [ ] Toast 正確滑入動畫
- [ ] 三種 Toast 類型有不同的顏色標識
- [ ] Toast 自動消失有淡出效果
- [ ] Skeleton 的 pulse 動畫流暢
- [ ] `@theme` 中正確定義了自訂動畫
- [ ] motion-reduce 使用者有合理的替代體驗

### Challenge 挑戰練習

**任務：** 建立一個完整的動畫展示頁面（Animation Gallery）。

需求：
- 展示所有四種內建動畫（spin、ping、pulse、bounce）
- 至少 3 種自訂 keyframe 動畫
- 在 React/Svelte 中實現一個可重用的 `<AnimatedPresence>` 元件
- 每個動畫有 motion-safe / motion-reduce 兩種模式的展示
- 包含一個互動式的 duration / easing 調整器

**驗收清單：**
- [ ] 所有內建動畫正確展示
- [ ] 自訂動畫在 `@theme` 中定義且正常運作
- [ ] AnimatedPresence 元件支援進入/離開動畫
- [ ] motion-reduce 模式有替代回饋
- [ ] 互動調整器能即時預覽不同的 duration 和 easing
- [ ] 同時提供 HTML 和 React 版本

## Reference Solution

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ch13 Lab - Animations Demo</title>
  <style>
    @import "tailwindcss";

    @theme {
      --animate-fade-in: fade-in 0.5s ease-out forwards;
      --animate-slide-up: slide-up 0.5s ease-out forwards;
      --animate-slide-down: slide-down 0.3s ease-out forwards;
      --animate-scale-in: scale-in 0.2s ease-out forwards;
    }

    @keyframes fade-in {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes slide-up {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slide-down {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes scale-in {
      from { opacity: 0; transform: scale(0.95); }
      to { opacity: 1; transform: scale(1); }
    }
  </style>
</head>
<body class="min-h-screen bg-gray-50 p-8 text-gray-900">

  <div class="mx-auto max-w-4xl space-y-16">

    <h1 class="text-3xl font-bold animate-fade-in">Animation Gallery</h1>

    <!-- ====== Built-in Animations ====== -->
    <section class="animate-slide-up">
      <h2 class="mb-6 text-xl font-semibold">Built-in Animations</h2>
      <div class="grid grid-cols-2 gap-6 md:grid-cols-4">
        <div class="flex flex-col items-center gap-3 rounded-xl border bg-white p-6">
          <div class="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <span class="text-sm font-medium">animate-spin</span>
        </div>
        <div class="flex flex-col items-center gap-3 rounded-xl border bg-white p-6">
          <span class="relative flex h-4 w-4">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-75"></span>
            <span class="relative inline-flex h-4 w-4 rounded-full bg-blue-500"></span>
          </span>
          <span class="text-sm font-medium">animate-ping</span>
        </div>
        <div class="flex flex-col items-center gap-3 rounded-xl border bg-white p-6">
          <div class="h-8 w-8 animate-pulse rounded-lg bg-gray-300"></div>
          <span class="text-sm font-medium">animate-pulse</span>
        </div>
        <div class="flex flex-col items-center gap-3 rounded-xl border bg-white p-6">
          <svg class="h-6 w-6 animate-bounce text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
          <span class="text-sm font-medium">animate-bounce</span>
        </div>
      </div>
    </section>

    <!-- ====== Transition Buttons ====== -->
    <section class="animate-slide-up" style="animation-delay: 100ms;">
      <h2 class="mb-6 text-xl font-semibold">Transition Examples</h2>
      <div class="flex flex-wrap gap-4">
        <button class="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white
                       transition-colors duration-200 ease-out
                       hover:bg-blue-700 active:bg-blue-800
                       motion-reduce:transition-none">
          Color Transition
        </button>
        <button class="rounded-lg bg-gray-900 px-6 py-3 text-sm font-medium text-white
                       transition-transform duration-200 ease-out
                       hover:scale-105 active:scale-95
                       motion-reduce:transform-none motion-reduce:transition-none">
          Scale Transition
        </button>
        <button class="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700
                       transition-shadow duration-300 ease-out
                       hover:shadow-lg hover:shadow-blue-500/20
                       motion-reduce:transition-none">
          Shadow Transition
        </button>
      </div>
    </section>

    <!-- ====== Skeleton Loading ====== -->
    <section>
      <h2 class="mb-6 text-xl font-semibold">Skeleton Loading</h2>
      <div class="rounded-xl border border-gray-200 bg-white p-6">
        <div class="flex items-center gap-4">
          <div class="h-14 w-14 animate-pulse rounded-full bg-gray-200
                      motion-reduce:animate-none motion-reduce:bg-gray-300"></div>
          <div class="flex-1 space-y-2">
            <div class="h-4 w-1/3 animate-pulse rounded bg-gray-200
                        motion-reduce:animate-none motion-reduce:bg-gray-300"></div>
            <div class="h-3 w-1/4 animate-pulse rounded bg-gray-200
                        motion-reduce:animate-none motion-reduce:bg-gray-300"></div>
          </div>
        </div>
        <div class="mt-6 space-y-3">
          <div class="h-3 animate-pulse rounded bg-gray-200
                      motion-reduce:animate-none motion-reduce:bg-gray-300"></div>
          <div class="h-3 w-5/6 animate-pulse rounded bg-gray-200
                      motion-reduce:animate-none motion-reduce:bg-gray-300"></div>
          <div class="h-3 w-4/6 animate-pulse rounded bg-gray-200
                      motion-reduce:animate-none motion-reduce:bg-gray-300"></div>
        </div>
      </div>
    </section>

    <!-- ====== Toast Demo ====== -->
    <section>
      <h2 class="mb-6 text-xl font-semibold">Toast Notifications</h2>
      <div class="flex gap-3">
        <button id="btn-success" class="rounded-lg bg-green-600 px-4 py-2 text-sm text-white
                                         transition-colors hover:bg-green-700">
          Show Success Toast
        </button>
        <button id="btn-error" class="rounded-lg bg-red-600 px-4 py-2 text-sm text-white
                                       transition-colors hover:bg-red-700">
          Show Error Toast
        </button>
      </div>
    </section>

    <!-- ====== Hover Card ====== -->
    <section>
      <h2 class="mb-6 text-xl font-semibold">Hover Elevation Card</h2>
      <div class="rounded-xl border border-gray-200 bg-white p-8 shadow-sm
                  transition-all duration-300 ease-out
                  hover:-translate-y-1 hover:shadow-xl hover:border-blue-200
                  motion-reduce:transform-none motion-reduce:transition-shadow motion-reduce:duration-0">
        <h3 class="text-lg font-semibold">Elevated Card</h3>
        <p class="mt-2 text-gray-600">
          Hover 時卡片向上位移 4px 並加深陰影。motion-reduce 模式下只改變陰影不位移。
        </p>
      </div>
    </section>
  </div>

  <!-- ====== Toast Container ====== -->
  <div id="toast-container" class="fixed right-4 top-4 z-50 w-80 space-y-3"></div>

  <script>
    let toastId = 0;

    function createToastElement(type, title, message) {
      const id = ++toastId;
      const colors = {
        success: { border: 'border-green-200', bg: 'bg-green-100', text: 'text-green-600' },
        error: { border: 'border-red-200', bg: 'bg-red-100', text: 'text-red-600' },
      };
      const c = colors[type];

      const toast = document.createElement('div');
      toast.id = 'toast-' + id;
      toast.className = 'flex items-start gap-3 rounded-lg border ' + c.border +
        ' bg-white p-4 shadow-lg animate-slide-down motion-reduce:animate-none transition-all duration-300';

      // Icon container
      const iconWrap = document.createElement('div');
      iconWrap.className = 'flex h-8 w-8 shrink-0 items-center justify-center rounded-full ' + c.bg;
      const iconSpan = document.createElement('span');
      iconSpan.className = c.text + ' text-lg font-bold';
      iconSpan.textContent = type === 'success' ? '\u2713' : '\u2717';
      iconWrap.appendChild(iconSpan);

      // Text container
      const textWrap = document.createElement('div');
      textWrap.className = 'flex-1';
      const titleEl = document.createElement('p');
      titleEl.className = 'text-sm font-semibold text-gray-900';
      titleEl.textContent = title;
      const msgEl = document.createElement('p');
      msgEl.className = 'mt-1 text-sm text-gray-500';
      msgEl.textContent = message;
      textWrap.appendChild(titleEl);
      textWrap.appendChild(msgEl);

      // Close button
      const closeBtn = document.createElement('button');
      closeBtn.className = 'text-gray-400 hover:text-gray-600 transition-colors';
      closeBtn.textContent = '\u00D7';
      closeBtn.addEventListener('click', function() { dismissToast(id); });

      toast.appendChild(iconWrap);
      toast.appendChild(textWrap);
      toast.appendChild(closeBtn);

      return { element: toast, id: id };
    }

    function showToast(type, title, message) {
      const container = document.getElementById('toast-container');
      const { element, id } = createToastElement(type, title, message);
      container.appendChild(element);
      setTimeout(function() { dismissToast(id); }, 5000);
    }

    function dismissToast(id) {
      const toast = document.getElementById('toast-' + id);
      if (!toast) return;
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(function() { toast.remove(); }, 300);
    }

    document.getElementById('btn-success').addEventListener('click', function() {
      showToast('success', 'Success!', 'Your changes have been saved.');
    });
    document.getElementById('btn-error').addEventListener('click', function() {
      showToast('error', 'Error', 'Something went wrong. Please try again.');
    });
  </script>

</body>
</html>
```

## Common Pitfalls

1. **Transition 套用在 `display` 或 `height: auto`：** CSS transition 無法平滑過渡 `display: none` -> `display: block` 或 `height: 0` -> `height: auto`。**解法：** 使用 `opacity` + `pointer-events` + `translate` 來模擬顯示/隱藏，或使用 `max-height` 搭配一個足夠大的值。

2. **所有屬性都用 `transition-all`：** `transition-all` 會監聽所有 CSS 屬性的變化，可能導致意外的動畫（例如 padding 改變時也會過渡）和效能問題。**解法：** 明確指定需要過渡的屬性，如 `transition-colors`、`transition-transform`，或使用 `transition-[background-color,transform]`。

3. **動畫時間過長或過短：** 過短（< 100ms）的過渡使用者幾乎感覺不到，過長（> 500ms）的過渡讓使用者等待煩躁。**解法：** 一般原則：微互動 100-200ms、中等過渡 200-400ms、複雜動畫 300-600ms。

4. **v4 特定 --- @keyframes 放在 @theme 之外：** 在 Tailwind CSS v4 中，`--animate-*` 在 `@theme` 內定義動畫名稱和參數，但 `@keyframes` 必須在 `@theme` 區塊之外定義（在全域 CSS 中）。如果把 `@keyframes` 放在 `@theme` 內會被忽略。

5. **忽略 motion-reduce 無障礙需求：** 有前庭障礙的使用者在看到大量動畫時可能感到不適甚至頭暈。**解法：** 每個動畫都應該有 `motion-reduce:` 替代方案，至少使用 `motion-reduce:animate-none` 或 `motion-reduce:transition-none`。

## Checklist

- [ ] 能使用 `transition-*` 為 hover/focus 狀態添加平滑過渡。
- [ ] 知道如何選擇合適的 `duration-*` 和 `ease-*` 值。
- [ ] 能使用 `delay-*` 錯開多個元素的動畫時序。
- [ ] 能正確使用 `animate-spin`、`animate-ping`、`animate-pulse`、`animate-bounce` 內建動畫。
- [ ] 能透過 `@theme` 的 `--animate-*` 定義自訂 keyframe 動畫。
- [ ] 能使用 `motion-safe:` 和 `motion-reduce:` 提供無障礙的動態體驗。
- [ ] 能組合 transition + animation 建立 Toast 通知和 Skeleton Loading。

## Further Reading (official links only)

- [Transition Property - Tailwind CSS](https://tailwindcss.com/docs/transition-property)
- [Transition Duration - Tailwind CSS](https://tailwindcss.com/docs/transition-duration)
- [Transition Timing Function - Tailwind CSS](https://tailwindcss.com/docs/transition-timing-function)
- [Animation - Tailwind CSS](https://tailwindcss.com/docs/animation)
- [Prefers Reduced Motion - Tailwind CSS](https://tailwindcss.com/docs/hover-focus-and-other-states#prefers-reduced-motion)
- [Tailwind CSS v4.0 - tailwindcss.com](https://tailwindcss.com/blog/tailwindcss-v4)
