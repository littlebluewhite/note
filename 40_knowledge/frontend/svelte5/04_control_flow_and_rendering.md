---
title: "Control Flow and Rendering / 流程控制與渲染"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "04"
level: beginner
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [03_runes_and_reactivity]
---
# Control Flow and Rendering / 流程控制與渲染

## Goal

學會使用 Svelte 的模板語法根據狀態條件渲染不同內容，並正確使用 key 來管理清單。

控制流程語法（`{#if}`、`{#each}`、`{#key}`）是將響應式狀態轉化為實際 UI 畫面的橋樑。理解 key expression 對 DOM 穩定性的影響、`{@html}` 的 XSS 風險，以及 `{#key}` 強制重建與一般更新的差異，是建構正確、安全且高效 Svelte 應用的必備知識。

- 銜接上一章：Ch03 建立了響應式狀態（`$state`、`$derived`、`$effect`），現在要根據這些狀態決定畫面如何渲染。
- 下一章預告：Ch05 將處理使用者輸入事件、表單與雙向綁定。

## Prerequisites

- 已完成 Ch03（Runes and Reactivity），理解 `$state` 與 `$derived` 的用法。
- 能在 `.svelte` 元件中宣告響應式狀態並觀察畫面自動更新。
- `svelte5-lab` 專案可正常執行 `npm run dev`。

## Core Concepts

### 1. `{#if}` / `{:else if}` / `{:else}` — 條件渲染

根據布林值或表達式決定是否渲染某段 HTML。Svelte 在編譯時期將條件分支轉為高效的 DOM 操作，不使用虛擬 DOM diff。

```svelte
{#if condition}
  <p>條件為 true 時顯示</p>
{:else if anotherCondition}
  <p>另一個條件為 true 時顯示</p>
{:else}
  <p>所有條件皆不成立時顯示</p>
{/if}
```

- **何時用**：根據狀態顯示或隱藏整個區塊，例如登入/未登入畫面、載入中/已完成/錯誤狀態切換、空清單提示。
- **何時不用**：只是切換元素的視覺樣式（例如 active / inactive），此時用 `class:` directive 更為語意化且高效，不需要銷毀與重建 DOM 節點。

### 2. `{#each}` — 清單渲染與 key

將陣列資料渲染為重複的 DOM 結構。語法支援解構、索引值與 key expression。

```svelte
{#each items as item, index (item.id)}
  <li>{index + 1}. {item.name}</li>
{:else}
  <p>清單為空</p>
{/each}
```

- `(item.id)` 是 key expression，幫助 Svelte 追蹤哪個 DOM 節點對應哪個資料項。
- `{:else}` 區塊在陣列為空時渲染。

- **何時用 keyed each**：清單項目擁有唯一 `id`，且可能被新增、刪除或重新排序。使用 key 可確保 Svelte 精確更新對應的 DOM 節點，而非銷毀後重建，保留元件內部狀態（如輸入框內容、動畫進度）。
- **何時不用 key**：完全靜態、不會重新排序的清單（例如固定的導覽選單），省略 key 可減少少量開銷。但在多數情況下，加上 key 是更安全的做法。

### 3. `{#key expression}` — 強制銷毀並重建

當 `expression` 的值改變時，`{#key}` 區塊內的所有內容會被完全銷毀再重新建立。這與一般的響應式更新不同——一般更新只修改變動的部分，而 `{#key}` 會觸發完整的 mount/unmount 生命週期。

```svelte
{#key selectedId}
  <DetailPanel id={selectedId} />
{/key}
```

- **何時用**：需要在某個值變化時銷毀並重建內部元件，例如動畫重置（transition 重新播放）、元件完全重新初始化（清除所有內部狀態）、切換路由參數時強制重載子元件。
- **何時不用**：一般的狀態更新不需要 `{#key}`。如果元件本身能正確處理 props 變化，就不需要強制重建。過度使用 `{#key}` 會損害效能，因為每次都要拆除與重建整個 DOM 子樹。

### 4. Template expressions — `{@const}`、`{@html}`、`{@debug}`

Svelte 模板內的特殊指令，用於宣告常數、插入原始 HTML 或輔助除錯。

#### `{@const}` — 模板區域常數

在 `{#each}` 或 `{#if}` 區塊內宣告只讀的區域變數，避免在模板中重複撰寫相同的運算式。

```svelte
{#each orders as order}
  {@const total = order.quantity * order.unitPrice}
  {@const formatted = `$${total.toFixed(2)}`}
  <p>{order.name}: {formatted}</p>
{/each}
```

