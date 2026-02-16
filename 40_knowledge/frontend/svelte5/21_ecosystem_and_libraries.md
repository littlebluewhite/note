---
title: "Ecosystem and Libraries / 生態系與常用套件"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-17
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "21"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [10_sveltekit_project_bootstrap]
---

# Ecosystem and Libraries / 生態系與常用套件

## Goal

全面掌握 Svelte 5 / SvelteKit 生態系中最重要的第三方套件與工具鏈。在實際專案中，很少有團隊從零造輪子——選對 UI 元件庫、表單處理方案、狀態管理工具和開發輔助工具，能大幅提升開發效率並降低維護成本。

本章涵蓋 UI 元件庫選型（shadcn-svelte、Bits UI、Skeleton、Flowbite Svelte）、表單處理最佳實踐（SuperForms + Zod）、狀態管理生態（runes vs stores vs 外部方案）、開發工具（DevTools、svelte-check、Vite inspector）以及圖表視覺化方案。每個選項都附帶決策矩陣，幫助你根據專案需求做出正確選擇。

- 銜接上一章：Ch20 完成了 Svelte 4 到 5 的遷移，現在要了解 Svelte 5 生態系中有哪些好用的工具可以加速開發。
- 下一章預告：Ch22 將深入認證模式（JWT、OAuth、Session-based auth）的實作。

## Prerequisites

- 已完成 Ch10，能獨立建立 SvelteKit 專案並理解基本專案結構。
- 熟悉 npm/pnpm 套件安裝與管理。
- 理解 Tailwind CSS 基礎概念（推薦但非必要）。
- 具備 TypeScript 基礎型別標註能力。

## Core Concepts

### 1. UI 元件庫選型

Svelte 5 生態系中有多種 UI 元件庫可供選擇，各有不同的設計哲學與適用場景。

#### 主要選項比較

| 特性 | shadcn-svelte | Bits UI | Skeleton | Flowbite Svelte |
|------|-------------|---------|----------|-----------------|
| 設計哲學 | Copy-paste 元件 | Headless primitives | 設計系統 + Tailwind | 預製樣式元件 |
| 樣式方案 | Tailwind v4 | 無樣式（自行設計） | Tailwind | Tailwind |
| 元件數量 | 50+ | 30+ primitives | 80+ | 60+ |
| 客製化程度 | 完全控制（原始碼在專案中） | 完全控制（自行設計樣式） | 主題系統 | 有限（透過 props） |
| Accessibility | 基於 Bits UI | 完整 WAI-ARIA | 基礎 | 基礎 |
| Svelte 5 支援 | 原生支援 | 原生支援 | 原生支援 | 原生支援 |
| 學習曲線 | 低 | 中 | 低 | 低 |
| 束縛程度 | 低（原始碼歸你） | 低 | 中 | 高 |

#### 選型決策矩陣

| 專案類型 | 推薦方案 | 理由 |
|----------|----------|------|
| SaaS / 管理後台 | shadcn-svelte | 需要專業外觀且可深度客製 |
| 設計系統 / 元件庫 | Bits UI | 需要完全控制樣式的 headless 方案 |
| 快速原型 / MVP | Flowbite Svelte 或 Skeleton | 預製樣式開箱即用，速度最快 |
| 高無障礙要求 | Bits UI + 自定義樣式 | WAI-ARIA 支援最完整 |
| 團隊有設計師 | Bits UI 或 shadcn-svelte | 設計師可自由定義視覺風格 |
| 團隊無設計師 | Skeleton 或 Flowbite | 預設主題即可直接使用 |

#### shadcn-svelte 特色說明

shadcn-svelte 不是傳統的 npm 套件——它是一個 CLI 工具，將元件原始碼直接複製到你的專案中。這意味著：

- 你擁有完整的元件原始碼，可以自由修改。
- 不存在版本升級破壞的問題。
- 底層使用 Bits UI 提供 accessibility 支援。
- 搭配 Tailwind v4 進行樣式設計。

```bash
# 初始化 shadcn-svelte（會建立設定檔和基礎樣式）
npx shadcn-svelte@latest init

# 加入特定元件
npx shadcn-svelte@latest add button
npx shadcn-svelte@latest add card
npx shadcn-svelte@latest add dialog
```

- **何時用 shadcn-svelte**：需要專業外觀、高度客製化、且團隊熟悉 Tailwind 的中大型專案。
- **何時不用**：不使用 Tailwind 的專案、或需要極簡依賴的微型專案。

### 2. 表單處理 — SuperForms + Zod

表單是 Web 應用的核心互動方式。SuperForms 是 SvelteKit 生態中最成熟的表單處理套件，搭配 Zod 進行驗證，提供型別安全、漸進增強、伺服器端驗證等完整功能。

#### 為什麼需要 SuperForms

