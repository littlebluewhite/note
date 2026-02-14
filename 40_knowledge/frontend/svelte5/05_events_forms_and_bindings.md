---
title: "Events, Forms, and Bindings / 事件、表單與雙向綁定"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "05"
level: beginner
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [04_control_flow_and_rendering]
---
# Events, Forms, and Bindings / 事件、表單與雙向綁定

## Goal

把「使用者輸入 → 驗證 → 提交 → 回饋」做成可預期流程，學會 Svelte 5 的事件處理與雙向綁定。

事件處理與表單綁定是前端開發中最常見的互動模式。Svelte 5 將事件語法從 `on:click` 指令改為 `onclick` 屬性，並移除了 `|preventDefault` 等修飾符，統一使用原生 DOM 屬性名稱。掌握這些 Svelte 5 特有的語法變化以及 `bind:value` / `bind:checked` / `bind:group` 的正確使用場景，能讓你高效地建構各種表單與互動介面。

- **銜接上一章**：Ch04 學會了根據狀態渲染不同內容，現在要處理使用者的互動輸入。
- **下一章預告**：Ch06 將學習 `$effect` 與生命週期，處理表單以外的副作用。

## Prerequisites

- 已完成第 04 章（Control Flow & Rendering）。
- 熟悉 `$state`、`$derived` 的基本用法（Ch03）。
- 理解 `{#if}` / `{#each}` 模板語法（Ch04）。

## Core Concepts

### 1. Event handlers as attributes（Svelte 5 事件語法）

> **重要**：Svelte 5 使用 `onclick={handler}` 屬性語法，**不再使用** Svelte 4 的 `on:click={handler}` 指令語法。

事件處理器直接作為 HTML 屬性傳遞，與原生 DOM 屬性名稱一致：

```svelte
<script lang="ts">
  let count = $state(0);

  function increment() {
    count += 1;
  }
</script>

<!-- Svelte 5：屬性語法 -->
<button onclick={increment}>+1</button>

<!-- inline handler 也可以 -->
<button onclick={() => (count -= 1)}>-1</button>
```

Event 物件的型別會由 Svelte 自動推斷，不需要手動標注：

```svelte
<script lang="ts">
  // event 自動推斷為 MouseEvent
  function handleClick(event: MouseEvent) {
    console.log(event.clientX, event.clientY);
  }
</script>

<button onclick={handleClick}>Click me</button>
```

| 何時用 inline handler | 何時抽成具名函式 |
|---|---|
| 邏輯只有一行、不需要重複使用 | 邏輯超過一行或包含條件判斷 |
| 簡單的狀態切換（如 toggle） | 需要在多個元素上重複使用 |
| 快速原型開發 | 需要寫單元測試 |

### 2. `bind:value` / `bind:checked` / `bind:group` / `bind:this`

Svelte 的 `bind:` 指令建立 state 與 DOM 之間的雙向同步。當使用者輸入時自動更新 state，state 改變時也自動更新 DOM：

```svelte
<script lang="ts">
  let name = $state('');
  let agreed = $state(false);
  let color = $state('red');
  let hobbies = $state<string[]>([]);
  let inputEl: HTMLInputElement;
</script>

<!-- bind:value — 文字輸入 -->
<input type="text" bind:value={name} />

<!-- bind:checked — 單一 checkbox -->
<input type="checkbox" bind:checked={agreed} />

<!-- bind:group — radio 群組，綁定到同一個變數 -->
<label><input type="radio" bind:group={color} value="red" /> Red</label>
<label><input type="radio" bind:group={color} value="blue" /> Blue</label>

<!-- bind:group — checkbox 群組，綁定到陣列 -->
<label><input type="checkbox" bind:group={hobbies} value="reading" /> Reading</label>
<label><input type="checkbox" bind:group={hobbies} value="gaming" /> Gaming</label>

<!-- bind:this — 取得 DOM 元素參考 -->
<input type="text" bind:this={inputEl} />
```

| 何時用 `bind:value` | 何時不用（用 FormData 更好） |
|---|---|
| 需要即時雙向同步（即時驗證、搜尋過濾） | 只在提交時讀取表單值 |
| 輸入值需要即時顯示在其他地方 | 表單欄位非常多，逐一綁定太繁瑣 |
| 需要根據輸入值動態改變 UI | 使用 SvelteKit form actions 的場景（Ch12） |

### 3. Form `onsubmit` 與 `preventDefault`

> **重要**：Svelte 5 不再支援 `|` 修飾符語法（如 `on:submit|preventDefault`）。必須在 handler 中手動呼叫 `event.preventDefault()`。

