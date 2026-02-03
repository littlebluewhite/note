#!/usr/bin/env python3
"""Add complexity properties to frontmatter without overwriting existing values.

Adds to algorithm/leetcode/data_structure notes:
  - complexity_time:
  - complexity_space:

Usage:
  python3 scripts/add_optional_properties.py --root /path/to/vault
  python3 scripts/add_optional_properties.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import re
import sys

SKIP_DIRS = {'.git', '.obsidian', '.idea', '.serena'}
FRONTMATTER_DELIM = '---'

COMPLEXITY = [
    ('complexity_time', ''),
    ('complexity_space', ''),
]


KEY_RE_CACHE: dict[str, re.Pattern] = {}


def key_exists(fm_text: str, key: str) -> bool:
    if key not in KEY_RE_CACHE:
        KEY_RE_CACHE[key] = re.compile(rf'(?m)^\s*{re.escape(key)}\s*:')
    return KEY_RE_CACHE[key].search(fm_text) is not None


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


def main():
    parser = argparse.ArgumentParser(description='Add optional properties to frontmatter.')
    parser.add_argument('--root', default='.', help='Root directory (default: current directory)')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without writing files')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    updated = 0
    skipped = 0

    for path in iter_md_files(root):
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()

        if text.startswith('\ufeff'):
            text = text.lstrip('\ufeff')

        lines = text.splitlines(keepends=True)
        fm_start, fm_end = parse_frontmatter(lines)

        if fm_start is None:
            if args.verbose:
                print(f'SKIP (no frontmatter): {path}')
            skipped += 1
            continue
        if fm_end is None:
            if args.verbose:
                print(f'SKIP (malformed frontmatter): {path}')
            skipped += 1
            continue

        fm_text = ''.join(lines[fm_start + 1:fm_end])

        rel_path = os.path.relpath(path, root)
        top_folder = rel_path.split(os.sep)[0].lower() if os.sep in rel_path else 'root'

        additions = []
        if top_folder in {'algorithm', 'leetcode', 'data_structure'}:
            for key, default in COMPLEXITY:
                if not key_exists(fm_text, key):
                    line = f'{key}: {default}\n' if default else f'{key}:\n'
                    additions.append(line)

        if not additions:
            skipped += 1
            continue

        new_lines = []
        new_lines.extend(lines[:fm_end])
        new_lines.extend(additions)
        new_lines.extend(lines[fm_end:])
        new_text = ''.join(new_lines)

        if args.dry_run:
            print(f'UPDATE: {path}')
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_text)
        updated += 1

    print(f'updated={updated} skipped={skipped}')


if __name__ == '__main__':
    sys.exit(main())