| 需求 | 原生 SvelteKit Form Actions | SuperForms + Zod |
|------|----------------------------|-----------------|
| 伺服器端驗證 | 手動實作 | Zod schema 自動驗證 |
| 客戶端驗證 | 手動實作 | 自動同步 schema |
| 型別安全 | 手動維護 | schema 推導型別 |
| 漸進增強 | 需手動 `use:enhance` | 內建支援 |
| 錯誤顯示 | 手動處理 | 自動對應欄位 |
| Loading 狀態 | 手動管理 | 內建 `$submitting` |
| 巢狀物件 | 手動處理 | 原生支援 |

#### Zod Schema 定義

```ts
// src/lib/schemas/login.ts
import { z } from 'zod';

export const loginSchema = z.object({
  email: z
    .string()
    .email('請輸入有效的 email 地址'),
  password: z
    .string()
    .min(8, '密碼至少 8 個字元')
    .max(128, '密碼不可超過 128 個字元')
});

export type LoginSchema = typeof loginSchema;
```

#### Server-side Form Action

```ts
// src/routes/login/+page.server.ts
import type { Actions } from './$types';
import { superValidate, message } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { loginSchema } from '$lib/schemas/login';
import { fail } from '@sveltejs/kit';

export const load = async () => {
  const form = await superValidate(zod(loginSchema));
  return { form };
};

export const actions = {
  default: async ({ request }) => {
    const form = await superValidate(request, zod(loginSchema));

    if (!form.valid) {
      return fail(400, { form });
    }

    // 驗證通過後執行登入邏輯
    const { email, password } = form.data;
    // ... authenticate user ...

    return message(form, 'Login successful!');
  }
} satisfies Actions;
```

#### Client-side Form Component

```svelte
<!-- src/routes/login/+page.svelte -->
<script lang="ts">
  import { superForm } from 'sveltekit-superforms';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  const {
    form,
    errors,
    submitting,
    message: formMessage,
    enhance
  } = superForm(data.form);
</script>

<h1>Login</h1>

{#if $formMessage}
  <p class="success">{$formMessage}</p>
{/if}

<form method="POST" use:enhance>
  <div>
    <label for="email">Email</label>
    <input id="email" name="email" type="email" bind:value={$form.email} />
    {#if $errors.email}
      <span class="error">{$errors.email}</span>
    {/if}
  </div>

  <div>
    <label for="password">Password</label>
    <input id="password" name="password" type="password" bind:value={$form.password} />
    {#if $errors.password}
      <span class="error">{$errors.password}</span>
    {/if}
  </div>

  <button type="submit" disabled={$submitting}>
    {$submitting ? 'Logging in...' : 'Login'}
  </button>
</form>
```

- **何時用 SuperForms**：任何有表單的 SvelteKit 專案，尤其是需要伺服器端驗證、漸進增強、多欄位錯誤處理的情境。
- **何時不用**：極簡的單欄位搜尋框、不需要驗證的快速原型。

### 3. 狀態管理生態

Svelte 5 的 Runes 系統已經非常強大，大多數情況下不需要額外的狀態管理套件。但在特定場景下，仍有其他方案可以搭配使用。

#### 狀態管理方案選擇

| 場景 | 推薦方案 | 理由 |
|------|----------|------|
| 元件內部狀態 | `$state` | 最簡單直接 |
| 跨元件共享狀態 | `.svelte.ts` module + `$state` | Svelte 5 原生方案 |
| 需要 localStorage 持久化 | `$state` + 自定義 adapter | Runes + side effect |
| 跨框架共享 | Svelte stores 或 nanostores | 框架無關的 API |
| 複雜非同步狀態 | TanStack Query (Svelte) | 快取、重試、失效管理 |

#### Runes 跨元件共享模式

```ts
// src/lib/state/theme.svelte.ts
type Theme = 'light' | 'dark';

let theme = $state<Theme>('light');

export function getTheme() {
  return theme;
}

export function setTheme(value: Theme) {
  theme = value;
}

export function toggleTheme() {
  theme = theme === 'light' ? 'dark' : 'light';
}
```

```svelte
<!-- 任何元件中都可以使用 -->
<script lang="ts">
  import { getTheme, toggleTheme } from '$lib/state/theme.svelte';
</script>

<p>Current theme: {getTheme()}</p>
<button onclick={toggleTheme}>Toggle Theme</button>
```

#### localStorage 持久化 Adapter

```ts
// src/lib/state/persisted.svelte.ts
export function createPersistedState<T>(key: string, initial: T) {
  let value = $state<T>(initial);

  // 從 localStorage 讀取初始值
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem(key);
    if (stored) {
      try {
        value = JSON.parse(stored);
      } catch {
        // ignore parse errors
      }
    }
  }

  // 監聽變更並寫入 localStorage
  $effect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(key, JSON.stringify(value));
    }
  });

  return {
    get value() { return value; },
    set value(v: T) { value = v; }
  };
}
```

