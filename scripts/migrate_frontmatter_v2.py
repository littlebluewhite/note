#!/usr/bin/env python3
"""Migrate markdown frontmatter to schema v2.

Usage:
  python3 scripts/migrate_frontmatter_v2.py --root .
  python3 scripts/migrate_frontmatter_v2.py --root . --write --rename-map reports/rename_map.csv
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
from pathlib import Path

from vault_utils_v2 import (
    DATE_PREFIX_RE,
    classify_note,
    dump_frontmatter,
    format_date,
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


def parse_tags(raw: str | list[str] | None, note_type: str, domain: str) -> list[str]:
    if isinstance(raw, list):
        tags = [str(x).strip() for x in raw if str(x).strip()]
    elif isinstance(raw, str) and raw.strip():
        tags = [raw.strip()]
    else:
        tags = []

    lowered = {t.lower() for t in tags}
    for t in [note_type, domain]:
        if t and t.lower() not in lowered:
            tags.append(t)
            lowered.add(t.lower())
    return tags


def infer_date_from_stem(stem: str) -> str | None:
    m = DATE_PREFIX_RE.match(stem)
    if not m:
        return None
    value = m.group(1)
    return value if valid_date(value) else None


def h1_title(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# "):
            t = line[2:].strip()
            if t:
                return t
    return None


def load_rename_map(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    out: dict[str, str] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            old_path = (row.get("old_path") or "").strip()
            new_path = (row.get("new_path") or "").strip()
            if old_path and new_path and old_path != new_path:
                out[new_path] = old_path
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate frontmatter to schema v2")
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--rename-map", default="", help="Optional rename map CSV path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rename_map_path = Path(args.rename_map).resolve() if args.rename_map else None
    rename_by_new = load_rename_map(rename_map_path)

    changed = 0
    scanned = 0

    for p in iter_markdown_files(root):
        scanned += 1
        rel = p.relative_to(root)
        rel_posix = rel.as_posix()
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm_text, body = parse_frontmatter(text)

        existing = parse_frontmatter_map(fm_text) if fm_text is not None else {}

        note_type_guess, domain_guess = classify_note(rel)
        note_type = str(existing.get("note_type", note_type_guess)).strip() or note_type_guess
        domain = str(existing.get("domain", domain_guess)).strip() or domain_guess

        created = str(existing.get("created", "")).strip()
        updated = str(existing.get("updated", "")).strip()

        st = p.stat()
        file_date = format_date(st.st_mtime)

        if not valid_date(created):
            created = str(existing.get("date", "")).strip() if valid_date(str(existing.get("date", "")).strip()) else file_date
        if not valid_date(updated):
            updated = file_date

        title = str(existing.get("title", "")).strip() or h1_title(body) or p.stem
        status = str(existing.get("status", "")).strip() or "active"
        source = str(existing.get("source", "")).strip() or note_type
        tags = parse_tags(existing.get("tags"), note_type, domain)

        data: dict[str, str | list[str]] = {
            "title": title,
            "note_type": note_type,
            "domain": domain,
            "tags": tags,
            "created": created,
            "updated": updated,
            "status": status,
            "source": source,
        }

        if note_type in {"daily", "briefing"}:
            date_val = str(existing.get("date", "")).strip()
            if not valid_date(date_val):
                date_val = infer_date_from_stem(p.stem) or created
            data["date"] = date_val

        if note_type == "knowledge" and domain in {"algorithm", "data_structure", "leetcode"}:
            ctime = str(existing.get("complexity_time", "")).strip() or "unknown"
            cspace = str(existing.get("complexity_space", "")).strip() or "unknown"
            data["complexity_time"] = ctime
            data["complexity_space"] = cspace

            interval_raw = str(existing.get("review_interval_days", "")).strip()
            interval = interval_raw if interval_raw.isdigit() else "14"
            data["review_interval_days"] = interval

            next_review = str(existing.get("next_review", "")).strip()
            if not valid_date(next_review):
                try:
                    base = dt.datetime.strptime(created, "%Y-%m-%d").date()
                except ValueError:
                    base = dt.date.today()
                next_review = (base + dt.timedelta(days=int(interval))).strftime("%Y-%m-%d")
            data["next_review"] = next_review

        canonical = rename_by_new.get(rel_posix)
        if canonical:
            data["canonical"] = canonical

        new_fm = dump_frontmatter(data, ORDER)
        new_text = new_fm + body

        if new_text != text:
            changed += 1
            if args.write:
                p.write_text(new_text, encoding="utf-8")

    print(f"scanned={scanned} changed={changed} write={args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
