---
title: Zustand 5 Series Overview / Zustand 5 系列導讀
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, zustand5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: zustand5_complete_notes
chapter: "00"
level: beginner
stack: "TypeScript + React 19 + Next.js 16 App Router + Zustand 5.0.11"
prerequisites: [basic_computer_usage]
---
# Zustand 5 Series Overview / Zustand 5 系列導讀

## Goal

本章目標是完成「系列導覽、版本快照與學習路線」並在 Next.js App Router 專案裡能安全落地。

- 銜接上一章：`basic_computer_usage`。
- 下一章預告：`01_state_management_why_zustand`。

## Prerequisites

- 已完成 `basic_computer_usage`。
- 熟悉 TypeScript 基本語法與 React function component。
- 可執行 `npm run dev` 並觀察畫面狀態變化。

## Core Concepts

1. 邊界先行（Boundary First）
- 何時用：先定義 store 的責任邊界與資料擁有者。
- 何時不用：還在 proof-of-concept，資料流完全不確定。

2. 訂閱最小化（Minimal Subscription）
- 何時用：只訂閱畫面需要的欄位，避免不必要重渲染。
- 何時不用：短期 demo，不追求效能與維護性。

3. 可驗證更新（Verifiable Update）
- 何時用：每個 action 都能在測試或驗收步驟被驗證。
- 何時不用：僅做概念展示，不要求上線品質。

## Step-by-step

1. 建立本章示範路由與檔案夾（建議 `src/app/zustand/ch00`）。
2. 定義 state/action 型別，先寫資料契約再寫實作。
3. 建立 store（必要時加入 middleware）。
4. 在 UI 端只取需要欄位，使用 selector 控制重渲染範圍。
5. 補上 loading/error/empty 的基本狀態顯示。
6. 加入至少 1 條失敗路徑（例：API 失敗、hydrate mismatch）檢查。
7. 執行手動驗收：新增/修改/重整/回復。
8. 記錄本章結論與下一章待改善項目。

## Hands-on Lab

### Foundation
任務：完成 `系列導覽、版本快照與學習路線` 的最小可用版本。

驗收條件：
- 主要功能可操作。
- state 變化符合預期。
- 沒有 TypeScript error。

### Advanced
任務：補齊邊界處理（loading/error/empty）並把 UI 與 store 解耦。

驗收條件：
- 至少 1 條錯誤路徑可重現。
- action 與 UI event 分離。
- selector 只暴露必要資料。

### Challenge
任務：加入性能或韌性強化（shallow、拆 store、reset、rollback、測試其一）。

驗收條件：
- 有明確前後差異（render 次數或錯誤恢復能力）。
- 行為可用測試或步驟穩定重現。
- 有一段可遷移到真實專案的結論。

## Reference Solution

```tsx
export const baseline = {
  snapshotDate: "2026-02-14",
  zustand: "5.0.11",
  react: "19.2.x",
  next: "16.x",
} as const;

export function assertBaseline() {
  return `${baseline.snapshotDate} / zustand ${baseline.zustand}`;
}
```

## Common Pitfalls

- 直接把整個 store 丟進元件，沒有 selector，導致重渲染放大。
- 在 action 裡混入 UI 副作用，讓 store 失去可測試性。
- 忽略 hydration/client boundary，導致 Next.js 畫面與狀態不一致。
- 只測 happy path，沒有覆蓋錯誤與回復路徑。

## Checklist

- [ ] frontmatter 欄位完整，chapter 與檔名一致。
- [ ] store 型別清楚（state/action/selectors）。
- [ ] 至少完成 1 個 Foundation + 1 個 Advanced 驗收條件。
- [ ] 有至少 1 個可重現的錯誤路徑測試。
- [ ] 本章結果可銜接下一章。

## Further Reading (official links only)

- [Primary Doc](https://zustand.docs.pmnd.rs/getting-started/introduction)
- [Secondary Doc](https://github.com/pmndrs/zustand/releases)
- [Zustand Releases](https://github.com/pmndrs/zustand/releases)