```svelte
<script lang="ts">
  import { createPersistedState } from '$lib/state/persisted.svelte';

  const settings = createPersistedState('user-settings', {
    language: 'zh-TW',
    fontSize: 16
  });
</script>

<p>Language: {settings.value.language}</p>
<button onclick={() => settings.value = { ...settings.value, fontSize: settings.value.fontSize + 1 }}>
  Increase font size ({settings.value.fontSize})
</button>
```

- **何時用 Runes 管理狀態**：絕大多數 Svelte 5 專案。Runes 足以處理元件內、跨元件、甚至持久化的狀態需求。
- **何時考慮外部方案**：需要跨框架共享狀態（如 Svelte + React micro-frontend）、或需要 TanStack Query 等進階非同步快取管理。

### 4. 開發工具

好的開發工具可以大幅提升除錯效率和開發體驗。

#### Svelte Language Tools 效能改進

Svelte Language Tools（VS Code 擴充功能 + LSP）在 2025–2026 年間經歷多次重大效能提升：

- **2025 年中**：支援 snippets 泛型型別推導（`language-tools@109.8.0`）、新增「儲存時自動加入缺少的 import」功能（`language-tools@109.6.0`）。
- **2025 Q4 – 2026 Q1**：大量效能最佳化，包含更快的型別檢查、減少記憶體用量、改善大型專案的回應速度。

> **建議**：定期更新 VS Code 的 Svelte 擴充功能，以確保獲得最新的效能改善。可在 VS Code 中搜尋 "Svelte for VS Code" 確認版本。

#### SvelteDoc VS Code 擴充功能

SvelteDoc 是社群開發的 VS Code 擴充功能，可在 hover 時顯示 Svelte 元件的 props 資訊，方便快速查看元件介面而不需要打開原始碼。

#### Svelte DevTools 瀏覽器擴充功能

Svelte DevTools 是 Chrome/Firefox 擴充功能，提供元件樹檢視、狀態檢查等功能。

- 安裝：Chrome Web Store 搜尋 "Svelte DevTools"。
- 功能：檢視元件階層、查看 props 和 state、追蹤 DOM 更新。

#### `svelte-check` CLI

`svelte-check` 是 Svelte 的靜態分析工具，檢查型別錯誤、accessibility 問題和未使用的 CSS。

```bash
# 一次性檢查
npx svelte-check

# 監聽模式（開發時持續檢查）
npx svelte-check --watch

# 搭配 tsconfig 路徑
npx svelte-check --tsconfig ./tsconfig.json
```

建議加入 `package.json` scripts：

```json
{
  "scripts": {
    "check": "svelte-check --tsconfig ./tsconfig.json",
    "check:watch": "svelte-check --tsconfig ./tsconfig.json --watch"
  }
}
```

#### `svelte-fast-check` — 高速型別檢查替代方案

`svelte-fast-check` 宣稱比內建的 `svelte-check` 快達 24 倍，適合大型專案在 CI/CD 中縮短檢查時間：

```bash
npm install -D svelte-fast-check

# 執行快速檢查
npx svelte-fast-check
```

> **注意**：`svelte-fast-check` 是社群套件，功能覆蓋範圍可能與官方 `svelte-check` 有差異。建議在 CI 中兩者並行使用，確保完整性。

#### Vite Inspector Plugin

`vite-plugin-svelte-inspector` 讓你在瀏覽器中按住 Meta 鍵點擊任何元素，直接跳轉到對應的 Svelte 元件原始碼。

```ts
// vite.config.ts
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    sveltekit()
    // Inspector 在 @sveltejs/vite-plugin-svelte 中內建
    // 開發模式下按 Meta + Shift 啟用
  ]
});
```

在 SvelteKit 專案中，Inspector 已內建於 `@sveltejs/vite-plugin-svelte`。開發模式下使用快捷鍵（macOS: `Cmd + Shift` 點擊元素）即可啟用。

- **何時用開發工具**：所有 Svelte 專案都應該配置 `svelte-check`，DevTools 和 Inspector 在開發除錯階段很有幫助。
- **何時不用**：CI/CD 環境只需 `svelte-check`（或 `svelte-fast-check`），其餘工具僅用於本地開發。

### 5. Svelte MCP — AI 輔助開發工具

Svelte MCP（Model Context Protocol）是 Svelte 官方提供的 AI 輔助開發伺服器（`@sveltejs/mcp-server`，v0.1.16+），讓 LLM 和 AI agent 能撰寫更好的 Svelte 程式碼。它同時支援 JavaScript API 和 CLI 兩種使用方式。

#### 核心工具

