---
title: "Tailwind with Svelte Component Patterns / Tailwind 與 Svelte 元件模式"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "21"
level: advanced
stack: Tailwind CSS 4.1.x + Svelte 5.50.x + SvelteKit 2.51.x
prerequisites: [20_tailwind_with_react_component_patterns]
---

# Tailwind with Svelte Component Patterns / Tailwind 與 Svelte 元件模式

## Goal

在前一章 [[20_tailwind_with_react_component_patterns]] 中，我們在 React 生態系中建立了一套包含 Button、Card、Dialog 的 UI 元件庫，使用了 `cva`、`clsx`、`tailwind-merge` 等工具。本章將以相同的元件規格，在 Svelte 5 + SvelteKit 2 的環境中實作對應版本。Svelte 的元件模型與 React 有根本性的不同：Svelte 使用編譯時框架、scoped styles、以及 runes（`$state`、`$props` 等）取代 React 的 hooks。這些差異直接影響 Tailwind CSS 的整合方式。

本章將深入探討 Svelte 中 `class:` directive 的使用、在 scoped `<style>` 區塊中使用 `@apply` 的時機（以及何時不應該使用）、Svelte 的 scoped styles 與 Tailwind utilities 的共存策略、以及如何在 Svelte 中建立元件變體模式。通過並列比較兩個框架的實作，你將更深入理解 Tailwind CSS 的框架無關性，以及不同框架的最佳整合模式。在下一章 [[22_design_system_patterns_and_token_architecture]] 中，我們將把這些元件模式提升到設計系統的層級，建立跨框架的令牌架構。

## Prerequisites

- 已完成第 20 章，理解 React 中的 Tailwind 元件模式。
- 熟悉 Svelte 5 的基礎知識（runes: `$state`, `$props`, `$derived`）。
- 理解 SvelteKit 的基本結構（routes、layouts、load functions）。
- 了解 Svelte 的 scoped styles 機制。
- 開發環境已設定 SvelteKit + Tailwind CSS v4。

## Core Concepts

### 1. class: Directive vs className / class: 指令與 className 對比

Svelte 使用 `class:name={condition}` directive 來條件式切換 CSS class，這是 Svelte 的原生語法特性。

**何時使用 class: directive：**
- 需要根據布林值切換單一 class。
- 條件簡單明確（true/false 切換）。
- Svelte 模板中少量的條件式樣式。

**何時不使用 class: directive（改用 clsx/cn）：**
- 需要在多個互斥的 class 之間切換（如 variant）。
- 條件邏輯複雜，涉及 3 個以上的 class 群組。
- 需要與外部傳入的 class 合併。

### 2. @apply in Scoped Styles / scoped 樣式中的 @apply

Svelte 的 `<style>` 區塊是 scoped 的，可以在其中使用 `@apply` 整合 Tailwind 工具類。但這應該是例外而非常態。

**何時使用 @apply in scoped styles：**
- 元件內部有無法加 class 的第三方 HTML（如 `{@html content}`）。
- 需要使用 Svelte 的 `:global()` 修飾符搭配 Tailwind 樣式。
- 少量元件需要複雜的 CSS 選擇器（如 `nth-child`）。

**何時不使用 @apply：**
- 可以直接在元素上寫 Tailwind class 時（幾乎所有情況）。
- 大量使用 `@apply` 等同於回到傳統 CSS 寫法，失去 utility-first 優勢。
- 想要利用 Tailwind 的 responsive/state 變體時，`@apply` 無法直接使用這些前綴。

### 3. Svelte Scoped Styles vs Tailwind Utilities / Svelte scoped 樣式與 Tailwind 工具類的共存

Svelte 的 scoped styles 和 Tailwind 的 utility classes 代表兩種不同的 CSS 組織哲學，但它們可以和諧共存。

**何時優先使用 Tailwind utilities：**
- 布局、間距、色彩、排版等可用工具類直接表達的樣式。
- 需要 responsive 和 state variants 的樣式。
- 團隊已統一使用 Tailwind 的設計令牌。

**何時使用 Svelte scoped styles：**
- 元件內部的複雜動畫（需要 `@keyframes`）。
- 使用 CSS 選擇器的進階功能（`:has()`、`::part()` 等）。
- 需要利用 Svelte 的 transition/animation 系統。

