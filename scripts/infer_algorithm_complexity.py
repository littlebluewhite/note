#!/usr/bin/env python3
"""Infer and write missing complexity_time/complexity_space.

- Uses existing Complexity section hints first.
- Falls back to a filename-based heuristic map.
- Writes values to frontmatter and adds lines to the Complexity section.

Usage:
  python3 scripts/infer_algorithm_complexity.py --root /path/to/vault
  python3 scripts/infer_algorithm_complexity.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import re
import sys

SKIP_DIRS = {'.git', '.obsidian', '.idea', '.serena'}
FRONTMATTER_DELIM = '---'

TIME_HINT_RE = re.compile(r'(?i)(time|runtime|時間|總時間)[^\n]*?(O\([^\)]+\))')
SPACE_HINT_RE = re.compile(r'(?i)(space|memory|空間)[^\n]*?(O\([^\)]+\))')
O_EXPR_RE = re.compile(r'O\([^\)]+\)')

FALLBACK = {
    'backtracking_dfs_memo': (None, 'O(#states)'),
    'combinatorics_counting': ('O(n)', 'O(1)'),
    'coordinate_compression': ('O(n log n)', 'O(n)'),
    'dp_dynamic_programming': (None, 'O(k^m)'),
    'dynamic_array_vec': (None, 'O(n)'),
    'event_sorting_sweep': (None, 'O(m)'),
    'frequency_counting': (None, 'O(U)'),
    'geometry_line_grouping': ('O(n^2)', 'O(n^2)'),
    'grouping_aggregation': ('O(n)', 'O(k)'),
    'lazy_deletion_priority_queue': (None, 'O(k)'),
    'monotonic_queue': (None, 'O(n)'),
    'prefix_sum': (None, 'O(n)'),
    'relaxation': ('O(1)', 'O(1)'),
    'sliding_window': (None, 'O(1)'),
    'sliding_window_k_smallest_sum': ('O(n log n)', 'O(n)'),
    'sorting_custom_order': (None, 'O(n)'),
    'tree_dp': (None, 'O(n)'),
    'two_pointers': (None, 'O(1)'),
    'value_sorted_prefix_min_sweep': (None, 'O(n)'),
}


def yaml_scalar(value: str) -> str:
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


def extract_complexity_section(body: str) -> tuple[int, int, str]:
    lines = body.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.strip() == '## Complexity':
            start = i
            break
    if start is None:
        return -1, -1, ''
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith('## '):
            end = j
            break
    section = ''.join(lines[start:end])
    return start, end, section


def infer_from_section(section: str) -> tuple[str | None, str | None]:
    time_val = None
    space_val = None
    for line in section.splitlines():
        m = TIME_HINT_RE.search(line)
        if m and not time_val:
            time_val = m.group(2)
        m = SPACE_HINT_RE.search(line)
        if m and not space_val:
            space_val = m.group(2)
    return time_val, space_val


def has_time_line(section: str) -> bool:
    return bool(re.search(r'(?i)^-\s*Time\s*:', section, re.M))


def has_space_line(section: str) -> bool:
    return bool(re.search(r'(?i)^-\s*Space\s*:', section, re.M))


def update_frontmatter(lines: list[str], key: str, value: str) -> tuple[list[str], bool]:
    changed = False
    key_re = re.compile(rf'^(\s*{re.escape(key)}\s*:[ \t]*)(.*)$')
    new_lines = []
    for line in lines:
        m = key_re.match(line)
        if m:
            existing = m.group(2).strip()
            if existing:
                new_lines.append(line)
            else:
                new_lines.append(f"{m.group(1)}{value}\n")
                changed = True
        else:
            new_lines.append(line)
    return new_lines, changed


def normalize_orphans(fm_lines: list[str]) -> tuple[list[str], bool]:
    changed = False
    new_lines = []
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        stripped = line.strip()
        if stripped.startswith(('complexity_time:', 'complexity_space:')):
            key = line.split(':', 1)[0]
            has_value = stripped.split(':', 1)[1].strip()
            if not has_value and i + 1 < len(fm_lines):
                nxt = fm_lines[i + 1].strip().strip('"')
                if O_EXPR_RE.fullmatch(nxt):
                    new_lines.append(f"{key}: {nxt}\n")
                    changed = True
                    i += 2
                    continue
        if O_EXPR_RE.fullmatch(stripped.strip('"')):
            changed = True
            i += 1
            continue
        new_lines.append(line)
        i += 1
    return new_lines, changed


def ensure_complexity_section(body: str, time_val: str | None, space_val: str | None) -> str:
    if not time_val and not space_val:
        return body

    lines = body.splitlines(keepends=True)
    start, end, section = extract_complexity_section(body)

    add_lines = []
    if time_val and (not section or not has_time_line(section)):
        add_lines.append(f"- Time: `{time_val}` / 時間：`{time_val}`\n")
    if space_val and (not section or not has_space_line(section)):
        add_lines.append(f"- Space: `{space_val}` / 空間：`{space_val}`\n")

    if not add_lines:
        return body

    if start == -1:
        # Insert before Related if possible, else append
        insert_at = len(lines)
        for i, line in enumerate(lines):
            if line.startswith('## Related'):
                insert_at = i
                break
        block = ['## Complexity\n'] + add_lines + ['\n']
        new_lines = lines[:insert_at] + block + lines[insert_at:]
        return ''.join(new_lines)

    # Existing section: insert after header line
    new_section_lines = section.splitlines(keepends=True)
    # Find insertion point after header line
    insert_at = 1
    while insert_at < len(new_section_lines) and new_section_lines[insert_at].strip() == '':
        insert_at += 1
    new_section_lines[insert_at:insert_at] = add_lines
    new_section = ''.join(new_section_lines)

    new_body = ''.join(lines[:start]) + new_section + ''.join(lines[end:])
    return new_body


def main():
    parser = argparse.ArgumentParser(description='Infer and write missing complexity fields.')
    parser.add_argument('--root', default='.', help='Root directory (default: current directory)')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without writing files')
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    updated = 0
    skipped = 0

    for path in iter_algorithm_files(root):
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()

        if not text.startswith('---'):
            skipped += 1
            continue

        lines = text.splitlines(keepends=True)
        fm_start, fm_end = parse_frontmatter(lines)
        if fm_start is None or fm_end is None:
            skipped += 1
            continue

        fm_lines = lines[fm_start + 1:fm_end]
        fm_lines, fm_changed = normalize_orphans(fm_lines)
        body = ''.join(lines[fm_end + 1:])

        # Read current values
        fm_text = ''.join(fm_lines)
        def get(key: str) -> str | None:
            m = re.search(rf'(?m)^[ \t]*{re.escape(key)}:[ \t]*(.*)$', fm_text)
            if not m:
                return None
            return m.group(1).strip()

        time_val = get('complexity_time') or ''
        space_val = get('complexity_space') or ''

        # Only fill missing
        need_time = not time_val
        need_space = not space_val
        if not (need_time or need_space):
            skipped += 1
            continue

        # infer from Complexity section
        _, _, section = extract_complexity_section(body)
        sec_time, sec_space = infer_from_section(section)

        inferred_time = time_val or sec_time
        inferred_space = space_val or sec_space

        # fallback by filename
        base = os.path.splitext(os.path.basename(path))[0]
        if base in FALLBACK:
            fb_time, fb_space = FALLBACK[base]
            if not inferred_time and fb_time:
                inferred_time = fb_time
            if not inferred_space and fb_space:
                inferred_space = fb_space

        if not inferred_time and not inferred_space:
            skipped += 1
            continue

        changed = False
        if inferred_time and need_time:
            fm_lines, c = update_frontmatter(fm_lines, 'complexity_time', yaml_scalar(inferred_time))
            changed = changed or c
        if inferred_space and need_space:
            fm_lines, c = update_frontmatter(fm_lines, 'complexity_space', yaml_scalar(inferred_space))
            changed = changed or c

        new_body = ensure_complexity_section(body, inferred_time if need_time else None, inferred_space if need_space else None)

        new_text = ''.join(lines[:fm_start + 1]) + ''.join(fm_lines) + '---\n' + new_body

        if new_text == text and not fm_changed:
            skipped += 1
            continue

        if args.dry_run:
            print(f'UPDATE: {path}')
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_text)
        updated += 1

    print(f'updated={updated} skipped={skipped}')


if __name__ == '__main__':
    sys.exit(main())