| 工具名稱 | 用途 |
|----------|------|
| `list-sections` | 列出所有可用的 Svelte 5 / SvelteKit 文件章節，含標題、使用場景和路徑 |
| `get-documentation` | 取得特定章節的完整文件內容，支援一次取多個章節 |
| `svelte-autofixer` | 靜態分析 Svelte 程式碼，回傳問題清單與修正建議（基於 AST 解析 + ESLint） |
| `playground-link` | 將程式碼生成 Svelte Playground 連結，方便分享 |

#### 使用方式

```bash
# 安裝
npm install @sveltejs/mcp-server

# CLI 方式啟動
npx @sveltejs/mcp-server
```

在支援 MCP 的 AI 工具（如 Claude、Cursor 等）中設定 Svelte MCP server 後，AI 可以：

1. 查詢最新的 Svelte 5 / SvelteKit 文件。
2. 在產生程式碼後自動呼叫 `svelte-autofixer` 檢查問題。
3. 偵測 Svelte 4 → 5 遷移問題（如 runes 語法錯誤、不正確的 state mutation）。
4. 產生可直接在 Svelte Playground 上測試的連結。

#### `svelte-autofixer` 的檢查項目

```typescript
// autofixer 接收 Svelte 元件程式碼並分析
// 回傳結構：
interface AutofixerResult {
  issues: string[];       // 發現的問題
  suggestions: string[];  // 修正建議
  require_another_tool_call_after_fixing: boolean;
}
```

常見的自動偵測項目包括：
- 將 runes 當作宣告而非函式呼叫使用。
- 在 `$effect` 中進行不正確的 state mutation。
- 缺少響應式宣告（reactivity declarations）。
- Svelte 4 舊語法殘留（如 `export let`、`<slot>`）。

| 何時用 Svelte MCP | 何時不用 |
|---|---|
| 使用 AI 輔助工具開發 Svelte 專案 | 不使用 AI 輔助開發的團隊 |
| 需要即時查詢最新 Svelte 文件 | 團隊已熟悉所有 API 且不需要文件參考 |
| 程式碼品質把關、自動化程式碼審查 | 已有完整的 ESLint / CI 檢查流程 |
| Svelte 4 → 5 遷移過程中的輔助檢查 | 純 Svelte 5 新專案且團隊經驗充足 |

### 6. 圖表與視覺化

Svelte 的 reactivity 系統非常適合資料視覺化——狀態變更時圖表自動更新。

#### LayerChart

LayerChart 是專為 Svelte 打造的圖表套件，基於 D3 scales 但提供 Svelte 友善的宣告式 API。

```bash
npm install layerchart
```

```svelte
<script lang="ts">
  import { Chart, Svg, Axis, Bars } from 'layerchart';
  import { scaleBand, scaleLinear } from 'd3-scale';

  let data = $state([
    { label: 'A', value: 30 },
    { label: 'B', value: 80 },
    { label: 'C', value: 45 },
    { label: 'D', value: 60 }
  ]);
</script>

<div class="chart-container" style="height: 300px;">
  <Chart
    {data}
    x="label"
    xScale={scaleBand().padding(0.4)}
    y="value"
    yDomain={[0, null]}
    yNice
    padding={{ left: 16, bottom: 24 }}
  >
    <Svg>
      <Axis placement="left" />
      <Axis placement="bottom" />
      <Bars radius={4} strokeWidth={1} class="fill-primary" />
    </Svg>
  </Chart>
</div>
```

#### D3 + Svelte 整合模式

若需要更底層的控制，可以直接結合 D3 與 Svelte。D3 負責資料計算（scales、layouts），Svelte 負責 DOM 渲染：

```svelte
<script lang="ts">
  import { scaleLinear, scaleTime } from 'd3-scale';
  import { line } from 'd3-shape';

  let width = $state(600);
  let height = $state(300);
  let margin = { top: 20, right: 20, bottom: 30, left: 40 };

  interface DataPoint { date: Date; value: number; }
  let data = $state<DataPoint[]>([
    { date: new Date('2026-01-01'), value: 30 },
    { date: new Date('2026-02-01'), value: 50 },
    { date: new Date('2026-03-01'), value: 45 },
    { date: new Date('2026-04-01'), value: 70 }
  ]);

  let xScale = $derived(
    scaleTime()
      .domain([data[0].date, data[data.length - 1].date])
      .range([margin.left, width - margin.right])
  );

  let yScale = $derived(
    scaleLinear()
      .domain([0, Math.max(...data.map(d => d.value))])
      .nice()
      .range([height - margin.bottom, margin.top])
  );

  let pathD = $derived(
    line<DataPoint>()
      .x(d => xScale(d.date))
      .y(d => yScale(d.value))(data) ?? ''
  );
</script>

<svg {width} {height}>
  <path d={pathD} fill="none" stroke="steelblue" stroke-width="2" />
  {#each data as point}
    <circle
      cx={xScale(point.date)}
      cy={yScale(point.value)}
      r="4"
      fill="steelblue"
    />
  {/each}
</svg>
```

