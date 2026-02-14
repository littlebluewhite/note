---
title: Performance Tuning: selectors, shallow, and splitting / 效能調校：selectors、shallow 與拆分
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, zustand5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: zustand5_complete_notes
chapter: "16"
level: beginner
stack: "TypeScript + React 19 + Next.js 16 App Router + Zustand 5.0.11"
prerequisites: [15_error_recovery_reset_and_resilience_patterns]
---
# Performance Tuning: selectors, shallow, and splitting / 效能調校：selectors、shallow 與拆分

## Goal

本章目標是完成「用 selector/shallow/store splitting 做效能優化」並在 Next.js App Router 專案裡能安全落地。

- 銜接上一章：`15_error_recovery_reset_and_resilience_patterns`。
- 下一章預告：`17_testing_store_and_ui_with_vitest_rtl`。

## Prerequisites

- 已完成 `15_error_recovery_reset_and_resilience_patterns`。
- 熟悉 TypeScript 基本語法與 React function component。
- 可執行 `npm run dev` 並觀察畫面狀態變化。

## Core Concepts

1. Selector output stability（v5 重點）
- 何時用：selector 回傳 object/array，需避免每次 render 產生新引用造成重渲染。
- 何時不用：selector 只回傳 primitive（string/number/boolean）。

2. `useShallow` as default path
- 何時用：在 v5 需要對 object selector 做淺比較時，優先用 `useShallow`。
- 何時不用：沿用舊寫法 `useStore(selector, shallow)`（v5 教學應避免）。

3. `createWithEqualityFn` as advanced path
- 何時用：要在 store 層定義 equality 策略，或需要更細緻訂閱控制。
- 何時不用：只為了單一簡單 selector 就過度抽象。

4. Re-render evidence first
- 何時用：先量測 render 次數再優化，避免無效調整。
- 何時不用：只憑感覺改 API。

## Step-by-step

1. 建立本章示範路由與檔案夾（建議 `src/app/zustand/ch16`）。
2. 先做 baseline：在 component 內加入 render counter（或 React Profiler）記錄次數。
3. 以 v5 預設路線重寫 selector：`useShallow((s) => ({ ... }))`。
4. 只訂閱畫面必要欄位，避免 `useStore()` 取整包 state。
5. 將高頻更新與低頻更新拆成不同 store 或 slice，降低影響範圍。
6. 若需要 store 級 equality 策略，改用 `createWithEqualityFn`。
7. 重跑同一操作序列，比較優化前後 render 次數差異。
8. 記錄 migration 決策：哪些地方從舊 equality 寫法改為 v5 推薦寫法。

## v5 Migration Quick Map

- 舊（不建議作為 v5 教學預設）：
  - `useStore((s) => ({ a: s.a, b: s.b }), shallow)`
- 新（v5 預設）：
  - `useStore(useShallow((s) => ({ a: s.a, b: s.b })))`
- 進階（需要 store 級 equality）：
  - `createWithEqualityFn(..., shallow)`

## Hands-on Lab

### Foundation
任務：完成 `用 selector/shallow/store splitting 做效能優化` 的最小可用版本。

驗收條件：
- 主要功能可操作。
- state 變化符合預期。
- 沒有 TypeScript error。
- 有 baseline 與優化後 render 次數記錄。

### Advanced
任務：將至少 1 個舊 equality 用法改為 v5 推薦寫法。

驗收條件：
- `useShallow` 導入後行為與舊版一致。
- selector 只暴露必要資料。
- render 次數可量化下降（或持平且可解釋）。

### Challenge
任務：加入性能或韌性強化（shallow、拆 store、reset、rollback、測試其一）。

驗收條件：
- 有明確前後差異（render 次數或錯誤恢復能力）。
- 行為可用測試或步驟穩定重現。
- 有一段可遷移到真實專案的結論。
- 至少示範一次 `createWithEqualityFn` 進階路線。

## Reference Solution

```tsx
import { create } from 'zustand';
import { useShallow } from 'zustand/react/shallow';

type UiState = {
  a: number;
  b: number;
  c: number;
  setA: (a: number) => void;
};

export const useUiStore = create<UiState>()((set) => ({
  a: 1,
  b: 2,
  c: 3,
  setA: (a) => set({ a }),
}));

export function Widget() {
  const { a, b } = useUiStore(
    useShallow((s) => ({ a: s.a, b: s.b })),
  );
  return <div>{a + b}</div>;
}
```

```tsx
import { shallow } from 'zustand/shallow';
import { createWithEqualityFn } from 'zustand/traditional';

type PanelState = {
  leftOpen: boolean;
  rightOpen: boolean;
  toggleLeft: () => void;
};

export const usePanelStore = createWithEqualityFn<PanelState>()(
  (set) => ({
    leftOpen: false,
    rightOpen: false,
    toggleLeft: () => set((s) => ({ leftOpen: !s.leftOpen })),
  }),
  shallow,
);
```

## Common Pitfalls

- 直接把整個 store 丟進元件，沒有 selector，導致重渲染放大。
- 仍使用舊 equality 寫法 `useStore(selector, shallow)` 當成 v5 預設範例。
- 在 action 裡混入 UI 副作用，讓 store 失去可測試性。
- 忽略 hydration/client boundary，導致 Next.js 畫面與狀態不一致。
- 只測 happy path，沒有覆蓋錯誤與回復路徑。

## Checklist

- [ ] frontmatter 欄位完整，chapter 與檔名一致。
- [ ] store 型別清楚（state/action/selectors）。
- [ ] 至少完成 1 個 Foundation + 1 個 Advanced 驗收條件。
- [ ] 已把至少 1 處舊 equality 用法改為 `useShallow` 或 `createWithEqualityFn`。
- [ ] 有優化前後 render 次數對比。
- [ ] 本章結果可銜接下一章。

## Further Reading (official links only)

- [Primary Doc](https://zustand.docs.pmnd.rs/apis/shallow)
- [Secondary Doc](https://zustand.docs.pmnd.rs/guides/prevent-rerenders-with-use-shallow)
- [createWithEqualityFn](https://zustand.docs.pmnd.rs/apis/create-with-equality-fn)
- [Migrate to v5](https://zustand.docs.pmnd.rs/migrations/migrating-to-v5)
- [Zustand Releases](https://github.com/pmndrs/zustand/releases)
