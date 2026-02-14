---
title: "Internationalization / 國際化"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "24"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [14_advanced_routing_and_hooks]
---
# Internationalization / 國際化

## Goal

學會在 SvelteKit 應用中實作完整的國際化方案，包含 locale-based 路由、型別安全的翻譯管理、日期/數字格式化，以及 SEO 最佳化。

國際化（i18n）讓應用能服務不同語言和地區的使用者。SvelteKit 的路由系統天然適合 locale-based URL（如 `/en/about`、`/zh/about`），搭配 hooks 可以自動偵測使用者語言偏好。本章將從翻譯檔案管理到 SEO meta 標籤，建立一套完整且型別安全的 i18n 方案。

- 銜接上一章：Ch14 學會了進階路由與 hooks（params matcher、handle hook、layout data），國際化的 locale routing 正是建立在這些知識之上。Ch23 學會了無障礙模式，i18n 也是 a11y 的重要面向（`<html lang="...">`）。
- 下一章預告：Ch25 將學習進階 TypeScript 模式，進一步強化型別安全。

## Prerequisites

- 已完成 Ch14（Advanced Routing and Hooks），理解 SvelteKit 的 params matcher、`handle` hook、layout data。
- 能建立 `+layout.ts`、`+layout.server.ts`、`+page.ts` 檔案並理解 `load` 函式。
- `svelte5-lab` 專案可正常執行 `npm run dev`。
- 對 URL 路由結構有基本認識（如 `/[lang]/about`）。

## Core Concepts

### 1. Locale-based Routing — 以語系為基礎的路由

SvelteKit 的檔案系統路由天然支援 locale-based URL 結構。透過 `[lang]` 動態參數搭配 params matcher，可以限制合法的語系值並在所有頁面中取得目前語系。

路由結構：

```
src/routes/
├── [lang=lang]/           ← params matcher 限制合法語系
│   ├── +layout.ts         ← 傳遞 lang 給所有頁面
│   ├── +layout.svelte     ← 共用 layout
│   ├── +page.svelte       ← 首頁 /en 或 /zh
│   ├── about/
│   │   └── +page.svelte   ← /en/about 或 /zh/about
│   └── contact/
│       └── +page.svelte   ← /en/contact 或 /zh/contact
└── +page.server.ts        ← 根路徑重導到預設語系
```

Params matcher 限制合法語系值：

```ts
// src/params/lang.ts
import type { ParamMatcher } from '@sveltejs/kit';

const supportedLocales = ['en', 'zh'] as const;
export type Locale = (typeof supportedLocales)[number];

export const match: ParamMatcher = (param) => {
  return supportedLocales.includes(param as Locale);
};
```

根路徑重導到預設語系：

```ts
// src/routes/+page.server.ts
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ request }) => {
  const acceptLanguage = request.headers.get('accept-language') ?? '';
  const prefersChinese = acceptLanguage.includes('zh');
  const locale = prefersChinese ? 'zh' : 'en';

  redirect(307, `/${locale}`);
};
```

Layout data 傳遞 lang 給所有頁面：

```ts
// src/routes/[lang=lang]/+layout.ts
import type { LayoutLoad } from './$types';
import type { Locale } from '../../params/lang';

export const load: LayoutLoad = async ({ params }) => {
  const lang = params.lang as Locale;

  return { lang };
};
```

- **何時用**：多語系的公開網站（SEO 重要）、每個語系需要獨立的 URL（如 `/en/about` vs `/zh/about`）以便搜尋引擎索引和分享連結。
- **何時不用**：純內部工具（只有一種語言的使用者）、或語系切換不需要反映在 URL 上的應用（如純前端設定偏好）。

### 2. 翻譯管理 — Type-safe Translation System

建立一套型別安全的翻譯系統，確保所有翻譯鍵都存在且型別正確。從 JSON 翻譯檔案到型別推導的翻譯函式。

翻譯檔案結構：

```json
// src/lib/i18n/en.json
{
  "common": {
    "appName": "My App",
    "loading": "Loading...",
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete"
  },
  "nav": {
    "home": "Home",
    "about": "About",
    "contact": "Contact"
  },
  "auth": {
    "login": "Login",
    "logout": "Logout",
    "register": "Register"
  },
  "errors": {
    "required": "{field} is required",
    "minLength": "{field} must be at least {min} characters",
    "notFound": "Page not found"
  }
}
```

```json
// src/lib/i18n/zh.json
{
  "common": {
    "appName": "我的應用",
    "loading": "載入中...",
    "save": "儲存",
    "cancel": "取消",
    "delete": "刪除"
  },
  "nav": {
    "home": "首頁",
    "about": "關於",
    "contact": "聯絡我們"
  },
  "auth": {
    "login": "登入",
    "logout": "登出",
    "register": "註冊"
  },
  "errors": {
    "required": "{field} 為必填",
    "minLength": "{field} 至少需要 {min} 個字元",
    "notFound": "找不到頁面"
  }
}
```

型別安全的翻譯函式：

