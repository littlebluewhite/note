---
title: "Upgrade Governance, Security, and Maintenance / 升級治理、安全與維護"
note_type: knowledge
domain: frontend
tags: [knowledge, frontend, tailwindcss4]
created: 2026-02-14
updated: 2026-02-14
status: active
source: knowledge
series: tailwindcss4_complete_notes
chapter: "24"
level: advanced
stack: Tailwind CSS 4.1.x
prerequisites: [23_migration_from_tailwind_v3_to_v4]
---

# Upgrade Governance, Security, and Maintenance / 升級治理、安全與維護

## Goal

在前一章 [[23_migration_from_tailwind_v3_to_v4]] 中，我們完成了從 Tailwind CSS v3 到 v4 的重大版本遷移。但軟體的維護不止於此 — Tailwind CSS 會持續發布小版本更新（4.1.x → 4.2.x），修復 bug、新增功能、改善效能。如何安全、有系統地管理這些持續的更新，是工程團隊長期穩定運作的關鍵。本章將建立一套完整的升級治理（upgrade governance）流程，涵蓋版本鎖定策略、安全監控、changelog 閱讀與影響評估、回歸測試、CSS 視覺回歸測試工具，以及每月更新工作流。

作為本系列的最後一章，我們也將回顧整個 24 章課程的關鍵學習，總結 Tailwind CSS v4 的核心概念和最佳實踐，並提供持續學習的方向指引。從第 01 章的 utility-first 哲學到本章的升級治理，你已經建立了從基礎到進階的完整 Tailwind CSS v4 知識體系。

## Prerequisites

- 已完成第 23 章，理解 v3 → v4 遷移流程。
- 熟悉 npm/pnpm 的版本管理機制（semver、lock files）。
- 理解 CI/CD 基本概念（自動化建置、測試）。
- 具備 Git 分支策略的基礎知識。
- 了解 npm audit 和安全漏洞的基本概念。

## Core Concepts

### 1. Version Pinning Strategy / 版本鎖定策略

版本鎖定是確保團隊所有成員和 CI 環境使用相同依賴版本的基礎。

**何時使用精確版本鎖定（exact pinning）：**
- 生產環境的專案，需要穩定可預測的行為。
- 團隊有嚴格的變更管理流程。
- 依賴套件的小版本更新曾經造成問題。

**何時使用範圍版本（^, ~）：**
- 開發初期，需要快速獲取 bug 修復。
- 個人專案或小型專案，能快速處理問題。
- 依賴套件的 semver 遵循嚴格且可信賴。

### 2. Security Monitoring / 安全監控

前端依賴也可能存在安全漏洞。CSS 框架雖然不直接處理敏感數據，但建置工具鏈中的漏洞可能影響開發環境安全。

**何時需要安全監控：**
- 所有生產環境的專案都應該有。
- 團隊有合規要求（如 SOC 2、ISO 27001）。
- 專案有長期維護需求（> 6 個月）。

**何時可以簡化安全流程：**
- 短期原型或 hackathon 專案。
- 純靜態展示頁面，不涉及任何用戶數據。
- 注意：即使簡化，仍應定期執行 `npm audit`。

### 3. Changelog Reading and Impact Assessment / Changelog 閱讀與影響評估

每次更新前閱讀 changelog 是專業開發者的基本功。

**何時需要完整的影響評估：**
- 主版本更新（v4 → v5）。
- 包含 breaking changes 的小版本更新。
- 更新的版本跨越多個小版本（如 4.1.x → 4.4.x）。

**何時可以快速評估：**
- Patch 版本更新（4.1.1 → 4.1.2）— 通常只是 bug 修復。
- Changelog 明確標示「No breaking changes」。
- 更新的功能完全不涉及專案使用的特性。

### 4. Regression Testing / 回歸測試

更新依賴後的回歸測試是防止引入新問題的最後防線。

**何時需要完整的回歸測試：**
- 依賴的主要版本或包含 breaking changes 的更新。
- 專案有高品質要求（面向客戶的產品）。
- 過去曾因依賴更新導致線上問題。

