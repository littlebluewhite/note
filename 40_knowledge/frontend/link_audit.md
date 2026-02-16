---
title: Frontend Link Audit
note_type: system
domain: frontend
tags: [system, frontend, audit]
created: 2026-02-16
updated: 2026-02-16
status: active
source: system
---
# Frontend Link Audit

## Audit Scope

- Scope root: `40_knowledge/frontend`
- File types: `*.md`
- Link types checked: 相對連結（排除 `http`, `mailto`, `#anchor`）
- Audit date: `2026-02-16`

## Audit Command

```bash
for f in $(rg --files 40_knowledge/frontend -g '*.md'); do
  rg -o '\[[^]]+\]\(([^)]+)\)' "$f" | while IFS= read -r link; do
    target=$(printf '%s' "$link" | sed -E 's/.*\]\(([^)#]+).*/\1/')
    case "$target" in
      http*|mailto:*|#*|'') continue ;;
    esac
    dir=$(dirname "$f")
    path="$dir/$target"
    [ -e "$path" ] || echo "$f -> $target"
  done
done
```

## Result Snapshot

- Broken link count: `0`
- Status: `PASS`

## Navigation Reachability Check

- Start point: `40_knowledge/frontend/readme.md`
- Expected: 4 個既有系列 + 1 個新實戰系列均可在 1 次點擊內抵達。
- Result: `PASS`
- Note: 系列 readme 到章節連結均為 1 次點擊，符合「不超過 2 次點擊」要求。

## Next Audit

- Schedule: 每月第 1 週更新
- Owner: `wilson08`
