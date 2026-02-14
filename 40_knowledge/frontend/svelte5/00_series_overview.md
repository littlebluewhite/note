---
title: Svelte 5 Series Overview / Svelte 5 系列導讀
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "00"
level: beginner
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [basic_computer_usage]
---
# Series Overview / 系列導讀

## Goal

建立一條從零開始到可完成中小型產品頁面的學習路徑，能理解 Svelte 5 與 SvelteKit 的實務關係。

透過本章，學習者將建立完整的開發環境與學習節奏，並釐清 Svelte（compiler / UI framework）與 SvelteKit（application framework）的角色分工。這是整個系列的地基——環境正確配置、版本基準釘選之後，後續章節才能專注在框架概念而非環境問題上。

- 前一章：無（本章為系列起點）。
- 下一章預告：Ch01 涵蓋進入 Svelte 前所需的 Web / JavaScript 基礎知識。

## Prerequisites

- 會使用終端機執行指令（terminal basics）。
- 知道檔案/資料夾與 Git 的基本概念。
- 尚不需要先學過 Svelte，本系列從零開始。

## Core Concepts

### 1. Svelte — 編譯時期 UI 框架

Svelte 是一個 compile-time UI framework，核心概念為 component、reactivity（runes）與 render。Svelte 在建置階段將元件編譯為高效的原生 JavaScript，執行時期不需要虛擬 DOM diff。

- **何時用**：需要輕量、高效能的互動式 UI；希望寫更少的 boilerplate；中小型到大型前端應用皆適合。
- **何時不用**：純靜態內容且完全不需互動；團隊已深度投入另一個框架且無遷移需求。

### 2. SvelteKit — 全端應用框架

SvelteKit 是基於 Svelte 的 framework，幫你處理 routing、SSR（Server-Side Rendering）、build 與 deploy。它之於 Svelte 的關係，如同 Next.js 之於 React。

- **何時用**：需要多頁路由、SEO、伺服器端渲染、API endpoints 或部署至各種平台（Vercel、Cloudflare、Node 等）。
- **何時不用**：只做一個嵌入式 widget 或單一元件庫，不需要路由與 SSR 時，可以單獨使用 Svelte。

### 3. 版本基準釘選

版本基準必須固定到一個日期快照，避免「最新」語意漂移（semantic drift）。本系列以 2026-02-14 為基準日期。

- **何時釘選（pin）**：教學文件、團隊共用開發環境、CI/CD pipeline 中，需確保可重現性。
- **何時浮動（float）**：個人實驗性質的 side project、主動追蹤新功能時，可使用 `latest` 但須留意 breaking changes。

## Step-by-step

1. 安裝 Node.js LTS（建議 22.x）與套件管理器（npm 或 pnpm）。
2. 建立練習專案（後續章節使用）：
   ```bash
   npx sv create svelte5-lab --template minimal --types ts
   ```
3. 進入專案並安裝相依套件、啟動開發伺服器：
   ```bash
   cd svelte5-lab && npm install && npm run dev
   ```
4. 開啟瀏覽器，確認開發伺服器在 `http://localhost:5173` 正常運行，看到預設首頁。
5. 版本基準快照（截至 2026-02-14）：
   - Svelte：`5.50.x`（來源：GitHub releases）。
   - SvelteKit：`2.51.x`（來源：GitHub releases）。
6. 完成 Ch00–04 章打穩 Svelte 基礎（元件語法、runes 響應式、模板邏輯、事件處理）。
7. 完成 Ch05–09 章建立互動模式與狀態管理觀念（stores、context、derived state、跨元件通訊）。
8. 完成 Ch10–19 章串接 SvelteKit 實戰、測試、部署與升級治理（routing、load functions、form actions、SSR/SSG、testing、deployment、version governance）。

## Hands-on Lab

任務：建立你的學習工作區與記錄節奏。

### Foundation 基礎層

- 執行 `npx sv create svelte5-lab --template minimal --types ts` 建立專案。
- 執行 `cd svelte5-lab && npm install && npm run dev` 啟動開發伺服器。
- 在瀏覽器開啟 `http://localhost:5173`，確認首頁可正常顯示。

### Advanced 進階層

- 在專案根目錄新增 `learning-log.md`，記錄今天日期與學習目標。
- 內容至少包含：日期、本次學習目標、預計完成的章節。

### Challenge 挑戰層

- 探索專案目錄結構，辨識以下關鍵檔案的用途：
  - `svelte.config.js`：Svelte 與 SvelteKit 的設定檔，定義 adapter、preprocess 等。
  - `vite.config.ts`：Vite 建置工具的設定檔，SvelteKit 底層使用 Vite。
  - `src/routes/+page.svelte`：SvelteKit 的首頁路由元件，對應 `/` 路徑。
- 嘗試修改 `+page.svelte` 的內容，觀察 HMR（Hot Module Replacement）即時更新。

## Reference Solution

```svelte
<!-- src/routes/+page.svelte -->
<script lang="ts">
  let { data } = $props();
</script>

<h1>Svelte 5 Lab</h1>
<p>Node: {data.nodeVersion}</p>
```

```typescript
// src/routes/+page.ts
import type { PageLoad } from './$types';

export const load: PageLoad = () => {
  return {
    nodeVersion: typeof process !== 'undefined' ? process.version : 'browser'
  };
};
```

```md
# learning-log.md

## 2026-02-14
- Setup: svelte5-lab project created with TypeScript template.
- Goal: finish chapter 00 series overview, explore project structure.
- Key files identified: svelte.config.js, vite.config.ts, src/routes/+page.svelte.
- Blocker: none.
```

## Common Pitfalls

- **使用 Svelte 4 舊教學**：Svelte 5 引入了 runes（`$state`、`$derived`、`$effect`）取代舊的 `$:` 響應式語法與 `export let` props，舊教學的寫法將無法直接套用。
- **未釘選版本**：沒有鎖定版本基準就開始學習，隔週回來發現套件升級導致範例跑不動。
- **一次想學完所有東西**：沒有先完成小里程碑就跳到進階主題，導致基礎不牢。
- **混淆 Svelte 與 SvelteKit**：Svelte 是 compiler / UI framework，SvelteKit 是建構在其上的 application framework；兩者角色不同，學習時需分清界線。

## Checklist

- [ ] 開發環境可正常執行（Node.js 22.x 已安裝）。
- [ ] 已建立 `svelte5-lab` 實作專案。
- [ ] `npm run dev` 可成功啟動開發伺服器。
- [ ] 已建立 `learning-log.md` 學習紀錄檔。
- [ ] 已理解本系列章節安排（Ch00–04 基礎 → Ch05–09 互動與狀態 → Ch10–19 SvelteKit 實戰）。

## Further Reading (official links only)

- [Svelte Documentation](https://svelte.dev/docs)
- [Svelte Tutorial](https://svelte.dev/tutorial)
- [SvelteKit Documentation](https://kit.svelte.dev/docs)
- [Svelte GitHub Repository](https://github.com/sveltejs/svelte)
- [SvelteKit GitHub Repository](https://github.com/sveltejs/kit)
