---
title: "Testing with Vitest and STL / 測試"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "17"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [16_performance_and_fine_grained_reactivity]
---
# Testing with Vitest and STL / 測試

## Goal

建立完整的測試策略，使用 Vitest + @testing-library/svelte 測試 Svelte 5 元件與 SvelteKit 功能。

測試是重構與持續交付的安全網。透過掌握 Vitest 的設定、元件測試的 render/query/assert 模式、以及 SvelteKit load function 的單元測試技巧，你能在 Svelte 5 的 runes 系統下建立高信心的自動化測試覆蓋，確保每次變更都不會破壞既有功能。

- **銜接上一章**：Ch16 優化了效能，現在要確保程式碼品質有測試保障。
- **下一章預告**：Ch18 將學習部署、adapters 與可觀測性。

## Prerequisites

- 已完成第 16 章（Performance and Fine-grained Reactivity），理解 `$state`、`$derived`、`$effect` 的運作方式與效能特性。
- 熟悉基本的測試概念（unit test、assertion、mock）。
- `svelte5-lab` 專案可正常執行 `npm run dev`。

## Core Concepts

### 1. Vitest + @testing-library/svelte setup

Vitest 是基於 Vite 的測試框架，與 SvelteKit 共用同一套建置管線。`@testing-library/svelte` 提供以使用者行為為中心的測試工具，鼓勵你「像使用者一樣測試」。

- `@testing-library/svelte` 提供 `render`, `screen`, `fireEvent`, `cleanup` 等核心 API。
- `@sveltejs/vite-plugin-svelte` 處理 `.svelte` 檔案的 transform，讓 Vitest 能理解 Svelte 元件。
- 測試環境可選 `jsdom`（功能完整、相容性高）或 `happy-dom`（速度更快、API 覆蓋略少）。
- `setupFiles` 中統一引入 `@testing-library/jest-dom/vitest`，為所有測試加上 DOM matcher（如 `toBeInTheDocument()`）。

| 何時用 unit test | 何時用 integration test | 何時用 e2e test |
|---|---|---|
| 測試單一函式或元件的邏輯 | 測試多個元件或模組的協作 | 測試完整的使用者流程 |
| Pure utility functions、validators | 表單元件 + 驗證 + API 呼叫 | 登入 → 建立資料 → 登出 |
| 執行快、回饋迅速 | 中等速度、涵蓋更多邊界條件 | 速度慢、但最接近真實使用情境 |
| Vitest + @testing-library/svelte | Vitest + @testing-library/svelte | Playwright / Cypress |

### 2. Testing `$state` / `$derived` components

Svelte 5 的 runes（`$state`、`$derived`）在測試環境中完全正常運作。`@testing-library/svelte` 的 `render` 會建立真實的 Svelte 元件實例，所有 reactivity 機制都會觸發。

- `render(Component, { props })` 建立元件並掛載到 jsdom。
- 使用者互動（`fireEvent.click`、`fireEvent.input`）觸發事件後，Svelte 的 reactivity 會自動更新 DOM。
- `await tick()` 可強制等待 Svelte 完成 DOM 批次更新。
- `screen.getByText()`、`screen.getByRole()` 等 query 會讀取最新的 DOM 狀態。

| 何時需要 `tick()` | 何時 testing-library 自動等待 |
|---|---|
| `$effect` 中的非同步副作用需要額外一個 microtask 才完成 | `fireEvent` 回傳 Promise，await 後 DOM 通常已更新 |
| 手動修改 `$state` 變數後立即斷言 | 使用 `waitFor()` 包裹斷言時，自動重試直到通過 |
| 多層 `$derived` 鏈需要多次 microtask 才完成傳播 | `findBy*` 系列 query 內建 polling 等待機制 |

### 3. Testing SvelteKit load functions

SvelteKit 的 `load` 函式本質上是一個接收 `LoadEvent` 並回傳資料的非同步函式，可以直接 import 並呼叫來進行單元測試。

- 直接 `import { load } from './+page.server'`，傳入模擬的參數物件。
- Mock `fetch`：傳入 `vi.fn()` 控制 API 回應。
- Mock `params`：傳入測試用的路由參數。
- Mock `cookies`：傳入包含 `get`、`set` 等方法的模擬物件。

