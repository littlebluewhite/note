---
title: Server Components and Client Boundaries / Server Components 與 Client 邊界
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, react19]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: react19_complete_notes
chapter: "11"
level: beginner
stack: TypeScript + Next.js 16 + React 19.2.x
prerequisites: [10_nextjs_app_router_bootstrap]
---
# Server Components and Client Boundaries / Server Components 與 Client 邊界

## Goal

本章目標是把 server/client 責任切清楚，讓頁面同時擁有可擴展互動與較佳首屏性能，並建立 React Server Components（RSC）安全修補基線。

銜接上一章：你已完成 App Router 骨架，現在要精準決定每個元件該跑在 server 還是 client。

下一章預告：第 12 章會在這個邊界上加入 Server Actions，建立完整提交流程。

## Prerequisites

- 已完成第 10 章。
- 理解 `"use client"` 的基本含義。
- 知道 props 傳遞與型別定義。

## Core Concepts

1. Server components for data + static rendering
- 何時用：首屏資料、SEO 內容、不需瀏覽器互動區塊。
- 何時不用：需要 `useState`, `useEffect`, `onClick` 的互動區塊。

2. Client components for interaction islands
- 何時用：輸入框、彈窗、拖曳、即時本地互動。
- 何時不用：純展示內容硬塞 client。

3. Serialization boundary
- 何時用：server 傳遞純資料（string/number/object）給 client。
- 何時不用：傳 function/class instance/date with custom prototype。

4. RSC security patch discipline
- 何時用：遇到 RSC 相關安全公告時，先做版本區間判斷再決策升級。
- 何時不用：只看功能測試通過就忽略 security patch（高風險）。

## Step-by-step

1. 在 `app/products/page.tsx` 建立 server component，確認資料取得留在 server。
2. 抽出 `ProductFilter.tsx` 成 client component，僅處理互動邏輯。
3. 僅傳遞可序列化資料，避免跨邊界傳遞 function/class instance。
4. 盤點目前 `react` / `react-dom` 版本，套用 RSC 安全區間判斷。
5. 依公告判斷是否受影響：`19.0.0 - 19.1.0`、`19.2.0 - 19.2.2`。
6. 若受影響，優先升級到修補版：`19.1.1` 或 `19.2.3+`。
7. 跑 `npm run build` + 關鍵路由 smoke test，檢查 serialization、hydration、RSC 流程。
8. 把版本判斷、升級決策、回歸證據寫回月檢紀錄。

## Hands-on Lab

### 基礎任務 (Foundation)
任務：完成 server 渲染產品列表 + client 搜尋框。

驗收條件：
- 首屏無需互動即可看到產品列表。
- 搜尋框可即時篩選目前列表。
- 產品資料由 server 傳遞而非 client 初始 fetch。

### 進階任務 (Advanced)
任務：新增 client side 排序控制（價格高低）並完成一次 RSC 安全版本判斷。

驗收條件：
- 排序只影響 client 顯示順序。
- server 資料來源維持不變。
- 排序狀態可重置。
- 明確紀錄是否落在受影響版本區間。

### 挑戰任務 (Challenge)
任務：拆分大型頁面成 1 個 server 區塊 + 2 個 client islands，並完成一次 patch 升級演練。

驗收條件：
- 每個 island 責任清楚。
- 減少 `"use client"` 檔案數。
- build 通過且無邊界錯誤。
- 有「版本判斷 -> 升級決策 -> 回歸檢查」完整記錄。

## Reference Solution

```tsx
type RscSecurityCheck = {
  react: string;
  reactDom: string;
};

function isAffected(v: string): boolean {
  const [major, minor, patch] = v.split(".").map(Number);
  if (major !== 19) return false;
  if (minor === 0) return true;
  if (minor === 1) return patch <= 0;
  if (minor === 2) return patch <= 2;
  return false;
}

export function evaluateRscPatch(input: RscSecurityCheck) {
  const affected = isAffected(input.react) || isAffected(input.reactDom);
  return {
    affected,
    action: affected ? "upgrade_to_19.2.3_plus" : "keep_current_and_monitor",
    affectedRanges: "19.0.0 - 19.1.0, 19.2.0 - 19.2.2",
    patchedRanges: "19.1.1, 19.2.3+",
  };
}
```

```tsx
// src/app/products/page.tsx (Server Component)
import { ProductFilter } from "@/components/ProductFilter";

type Product = { id: string; name: string; price: number };

async function getProducts(): Promise<Product[]> {
  const res = await fetch("https://example.com/api/products", { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load products");
  return res.json() as Promise<Product[]>;
}

export default async function ProductsPage() {
  const products = await getProducts();
  return (
    <main>
      <h1>Products</h1>
      <ProductFilter initialItems={products} />
    </main>
  );
}

// src/components/ProductFilter.tsx (Client Component)
"use client";

import { useMemo, useState } from "react";

type Product = { id: string; name: string; price: number };

export function ProductFilter({ initialItems }: { initialItems: Product[] }) {
  const [keyword, setKeyword] = useState("");
  const visible = useMemo(() => {
    const k = keyword.trim().toLowerCase();
    if (!k) return initialItems;
    return initialItems.filter((item) => item.name.toLowerCase().includes(k));
  }, [keyword, initialItems]);

  return (
    <section>
      <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="Search product" />
      <ul>{visible.map((item) => <li key={item.id}>{item.name} - ${item.price}</li>)}</ul>
    </section>
  );
}
```

## Common Pitfalls

- 把整頁標記 `"use client"` 只為了其中一個按鈕。
- server 傳遞不可序列化資料給 client，導致 runtime/build 錯誤。
- client component 重抓一遍 server 已抓過的資料，造成重工。
- 忘記 server fetch 的快取策略，導致資料更新不符預期。
- 忽略 RSC 安全公告，仍停留在受影響版本區間。

## Checklist

- [ ] `ProductsPage` 仍為 server component（無 `"use client"`）。
- [ ] 至少一個 client island 負責互動。
- [ ] props 僅傳遞可序列化資料。
- [ ] build 不出 serialization 錯誤。
- [ ] client bundle 沒有不必要大型依賴。
- [ ] 已完成 RSC 版本區間判斷與決策記錄。
- [ ] 若受影響，已升級到 `19.1.1` 或 `19.2.3+` 並附回歸證據。

## Further Reading (official links only)

- [React Server Components](https://react.dev/reference/rsc/server-components)
- [Next.js Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Passing Data Between Server and Client Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components#passing-data-from-server-to-client-components)
- [React Security Update Note](https://react.dev/blog/2025/12/11/react-19-upgrade-guide#updates-since-the-release-of-react-19)
