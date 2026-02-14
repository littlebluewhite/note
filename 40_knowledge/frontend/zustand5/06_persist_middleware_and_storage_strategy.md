---
title: Persist Middleware and Storage Strategy / Persist 中介層與儲存策略
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, zustand5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: zustand5_complete_notes
chapter: "06"
level: beginner
stack: "TypeScript + React 19 + Next.js 16 App Router + Zustand 5.0.11"
prerequisites: [05_async_actions_and_error_handling]
---
# Persist Middleware and Storage Strategy / Persist 中介層與儲存策略

## Goal

本章目標是完成「用 persist 進行持久化與版本遷移」，並在 Next.js App Router 專案裡建立可驗證的一致性流程。

- 銜接上一章：`05_async_actions_and_error_handling`。
- 下一章預告：`07_devtools_redux_middleware_and_debugging`。

## Prerequisites

- 已完成 `05_async_actions_and_error_handling`。
- 熟悉 TypeScript 基本語法與 React function component。
- 可執行 `npm run dev` 並觀察畫面狀態變化。

## Core Concepts

1. Persist scope design
- 何時用：只持久化跨重整真正需要保留的資料（搭配 `partialize`）。
- 何時不用：把 loading/error 等暫態欄位一起寫進 storage。

2. Versioned migration
- 何時用：資料結構調整時以 `version` + `migrate` 維持可升級性。
- 何時不用：直接改欄位名稱，導致舊資料無法使用。

3. Rapid updates consistency
- 何時用：高頻更新（連續輸入、多次 action）下驗證 storage 與 in-memory 一致。
- 何時不用：只驗 happy path 的單次更新。

## Step-by-step

1. 建立本章示範路由與檔案夾（建議 `src/app/zustand/ch06`）。
2. 定義 state/action 與持久化契約，先決定哪些欄位可落盤。
3. 以 `persist` + `createJSONStorage` 建立 store，明確指定 `name` 與 `version`。
4. 用 `partialize` 限縮寫入欄位，避免暫態狀態污染。
5. 實作 `migrate`，處理舊版欄位映射到新版結構。
6. 在 Next.js client 邊界驗證 hydration 行為。
7. 建立 rapid updates 驗收：連續更新後比對 storage 與 in-memory 最終值。
8. 記錄 persist 風險與修補策略（migrate、hydration、一致性）。

## Hands-on Lab

### Foundation
任務：完成 `用 persist 進行持久化與版本遷移` 的最小可用版本。

驗收條件：
- 主要功能可操作。
- state 變化符合預期。
- 沒有 TypeScript error。
- 重整後能正確還原持久化欄位。

### Advanced
任務：實作 `version` + `migrate`，並驗證舊資料升級成功。

驗收條件：
- 舊版 storage 資料可遷移到新版。
- migration 後不遺失關鍵欄位。
- hydrate 後 UI 狀態正確。

### Challenge
任務：加入 rapid updates 一致性驗收（高頻更新後比對 storage 與 in-memory）。

驗收條件：
- 高頻更新後最終狀態一致。
- 行為可用測試或步驟穩定重現。
- 有一段可遷移到真實專案的結論。

## Reference Solution

```tsx
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

type SessionState = {
  token: string;
  profileVersion: number;
  setToken: (token: string) => void;
  clear: () => void;
};

export const useSessionStore = create<SessionState>()(
  persist(
    (set) => ({
      token: '',
      profileVersion: 2,
      setToken: (token) => set({ token }),
      clear: () => set({ token: '' }),
    }),
    {
      name: 'session-store',
      version: 2,
      storage: createJSONStorage(() => localStorage),
      partialize: (s) => ({ token: s.token, profileVersion: s.profileVersion }),
      migrate: (state: any, version) => {
        if (version < 2) {
          return {
            token: state?.accessToken ?? '',
            profileVersion: 2,
          };
        }
        return state as SessionState;
      },
    },
  ),
);

export async function runRapidUpdateCheck(iterations = 200) {
  for (let i = 0; i < iterations; i += 1) {
    useSessionStore.getState().setToken(`t-${i}`);
  }
  await Promise.resolve();

  const memoryToken = useSessionStore.getState().token;
  const raw = localStorage.getItem('session-store');
  const persisted = raw ? JSON.parse(raw) : null;
  return persisted?.state?.token === memoryToken;
}
```

## Common Pitfalls

- 把整個 state 全部持久化，導致暫態欄位污染與過期資料問題。
- 忘記 `version` + `migrate`，一改欄位就破壞舊資料。
- 忽略 hydration/client boundary，導致 Next.js 畫面與狀態不一致。
- 只測單次更新，沒驗證 rapid updates 的最終一致性。

## Checklist

- [ ] frontmatter 欄位完整，chapter 與檔名一致。
- [ ] store 型別清楚（state/action/selectors）。
- [ ] 至少完成 1 個 Foundation + 1 個 Advanced 驗收條件。
- [ ] 有 `version` 與 `migrate` 實作與驗證。
- [ ] 有 rapid updates 一致性檢核（storage vs in-memory）。

## Further Reading (official links only)

- [Primary Doc](https://zustand.docs.pmnd.rs/middlewares/persist)
- [Secondary Doc](https://zustand.docs.pmnd.rs/integrations/persisting-store-data)
- [Migrate to v5](https://zustand.docs.pmnd.rs/migrations/migrating-to-v5)
- [Zustand Releases](https://github.com/pmndrs/zustand/releases)