- **何時用 LayerChart**：需要常見圖表類型（bar、line、pie、area）且希望快速開發。
- **何時用 D3 + Svelte**：需要高度客製化的視覺化、互動式圖表、或 LayerChart 不支援的圖表類型。

### 7. 社群套件精選

Svelte 生態系持續壯大，以下是 2025–2026 年間值得關注的社群新專案：

#### 終端機與 CLI 相關

| 套件 | 說明 |
|------|------|
| **SvelTTY** | 終端機渲染 runtime，讓你在終端機中渲染和操作 Svelte 應用 |
| **svelte-bash** | 輕量、可自訂的終端模擬器元件，內建虛擬檔案系統、自訂命令、主題和自動播放模式 |

#### 基礎建設與安全

| 套件 | 說明 |
|------|------|
| **@svelte-safe-html/core** | 靜態分析器，偵測不安全的 `{@html}` 使用 |
| **sveltekit-discriminated-fields** | 為 Remote Functions 提供 type-safe 的 discriminated unions |
| **pocket-mocker** | 頁面內 HTTP 控制器，可攔截和模擬 API 回應，方便前端開發與測試 |
| **SvelteKit Auto OpenAPI** | 型別安全的 OpenAPI 文件自動產生與 runtime 驗證 |

#### UI 元件與動畫

| 套件 | 說明 |
|------|------|
| **mapcn-svelte** | 基於 MapLibre GL 的 Svelte 地圖元件，支援 Tailwind 樣式，相容 shadcn-svelte |
| **Motion Core** | 以 GSAP 和 Three.js 驅動的動畫元件集合 |
| **Tilt Svelte** | 3D 傾斜效果元件，靈感來自 vanilla-tilt.js |
| **trioxide** | 專注於非典型 UI 片段的可自訂元件集 |
| **svelte-asciiart** | Svelte 5 ASCII art 渲染元件，可產生可縮放 SVG |

#### 狀態管理

| 套件 | 說明 |
|------|------|
| **Reddo.js** | 跨框架（JS / React / Vue / Svelte）的 undo/redo 工具 |
| **svstate** | 深層響應式 proxy，支援驗證、snapshot/undo 和 side effects |
| **rune-sync** | 將 runes 響應式狀態同步到各種 storage backend |

#### 部署與執行環境

| 套件 | 說明 |
|------|------|
| **fastify-svelte-view** | Fastify 插件，支援 SSR、CSR 和 hydration 渲染 |
| **kit-on-lambda** | SvelteKit 的 AWS Lambda adapter，支援 Node.js 和 Bun runtime |

#### 應用程式展示

| 專案 | 說明 |
|------|------|
| **Frame** | 基於 Tauri v2 的高效能媒體轉換工具，提供 FFmpeg 操作的原生介面 |
| **LogTide** | 開源的日誌管理平台，替代 Datadog / Splunk / ELK，強調 GDPR 合規與資料自主 |
| **Pelican** | 從文字提示產生 SVG 向量圖和 ASCII art，支援 AI 多步精煉 |

## Step-by-step

### Step 1：安裝 shadcn-svelte

在既有 SvelteKit 專案中初始化 shadcn-svelte：

```bash
# 確保已安裝 Tailwind CSS v4
# 如果尚未安裝，先執行：
npx sv add tailwindcss

# 初始化 shadcn-svelte
npx shadcn-svelte@latest init
```

初始化過程中會詢問幾個設定：
- Style: Default / New York（視覺風格）
- Base color: Slate / Gray / Zinc / Neutral / Stone
- CSS variables: Yes（推薦）

初始化後會建立以下檔案：
- `$lib/components/ui/` — 元件存放目錄
- `$lib/utils.ts` — 工具函式（`cn` class 合併函式）
- 更新 `app.css` 加入 CSS 變數

### Step 2：安裝第一個 shadcn-svelte 元件

```bash
# 安裝 Button 元件
npx shadcn-svelte@latest add button
```

安裝後檢查 `src/lib/components/ui/button/` 目錄，會看到元件原始碼直接在你的專案中。

使用 Button：

```svelte
<script lang="ts">
  import { Button } from '$lib/components/ui/button';
</script>

<Button variant="default">Primary</Button>
<Button variant="outline">Outline</Button>
<Button variant="destructive">Delete</Button>
<Button variant="ghost" size="sm">Small Ghost</Button>
```

### Step 3：使用 shadcn-svelte 建立 Card 元件

```bash
npx shadcn-svelte@latest add card
```

