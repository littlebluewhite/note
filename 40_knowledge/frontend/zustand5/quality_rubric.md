---
title: Zustand 5 Chapter Quality Rubric
note_type: system
domain: frontend
tags: [system, frontend, zustand5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: system
---
# Zustand 5 Chapter Quality Rubric

## Purpose

定義 `zustand5` 系列每章最低教學品質，確保內容深度、可執行性、可驗證性一致。

## Scope

適用檔案：`00` 到 `19` 全章。

## Chapter-level Minimums

- 章節合約：必須含 9 個固定標題。
- `Goal`：至少 2 段，含「銜接上一章」與「下一章預告」。
- `Core Concepts`：至少 3 組「何時用 / 何時不用」對照。
- `Step-by-step`：6-10 個可照做步驟，每步可驗證。
- `Hands-on Lab`：需含 Foundation / Advanced / Challenge，且每段有驗收條件。
- `Reference Solution`：至少 1 段可貼用 TypeScript 範例，含狀態型別。
- `Common Pitfalls`：至少 4 條，且至少 1 條為 React/Next/Zustand 邊界陷阱。
- `Checklist`：至少 5 條可量測項目。
- `Further Reading`：官方來源優先，推薦 `zustand.docs.pmnd.rs`、`github.com/pmndrs/zustand`、`nextjs.org`、`react.dev`。

## Zustand-specific Requirements

- 至少在對應章節覆蓋：`create`, `createStore`, `useStore`, `set/get/subscribe`。
- middleware 章節需覆蓋：`persist`, `devtools`, `redux`, `subscribeWithSelector`, `immer`。
- Next.js 章節需說明 `"use client"` 邊界、SSR/hydration 與 per-request store。

## Review Checklist

- [ ] 章節標題完整且順序正確。
- [ ] 每章都有用 / 不用邊界判斷。
- [ ] 範例可在 TypeScript + Next.js App Router 專案落地。
- [ ] 有明確驗收步驟與至少一個可測試點。
- [ ] 官方連結可追溯且版本敘述含日期快照。