- **何時用**：在迴圈或條件區塊內，需要根據當前項目計算衍生值並重複使用。
- **何時不用**：只使用一次的簡單表達式，直接內嵌在模板中即可，不需額外宣告 `{@const}`。

#### `{@html}` — 插入原始 HTML

將字串直接作為 HTML 插入 DOM，Svelte 不會對其進行轉義。

```svelte
{@html articleContent}
```

> **XSS 風險警告**：`{@html}` 不會對內容進行任何消毒（sanitization）。如果插入的字串來自使用者輸入或外部來源，攻擊者可以注入惡意 `<script>` 標籤或事件處理器。**務必只用於已消毒（sanitized）的可信任內容**，例如經過 DOMPurify 處理後的 Markdown 渲染結果。

- **何時用**：渲染已消毒的富文本內容（如 CMS 輸出、Markdown 轉 HTML 後的結果）。
- **何時不用**：任何含有使用者輸入且未經消毒的字串。如果你不確定內容是否安全，就不要用 `{@html}`。

#### `{@debug}` — 開發除錯

在開發模式下，當指定的變數值改變時觸發瀏覽器的 `debugger` 斷點。

```svelte
{@debug items, filter}
```

- **何時用**：開發階段需要即時檢查模板中的變數值。
- **何時不用**：生產環境。上線前應移除所有 `{@debug}` 指令。

## Step-by-step

### Step 1：使用 `{#if}` 根據布林狀態顯示/隱藏內容

建立一個元件，用 `$state` 控制區塊的可見性。

```svelte
<!-- src/routes/ch04/+page.svelte -->
<script lang="ts">
  let isVisible = $state(true);
</script>

<button onclick={() => isVisible = !isVisible}>
  {isVisible ? 'Hide' : 'Show'}
</button>

{#if isVisible}
  <p>This content is conditionally rendered.</p>
{/if}
```

### Step 2：加入 `{:else if}` 與 `{:else}` 處理多重條件

```svelte
<script lang="ts">
  type Status = 'loading' | 'success' | 'error';
  let status = $state<Status>('loading');
</script>

{#if status === 'loading'}
  <p>Loading...</p>
{:else if status === 'error'}
  <p class="error">Something went wrong.</p>
{:else}
  <p>Data loaded successfully!</p>
{/if}

<button onclick={() => status = 'success'}>Simulate Success</button>
<button onclick={() => status = 'error'}>Simulate Error</button>
```

### Step 3：使用 `{#each}` 搭配索引渲染清單

```svelte
<script lang="ts">
  let fruits = $state(['Apple', 'Banana', 'Cherry']);
</script>

<ul>
  {#each fruits as fruit, i}
    <li>{i + 1}. {fruit}</li>
  {/each}
</ul>
```

### Step 4：為 `{#each}` 加上 key

當清單項目有唯一識別碼時，使用 key expression 讓 Svelte 精準追蹤 DOM 節點。

```svelte
<script lang="ts">
  interface Todo {
    id: number;
    text: string;
    done: boolean;
  }

  let todos = $state<Todo[]>([
    { id: 1, text: 'Learn Svelte', done: false },
    { id: 2, text: 'Build a project', done: false },
    { id: 3, text: 'Deploy to production', done: false },
  ]);
</script>

<ul>
  {#each todos as todo (todo.id)}
    <li>
      <input type="checkbox" bind:checked={todo.done} />
      <span class:done={todo.done}>{todo.text}</span>
    </li>
  {/each}
</ul>
```

### Step 5：實作新增、刪除、重新排序以展示 key 的重要性

```svelte
<script lang="ts">
  interface Item {
    id: number;
    name: string;
  }

  let nextId = $state(4);
  let items = $state<Item[]>([
    { id: 1, name: 'First' },
    { id: 2, name: 'Second' },
    { id: 3, name: 'Third' },
  ]);

  function addItem() {
    items.push({ id: nextId++, name: `Item ${nextId - 1}` });
  }

  function removeItem(id: number) {
    const index = items.findIndex(item => item.id === id);
    if (index !== -1) items.splice(index, 1);
  }

  function moveUp(index: number) {
    if (index === 0) return;
    const temp = items[index];
    items[index] = items[index - 1];
    items[index - 1] = temp;
  }
</script>

<button onclick={addItem}>Add Item</button>

<ul>
  {#each items as item, i (item.id)}
    <li>
      <button onclick={() => moveUp(i)} disabled={i === 0}>Up</button>
      <button onclick={() => removeItem(item.id)}>Remove</button>
      <input value={item.name} /> <!-- 用 key 確保輸入框不會錯位 -->
    </li>
  {/each}
</ul>
```

