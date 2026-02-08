#!/usr/bin/env python3
"""Mark knowledge notes as reviewed, advancing next_review with spaced repetition.

Usage:
  python3 scripts/mark_reviewed.py --root . --file 40_knowledge/algorithm/prefix_sum.md --write
  python3 scripts/mark_reviewed.py --root . --file 40_knowledge/algorithm/prefix_sum.md --quality easy --write
  python3 scripts/mark_reviewed.py --root . --due-today --dry-run
  python3 scripts/mark_reviewed.py --root . --due-today --write
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from vault_utils_v2 import (
    dump_frontmatter,
    iter_markdown_files,
    parse_frontmatter,
    parse_frontmatter_map,
    today_str,
    valid_date,
)

ORDER = [
    "title",
    "note_type",
    "domain",
    "tags",
    "created",
    "updated",
    "status",
    "source",
    "date",
    "complexity_time",
    "complexity_space",
    "review_interval_days",
    "next_review",
    "canonical",
]

MULTIPLIERS = {"easy": 2.5, "good": 1.5, "hard": 0.5}
MIN_INTERVAL = 1
MAX_INTERVAL = 180


def compute_next_interval(current: int, quality: str) -> int:
    mult = MULTIPLIERS.get(quality, 1.5)
    new = int(current * mult)
    return max(MIN_INTERVAL, min(MAX_INTERVAL, new))


def find_due_notes(root: Path, today: str) -> list[Path]:
    due: list[Path] = []
    for p in iter_markdown_files(root):
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm_text, _ = parse_frontmatter(text)
        if fm_text is None:
            continue
        fm = parse_frontmatter_map(fm_text)
        next_review = str(fm.get("next_review", "")).strip()
        if not valid_date(next_review):
            continue
        if next_review <= today:
            due.append(p)
    return sorted(due)


def update_note(p: Path, quality: str, today: str, write: bool) -> dict[str, str]:
    text = p.read_text(encoding="utf-8", errors="ignore")
    fm_text, body = parse_frontmatter(text)
    if fm_text is None:
        return {"file": str(p), "status": "skip", "reason": "no frontmatter"}

    fm = parse_frontmatter_map(fm_text)
    interval_raw = str(fm.get("review_interval_days", "")).strip()
    if not interval_raw.isdigit():
        return {"file": str(p), "status": "skip", "reason": "no review_interval_days"}

    old_interval = int(interval_raw)
    new_interval = compute_next_interval(old_interval, quality)
    next_date = (dt.date.today() + dt.timedelta(days=new_interval)).strftime("%Y-%m-%d")

    fm["review_interval_days"] = str(new_interval)
    fm["next_review"] = next_date
    fm["updated"] = today

    new_fm = dump_frontmatter(fm, ORDER)
    new_text = new_fm + body

    if write:
        p.write_text(new_text, encoding="utf-8")

    return {
        "file": str(p),
        "status": "updated" if write else "would_update",
        "quality": quality,
        "old_interval": str(old_interval),
        "new_interval": str(new_interval),
        "next_review": next_date,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Mark notes as reviewed")
    parser.add_argument("--root", default=".")
    parser.add_argument("--file", dest="file_path", default="", help="Relative path to a single note")
    parser.add_argument("--due-today", action="store_true", help="Find and process all overdue notes")
    parser.add_argument("--quality", choices=["easy", "good", "hard"], default="good")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.write and args.dry_run:
        print("Cannot use --write and --dry-run together")
        return 2

    if not args.file_path and not args.due_today:
        print("Must specify --file or --due-today")
        return 2

    root = Path(args.root).resolve()
    today = today_str()
    write = args.write

    results: list[dict[str, str]] = []

    if args.file_path:
        target = root / args.file_path
        if not target.exists():
            print(f"File not found: {args.file_path}")
            return 1
        results.append(update_note(target, args.quality, today, write))
    elif args.due_today:
        due = find_due_notes(root, today)
        if not due:
            print(f"due=0 (no notes with next_review <= {today})")
            return 0
        for p in due:
            results.append(update_note(p, args.quality, today, write))

    updated = sum(1 for r in results if r["status"] in ("updated", "would_update"))
    skipped = sum(1 for r in results if r["status"] == "skip")
    mode = "write" if write else "dry-run"

    for r in results:
        if r["status"] in ("updated", "would_update"):
            print(f"  {r['file']}: interval {r['old_interval']}d -> {r['new_interval']}d, next={r['next_review']}")

    print(f"mode={mode} due={len(results)} updated={updated} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
