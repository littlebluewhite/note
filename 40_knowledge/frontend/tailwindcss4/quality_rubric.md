---
title: Tailwind CSS 4 Chapter Quality Rubric
note_type: system
domain: frontend
tags: [system, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-16
status: active
source: system
---
# Tailwind CSS 4 Chapter Quality Rubric

## Purpose

定義 `tailwindcss4` 系列每章最低可教學品質，確保內容深度、可執行性、可驗證性一致。

## Scope

適用檔案：

- `00_series_overview.md`
- `01_utility_first_philosophy_and_mental_model.md`
- `02_installation_and_css_first_configuration.md`
- `03_colors_backgrounds_and_opacity.md`
- `04_typography_and_text_styling.md`
- `05_spacing_sizing_and_box_model.md`
- `06_borders_shadows_and_rings.md`
- `07_flexbox_layout.md`
- `08_grid_layout.md`
- `09_positioning_z_index_and_overflow.md`
- `10_responsive_design_and_breakpoints.md`
- `11_state_variants_hover_focus_and_groups.md`
- `12_dark_mode_and_multi_theme_system.md`
- `13_transitions_animations_and_motion.md`
- `14_gradients_filters_and_blend_modes.md`
- `15_container_queries_and_modern_layout_patterns.md`
- `16_theme_directive_and_design_tokens.md`
- `17_custom_utilities_and_variants_with_at_utility.md`
- `18_plugins_extensions_and_ecosystem.md`
- `19_performance_optimization_and_production_build.md`
- `20_tailwind_with_react_component_patterns.md`
- `21_tailwind_with_svelte_component_patterns.md`
- `22_design_system_patterns_and_token_architecture.md`
- `23_migration_from_tailwind_v3_to_v4.md`
- `24_upgrade_governance_security_and_maintenance.md`
- `25_capstone_design_system_delivery.md`

## Chapter-level Minimums

- 章節合約：必須含 9 個固定標題，並額外加入 `Evidence` 區塊。
- `Goal`：至少 2 段，含「銜接上一章」與「下一章預告」。
- `Core Concepts`：至少 3 組「何時用 / 何時不用」對照。
- `Step-by-step`：6-10 個可照做步驟，每步可驗證。
- `Hands-on Lab`：需包含三段：Foundation/Advanced/Challenge，且每段有驗收條件。
- `Reference Solution`：至少 1 段完整可貼用範例，需含完整 HTML 結構或 CSS-first 設定。
- `Evidence`：至少 2 種可追溯證據（命令輸出、視覺回歸報告、截圖路徑、示例頁 URL）。
- `Common Pitfalls`：至少 4 條，且至少 1 條為 Tailwind CSS v4 特有邊界陷阱。
- `Checklist`：至少 5 條可量測項目（包含命令、檔案、畫面或瀏覽器結果）。
- `Further Reading`：官方來源優先。允許域名：`tailwindcss.com`、`github.com/tailwindlabs`。`20` 章可額外使用 `react.dev`。`21` 章可額外使用 `svelte.dev`。

## Code Snippet Standards

- 語境分段：
  - Ch00-15：純 HTML + Vite / Play CDN。
  - Ch16-19：build 設定（CSS-first config、Vite plugin config）。
  - Ch20：React TSX + Next.js App Router。
  - Ch21：Svelte component。
  - Ch22-25：混合語境（HTML/TSX/Svelte 依章節需求）。
- Snippet 命名具意圖，不使用 `foo`, `bar`。
- 每段程式碼應可直接貼入對應語境專案執行。
- 若涉及框架整合，需明確指示框架設定步驟。

## v4 Pitfall Requirement

- 每章 `Common Pitfalls` 至少 1 條必須為 Tailwind CSS v4 特有的邊界情況。
- 常見 v4 陷阱範例：
  - 嘗試使用 `tailwind.config.js`（v3 習慣）。
  - 使用舊版 `@tailwind base; @tailwind components; @tailwind utilities;` 指令。
  - 未理解 CSS-first `@theme` 與 `@import "tailwindcss"` 的新設定方式。
  - 認為需要手動設定 `content: [...]`（v4 自動偵測）。
  - 不知道 v4 預設使用 oklch 色彩空間。
  - 不知道 v4 spacing/grid/columns 數值可自由使用（如 `w-103`、`grid-cols-15`）。

## Review Checklist

- [ ] 章節標題完整且順序正確。
- [ ] 核心概念有「用 / 不用」對照。
- [ ] 步驟數量符合 6-10。
- [ ] 三段式練習與驗收條件完整。
- [ ] 參考解答可直接貼進對應語境專案。
- [ ] Evidence 區塊可追溯且至少 2 種證據。
- [ ] 陷阱條目 >= 4 且含 v4 特有陷阱。
- [ ] 延伸閱讀域名符合規範。