### 4. Component Variants Pattern in Svelte / Svelte 中的元件變體模式

Svelte 沒有 `cva` 的直接對應物（雖然 cva 也可以在 Svelte 中使用），但 Svelte 的模板語法提供了多種實現變體的方式。

**何時使用 cva（跨框架方案）：**
- 團隊同時維護 React 和 Svelte 版本，需要統一的變體定義。
- 變體組合矩陣複雜（3+ 維度）。
- 需要從變體定義中推導 TypeScript 型別。

**何時使用 Svelte 原生模式：**
- 專案只使用 Svelte，不需要跨框架相容性。
- 變體簡單（1-2 個維度），用 `$derived` 和物件映射即可。
- 希望減少第三方依賴。

## Step-by-step

### 步驟 1：建立 SvelteKit + Tailwind v4 專案

```bash
npx sv create tailwind-svelte-demo
cd tailwind-svelte-demo
npm install
```

確認 CSS 入口檔案正確設定：

```css
/* src/app.css */
@import "tailwindcss";
```

```svelte
<!-- src/routes/+layout.svelte -->
<script>
  import "../app.css";
  let { children } = $props();
</script>

{@render children()}
```

建立工具函式（與 React 版本相同）：

```ts
// src/lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

```bash
npm install clsx tailwind-merge
```

驗證：`npm run dev` 啟動後，Tailwind class 在頁面中正常顯示。

### 步驟 2：建立 Button 元件（Svelte 原生變體模式）

```svelte
<!-- src/lib/components/ui/Button.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";
  import type { HTMLButtonAttributes } from "svelte/elements";

  type Variant = "primary" | "secondary" | "destructive" | "outline" | "ghost" | "link";
  type Size = "sm" | "md" | "lg" | "icon";

  interface ButtonProps extends HTMLButtonAttributes {
    variant?: Variant;
    size?: Size;
    loading?: boolean;
    class?: string;
    children: Snippet;
  }

  let {
    variant = "primary",
    size = "md",
    loading = false,
    class: className,
    disabled,
    children,
    ...restProps
  }: ButtonProps = $props();

  const variantStyles: Record<Variant, string> = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-500",
    secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-400",
    destructive: "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500",
    outline: "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus-visible:ring-gray-400",
    ghost: "text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-400",
    link: "text-blue-600 underline-offset-4 hover:underline focus-visible:ring-blue-500",
  };

  const sizeStyles: Record<Size, string> = {
    sm: "h-8 px-3 text-sm",
    md: "h-10 px-4 text-sm",
    lg: "h-12 px-6 text-base",
    icon: "h-10 w-10",
  };

  let computedClass = $derived(
    cn(
      "inline-flex items-center justify-center gap-2 rounded-lg font-medium",
      "transition-colors duration-200",
      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
      "disabled:pointer-events-none disabled:opacity-50",
      variantStyles[variant],
      sizeStyles[size],
      loading && "cursor-wait",
      className
    )
  );
</script>

<button
  class={computedClass}
  disabled={disabled || loading}
  {...restProps}
