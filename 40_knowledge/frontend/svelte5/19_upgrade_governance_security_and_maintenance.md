---
title: "Upgrade Governance, Security, and Maintenance / 升級治理與維護"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, svelte5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: svelte5_complete_notes
chapter: "19"
level: intermediate
stack: "TypeScript + SvelteKit 2.51.x + Svelte 5.50.x"
prerequisites: [18_deployment_adapters_and_observability]
---
# Upgrade Governance, Security, and Maintenance / 升級治理與維護

## Goal

建立系統化的升級流程與安全維護策略，確保專案長期健康。

技術債務的累積往往不是因為缺乏意識，而是缺乏流程。透過建立標準化的版本追蹤、安全掃描與升級決策模板，你能將維護工作從被動救火轉變為主動治理，讓 Svelte 5 專案在快速迭代的生態系統中持續保持健康。

- **銜接上一章**：Ch18 完成了部署與可觀測性設定，現在要確保專案能持續維護。
- **本章是系列最終章**。回顧：從 Ch00 建立工作區到 Ch18 部署，本章確保長期可持續性。

## Prerequisites

- 已完成第 18 章（Deployment, Adapters & Observability），專案已可部署至生產環境。
- 熟悉 npm 套件管理與 `package.json` 中版本號的意義。
- 理解 Git 分支策略與 CI/CD 基本流程。
- `svelte5-lab` 專案可正常執行 `npm run dev`、`npm run build`。

## Core Concepts

### 1. Version tracking: Svelte + SvelteKit + Vite — 版本追蹤

追蹤三個核心版本：Svelte、SvelteKit、Vite。這三者是 SvelteKit 專案的技術基礎，版本變動可能互相影響。

**Semantic versioning 規則：**

| 版本類型 | 格式 | 變更性質 | 範例 |
|----------|------|----------|------|
| patch | `x.y.Z` | 安全修復、bug fix | `5.50.0` -> `5.50.1` |
| minor | `x.Y.z` | 新功能，向後相容 | `5.50.0` -> `5.51.0` |
| major | `X.y.z` | 破壞性變更 | `5.50.0` -> `6.0.0` |

**升級決策矩陣：**

| 情境 | 行動 | 時程 |
|------|------|------|
| Security patch | 立即升級 | 當天 |
| Bug fix patch | 排入本週 | 本週 |
| Minor（新功能） | 評估需求後決定 | 下次 sprint |
| Major（破壞性變更） | 完整評估、測試、遷移 | 規劃專門的升級 sprint |

- **何時立即升級**：security patch 被公告、已知影響你使用的功能的 bug fix。
- **何時延後升級**：major 版本剛發布還不穩定、團隊正在衝刺重要功能無暇評估。

### 2. `npx sv migrate` — SvelteKit migration tool — 遷移工具

SvelteKit 提供自動化遷移指令，用於處理版本間的破壞性變更。這個工具會自動修改你的程式碼，將舊的 API 用法轉換為新版本的對應寫法。

```bash
# 列出可用的 migration
npx sv migrate

# 執行特定的 migration（例如 Svelte 5 遷移）
npx sv migrate svelte-5

# 執行 SvelteKit 特定版本的 migration
npx sv migrate sveltekit-2
```

遷移工具會掃描專案中的檔案，自動替換已棄用的 API、語法與匯入路徑。執行後務必 review 所有變更，因為自動遷移可能無法處理所有邊緣情況。

- **何時用**：SvelteKit 或 Svelte 發布了包含 breaking changes 的新版本，且官方提供了對應的 migration script。
- **何時不用**：patch/minor 版本更新通常不需要 migration。如果只是 bug fix 或新增功能，直接 `npm update` 即可。

### 3. Monthly check cadence and security advisory sources — 每月檢查節奏

固定每月檢查版本與安全公告，避免累積過多技術債。定期檢查比臨時救火更有效率。

**Security advisory sources：**

| 來源 | 用途 | 網址 |
|------|------|------|
| GitHub Advisory Database | 已知漏洞資料庫 | github.com/advisories |
| `npm audit` | 掃描 node_modules 中的已知漏洞 | CLI 指令 |
| Svelte release notes | 官方版本更新與安全修復公告 | github.com/sveltejs/svelte/releases |
| SvelteKit release notes | 框架層級的安全修復與破壞性變更 | github.com/sveltejs/kit/releases |

**建議的月度檢查流程：**

1. 執行 `npm outdated` 檢視過期套件
2. 執行 `npm audit` 掃描安全漏洞
3. 瀏覽 Svelte 與 SvelteKit 的 release notes
4. 記錄結果至月度更新日誌
5. 根據風險等級決定行動