```svelte
<script lang="ts">
  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault(); // 手動阻止預設行為
    // 處理表單提交...
  }
</script>

<!-- Svelte 5：直接使用 onsubmit 屬性 -->
<form onsubmit={handleSubmit}>
  <!-- 表單欄位 -->
  <button type="submit">Submit</button>
</form>
```

| 何時用 client-side form handling | 何時用 SvelteKit form actions（Ch12） |
|---|---|
| 純前端互動，無需伺服器處理 | 需要伺服器端驗證與資料持久化 |
| SPA 模式，已有獨立 API 後端 | 希望支援 progressive enhancement（無 JS 也能提交） |
| 即時回饋體驗優先 | SEO 與可存取性優先 |

### 4. Binding vs one-way data flow（雙向綁定 vs 單向資料流）

`bind:` 是語法糖，等效於同時傳 value prop 和 oninput callback。選擇使用前需考慮資料流的清晰度：

```svelte
<!-- 雙向綁定（語法簡潔，適合表單） -->
<input bind:value={name} />

<!-- 等效的單向資料流寫法 -->
<input value={name} oninput={(e) => (name = e.currentTarget.value)} />
```

| 何時用 `bind:` | 何時不用 `bind:`（單向 + callback 更好） |
|---|---|
| 表單輸入欄位 | 元件之間的資料通訊（用 props + callback） |
| 需要即時驗證的場景 | 純顯示用途，不需要寫回 |
| `bind:this` 取得 DOM 參考 | 跨元件共享狀態（用 stores / context，Ch07） |
| 簡單的本地 UI 狀態 | 需要對資料變更做攔截或轉換 |

## Step-by-step

### Step 1：建立登入表單頁面

建立 `src/routes/login/+page.svelte`，先寫出基本的 HTML 結構：

```svelte
<main>
  <h1>Sign in</h1>
  <form>
    <label>
      Email
      <input type="email" />
    </label>
    <label>
      Password
      <input type="password" />
    </label>
    <button type="submit">Sign in</button>
  </form>
</main>
```

### Step 2：加入 `$state` 管理表單欄位

使用 `$state` 宣告表單資料，並定義 TypeScript 型別：

```svelte
<script lang="ts">
  type LoginForm = {
    email: string;
    password: string;
    remember: boolean;
  };

  let form = $state<LoginForm>({
    email: '',
    password: '',
    remember: false,
  });
</script>
```

### Step 3：使用 `bind:value` 和 `bind:checked` 綁定輸入

將 `$state` 與表單欄位雙向綁定：

```svelte
<input type="email" bind:value={form.email} />
<input type="password" bind:value={form.password} />
<input type="checkbox" bind:checked={form.remember} />
```

此時在輸入框打字，`form` 物件會即時更新；反之修改 `form` 也會反映到 UI。

### Step 4：使用 `onclick` 語法撰寫事件處理（NOT `on:click`）

加入一個「清除表單」按鈕，練習 Svelte 5 事件語法：

```svelte
<script lang="ts">
  function resetForm() {
    form = { email: '', password: '', remember: false };
  }
</script>

<!-- Svelte 5：onclick 屬性語法 -->
<button type="button" onclick={resetForm}>Reset</button>
```

### Step 5：撰寫 `validate()` 函式回傳錯誤對應表

驗證函式接收表單資料，回傳一個以欄位名為 key、錯誤訊息為 value 的物件：

```svelte
<script lang="ts">
  type LoginErrors = Partial<Record<keyof LoginForm, string>>;

  let errors = $state<LoginErrors>({});

  function validate(data: LoginForm): LoginErrors {
    const errs: LoginErrors = {};
    if (!data.email.includes('@')) {
      errs.email = 'Email format is invalid.';
    }
    if (data.password.length < 8) {
      errs.password = 'Password must be at least 8 chars.';
    }
    return errs;
  }
</script>
```

### Step 6：處理 `onsubmit`，執行驗證

在 `<form>` 上使用 `onsubmit` 屬性，handler 中呼叫 `event.preventDefault()` 阻止頁面重整：

```svelte
<script lang="ts">
  let isSubmitting = $state(false);
  let message = $state('');

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    if (isSubmitting) return; // 防止重複提交

    const nextErrors = validate(form);
    errors = nextErrors;
    message = '';

    if (Object.keys(nextErrors).length > 0) return;

    try {
      isSubmitting = true;
      await new Promise((resolve) => setTimeout(resolve, 600));
      message = 'Login success.';
    } catch {
      message = 'Login failed. Please retry.';
    } finally {
      isSubmitting = false;
    }
  }
</script>

<form onsubmit={handleSubmit}>
  <!-- 表單欄位 -->
</form>
```

### Step 7：顯示三種狀態 — idle / submitting / error-or-success