>
  {#if loading}
    <svg
      class="h-4 w-4 animate-spin"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      />
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  {/if}
  {@render children()}
</button>
```

使用方式：

```svelte
<script>
  import Button from "$lib/components/ui/Button.svelte";
</script>

<Button variant="primary" size="lg">主要按鈕</Button>
<Button variant="destructive" loading>刪除中</Button>
<Button variant="outline" class="rounded-full">圓角按鈕</Button>
```

驗證：所有 variant x size 組合正確渲染。loading 狀態顯示 spinner 且禁用點擊。

### 步驟 3：建立 Card 元件（compound component 模式）

```svelte
<!-- src/lib/components/ui/Card.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  type Variant = "default" | "outline" | "elevated";

  interface CardProps {
    variant?: Variant;
    class?: string;
    children: Snippet;
  }

  let { variant = "default", class: className, children }: CardProps = $props();

  const variantStyles: Record<Variant, string> = {
    default: "border border-gray-200 shadow-sm",
    outline: "border-2 border-gray-300",
    elevated: "shadow-lg shadow-gray-200/50",
  };

  let computedClass = $derived(
    cn("rounded-xl bg-white text-gray-950", variantStyles[variant], className)
  );
</script>

<div class={computedClass}>
  {@render children()}
</div>
```

```svelte
<!-- src/lib/components/ui/CardHeader.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  interface CardHeaderProps {
    class?: string;
    children: Snippet;
  }

  let { class: className, children }: CardHeaderProps = $props();
</script>

<div class={cn("flex flex-col gap-1.5 p-6 pb-0", className)}>
  {@render children()}
</div>
```

```svelte
<!-- src/lib/components/ui/CardTitle.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  interface CardTitleProps {
    class?: string;
    children: Snippet;
  }

  let { class: className, children }: CardTitleProps = $props();
</script>

<h3 class={cn("text-xl font-semibold leading-tight tracking-tight", className)}>
  {@render children()}
</h3>
```

```svelte
<!-- src/lib/components/ui/CardDescription.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  interface CardDescriptionProps {
    class?: string;
    children: Snippet;
  }

  let { class: className, children }: CardDescriptionProps = $props();
</script>

<p class={cn("text-sm text-gray-500", className)}>
  {@render children()}
</p>
```

```svelte
<!-- src/lib/components/ui/CardContent.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  interface CardContentProps {
    class?: string;
    children: Snippet;
  }

  let { class: className, children }: CardContentProps = $props();
</script>

<div class={cn("p-6", className)}>
  {@render children()}
</div>
```

```svelte
<!-- src/lib/components/ui/CardFooter.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  interface CardFooterProps {
    class?: string;
    children: Snippet;
  }

  let { class: className, children }: CardFooterProps = $props();
</script>

<div class={cn("flex items-center gap-2 p-6 pt-0", className)}>
  {@render children()}
</div>
```

使用方式：

```svelte
<script>
  import Card from "$lib/components/ui/Card.svelte";
  import CardHeader from "$lib/components/ui/CardHeader.svelte";
  import CardTitle from "$lib/components/ui/CardTitle.svelte";
  import CardDescription from "$lib/components/ui/CardDescription.svelte";
  import CardContent from "$lib/components/ui/CardContent.svelte";
  import CardFooter from "$lib/components/ui/CardFooter.svelte";
  import Button from "$lib/components/ui/Button.svelte";
</script>

<Card variant="elevated" class="max-w-md mx-auto">
  <CardHeader>
    <CardTitle>專案統計</CardTitle>
    <CardDescription>上週的開發進度摘要。</CardDescription>
  </CardHeader>
  <CardContent>
    <div class="grid grid-cols-2 gap-4">
      <div>
        <p class="text-2xl font-bold">128</p>
        <p class="text-sm text-gray-500">commits</p>
      </div>
      <div>
        <p class="text-2xl font-bold">24</p>
        <p class="text-sm text-gray-500">PRs merged</p>
      </div>
    </div>
  </CardContent>
  <CardFooter>
    <Button variant="outline" size="sm">查看詳情</Button>
  </CardFooter>
</Card>
```

驗證：Card 及其子元件正確組合渲染，三種 variant 有明顯視覺區分。

### 步驟 4：建立 Dialog 元件（使用 Svelte transition）

Svelte 有內建的 transition 系統，不需要 Headless UI：

```svelte
<!-- src/lib/components/ui/Dialog.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import { fade, scale } from "svelte/transition";
  import type { Snippet } from "svelte";

  interface DialogProps {
    open: boolean;
    onclose: () => void;
    class?: string;
    children: Snippet;
  }

  let { open, onclose, class: className, children }: DialogProps = $props();

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Escape") {
      onclose();
    }
  }

  function handleBackdropClick() {
    onclose();
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <!-- Backdrop -->
  <div
    class="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
    transition:fade={{ duration: 200 }}
    role="presentation"
    onclick={handleBackdropClick}
  >
  </div>

  <!-- Dialog Panel -->
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    role="dialog"
    aria-modal="true"
  >
    <div
      class={cn(
        "w-full max-w-md rounded-2xl bg-white p-6 shadow-xl",
        "ring-1 ring-gray-200",
        className
      )}
      transition:scale={{ start: 0.95, duration: 200 }}
      onclick|stopPropagation
    >
      {@render children()}
    </div>
  </div>
{/if}
```

```svelte
<!-- src/lib/components/ui/DialogTitle.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  interface DialogTitleProps {
    class?: string;
    children: Snippet;
  }

  let { class: className, children }: DialogTitleProps = $props();
</script>

<h2 class={cn("text-lg font-semibold text-gray-900", className)}>
  {@render children()}
</h2>
```

```svelte
<!-- src/lib/components/ui/DialogDescription.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  interface DialogDescriptionProps {
    class?: string;
    children: Snippet;
  }

  let { class: className, children }: DialogDescriptionProps = $props();
</script>

<p class={cn("mt-2 text-sm text-gray-500", className)}>
  {@render children()}
</p>
```

```svelte
<!-- src/lib/components/ui/DialogFooter.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  interface DialogFooterProps {
    class?: string;
    children: Snippet;
  }

  let { class: className, children }: DialogFooterProps = $props();
</script>

<div class={cn("mt-6 flex justify-end gap-3", className)}>
  {@render children()}
</div>
```

使用方式：

```svelte
<!-- src/routes/demo/+page.svelte -->
<script lang="ts">
  import Button from "$lib/components/ui/Button.svelte";
  import Dialog from "$lib/components/ui/Dialog.svelte";
  import DialogTitle from "$lib/components/ui/DialogTitle.svelte";
  import DialogDescription from "$lib/components/ui/DialogDescription.svelte";
  import DialogFooter from "$lib/components/ui/DialogFooter.svelte";

  let isOpen = $state(false);
</script>

<div class="flex min-h-screen items-center justify-center">
  <Button onclick={() => (isOpen = true)}>開啟 Dialog</Button>

  <Dialog open={isOpen} onclose={() => (isOpen = false)}>
    <DialogTitle>確認刪除</DialogTitle>
    <DialogDescription>
      確定要刪除這個項目嗎？此操作無法復原。
    </DialogDescription>
    <DialogFooter>
      <Button variant="outline" onclick={() => (isOpen = false)}>取消</Button>
      <Button variant="destructive" onclick={() => (isOpen = false)}>刪除</Button>
    </DialogFooter>
  </Dialog>
</div>
```

驗證：Dialog 開啟時有 fade + scale 進場動畫和 backdrop blur。Esc 鍵和點擊外部可關閉。

### 步驟 5：示範 class: directive 的使用場景

`class:` directive 是 Svelte 特有的條件式 class 語法：

```svelte
<!-- src/lib/components/ui/Toggle.svelte -->
<script lang="ts">
  interface ToggleProps {
    checked?: boolean;
    onchange?: (checked: boolean) => void;
    label?: string;
  }

  let { checked = false, onchange, label }: ToggleProps = $props();

  function toggle() {
    checked = !checked;
    onchange?.(checked);
  }
</script>

<button
  type="button"
  role="switch"
  aria-checked={checked}
  class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full
         border-2 border-transparent transition-colors duration-200
         focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
         focus-visible:ring-offset-2"
  class:bg-blue-600={checked}
  class:bg-gray-200={!checked}
  onclick={toggle}
>
  <span
    class="pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow-lg
           ring-0 transition-transform duration-200"
    class:translate-x-5={checked}
    class:translate-x-0={!checked}
  ></span>
</button>
{#if label}
  <span class="ml-3 text-sm text-gray-700">{label}</span>
{/if}
```

使用方式：

```svelte
<script>
  import Toggle from "$lib/components/ui/Toggle.svelte";
  let darkMode = $state(false);
</script>

<Toggle bind:checked={darkMode} label="深色模式" />
<p>目前狀態：{darkMode ? '開啟' : '關閉'}</p>
```

驗證：Toggle 切換時有流暢的滑動動畫，背景色在藍色和灰色之間切換。

### 步驟 6：@apply 在 scoped styles 中的正確使用

展示 `@apply` 的合理使用場景（處理無法控制 class 的 HTML）：

```svelte
<!-- src/lib/components/ProseContent.svelte -->
<script lang="ts">
  interface ProseContentProps {
    html: string;
  }

  let { html }: ProseContentProps = $props();
</script>

<div class="prose-content">
  {@html html}
</div>

<style>
  /* 合理使用 @apply：無法直接控制 {@html} 產生的 HTML 元素 */
  .prose-content :global(h1) {
    @apply text-3xl font-bold text-gray-900 mb-4;
  }
  .prose-content :global(h2) {
    @apply text-2xl font-semibold text-gray-800 mb-3 mt-8;
  }
  .prose-content :global(p) {
    @apply text-base text-gray-700 leading-relaxed mb-4;
  }
  .prose-content :global(a) {
    @apply text-blue-600 underline underline-offset-2 hover:text-blue-800;
  }
  .prose-content :global(code) {
    @apply bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono;
  }
  .prose-content :global(blockquote) {
    @apply border-l-4 border-gray-300 pl-4 italic text-gray-600 my-4;
  }
  .prose-content :global(ul) {
    @apply list-disc pl-6 mb-4 space-y-1;
  }
  .prose-content :global(ol) {
    @apply list-decimal pl-6 mb-4 space-y-1;
  }
</style>
```

使用方式：

```svelte
<script>
  import ProseContent from "$lib/components/ProseContent.svelte";
  const articleHtml = `
    <h1>文章標題</h1>
    <p>這是從 CMS 取得的 HTML 內容，我們無法控制它的 class 屬性。</p>
    <blockquote><p>這是一段引用。</p></blockquote>
    <ul><li>項目一</li><li>項目二</li></ul>
  `;
</script>

<ProseContent html={articleHtml} />
```

驗證：透過 `{@html}` 渲染的 HTML 有正確的 Tailwind 排版樣式。

### 步驟 7：Svelte scoped styles 與 Tailwind utilities 共存

展示兩者和諧共存的模式：

```svelte
<!-- src/lib/components/ui/AnimatedCard.svelte -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import type { Snippet } from "svelte";

  interface AnimatedCardProps {
    class?: string;
    children: Snippet;
    hoverEffect?: boolean;
  }

  let { class: className, children, hoverEffect = true }: AnimatedCardProps = $props();
</script>

<!-- Tailwind utilities 處理布局、色彩、間距 -->
<div
  class={cn(
    "rounded-xl bg-white p-6 shadow-md border border-gray-200",
    hoverEffect && "card-hover",
    className
  )}
>
  {@render children()}
</div>

<style>
  /* Svelte scoped styles 處理複雜動畫 */
  .card-hover {
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
                box-shadow 0.3s ease;
  }
  .card-hover:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.15);
  }

  /* 不使用 @apply，因為 Tailwind class 已經在模板中了 */
  /* 只用 scoped styles 處理 Tailwind 不擅長的複雜動畫 */
