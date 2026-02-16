---
title: Design Pattern Chapter Quality Rubric
note_type: system
domain: design_pattern
tags: [system, design-pattern]
created: 2026-02-17
updated: 2026-02-17
status: active
source: system
---
# Design Pattern Chapter Quality Rubric

## Purpose

定義 `design_pattern` 系列每章最低可教學品質，確保內容深度、雙語實作正確性、可執行性一致。

## Scope

適用檔案：

- `creational/01_singleton.md`
- `creational/02_factory_method.md`
- `creational/03_abstract_factory.md`
- `creational/04_builder.md`
- `creational/05_prototype.md`
- `structural/06_adapter.md`
- `structural/07_bridge.md`
- `structural/08_composite.md`
- `structural/09_decorator.md`
- `structural/10_facade.md`
- `structural/11_flyweight.md`
- `structural/12_proxy.md`
- `behavioral/13_chain_of_responsibility.md`
- `behavioral/14_command.md`
- `behavioral/15_iterator.md`
- `behavioral/16_mediator.md`
- `behavioral/17_memento.md`
- `behavioral/18_observer.md`
- `behavioral/19_state.md`
- `behavioral/20_strategy.md`
- `behavioral/21_template_method.md`
- `behavioral/22_visitor.md`
- `behavioral/23_interpreter.md`
- `modern/24_functional_options.md`
- `modern/25_newtype.md`
- `modern/26_typestate.md`
- `modern/27_repository.md`
- `modern/28_middleware.md`
- `modern/29_worker_pool.md`
- `modern/30_circuit_breaker.md`
- `modern/31_raii.md`

## Frontmatter Requirements

每章 frontmatter 必須包含以下欄位：

| 欄位 | 型別 | 說明 |
|------|------|------|
| `title` | string | 模式英文名 / 中文名 |
| `note_type` | string | 固定為 `knowledge` |
| `domain` | string | 固定為 `design_pattern` |
| `category` | string | `creational` / `structural` / `behavioral` / `modern` |
| `tags` | list | 至少含 `design-pattern`, category, `go`, `rust`, pattern kebab name |
| `created` | date | 建立日期 |
| `updated` | date | 最後更新日期 |
| `status` | string | `active` / `draft` |
| `source` | string | 固定為 `knowledge` |
| `series` | string | 固定為 `design_pattern` |
| `chapter` | string | 兩位數字串，如 `"01"` |
| `level` | string | `beginner` / `intermediate` / `advanced` |
| `review_interval_days` | int | 複習間隔天數 |
| `next_review` | date | 下次複習日期 |

## Chapter-level Minimums

- 章節合約：必須含以下固定標題，順序不可調換。
  1. `Intent / 意圖`
  2. `Problem / 問題情境`
  3. `Solution / 解決方案`
  4. `Structure / 結構`
  5. `Participants / 參與者`
  6. `Go 實作`
  7. `Rust 實作`
  8. `Go vs Rust 對照表`
  9. `When to Use / 適用場景`
  10. `When NOT to Use / 不適用場景`
  11. `Real-World Examples / 真實世界案例`
  12. `Related Patterns / 相關模式`
  13. `Pitfalls / 常見陷阱`
  14. `References / 參考資料`

### Intent / 意圖

- 1-2 句話，明確表達模式的核心目的。
- 需讓讀者在 10 秒內理解「這個模式做什麼」。

### Problem / 問題情境

- 至少 1 個具體場景（非抽象描述）。
- 場景需包含「沒有此模式時的痛點」。

### Structure / 結構

- 必須包含 Mermaid `classDiagram`。
- Diagram 需覆蓋所有 Participants。

### Go 實作

- 完整可編譯可執行，含 `package main`、`import`、`func main()`。
- 程式碼尾端需以註解標注預期輸出（`// Output:` 區塊）。
- 語法需符合 Go 1.24+。
- 變數與函式命名具意圖，不使用 `foo`, `bar`。

### Rust 實作

- 完整可編譯可執行，含 `fn main()`。
- 程式碼尾端需以註解標注預期輸出（`// Output:` 區塊）。
- 語法需符合 Rust 2024 edition。
- 變數與函式命名具意圖，不使用 `foo`, `bar`。

### Go vs Rust 對照表

- 至少 3 個面向的比較（如：型別系統、並行安全、慣用寫法等）。

### When to Use / 適用場景

- 至少 2 條具體使用情境。

### When NOT to Use / 不適用場景

- 至少 2 條具體不適用情境。

### Real-World Examples / 真實世界案例

- 至少 1 個標準庫或知名開源專案的實際案例。
- 需附上專案名稱與簡要說明。

### Related Patterns / 相關模式

- 至少列出 1 個相關模式。
- 使用相對路徑連結，如 `[Builder](04_builder.md)`。

### Pitfalls / 常見陷阱

- 至少 2 條。
- 需針對 Go 與 Rust 各至少提及 1 個語言特有陷阱。

### References / 參考資料

- 至少列出 1 個參考來源。
- 優先使用官方文件或經典書籍。

## Review Checklist

- [ ] Frontmatter 所有必填欄位完整。
- [ ] 14 個固定標題完整且順序正確。
- [ ] Intent 精簡且準確（1-2 句）。
- [ ] Problem 含具體場景。
- [ ] Structure 含 Mermaid classDiagram。
- [ ] Go 程式碼可直接編譯執行。
- [ ] Rust 程式碼可直接編譯執行。
- [ ] 對照表至少 3 行。
- [ ] 適用 / 不適用各至少 2 條。
- [ ] Real-World Examples 至少 1 個。
- [ ] Related Patterns 至少 1 個且含相對連結。
- [ ] Pitfalls 至少 2 條且含語言特有陷阱。
