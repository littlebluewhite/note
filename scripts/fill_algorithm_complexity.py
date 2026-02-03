#!/usr/bin/env python3
"""Fill complexity_time/complexity_space in algorithm notes from the Complexity section.

- Only fills if the frontmatter field is empty.
- Extracts first O(...) expression near Time/Space keywords.

Usage:
  python3 scripts/fill_algorithm_complexity.py --root /path/to/vault
  python3 scripts/fill_algorithm_complexity.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import re
import sys

SKIP_DIRS = {'.git', '.obsidian', '.idea', '.serena'}
FRONTMATTER_DELIM = '---'

TIME_LINE_RE = re.compile(r'(?i)(time|total\s*time|runtime|時間|總時間|時間複雜度)[^\n]*?(O\([^\)]+\))')
SPACE_LINE_RE = re.compile(r'(?i)(space|memory|extra\s*space|空間|空間複雜度)[^\n]*?(O\([^\)]+\))')
O_EXPR_RE = re.compile(r'O\([^\)]+\)')
ORPHAN_O_RE = re.compile(r'^\"?O\([^\)]+\)\"?$')


def yaml_scalar(value: str) -> str:
    if not value:
        return value
    if re.search(r'\s', value):
        return f'"{value}"'
    return value


def iter_algorithm_files(root: str):
    base = os.path.join(root, 'algorithm')
    for dirpath, dirnames, filenames in os.walk(base):
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


def extract_complexity_section(body: str) -> str:
    lines = body.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == '## Complexity':
            start = i + 1
            break
    if start is None:
        return ''
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith('## ') and j != start:
            end = j
            break
    return '\n'.join(lines[start:end]).strip()


def extract_time_space(section: str):
    time_val = None
    space_val = None

    if not section:
        return None, None

    for line in section.splitlines():
        m = TIME_LINE_RE.search(line)
        if m and not time_val:
            time_val = m.group(2)
        m = SPACE_LINE_RE.search(line)
        if m and not space_val:
            space_val = m.group(2)

    if not time_val:
        # fallback: first O(...) in section
        m = O_EXPR_RE.search(section)
        if m:
            time_val = m.group(0)

    return time_val, space_val


def update_frontmatter(lines: list[str], key: str, value: str, overwrite: bool) -> tuple[list[str], bool]:
    changed = False
    new_lines = []
    key_re = re.compile(rf'^(\s*{re.escape(key)}\s*:)(\s*)(.*)$')
    i = 0
    last_key = None
    while i < len(lines):
        line = lines[i]
        if ORPHAN_O_RE.match(line.strip()) and last_key in {'complexity_time', 'complexity_space'}:
            # Drop orphan complexity line from previous bad updates
            changed = True
            i += 1
            continue
        m = key_re.match(line)
        if m:
            existing = m.group(3).strip()
            if existing and not overwrite:
                new_lines.append(line)
            else:
                if value:
                    new_lines.append(f"{m.group(1)} {value}\n")
                else:
                    new_lines.append(f"{m.group(1)}\n")
                changed = True
            last_key = key
        else:
            new_lines.append(line)
            last_key = None
        i += 1
    return new_lines, changed


def main():
    parser = argparse.ArgumentParser(description='Fill complexity_time/space from Complexity section.')
    parser.add_argument('--root', default='.', help='Root directory (default: current directory)')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without writing files')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing complexity fields')
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    updated = 0
    skipped = 0

    for path in iter_algorithm_files(root):
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        if text.startswith('\ufeff'):
            text = text.lstrip('\ufeff')
        lines = text.splitlines(keepends=True)
        fm_start, fm_end = parse_frontmatter(lines)
        if fm_start is None or fm_end is None:
            skipped += 1
            continue
        fm_lines = lines[fm_start + 1:fm_end]
        body = ''.join(lines[fm_end + 1:])

        section = extract_complexity_section(body)
        time_val, space_val = extract_time_space(section)

        changed = False
        fm_lines, c = update_frontmatter(
            fm_lines,
            'complexity_time',
            yaml_scalar(time_val) if time_val else '',
            args.overwrite,
        )
        changed = changed or c
        fm_lines, c = update_frontmatter(
            fm_lines,
            'complexity_space',
            yaml_scalar(space_val) if space_val else '',
            args.overwrite,
        )
        changed = changed or c

        if not changed:
            skipped += 1
            continue

        new_text = ''.join(lines[:fm_start + 1]) + ''.join(fm_lines) + ''.join(lines[fm_end:])
        if args.dry_run:
            print(f'UPDATE: {path}')
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_text)
        updated += 1

    print(f'updated={updated} skipped={skipped}')


if __name__ == '__main__':
    sys.exit(main())
