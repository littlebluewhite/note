---
title: Property Dictionary
note_type: system
domain: system
tags: [system, schema]
created: 2026-02-03
updated: 2026-02-08
status: active
source: system
---
# Property Dictionary

## Frontmatter v2

### Required for all notes

| property | type | allowed | notes |
| --- | --- | --- | --- |
| title | Text | any | Prefer H1-aligned title. |
| note_type | Text | `knowledge`, `briefing`, `daily`, `project`, `system`, `inbox`, `archive` | Primary classification. |
| domain | Text | any slug | Logical area, e.g. `algorithm`, `database`, `programming`. |
| tags | List | any | Must include `note_type` and `domain`. |
| created | Date | `YYYY-MM-DD` | Creation date. |
| updated | Date | `YYYY-MM-DD` | Last update date. |
| status | Text | `draft`, `active`, `archived` | Lifecycle status. |
| source | Text | any | Source origin, e.g. `briefing`, `knowledge`, `project`. |

### Conditional required fields

| property | required when | notes |
| --- | --- | --- |
| date | `note_type` in (`daily`, `briefing`) | Event/content date in `YYYY-MM-DD`. |
| complexity_time | `note_type=knowledge` and `domain` in (`algorithm`, `data_structure`, `leetcode`) | Time complexity summary. |
| complexity_space | `note_type=knowledge` and `domain` in (`algorithm`, `data_structure`, `leetcode`) | Space complexity summary. |
| review_interval_days | `note_type=knowledge` and `domain` in (`algorithm`, `data_structure`, `leetcode`) | Review cadence in days. |
| next_review | `note_type=knowledge` and `domain` in (`algorithm`, `data_structure`, `leetcode`) | Next review date (`YYYY-MM-DD`). |

### Optional fields

| property | type | notes |
| --- | --- | --- |
| canonical | Text | Original path before rename/migration. |

## Naming rules

- Markdown filename: snake_case, e.g. `segment_tree_lazy.md`.
- Briefing/daily filename: `YYYY-MM-DD_topic_slug.md`.
- Folder layout:
  - `00_system`
  - `10_inbox`
  - `20_daily`
  - `30_briefings`
  - `40_knowledge`
  - `50_projects`
  - `90_archive`

## Automation commands

- `python3 scripts/vault_lint_v2.py --root . --json reports/vault_health.json`
- `python3 scripts/refactor_to_snake_case.py --root . --apply --map reports/rename_map.csv`
- `python3 scripts/migrate_frontmatter_v2.py --root . --write --rename-map reports/rename_map.csv`
- `python3 scripts/rebuild_indexes.py --root . --write`
- `python3 scripts/briefing_extract.py --root . --date today --out 10_inbox/briefing_candidates.md`
- `python3 scripts/daily_maintenance.py --root . --write`