| 何時直接測試 load function | 何時用 integration test |
|---|---|
| load 函式包含複雜的資料轉換邏輯 | 需要測試 load 資料如何渲染在頁面上 |
| 需要驗證不同參數組合的回傳結果 | 需要測試 load 失敗時的錯誤頁面顯示 |
| 回傳值的結構與型別需要嚴格驗證 | 涉及多個 layout load 函式的資料合併 |
| 測試速度要求高（不需掛載元件） | 需要測試 streaming 的漸進式渲染行為 |

### 4. Mocking `$app/stores`, `$app/navigation`

SvelteKit 的 `$app/*` 模組在測試環境中無法自動解析，需要透過 Vitest 的 alias 或 `vi.mock()` 提供模擬實作。

- 在 `vitest.config.ts` 的 `resolve.alias` 中將 `$app/navigation` 指向自訂的 mock 檔案。
- Mock `goto`：`vi.fn()` 模擬導航函式，測試中斷言呼叫參數。
- Mock `invalidate` / `invalidateAll`：驗證元件是否正確觸發資料重新載入。
- Mock `page` store：提供 `readable` store 模擬當前頁面的 `url`、`params`、`data`。

| 何時用 alias mock | 何時用 `vi.mock()` |
|---|---|
| 專案中所有測試都需要相同的 mock | 個別測試需要不同的 mock 行為 |
| 設定一次、全域生效 | 需要在每個測試中動態調整回傳值 |
| `$app/navigation`、`$app/stores` 等穩定模組 | 第三方 library 或專案內部模組 |

### 5. E2E Testing with Playwright

Playwright 是 Microsoft 開源的瀏覽器自動化框架，用於撰寫端到端（End-to-End）測試。在測試金字塔中，E2E 測試位於最上層，數量最少但覆蓋面最廣。

**測試金字塔**：

```
        /  E2E  \        ← 少量，最慢，最接近真實使用者體驗（Playwright）
       /----------\
      / Integration \    ← 適量，中等速度，測試元件與模組協作（Vitest + STL）
     /----------------\
    /    Unit Tests     \ ← 大量，最快，測試單一函式或元件邏輯（Vitest）
   /--------------------\
```

| 比較項目 | Vitest + @testing-library/svelte | Playwright |
|---|---|---|
| 測試層級 | Unit / Integration | End-to-End |
| 執行環境 | jsdom / happy-dom（模擬） | 真實瀏覽器（Chromium / Firefox / WebKit） |
| 速度 | 快（毫秒級） | 慢（秒級） |
| 適用場景 | 單一元件行為、utility 函式、load function | 完整使用者流程（登入→操作→登出） |
| CSS / 視覺測試 | 無法測試（jsdom 不算 CSS） | 支援 screenshot 比對 |
| 網路請求 | 需 mock（`vi.fn()`） | 真實請求（或 route intercept） |
| 跨瀏覽器 | 不支援 | Chromium / Firefox / WebKit 並行 |

- **何時用 Playwright**：需要測試完整使用者流程（填表→提交→看到結果）；需要跨瀏覽器驗證；需要測試 CSS 排版或視覺效果；CI/CD 中的 smoke test。
- **何時不用 Playwright**：單一元件的邏輯驗證（用 Vitest 更快）；純函式的單元測試；頻繁迭代的開發階段（E2E 太慢影響 feedback loop）。

## Step-by-step

### Step 1：安裝測試依賴

安裝 Vitest、Svelte Testing Library、jest-dom matcher 和 jsdom 環境：

```bash
npm install -D vitest @testing-library/svelte @testing-library/jest-dom jsdom
```

這四個套件各司其職：

- `vitest`：測試 runner 與斷言庫。
- `@testing-library/svelte`：提供 `render`、`screen`、`fireEvent` 等元件測試 API。
- `@testing-library/jest-dom`：擴充 `expect` 的 DOM matcher（如 `toBeInTheDocument()`、`toHaveTextContent()`）。
- `jsdom`：在 Node.js 中模擬瀏覽器 DOM 環境。

### Step 2：設定 `vitest.config.ts`