使用 `$derived` 計算是否有錯誤，配合 `{#if}` 區塊顯示對應訊息：

```svelte
<script lang="ts">
  let hasError = $derived(Object.keys(errors).length > 0);
</script>

{#if hasError}
  <p role="alert">Please fix input errors.</p>
{/if}

{#if message}
  <p>{message}</p>
{/if}

<button type="submit" disabled={isSubmitting}>
  {isSubmitting ? 'Signing in...' : 'Sign in'}
</button>
```

### Step 8：使用 `bind:this` 在掛載時聚焦 email 輸入框

透過 `bind:this` 取得 DOM 元素參考，搭配 `$effect`（預告 Ch06）在元件掛載後自動聚焦：

```svelte
<script lang="ts">
  let emailInput: HTMLInputElement;

  $effect(() => {
    emailInput?.focus();
  });
</script>

<input type="email" bind:this={emailInput} bind:value={form.email} />
```

## Hands-on Lab

### Foundation：完成登入表單

建立 `src/routes/login/+page.svelte`，實作基本登入表單：

- Email 輸入框搭配 `bind:value`。
- Password 輸入框搭配 `bind:value`。
- 驗證邏輯：email 必須含 `@`，password 長度 >= 8。
- Submit 按鈕在提交期間顯示 "Signing in..."。

**驗收標準**：
- [ ] email 格式檢查生效，輸入無 `@` 的值時顯示錯誤訊息。
- [ ] password 少於 8 字元時顯示錯誤訊息。
- [ ] 提交按鈕在送出期間文字變為 "Signing in..."。

### Advanced：加入 remember-me、錯誤摘要與即時清除

在 Foundation 基礎上擴充：

- 加入 "Remember me" checkbox，使用 `bind:checked` 綁定。
- 頂部顯示 error summary，列出所有欄位錯誤。
- 當使用者修改有錯誤的欄位時，該欄位的錯誤即時清除。

**驗收標準**：
- [ ] checkbox 正確綁定，勾選狀態反映在 `form.remember`。
- [ ] 編輯欄位時，對應的錯誤訊息即時消失。
- [ ] error summary 顯示所有待修正的錯誤。

### Challenge：防抖提交保護與欄位停用

在 Advanced 基礎上擴充：

- 快速連續點擊 submit 只觸發一次提交。
- 提交期間所有表單欄位與按鈕 disabled。
- 失敗後可重新嘗試提交。

**驗收標準**：
- [ ] 快速點擊只送出一次請求（console.log 驗證）。
- [ ] 提交期間所有 input 和 button 呈現 disabled 狀態。
- [ ] 失敗情境下，欄位重新啟用，可再次提交。

## Reference Solution

### login/+page.svelte

```svelte
<script lang="ts">
  type LoginForm = {
    email: string;
    password: string;
    remember: boolean;
  };

  type LoginErrors = Partial<Record<keyof LoginForm, string>>;

  let form = $state<LoginForm>({ email: '', password: '', remember: false });
  let errors = $state<LoginErrors>({});
  let isSubmitting = $state(false);
  let message = $state('');

  let hasError = $derived(Object.keys(errors).length > 0);

  function validate(data: LoginForm): LoginErrors {
    const errs: LoginErrors = {};
    if (!data.email.includes('@')) errs.email = 'Email format is invalid.';
    if (data.password.length < 8) errs.password = 'Password must be at least 8 chars.';
    return errs;
  }

  function clearError(key: keyof LoginForm) {
    delete errors[key];
  }

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    if (isSubmitting) return;

    const nextErrors = validate(form);
    errors = nextErrors;
    message = '';
    if (Object.keys(nextErrors).length > 0) return;

    try {
      isSubmitting = true;
      await new Promise((resolve) => setTimeout(resolve, 600));
      message = 'Login success.';
    } catch {
      message = 'Login failed. Please retry.';
    } finally {
      isSubmitting = false;
    }
  }
</script>

<main>
  <h1>Sign in</h1>
  {#if hasError}
    <p role="alert">Please fix input errors.</p>
  {/if}
  {#if message}
    <p>{message}</p>
  {/if}

  <form onsubmit={handleSubmit}>
    <label>
      Email
      <input
        type="email"
        bind:value={form.email}
        disabled={isSubmitting}
        oninput={() => clearError('email')}
      />
    </label>
    {#if errors.email}
      <p role="alert">{errors.email}</p>
    {/if}

    <label>
      Password
      <input
        type="password"
        bind:value={form.password}
        disabled={isSubmitting}
        oninput={() => clearError('password')}
      />
    </label>
    {#if errors.password}
      <p role="alert">{errors.password}</p>
    {/if}

    <label>
      <input
        type="checkbox"
        bind:checked={form.remember}
        disabled={isSubmitting}
      />
      Remember me
    </label>

    <button type="submit" disabled={isSubmitting}>
      {isSubmitting ? 'Signing in...' : 'Sign in'}
    </button>
  </form>
</main>
```