```svelte
<!-- src/routes/dashboard/+page.svelte -->
<script lang="ts">
  import * as Card from '$lib/components/ui/card';
  import { Button } from '$lib/components/ui/button';
</script>

<Card.Root class="w-[350px]">
  <Card.Header>
    <Card.Title>Project Overview</Card.Title>
    <Card.Description>
      Your project statistics at a glance.
    </Card.Description>
  </Card.Header>
  <Card.Content>
    <div class="grid gap-4">
      <div class="flex items-center justify-between">
        <span>Total Users</span>
        <span class="font-bold">1,234</span>
      </div>
      <div class="flex items-center justify-between">
        <span>Active Sessions</span>
        <span class="font-bold">56</span>
      </div>
    </div>
  </Card.Content>
  <Card.Footer>
    <Button class="w-full">View Details</Button>
  </Card.Footer>
</Card.Root>
```

### Step 4：安裝 SuperForms + Zod

```bash
npm install sveltekit-superforms zod
```

確認 `tsconfig.json` 有啟用 strict mode（SuperForms 型別推導需要）：

```json
{
  "compilerOptions": {
    "strict": true
  }
}
```

### Step 5：使用 SuperForms 建立驗證登入表單

建立 Zod schema：

```ts
// src/lib/schemas/login.ts
import { z } from 'zod';

export const loginSchema = z.object({
  email: z
    .string({ required_error: 'Email is required' })
    .email('Please enter a valid email address'),
  password: z
    .string({ required_error: 'Password is required' })
    .min(8, 'Password must be at least 8 characters')
});

export type LoginSchema = typeof loginSchema;
```

建立 server-side load 與 action：

```ts
// src/routes/login/+page.server.ts
import type { Actions, PageServerLoad } from './$types';
import { superValidate, message } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { loginSchema } from '$lib/schemas/login';
import { fail } from '@sveltejs/kit';

export const load: PageServerLoad = async () => {
  const form = await superValidate(zod(loginSchema));
  return { form };
};

export const actions = {
  default: async ({ request }) => {
    const form = await superValidate(request, zod(loginSchema));

    if (!form.valid) {
      return fail(400, { form });
    }

    // 模擬登入驗證
    const { email, password } = form.data;
    if (email !== 'admin@example.com' || password !== 'password123') {
      return message(form, 'Invalid credentials', { status: 401 });
    }

    return message(form, 'Login successful!');
  }
} satisfies Actions;
```

建立表單頁面：

```svelte
<!-- src/routes/login/+page.svelte -->
<script lang="ts">
  import { superForm } from 'sveltekit-superforms';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  const {
    form,
    errors,
    submitting,
    delayed,
    message: formMessage,
    enhance
  } = superForm(data.form, {
    delayMs: 300,
    timeoutMs: 5000
  });
</script>

<div class="max-w-md mx-auto mt-8">
  <h1 class="text-2xl font-bold mb-4">Login</h1>

  {#if $formMessage}
    <div class="p-3 rounded mb-4 bg-blue-100 text-blue-800">
      {$formMessage}
    </div>
  {/if}

  <form method="POST" use:enhance class="space-y-4">
    <div>
      <label for="email" class="block text-sm font-medium">Email</label>
      <input
        id="email"
        name="email"
        type="email"
        bind:value={$form.email}
        class="mt-1 block w-full rounded border px-3 py-2"
        class:border-red-500={$errors.email}
      />
      {#if $errors.email}
        <p class="mt-1 text-sm text-red-500">{$errors.email}</p>
      {/if}
    </div>

    <div>
      <label for="password" class="block text-sm font-medium">Password</label>
      <input
        id="password"
        name="password"
        type="password"
        bind:value={$form.password}
        class="mt-1 block w-full rounded border px-3 py-2"
        class:border-red-500={$errors.password}
      />
      {#if $errors.password}
        <p class="mt-1 text-sm text-red-500">{$errors.password}</p>
      {/if}
    </div>

    <button
      type="submit"
      disabled={$submitting}
      class="w-full rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
    >
      {#if $delayed}
        Logging in...
      {:else}
        Login
      {/if}
    </button>
  </form>
</div>
```

### Step 6：設定 Svelte DevTools 與 svelte-check

安裝 Svelte DevTools 瀏覽器擴充功能：

1. 前往 Chrome Web Store 或 Firefox Add-ons。
2. 搜尋 "Svelte DevTools"。
3. 安裝擴充功能。
4. 開啟開發中的 SvelteKit 應用，在 DevTools 中會看到新的 "Svelte" 分頁。

設定 `svelte-check` 在 CI/CD 中執行：

```json
{
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "check": "svelte-check --tsconfig ./tsconfig.json",
    "check:watch": "svelte-check --tsconfig ./tsconfig.json --watch"
  }
}
```

```bash
# 本地開發時使用 watch 模式
npm run check:watch

# CI/CD 中使用一次性檢查
npm run check
```

## Hands-on Lab

### Foundation 基礎層

**任務**：使用 shadcn-svelte 建立一個統計 Card 元件。

要求：
- 初始化 shadcn-svelte。
- 安裝 Card 和 Button 元件。
- 建立一個 `StatsCard` 元件，接收 `title`、`value`、`description` props。
- 在頁面中展示 3 張 StatsCard（Users、Revenue、Orders）。
- 使用 `$state` 管理數據，加入「重新整理」按鈕模擬更新。