在專案根目錄建立 `vitest.config.ts`，設定 Svelte plugin、jsdom 環境與 alias：

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte({ hot: false })],
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.ts'],
    globals: true,
    setupFiles: ['./src/tests/setup.ts']
  },
  resolve: {
    alias: {
      $lib: '/src/lib',
      '$app/navigation': '/src/tests/mocks/navigation.ts',
      '$app/stores': '/src/tests/mocks/stores.ts',
      '$app/environment': '/src/tests/mocks/environment.ts'
    }
  }
});
```

重點：`hot: false` 關閉 HMR（測試環境不需要），`globals: true` 讓 `describe`、`it`、`expect` 不需要每次 import。

### Step 3：建立測試 setup 檔案與 mock 模組

建立 `src/tests/setup.ts`，引入 jest-dom matcher 並設定自動 cleanup：

```ts
// src/tests/setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/svelte';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```

建立 `$app/navigation` 的 mock：

```ts
// src/tests/mocks/navigation.ts
import { vi } from 'vitest';

export const goto = vi.fn();
export const invalidate = vi.fn();
export const invalidateAll = vi.fn();
export const prefetch = vi.fn();
```

重點：`cleanup()` 在每個測試結束後卸載元件，避免測試之間互相污染。

### Step 4：撰寫第一個測試 — render 元件並斷言文字內容

建立一個簡單的 Counter 元件和對應的測試：

```ts
// src/lib/components/__tests__/Counter.test.ts
import { render, screen } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Counter from '../Counter.svelte';

describe('Counter', () => {
  it('renders initial count', () => {
    render(Counter, { props: { initial: 5 } });
    expect(screen.getByText('Count: 5')).toBeInTheDocument();
  });
});
```

重點：`render(Component, { props })` 將元件掛載到 jsdom，`screen.getByText()` 在整個 document 中搜尋包含指定文字的元素。

### Step 5：測試使用者互動 — `fireEvent.click` 與狀態變更

模擬使用者點擊按鈕，斷言 `$state` 驅動的 DOM 更新：

```ts
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Counter from '../Counter.svelte';

describe('Counter', () => {
  it('increments on click', async () => {
    render(Counter, { props: { initial: 0 } });
    const button = screen.getByRole('button', { name: 'Increment' });

    await fireEvent.click(button);

    expect(screen.getByText('Count: 1')).toBeInTheDocument();
  });
});
```

重點：`fireEvent.click()` 回傳 Promise，使用 `await` 等待事件處理與 DOM 更新完成後再斷言。

### Step 6：測試表單提交 — 填寫輸入、提交、斷言驗證錯誤

模擬使用者填寫表單並提交，斷言驗證邏輯是否正確顯示錯誤訊息：

```ts
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import LoginForm from '../LoginForm.svelte';

describe('LoginForm', () => {
  it('shows validation error for empty email', async () => {
    render(LoginForm);

    const submitButton = screen.getByRole('button', { name: 'Login' });
    await fireEvent.click(submitButton);

    expect(screen.getByText('Email is required')).toBeInTheDocument();
  });

  it('accepts valid input', async () => {
    render(LoginForm);

    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');

    await fireEvent.input(emailInput, { target: { value: 'user@example.com' } });
    await fireEvent.input(passwordInput, { target: { value: 'password123' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Login' }));

    expect(screen.queryByText('Email is required')).not.toBeInTheDocument();
  });
});
```

重點：使用 `screen.queryByText()` 搭配 `.not.toBeInTheDocument()` 斷言某個元素不存在（`getByText` 找不到會直接 throw）。

### Step 7：測試 `$state` reactivity — 輸入變更觸發 `$derived` 更新

驗證 `$derived` 能正確反映 `$state` 的變更：

```ts
describe('Counter', () => {
  it('shows doubled value', async () => {
    render(Counter, { props: { initial: 3 } });
    expect(screen.getByText('Doubled: 6')).toBeInTheDocument();

    const button = screen.getByRole('button', { name: 'Increment' });
    await fireEvent.click(button);

    expect(screen.getByText('Doubled: 8')).toBeInTheDocument();
  });
});
```

重點：不需要手動觸發 `tick()` — `await fireEvent.click()` 完成後，Svelte 的 reactivity 已經完成 DOM 更新，`$derived` 的值也已經同步反映。