> 試試移除 `(item.id)` key，然後操作排序——你會看到 `<input>` 的值沒有跟著項目移動，這就是缺少 key 造成的 DOM 錯位。

### Step 6：使用 `{@const}` 在 `{#each}` 內計算顯示值

```svelte
{#each products as product (product.id)}
  {@const discountedPrice = product.price * 0.9}
  {@const displayPrice = `$${discountedPrice.toFixed(2)}`}
  <li>{product.name} — Original: ${product.price.toFixed(2)} → Sale: {displayPrice}</li>
{/each}
```

`{@const}` 讓模板更整潔，避免在插值中重複撰寫運算邏輯。

### Step 7：展示 `{@html}` 與 XSS 風險

```svelte
<script lang="ts">
  // 安全內容（來自可信任來源）
  let safeHtml = $state('<strong>Bold text</strong> and <em>italic text</em>');

  // 危險內容（模擬使用者輸入）
  let userInput = $state('');
</script>

<h3>Safe usage:</h3>
{@html safeHtml}

<h3>Dangerous demo (never do this in production):</h3>
<input bind:value={userInput} placeholder="Try typing: <img src=x onerror=alert('XSS')>" />
<div class="preview">
  {@html userInput} <!-- ⚠️ 永遠不要這樣做！僅為教學示範 -->
</div>
```

> 在輸入框中輸入 `<img src=x onerror=alert('XSS')>` 可以看到瀏覽器執行了注入的 JavaScript。在真實應用中，務必使用 DOMPurify 等工具對內容進行消毒。

### Step 8：使用 `{#key}` 在值變化時強制重建元件

```svelte
<!-- DetailPanel.svelte -->
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  let { id }: { id: number } = $props();
  let data = $state<string | null>(null);

  onMount(() => {
    console.log(`Mounted with id: ${id}`);
    // 模擬資料載入
    data = `Content for item ${id}`;
  });

  onDestroy(() => {
    console.log(`Destroyed panel for id: ${id}`);
  });
</script>

<div class="panel">
  {#if data}
    <p>{data}</p>
  {:else}
    <p>Loading...</p>
  {/if}
</div>
```

```svelte
<!-- 父元件 -->
<script lang="ts">
  import DetailPanel from './DetailPanel.svelte';

  let selectedId = $state(1);
</script>

<select bind:value={selectedId}>
  <option value={1}>Item 1</option>
  <option value={2}>Item 2</option>
  <option value={3}>Item 3</option>
</select>

{#key selectedId}
  <DetailPanel id={selectedId} />
{/key}
```

每次 `selectedId` 改變，`DetailPanel` 會被完全銷毀再重建，`onMount` 會重新執行。檢查瀏覽器 console 可看到 mount/destroy 的訊息。

## Hands-on Lab

任務：建立一個可篩選、排序並重新排列的商品清單元件。

### Foundation 基礎層

建立一個可篩選的商品清單：

- 使用 `$state` 管理商品陣列與搜尋關鍵字。
- 使用 `$derived` 計算篩選後的商品清單。
- 使用 `{#if}` 在篩選結果為空時顯示「No products found.」提示。
- 使用 `{#each}` 搭配 `(product.id)` key 渲染商品清單。
- 每個商品顯示名稱與價格，缺貨商品顯示「Out of stock」標籤。

### Advanced 進階層

在 Foundation 基礎上加入排序與分類篩選：

- 新增排序功能：可按名稱（A–Z / Z–A）或價格（低到高 / 高到低）排序。
- 新增分類篩選（category filter）下拉選單，可選擇「All」或特定分類。
- 使用 `{@const}` 在 `{#each}` 內計算折扣後的顯示價格（例如所有商品打 9 折）。
- 顯示目前篩選結果數量（例如「Showing 3 of 5 products」）。

### Challenge 挑戰層

實作手動排序（Move Up / Move Down）以展示 key 對 DOM 穩定性的重要性：

- 為每個商品新增「Move Up」和「Move Down」按鈕。
- 每個商品旁有一個文字輸入框（備註欄），用於輸入自訂備註。
- 先不加 key，操作排序後觀察輸入框的值是否跟著項目移動。
- 加上 key，再次操作排序，確認輸入框的值正確跟隨項目。
- （額外挑戰）使用 `{#key}` 包裹商品詳情元件，在切換選取商品時觸發進入動畫。

## Reference Solution

完整的商品清單元件，涵蓋條件渲染、清單渲染（含 key）、`{@const}` 與排序功能。