驗收條件：
- 三張卡片正確顯示不同統計數據。
- 點擊重新整理按鈕後數據更新。
- 視覺風格統一、排版整齊。
- `npx svelte-check` 通過。

### Advanced 進階層

**任務**：使用 SuperForms + Zod 建立完整的登入表單。

要求：
- 定義 Zod schema，包含 email 驗證和密碼長度限制。
- 實作 server-side form action 進行驗證。
- 實作 client-side 表單，顯示欄位級別錯誤訊息。
- 加入 loading 狀態指示。
- 表單支援漸進增強（JavaScript 關閉時仍可提交）。

驗收條件：
- 空白提交時顯示所有錯誤訊息。
- email 格式錯誤時顯示對應錯誤。
- 提交中顯示 loading 狀態。
- 關閉 JavaScript 後表單仍可正常提交與驗證。
- `npx svelte-check` 通過。

### Challenge 挑戰層

**任務**：建立一個 Dashboard 頁面，結合 shadcn-svelte 元件、SuperForms 表單和一個簡單圖表。

要求：
- 頁面頂部：4 張 StatsCard 顯示 KPI 數據。
- 中間：使用 D3 或 LayerChart 繪製一個 bar chart。
- 底部：使用 SuperForms 建立一個「新增數據」的表單。
- 表單提交後，數據即時反映在圖表和統計卡片上。
- 使用 localStorage 持久化數據（使用 Core Concepts 中的 adapter）。

驗收條件：
- 統計卡片、圖表、表單三者數據連動。
- 重新整理頁面後數據仍保留（localStorage 持久化）。
- 表單有完整的 Zod 驗證。
- 視覺風格統一。
- `npx svelte-check` 通過。

## Reference Solution

### Foundation：StatsCard 元件

```svelte
<!-- src/lib/components/StatsCard.svelte -->
<script lang="ts">
  import * as Card from '$lib/components/ui/card';

  let {
    title,
    value,
    description
  } = $props<{
    title: string;
    value: string | number;
    description: string;
  }>();
</script>

<Card.Root>
  <Card.Header class="pb-2">
    <Card.Description>{title}</Card.Description>
    <Card.Title class="text-3xl font-bold">{value}</Card.Title>
  </Card.Header>
  <Card.Content>
    <p class="text-xs text-muted-foreground">{description}</p>
  </Card.Content>
</Card.Root>
```

```svelte
<!-- src/routes/dashboard/+page.svelte -->
<script lang="ts">
  import StatsCard from '$lib/components/StatsCard.svelte';
  import { Button } from '$lib/components/ui/button';

  let users = $state(1234);
  let revenue = $state(56789);
  let orders = $state(342);

  function refresh() {
    users += Math.floor(Math.random() * 50);
    revenue += Math.floor(Math.random() * 5000);
    orders += Math.floor(Math.random() * 20);
  }
</script>

<div class="p-8">
  <div class="flex items-center justify-between mb-6">
    <h1 class="text-2xl font-bold">Dashboard</h1>
    <Button onclick={refresh}>Refresh</Button>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <StatsCard
      title="Total Users"
      value={users.toLocaleString()}
      description="+12% from last month"
    />
    <StatsCard
      title="Revenue"
      value={`$${revenue.toLocaleString()}`}
      description="+8% from last month"
    />
    <StatsCard
      title="Orders"
      value={orders}
      description="+3% from last month"
    />
  </div>
</div>
```

### Advanced：SuperForms 登入表單

完整程式碼請參考 Step 5 的三個檔案：`src/lib/schemas/login.ts`、`src/routes/login/+page.server.ts`、`src/routes/login/+page.svelte`。

### Challenge：D3 + Svelte Bar Chart

```svelte
<!-- src/lib/components/BarChart.svelte -->
<script lang="ts">
  import { scaleBand, scaleLinear } from 'd3-scale';

  interface DataItem {
    label: string;
    value: number;
  }

  let { data, width = 500, height = 300 } = $props<{
    data: DataItem[];
    width?: number;
    height?: number;
  }>();

  let margin = { top: 20, right: 20, bottom: 40, left: 50 };
  let innerWidth = $derived(width - margin.left - margin.right);
  let innerHeight = $derived(height - margin.top - margin.bottom);

  let xScale = $derived(
    scaleBand<string>()
      .domain(data.map(d => d.label))
      .range([0, innerWidth])
      .padding(0.3)
  );

  let yScale = $derived(
    scaleLinear()
      .domain([0, Math.max(...data.map(d => d.value), 10)])
      .nice()
      .range([innerHeight, 0])
  );

  let yTicks = $derived(yScale.ticks(5));
</script>

<svg {width} {height}>
  <g transform="translate({margin.left}, {margin.top})">
    <!-- Y axis -->
    {#each yTicks as tick}
      <g transform="translate(0, {yScale(tick)})">
        <line x1="0" x2={innerWidth} stroke="#e0e0e0" />
        <text x="-8" dy="0.35em" text-anchor="end" font-size="12">{tick}</text>
      </g>
    {/each}

    <!-- Bars -->
    {#each data as item}
      <rect
        x={xScale(item.label)}
        y={yScale(item.value)}
        width={xScale.bandwidth()}
        height={innerHeight - yScale(item.value)}
        fill="steelblue"
        rx="4"
      />
    {/each}

    <!-- X axis labels -->
    {#each data as item}
      <text
        x={(xScale(item.label) ?? 0) + xScale.bandwidth() / 2}
        y={innerHeight + 20}
        text-anchor="middle"
        font-size="12"
      >
        {item.label}
      </text>
    {/each}
  </g>
</svg>
```

