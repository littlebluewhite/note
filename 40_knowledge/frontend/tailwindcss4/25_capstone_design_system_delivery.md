---
title: Tailwind CSS 4 Capstone Design System Delivery
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4, capstone]
created: 2026-02-16
updated: 2026-02-16
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "25"
level: advanced
stack: Tailwind CSS 4.1.x + Vite/React/Svelte integrations
prerequisites: [tailwindcss4_ch00_ch24]
---
# Tailwind CSS 4 Capstone Design System Delivery

## Goal

完成一套可交付的 Tailwind v4 設計系統實作（token、component、theme、文件、驗收）。

銜接上一章：升級治理。下一章預告：把設計系統轉成團隊共用 release package。

## Prerequisites

- 完成 `00-24` 章。
- 熟悉 `@theme`、`@utility`、variants 與框架整合。
- 可執行 build 與視覺回歸檢查。

## Core Concepts

1. 設計系統是交付介面，不是樣式集合。
- 何時用：多頁、多團隊產品。
- 何時不用：單頁一次性活動。

2. token 與元件契約要穩定。
- 何時用：長期維護。
- 何時不用：快速原型。

3. 視覺回歸要自動化。
- 何時用：頻繁改版。
- 何時不用：幾乎不變的頁面。

## Step-by-step

1. 功能需求：Button/Input/Card/Table 四類元件與三種語意狀態。
2. 非功能需求：dark mode、響應式、a11y 對比度、bundle 控制。
3. 觀測指標：CSS bundle size、visual regression delta、theme token 覆蓋率。
4. 驗收腳本：`npm run lint && npm run build && npm run test:visual`。
5. 回歸清單：亮暗主題、sm/md/lg、disabled/error/focus 狀態。
6. 針對 v3->v4 兼容點做一輪 migration 測試。

## Hands-on Lab

### Foundation
- 完成 token + 基礎元件庫。

### Advanced
- 完成 React/Svelte 雙框架示例頁。

### Challenge
- 產出視覺回歸報告並達成零阻斷差異。

## Reference Solution

```css
@theme {
  --color-brand-500: oklch(62% 0.19 258);
  --radius-control: 0.625rem;
}
```

## Evidence

- Demo pages: `/design-system/react`, `/design-system/svelte`
- Commands: `npm run test:visual`, `npm run build`
- Artifacts: `reports/tailwind-capstone/`

## Common Pitfalls

- 混用舊 v3 config 與 v4 CSS-first 模式。
- token 命名無治理，後續難以維護。
- 不做主題與狀態回歸測試。
- 視覺差異有發現但無 gate。

## Checklist

- [ ] 功能需求元件齊全。
- [ ] 非功能需求達標。
- [ ] 驗收腳本可重跑。
- [ ] 回歸清單可執行。
- [ ] migration 測試結果已記錄。

## Further Reading

- https://tailwindcss.com/docs
- https://tailwindcss.com/docs/theme
- https://github.com/tailwindlabs/tailwindcss