- **何時提升檢查頻率（每週或更頻繁）**：使用者面向產品（user-facing product）、處理敏感資料（PII、金融資料）、有 compliance 要求（SOC2、GDPR）。
- **何時維持每月節奏**：內部工具、side project、無敏感資料的靜態網站。

### 4. Evidence-based upgrade template — 證據導向的升級模板

標準化的升級決策流程：**檢查 -> 評估 -> 測試 -> 升級 -> 驗證**。每次升級都留下書面記錄，作為未來決策的參考依據。

**升級流程五步驟：**

```
1. 檢查（Check）     — npm outdated + npm audit + release notes
2. 評估（Evaluate）   — 變更影響範圍、是否有 breaking changes、是否影響現有功能
3. 測試（Test）       — 在升級分支上執行完整 CI（lint + check + test + build）
4. 升級（Upgrade）    — 確認通過後 merge 升級分支
5. 驗證（Verify）     — 部署至 staging 環境，執行 smoke test
```

記錄每次升級的決策與結果，包含：版本差異、升級原因、測試結果、遇到的問題與解法。這份記錄在未來遇到問題時，能快速回溯升級歷史。

- **何時用正式流程**：major 版本升級、安全性修復、生產環境專案。
- **何時快速升級**：patch 版本、開發環境、個人 side project——仍建議記錄，但流程可簡化。

### 5. Svelte 4 to Svelte 5 migration considerations — Svelte 4 到 5 遷移考量

Svelte 5 引入了根本性的 reactivity 模型變更（runes），但提供了 compatibility mode 讓你逐步遷移。

```bash
# 自動遷移工具
npx sv migrate svelte-5
```

**主要變更：**

| Svelte 4 | Svelte 5 | 說明 |
|----------|----------|------|
| `let count = 0`（自動 reactive） | `let count = $state(0)` | 明確宣告 reactive state |
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` | 明確宣告 derived value |
| `$: { ... }` | `$effect(() => { ... })` | 明確宣告 side effects |
| `<slot />` | `{@render children()}` | Snippets 取代 slots |
| `on:click={handler}` | `onclick={handler}` | 原生事件語法 |
| `createEventDispatcher()` | Callback props | 元件事件傳遞方式 |

**Compatibility mode**：Svelte 5 支援在同一個專案中混用舊語法（`.svelte` 檔案不使用 runes）與新語法。你可以逐個元件遷移，不需要一次全部改完。

- **何時用 `npx sv migrate svelte-5`**：計畫從 Svelte 4 升級到 Svelte 5，想讓工具自動處理大部分語法轉換。
- **何時不用**：已經在 Svelte 5 上、或元件結構過於複雜需要手動逐步重構。

## Step-by-step

### Step 1：記錄當前版本基線

用 `npm ls` 查看並記錄目前專案使用的核心版本，作為升級前的基準。

```bash
npm ls svelte @sveltejs/kit vite --depth=0
```

輸出範例：

```
svelte5-lab@0.1.0
├── @sveltejs/kit@2.51.0
├── svelte@5.50.0
└── vite@6.1.0
```

將此版本資訊記錄到月度更新日誌中。這是整個升級流程的起點——沒有基線，就無法衡量變化。

### Step 2：檢查可用更新

用 `npm outdated` 查看哪些套件有新版本。

```bash
npm outdated
```

輸出範例：

```
Package          Current  Wanted  Latest  Location
svelte           5.50.0   5.50.2  5.50.2  node_modules/svelte
@sveltejs/kit    2.51.0   2.51.1  2.51.1  node_modules/@sveltejs/kit
vite             6.1.0    6.1.2   6.1.2   node_modules/vite
```

- **Current**：目前安裝的版本。
- **Wanted**：`package.json` 中版本範圍允許的最高版本。
- **Latest**：npm registry 上的最新版本。
- 若 Wanted 與 Latest 不同，可能代表有 major 版本升級需要手動處理。

### Step 3：檢閱 Svelte 與 SvelteKit release notes

前往 GitHub releases 頁面，閱讀從 Current 到 Latest 之間所有版本的變更記錄。

```
https://github.com/sveltejs/svelte/releases
https://github.com/sveltejs/kit/releases
```

重點關注：
- **Breaking Changes**：標記為 BREAKING 的變更，需要修改程式碼。
- **Deprecations**：即將在未來版本移除的功能，應儘早遷移。
- **Security Fixes**：安全性修復，應優先升級。
- **Bug Fixes**：是否修復了你遇到的問題。

### Step 4：執行安全性掃描

用 `npm audit` 掃描依賴樹中的已知漏洞。

```bash
npm audit
```

- **0 vulnerabilities**：安全無虞。
- **low / moderate**：評估後排入下次升級。
- **high / critical**：應立即處理。

若有漏洞，嘗試 `npm audit fix`（僅升級相容版本）。若需要 breaking changes 才能修復，用 `npm audit fix --force` 但務必之後執行完整測試。

### Step 5：建立升級分支

在獨立分支上進行升級，確保主分支不受影響。

```bash
git checkout -b upgrade/svelte-5.50.2
```

分支命名建議：`upgrade/<主要升級項目>-<版本號>` 或 `upgrade/<日期>`。這讓 PR review 與 rollback 都更容易。

### Step 6：套用更新

在升級分支上安裝新版本。

```bash
# Patch / minor 更新
npm update svelte @sveltejs/kit vite