```ts
// src/lib/i18n/index.ts
import en from './en.json';
import zh from './zh.json';
import type { Locale } from '../../params/lang';

// 翻譯檔案映射
const translations: Record<Locale, typeof en> = { en, zh };

// 支援 dot-notation 的鍵路徑型別
type NestedKeyOf<T> = T extends object
  ? {
      [K in keyof T & string]: T[K] extends object
        ? `${K}.${NestedKeyOf<T[K]>}`
        : K;
    }[keyof T & string]
  : never;

type TranslationKey = NestedKeyOf<typeof en>;

// 根據 dot-notation 取值
function getNestedValue(obj: Record<string, unknown>, path: string): string {
  const keys = path.split('.');
  let current: unknown = obj;

  for (const key of keys) {
    if (current === null || current === undefined) return path;
    current = (current as Record<string, unknown>)[key];
  }

  return typeof current === 'string' ? current : path;
}

// 插值：將 {field}、{min} 等佔位符替換為實際值
function interpolate(
  template: string,
  params?: Record<string, string | number>
): string {
  if (!params) return template;

  return Object.entries(params).reduce(
    (result, [key, value]) => result.replace(new RegExp(`\\{${key}\\}`, 'g'), String(value)),
    template
  );
}

// 建立翻譯函式
export function createTranslator(locale: Locale) {
  const dict = translations[locale];

  return function t(
    key: TranslationKey,
    params?: Record<string, string | number>
  ): string {
    const template = getNestedValue(dict as Record<string, unknown>, key);
    return interpolate(template, params);
  };
}

// 取得所有支援的語系
export function getSupportedLocales(): Locale[] {
  return ['en', 'zh'];
}

// 預設語系
export const defaultLocale: Locale = 'en';
```

在元件中使用：

```svelte
<script lang="ts">
  import { createTranslator } from '$lib/i18n';
  import type { Locale } from '../../params/lang';

  let { lang }: { lang: Locale } = $props();

  let t = $derived(createTranslator(lang));
</script>

<h1>{t('common.appName')}</h1>
<p>{t('errors.required', { field: 'Email' })}</p>
```

替代方案如 paraglide-js 提供編譯時期的型別安全與 tree-shaking，適合大型專案。本章的手動方案適合中小型專案或學習 i18n 原理。

- **何時用**：任何需要多語系支援的應用。型別安全的翻譯系統能在編譯時期捕捉缺少的翻譯鍵，避免上線後才發現未翻譯的文字。
- **何時不用**：單一語言的應用、或已經使用 paraglide-js 等成熟 i18n 框架的專案不需要自己實作翻譯系統。

### 3. 日期/數字/貨幣格式化 — Locale-aware Formatting

`Intl` API 是瀏覽器原生的國際化格式化工具，能根據語系自動調整日期、數字、貨幣的顯示格式。封裝為 Svelte helper 函式方便在元件中使用。

```ts
// src/lib/i18n/format.ts
import type { Locale } from '../../params/lang';

// 語系到 BCP 47 tag 的映射
const localeMap: Record<Locale, string> = {
  en: 'en-US',
  zh: 'zh-TW',
};

// 日期格式化
export function formatDate(
  date: Date,
  locale: Locale,
  options?: Intl.DateTimeFormatOptions
): string {
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options,
  };

  return new Intl.DateTimeFormat(localeMap[locale], defaultOptions).format(date);
}

// 相對時間格式化（如「3 天前」、「in 2 hours」）
export function formatRelativeTime(
  date: Date,
  locale: Locale
): string {
  const now = Date.now();
  const diffMs = date.getTime() - now;
  const diffSeconds = Math.round(diffMs / 1000);
  const diffMinutes = Math.round(diffSeconds / 60);
  const diffHours = Math.round(diffMinutes / 60);
  const diffDays = Math.round(diffHours / 24);

  const rtf = new Intl.RelativeTimeFormat(localeMap[locale], { numeric: 'auto' });

  if (Math.abs(diffDays) >= 1) return rtf.format(diffDays, 'day');
  if (Math.abs(diffHours) >= 1) return rtf.format(diffHours, 'hour');
  if (Math.abs(diffMinutes) >= 1) return rtf.format(diffMinutes, 'minute');
  return rtf.format(diffSeconds, 'second');
}

// 數字格式化
export function formatNumber(
  value: number,
  locale: Locale,
  options?: Intl.NumberFormatOptions
): string {
  return new Intl.NumberFormat(localeMap[locale], options).format(value);
}

// 貨幣格式化
export function formatCurrency(
  value: number,
  locale: Locale,
  currency: string = locale === 'zh' ? 'TWD' : 'USD'
): string {
  return new Intl.NumberFormat(localeMap[locale], {
    style: 'currency',
    currency,
  }).format(value);
}
```

在元件中使用：

```svelte
<script lang="ts">
  import { formatDate, formatCurrency, formatNumber } from '$lib/i18n/format';
  import type { Locale } from '../../params/lang';

  let { lang }: { lang: Locale } = $props();

  const now = new Date();
  const price = 1234.56;
  const count = 1000000;
</script>

<p>Date: {formatDate(now, lang)}</p>
<!-- en: "February 14, 2026" / zh: "2026年2月14日" -->

<p>Price: {formatCurrency(price, lang)}</p>
<!-- en: "$1,234.56" / zh: "NT$1,234.56" -->

<p>Count: {formatNumber(count, lang)}</p>
<!-- en: "1,000,000" / zh: "1,000,000" -->
```

