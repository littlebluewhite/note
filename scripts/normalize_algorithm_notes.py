#!/usr/bin/env python3
"""Normalize Algorithm notes to a consistent section format.

- Preserves frontmatter and H1.
- Maps existing sections into a canonical order.
- Unrecognized sections are moved under Notes with subheadings.
- Omits empty sections.

Usage:
  python3 scripts/normalize_algorithm_notes.py --root /path/to/vault
  python3 scripts/normalize_algorithm_notes.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import re
import sys

SKIP_DIRS = {'.git', '.obsidian', '.idea', '.serena'}
FRONTMATTER_DELIM = '---'

CANONICAL = [
    'Goal',
    'When to Use',
    'Core Idea',
    'Steps',
    'Complexity',
    'Pitfalls',
    'Examples',
    'Notes',
    'Related',
]

RE_GOAL = re.compile(r'\bgoal\b|目標|目的', re.IGNORECASE)
RE_WHEN = re.compile(r'when\s+to\s+use|use\s+cases?|usage|preconditions?|prereq|assumptions', re.IGNORECASE)
RE_WHEN_ZH = re.compile(r'使用時機|何時使用|前置|先備知識|先決條件|適用')
RE_CORE = re.compile(r'core\s+idea|key\s+idea|key\s+formula|definition|concept|principle|common\s+formulas', re.IGNORECASE)
RE_CORE_ZH = re.compile(r'核心|關鍵|公式|原理|概念|定義|常用公式')
RE_STEPS_INLINE = re.compile(r'pattern|workflow|steps?|algorithm|procedure|approach|strategy|process', re.IGNORECASE)
RE_STEPS_INLINE_ZH = re.compile(r'流程|步驟|策略|作法|方法|模式')
RE_STEPS_DETAIL = re.compile(r'state|transition|base\s+cases?|order|invariant|rule|update\s+rule', re.IGNORECASE)
RE_STEPS_DETAIL_ZH = re.compile(r'狀態|轉移|初始條件|計算順序|不變量|規則')
RE_COMPLEXITY = re.compile(r'complexity|複雜度', re.IGNORECASE)
RE_PITFALLS = re.compile(r'pitfalls?|gotchas?|edge\s+cases?|陷阱|易錯|注意事項', re.IGNORECASE)
RE_RELATED = re.compile(r'related|references?|相關|延伸', re.IGNORECASE)

RE_EXAMPLES = re.compile(r'example|examples|worked\s+example|demo|範例|例子|示例|實作範例', re.IGNORECASE)
RE_EXAMPLE_DETAIL = re.compile(r'(example|範例|例子|示例)\\s*\\d|[:：]', re.IGNORECASE)
RE_RUST_SNIPPET = re.compile(r'rust\\s+snippet|rust\\s+範例|code\\s+snippet', re.IGNORECASE)
RE_DIAGRAM = re.compile(r'diagram|visual|圖示|視覺化', re.IGNORECASE)

RE_NOTES_INLINE = re.compile(r'^notes?$', re.IGNORECASE)
RE_NOTES_DETAIL = re.compile(r'notes?|implementation|snippet|template|minimal\\s+template|proof|correctness|why\\s+it\\s+works|thought\\s+process|variations', re.IGNORECASE)


def classify_heading(title: str) -> tuple[str, bool]:
    t = title.strip()

    if RE_RUST_SNIPPET.search(t):
        return 'Examples', False
    if RE_DIAGRAM.search(t):
        return 'Examples', False
    if RE_EXAMPLES.search(t):
        if RE_EXAMPLE_DETAIL.search(t):
            return 'Examples', False
        return 'Examples', True

    if RE_GOAL.search(t):
        return 'Goal', True
    if RE_WHEN.search(t) or RE_WHEN_ZH.search(t):
        return 'When to Use', True
    if RE_CORE.search(t) or RE_CORE_ZH.search(t):
        return 'Core Idea', True

    if RE_STEPS_DETAIL.search(t) or RE_STEPS_DETAIL_ZH.search(t):
        return 'Steps', False
    if RE_STEPS_INLINE.search(t) or RE_STEPS_INLINE_ZH.search(t):
        return 'Steps', True

    if RE_COMPLEXITY.search(t):
        return 'Complexity', True
    if RE_PITFALLS.search(t):
        return 'Pitfalls', True
    if RE_RELATED.search(t):
        return 'Related', True

    if RE_NOTES_INLINE.search(t):
        return 'Notes', True
    if RE_NOTES_DETAIL.search(t):
        return 'Notes', False

    return 'Notes', False


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


def strip_goal_prefix(text: str) -> str:
    t = text.strip()
    prefixes = ['goal:', 'goal：', '目標：', '目的：', '目標:', '目的:']
    for p in prefixes:
        if t.lower().startswith(p):
            return t[len(p):].strip()
    return text.strip()


def is_placeholder(content: str) -> bool:
    return content.strip() in {'-', '—', '–'}


def split_subsections(lines: list[str]) -> tuple[str, list[tuple[str, str]]]:
    main_lines: list[str] = []
    subs: list[tuple[str, str]] = []
    current_heading: str | None = None
    current_lines: list[str] = []
    in_code = False

    def flush_sub():
        nonlocal current_heading, current_lines
        if current_heading is not None:
            subs.append((current_heading, ''.join(current_lines).strip()))
        current_heading = None
        current_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code

        if (not in_code) and line.startswith('### '):
            if current_heading is not None:
                flush_sub()
            current_heading = line[4:].strip()
            current_lines = []
        else:
            if current_heading is None:
                main_lines.append(line)
            else:
                current_lines.append(line)

    if current_heading is not None:
        flush_sub()

    main_content = ''.join(main_lines).strip()
    return main_content, subs


def normalize_file(path: str, dry_run: bool, verbose: bool) -> bool:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    if text.startswith('\ufeff'):
        text = text.lstrip('\ufeff')

    lines = text.splitlines(keepends=True)
    fm_start, fm_end = parse_frontmatter(lines)
    if fm_start is not None and fm_end is None:
        if verbose:
            print(f'SKIP (malformed frontmatter): {path}')
        return False

    body = ''.join(lines[fm_end + 1:]) if fm_start is not None else text

    body_lines = body.splitlines(keepends=True)
    h1_idx = None
    for i, line in enumerate(body_lines):
        if line.startswith('# '):
            h1_idx = i
            break

    if h1_idx is None:
        if verbose:
            print(f'SKIP (no H1): {path}')
        return False

    h1_line = body_lines[h1_idx].rstrip('\n')
    after_h1 = body_lines[h1_idx + 1:]

    # Collect intro + sections (ignore headings inside fenced code blocks)
    intro_lines: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current_heading: str | None = None
    current_lines: list[str] = []
    in_code = False

    def flush_section():
        nonlocal current_heading, current_lines
        if current_heading is not None:
            sections.append((current_heading, current_lines))
        current_heading = None
        current_lines = []

    for line in after_h1:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code

        if (not in_code) and line.startswith('## '):
            if current_heading is None:
                intro_lines = current_lines
            else:
                flush_section()
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_heading is None:
        intro_lines = current_lines
    else:
        flush_section()

    intro_text = ''.join(intro_lines).strip()
    if intro_text:
        intro_text = strip_goal_prefix(intro_text)

    buckets: dict[str, list[str]] = {k: [] for k in CANONICAL}

    if intro_text:
        buckets['Goal'].append(intro_text)

    for heading, content_lines in sections:
        main_content, sub_sections = split_subsections(content_lines)
        if main_content and not is_placeholder(main_content):
            target, inline = classify_heading(heading)
            if inline:
                block = main_content
            else:
                block = f"### {heading}\n\n{main_content}"
            buckets[target].append(block)

        for sub_heading, sub_content in sub_sections:
            if not sub_content or is_placeholder(sub_content):
                continue
            target, inline = classify_heading(sub_heading)
            if inline:
                block = sub_content
            else:
                block = f"### {sub_heading}\n\n{sub_content}"
            buckets[target].append(block)

    # Build normalized body
    out_lines = []
    out_lines.append(h1_line)
    out_lines.append('')

    for section in CANONICAL:
        content_blocks = [b.strip() for b in buckets[section] if b.strip()]
        if not content_blocks:
            continue
        out_lines.append(f"## {section}")
        out_lines.append('\n\n'.join(content_blocks))
        out_lines.append('')

    new_body = '\n'.join(out_lines).rstrip() + '\n'

    if fm_start is not None:
        new_text = ''.join(lines[:fm_end + 1]) + '\n' + new_body
    else:
        new_text = new_body

    if new_text == text:
        return False

    if dry_run:
        print(f'UPDATE: {path}')
        return True

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)

    if verbose:
        print(f'UPDATED: {path}')

    return True


def main():
    parser = argparse.ArgumentParser(description='Normalize algorithm notes to a consistent format.')
    parser.add_argument('--root', default='.', help='Root directory (default: current directory)')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without writing files')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    updated = 0
    skipped = 0

    for path in iter_algorithm_files(root):
        if normalize_file(path, args.dry_run, args.verbose):
            updated += 1
        else:
            skipped += 1

    print(f'updated={updated} skipped={skipped}')


if __name__ == '__main__':
    sys.exit(main())
