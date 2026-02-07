#!/usr/bin/env python3
"""Vault health checks: front matter, H1, and broken links.

Usage:
  python3 scripts/note_health_check.py
  python3 scripts/note_health_check.py --root /path/to/vault
  python3 scripts/note_health_check.py --no-links
  python3 scripts/note_health_check.py --max 200
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

DEFAULT_SKIP_DIRS = {".git", ".obsidian", ".idea", ".serena", "__pycache__", ".pytest_cache"}
FRONTMATTER_DELIM = "---"

MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def iter_md_files(root: Path, skip_dirs: set[str]):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for name in filenames:
            if name.lower().endswith(".md"):
                yield Path(dirpath) / name


def parse_frontmatter(text: str):
    if not text.startswith(FRONTMATTER_DELIM + "\n"):
        return None
    end = text.find("\n" + FRONTMATTER_DELIM + "\n", 4)
    if end == -1:
        return None
    return (0, end + 5)


def strip_frontmatter(text: str) -> str:
    fm = parse_frontmatter(text)
    if not fm:
        return text
    return text[fm[1]:]


def has_h1(text: str) -> bool:
    return re.search(r"^#\s+\S", text, re.M) is not None


def is_external(target: str) -> bool:
    return target.startswith("http://") or target.startswith("https://") or target.startswith("mailto:")


def should_skip_wiki_target(target: str) -> bool:
    if not target:
        return True
    # Ignore numeric arrays like [[9, 4, 1]]
    if re.match(r"^[\d\s,]+$", target):
        return True
    return False


def check_links(md_files: list[Path], root: Path, max_items: int):
    md_set = {p.resolve() for p in md_files}
    by_name: dict[str, list[Path]] = {}
    for p in md_files:
        by_name.setdefault(p.name, []).append(p.resolve())

    broken: list[tuple[Path, str]] = []

    for p in md_files:
        text = p.read_text(encoding="utf-8", errors="ignore")

        # Markdown links
        for m in MD_LINK_RE.finditer(text):
            target = m.group(1).strip()
            if not target or target.startswith("#") or is_external(target):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            tpath = (p.parent / target).resolve()
            if not tpath.exists():
                broken.append((p, target))
                if len(broken) >= max_items:
                    return broken

        # Wiki links
        for m in WIKI_LINK_RE.finditer(text):
            target = m.group(1).strip()
            if "|" in target:
                target = target.split("|", 1)[0].strip()
            if should_skip_wiki_target(target):
                continue

            candidates: list[Path] = []
            if target.endswith(".md") or "/" in target:
                candidates.append((root / target).resolve())
            else:
                candidates.extend(by_name.get(target + ".md", []))
                candidates.append((root / (target + ".md")).resolve())

            if not any(c in md_set for c in candidates):
                broken.append((p, target))
                if len(broken) >= max_items:
                    return broken

    return broken


def main() -> int:
    parser = argparse.ArgumentParser(description="Vault health checks: front matter, H1, and broken links.")
    parser.add_argument("--root", default=".", help="Vault root (default: current directory)")
    parser.add_argument("--no-frontmatter", action="store_true", help="Skip front matter check")
    parser.add_argument("--no-h1", action="store_true", help="Skip H1 check")
    parser.add_argument("--no-links", action="store_true", help="Skip broken link check")
    parser.add_argument("--max", type=int, default=200, help="Max items to report per category")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    md_files = list(iter_md_files(root, DEFAULT_SKIP_DIRS))

    missing_front: list[Path] = []
    missing_h1: list[Path] = []

    if not args.no_frontmatter or not args.no_h1:
        for p in md_files:
            text = p.read_text(encoding="utf-8", errors="ignore")
            if not args.no_frontmatter:
                if not parse_frontmatter(text):
                    missing_front.append(p)
                    if len(missing_front) >= args.max:
                        break

        if not args.no_h1:
            for p in md_files:
                text = p.read_text(encoding="utf-8", errors="ignore")
                body = strip_frontmatter(text)
                if not has_h1(body):
                    missing_h1.append(p)
                    if len(missing_h1) >= args.max:
                        break

    broken = []
    if not args.no_links:
        broken = check_links(md_files, root, args.max)

    # Report
    issues = 0
    print(f"md_files={len(md_files)}")

    if not args.no_frontmatter:
        print(f"missing_frontmatter={len(missing_front)}")
        for p in missing_front[: args.max]:
            print(f"  {p}")
        if missing_front:
            issues += len(missing_front)

    if not args.no_h1:
        print(f"missing_h1={len(missing_h1)}")
        for p in missing_h1[: args.max]:
            print(f"  {p}")
        if missing_h1:
            issues += len(missing_h1)

    if not args.no_links:
        print(f"broken_links={len(broken)}")
        for p, target in broken[: args.max]:
            print(f"  {p} -> {target}")
        if broken:
            issues += len(broken)

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