```svelte
<!-- src/routes/ch04/+page.svelte -->
<script lang="ts">
  interface Product {
    id: number;
    name: string;
    price: number;
    category: string;
    inStock: boolean;
  }

  let products = $state<Product[]>([
    { id: 1, name: 'Keyboard', price: 79.99, category: 'peripherals', inStock: true },
    { id: 2, name: 'Mouse', price: 49.99, category: 'peripherals', inStock: true },
    { id: 3, name: 'Monitor', price: 299.99, category: 'displays', inStock: false },
    { id: 4, name: 'Webcam', price: 89.99, category: 'peripherals', inStock: true },
    { id: 5, name: 'Desk Lamp', price: 39.99, category: 'accessories', inStock: true },
  ]);

  let search = $state('');
  let showInStockOnly = $state(false);
  let selectedCategory = $state('all');
  let sortBy = $state<'name' | 'price'>('name');
  let sortOrder = $state<'asc' | 'desc'>('asc');

  let categories = $derived([...new Set(products.map(p => p.category))]);

  let filtered = $derived.by(() => {
    let result = products;

    // 搜尋篩選
    if (search) {
      result = result.filter(p =>
        p.name.toLowerCase().includes(search.toLowerCase())
      );
    }

    // 庫存篩選
    if (showInStockOnly) {
      result = result.filter(p => p.inStock);
    }

    // 分類篩選
    if (selectedCategory !== 'all') {
      result = result.filter(p => p.category === selectedCategory);
    }

    // 排序
    result = [...result].sort((a, b) => {
      const factor = sortOrder === 'asc' ? 1 : -1;
      if (sortBy === 'name') return factor * a.name.localeCompare(b.name);
      return factor * (a.price - b.price);
    });

    return result;
  });

  // 手動排序
  function moveUp(index: number) {
    if (index === 0) return;
    const productId = filtered[index].id;
    const originalIndex = products.findIndex(p => p.id === productId);
    const prevProductId = filtered[index - 1].id;
    const prevOriginalIndex = products.findIndex(p => p.id === prevProductId);

    const temp = products[originalIndex];
    products[originalIndex] = products[prevOriginalIndex];
    products[prevOriginalIndex] = temp;
  }

  function moveDown(index: number) {
    if (index >= filtered.length - 1) return;
    const productId = filtered[index].id;
    const originalIndex = products.findIndex(p => p.id === productId);
    const nextProductId = filtered[index + 1].id;
    const nextOriginalIndex = products.findIndex(p => p.id === nextProductId);

    const temp = products[originalIndex];
    products[originalIndex] = products[nextOriginalIndex];
    products[nextOriginalIndex] = temp;
  }

  // 用於 {#key} 示範
  let selectedProductId = $state<number | null>(null);
  let selectedProduct = $derived(
    products.find(p => p.id === selectedProductId) ?? null
  );
</script>

<!-- 篩選控制列 -->
<div class="controls">
  <input bind:value={search} placeholder="Search products..." />

  <label>
    <input type="checkbox" bind:checked={showInStockOnly} />
    In stock only
  </label>

  <select bind:value={selectedCategory}>
    <option value="all">All categories</option>
    {#each categories as cat}
      <option value={cat}>{cat}</option>
    {/each}
  </select>

  <select bind:value={sortBy}>
    <option value="name">Sort by name</option>
    <option value="price">Sort by price</option>
  </select>

  <button onclick={() => sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'}>
    {sortOrder === 'asc' ? '↑ Ascending' : '↓ Descending'}
  </button>
</div>

<!-- 結果統計 -->
<p>Showing {filtered.length} of {products.length} products</p>

<!-- 商品清單 -->
{#if filtered.length === 0}
  <p>No products found.</p>
{:else}
  <ul>
    {#each filtered as product, i (product.id)}
      {@const discountRate = 0.9}
      {@const salePrice = product.price * discountRate}
      {@const displayPrice = `$${salePrice.toFixed(2)}`}
      <li>
        <span class="controls">
          <button onclick={() => moveUp(i)} disabled={i === 0}>▲</button>
          <button onclick={() => moveDown(i)} disabled={i >= filtered.length - 1}>▼</button>
        </span>
        <strong>{product.name}</strong>
        — <del>${product.price.toFixed(2)}</del> {displayPrice}
        <span class="category">[{product.category}]</span>
        {#if !product.inStock}
          <span class="out-of-stock">Out of stock</span>
        {/if}
        <button onclick={() => selectedProductId = product.id}>Details</button>
      </li>
    {/each}
  </ul>
{/if}

<!-- {#key} 示範：切換商品詳情時強制重建 -->
{#if selectedProduct}
  {#key selectedProductId}
    <div class="detail-panel">
      <h3>{selectedProduct.name}</h3>
      <p>Category: {selectedProduct.category}</p>
      <p>Price: ${selectedProduct.price.toFixed(2)}</p>
      <p>Status: {selectedProduct.inStock ? 'In stock' : 'Out of stock'}</p>
    </div>
  {/key}
{/if}

<style>
  .out-of-stock {
    color: red;
    font-weight: bold;
  }

  .category {
    color: gray;
    font-size: 0.9em;
  }

  .detail-panel {
    border: 1px solid #ccc;
    padding: 1rem;
    margin-top: 1rem;
    border-radius: 4px;
  }

  del {
    color: gray;
  }
</style>
```

