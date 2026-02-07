---
title: daily_workflow
note_type: system
domain: runbook
tags: [system, runbook]
created: 2026-02-08
updated: 2026-02-08
status: active
source: system
---
# Daily Workflow

## Start of Day
- Capture new ideas in `10_inbox`.
- Open today's note in `20_daily` (create from `daily.md` if absent).
- Link ongoing work to related notes in `40_knowledge` and `50_projects`.

## During Work
- Prefer creating/renaming notes with snake_case filenames.
- Keep frontmatter v2 fields complete.
- Add at least one inbound/outbound link for new knowledge notes.

## End of Day
- Run dry-run pipeline:
  - `python3 scripts/daily_maintenance.py --root . --dry-run`
- If output is clean, run write pipeline:
  - `python3 scripts/daily_maintenance.py --root . --write`
- Review generated `reports/daily_maintenance_summary.json`.

## Weekly Review
- Open `00_system/bases/review_queue.base`.
- Process notes with `next_review` due date <= today.
- Archive stale notes to `90_archive` when no longer active.