### Step 8：測試 SvelteKit load function — mock 參數並斷言回傳資料

直接 import load 函式進行單元測試：

```ts
// src/routes/blog/__tests__/page.server.test.ts
import { describe, it, expect, vi } from 'vitest';
import { load } from '../+page.server';

describe('blog load function', () => {
  it('returns posts', async () => {
    const result = await load({
      params: {},
      fetch: vi.fn(),
      cookies: { get: vi.fn(), set: vi.fn() } as any,
      locals: { user: null },
    } as any);

    expect(result.posts).toBeDefined();
    expect(result.posts.length).toBeGreaterThan(0);
  });
});
```

重點：使用 `as any` 跳過完整的 `LoadEvent` 型別檢查，只提供測試所需的屬性。若 load 函式依賴 `fetch`，傳入 `vi.fn().mockResolvedValue(...)` 控制回應。

### Step 9：Mock `$app/navigation` — 測試呼叫 `goto()` 的元件

驗證元件在特定操作後正確呼叫 `goto()` 導航：

```ts
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import { goto } from '$app/navigation';
import LogoutButton from '../LogoutButton.svelte';

describe('LogoutButton', () => {
  it('navigates to login page on logout', async () => {
    render(LogoutButton);

    await fireEvent.click(screen.getByRole('button', { name: 'Logout' }));

    expect(goto).toHaveBeenCalledWith('/login');
  });
});
```

重點：因為 `vitest.config.ts` 中已將 `$app/navigation` alias 到 mock 檔案，`goto` 是一個 `vi.fn()`，可以直接斷言呼叫參數。

### Step 10：測試非同步元件 — 使用 `waitFor` 等待非同步操作

元件中有非同步操作（如 API 呼叫）時，使用 `waitFor` 等待 DOM 更新：

```ts
import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import UserProfile from '../UserProfile.svelte';

describe('UserProfile', () => {
  it('displays user name after loading', async () => {
    render(UserProfile, { props: { userId: '123' } });

    // 等待非同步資料載入完成
    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    render(UserProfile, { props: { userId: '123' } });
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});
```

重點：`waitFor` 會重複執行 callback 直到不 throw 或 timeout。預設 timeout 1000ms，可透過第二個參數調整：`waitFor(callback, { timeout: 3000 })`。

### Step 11：安裝 Playwright

安裝 Playwright 測試框架與瀏覽器引擎：

```bash
npm install -D @playwright/test
npx playwright install
```

`npx playwright install` 會下載 Chromium、Firefox、WebKit 三個瀏覽器引擎。若只需要特定瀏覽器：`npx playwright install chromium`。

### Step 12：設定 `playwright.config.ts`

在專案根目錄建立 `playwright.config.ts`，設定 webServer 指向 SvelteKit dev server：

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  testMatch: '**/*.e2e.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    }
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000
  }
});
```

重點：`webServer` 設定讓 Playwright 自動啟動 SvelteKit dev server。`reuseExistingServer: !process.env.CI` 表示本地開發時會重用已啟動的 server，CI 環境則每次重新啟動。

### Step 13：撰寫 E2E 測試 — 表單提交與導航

建立 `e2e/todo.e2e.ts`，測試完整的 todo 使用者流程：

```ts
// e2e/todo.e2e.ts
import { test, expect } from '@playwright/test';

test.describe('Todo App', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/todo');
  });

  test('should add a new todo', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Buy groceries');
    await input.press('Enter');

    await expect(page.getByText('Buy groceries')).toBeVisible();
    await expect(page.getByText('1 item remaining')).toBeVisible();
  });

  test('should toggle todo completion', async ({ page }) => {
    // 先新增一筆
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Learn Playwright');
    await input.press('Enter');

    // 勾選完成
    const checkbox = page.getByRole('checkbox');
    await checkbox.check();

    await expect(page.getByText('0 items remaining')).toBeVisible();
  });

  test('should navigate between pages', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL('/');

    await page.getByRole('link', { name: 'Todo' }).click();
    await expect(page).toHaveURL('/todo');
  });
});

