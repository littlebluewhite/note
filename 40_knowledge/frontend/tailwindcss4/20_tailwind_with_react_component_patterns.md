---
title: "Tailwind with React Component Patterns / Tailwind 與 React 元件模式"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "20"
level: advanced
stack: Tailwind CSS 4.1.x + React 19.2.x + Next.js 16
prerequisites: [19_performance_optimization_and_production_build]
---

# Tailwind with React Component Patterns / Tailwind 與 React 元件模式

## Goal

在前一章 [[19_performance_optimization_and_production_build]] 中，我們學會了如何最佳化 Tailwind CSS 的效能和生產建置。本章將把所有 Tailwind CSS 知識帶入 React 生態系，深入探討如何在 React 19 + Next.js 16 的環境中建立可維護、可重用的 Tailwind 元件模式。我們會涵蓋 `className` 的慣用模式、使用 `clsx` 進行條件式 class 管理、使用 `cva`（Class Variance Authority）建立元件變體系統、使用 `tailwind-merge` 處理 class 衝突與覆蓋、以及如何結合 Headless UI 打造無障礙元件。

React 元件天然就是 Tailwind 工具類的最佳封裝層。相較於在 CSS 中用 `@apply` 或 `@layer components` 來抽取重複樣式，在 React 中直接用元件封裝是更符合 React 思維的方式。本章將建立一套包含 Button、Card、Dialog 三個基礎元件的迷你設計系統。在下一章 [[21_tailwind_with_svelte_component_patterns]] 中，我們將以相同的元件規格在 Svelte 中實作對應版本，讓你能比較兩個框架中 Tailwind 整合模式的異同。

## Prerequisites

- 已完成第 19 章，理解 Tailwind CSS v4 效能最佳化。
- 熟悉 React 19 的基礎知識（元件、props、hooks）。
- 熟悉 TypeScript 基礎（type、interface、generics）。
- 了解 Next.js App Router 的基本結構（`app/` 目錄、Server/Client Components）。
- 已安裝 `clsx`、`tailwind-merge`、`class-variance-authority`（參考第 18 章）。

## Core Concepts

### 1. className Patterns in React / React 中的 className 模式

在 React 中使用 Tailwind 有多種 className 組織模式，選擇適合的模式對可維護性至關重要。

**何時使用直接內聯 className：**
- 元件只在一處使用，不需要重用。
- 樣式簡單，class 數量 < 10 個。
- 快速原型開發階段。

**何時使用元件封裝 className：**
- 相同的 class 組合在 3 處以上重複使用。
- 元件有多個視覺變體（variant）。
- 需要統一修改樣式時，只改一處。

**何時不建議的做法：**
- 過度抽象：為每個 `<div>` 都建立封裝元件。
- 使用 `@apply` 在 CSS 中抽取 React 元件的樣式（失去 colocation 優勢）。

### 2. Conditional Classes with clsx / 使用 clsx 的條件式 class

`clsx` 提供了簡潔的 API 來組合條件式 class 名稱。

**何時使用 clsx：**
- 元件有基於 props 的條件式樣式。
- 需要根據狀態（disabled、loading、active）切換樣式。
- 需要合併多個 class 來源（基礎 + 變體 + 外部傳入）。

**何時不使用 clsx：**
- 只有簡單的二選一條件，用三元運算子更直接。
- 沒有條件式邏輯，class 是固定的。

### 3. Class Variance Authority (cva) / 元件變體系統

`cva` 專為 Tailwind 元件變體設計，提供類型安全的 variant 定義和組合。

**何時使用 cva：**
- 元件有 2 個以上的 variant 維度（如 variant x size x color）。
- 需要 TypeScript 自動推導 variant props 型別。
- 團隊需要標準化元件 API。
- 建立設計系統或元件庫。

**何時不使用 cva：**
- 元件沒有 variant 概念，樣式固定。
- 只有一個 variant 維度（如只有 size），clsx 即可處理。
- 追求最小化依賴的輕量專案。

### 4. "use client" Boundary Considerations / "use client" 邊界考量