# 或指定確切版本
npm install svelte@5.50.2 @sveltejs/kit@2.51.1 vite@6.1.2
```

如果是 SvelteKit 的 breaking change migration，先執行遷移工具：

```bash
npx sv migrate
```

更新完成後，檢查 `package.json` 與 `package-lock.json` 的變更，確認版本號正確。

### Step 7：執行完整驗證

依序執行所有品質檢查。每一步都必須通過，才能確認升級安全。

```bash
# Lint — 程式碼風格檢查
npm run lint

# Type check — TypeScript 型別檢查
npx svelte-check --tsconfig ./tsconfig.json

# Test — 單元與整合測試
npm run test -- --run

# Build — 完整建置
npm run build
```

如果任何步驟失敗：
1. 閱讀錯誤訊息，對照 release notes 中的 breaking changes。
2. 修復程式碼，重新執行完整驗證。
3. 將修復過程記錄在升級日誌中。

### Step 8：記錄升級決策至月度更新日誌

無論升級是否執行，都將檢查結果與決策記錄下來。

```bash
# 在專案根目錄或團隊知識庫中維護更新日誌
# 例如：docs/update-log.md 或 Notion/Confluence 頁面
```

記錄內容包含：
- 版本狀態（current vs latest）
- 安全掃描結果
- 升級決策（升級 / 延後 / 不升級）與原因
- 驗證結果
- 後續行動（需要更新文件、通知團隊等）

## Hands-on Lab

任務：建立並實踐系統化的升級治理流程。

### Foundation 基礎層

執行版本檢查與安全掃描，建立目前的基線記錄。

- 執行 `npm ls svelte @sveltejs/kit vite --depth=0`，記錄目前版本。
- 執行 `npm outdated`，記錄可用更新。
- 執行 `npm audit`，記錄安全掃描結果。
- 將以上結果填入月度更新日誌模板（見 Reference Solution），包含 Version status、Security status、Decision 三個區塊。

### Advanced 進階層

模擬一次 minor 版本升級，在分支上完成完整 CI 驗證，並記錄結果。

- 建立 `upgrade/<今日日期>` 分支。
- 執行 `npm update svelte @sveltejs/kit vite` 套用更新。
- 依序執行完整驗證：`npm run lint` -> `npx svelte-check` -> `npm run test -- --run` -> `npm run build`。
- 將每一步的結果（pass / fail）記錄到月度更新日誌。
- 若有失敗，分析原因並記錄修復方式。
- 完成後 commit 並建立 PR，附上更新日誌作為 PR description。

### Challenge 挑戰層

建立一個 GitHub Action，每月自動檢查過期依賴並開立 issue。

- 在 `.github/workflows/` 目錄下建立 `dependency-check.yml`。
- 使用 `schedule` trigger，設定每月第一天 9:00 AM 執行。
- Action 步驟：checkout -> setup Node 22 -> `npm ci` -> `npm outdated` -> `npm audit` -> 將結果寫入 report -> 用 `peter-evans/create-issue-from-file` 開立 issue。
- 加入 `workflow_dispatch` trigger，方便手動觸發測試。
- 測試：手動觸發 workflow，確認 issue 被正確建立。

## Reference Solution

### Version check utility（TypeScript）

```typescript
// src/lib/version-check.ts
interface VersionInfo {
  name: string;
  current: string;
  latest: string;
  updateAvailable: boolean;
}

export async function checkDependencyVersions(
  deps: Record<string, string>
): Promise<VersionInfo[]> {
  const results: VersionInfo[] = [];
  for (const [name, current] of Object.entries(deps)) {
    const res = await fetch(`https://registry.npmjs.org/${name}/latest`);
    const data = await res.json() as { version: string };
    results.push({
      name,
      current: current.replace(/^[\^~]/, ''),
      latest: data.version,
      updateAvailable: current.replace(/^[\^~]/, '') !== data.version,
    });
  }
  return results;
}
```

月度更新日誌模板，記錄版本狀態、安全掃描與升級決策。

```md
## 2026-02 (owner: Wilson)