- **何時用**：所有需要顯示日期、數字、貨幣的多語系應用。`Intl` API 是標準化的瀏覽器 API，不需要額外安裝套件。
- **何時不用**：如果應用只支援單一語系且格式固定，可以直接使用固定格式的 helper 函式，不需要 `Intl` API 的動態切換能力。

### 4. Language Switcher Component — 語言切換元件

讓使用者能夠手動切換語言，並透過 cookie 記住偏好。搭配 SEO 必要的 `<link rel="alternate">` 和 `<html lang="...">` 標籤。

```svelte
<!-- src/lib/components/LanguageSwitcher.svelte -->
<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { getSupportedLocales } from '$lib/i18n';
  import type { Locale } from '../../params/lang';

  interface Props {
    currentLocale: Locale;
  }

  let { currentLocale }: Props = $props();

  const localeLabels: Record<Locale, string> = {
    en: 'English',
    zh: '中文',
  };

  const locales = getSupportedLocales();

  async function switchLocale(newLocale: Locale) {
    if (newLocale === currentLocale) return;

    // 設定 cookie 記住偏好
    document.cookie = `locale=${newLocale};path=/;max-age=${60 * 60 * 24 * 365};SameSite=Lax`;

    // 將目前路徑的語系替換為新語系
    const currentPath = $page.url.pathname;
    const newPath = currentPath.replace(`/${currentLocale}`, `/${newLocale}`);

    await goto(newPath);
  }
</script>

<div class="language-switcher" role="group" aria-label="Language selection">
  {#each locales as locale (locale)}
    <button
      onclick={() => switchLocale(locale)}
      aria-current={locale === currentLocale ? 'true' : undefined}
      class:active={locale === currentLocale}
      lang={locale}
    >
      {localeLabels[locale]}
    </button>
  {/each}
</div>

<style>
  .language-switcher {
    display: flex;
    gap: 0.5rem;
  }

  button {
    padding: 0.25rem 0.75rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: transparent;
    cursor: pointer;
  }

  button.active {
    background: #0066cc;
    color: white;
    border-color: #0066cc;
  }

  button:focus-visible {
    outline: 3px solid #4A90D9;
    outline-offset: 2px;
  }
</style>
```

SEO meta 標籤（在 layout 中設定）：

```svelte
<!-- src/routes/[lang=lang]/+layout.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
  import { page } from '$app/stores';
  import { getSupportedLocales, createTranslator } from '$lib/i18n';
  import type { Locale } from '../../params/lang';

  interface Props {
    data: { lang: Locale };
    children: Snippet;
  }

  let { data, children }: Props = $props();

  let t = $derived(createTranslator(data.lang));
  let locales = getSupportedLocales();

  // 為 hreflang 建立替代語系的 URL
  let alternateUrls = $derived(
    locales.map((locale) => ({
      locale,
      href: $page.url.pathname.replace(`/${data.lang}`, `/${locale}`),
    }))
  );
</script>

<svelte:head>
  <html lang={data.lang} />
  {#each alternateUrls as alt (alt.locale)}
    <link rel="alternate" hreflang={alt.locale} href={alt.href} />
  {/each}
  <link rel="alternate" hreflang="x-default" href={`/en${$page.url.pathname.slice(3)}`} />
</svelte:head>

<header>
  <nav aria-label={t('nav.home')}>
    <a href={`/${data.lang}`}>{t('nav.home')}</a>
    <a href={`/${data.lang}/about`}>{t('nav.about')}</a>
    <a href={`/${data.lang}/contact`}>{t('nav.contact')}</a>
  </nav>
  <LanguageSwitcher currentLocale={data.lang} />
</header>

<main>
  {@render children()}
</main>
```

- **何時用**：所有多語系網站都需要語言切換器。SEO 重要的網站必須加上 `hreflang` 標籤，讓搜尋引擎理解不同語系版本之間的關聯。
- **何時不用**：如果語系只由伺服器端根據 Accept-Language 自動決定，且不提供使用者手動切換的選項（罕見情境）。

### 5. SvelteKit Hooks Integration — 整合 SvelteKit Hooks

透過 `handle` hook 在伺服器端偵測使用者的語言偏好（cookie、Accept-Language header），並將語系資訊傳遞到 `event.locals` 供所有 load 函式使用。

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import type { Locale } from './params/lang';

const supportedLocales: Locale[] = ['en', 'zh'];
const defaultLocale: Locale = 'en';

function getPreferredLocale(request: Request): Locale {
  // 1. 先檢查 cookie
  const cookies = request.headers.get('cookie') ?? '';
  const localeCookie = cookies
    .split(';')
    .map((c) => c.trim())
    .find((c) => c.startsWith('locale='));

  if (localeCookie) {
    const value = localeCookie.split('=')[1] as Locale;
    if (supportedLocales.includes(value)) {
      return value;
    }
  }

  // 2. 檢查 Accept-Language header
  const acceptLanguage = request.headers.get('accept-language') ?? '';
  for (const locale of supportedLocales) {
    if (acceptLanguage.includes(locale)) {
      return locale;
    }
  }

  return defaultLocale;
}

