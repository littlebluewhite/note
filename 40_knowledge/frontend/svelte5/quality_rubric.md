---
title: Svelte 5 Chapter Quality Rubric
note_type: system
domain: frontend
tags: [system, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-16
status: active
source: system
---
# Svelte 5 Chapter Quality Rubric

## Purpose

定義 `svelte5` 系列每章最低可教學品質，確保內容深度、可執行性、可驗證性一致。

## Scope

適用檔案：

- `05_events_forms_and_bindings.md`
- `06_effects_and_lifecycle.md`
- `07_stores_context_and_state_patterns.md`
- `08_snippets_and_component_composition.md`
- `09_styling_transitions_and_animations.md`
- `10_sveltekit_project_bootstrap.md`
- `11_loading_data_and_server_functions.md`
- `12_form_actions_and_data_mutations.md`
- `13_ssr_streaming_and_page_options.md`
- `14_advanced_routing_and_hooks.md`
- `15_error_handling_and_recovery.md`
- `16_performance_and_fine_grained_reactivity.md`
- `17_testing_with_vitest_and_svelte_testing_library.md`
- `18_deployment_adapters_and_observability.md`
- `19_upgrade_governance_security_and_maintenance.md`
- `26_capstone_product_delivery.md`

## Chapter-level Minimums

- 章節合約：必須含 9 個固定標題，並額外加入 `Evidence` 區塊。
- `Goal`：至少 2 段，含「銜接上一章」與「下一章預告」。
- `Core Concepts`：至少 3 組「何時用 / 何時不用」對照。
- `Step-by-step`：6-10 個可照做步驟，每步可驗證。
- `Hands-on Lab`：需包含三段：Foundation/Advanced/Challenge，且每段有驗收條件。
- `Reference Solution`：至少 1 段完整可貼用範例，需含必要 TypeScript type。
- `Evidence`：至少 2 種可追溯證據（命令輸出、路由、測試報告、截圖路徑）。
- `Common Pitfalls`：至少 4 條，且至少 1 條為 Svelte 5 或 SvelteKit 邊界陷阱。
- `Checklist`：至少 5 條可量測項目（包含命令、檔案、畫面或測試結果）。
- `Further Reading`：官方來源優先。允許域名：`svelte.dev`、`kit.svelte.dev`、`github.com/sveltejs/svelte`、`github.com/sveltejs/kit`。`17` 章可額外使用 `vitest.dev` 與 `testing-library.com`。

## Code Snippet Standards

- 語境固定：TypeScript + SvelteKit。
- Snippet 命名具意圖，不使用 `foo`, `bar`。
- 同一段程式碼內避免混用未宣告型別。
- `.svelte` 檔案中 script block 需明確 `lang="ts"`。
- 若涉及 server-only 邏輯，需放在 `+page.server.ts` 或 `+server.ts`。
- 必須使用 Svelte 5 語法（`$state`、`$props()`、`onclick`、`{#snippet}`），不使用 Svelte 4 語法（`export let`、`on:click`、`<slot>`）。

## Review Checklist

- [ ] 章節標題完整且順序正確。
- [ ] 核心概念有「用 / 不用」對照。
- [ ] 步驟數量符合 6-10。
- [ ] 三段式練習與驗收條件完整。
- [ ] 參考解答可直接貼進 SvelteKit 專案。
- [ ] Evidence 區塊可追溯且至少 2 種證據。
- [ ] 陷阱條目 >= 4 且含邊界陷阱。
- [ ] 延伸閱讀域名符合規範。