### Version status
- Current: svelte 5.50.0 / @sveltejs/kit 2.51.0 / vite 6.1.0
- Latest: svelte 5.50.2 / @sveltejs/kit 2.51.1 / vite 6.1.2
- Delta: patch updates only

### Security status
- Svelte advisories: none
- SvelteKit advisories: none
- npm audit: 0 vulnerabilities
- Risk level: low

### Decision
- Action: patch now
- Reason: patch updates with bug fixes, no breaking changes
- Deadline: this week

### Validation
- Commands:
  - npm run lint ✓
  - npx svelte-check ✓
  - npm run test ✓
  - npm run build ✓
- Result: all pass

### Follow-ups
- Docs update needed: none
- Training note needed: none
- Owner: Wilson
```

GitHub Action：每月自動檢查依賴並開立 issue。

```yaml
# .github/workflows/dependency-check.yml
name: Monthly Dependency Check
on:
  schedule:
    - cron: '0 9 1 * *'  # First day of each month at 9 AM
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - name: Check outdated
        id: outdated
        run: |
          echo "## Dependency Report" > report.md
          echo '```' >> report.md
          npm outdated || true >> report.md
          echo '```' >> report.md
          echo "## Security Audit" >> report.md
          echo '```' >> report.md
          npm audit || true >> report.md
          echo '```' >> report.md
      - name: Create issue
        uses: peter-evans/create-issue-from-file@v5
        with:
          title: "Monthly Dependency Check - $(date +'%Y-%m')"
          content-filepath: report.md
          labels: dependencies,maintenance
```

升級腳本，自動化版本檢查、安全掃描與驗證流程。

```bash
# scripts/upgrade.sh
#!/bin/bash
set -e

echo "=== Current versions ==="
npm ls svelte @sveltejs/kit vite --depth=0

echo "=== Checking for updates ==="
npm outdated || true

echo "=== Running security audit ==="
npm audit || true

echo "=== Creating upgrade branch ==="
git checkout -b upgrade/$(date +%Y-%m-%d)

echo "=== Applying updates ==="
npm update svelte @sveltejs/kit vite

echo "=== Running validation ==="
npm run lint
npx svelte-check --tsconfig ./tsconfig.json
npm run test -- --run
npm run build

echo "=== All checks passed ==="
npm ls svelte @sveltejs/kit vite --depth=0
```

## Common Pitfalls

- **跳過 `npm audit` 不執行安全掃描**：已知漏洞長期未修補，等到被攻擊才發現。安全掃描應該是每次升級流程的必要步驟，也應納入 CI pipeline。即使 `npm audit` 回報 0 vulnerabilities，記錄這個結果本身就是有價值的證據。

- **未閱讀 migration guide 就升級 major 版本**：直接 `npm install svelte@next` 然後發現一堆編譯錯誤。Major 版本升級前，務必完整閱讀 release notes 與 migration guide，理解所有 breaking changes 的影響範圍，再決定升級時程與策略。

- **升級後只確認「能編譯」就認為沒問題**：`npm run build` 通過不代表功能正確。編譯只檢查語法與型別，不驗證業務邏輯。升級後必須執行完整測試套件（unit test + integration test），並在 staging 環境進行 smoke test。

- **一次升級所有依賴而非逐一升級**：`npm update` 一次升級十幾個套件，某個功能壞了卻不知道是哪個套件造成的。應該一次升級一個核心套件（或一組緊密耦合的套件），確認通過後再升級下一個。這讓問題更容易隔離與修復。

- **未記錄升級決策與結果**：三個月後某個功能出現奇怪行為，沒人記得上次升級了什麼、為什麼選擇那個版本。每次升級（包含決定「不升級」）都應留下書面記錄，包含版本差異、決策理由、測試結果與遇到的問題。

## Checklist

- [ ] 版本基線已記錄（`npm ls svelte @sveltejs/kit vite --depth=0` 的輸出）。
- [ ] `npm audit` 顯示無 high/critical 漏洞。
- [ ] 已建立每月檢查節奏（日曆提醒或 GitHub Action 排程）。
- [ ] 升級流程已文件化且可重複執行（腳本或 checklist）。
- [ ] CI 在每個 PR 上執行 lint、svelte-check、test、build。
- [ ] 月度更新日誌模板已建立並可供使用。

## Further Reading

- [Svelte Releases](https://github.com/sveltejs/svelte/releases)
- [SvelteKit Releases](https://github.com/sveltejs/kit/releases)
- [SvelteKit Docs — Migrating](https://svelte.dev/docs/kit/migrating)
- [Svelte Docs — Svelte 5 migration guide](https://svelte.dev/docs/svelte/v5-migration-guide)
- [SvelteKit Docs — CLI: sv migrate](https://svelte.dev/docs/cli/sv-migrate)