export const handle: Handle = async ({ event, resolve }) => {
  // 從 URL 中提取語系
  const lang = event.params.lang as Locale | undefined;

  if (lang && supportedLocales.includes(lang)) {
    event.locals.lang = lang;
  } else {
    event.locals.lang = getPreferredLocale(event.request);
  }

  const response = await resolve(event, {
    // 動態設定 <html lang="...">
    transformPageChunk: ({ html }) =>
      html.replace('%lang%', event.locals.lang),
  });

  return response;
};
```

```ts
// src/app.d.ts
import type { Locale } from './params/lang';

declare global {
  namespace App {
    interface Locals {
      lang: Locale;
    }
  }
}

export {};
```

```html
<!-- src/app.html -->
<!doctype html>
<html lang="%lang%">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    %sveltekit.head%
  </head>
  <body data-sveltekit-prerender="true">
    <div style="display: contents">%sveltekit.body%</div>
  </body>
</html>
```

- **何時用**：需要伺服器端語系偵測的 SSR 應用。`handle` hook 是設定 `event.locals` 與修改 HTML 回應的最佳位置。
- **何時不用**：純 SPA 模式（無 SSR）的應用可以在 client 端直接從 cookie 或 localStorage 讀取語系偏好，不需要 hooks。

## Step-by-step

### Step 1：建立翻譯 JSON 檔案

建立英文和中文兩個翻譯檔案，定義所有需要翻譯的文字。

```json
// src/lib/i18n/en.json
{
  "common": {
    "appName": "My App",
    "loading": "Loading...",
    "save": "Save",
    "cancel": "Cancel"
  },
  "nav": {
    "home": "Home",
    "about": "About",
    "contact": "Contact"
  },
  "errors": {
    "required": "{field} is required",
    "notFound": "Page not found"
  }
}
```

```json
// src/lib/i18n/zh.json
{
  "common": {
    "appName": "我的應用",
    "loading": "載入中...",
    "save": "儲存",
    "cancel": "取消"
  },
  "nav": {
    "home": "首頁",
    "about": "關於",
    "contact": "聯絡我們"
  },
  "errors": {
    "required": "{field} 為必填",
    "notFound": "找不到頁面"
  }
}
```

確保兩個檔案的 key 結構完全一致。缺少的 key 在執行時會直接顯示 key 路徑（如 `errors.notFound`），方便發現遺漏。

### Step 2：建立型別安全的翻譯 helper

```ts
// src/lib/i18n/index.ts
import en from './en.json';
import zh from './zh.json';
import type { Locale } from '../../params/lang';

const translations: Record<Locale, typeof en> = { en, zh };

type NestedKeyOf<T> = T extends object
  ? {
      [K in keyof T & string]: T[K] extends object
        ? `${K}.${NestedKeyOf<T[K]>}`
        : K;
    }[keyof T & string]
  : never;

export type TranslationKey = NestedKeyOf<typeof en>;

function getNestedValue(obj: Record<string, unknown>, path: string): string {
  const keys = path.split('.');
  let current: unknown = obj;

  for (const key of keys) {
    if (current === null || current === undefined) return path;
    current = (current as Record<string, unknown>)[key];
  }

  return typeof current === 'string' ? current : path;
}

function interpolate(
  template: string,
  params?: Record<string, string | number>
): string {
  if (!params) return template;

  return Object.entries(params).reduce(
    (result, [key, value]) =>
      result.replace(new RegExp(`\\{${key}\\}`, 'g'), String(value)),
    template
  );
}

export function createTranslator(locale: Locale) {
  const dict = translations[locale];

  return function t(
    key: TranslationKey,
    params?: Record<string, string | number>
  ): string {
    const template = getNestedValue(dict as Record<string, unknown>, key);
    return interpolate(template, params);
  };
}

export function getSupportedLocales(): Locale[] {
  return ['en', 'zh'];
}

export const defaultLocale: Locale = 'en';
```

TypeScript 會自動從 `en.json` 推導出所有合法的 key 路徑，在編輯器中提供自動完成。

### Step 3：設定 locale-based 路由

```ts
// src/routes/[lang=lang]/+layout.ts
import type { LayoutLoad } from './$types';
import type { Locale } from '../../params/lang';

export const load: LayoutLoad = async ({ params }) => {
  const lang = params.lang as Locale;

  return { lang };
};
```

```svelte
<!-- src/routes/[lang=lang]/+layout.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { createTranslator } from '$lib/i18n';
  import type { Locale } from '../../params/lang';

  interface Props {
    data: { lang: Locale };
    children: Snippet;
  }

  let { data, children }: Props = $props();

  let t = $derived(createTranslator(data.lang));
</script>

<nav>
  <a href={`/${data.lang}`}>{t('nav.home')}</a>
  <a href={`/${data.lang}/about`}>{t('nav.about')}</a>
</nav>

<main>
  {@render children()}
</main>
```

```svelte
<!-- src/routes/[lang=lang]/+page.svelte -->
<script lang="ts">
  import { createTranslator } from '$lib/i18n';
  import type { Locale } from '../../params/lang';

  interface Props {
    data: { lang: Locale };
  }

  let { data }: Props = $props();

  let t = $derived(createTranslator(data.lang));
