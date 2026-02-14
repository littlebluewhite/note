---
title: Zustand 5 Monthly Update Log Template
note_type: system
domain: frontend
tags: [system, frontend, zustand5]
created: 2026-02-14
updated: 2026-02-14
status: active
source: system
---
# Zustand 5 Monthly Update Log Template

## Purpose

固定每月檢查 Zustand / React / Next 版本與安全資訊，避免「知道要更新但沒落地」。

## Baseline Snapshot

- Snapshot date: `2026-02-14`
- Zustand latest stable (reference): `5.0.11` (2026-02-01)
- React main line: `19.2`
- Next.js baseline: `16.x App Router`
- Track sources:
  - https://github.com/pmndrs/zustand/releases
  - https://zustand.docs.pmnd.rs/migrations/migrating-to-v5
  - https://react.dev/
  - https://nextjs.org/docs/app/building-your-application/upgrading

## Monthly Checklist

- [ ] 查 Zustand 最新 release 與 migration note。
- [ ] 查 React/Next 最新 release 與 advisories。
- [ ] 比對目前專案版本與目標版本。
- [ ] 檢查 v5 API 正確性（`useShallow` / `createWithEqualityFn`）。
- [ ] 檢查 persist rapid updates 一致性（storage vs in-memory）。
- [ ] 跑 lint/test/build + smoke。
- [ ] 記錄決策：立即升級 / 延後升級。

## Log Entry Template

```md
## YYYY-MM (owner: <name>)

### Version status
- Current: zustand __ / react __ / next __
- Latest: zustand __ (release date: __) / react __ (release date: __) / next __ (release date: __)
- Delta: __

### Risk status
- Breaking change risk: low / medium / high
- Security advisories: none / <link>
- API compatibility: clean / legacy pattern found
- Persist consistency: pass / fail

### Decision
- Action: patch now / minor now / defer
- Reason:
- Deadline:

### Validation
- Commands:
  - npm run lint
  - npm run test
  - npm run build
- Smoke routes:
  - /
  - /dashboard
  - /settings
- Persist checks:
  - rapid updates consistency: pass / fail
- Result:

### Follow-ups
- Docs update needed:
- Team training note needed:
- Owner:
```