**何時可以精簡回歸測試：**
- Patch 版本的安全修復。
- 更新完全不涉及 CSS 輸出的變更（如 CLI 工具修復）。
- 有完整的自動化測試覆蓋率。

## Step-by-step

### 步驟 1：建立版本鎖定策略

設定 package.json 中的精確版本鎖定：

```json
{
  "devDependencies": {
    "tailwindcss": "4.1.3",
    "@tailwindcss/vite": "4.1.3",
    "vite": "6.1.2"
  },
  "dependencies": {
    "@tailwindcss/typography": "0.5.16",
    "@tailwindcss/forms": "0.5.10"
  }
}
```

設定 `.npmrc` 確保安裝時使用精確版本：

```ini
# .npmrc
save-exact=true
engine-strict=true
```

確認 lock file 被提交到版本控制：

```gitignore
# .gitignore
# 確保 lock file 不在 gitignore 中
# package-lock.json  <-- 不要忽略！
# pnpm-lock.yaml     <-- 不要忽略！
```

驗證：`npm ls tailwindcss` 顯示精確版本號，無 `^` 或 `~` 前綴。

### 步驟 2：設定安全監控

**npm audit 手動檢查：**

```bash
# 執行安全審計
npm audit

# 只檢查生產依賴
npm audit --omit=dev

# 嘗試自動修復
npm audit fix

# 查看詳細的漏洞報告
npm audit --json > audit-report.json
```

**GitHub Dependabot 自動監控：**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Asia/Taipei"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "security"
    # 將 Tailwind 相關更新分組
    groups:
      tailwind:
        patterns:
          - "tailwindcss"
          - "@tailwindcss/*"
      vite:
        patterns:
          - "vite"
          - "@vitejs/*"
    # 忽略主版本更新（需要手動評估）
    ignore:
      - dependency-name: "tailwindcss"
        update-types: ["version-update:semver-major"]
```

驗證：Dependabot 設定後，GitHub 會在發現更新時自動建立 PR。

### 步驟 3：建立 Changelog 閱讀流程

建立結構化的 changelog 閱讀和影響評估模板：

```markdown
# Tailwind CSS Update Assessment

## Update Info
- **From**: v4.1.2
- **To**: v4.1.3
- **Date**: YYYY-MM-DD
- **Changelog URL**: https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.3

## Changes Summary
### Bug Fixes
- [ ] (列出每個 bug fix，標記是否影響我們的專案)

### New Features
- [ ] (列出每個新功能，評估是否有用)

### Breaking Changes
- [ ] (列出每個 breaking change，評估影響範圍)

### Performance
- [ ] (列出效能改善項目)

## Impact Assessment
- **Risk Level**: Low / Medium / High
- **Affected Components**: (列出可能受影響的元件)
- **Testing Required**: Minimal / Standard / Full regression

## Decision
- [ ] Update immediately
- [ ] Update in next sprint
- [ ] Skip this version
- [ ] Investigate further

## Notes
(記錄任何額外的觀察或決策理由)
```

自動追蹤 Tailwind CSS releases：

```bash
# 使用 GitHub CLI 查看最新 releases
gh release list --repo tailwindlabs/tailwindcss --limit 5

# 查看特定 release 的詳細資訊
gh release view v4.1.3 --repo tailwindlabs/tailwindcss
```

驗證：changelog 評估模板已建立，能使用 `gh` CLI 查看 releases。

### 步驟 4：建立更新測試工作流

建立一個結構化的更新測試流程：

```bash
#!/bin/bash
# scripts/update-tailwind.sh

set -e

echo "=== Tailwind CSS Update Script ==="
echo ""

