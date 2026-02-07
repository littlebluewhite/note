#!/usr/bin/env python3
"""Normalize Briefings frontmatter to a canonical schema.

Rules:
- Target: Briefings/**/*.md
- Default skip: Briefings/README.md
- Keep body unchanged
- Enforce frontmatter keys:
  title, category, tags, created, updated, difficulty, source, status, date

Usage:
  python3 scripts/normalize_briefings_frontmatter.py --root .
  python3 scripts/normalize_briefings_frontmatter.py --root . --dry-run
  python3 scripts/normalize_briefings_frontmatter.py --root . --write
  python3 scripts/normalize_briefings_frontmatter.py --root . --write --include-readme
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

FRONTMATTER_DELIM = "---"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FILENAME_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
KEY_RE = re.compile(r"^([A-Za-z0-9_]+):\s*(.*)$")


def parse_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith(FRONTMATTER_DELIM + "\n"):
        return None, text
    end = text.find("\n" + FRONTMATTER_DELIM + "\n", len(FRONTMATTER_DELIM) + 1)
    if end == -1:
        return None, text
    fm = text[len(FRONTMATTER_DELIM) + 1 : end]
    body = text[end + len("\n" + FRONTMATTER_DELIM + "\n") :]
    return fm, body


def strip_quotes(value: str) -> str:
    v = value.strip()
    if len(v) >= 2 and ((v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'"))):
        return v[1:-1]
    return v


def parse_inline_list(value: str) -> list[str]:
    inner = value.strip()
    if not (inner.startswith("[") and inner.endswith("]")):
        return []
    inner = inner[1:-1].strip()
    if not inner:
        return []
    parts = [p.strip() for p in inner.split(",")]
    items: list[str] = []
    for part in parts:
        cleaned = strip_quotes(part).strip()
        if cleaned:
            items.append(cleaned)
    return items


def parse_frontmatter_map(fm_text: str) -> dict[str, str | list[str]]:
    data: dict[str, str | list[str]] = {}
    lines = fm_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = KEY_RE.match(line)
        if not m:
            i += 1
            continue

        key = m.group(1).strip()
        raw = m.group(2).strip()
        if raw == "":
            j = i + 1
            list_items: list[str] = []
            while j < len(lines):
                nxt = lines[j]
                if not nxt.startswith("  - "):
                    break
                item = strip_quotes(nxt[4:].strip())
                if item:
                    list_items.append(item)
                j += 1
            if list_items:
                data[key] = list_items
                i = j
                continue
            data[key] = ""
            i += 1
            continue

        if raw.startswith("[") and raw.endswith("]"):
            data[key] = parse_inline_list(raw)
        else:
            data[key] = strip_quotes(raw)
        i += 1
    return data


def format_tags_inline(tags: list[str]) -> str:
    escaped = [t.replace('"', '\\"') for t in tags]
    return "[" + ", ".join(escaped) + "]"


def normalize_tags(existing: str | list[str] | None, topic_tag: str | None) -> list[str]:
    items: list[str] = []
    if isinstance(existing, list):
        items = [str(x).strip() for x in existing if str(x).strip()]
    elif isinstance(existing, str) and existing.strip():
        items = [existing.strip()]

    def add_if_missing(tag: str):
        lowered = {t.lower() for t in items}
        if tag.lower() not in lowered:
            items.append(tag)

    add_if_missing("briefings")
    if topic_tag:
        add_if_missing(topic_tag)
    return items


def infer_topic_tag(rel_path: Path) -> str | None:
    parts = rel_path.parts
    if len(parts) < 2:
        return None
    folder = parts[1].lower()
    if folder == "programming":
        return "programming"
    if folder == "news":
        return "news"
    return None


def infer_date(existing: str | None, file_name: str, mtime: float) -> str:
    if existing and DATE_RE.match(existing.strip()):
        return existing.strip()
    m = FILENAME_DATE_RE.match(file_name)
    if m:
        return m.group(1)
    return time.strftime("%Y-%m-%d", time.localtime(mtime))


def valid_or_fallback(value: str | None, fallback: str) -> str:
    if value and DATE_RE.match(value.strip()):
        return value.strip()
    return fallback


def build_frontmatter(rel_path: Path, existing: dict[str, str | list[str]], file_mtime: float) -> str:
    existing_title = str(existing.get("title", "")).strip() if "title" in existing else ""
    title = existing_title or rel_path.stem

    existing_date = str(existing.get("date", "")).strip() if "date" in existing else ""
    date_val = infer_date(existing_date, rel_path.name, file_mtime)

    created_val = valid_or_fallback(str(existing.get("created", "")).strip(), date_val)
    updated_val = valid_or_fallback(str(existing.get("updated", "")).strip(), date_val)

    topic_tag = infer_topic_tag(rel_path)
    tags = normalize_tags(existing.get("tags"), topic_tag)

    lines = [
        FRONTMATTER_DELIM,
        f'title: "{title.replace(chr(34), r"\\\"")}"',
        "category: briefings",
        f"tags: {format_tags_inline(tags)}",
        f"created: {created_val}",
        f"updated: {updated_val}",
        "difficulty: n/a",
        "source: briefing",
        "status: active",
        f"date: {date_val}",
        FRONTMATTER_DELIM,
        "",
    ]
    return "\n".join(lines)


def iter_briefings(root: Path, include_readme: bool):
    base = root / "Briefings"
    if not base.exists():
        return
    for p in sorted(base.rglob("*.md")):
        rel = p.relative_to(root)
        if not include_readme and rel.as_posix() == "Briefings/README.md":
            continue
        yield p, rel


def normalize_file(path: Path, rel: Path, write: bool, dry_run: bool) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")

    fm, body = parse_frontmatter(text)
    existing = parse_frontmatter_map(fm) if fm is not None else {}
    st = path.stat()

    new_fm = build_frontmatter(rel, existing, st.st_mtime)
    new_text = new_fm + body

    changed = new_text != text
    if changed and (dry_run or not write):
        print(f"UPDATE: {rel.as_posix()}")
    if changed and write:
        path.write_text(new_text, encoding="utf-8")
        print(f"UPDATED: {rel.as_posix()}")
    return changed, rel.as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Briefings frontmatter")
    parser.add_argument("--root", default=".", help="Vault root (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes")
    parser.add_argument("--write", action="store_true", help="Write changes to files")
    parser.add_argument("--include-readme", action="store_true", help="Also process Briefings/README.md")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    updated = 0
    skipped = 0

    for path, rel in iter_briefings(root, args.include_readme):
        changed, _ = normalize_file(path, rel, write=args.write, dry_run=args.dry_run)
        if changed:
            updated += 1
        else:
            skipped += 1

    mode = "write" if args.write else "preview"
    print(f"mode={mode} updated={updated} skipped={skipped}")
    if not args.write and not args.dry_run:
        print("hint=Use --write to apply changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
