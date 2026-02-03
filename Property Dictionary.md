---
title: "Property Dictionary"
category: root
tags: [root]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: note
status: active
---
# Property Dictionary

This note defines the canonical properties for this vault. Keep property names and types consistent across notes.

## Core properties

| property | type | applies to | default | allowed | notes |
| --- | --- | --- | --- | --- | --- |
| title | Text | all md | (manual) | any | Prefer the H1 or filename if empty. |
| category | Text | all md | folder name | e.g. algorithm, leetcode, database | Derived from top-level folder (lowercase). Template files may keep the target category. |
| tags | List | all md | [category] | any | Keep category in tags (templates may use target tags). |
| created | Date | all md | file birth time | YYYY-MM-DD | Set on note creation. |
| updated | Date | all md | file mtime | YYYY-MM-DD | Update when content changes. |
| difficulty | Text | leetcode | unknown | easy, medium, hard, unknown, n/a | Use n/a outside leetcode. |
| source | Text | all md | category | note, briefing, algorithm, leetcode, database | Use where the content originates. |
| status | Text | all md | active | draft, active, archived | Lifecycle control. |

## Optional properties (future)

| property | type | applies to | default | allowed | notes |
| --- | --- | --- | --- | --- | --- |
| complexity_time | Text | algorithm/leetcode |  | e.g. O(n log n) | Time complexity. |
| complexity_space | Text | algorithm/leetcode |  | e.g. O(n) | Space complexity. |
| date | Date | briefings |  | YYYY-MM-DD | Briefing date. |

## Automation

- `scripts/update_updated.py`: syncs `updated` to file modification date (mtime) for Markdown notes.
- `scripts/add_optional_properties.py`: adds complexity fields without overwriting values.
- `scripts/infer_data_structure_complexity.py`: infers and fills complexity fields for data_structure notes.