</style>
```

驗證：卡片 hover 時有彈性的上浮和放大動畫，Tailwind 的布局樣式同時正常運作。

### 步驟 8：使用 cva 實現跨框架變體（選用方案）

展示 cva 在 Svelte 中的使用方式，實現與 React 版本完全相同的變體定義：

```bash
npm install class-variance-authority
```

```ts
// src/lib/components/ui/button-variants.ts
// 獨立的變體定義檔案，可在 React 和 Svelte 之間共用
import { cva, type VariantProps } from "class-variance-authority";

export const buttonVariants = cva(
  [
    "inline-flex items-center justify-center gap-2 rounded-lg font-medium",
    "transition-colors duration-200",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
    "disabled:pointer-events-none disabled:opacity-50",
  ],
  {
    variants: {
      variant: {
        primary: "bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-500",
        secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-400",
        destructive: "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500",
        outline: "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus-visible:ring-gray-400",
        ghost: "text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-400",
        link: "text-blue-600 underline-offset-4 hover:underline focus-visible:ring-blue-500",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-sm",
        lg: "h-12 px-6 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

export type ButtonVariantProps = VariantProps<typeof buttonVariants>;
```

```svelte
<!-- src/lib/components/ui/ButtonCva.svelte -->
<!-- 使用 cva 的 Button（跨框架方案） -->
<script lang="ts">
  import { cn } from "$lib/utils";
  import { buttonVariants, type ButtonVariantProps } from "./button-variants";
  import type { Snippet } from "svelte";
  import type { HTMLButtonAttributes } from "svelte/elements";

  interface ButtonCvaProps extends HTMLButtonAttributes {
    variant?: ButtonVariantProps["variant"];
    size?: ButtonVariantProps["size"];
    loading?: boolean;
    class?: string;
    children: Snippet;
  }

  let {
    variant,
    size,
    loading = false,
    class: className,
    disabled,
    children,
    ...restProps
  }: ButtonCvaProps = $props();

  let computedClass = $derived(
    cn(buttonVariants({ variant, size }), loading && "cursor-wait", className)
  );
</script>

<button
  class={computedClass}
  disabled={disabled || loading}
  {...restProps}
>
  {#if loading}
    <svg class="h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  {/if}
  {@render children()}
</button>
```

驗證：ButtonCva 的行為與步驟 2 的 Button 完全一致。變體定義檔案可以在 React 和 Svelte 之間共用。

### 步驟 9：建立完整的元件展示頁面

```svelte
<!-- src/routes/components/+page.svelte -->
<script lang="ts">
  import Button from "$lib/components/ui/Button.svelte";
  import Card from "$lib/components/ui/Card.svelte";
  import CardHeader from "$lib/components/ui/CardHeader.svelte";
  import CardTitle from "$lib/components/ui/CardTitle.svelte";
  import CardDescription from "$lib/components/ui/CardDescription.svelte";
  import CardContent from "$lib/components/ui/CardContent.svelte";
  import CardFooter from "$lib/components/ui/CardFooter.svelte";
  import Dialog from "$lib/components/ui/Dialog.svelte";
  import DialogTitle from "$lib/components/ui/DialogTitle.svelte";
  import DialogDescription from "$lib/components/ui/DialogDescription.svelte";
  import DialogFooter from "$lib/components/ui/DialogFooter.svelte";
  import Toggle from "$lib/components/ui/Toggle.svelte";

  let dialogOpen = $state(false);
  let darkMode = $state(false);

  const variants = ["primary", "secondary", "destructive", "outline", "ghost", "link"] as const;
  const sizes = ["sm", "md", "lg"] as const;
</script>

<div class="mx-auto max-w-4xl space-y-16 p-8">
  <h1 class="text-4xl font-bold">Svelte UI 元件展示</h1>

  <!-- Buttons -->
  <section class="space-y-4">
    <h2 class="text-2xl font-semibold">Button</h2>
    <div class="flex flex-wrap items-center gap-4">
      {#each variants as v}
        <Button variant={v}>{v}</Button>
      {/each}
    </div>
    <div class="flex flex-wrap items-center gap-4">
      {#each sizes as s}
        <Button size={s}>{s.toUpperCase()}</Button>
      {/each}
    </div>
    <div class="flex flex-wrap items-center gap-4">
      <Button disabled>Disabled</Button>
      <Button loading>Loading</Button>
    </div>
  </section>

  <!-- Cards -->
  <section class="space-y-4">
    <h2 class="text-2xl font-semibold">Card</h2>
    <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
      {#each ["default", "outline", "elevated"] as v}
        <Card variant={v}>
          <CardHeader>
            <CardTitle>{v}</CardTitle>
            <CardDescription>{v} 樣式的卡片。</CardDescription>
          </CardHeader>
          <CardContent>
            <p class="text-sm text-gray-600">卡片內容區域。</p>
          </CardContent>
        </Card>
      {/each}
    </div>
  </section>

  <!-- Toggle -->
  <section class="space-y-4">
    <h2 class="text-2xl font-semibold">Toggle</h2>
    <div class="flex items-center gap-4">
      <Toggle bind:checked={darkMode} label="深色模式" />
      <span class="text-sm text-gray-500">狀態：{darkMode ? "開啟" : "關閉"}</span>
    </div>
  </section>

  <!-- Dialog -->
  <section class="space-y-4">
    <h2 class="text-2xl font-semibold">Dialog</h2>
    <Button onclick={() => (dialogOpen = true)}>開啟 Dialog</Button>
    <Dialog open={dialogOpen} onclose={() => (dialogOpen = false)}>
      <DialogTitle>測試 Dialog</DialogTitle>
      <DialogDescription>這是 Svelte 版的 Dialog 元件。</DialogDescription>
      <DialogFooter>
        <Button variant="outline" onclick={() => (dialogOpen = false)}>取消</Button>
        <Button onclick={() => (dialogOpen = false)}>確認</Button>
      </DialogFooter>
    </Dialog>
  </section>
</div>
```

驗證：所有元件在展示頁面中正確渲染，互動功能正常。

### 步驟 10：React vs Svelte 整合模式比較總結

建立一個比較對照表：

| 面向 | React (Ch20) | Svelte (Ch21) |
|------|-------------|---------------|
| 條件式 class | `clsx({...})` | `class:name={cond}` 或 `cn(...)` |
| 元件變體 | `cva` + `VariantProps` | 原生 Record 映射或 `cva` |
| class 合併 | `cn()` = `clsx` + `twMerge` | 同上，工具函式可共用 |
| 動畫/Transition | Headless UI `<Transition>` | Svelte 內建 `transition:` |
| scoped styles | CSS Modules（較少用） | `<style>` 區塊（原生支援） |
| Server/Client 邊界 | `"use client"` directive | SvelteKit 的 `+page.server.ts` |
| Props 傳遞 class | `className` prop | `class` prop（Svelte 保留字處理） |
| 子內容 | `children: ReactNode` | `children: Snippet` + `{@render}` |
| 表單綁定 | `value` + `onChange` | `bind:value` |

驗證：能清楚說明各模式在兩個框架中的對應關係和差異。

## Hands-on Lab

### Foundation / 基礎練習

**任務：建立 Svelte Button 元件**

1. 建立 SvelteKit + Tailwind v4 專案。
2. 建立 `cn()` 工具函式。
3. 建立 Button.svelte，支援 3 種 variant 和 2 種 size。
4. 支援 `disabled` 和 `loading` 狀態。
5. 建立展示頁面。

**驗收清單：**
- [ ] `npm run dev` 無錯誤啟動。
- [ ] 3 variant x 2 size 組合正確渲染。
- [ ] `disabled` 狀態有半透明和禁用游標效果。
- [ ] `loading` 狀態顯示 spinner 動畫。
- [ ] 外部 `class="rounded-full"` 能覆蓋預設圓角。

### Advanced / 進階練習

**任務：建立 Card + Dialog 元件**

1. 建立 Card compound component（Card, CardHeader, CardTitle, CardContent, CardFooter）。
2. 建立 Dialog 元件，使用 Svelte 內建 `transition:fade` 和 `transition:scale`。
3. Dialog 支援 Esc 鍵關閉和點擊外部關閉。
4. 建立一個 Dashboard 頁面整合 Card 和 Dialog。

**驗收清單：**
- [ ] Card 支援 3 種 variant。
- [ ] Card 子元件可獨立使用。
- [ ] Dialog 有進場/退場動畫。
- [ ] Esc 鍵可關閉 Dialog。
- [ ] 點擊 backdrop 可關閉 Dialog。

### Challenge / 挑戰練習

**任務：建立與 Ch20 完全對等的 Svelte UI 元件庫**

1. 實作 Ch20 中所有元件的 Svelte 版本（Button, Card, Dialog, Badge, Input, Toggle）。
2. 使用 `class:` directive 和 `cn()` 混合模式。
3. 展示 `@apply` 在 scoped styles 中的合理使用場景。
4. 使用 cva 建立可跨框架共用的變體定義。
5. 建立完整的元件展示頁面。
6. 撰寫 React vs Svelte 的比較文件。

**驗收清單：**
- [ ] 6 個元件全部完成，TypeScript 無錯誤。
- [ ] 至少一個元件使用 `class:` directive 展示 Svelte 特色。
- [ ] ProseContent 元件正確示範 `@apply` 在 scoped styles 中的使用。
- [ ] `button-variants.ts` 變體定義可在 React 和 Svelte 間共用。
- [ ] 元件展示頁面可瀏覽所有元件的所有狀態。
- [ ] 能口頭說明 React 和 Svelte 整合模式的 3 個主要差異。

## Reference Solution

本章 Step-by-step 中的所有程式碼片段合在一起就是完整的 Reference Solution。關鍵檔案清單：

- `src/lib/utils.ts` — cn() 工具函式（步驟 1）
- `src/lib/components/ui/Button.svelte` — Button 元件（步驟 2）
- `src/lib/components/ui/Card.svelte` 及子元件 — Card compound component（步驟 3）
- `src/lib/components/ui/Dialog.svelte` 及子元件 — Dialog 元件 with Svelte transitions（步驟 4）
- `src/lib/components/ui/Toggle.svelte` — Toggle 元件，展示 class: directive（步驟 5）
- `src/lib/components/ProseContent.svelte` — @apply 合理使用範例（步驟 6）
- `src/lib/components/ui/AnimatedCard.svelte` — scoped styles 共存範例（步驟 7）
- `src/lib/components/ui/button-variants.ts` — 跨框架 cva 變體（步驟 8）
- `src/routes/components/+page.svelte` — 元件展示頁面（步驟 9）

所有程式碼都已在步驟中完整提供，可直接複製貼入 SvelteKit 專案使用。

## Common Pitfalls

### 1. v4 特有：Svelte scoped styles 中的 @apply 與 v4 @import 路徑

在 Tailwind v4 中，scoped `<style>` 中使用 `@apply` 時，確保全域 CSS 已透過 `@import "tailwindcss"` 正確載入，否則 `@apply` 的工具類無法解析。

```svelte
<!-- 正確：全域 CSS 已在 +layout.svelte 中引入 -->
<style>
  .content :global(h1) {
    @apply text-3xl font-bold; /* 這需要 Tailwind 已在全域載入 */
  }
</style>

<!-- 常見錯誤：忘記在 +layout.svelte 中引入 app.css -->
<!-- 導致 @apply 的工具類無法解析 -->
```

### 2. Svelte 5 的 class prop 命名衝突

在 Svelte 5 中，`class` 是 HTML 屬性名稱，但在 `$props()` 解構時需要特殊處理。

```svelte
<script lang="ts">
  // 錯誤：class 是 JavaScript 保留字
  // let { class } = $props();

  // 正確：使用重新命名
  let { class: className, ...rest } = $props();
</script>
```

### 3. class: directive 與 cn() 混用導致衝突

同時使用 `class:` directive 和 `cn()` 動態 class 時，可能導致同一屬性被設定兩次。

```svelte
<!-- 潛在問題：bg-blue-600 可能和 class: 中的背景色衝突 -->
<div
  class={cn("rounded-lg p-4", someClass)}
  class:bg-blue-600={isActive}
  class:bg-gray-200={!isActive}
>

<!-- 建議：統一使用 cn() 處理所有動態 class -->
<div
  class={cn(
    "rounded-lg p-4",
    isActive ? "bg-blue-600" : "bg-gray-200",
    someClass
  )}
>
```

### 4. 過度使用 @apply 抵銷 utility-first 優勢

```svelte
<!-- 不建議：大量使用 @apply -->
<style>
  .button {
    @apply inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium bg-blue-600 text-white hover:bg-blue-700;
  }
</style>
<button class="button">Click</button>

<!-- 建議：直接在模板中使用 Tailwind class -->
<button class="inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium bg-blue-600 text-white hover:bg-blue-700">
  Click
</button>
```

### 5. Svelte transition 與 Tailwind animation class 衝突

同時使用 Svelte 的 `transition:` directive 和 Tailwind 的 `animate-*` class 可能導致衝突。

```svelte
<!-- 潛在衝突：Svelte transition 和 Tailwind animate 同時控制動畫 -->
<div transition:scale class="animate-bounce">...</div>

<!-- 建議：選擇其中一種方案 -->
<!-- 方案 1：用 Svelte transition 處理進場/退場 -->
<div transition:scale>...</div>
<!-- 方案 2：用 Tailwind 處理持續性動畫 -->
<div class="animate-bounce">...</div>
```

## Checklist

- [ ] 能在 SvelteKit 專案中設定 Tailwind CSS v4。
- [ ] 能使用 `$props()` 正確接收 `class` prop 並用 `cn()` 合併。
- [ ] 能使用 `class:name={condition}` directive 進行條件式 class 切換。
- [ ] 理解何時使用 `@apply` 在 scoped styles 中，何時直接使用 Tailwind class。
- [ ] 能使用 Svelte 內建 `transition:` 建立 Dialog 的進場/退場動畫。
- [ ] 能建立 Svelte compound component（Card 及其子元件）。
- [ ] 能說明 React 和 Svelte 中 Tailwind 整合模式的主要差異。

## Further Reading (official links only)

- [Tailwind CSS with SvelteKit](https://tailwindcss.com/docs/installation/framework-guides/sveltekit)
- [Tailwind CSS - Reusing Styles](https://tailwindcss.com/docs/reusing-styles)
- [Tailwind CSS GitHub Repository](https://github.com/tailwindlabs/tailwindcss)
- [Svelte 5 - Runes](https://svelte.dev/docs/svelte/$state)
- [Svelte - class: directive](https://svelte.dev/docs/svelte/class)
- [Svelte - Transitions](https://svelte.dev/docs/svelte/transition)
- [SvelteKit - Routing](https://svelte.dev/docs/kit/routing)