## Common Pitfalls

1. **安裝 shadcn-svelte 元件前未初始化**
   必須先執行 `npx shadcn-svelte@latest init` 完成初始化（建立設定檔、CSS 變數等），才能用 `add` 指令安裝個別元件。否則會看到路徑錯誤或找不到設定檔的錯誤。

2. **SuperForms 忘記在 load 函式中建立 form 物件**
   SuperForms 需要在 `+page.server.ts` 的 `load` 函式中呼叫 `superValidate` 來建立初始 form 物件，並傳遞給 client。如果跳過這步，client 端會沒有 form 資料可以操作。

   ```ts
   // Bad: 沒有 load 函式
   // export const actions = { ... }

   // Good: 有 load 函式提供初始 form
   export const load = async () => {
     const form = await superValidate(zod(schema));
     return { form };
   };
   ```

3. **在 `.ts` 檔案中使用 runes（應使用 `.svelte.ts`）**
   跨元件共享的響應式狀態必須放在 `.svelte.ts` 檔案中，不可放在一般的 `.ts` 檔案。Svelte compiler 只會處理 `.svelte` 和 `.svelte.ts` 檔案中的 runes。

4. **D3 直接操作 DOM 而非讓 Svelte 管理**
   結合 D3 與 Svelte 時，應該只使用 D3 的資料計算功能（scales、layouts、shapes），讓 Svelte 負責實際的 DOM 渲染。不要在 Svelte 元件中使用 `d3.select().append()` 等 DOM 操作方法，這會與 Svelte 的 DOM 管理衝突。

   ```svelte
   <!-- Bad: D3 直接操作 DOM -->
   <script lang="ts">
     import * as d3 from 'd3';
     import { onMount } from 'svelte';
     onMount(() => {
       d3.select('#chart').append('rect')... // 避免！
     });
   </script>

   <!-- Good: D3 計算 + Svelte 渲染 -->
   <script lang="ts">
     import { scaleLinear } from 'd3-scale';
     let yScale = $derived(scaleLinear().domain([0, 100]).range([300, 0]));
   </script>
   <rect y={yScale(50)} ... />
   ```

## Checklist

- [ ] 能根據專案需求從 shadcn-svelte、Bits UI、Skeleton、Flowbite 中選擇合適的 UI 套件
- [ ] 能初始化 shadcn-svelte 並安裝、使用、自定義元件
- [ ] 能使用 SuperForms + Zod 建立具有伺服器端驗證的表單
- [ ] 能使用 `.svelte.ts` + runes 實作跨元件共享狀態
- [ ] 能配置 svelte-check 並在開發與 CI/CD 中使用
- [ ] 能選擇適當的圖表方案（LayerChart 或 D3 + Svelte）並實作基礎圖表
- [ ] 了解 Svelte MCP 的用途，能在支援 MCP 的 AI 工具中配置使用
- [ ] 能根據專案需求評估和選擇適合的社群套件

## Further Reading

- [shadcn-svelte Documentation](https://www.shadcn-svelte.com/)
- [Bits UI Documentation](https://www.bits-ui.com/)
- [Skeleton UI Documentation](https://www.skeleton.dev/)
- [Flowbite Svelte Documentation](https://flowbite-svelte.com/)
- [SuperForms Documentation](https://superforms.rocks/)
- [Zod Documentation](https://zod.dev/)
- [LayerChart Documentation](https://www.layerchart.com/)
- [Svelte DevTools](https://github.com/sveltejs/svelte-devtools)
- [svelte-check](https://www.npmjs.com/package/svelte-check)
- [Svelte MCP Server](https://github.com/sveltejs/mcp)
- [Svelte MCP Documentation](https://mcp.svelte.dev/)
- [Svelte Packages Directory](https://svelte.dev/packages)
- [Svelte Society Packages](https://sveltesociety.dev/packages)
- [What's new in Svelte — Blog](https://svelte.dev/blog)