</script>

<h1>{t('common.appName')}</h1>
<p>{t('common.loading')}</p>
```

### Step 4：建立 params matcher

```ts
// src/params/lang.ts
import type { ParamMatcher } from '@sveltejs/kit';

const supportedLocales = ['en', 'zh'] as const;
export type Locale = (typeof supportedLocales)[number];

export const match: ParamMatcher = (param) => {
  return supportedLocales.includes(param as Locale);
};
```

params matcher 確保只有合法的語系值（`en`、`zh`）能匹配 `[lang=lang]` 路由參數。不合法的值（如 `/fr/about`）會觸發 404。

### Step 5：建立語言切換元件

```svelte
<!-- src/lib/components/LanguageSwitcher.svelte -->
<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { getSupportedLocales } from '$lib/i18n';
  import type { Locale } from '../../params/lang';

  interface Props {
    currentLocale: Locale;
  }

  let { currentLocale }: Props = $props();

  const localeLabels: Record<Locale, string> = {
    en: 'English',
    zh: '中文',
  };

  const locales = getSupportedLocales();

  async function switchLocale(newLocale: Locale) {
    if (newLocale === currentLocale) return;

    // 用 cookie 記住使用者偏好，有效期一年
    document.cookie = `locale=${newLocale};path=/;max-age=${60 * 60 * 24 * 365};SameSite=Lax`;

    const currentPath = $page.url.pathname;
    const newPath = currentPath.replace(`/${currentLocale}`, `/${newLocale}`);

    await goto(newPath);
  }
</script>

<div class="language-switcher" role="group" aria-label="Language selection">
  {#each locales as locale (locale)}
    <button
      onclick={() => switchLocale(locale)}
      aria-current={locale === currentLocale ? 'true' : undefined}
      class:active={locale === currentLocale}
      lang={locale}
    >
      {localeLabels[locale]}
    </button>
  {/each}
</div>
```

### Step 6：加入 `handle` hook 偵測 Accept-Language

```ts
// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';

const supportedLocales = ['en', 'zh'] as const;
type Locale = (typeof supportedLocales)[number];
const defaultLocale: Locale = 'en';

function getPreferredLocale(request: Request): Locale {
  // 優先讀取 cookie
  const cookies = request.headers.get('cookie') ?? '';
  const localeCookie = cookies
    .split(';')
    .map((c) => c.trim())
    .find((c) => c.startsWith('locale='));

  if (localeCookie) {
    const value = localeCookie.split('=')[1] as Locale;
    if (supportedLocales.includes(value)) return value;
  }

  // 再檢查 Accept-Language header
  const acceptLanguage = request.headers.get('accept-language') ?? '';
  for (const locale of supportedLocales) {
    if (acceptLanguage.includes(locale)) return locale;
  }

  return defaultLocale;
}

export const handle: Handle = async ({ event, resolve }) => {
  const lang = event.params.lang as Locale | undefined;

  if (lang && supportedLocales.includes(lang)) {
    event.locals.lang = lang;
  } else {
    event.locals.lang = getPreferredLocale(event.request);
  }

  const response = await resolve(event, {
    transformPageChunk: ({ html }) =>
      html.replace('%lang%', event.locals.lang),
  });

  return response;
};
```

### Step 7：實作日期/數字格式化 helper

```ts
// src/lib/i18n/format.ts
import type { Locale } from '../../params/lang';

const localeMap: Record<Locale, string> = {
  en: 'en-US',
  zh: 'zh-TW',
};

export function formatDate(
  date: Date,
  locale: Locale,
  options?: Intl.DateTimeFormatOptions
): string {
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options,
  };

  return new Intl.DateTimeFormat(localeMap[locale], defaultOptions).format(date);
}

export function formatRelativeTime(date: Date, locale: Locale): string {
  const now = Date.now();
  const diffMs = date.getTime() - now;
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));
  const diffHours = Math.round(diffMs / (1000 * 60 * 60));
  const diffMinutes = Math.round(diffMs / (1000 * 60));

  const rtf = new Intl.RelativeTimeFormat(localeMap[locale], { numeric: 'auto' });

  if (Math.abs(diffDays) >= 1) return rtf.format(diffDays, 'day');
  if (Math.abs(diffHours) >= 1) return rtf.format(diffHours, 'hour');
  return rtf.format(diffMinutes, 'minute');
}

export function formatNumber(
  value: number,
  locale: Locale,
  options?: Intl.NumberFormatOptions
): string {
  return new Intl.NumberFormat(localeMap[locale], options).format(value);
}

export function formatCurrency(
  value: number,
  locale: Locale,
  currency?: string
): string {
  const defaultCurrency = locale === 'zh' ? 'TWD' : 'USD';

  return new Intl.NumberFormat(localeMap[locale], {
    style: 'currency',
    currency: currency ?? defaultCurrency,
  }).format(value);
}
```

使用方式：

```svelte
<script lang="ts">
  import { formatDate, formatCurrency } from '$lib/i18n/format';
  import type { Locale } from '../../params/lang';

  let { data }: { data: { lang: Locale } } = $props();

  const date = new Date('2026-02-14');
  const price = 2499;