# 步驟 1：記錄當前狀態
echo "Step 1: Recording current state..."
CURRENT_VERSION=$(npm ls tailwindcss --json | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8');console.log(JSON.parse(d).dependencies.tailwindcss.version)" 2>/dev/null || echo "unknown")
echo "Current Tailwind version: $CURRENT_VERSION"

# 建置基準
npm run build 2>&1 | tail -5 > /tmp/tw-build-before.txt
ls -lh dist/assets/*.css 2>/dev/null > /tmp/tw-sizes-before.txt || true

# 步驟 2：建立更新分支
echo ""
echo "Step 2: Creating update branch..."
BRANCH_NAME="chore/tailwind-update-$(date +%Y%m%d)"
git checkout -b "$BRANCH_NAME"

# 步驟 3：更新依賴
echo ""
echo "Step 3: Updating Tailwind CSS..."
npm update tailwindcss @tailwindcss/vite @tailwindcss/postcss

NEW_VERSION=$(npm ls tailwindcss --json | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8');console.log(JSON.parse(d).dependencies.tailwindcss.version)" 2>/dev/null || echo "unknown")
echo "Updated to: $NEW_VERSION"

# 步驟 4：建置測試
echo ""
echo "Step 4: Building..."
npm run build 2>&1 | tail -5 > /tmp/tw-build-after.txt
ls -lh dist/assets/*.css 2>/dev/null > /tmp/tw-sizes-after.txt || true

# 步驟 5：比較結果
echo ""
echo "=== Build Comparison ==="
echo "Before:"
cat /tmp/tw-sizes-before.txt
echo "After:"
cat /tmp/tw-sizes-after.txt

echo ""
echo "=== Next Steps ==="
echo "1. Review changelog for $CURRENT_VERSION → $NEW_VERSION"
echo "2. Run visual regression tests"
echo "3. Test critical user flows"
echo "4. If OK: git add -A && git commit && git push"
echo "5. If NOT OK: git checkout main && git branch -D $BRANCH_NAME"
```

```bash
chmod +x scripts/update-tailwind.sh
```

驗證：腳本能成功執行，輸出版本比較和建置大小比較。

### 步驟 5：設定 CSS 視覺回歸測試

使用 Playwright 進行自動化的視覺回歸測試：

```bash
npm install -D @playwright/test
npx playwright install
```

```ts
// tests/visual-regression.spec.ts
import { test, expect } from "@playwright/test";

const pages = [
  { name: "home", url: "/" },
  { name: "about", url: "/about" },
  { name: "components", url: "/components" },
  { name: "blog", url: "/blog" },
];

const viewports = [
  { name: "mobile", width: 375, height: 812 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "desktop", width: 1440, height: 900 },
];

for (const page of pages) {
  for (const viewport of viewports) {
    test(`${page.name} - ${viewport.name}`, async ({ page: browserPage }) => {
      await browserPage.setViewportSize({
        width: viewport.width,
        height: viewport.height,
      });
      await browserPage.goto(page.url);
      // 等待所有 CSS 載入
      await browserPage.waitForLoadState("networkidle");
      // 截圖比較
      await expect(browserPage).toHaveScreenshot(
        `${page.name}-${viewport.name}.png`,
        {
          maxDiffPixelRatio: 0.01, // 允許 1% 的像素差異
          threshold: 0.2, // 色彩差異容忍度
        }
      );
    });
  }
}

// 深色模式測試
for (const page of pages) {
  test(`${page.name} - dark mode`, async ({ page: browserPage }) => {
    await browserPage.setViewportSize({ width: 1440, height: 900 });
    // 啟用深色模式
    await browserPage.emulateMedia({ colorScheme: "dark" });
    await browserPage.goto(page.url);
    await browserPage.waitForLoadState("networkidle");
    await expect(browserPage).toHaveScreenshot(
      `${page.name}-dark.png`,
      { maxDiffPixelRatio: 0.01 }
    );
  });
}
```

```json
// package.json scripts
{
  "scripts": {
    "test:visual": "npx playwright test tests/visual-regression.spec.ts",
    "test:visual:update": "npx playwright test tests/visual-regression.spec.ts --update-snapshots"
  }
}
```

執行流程：

```bash
# 首次：建立基準截圖
npm run test:visual:update

# 更新後：比較截圖
npm run test:visual
# 如果有差異，Playwright 會在 test-results/ 中生成 diff 圖
```

驗證：視覺回歸測試能自動偵測 CSS 變更導致的視覺差異。

### 步驟 6：建立 CI/CD 中的更新驗證管線

```yaml
# .github/workflows/tailwind-update-check.yml
name: Tailwind CSS Update Check

on:
  pull_request:
    paths:
      - "package.json"
      - "package-lock.json"
      - "pnpm-lock.yaml"
      - "**/*.css"

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Check CSS output size
        run: |
          echo "## CSS Output Size" >> $GITHUB_STEP_SUMMARY
          for file in dist/assets/*.css; do
            SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
            KB=$(echo "scale=2; $SIZE / 1024" | bc)
            echo "- $(basename $file): ${KB}KB" >> $GITHUB_STEP_SUMMARY
          done

      - name: Run visual regression tests
        run: |
          npx playwright install --with-deps
          npm run test:visual

      - name: Upload visual diff artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: visual-regression-diffs
          path: test-results/
          retention-days: 7

      - name: Security audit
        run: npm audit --omit=dev
        continue-on-error: true
```

驗證：PR 中包含 CSS 變更時，CI 自動執行建置、大小檢查和視覺回歸測試。

### 步驟 7：建立每月更新工作流

```markdown
# Monthly Tailwind CSS Update Workflow

## Schedule
- **日期**: 每月第一個星期一
- **負責人**: 前端 tech lead（輪值）
- **預計時間**: 1-2 小時

## Checklist

### 1. 準備 (15 min)
- [ ] 查看上次更新日期和版本
- [ ] 使用 `gh release list --repo tailwindlabs/tailwindcss --limit 10` 查看新版本
- [ ] 閱讀所有中間版本的 changelog

### 2. 影響評估 (15 min)
- [ ] 填寫 Update Assessment 模板
- [ ] 標記 Risk Level
- [ ] 識別可能受影響的元件

### 3. 更新執行 (15 min)
- [ ] 執行 `scripts/update-tailwind.sh`
- [ ] 解決任何安裝錯誤

### 4. 驗證 (30-60 min)
- [ ] `npm run build` 無錯誤
- [ ] `npm run test:visual` 通過或差異可接受
- [ ] 手動檢查 3-5 個關鍵頁面
- [ ] 深色模式檢查
- [ ] 響應式斷點檢查（mobile/tablet/desktop）
- [ ] `npm audit` 無高風險漏洞

### 5. 提交 (10 min)
- [ ] 提交到更新分支
- [ ] 建立 PR，附上 changelog 摘要和影響評估
- [ ] 請求 code review

### 6. 記錄 (10 min)
- [ ] 更新 monthly_update_log
- [ ] 記錄任何需要注意的行為變更
```

驗證：工作流文件完整，團隊能按照步驟執行每月更新。

### 步驟 8：設定版本更新通知

```yaml
# .github/workflows/version-check.yml
name: Check for Tailwind Updates

on:
  schedule:
    - cron: "0 1 * * 1" # 每週一 UTC 01:00

jobs:
  check-updates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "22"

      - name: Check for updates
        run: |
          npm install
          CURRENT=$(npm ls tailwindcss --json 2>/dev/null | node -e "
            const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
            console.log(d.dependencies?.tailwindcss?.version || 'unknown');
          ")
          LATEST=$(npm view tailwindcss version)
          echo "Current: $CURRENT"
          echo "Latest:  $LATEST"

          if [ "$CURRENT" != "$LATEST" ]; then
            echo "UPDATE_AVAILABLE=true" >> $GITHUB_ENV
            echo "CURRENT_VERSION=$CURRENT" >> $GITHUB_ENV
            echo "LATEST_VERSION=$LATEST" >> $GITHUB_ENV
          fi

      - name: Create issue if update available
        if: env.UPDATE_AVAILABLE == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            const existing = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              labels: 'tailwind-update',
              state: 'open',
            });
            if (existing.data.length === 0) {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: `Tailwind CSS update available: ${process.env.CURRENT_VERSION} → ${process.env.LATEST_VERSION}`,
                labels: ['tailwind-update', 'dependencies'],
                body: `A new version of Tailwind CSS is available.\n\n` +
                      `- Current: ${process.env.CURRENT_VERSION}\n` +
                      `- Latest: ${process.env.LATEST_VERSION}\n\n` +
                      `Please review the [changelog](https://github.com/tailwindlabs/tailwindcss/releases) ` +
                      `and follow the monthly update workflow.`,
              });
            }
```

驗證：GitHub Actions 能自動偵測新版本並建立 issue。

### 步驟 9：建立回滾計畫

```bash
# scripts/rollback-tailwind.sh
#!/bin/bash
set -e

echo "=== Tailwind CSS Rollback ==="

# 查看最近的更新提交
echo "Recent commits:"
git log --oneline -10

read -p "Enter commit hash to rollback to: " COMMIT_HASH

# 確認
echo "This will revert package.json and lock file to $COMMIT_HASH"
read -p "Continue? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
  echo "Rollback cancelled."
  exit 0
fi

# 只回滾 package 相關檔案
git checkout "$COMMIT_HASH" -- package.json package-lock.json

# 重新安裝
npm ci

# 重新建置
npm run build

echo ""
echo "Rollback complete. Please verify and commit if OK."
echo "git add package.json package-lock.json && git commit -m 'chore: rollback tailwind version'"
```

CI/CD 中的回滾策略：

```yaml
# 在部署工作流中保留最近 3 個成功的建置
# 如果更新後出問題，可以快速回滾到前一個版本
```

驗證：回滾腳本能成功恢復到前一個 Tailwind 版本。

### 步驟 10：系列總結與學習路線圖

回顧整個 24 章系列的核心知識：

```
Tailwind CSS v4 Complete Notes - 學習路線回顧
==============================================

第一階段：基礎篇（Ch01-06）
├── Ch01: Utility-first 哲學 — 理解為何使用工具類
├── Ch02: 安裝與 CSS-first 配置 — @import "tailwindcss"
├── Ch03: 色彩系統 — oklch 色彩空間
├── Ch04: 排版與文字 — 字型、大小、行高
├── Ch05: 間距與尺寸 — spacing、sizing、box model
└── Ch06: 邊框與陰影 — border、shadow、ring

第二階段：布局篇（Ch07-09）
├── Ch07: Flexbox 布局
├── Ch08: Grid 布局
└── Ch09: 定位與 z-index

第三階段：響應式與狀態（Ch10-12）
├── Ch10: 響應式設計 — breakpoints、mobile-first
├── Ch11: 狀態變體 — hover、focus、group、peer
└── Ch12: 深色模式 — dark variant、多主題

第四階段：視覺效果（Ch13-15）
├── Ch13: 動畫與過渡 — transition、animation
├── Ch14: 漸層與濾鏡 — gradient、filter、blend
└── Ch15: 容器查詢 — @container（v4 內建）

第五階段：進階配置（Ch16-18）
├── Ch16: @theme 指令 — 設計令牌配置
├── Ch17: @utility 指令 — 自訂工具類
└── Ch18: 插件生態系 — 官方與社群

第六階段：效能與框架整合（Ch19-21）
├── Ch19: 效能最佳化 — Oxide 引擎、JIT、CSS layers
├── Ch20: React 整合 — cva、tailwind-merge、Headless UI
└── Ch21: Svelte 整合 — class directive、scoped styles

第七階段：架構與維護（Ch22-24）
├── Ch22: 設計系統 — 令牌層次、元件抽取模式
├── Ch23: v3 → v4 遷移 — 升級工具、breaking changes
└── Ch24: 升級治理 — 版本鎖定、安全監控、回歸測試
```

```
持續學習方向
============

1. CSS 原生新功能
   - CSS Nesting（Tailwind v4 已支援）
   - CSS Container Queries（已內建）
   - CSS Color Level 4（oklch, display-p3）
   - CSS Anchor Positioning
   - View Transitions API

2. 框架深度整合
   - Next.js App Router + RSC 最佳實踐
   - SvelteKit 2 的進階功能
   - Astro + Tailwind（多框架）

3. 工具鏈進化
   - Vite 的最新功能
   - Lightning CSS 的進階用法
   - Biome（取代 ESLint + Prettier）

4. 設計系統進階
   - Figma Tokens + Style Dictionary
   - Design Token Community Group (DTCG) 標準
   - 跨平台設計令牌（Web + Mobile）

5. 效能監控
   - Web Vitals 持續監控
   - CSS-in-JS vs Utility CSS 效能對比
   - Edge 渲染和 streaming CSS
```

驗證：能清楚概述系列的學習路線和各階段的關鍵知識點。

## Hands-on Lab

### Foundation / 基礎練習

**任務：設定版本鎖定和安全監控**

1. 設定 `.npmrc` 啟用 `save-exact=true`。
2. 確認 `package-lock.json` 已提交到 Git。
3. 執行 `npm audit` 並記錄結果。
4. 建立 `.github/dependabot.yml` 配置。

**驗收清單：**
- [ ] `.npmrc` 包含 `save-exact=true`。
- [ ] `npm install some-package` 後 `package.json` 中無 `^` 或 `~` 前綴。
- [ ] `npm audit` 執行成功並輸出報告。
- [ ] `dependabot.yml` 格式正確且包含 Tailwind 分組。
- [ ] lock file 在 Git 中被追蹤（不在 `.gitignore` 中）。

### Advanced / 進階練習

**任務：建立更新評估流程和測試腳本**

1. 建立 Update Assessment 模板（Markdown 格式）。
2. 建立 `scripts/update-tailwind.sh` 更新腳本。
3. 使用 `gh release list` 查看最近 5 個 Tailwind releases。
4. 對最新版本填寫一份完整的 Update Assessment。
5. 建立 CSS 大小比較腳本。

**驗收清單：**
- [ ] Update Assessment 模板包含所有必要欄位。
- [ ] `update-tailwind.sh` 能成功執行並輸出版本比較。
- [ ] `gh release list` 正確列出 Tailwind releases。
- [ ] 完成了一份真實的 Update Assessment。
- [ ] CSS 大小比較腳本輸出 before/after 對照。

### Challenge / 挑戰練習

**任務：建立完整的升級治理系統並實際測試一次更新**

1. 設定所有版本鎖定和安全監控配置。
2. 建立 Playwright 視覺回歸測試（至少 3 頁面 x 3 視口）。
3. 建立 CI/CD 更新驗證管線（GitHub Actions）。
4. 建立每月更新工作流文件。
5. 設定版本更新通知（GitHub Actions cron）。
6. 建立回滾腳本。
7. 實際執行一次 Tailwind 小版本更新（或模擬），走完完整流程。

**驗收清單：**
- [ ] `.npmrc`, `dependabot.yml`, CI/CD workflows 都已設定。
- [ ] Playwright 視覺回歸測試至少覆蓋 9 個場景（3 頁 x 3 視口）。
- [ ] CI/CD 在 PR 中自動執行建置和視覺回歸。
- [ ] 每月更新工作流文件完整且可執行。
- [ ] 版本更新通知能自動建立 GitHub issue。
- [ ] 回滾腳本已測試且可用。
- [ ] 完成了一次端到端的更新流程（含 assessment、update、test、commit）。

## Reference Solution

以下是完整的升級治理系統檔案結構：

```
project-root/
├── .npmrc                               # 版本鎖定配置
├── .github/
│   ├── dependabot.yml                   # 安全監控配置
│   └── workflows/
│       ├── tailwind-update-check.yml    # PR 驗證管線
│       └── version-check.yml           # 每週版本檢查
├── scripts/
│   ├── update-tailwind.sh              # 更新腳本
│   ├── rollback-tailwind.sh            # 回滾腳本
│   └── analyze-css.mjs                 # CSS 分析腳本（Ch19）
├── tests/
│   └── visual-regression.spec.ts       # Playwright 視覺回歸
├── docs/
│   ├── update-assessment-template.md   # 評估模板
│   └── monthly-update-workflow.md      # 每月更新流程
└── update-logs/
    └── 2026-02.md                      # 月度更新記錄
```

`.npmrc`:

```ini
save-exact=true
engine-strict=true
```

完整的 `scripts/update-tailwind.sh`:

```bash
#!/bin/bash
set -e

echo "=== Tailwind CSS Update Script ==="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 檢查工作目錄是否乾淨
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: Working directory is not clean. Please commit or stash changes first."
  exit 1
fi

# 記錄當前版本
CURRENT_VERSION=$(npm ls tailwindcss --json 2>/dev/null | node -e "
  const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  console.log(d.dependencies?.tailwindcss?.version || 'unknown');
")
echo "Current version: $CURRENT_VERSION"

# 建置基準
echo ""
echo "Building baseline..."
npm run build > /dev/null 2>&1

# 記錄 CSS 大小
echo "Baseline CSS sizes:"
for file in dist/assets/*.css; do
  SIZE=$(wc -c < "$file" | tr -d ' ')
  KB=$(echo "scale=2; $SIZE / 1024" | bc)
  echo "  $(basename $file): ${KB} KB"
done

# 建立更新分支
BRANCH_NAME="chore/tailwind-update-$(date +%Y%m%d)"
echo ""
echo "Creating branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# 更新 Tailwind 相關套件
echo ""
echo "Updating packages..."
npm update tailwindcss @tailwindcss/vite @tailwindcss/postcss @tailwindcss/typography @tailwindcss/forms 2>/dev/null || true

# 安裝更新的依賴
npm install

# 記錄新版本
NEW_VERSION=$(npm ls tailwindcss --json 2>/dev/null | node -e "
  const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  console.log(d.dependencies?.tailwindcss?.version || 'unknown');
")
echo "Updated version: $NEW_VERSION"

if [ "$CURRENT_VERSION" = "$NEW_VERSION" ]; then
  echo ""
  echo "Already on latest version. No update needed."
  git checkout main
  git branch -d "$BRANCH_NAME"
  exit 0
fi

# 重新建置
echo ""
echo "Building with updated version..."
npm run build > /dev/null 2>&1

echo "Updated CSS sizes:"
for file in dist/assets/*.css; do
  SIZE=$(wc -c < "$file" | tr -d ' ')
  KB=$(echo "scale=2; $SIZE / 1024" | bc)
  echo "  $(basename $file): ${KB} KB"
done

# 執行測試（如果有）
echo ""
if npm run test:visual --if-present 2>/dev/null; then
  echo "Visual regression tests: PASSED"
else
  echo "Visual regression tests: FAILED or not configured"
  echo "Please review manually."
fi

echo ""
echo "=== Update Summary ==="
echo "From: $CURRENT_VERSION"
echo "To:   $NEW_VERSION"
echo ""
echo "Next steps:"
echo "1. Review: gh release view v$NEW_VERSION --repo tailwindlabs/tailwindcss"
echo "2. Test:   npm run dev (manual visual check)"
echo "3. Commit: git add -A && git commit -m 'chore: update tailwind $CURRENT_VERSION → $NEW_VERSION'"
echo "4. PR:     gh pr create --title 'chore: update Tailwind CSS to v$NEW_VERSION'"
echo "5. Cancel: git checkout main && git branch -D $BRANCH_NAME"
```

月度更新記錄範例：

```markdown
# Update Log - 2026-02

## Update 1: 2026-02-03
- **Package**: tailwindcss
- **From**: 4.1.2
- **To**: 4.1.3
- **Risk**: Low
- **Changes**:
  - Bug fix: Fixed arbitrary value parsing with nested parentheses
  - Bug fix: Corrected specificity for @custom-variant
- **Impact on our project**: None (we don't use the affected features)
- **CSS size change**: 42.3 KB → 42.1 KB (-0.5%)
- **Visual regression**: Passed, no differences
- **Decision**: Updated

## Update 2: 2026-02-17
- **Package**: @tailwindcss/typography
- **From**: 0.5.15
- **To**: 0.5.16
- **Risk**: Low
- **Changes**:
  - Added support for `figure` and `figcaption` styling
- **Decision**: Updated
```

驗證：所有檔案結構完整，腳本可執行，工作流可操作。

## Common Pitfalls

### 1. v4 特有：更新後 @theme 中的自訂 token 被預設值覆蓋

v4 的小版本更新可能新增預設的 theme 值。如果你使用了 `--color-*: initial` 來清除預設值，新增的預設值不會生效（這是預期行為）。但如果你沒有使用 `initial`，新的預設值可能與你的自訂值產生衝突。

```css
/* 安全做法：明確清除預設值 */
@theme {
  --color-*: initial; /* 確保只有你定義的色彩生效 */
  --color-brand: oklch(0.62 0.19 250);
}

/* 風險做法：不清除預設值 */
@theme {
  --color-brand: oklch(0.62 0.19 250);
  /* 如果 v4.2 新增了 --color-brand-xxx，可能與你的 brand 系統衝突 */
}
```

### 2. lock file 未提交導致 CI 環境版本不一致

```bash
# 確認 lock file 在 Git 中
git ls-files package-lock.json  # 應有輸出
git ls-files pnpm-lock.yaml     # 如果使用 pnpm

# 確認 CI 使用 ci 安裝（嚴格按照 lock file）
# npm ci    ← 正確
# npm install  ← 錯誤（可能更新 lock file）
```

### 3. 跳過多個小版本的累積風險

從 4.1.0 直接跳到 4.5.0 比逐步更新風險更高，因為中間可能有多個 breaking changes 累積。

```bash
# 建議：每月更新，避免跳過太多版本

# 如果已經落後多個版本：
# 1. 閱讀所有中間版本的 changelog
# 2. 特別注意標記為 "Breaking" 的變更
# 3. 考慮逐步更新（4.1 → 4.2 → 4.3 → ...）
```

### 4. 只依賴自動化測試而忽略手動檢查

視覺回歸測試有局限性，某些 CSS 變更（如 box-shadow 色差、字型渲染微調）可能低於 diff threshold 但對用戶體驗有影響。

```
每次更新後仍需手動檢查：
- 首頁的整體視覺感受
- 表單元素的互動狀態（focus, hover）
- 深色模式的對比度
- 響應式斷點的佈局切換
- 動畫的流暢度
```

### 5. Dependabot PR 自動合併而未經審查

```yaml
# 不建議：自動合併所有 Dependabot PR
# 建議：設定 PR 需要手動 review
# dependabot.yml 中不要設定 auto-merge
```

## Checklist

- [ ] 能設定 `.npmrc` 的 `save-exact=true` 確保精確版本鎖定。
- [ ] 能設定 GitHub Dependabot 進行安全監控。
- [ ] 能使用 `gh release list` 查看 Tailwind CSS 的最新版本。
- [ ] 能填寫完整的 Update Assessment 評估版本更新的影響。
- [ ] 能使用 Playwright 建立 CSS 視覺回歸測試。
- [ ] 能建立更新和回滾腳本。
- [ ] 能按照每月更新工作流完成一次端到端的依賴更新。

## Further Reading (official links only)

- [Tailwind CSS Releases](https://github.com/tailwindlabs/tailwindcss/releases)
- [Tailwind CSS Changelog](https://tailwindcss.com/changelog)
- [Tailwind CSS Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide)
- [Tailwind CSS GitHub Repository](https://github.com/tailwindlabs/tailwindcss)
- [Tailwind CSS Blog](https://tailwindcss.com/blog)
