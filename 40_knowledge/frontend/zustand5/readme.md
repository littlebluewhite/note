---
title: Zustand 5 Series README
note_type: system
domain: frontend
tags: [system, frontend, zustand5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: system
---
# Zustand 5 Series README

## Summary

- Audience: beginner to practical level.
- Stack baseline: TypeScript + React 19 + Next.js 16 App Router + Zustand 5.0.11.
- Baseline date: 2026-02-14.
- Learning mode: each batch covers 4 chapters with hands-on tasks.

## Batch Learning Route (5 batches)

- Batch 1: `00`, `01`, `02`, `03` (overview/core APIs/actions-selectors)
- Batch 2: `04`, `05`, `06`, `07` (slices/async/persist/devtools-redux)
- Batch 3: `08`, `09`, `10`, `11` (subscription/immer/Next boundary/SSR-hydration)
- Batch 4: `12`, `13`, `14`, `15` (server actions/suspense/optimistic/error recovery)
- Batch 5: `16`, `17`, `18`, `19` (performance/testing/deploy/governance)

## Estimated Time Per Chapter

- Must-read chapters: 90-120 min each.
- Skippable chapters: 70-90 min each.
- Recommended cadence: 4 chapters per week + 1 review day.

## Reading Priority

- Must-read (`必讀`): `00`, `01`, `02`, `03`, `04`, `05`, `06`, `10`, `11`, `12`, `16`, `17`, `19`
- Optional (`可跳讀`): `07`, `08`, `09`, `13`, `14`, `15`, `18`

## Support Documents

- [quality_rubric](quality_rubric.md)
- [exercise_scoring](exercise_scoring.md)
- [monthly_update_log_template](monthly_update_log_template.md)

## Chapters

- [00_series_overview](00_series_overview.md) - 必讀 - 60 min
- [01_state_management_why_zustand](01_state_management_why_zustand.md) - 必讀 - 90 min
- [02_first_store_create_and_use_store](02_first_store_create_and_use_store.md) - 必讀 - 100 min
- [03_actions_selectors_and_derived_state](03_actions_selectors_and_derived_state.md) - 必讀 - 110 min
- [04_slices_pattern_and_store_composition](04_slices_pattern_and_store_composition.md) - 必讀 - 110 min
- [05_async_actions_and_error_handling](05_async_actions_and_error_handling.md) - 必讀 - 110 min
- [06_persist_middleware_and_storage_strategy](06_persist_middleware_and_storage_strategy.md) - 必讀 - 110 min
- [07_devtools_redux_middleware_and_debugging](07_devtools_redux_middleware_and_debugging.md) - 可跳讀 - 85 min
- [08_subscribe_with_selector_and_transient_updates](08_subscribe_with_selector_and_transient_updates.md) - 可跳讀 - 85 min
- [09_immer_middleware_and_complex_updates](09_immer_middleware_and_complex_updates.md) - 可跳讀 - 85 min
- [10_nextjs_app_router_client_boundary_setup](10_nextjs_app_router_client_boundary_setup.md) - 必讀 - 100 min
- [11_ssr_hydration_and_per_request_store](11_ssr_hydration_and_per_request_store.md) - 必讀 - 120 min
- [12_server_actions_and_client_store_sync](12_server_actions_and_client_store_sync.md) - 必讀 - 110 min
- [13_suspense_loading_and_request_state_patterns](13_suspense_loading_and_request_state_patterns.md) - 可跳讀 - 95 min
- [14_forms_optimistic_ui_and_rollback](14_forms_optimistic_ui_and_rollback.md) - 可跳讀 - 95 min
- [15_error_recovery_reset_and_resilience_patterns](15_error_recovery_reset_and_resilience_patterns.md) - 可跳讀 - 90 min
- [16_performance_tuning_selectors_shallow_and_splitting](16_performance_tuning_selectors_shallow_and_splitting.md) - 必讀 - 110 min
- [17_testing_store_and_ui_with_vitest_rtl](17_testing_store_and_ui_with_vitest_rtl.md) - 必讀 - 120 min
- [18_deployment_observability_and_runtime_debug_workflow](18_deployment_observability_and_runtime_debug_workflow.md) - 可跳讀 - 80 min
- [19_upgrade_security_and_monthly_update_playbook](19_upgrade_security_and_monthly_update_playbook.md) - 必讀 - 90 min