</script>

<p>{formatDate(date, data.lang)}</p>
<!-- en: "February 14, 2026" -->
<!-- zh: "2026年2月14日" -->

<p>{formatCurrency(price, data.lang)}</p>
<!-- en: "$2,499.00" -->
<!-- zh: "NT$2,499" -->
```

### Step 8：加入 hreflang SEO meta 標籤

```svelte
<!-- src/routes/[lang=lang]/+layout.svelte（完整版） -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { page } from '$app/stores';
  import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
  import { createTranslator, getSupportedLocales } from '$lib/i18n';
  import type { Locale } from '../../params/lang';

  interface Props {
    data: { lang: Locale };
    children: Snippet;
  }

  let { data, children }: Props = $props();

  let t = $derived(createTranslator(data.lang));
  let locales = getSupportedLocales();

  let alternateUrls = $derived(
    locales.map((locale) => ({
      locale,
      href: `${$page.url.origin}${$page.url.pathname.replace(`/${data.lang}`, `/${locale}`)}`,
    }))
  );

  // x-default 指向英文版
  let xDefaultUrl = $derived(
    `${$page.url.origin}/en${$page.url.pathname.slice(3)}`
  );
</script>

<svelte:head>
  {#each alternateUrls as alt (alt.locale)}
    <link rel="alternate" hreflang={alt.locale} href={alt.href} />
  {/each}
  <link rel="alternate" hreflang="x-default" href={xDefaultUrl} />
</svelte:head>

<header>
  <nav aria-label="Main navigation">
    <a href={`/${data.lang}`}>{t('nav.home')}</a>
    <a href={`/${data.lang}/about`}>{t('nav.about')}</a>
    <a href={`/${data.lang}/contact`}>{t('nav.contact')}</a>
  </nav>
  <LanguageSwitcher currentLocale={data.lang} />
</header>

<main>
  {@render children()}
</main>
```

`hreflang` 標籤告訴搜尋引擎同一頁面的不同語言版本，避免重複內容懲罰並確保使用者看到正確語言的搜尋結果。

## Hands-on Lab

任務：建立一個完整的多語系 SvelteKit 應用。

### Foundation 基礎層

建立一個雙語切換功能：

- 建立 `en.json` 和 `zh.json` 翻譯檔案，包含至少 10 個翻譯鍵。
- 建立 `createTranslator` 函式。
- 在頁面中使用翻譯函式顯示內容。
- 建立語言切換按鈕，用 cookie 記住偏好。

**驗收條件：**
- [ ] 點擊語言切換按鈕，頁面內容切換為對應語言。
- [ ] 重新整理頁面後，語言偏好仍然保持。
- [ ] TypeScript 不允許使用不存在的翻譯 key。
- [ ] `npx svelte-check` 通過。

### Advanced 進階層

建立完整的 locale-based 路由系統：

- 設定 `[lang=lang]` 路由結構搭配 params matcher。
- 建立 `handle` hook 偵測 Accept-Language header。
- 根路徑自動重導到偵測到的語系。
- 語言切換時更新 URL（如 `/en/about` → `/zh/about`）。
- 所有頁面透過 layout data 取得目前語系。

**驗收條件：**
- [ ] `/en/about` 和 `/zh/about` 顯示對應語言的內容。
- [ ] 直接訪問 `/` 會重導到偵測到的語系。
- [ ] 語言切換時 URL 同步更新。
- [ ] 不合法的語系（如 `/fr/about`）觸發 404。

### Challenge 挑戰層

建立完整的 i18n 方案，含日期格式化與 SEO：

- 在 Advanced 層基礎上加入日期/數字/貨幣格式化 helper。
- 加入 `<link rel="alternate" hreflang="...">` SEO 標籤。
- 動態設定 `<html lang="...">`。
- 支援插值翻譯（如 `{field} is required`）。
- 加入 `x-default` hreflang。
- 在頁面中展示格式化的日期、數字、貨幣。

**驗收條件：**
- [ ] 日期在英文顯示為 "February 14, 2026"，中文顯示為 "2026年2月14日"。
- [ ] 貨幣在英文顯示為 "$1,234.56"，中文顯示為 "NT$1,234"。
- [ ] HTML source 包含正確的 `hreflang` 標籤。
- [ ] `<html lang="...">` 隨語系變更動態更新。
- [ ] 插值翻譯正確顯示（如 "Email is required" / "Email 為必填"）。

## Reference Solution

完整的 i18n 設定，包含翻譯 helper、locale routing、語言切換器、格式化工具。

翻譯系統核心：

```ts
// src/lib/i18n/index.ts
import en from './en.json';
import zh from './zh.json';
import type { Locale } from '../../params/lang';

const translations: Record<Locale, typeof en> = { en, zh };

type NestedKeyOf<T> = T extends object
  ? {
      [K in keyof T & string]: T[K] extends object
        ? `${K}.${NestedKeyOf<T[K]>}`
        : K;
    }[keyof T & string]
  : never;

export type TranslationKey = NestedKeyOf<typeof en>;

function getNestedValue(obj: Record<string, unknown>, path: string): string {
  const keys = path.split('.');
  let current: unknown = obj;
  for (const key of keys) {
    if (current === null || current === undefined) return path;
    current = (current as Record<string, unknown>)[key];
  }
  return typeof current === 'string' ? current : path;
}

function interpolate(
  template: string,
  params?: Record<string, string | number>
): string {
  if (!params) return template;
  return Object.entries(params).reduce(
    (result, [key, value]) =>
      result.replace(new RegExp(`\\{${key}\\}`, 'g'), String(value)),
    template
  );
}

export function createTranslator(locale: Locale) {
  const dict = translations[locale];
  return function t(
    key: TranslationKey,
    params?: Record<string, string | number>
  ): string {
    const template = getNestedValue(dict as Record<string, unknown>, key);
    return interpolate(template, params);
  };
}

export function getSupportedLocales(): Locale[] {
  return ['en', 'zh'];
}

export const defaultLocale: Locale = 'en';
```

Params matcher：

```ts
// src/params/lang.ts
import type { ParamMatcher } from '@sveltejs/kit';

const supportedLocales = ['en', 'zh'] as const;
export type Locale = (typeof supportedLocales)[number];

export const match: ParamMatcher = (param) => {
  return supportedLocales.includes(param as Locale);
};
```

格式化工具：

```ts
// src/lib/i18n/format.ts
import type { Locale } from '../../params/lang';

const localeMap: Record<Locale, string> = {
  en: 'en-US',
  zh: 'zh-TW',
};

export function formatDate(
  date: Date,
  locale: Locale,
  options?: Intl.DateTimeFormatOptions
): string {
  return new Intl.DateTimeFormat(localeMap[locale], {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options,
  }).format(date);
}

export function formatNumber(
  value: number,
  locale: Locale,
  options?: Intl.NumberFormatOptions
): string {
  return new Intl.NumberFormat(localeMap[locale], options).format(value);
}

export function formatCurrency(
  value: number,
  locale: Locale,
  currency?: string
): string {
  return new Intl.NumberFormat(localeMap[locale], {
    style: 'currency',
    currency: currency ?? (locale === 'zh' ? 'TWD' : 'USD'),
  }).format(value);
}

export function formatRelativeTime(date: Date, locale: Locale): string {
  const now = Date.now();
  const diffMs = date.getTime() - now;
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));
  const diffHours = Math.round(diffMs / (1000 * 60 * 60));
  const diffMinutes = Math.round(diffMs / (1000 * 60));

  const rtf = new Intl.RelativeTimeFormat(localeMap[locale], { numeric: 'auto' });

  if (Math.abs(diffDays) >= 1) return rtf.format(diffDays, 'day');
  if (Math.abs(diffHours) >= 1) return rtf.format(diffHours, 'hour');
  return rtf.format(diffMinutes, 'minute');
}
```

語言切換器：

```svelte
<!-- src/lib/components/LanguageSwitcher.svelte -->
<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { getSupportedLocales } from '$lib/i18n';
  import type { Locale } from '../../params/lang';

  interface Props {
    currentLocale: Locale;
  }

  let { currentLocale }: Props = $props();

  const localeLabels: Record<Locale, string> = {
    en: 'English',
    zh: '中文',
  };

  const locales = getSupportedLocales();

  async function switchLocale(newLocale: Locale) {
    if (newLocale === currentLocale) return;
    document.cookie = `locale=${newLocale};path=/;max-age=${60 * 60 * 24 * 365};SameSite=Lax`;
    const newPath = $page.url.pathname.replace(`/${currentLocale}`, `/${newLocale}`);
    await goto(newPath);
  }
