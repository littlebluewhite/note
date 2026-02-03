#!/usr/bin/env python3
"""Infer and write missing complexity_time/complexity_space for data_structure notes.

- Uses existing Complexity section hints when possible.
- Falls back to filename-based defaults.
- Writes values to frontmatter and adds Time/Space lines to Complexity section.

Usage:
  python3 scripts/infer_data_structure_complexity.py --root /path/to/vault
  python3 scripts/infer_data_structure_complexity.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import re
import sys

SKIP_DIRS = {'.git', '.obsidian', '.idea', '.serena'}
FRONTMATTER_DELIM = '---'

TIME_HINT_RE = re.compile(r'(?i)(time|build|update|query|access|insert|remove|push|pop|lookup|find|union|amortized|average|traversal|bfs|dfs|scan)[^\n]*?(O\([^\)]+\))')
SPACE_HINT_RE = re.compile(r'(?i)(space|memory|extra\s*space|空間)[^\n]*?(O\([^\)]+\))')
O_EXPR_RE = re.compile(r'O\([^\)]+\)')

FALLBACK = {
    'adjacency_list': ('O(n + m)', 'O(n + m)'),
    'binary_tree': ('O(n)', 'O(h)'),
    'deque_vecdeque': ('O(1)', 'O(n)'),
    'doubly_linked_list': ('O(1)', 'O(n)'),
    'dp_1d_array': ('O(n^2)', 'O(n)'),
    'dp_2d_array': ('O(mn)', 'O(mn)'),
    'hash_map_set': ('O(1)', 'O(n)'),
    'ordered_multiset_btreemap': ('O(log n)', 'O(n)'),
    'pairwise_index_scan': ('O(n^2)', 'O(1)'),
    'prefix_suffix_count_array': ('O(n)', 'O(n)'),
    'presence_array': ('O(1)', 'O(R)'),
    'priority_queue_binary_heap': ('O(log n)', 'O(n)'),
    'segment_tree_lazy': ('O(log n)', 'O(n)'),
    'sorted_array': ('O(n log n)', 'O(n)'),
    'stack': ('O(1)', 'O(n)'),
    'state_tracking_array': ('O(1)', 'O(n)'),
    'suffix_max_array': ('O(n)', 'O(n)'),
    'union_find_dsu': ('O(alpha(n))', 'O(n)'),
    'weighted_graph': ('O(n + m)', 'O(n + m)'),
}


def yaml_scalar(value: str) -> str:
    if re.search(r'\s', value):
        return f'"{value}"'
    return value


def iter_files(root: str):
    base = os.path.join(root, 'data_structure')
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
        if line.strip() in {'## Complexity', '## Complexity / 複雜度', '## Complexity / 复杂度'}:
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


def section_has_time(section: str) -> bool:
    if not section:
        return False
    for line in section.splitlines():
        if 'space' in line.lower() or '空間' in line:
            continue
        if O_EXPR_RE.search(line):
            return True
    return False


def section_has_space(section: str) -> bool:
    return bool(SPACE_HINT_RE.search(section))


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


def ensure_complexity_section(body: str, time_val: str | None, space_val: str | None) -> str:
    if not time_val and not space_val:
        return body

    lines = body.splitlines(keepends=True)
    start, end, section = extract_complexity_section(body)

    add_lines = []
    if time_val and not section_has_time(section):
        add_lines.append(f"- Time: `{time_val}` / 時間：`{time_val}`\n")
    if space_val and not section_has_space(section):
        add_lines.append(f"- Space: `{space_val}` / 空間：`{space_val}`\n")

    if not add_lines and section:
        return body

    if start == -1:
        insert_at = len(lines)
        for i, line in enumerate(lines):
            if line.startswith('## Pitfalls') or line.startswith('## Notes') or line.startswith('## Related'):
                insert_at = i
                break
        block = ['## Complexity / 複雜度\n'] + add_lines + ['\n']
        new_lines = lines[:insert_at] + block + lines[insert_at:]
        return ''.join(new_lines)

    new_section_lines = section.splitlines(keepends=True)
    insert_at = 1
    while insert_at < len(new_section_lines) and new_section_lines[insert_at].strip() == '':
        insert_at += 1
    new_section_lines[insert_at:insert_at] = add_lines
    new_section = ''.join(new_section_lines)

    new_body = ''.join(lines[:start]) + new_section + ''.join(lines[end:])
    return new_body


def main():
    parser = argparse.ArgumentParser(description='Infer and write missing complexity fields for data_structure notes.')
    parser.add_argument('--root', default='.', help='Root directory (default: current directory)')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without writing files')
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    updated = 0
    skipped = 0

    for path in iter_files(root):
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
        body = ''.join(lines[fm_end + 1:])

        fm_text = ''.join(fm_lines)
        def get(key: str) -> str | None:
            m = re.search(rf'(?m)^[ \t]*{re.escape(key)}:[ \t]*(.*)$', fm_text)
            if not m:
                return None
            return m.group(1).strip()

        time_val = get('complexity_time') or ''
        space_val = get('complexity_space') or ''

        need_time = not time_val
        need_space = not space_val

        start, end, section = extract_complexity_section(body)
        sec_time, sec_space = infer_from_section(section)

        inferred_time = time_val or sec_time
        inferred_space = space_val or sec_space

        base = os.path.splitext(os.path.basename(path))[0]
        if base in FALLBACK:
            fb_time, fb_space = FALLBACK[base]
            if not inferred_time and fb_time:
                inferred_time = fb_time
            if not inferred_space and fb_space:
                inferred_space = fb_space

        changed = False
        if inferred_time and need_time:
            fm_lines, c = update_frontmatter(fm_lines, 'complexity_time', yaml_scalar(inferred_time))
            changed = changed or c
        if inferred_space and need_space:
            fm_lines, c = update_frontmatter(fm_lines, 'complexity_space', yaml_scalar(inferred_space))
            changed = changed or c

        new_body = ensure_complexity_section(body, inferred_time if need_time else None, inferred_space if need_space else None)

        new_text = ''.join(lines[:fm_start + 1]) + ''.join(fm_lines) + '---\n' + new_body

        if new_text == text:
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