test.describe('Auth Flow', () => {
  test('should redirect unauthenticated user to login', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/);
  });

  test('should login and redirect to dashboard', async ({ page }) => {
    await page.goto('/login');

    await page.getByLabel('Email').fill('admin@example.com');
    await page.getByLabel('Password').fill('password');
    await page.getByRole('button', { name: 'Login' }).click();

    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Welcome')).toBeVisible();
  });
});
```

執行 E2E 測試：

```bash
# 執行所有 E2E 測試
npx playwright test

# 只執行 chromium
npx playwright test --project=chromium

# 開啟 UI 模式（互動式除錯）
npx playwright test --ui

# 查看測試報告
npx playwright show-report
```

重點：Playwright 使用 locator API（`getByRole`、`getByLabel`、`getByText`）查詢元素，與 @testing-library 的理念一致——以使用者可見的方式查詢，鼓勵 accessible 的 HTML。

## Hands-on Lab

### Foundation：Counter 元件測試

**任務：為 Counter 元件撰寫完整的測試。**

1. 建立 `src/lib/components/Counter.svelte`（若尚未存在），包含 `initial` prop、increment/decrement 按鈕、顯示 count 與 doubled 值。
2. 建立 `src/lib/components/__tests__/Counter.test.ts`。
3. 撰寫以下測試案例：
   - 初始化時顯示正確的 count 值。
   - 點擊 Increment 按鈕後 count 加 1。
   - 點擊 Decrement 按鈕後 count 減 1。
   - `$derived` 的 doubled 值始終正確。

**驗收條件：**
- `npx vitest run` 全部通過。
- 使用 `screen.getByRole` 或 `screen.getByText` 查詢元素（不使用 `querySelector`）。
- 所有 `fireEvent` 都有 `await`。

### Advanced：登入表單測試（銜接 Ch05）

**任務：為 Ch05 的登入表單撰寫完整的驗證與互動測試。**

1. 建立 `src/lib/components/__tests__/LoginForm.test.ts`。
2. 撰寫以下測試案例：
   - 空白提交時顯示 email 與 password 的驗證錯誤。
   - 輸入不合法 email 格式時顯示格式錯誤。
   - 輸入合法資料並提交後，驗證錯誤消失。
   - 提交時按鈕顯示 loading 狀態（disabled + 文字變更）。
   - 提交成功後呼叫 `onSuccess` callback。

**驗收條件：**
- 至少 5 個測試案例全部通過。
- 使用 `screen.getByLabelText` 查詢表單欄位（驗證 accessibility）。
- 不測試元件內部的 `$state` 變數，只測試 DOM 呈現。

### Challenge：SvelteKit load function + `$app/navigation` 測試

**任務：為 SvelteKit 的 load function 與使用 `$app/navigation` 的元件撰寫測試。**

1. 撰寫 `src/routes/blog/__tests__/page.server.test.ts`：
   - 測試 load function 正常回傳文章清單。
   - 測試 load function 在 fetch 失敗時拋出正確的錯誤。
   - 測試 load function 根據不同 params 回傳不同資料。
2. 撰寫 `src/lib/components/__tests__/LogoutButton.test.ts`：
   - 測試點擊 logout 後呼叫 `goto('/login')`。
   - 測試 logout API 失敗時顯示錯誤訊息而不導航。
3. 在 `vitest.config.ts` 中正確設定 `$app/*` 的 alias。

**驗收條件：**
- Load function 測試至少 3 個案例。
- `$app/navigation` mock 正確運作。
- 每個測試都能獨立執行（`afterEach` 中重置 mock）。
- `npx vitest run` 全部通過。

### Challenge+：Playwright E2E 測試

**任務：為應用撰寫 Playwright E2E 測試，覆蓋完整使用者流程。**

1. 安裝 Playwright 並設定 `playwright.config.ts`，配置 webServer 指向 SvelteKit dev server。
2. 建立 `e2e/` 目錄，撰寫以下測試案例：
   - 新增 todo → 確認顯示在列表中 → 勾選完成 → 確認顯示刪除線。
   - 未登入造訪 `/dashboard` → 被 redirect 到 `/login` → 登入 → 回到 `/dashboard`。
   - 填寫表單但留空必填欄位 → 提交 → 確認顯示驗證錯誤 → 填入正確資料 → 提交成功。
3. 在 `package.json` 的 scripts 中加入 `"test:e2e": "playwright test"`。

**驗收條件：**
- `npx playwright test` 全部通過（至少在 chromium 上）。
- 測試使用 locator API（`getByRole`、`getByLabel`、`getByText`），不使用 CSS selector。
- `playwright.config.ts` 設定至少兩個瀏覽器 project。
- 測試報告可透過 `npx playwright show-report` 檢視。

## Reference Solution

### vitest.config.ts — 測試環境設定

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte({ hot: false })],
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.ts'],
    globals: true,
    setupFiles: ['./src/tests/setup.ts']
  },
  resolve: {
    alias: {
      $lib: '/src/lib',
      '$app/navigation': '/src/tests/mocks/navigation.ts',
      '$app/stores': '/src/tests/mocks/stores.ts',
      '$app/environment': '/src/tests/mocks/environment.ts'
    }
  }
});
```

### src/tests/setup.ts — 測試全域設定

```ts
// src/tests/setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/svelte';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```

### src/tests/mocks/navigation.ts — $app/navigation mock

```ts
// src/tests/mocks/navigation.ts
import { vi } from 'vitest';

export const goto = vi.fn();
export const invalidate = vi.fn();
export const invalidateAll = vi.fn();
export const prefetch = vi.fn();
```

### Counter.test.ts — 元件測試

```ts
// src/lib/components/__tests__/Counter.test.ts
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Counter from '../Counter.svelte';

describe('Counter', () => {
  it('renders initial count', () => {
    render(Counter, { props: { initial: 5 } });
    expect(screen.getByText('Count: 5')).toBeInTheDocument();
  });

  it('increments on click', async () => {
    render(Counter, { props: { initial: 0 } });
    const button = screen.getByRole('button', { name: 'Increment' });

    await fireEvent.click(button);

    expect(screen.getByText('Count: 1')).toBeInTheDocument();
  });

  it('shows doubled value', async () => {
    render(Counter, { props: { initial: 3 } });
    expect(screen.getByText('Doubled: 6')).toBeInTheDocument();
  });
});
```

### Load function 測試

```ts
// src/routes/blog/__tests__/page.server.test.ts
import { describe, it, expect, vi } from 'vitest';
import { load } from '../+page.server';

describe('blog load function', () => {
  it('returns posts', async () => {
    const result = await load({
      params: {},
      fetch: vi.fn(),
      cookies: { get: vi.fn(), set: vi.fn() } as any,
      locals: { user: null },
    } as any);

    expect(result.posts).toBeDefined();
    expect(result.posts.length).toBeGreaterThan(0);
  });

  it('handles fetch errors gracefully', async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error('Network error'));

    await expect(
      load({
        params: {},
        fetch: mockFetch,
        cookies: { get: vi.fn(), set: vi.fn() } as any,
        locals: { user: null },
      } as any)
    ).rejects.toThrow();
  });
});
```

### $app/navigation 元件測試

```ts
// src/lib/components/__tests__/LogoutButton.test.ts
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { goto } from '$app/navigation';
import LogoutButton from '../LogoutButton.svelte';

describe('LogoutButton', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('navigates to login page on logout', async () => {
    render(LogoutButton);

    await fireEvent.click(screen.getByRole('button', { name: 'Logout' }));

    expect(goto).toHaveBeenCalledWith('/login');
  });

  it('does not navigate if logout API fails', async () => {
    // 假設元件內部 fetch logout API 失敗
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('API error'));

    render(LogoutButton);
    await fireEvent.click(screen.getByRole('button', { name: 'Logout' }));

    expect(goto).not.toHaveBeenCalled();
    expect(screen.getByText('Logout failed')).toBeInTheDocument();
  });
});
```

## Common Pitfalls

### 1. 忘記在 `afterEach` 中呼叫 `cleanup()` — 元件洩漏

不呼叫 `cleanup()` 時，前一個測試掛載的元件仍留在 DOM 中，導致後續測試的 `screen.getByText()` 可能找到前一個測試的元素。

```ts
// 錯誤：沒有 cleanup，元件洩漏
afterEach(() => {
  // 什麼都沒做
});

// 正確：每個測試結束後卸載所有元件
afterEach(() => {
  cleanup();
});
```

建議在 `setup.ts` 中統一設定，避免每個測試檔都要重複。

### 2. 沒有 `await fireEvent` — 斷言在 DOM 更新前執行

`fireEvent` 回傳 Promise，如果不 `await`，斷言可能在 Svelte 完成 DOM 更新之前就執行。

```ts
// 錯誤：DOM 可能尚未更新
fireEvent.click(button);
expect(screen.getByText('Count: 1')).toBeInTheDocument(); // 可能失敗

// 正確：等待事件處理與 DOM 更新完成
await fireEvent.click(button);
expect(screen.getByText('Count: 1')).toBeInTheDocument();
```

### 3. 測試實作細節而非使用者可見行為

不要斷言 `$state` 變數的內部值，應該斷言 DOM 上使用者看得到的結果。

```ts
// 錯誤：直接存取元件內部狀態（脆弱、與實作耦合）
const component = render(Counter, { props: { initial: 0 } });
expect(component.count).toBe(0); // 測試實作細節

// 正確：斷言 DOM 呈現的結果
render(Counter, { props: { initial: 0 } });
expect(screen.getByText('Count: 0')).toBeInTheDocument();
```

經驗法則：如果重構元件內部邏輯（不改變 UI 行為），測試不應該壞掉。

### 4. 沒有 mock `$app/*` 模組 — 模組解析失敗

測試中 import 使用 `$app/navigation` 的元件時，Vitest 無法解析這些 SvelteKit 專屬模組。

```
Error: Failed to resolve import "$app/navigation"
```

```ts
// vitest.config.ts — 必須設定 alias
resolve: {
  alias: {
    '$app/navigation': '/src/tests/mocks/navigation.ts',
    '$app/stores': '/src/tests/mocks/stores.ts',
    '$app/environment': '/src/tests/mocks/environment.ts'
  }
}
```

### 5. 使用 `querySelector` 取代 testing-library queries

`querySelector` 依賴 CSS selector，與 DOM 結構緊密耦合。Testing-library 的 query 以使用者可感知的方式（文字、角色、label）查詢元素，更穩定也更鼓勵 accessible 的 HTML。

```ts
// 不建議：依賴 CSS class 名稱，重構就壞
const button = document.querySelector('.btn-primary');

// 建議：以使用者角色查詢，HTML 語意正確就能找到
const button = screen.getByRole('button', { name: 'Submit' });

// 建議：以 label 查詢，確保表單欄位有正確的 accessibility
const input = screen.getByLabelText('Email');
```

Query 優先順序（由最推薦到最不推薦）：`getByRole` → `getByLabelText` → `getByText` → `getByTestId`。

## Checklist

- [ ] Vitest + @testing-library/svelte 已安裝並正確設定
- [ ] 能 `render` 元件並用 `screen` 斷言 DOM 內容
- [ ] 能用 `fireEvent` 模擬使用者互動（click、input、submit）
- [ ] 能測試 `$state` / `$derived` 驅動的 reactivity 更新
- [ ] 能直接測試 SvelteKit load function 並 mock 參數
- [ ] 能 mock `$app/navigation` 和 `$app/stores`，測試導航邏輯
- [ ] 能使用 Playwright 撰寫 E2E 測試
- [ ] `npm run test`（或 `npx vitest run`）全部測試通過

## Further Reading

- [Vitest — Getting Started](https://vitest.dev/guide/) -- Vitest 官方入門指南，設定、API 與 CLI 說明。
- [@testing-library/svelte](https://testing-library.com/docs/svelte-testing-library/intro) -- Svelte Testing Library 官方文件，API reference 與範例。
- [Testing Library — Queries](https://testing-library.com/docs/queries/about) -- query 優先順序與使用建議。
- [Svelte — Testing](https://svelte.dev/docs/svelte/testing) -- Svelte 官方測試指南，包含 Vitest 設定與 Svelte 5 特有注意事項。
- [SvelteKit — Testing](https://svelte.dev/docs/kit/testing) -- SvelteKit 官方測試指南，涵蓋 unit test 與 integration test。
- [@testing-library/jest-dom](https://testing-library.com/docs/ecosystem-jest-dom/) -- 自訂 DOM matcher（`toBeInTheDocument`、`toHaveTextContent` 等）的完整清單。