在 Next.js App Router 中，Server Components 和 Client Components 的邊界影響 Tailwind 的使用方式。

**何時需要 "use client"：**
- 元件使用 `useState`、`useEffect` 等 hooks。
- 元件有事件處理（onClick、onChange 等）。
- 元件使用 Headless UI 等需要 JavaScript 互動的庫。

**何時保持 Server Component：**
- 純展示性元件（Card、Badge、Typography）。
- 不需要互動的靜態 UI。
- 數據獲取和渲染在伺服器端完成。
- 只使用 Tailwind class 做靜態樣式。

## Step-by-step

### 步驟 1：建立專案和工具函式

確認 Next.js 16 + Tailwind v4 專案已建立，並設定核心工具函式：

```tsx
// src/lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * 合併 Tailwind CSS class 名稱，自動處理衝突。
 * 結合 clsx（條件式組合）和 tailwind-merge（衝突解決）。
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

驗證：`cn("bg-red-500", "bg-blue-500")` 回傳 `"bg-blue-500"`，後者正確覆蓋前者。

### 步驟 2：建立 Button 元件（使用 cva）

```tsx
// src/components/ui/Button.tsx
"use client";

import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  // 基礎樣式（所有變體共用）
  [
    "inline-flex items-center justify-center gap-2",
    "rounded-lg font-medium",
    "transition-colors duration-200",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
    "disabled:pointer-events-none disabled:opacity-50",
  ],
  {
    variants: {
      variant: {
        primary:
          "bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-500",
        secondary:
          "bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-400",
        destructive:
          "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500",
        outline:
          "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus-visible:ring-gray-400",
        ghost:
          "text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-400",
        link:
          "text-blue-600 underline-offset-4 hover:underline focus-visible:ring-blue-500",
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

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & {
    loading?: boolean;
  };

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  function Button({ className, variant, size, loading, disabled, children, ...props }, ref) {
    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size }), className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg
            className="h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

export { buttonVariants };
```

驗證：`<Button variant="primary" size="lg">Click</Button>` 渲染正確的大型藍色按鈕。

### 步驟 3：建立 Card 元件（Server Component）

Card 是純展示性元件，不需要 "use client"：

```tsx
// src/components/ui/Card.tsx
import { type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

// ---- Card Root ----
type CardProps = HTMLAttributes<HTMLDivElement> & {
  variant?: "default" | "outline" | "elevated";
};

export function Card({ className, variant = "default", children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl bg-white text-gray-950",
        {
          "border border-gray-200 shadow-sm": variant === "default",
          "border-2 border-gray-300": variant === "outline",
          "shadow-lg shadow-gray-200/50": variant === "elevated",
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

// ---- Card Header ----
type CardHeaderProps = HTMLAttributes<HTMLDivElement>;

export function CardHeader({ className, children, ...props }: CardHeaderProps) {
  return (
    <div className={cn("flex flex-col gap-1.5 p-6 pb-0", className)} {...props}>
      {children}
    </div>
  );
}

// ---- Card Title ----
type CardTitleProps = HTMLAttributes<HTMLHeadingElement>;

export function CardTitle({ className, children, ...props }: CardTitleProps) {
  return (
    <h3 className={cn("text-xl font-semibold leading-tight tracking-tight", className)} {...props}>
      {children}
    </h3>
  );
}

// ---- Card Description ----
type CardDescriptionProps = HTMLAttributes<HTMLParagraphElement>;

export function CardDescription({ className, children, ...props }: CardDescriptionProps) {
  return (
    <p className={cn("text-sm text-gray-500", className)} {...props}>
      {children}
    </p>
  );
}

// ---- Card Content ----
type CardContentProps = HTMLAttributes<HTMLDivElement>;

export function CardContent({ className, children, ...props }: CardContentProps) {
  return (
    <div className={cn("p-6", className)} {...props}>
      {children}
    </div>
  );
}

// ---- Card Footer ----
type CardFooterProps = HTMLAttributes<HTMLDivElement>;

export function CardFooter({ className, children, ...props }: CardFooterProps) {
  return (
    <div className={cn("flex items-center gap-2 p-6 pt-0", className)} {...props}>
      {children}
    </div>
  );
}
```

使用方式：

```tsx
// app/page.tsx (Server Component)
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function HomePage() {
  return (
    <Card variant="elevated" className="max-w-md mx-auto mt-12">
      <CardHeader>
        <CardTitle>專案統計</CardTitle>
        <CardDescription>上週的開發進度摘要。</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-2xl font-bold">128</p>
            <p className="text-sm text-gray-500">commits</p>
          </div>
          <div>
            <p className="text-2xl font-bold">24</p>
            <p className="text-sm text-gray-500">PRs merged</p>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button variant="outline" size="sm">查看詳情</Button>
      </CardFooter>
    </Card>
  );
}
```

驗證：Card 在伺服器端渲染，HTML 原始碼中不包含 JavaScript bundle 引用。

### 步驟 4：建立 Dialog 元件（Client Component + Headless UI）

安裝 Headless UI：

```bash
npm install @headlessui/react
```

```tsx
// src/components/ui/Dialog.tsx
"use client";

import {
  Dialog as HeadlessDialog,
  DialogPanel,
  DialogTitle,
  Transition,
  TransitionChild,
} from "@headlessui/react";
import { Fragment, type ReactNode } from "react";
import { cn } from "@/lib/utils";

type DialogProps = {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  className?: string;
};

export function Dialog({ open, onClose, children, className }: DialogProps) {
  return (
    <Transition show={open} as={Fragment}>
      <HeadlessDialog onClose={onClose} className="relative z-50">
        {/* Backdrop */}
        <TransitionChild
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm" />
        </TransitionChild>

        {/* Panel Container */}
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <TransitionChild
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <DialogPanel
              className={cn(
                "w-full max-w-md rounded-2xl bg-white p-6 shadow-xl",
                "ring-1 ring-gray-200",
                className
              )}
            >
              {children}
            </DialogPanel>
          </TransitionChild>
        </div>
      </HeadlessDialog>
    </Transition>
  );
}

// ---- Dialog Title ----
type DialogTitleComponentProps = {
  children: ReactNode;
  className?: string;
};

export function DialogTitleComponent({ children, className }: DialogTitleComponentProps) {
  return (
    <DialogTitle className={cn("text-lg font-semibold text-gray-900", className)}>
      {children}
    </DialogTitle>
  );
}

// ---- Dialog Description ----
type DialogDescriptionProps = {
  children: ReactNode;
  className?: string;
};

export function DialogDescription({ children, className }: DialogDescriptionProps) {
  return (
    <p className={cn("mt-2 text-sm text-gray-500", className)}>
      {children}
    </p>
  );
}

// ---- Dialog Footer ----
type DialogFooterProps = {
  children: ReactNode;
  className?: string;
};

export function DialogFooter({ children, className }: DialogFooterProps) {
  return (
    <div className={cn("mt-6 flex justify-end gap-3", className)}>
      {children}
    </div>
  );
}
```

使用方式：

```tsx
// app/demo/page.tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import {
  Dialog,
  DialogTitleComponent,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/Dialog";

export default function DemoPage() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <Button onClick={() => setIsOpen(true)}>開啟 Dialog</Button>

      <Dialog open={isOpen} onClose={() => setIsOpen(false)}>
        <DialogTitleComponent>確認刪除</DialogTitleComponent>
        <DialogDescription>
          確定要刪除這個項目嗎？此操作無法復原。
        </DialogDescription>
        <DialogFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            取消
          </Button>
          <Button variant="destructive" onClick={() => setIsOpen(false)}>
            刪除
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
}
```

驗證：Dialog 開啟時有 backdrop blur 和進場動畫，按 Esc 或點擊外部可關閉。

### 步驟 5：實作 Tailwind Merge 進階配置

處理自訂工具類的合併衝突：

```tsx
// src/lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { extendTailwindMerge } from "tailwind-merge";

const twMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      // 自訂工具類群組（來自第 17 章）
      "text-shadow": [
        { "text-shadow": ["sm", "md", "lg", "xl", "none"] },
      ],
      glass: [
        { glass: ["sm", "md", "lg", "none"] },
      ],
    },
  },
});

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

驗證：`cn("text-shadow-sm", "text-shadow-lg")` 回傳 `"text-shadow-lg"`。

### 步驟 6：建立 Badge 元件（展示 clsx 條件式模式）

```tsx
// src/components/ui/Badge.tsx
import { type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const variantStyles = {
  default: "bg-gray-100 text-gray-800 border-gray-200",
  primary: "bg-blue-100 text-blue-800 border-blue-200",
  success: "bg-green-100 text-green-800 border-green-200",
  warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
  error: "bg-red-100 text-red-800 border-red-200",
} as const;

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  variant?: keyof typeof variantStyles;
  removable?: boolean;
  onRemove?: () => void;
};

export function Badge({
  className,
  variant = "default",
  removable = false,
  onRemove,
  children,
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
      {removable && (
        <button
          type="button"
          onClick={onRemove}
          className="ml-0.5 inline-flex h-3.5 w-3.5 items-center justify-center rounded-full
                     hover:bg-black/10 focus:outline-none"
          aria-label="移除"
        >
          <svg className="h-2.5 w-2.5" viewBox="0 0 10 10" fill="currentColor">
            <path d="M2.5 2.5l5 5M7.5 2.5l-5 5" stroke="currentColor" strokeWidth="1.5" fill="none" />
          </svg>
        </button>
      )}
    </span>
  );
}
```

驗證：不同 variant 的 Badge 顯示對應色系。removable Badge 有可點擊的 X 按鈕。

### 步驟 7：建立 Input 元件（表單元件模式）

```tsx
// src/components/ui/Input.tsx
"use client";

import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
  helperText?: string;
};

export const Input = forwardRef<HTMLInputElement, InputProps>(
  function Input({ className, label, error, helperText, id, ...props }, ref) {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="space-y-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            "block w-full rounded-lg border px-3 py-2 text-sm",
            "transition-colors duration-200",
            "placeholder:text-gray-400",
            "focus:outline-none focus:ring-2 focus:ring-offset-0",
            error
              ? "border-red-300 text-red-900 focus:border-red-500 focus:ring-red-200"
              : "border-gray-300 text-gray-900 focus:border-blue-500 focus:ring-blue-200",
            "disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500",
            className
          )}
          aria-invalid={error ? "true" : undefined}
          aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
          {...props}
        />
        {error && (
          <p id={`${inputId}-error`} className="text-sm text-red-600">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p id={`${inputId}-helper`} className="text-sm text-gray-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);
```

驗證：正常狀態有灰色邊框，error 狀態有紅色邊框和錯誤訊息。Focus 時有 ring。

### 步驟 8：Server Component vs Client Component 邊界實踐

展示如何正確劃分 Server/Client Component 邊界：

```tsx
// app/dashboard/page.tsx (Server Component)
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { DashboardActions } from "./DashboardActions"; // Client Component

// 模擬伺服器端數據獲取
async function getStats() {
  return {
    users: 1234,
    revenue: 56789,
    orders: 42,
    status: "healthy" as const,
  };
}

export default async function DashboardPage() {
  const stats = await getStats();

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <Badge variant={stats.status === "healthy" ? "success" : "error"}>
          {stats.status}
        </Badge>
      </div>

      {/* 靜態展示：Server Component（不包含 JS） */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>使用者</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.users.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>營收</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">${stats.revenue.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>訂單</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.orders}</p>
          </CardContent>
        </Card>
      </div>

      {/* 互動功能：Client Component（包含 JS） */}
      <DashboardActions />
    </div>
  );
}
```

```tsx
// app/dashboard/DashboardActions.tsx (Client Component)
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Dialog, DialogTitleComponent, DialogDescription, DialogFooter } from "@/components/ui/Dialog";

export function DashboardActions() {
  const [showExport, setShowExport] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  async function handleExport() {
    setIsExporting(true);
    // 模擬匯出
    await new Promise((r) => setTimeout(r, 2000));
    setIsExporting(false);
    setShowExport(false);
  }

  return (
    <>
      <div className="flex gap-4">
        <Button onClick={() => setShowExport(true)}>匯出報告</Button>
        <Button variant="outline">篩選條件</Button>
      </div>

      <Dialog open={showExport} onClose={() => setShowExport(false)}>
        <DialogTitleComponent>匯出報告</DialogTitleComponent>
        <DialogDescription>
          系統將匯出過去 30 天的完整報告為 CSV 檔案。
        </DialogDescription>
        <DialogFooter>
          <Button variant="outline" onClick={() => setShowExport(false)}>
            取消
          </Button>
          <Button loading={isExporting} onClick={handleExport}>
            {isExporting ? "匯出中..." : "開始匯出"}
          </Button>
        </DialogFooter>
      </Dialog>
    </>
  );
}
```

驗證：Dashboard 頁面的卡片統計資料不包含在 client JS bundle 中。只有 DashboardActions 包含互動 JS。

### 步驟 9：建立元件展示頁面

```tsx
// app/components/page.tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Dialog, DialogTitleComponent, DialogDescription, DialogFooter } from "@/components/ui/Dialog";

export default function ComponentShowcase() {
  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <div className="mx-auto max-w-4xl space-y-16 p-8">
      <h1 className="text-4xl font-bold">UI 元件展示</h1>

      {/* Buttons */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Button</h2>
        <div className="flex flex-wrap items-center gap-4">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="link">Link</Button>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <Button disabled>Disabled</Button>
          <Button loading>Loading</Button>
        </div>
      </section>

      {/* Cards */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Card</h2>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <Card variant="default">
            <CardHeader>
              <CardTitle>Default</CardTitle>
              <CardDescription>預設卡片樣式。</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">卡片內容區域。</p>
            </CardContent>
          </Card>
          <Card variant="outline">
            <CardHeader>
              <CardTitle>Outline</CardTitle>
              <CardDescription>外框卡片樣式。</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">卡片內容區域。</p>
            </CardContent>
          </Card>
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Elevated</CardTitle>
              <CardDescription>浮起卡片樣式。</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">卡片內容區域。</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Badges */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Badge</h2>
        <div className="flex flex-wrap gap-3">
          <Badge>Default</Badge>
          <Badge variant="primary">Primary</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="error">Error</Badge>
          <Badge variant="primary" removable onRemove={() => alert("Removed!")}>
            Removable
          </Badge>
        </div>
      </section>

      {/* Inputs */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Input</h2>
        <div className="max-w-md space-y-4">
          <Input label="姓名" placeholder="請輸入姓名" />
          <Input label="電子郵件" type="email" placeholder="you@example.com" helperText="我們不會分享你的電子郵件。" />
          <Input label="密碼" type="password" error="密碼至少需要 8 個字元。" />
          <Input label="備註" disabled placeholder="此欄位已停用" />
        </div>
      </section>

      {/* Dialog */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Dialog</h2>
        <Button onClick={() => setDialogOpen(true)}>開啟 Dialog</Button>
        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
          <DialogTitleComponent>標題</DialogTitleComponent>
          <DialogDescription>這是一個 Dialog 元件的展示範例。</DialogDescription>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>關閉</Button>
            <Button onClick={() => setDialogOpen(false)}>確認</Button>
          </DialogFooter>
        </Dialog>
      </section>
    </div>
  );
}
```

驗證：所有元件在展示頁面中正確渲染，互動功能正常。

### 步驟 10：建立元件匯出 barrel 檔案

```tsx
// src/components/ui/index.ts
export { Button, buttonVariants, type ButtonProps } from "./Button";
export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "./Card";
export { Badge } from "./Badge";
export { Input } from "./Input";
export {
  Dialog,
  DialogTitleComponent,
  DialogDescription,
  DialogFooter,
} from "./Dialog";
```

使用方式：

```tsx
// 從 barrel 檔案統一引入
import { Button, Card, CardContent, Badge } from "@/components/ui";
```

驗證：從 barrel 檔案引入的元件與直接引入的行為一致。Next.js 的 tree-shaking 正確排除未使用的元件。

## Hands-on Lab

### Foundation / 基礎練習

**任務：建立 Button 元件**

1. 建立 `src/lib/utils.ts`，實作 `cn()` 函式。
2. 使用 `cva` 建立 Button 元件，支援 3 種 variant 和 2 種 size。
3. 支援 `disabled` 狀態。
4. 接受外部 `className` 並正確合併。
5. 建立展示頁面顯示所有組合。

**驗收清單：**
- [ ] `cn()` 正確解決 Tailwind class 衝突。
- [ ] 3 variant x 2 size 的組合全部正確渲染。
- [ ] `disabled` 狀態有視覺回饋（半透明 + 禁用游標）。
- [ ] 外部 `className="rounded-full"` 能覆蓋預設 `rounded-lg`。
- [ ] TypeScript 型別完整，variant prop 有自動補全。

### Advanced / 進階練習

**任務：建立 Card 元件系統**

1. 建立 Card、CardHeader、CardTitle、CardDescription、CardContent、CardFooter 六個子元件。
2. Card 支援 3 種 variant（default、outline、elevated）。
3. Card 是 Server Component（不使用 "use client"）。
4. 所有子元件都接受 `className` prop。
5. 建立一個 Dashboard 頁面，使用 Card 展示統計數據。

**驗收清單：**
- [ ] Card 的 6 個子元件都可獨立使用。
- [ ] 3 種 variant 有明顯的視覺區分。
- [ ] Card 作為 Server Component 不包含在 client bundle 中。
- [ ] `className` prop 能正確覆蓋預設樣式。
- [ ] Dashboard 頁面在 Server Side 正確渲染。

### Challenge / 挑戰練習

**任務：建立包含 Button、Card、Dialog 的完整 UI 元件庫**

1. 建立 Button（6 variant, 4 size, loading 狀態）。
2. 建立 Card（3 variant, compound component 模式）。
3. 建立 Dialog（使用 Headless UI，含進場/退場動畫）。
4. 建立 Badge（5 variant, removable 模式）。
5. 建立 Input（label, error, helperText, disabled 狀態）。
6. 正確劃分 Server/Client Component 邊界。
7. 建立完整的元件展示頁面。
8. 建立 barrel 匯出檔案。

**驗收清單：**
- [ ] 5 個元件全部完成且 TypeScript 無錯誤。
- [ ] Dialog 有進場動畫（scale + opacity）和 backdrop blur。
- [ ] Server Component（Card, Badge）不包含在 client JS bundle。
- [ ] Client Component（Button, Dialog, Input）有 "use client" 標記。
- [ ] 元件展示頁面可瀏覽所有元件的所有狀態。
- [ ] `cn()` 正確處理自訂工具類（text-shadow, glass）。
- [ ] barrel 檔案支援 tree-shaking。

## Reference Solution

本章 Step-by-step 中的所有程式碼片段合在一起就是完整的 Reference Solution。關鍵檔案清單：

- `src/lib/utils.ts` — cn() 工具函式（步驟 1 + 步驟 5）
- `src/components/ui/Button.tsx` — Button 元件（步驟 2）
- `src/components/ui/Card.tsx` — Card compound component（步驟 3）
- `src/components/ui/Dialog.tsx` — Dialog 元件 with Headless UI（步驟 4）
- `src/components/ui/Badge.tsx` — Badge 元件（步驟 6）
- `src/components/ui/Input.tsx` — Input 表單元件（步驟 7）
- `src/components/ui/index.ts` — barrel 匯出（步驟 10）
- `app/dashboard/page.tsx` — Server Component 範例（步驟 8）
- `app/dashboard/DashboardActions.tsx` — Client Component 範例（步驟 8）
- `app/components/page.tsx` — 元件展示頁面（步驟 9）

所有程式碼都已在步驟中完整提供，可直接複製貼入 Next.js 16 專案使用。

## Common Pitfalls

### 1. v4 特有：在 Next.js 中混淆 @import "tailwindcss" 的位置

在 Next.js 16 + Tailwind v4 中，CSS 的入口點配置與 v3 不同。

```css
/* 正確：app/globals.css (Next.js 16 with Tailwind v4) */
@import "tailwindcss";

/* 錯誤：仍使用 v3 的 @tailwind 指令 */
/* @tailwind base; */
/* @tailwind components; */
/* @tailwind utilities; */
```

### 2. 在 Server Component 中使用 useState/onClick

Server Component 不能有互動邏輯。如果 Tailwind class 中包含 `hover:` 等 CSS 偽類，這在 Server Component 中完全沒問題（因為是純 CSS）。但 `onClick` 等事件處理器需要 Client Component。

```tsx
// 錯誤：Server Component 中使用 onClick
export default function Page() {
  return <button onClick={() => alert("hi")} className="hover:bg-blue-600">Click</button>;
  // hover: 可以用，但 onClick 會報錯
}

// 正確：分離到 Client Component
// InteractiveButton.tsx
"use client";
export function InteractiveButton() {
  return <button onClick={() => alert("hi")} className="hover:bg-blue-600">Click</button>;
}
```

### 3. tailwind-merge 不認識自訂 class

使用 `@utility` 定義的自訂工具類不會被 `tailwind-merge` 預設識別，需要擴展配置（見步驟 5）。

```tsx
// 問題：兩個自訂 class 都保留，導致衝突
cn("glass-sm", "glass-lg"); // "glass-sm glass-lg"（兩者都保留）

// 解法：擴展 tailwind-merge
const twMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      glass: [{ glass: ["sm", "md", "lg", "none"] }],
    },
  },
});
```

### 4. cva 中遺漏 defaultVariants 導致無樣式

```tsx
// 問題：不傳 variant 時沒有任何 variant 樣式
<Button /> // 只有基礎樣式，無 variant 色彩

// 解法：始終設定 defaultVariants
const buttonVariants = cva("...", {
  variants: { variant: { primary: "...", secondary: "..." } },
  defaultVariants: { variant: "primary" }, // 確保預設有樣式
});
```

### 5. barrel 檔案導致 Server Component 被拉入 client bundle

如果 barrel 檔案混合匯出 Server 和 Client Component，可能導致 Server Component 被意外包含在 client bundle 中。

```tsx
// 潛在問題：Dialog (client) 和 Card (server) 在同一個 barrel 中
// 如果 Next.js tree-shaking 不完善，可能影響 bundle 大小

// 解法 1：確保 Next.js 版本支援 barrel 檔案 tree-shaking
// 解法 2：分開 client 和 server 的 barrel 檔案
// src/components/ui/server.ts
export { Card, CardHeader, ... } from "./Card";
export { Badge } from "./Badge";

// src/components/ui/client.ts
export { Button } from "./Button";
export { Dialog, ... } from "./Dialog";
```

## Checklist

- [ ] 能建立 `cn()` 工具函式（clsx + tailwind-merge）。
- [ ] 能使用 `cva` 定義 Button 元件的 variant + size 系統。
- [ ] 能建立 compound component 模式的 Card 元件。
- [ ] 能使用 Headless UI + Tailwind 建立無障礙的 Dialog 元件。
- [ ] 正確區分 Server Component 和 Client Component 的使用場景。
- [ ] 能使用 `extendTailwindMerge` 處理自訂工具類的合併衝突。
- [ ] 能建立元件展示頁面驗證所有元件狀態。

## Further Reading (official links only)

- [Tailwind CSS - Reusing Styles](https://tailwindcss.com/docs/reusing-styles)
- [Tailwind CSS - Adding Custom Styles](https://tailwindcss.com/docs/adding-custom-styles)
- [Tailwind CSS with Next.js](https://tailwindcss.com/docs/installation/framework-guides/nextjs)
- [Tailwind CSS GitHub Repository](https://github.com/tailwindlabs/tailwindcss)
- [React - Server Components](https://react.dev/reference/rsc/server-components)
- [React - forwardRef](https://react.dev/reference/react/forwardRef)
- [React - Reusing Logic with Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)
