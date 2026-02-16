---
title: Frontend Coverage Matrix
note_type: system
domain: frontend
tags: [system, frontend, audit]
created: 2026-02-16
updated: 2026-02-16
status: active
source: system
---
# Frontend Coverage Matrix

## Coverage Status (2026-02-16)

| Capability Area | Required Topic | Coverage Files | Status |
| --- | --- | --- | --- |
| Browser/Platform | Rendering pipeline | `web_platform_practice/01_rendering_pipeline_and_event_loop.md` | Done |
| Browser/Platform | Event loop | `web_platform_practice/01_rendering_pipeline_and_event_loop.md` | Done |
| Browser/Platform | Web Workers | `web_platform_practice/02_web_workers_storage_cache_and_offline.md` | Done |
| Browser/Platform | Storage strategy | `web_platform_practice/02_web_workers_storage_cache_and_offline.md` | Done |
| Browser/Platform | Cache/Service Worker | `web_platform_practice/02_web_workers_storage_cache_and_offline.md` | Done |
| Security | CSP/CORS/CSRF/XSS | `web_platform_practice/03_web_security_csp_cors_csrf_xss.md` | Done |
| Performance/Delivery | Core Web Vitals | `web_platform_practice/04_core_web_vitals_and_frontend_profiling.md` | Done |
| Performance/Delivery | Profiling | `web_platform_practice/04_core_web_vitals_and_frontend_profiling.md` | Done |
| Performance/Delivery | Bundle analysis | `web_platform_practice/05_bundle_image_font_and_cache_delivery.md` | Done |
| Performance/Delivery | Image/font strategy | `web_platform_practice/05_bundle_image_font_and_cache_delivery.md` | Done |
| Performance/Delivery | Cache delivery | `web_platform_practice/05_bundle_image_font_and_cache_delivery.md` | Done |
| Performance/Delivery | Error budget/release gate | `web_platform_practice/07_capstone_release_readiness.md` | Done |
| Testing/CI | E2E Playwright | `web_platform_practice/06_playwright_contract_mocking_and_ci.md` | Done |
| Testing/CI | Contract/API mocking | `web_platform_practice/06_playwright_contract_mocking_and_ci.md` | Done |
| Testing/CI | CI triage workflow | `web_platform_practice/06_playwright_contract_mocking_and_ci.md` | Done |
| React Capstone | Product delivery task | `react19/20_capstone_product_delivery.md` | Done |
| Svelte Capstone | Product delivery task | `svelte5/26_capstone_product_delivery.md` | Done |
| Tailwind Capstone | Design system delivery | `tailwindcss4/25_capstone_design_system_delivery.md` | Done |
| Zustand Capstone | State platform delivery | `zustand5/20_capstone_state_platform_delivery.md` | Done |

## Contract and Interface Changes

- Series navigation contract:
  - 所有系列 readme 的章節連結命名與實際檔名一致。
  - `40_knowledge/frontend/readme.md` 補齊 `tailwindcss4` 與新系列入口。
- Chapter contract:
  - 於各系列 `quality_rubric.md` 新增 `Evidence` 區塊要求。
  - Capstone 章節全面採用 `Goal..Further Reading + Evidence`。
- Audit artifacts:
  - 新增 `40_knowledge/frontend/link_audit.md`
  - 新增 `40_knowledge/frontend/coverage_matrix.md`

## Remaining Gaps

- 缺真實 production 專案連結與實測 artifact（目前多為章節規格與流程證據）。
- 建議下月補充：至少 1 組 React + 1 組 Svelte 的實際報告。