## Common Pitfalls

- **忘記在 `{#each}` 加上 key 導致重排序時 DOM 錯位**：當清單項目被刪除或重新排序時，沒有 key 的 `{#each}` 只會依照索引更新，導致元件內部狀態（如 `<input>` 的值）留在錯誤的位置。解法：對任何可能變動順序的清單，一律使用 `(item.id)` 作為 key。
- **使用陣列索引作為 key**：`{#each items as item, i (i)}` 等同於沒有 key，因為索引永遠是 0, 1, 2...，在項目被刪除或重排後索引值仍然不變。Key 必須是唯一且穩定對應到特定資料項的值（如資料庫 ID 或 UUID）。
- **使用 `{@html}` 渲染未消毒的使用者輸入**：這是最常見的 XSS 攻擊入口之一。攻擊者可透過 `<script>`、`<img onerror>`、`<a href="javascript:">` 等方式注入惡意程式碼。務必在渲染前使用 DOMPurify 等工具消毒。
- **過度巢套 `{#if}` 而非使用 `{:else if}` 或預先計算狀態**：多層 `{#if}` 巢套讓模板難以閱讀與維護。當有多個互斥條件時，使用 `{:else if}` 鏈可大幅提升可讀性。更好的做法是在 `<script>` 中以 `$derived` 計算出一個清晰的狀態值，再在模板中用單一 `{#if}` 判斷。
- **混淆 `{#key}` 與 `{#each}` 的 key**：`{#key expression}` 是當 expression 改變時銷毀並重建整個區塊；`{#each items as item (item.id)}` 的 key 是用來追蹤清單中每個項目對應的 DOM 節點。兩者名稱相似但用途完全不同。
- **在 Svelte 5 中混用 `$:` reactive statement 與模板控制流程**：Svelte 5 使用 runes（`$state`、`$derived`）取代 Svelte 4 的 `$:` 語法。若在模板的 `{#if}` / `{#each}` / `{#await}` 控制流程中仍依賴 `$:` 聲明來驅動資料，將導致非預期行為或編譯錯誤。例如 `$: filtered = items.filter(...)` 搭配 `{#each filtered as item}` 在 Svelte 5 中應改為 `let filtered = $derived(items.filter(...))`。應統一使用 `$state` / `$derived` 管理所有驅動模板渲染的狀態。

## Checklist

- [ ] 能使用 `{#if}` / `{:else if}` / `{:else}` 進行條件渲染。
- [ ] 能使用 `{#each}` 搭配正確的 key 渲染清單。
- [ ] 能解釋為什麼 key 對清單的 DOM 更新很重要（避免 DOM 錯位、保留元件內部狀態）。
- [ ] 能使用 `{@const}` 在模板區塊內宣告區域計算值。
- [ ] 理解 `{@html}` 的 XSS 風險，知道何時可以安全使用（僅限已消毒的可信任內容）。
- [ ] 理解 `{#key}` 的用途（強制銷毀重建），不會與 `{#each}` key 混淆。
- [ ] `npx svelte-check` 通過，無型別錯誤。

## Further Reading (official links only)

- [Svelte Docs — {#if ...}](https://svelte.dev/docs/svelte/if)
- [Svelte Docs — {#each ...}](https://svelte.dev/docs/svelte/each)
- [Svelte Docs — {#key ...}](https://svelte.dev/docs/svelte/key)
- [Svelte Docs — {@const ...}](https://svelte.dev/docs/svelte/const)
- [Svelte Docs — {@html ...}](https://svelte.dev/docs/svelte/html)
- [Svelte Docs — {@debug ...}](https://svelte.dev/docs/svelte/debug)
- [Svelte Tutorial — Logic](https://svelte.dev/tutorial/svelte/if-blocks)