</script>

<div class="language-switcher" role="group" aria-label="Language selection">
  {#each locales as locale (locale)}
    <button
      onclick={() => switchLocale(locale)}
      aria-current={locale === currentLocale ? 'true' : undefined}
      class:active={locale === currentLocale}
      lang={locale}
    >
      {localeLabels[locale]}
    </button>
  {/each}
</div>

<style>
  .language-switcher {
    display: flex;
    gap: 0.5rem;
  }

  button {
    padding: 0.25rem 0.75rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: transparent;
    cursor: pointer;
    font-size: 0.875rem;
  }

  button.active {
    background: #0066cc;
    color: white;
    border-color: #0066cc;
  }

  button:focus-visible {
    outline: 3px solid #4A90D9;
    outline-offset: 2px;
  }
</style>
```

完整 Layout（含 SEO 標籤）：

```svelte
<!-- src/routes/[lang=lang]/+layout.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { page } from '$app/stores';
  import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
  import { createTranslator, getSupportedLocales } from '$lib/i18n';
  import type { Locale } from '../../params/lang';

  interface Props {
    data: { lang: Locale };
    children: Snippet;
  }

  let { data, children }: Props = $props();

  let t = $derived(createTranslator(data.lang));
  let locales = getSupportedLocales();

  let alternateUrls = $derived(
    locales.map((locale) => ({
      locale,
      href: `${$page.url.origin}${$page.url.pathname.replace(`/${data.lang}`, `/${locale}`)}`,
    }))
  );

  let xDefaultUrl = $derived(
    `${$page.url.origin}/en${$page.url.pathname.slice(3)}`
  );
</script>

<svelte:head>
  {#each alternateUrls as alt (alt.locale)}
    <link rel="alternate" hreflang={alt.locale} href={alt.href} />
  {/each}
  <link rel="alternate" hreflang="x-default" href={xDefaultUrl} />
</svelte:head>

<header>
  <nav aria-label="Main navigation">
    <a href={`/${data.lang}`}>{t('nav.home')}</a>
    <a href={`/${data.lang}/about`}>{t('nav.about')}</a>
    <a href={`/${data.lang}/contact`}>{t('nav.contact')}</a>
  </nav>
  <LanguageSwitcher currentLocale={data.lang} />
</header>

<main>
  {@render children()}
</main>
```

## Common Pitfalls

1. **在模板中寫死文字而非使用翻譯函式**：所有使用者可見的文字都應透過翻譯函式 `t()` 輸出。寫死的文字在切換語言時不會改變，常見於 placeholder、title、aria-label 等容易遺忘的屬性。

   ```svelte
   <!-- BAD -->
   <button>Save</button>
   <input placeholder="Enter your name" />

   <!-- GOOD -->
   <button>{t('common.save')}</button>
   <input placeholder={t('form.namePlaceholder')} />
   ```

2. **缺少 `<link rel="alternate" hreflang="...">` 標籤**：沒有 hreflang 標籤，搜尋引擎無法理解不同語系版本之間的關聯，可能將它們視為重複內容並懲罰排名。務必在每個頁面加上所有語系版本的 hreflang 標籤，以及 `x-default` 標籤。

   ```svelte
   <!-- BAD: 沒有 hreflang -->
   <svelte:head>
     <title>{t('common.appName')}</title>
   </svelte:head>

   <!-- GOOD: 包含完整的 hreflang -->
   <svelte:head>
     <title>{t('common.appName')}</title>
     <link rel="alternate" hreflang="en" href="/en/about" />
     <link rel="alternate" hreflang="zh" href="/zh/about" />
     <link rel="alternate" hreflang="x-default" href="/en/about" />
   </svelte:head>
   ```

3. **沒有持久化語言偏好**：使用者切換語言後，如果沒有將偏好存入 cookie，下次訪問時又會回到預設語言。使用 cookie（而非 localStorage）是因為 cookie 會隨 HTTP 請求發送到伺服器，讓 SSR 也能使用正確的語系。

   ```ts
   // BAD: 只存在記憶體中
   let currentLocale = 'en';

   // GOOD: 存入 cookie
   document.cookie = `locale=${newLocale};path=/;max-age=${60 * 60 * 24 * 365};SameSite=Lax`;
   ```

4. **SSR 與 client 端的語系不一致導致 hydration 錯誤**：如果伺服器端渲染的語系與 client 端不同，會觸發 hydration mismatch 錯誤。確保 `handle` hook 和 client 端使用相同的語系判斷邏輯（優先讀取 cookie，再檢查 Accept-Language）。

   ```ts
   // BAD: 伺服器端用 Accept-Language，client 端用 localStorage
   // 兩者結果可能不一致

   // GOOD: 統一用 cookie 作為 single source of truth
   // handle hook 讀 cookie → layout data → client 端一致
   ```

5. **日期格式化沒有考慮時區**：`Intl.DateTimeFormat` 預設使用瀏覽器的本地時區。如果你的日期資料是 UTC，在不同時區的使用者會看到不同的日期。對於需要精確的日期顯示（如事件時間），應明確指定 `timeZone` 選項。

   ```ts
   // BAD: 可能因時區差異顯示錯誤的日期
   formatDate(new Date('2026-02-14T00:00:00Z'), 'zh');

   // GOOD: 明確指定時區
   formatDate(new Date('2026-02-14T00:00:00Z'), 'zh', {
     timeZone: 'Asia/Taipei',
   });
   ```

## Checklist

- [ ] 能建立 JSON 翻譯檔案並維持所有語系的 key 結構一致。
- [ ] 能建立型別安全的翻譯函式，TypeScript 會檢查翻譯 key 的存在性。
- [ ] 能設定 `[lang=lang]` locale-based 路由與 params matcher。
- [ ] 能建立語言切換元件，切換時更新 URL 並以 cookie 持久化偏好。
- [ ] 能在 `handle` hook 中偵測 Accept-Language header 並設定預設語系。
- [ ] 能使用 `Intl.DateTimeFormat` 和 `Intl.NumberFormat` 格式化日期與數字。
- [ ] 能加入 `<link rel="alternate" hreflang="...">` 和 `<html lang="...">` SEO 標籤。

## Further Reading

- [SvelteKit Docs — Routing](https://svelte.dev/docs/kit/routing)
- [SvelteKit Docs — Hooks](https://svelte.dev/docs/kit/hooks)
- [SvelteKit Docs — Params](https://svelte.dev/docs/kit/advanced-routing#Matching)
- [MDN — Intl.DateTimeFormat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat)
- [MDN — Intl.NumberFormat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat)
- [MDN — Intl.RelativeTimeFormat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/RelativeTimeFormat)
- [Google — Hreflang Guide](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [paraglide-js — GitHub](https://github.com/opral/monorepo/tree/main/inlang/packages/paraglide)
