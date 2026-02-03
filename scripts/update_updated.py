#!/usr/bin/env python3
"""Sync the 'updated' frontmatter field with file modification date.

Usage:
  python3 scripts/update_updated.py
  python3 scripts/update_updated.py --root /path/to/vault
  python3 scripts/update_updated.py --dry-run
  python3 scripts/update_updated.py --no-preserve-mtime
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time

SKIP_DIRS = {'.git', '.obsidian', '.idea', '.serena'}

FRONTMATTER_DELIM = '---'
UPDATED_RE = re.compile(r'^(\s*)updated\s*:\s*(.*?)\s*$')


def format_date(ts: float) -> str:
    return time.strftime('%Y-%m-%d', time.localtime(ts))


def iter_md_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.lower().endswith('.md'):
                yield os.path.join(dirpath, name)


def parse_frontmatter(lines: list[str]):
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return None, None
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIM:
            return 0, i
    return 0, None


def update_file(path: str, preserve_mtime: bool, dry_run: bool, verbose: bool) -> bool:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    if text.startswith('\ufeff'):
        text = text.lstrip('\ufeff')

    lines = text.splitlines(keepends=True)
    fm_start, fm_end = parse_frontmatter(lines)

    st = os.stat(path)
    mtime_date = format_date(st.st_mtime)

    updated_value = None
    updated_line_idx = None

    if fm_start is not None and fm_end is not None:
        fm_lines = lines[fm_start + 1:fm_end]
        for i, line in enumerate(fm_lines):
            m = UPDATED_RE.match(line.rstrip('\n'))
            if m:
                updated_value = m.group(2)
                updated_line_idx = i
                break

        if updated_value and updated_value >= mtime_date:
            return False

        new_fm_lines = list(fm_lines)
        if updated_line_idx is not None:
            indent = UPDATED_RE.match(fm_lines[updated_line_idx].rstrip('\n')).group(1)
            new_fm_lines[updated_line_idx] = f"{indent}updated: {mtime_date}\n"
        else:
            new_fm_lines.append(f"updated: {mtime_date}\n")

        new_text = ''.join(lines[:fm_start + 1]) + ''.join(new_fm_lines) + ''.join(lines[fm_end:])
    elif fm_start is None:
        if verbose:
            print(f"SKIP (no frontmatter): {path}")
        return False
    else:
        if verbose:
            print(f"SKIP (malformed frontmatter): {path}")
        return False

    if new_text == text:
        return False

    if dry_run:
        print(f"UPDATE: {path} -> updated: {mtime_date}")
        return True

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)

    if preserve_mtime:
        os.utime(path, (st.st_atime, st.st_mtime))

    if verbose:
        print(f"UPDATED: {path} -> updated: {mtime_date}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Sync 'updated' frontmatter with file mtime date.")
    parser.add_argument('--root', default='.', help='Root directory (default: current directory)')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without writing files')
    parser.add_argument('--no-preserve-mtime', dest='preserve_mtime', action='store_false', help='Do not restore original mtime')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    root = os.path.abspath(args.root)
    updated = 0

    for path in iter_md_files(root):
        if update_file(path, args.preserve_mtime, args.dry_run, args.verbose):
            updated += 1

    print(f"updated={updated}")


if __name__ == '__main__':
    sys.exit(main())