**重點解析**：

- `$state<LoginForm>` 管理所有表單欄位，集中在一個物件中。
- `$derived` 計算 `hasError`，當 `errors` 物件改變時自動重新計算。
- `onsubmit={handleSubmit}` 使用 Svelte 5 屬性語法，NOT `on:submit`。
- `event.preventDefault()` 在 handler 中手動呼叫，NOT `|preventDefault` 修飾符。
- `oninput={() => clearError('email')}` 實現欄位編輯時即時清除錯誤。
- `disabled={isSubmitting}` 在提交期間停用所有欄位，防止重複提交。
- `if (isSubmitting) return` 作為額外的防抖保護。

## Common Pitfalls

### 1. 使用 `on:click`（Svelte 4）而非 `onclick`（Svelte 5）

```svelte
<!-- 錯誤：Svelte 4 指令語法 -->
<button on:click={handler}>Click</button>

<!-- 正確：Svelte 5 屬性語法 -->
<button onclick={handler}>Click</button>
```

Svelte 5 將事件處理器統一為 HTML 屬性形式，與 DOM 原生屬性名稱一致。所有事件都使用小寫屬性名：`onclick`、`onsubmit`、`oninput`、`onkeydown` 等。

### 2. 使用 `|preventDefault` 修飾符（Svelte 4）

```svelte
<!-- 錯誤：Svelte 4 修飾符語法，Svelte 5 不支援 -->
<form on:submit|preventDefault={handleSubmit}>

<!-- 正確：Svelte 5 在 handler 中手動呼叫 -->
<form onsubmit={handleSubmit}>

<script lang="ts">
  function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    // ...
  }
</script>
```

Svelte 5 移除了 `|` 修飾符語法（`|preventDefault`、`|stopPropagation`、`|once` 等），所有行為都需要在 handler 函式內明確處理。

### 3. 在父子元件之間濫用 `bind:` 造成緊耦合

```svelte
<!-- 不建議：父元件直接 bind 子元件的內部狀態 -->
<ChildInput bind:value={parentValue} />

<!-- 建議：用 props + callback 保持單向資料流 -->
<ChildInput value={parentValue} onchange={(v) => (parentValue = v)} />
```

`bind:` 在表單元素上很方便，但在元件之間使用會建立隱式的雙向依賴，讓資料流難以追蹤。優先使用 props 傳入 + callback 傳出的模式。

### 4. 只做 client-side 驗證，忘記 server-side 驗證

Client-side 驗證提升使用者體驗，但**不能取代**伺服器端驗證。使用者可以透過瀏覽器開發者工具繞過前端驗證。安全性相關的驗證（如身份認證、權限檢查、資料完整性）必須在伺服器端執行。

### 5. 非同步提交期間未停用表單，導致重複提交

```svelte
<!-- 錯誤：提交期間按鈕仍可點擊 -->
<button type="submit">Submit</button>

<!-- 正確：提交期間停用按鈕與欄位 -->
<button type="submit" disabled={isSubmitting}>
  {isSubmitting ? 'Submitting...' : 'Submit'}
</button>
```

務必在 `isSubmitting` 為 `true` 時停用所有表單控制項，並在 handler 開頭加入 `if (isSubmitting) return` 作為雙重保護。

## Checklist

- [ ] 登入表單可正常渲染並接受輸入
- [ ] 無效 email / 過短 password 顯示對應的錯誤訊息
- [ ] Submit 按鈕在提交期間變更文字並防止重複點擊
- [ ] 失敗後可重新嘗試，錯誤訊息不會永久殘留
- [ ] 程式碼使用 `$state`、`$derived`，以及 Svelte 5 事件語法（`onclick` / `onsubmit`）
- [ ] `npx svelte-check` 通過，無型別錯誤

## Further Reading

- [Event handlers — Svelte 5 Template Syntax](https://svelte.dev/docs/svelte/event-handlers)
- [bind: — Svelte 5 Template Syntax](https://svelte.dev/docs/svelte/bind)
- [$state — Svelte 5 Runes](https://svelte.dev/docs/svelte/$state)
- [$derived — Svelte 5 Runes](https://svelte.dev/docs/svelte/$derived)
- [$effect — Svelte 5 Runes](https://svelte.dev/docs/svelte/$effect)
- [Svelte Tutorial: Events](https://svelte.dev/tutorial/svelte/dom-events)
