---
title: React 19 Chapter Quality Rubric
note_type: system
domain: frontend
tags: [system, frontend, react19]
created: 2026-02-14
updated: 2026-02-16
status: active
source: system
---
# React 19 Chapter Quality Rubric

## Purpose

定義 `react19` 系列每章最低可教學品質，確保內容深度、可執行性、可驗證性一致。

## Scope

適用檔案：

- `05_events_forms_and_controlled_inputs.md`
- `06_effects_and_common_side_effect_patterns.md`
- `07_data_fetching_client_patterns.md`
- `08_context_and_reducer_state_management.md`
- `09_custom_hooks_and_reuse_patterns.md`
- `10_nextjs_app_router_bootstrap.md`
- `11_server_components_and_client_boundaries.md`
- `12_server_actions_and_form_workflows.md`
- `13_suspense_streaming_and_loading_ui.md`
- `14_transitions_optimistic_ui_and_user_experience.md`
- `15_error_boundaries_not_found_and_recovery.md`
- `16_performance_memoization_and_react_compiler.md`
- `17_testing_with_vitest_and_rtl.md`
- `18_deployment_observability_and_debug_workflow.md`
- `19_upgrade_security_and_monthly_update_playbook.md`
- `20_capstone_product_delivery.md`

## Chapter-level Minimums

- 章節合約：必須含 9 個固定標題，並額外加入 `Evidence` 區塊。
- `Goal`：至少 2 段，含「銜接上一章」與「下一章預告」。
- `Core Concepts`：至少 3 組「何時用 / 何時不用」對照。
- `Step-by-step`：6-10 個可照做步驟，每步可驗證。
- `Hands-on Lab`：需包含三段：Foundation/Advanced/Challenge，且每段有驗收條件。
- `Reference Solution`：至少 1 段完整可貼用範例，需含必要 TypeScript type。
- `Evidence`：至少 2 種可追溯證據（命令輸出、路由、測試報告、截圖路徑）。
- `Common Pitfalls`：至少 4 條，且至少 1 條為 React 19 或 Next.js 邊界陷阱。
- `Checklist`：至少 5 條可量測項目（包含命令、檔案、畫面或測試結果）。
- `Further Reading`：官方來源優先。允許域名：`react.dev`、`nextjs.org`、`github.com/facebook/react/releases`。`17` 章可額外使用 `vitest.dev` 與 `testing-library.com`。

## Code Snippet Standards

- 語境固定：TypeScript + Next.js App Router。
- Snippet 命名具意圖，不使用 `foo`, `bar`。
- 同一段程式碼內避免混用未宣告型別。
- 若涉及 client interaction，需明確 `"use client"` 邊界。
- 若涉及 server action，需明確 `"use server"` 邊界。

## Review Checklist

- [ ] 章節標題完整且順序正確。
- [ ] 核心概念有「用 / 不用」對照。
- [ ] 步驟數量符合 6-10。
- [ ] 三段式練習與驗收條件完整。
- [ ] 參考解答可直接貼進 Next.js 專案。
- [ ] Evidence 區塊可追溯且至少 2 種證據。
- [ ] 陷阱條目 >= 4 且含邊界陷阱。
- [ ] 延伸閱讀域名符合規範。
