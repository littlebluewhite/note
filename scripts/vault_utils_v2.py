#!/usr/bin/env python3
"""Shared utilities for vault v2 maintenance scripts."""

from __future__ import annotations

import datetime as dt
import os
import re
from pathlib import Path
from typing import Iterable

SKIP_DIRS = {".git", ".obsidian", ".idea", ".serena", "__pycache__", ".pytest_cache"}
FRONTMATTER_DELIM = "---"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:[_\-](.+))?$")

MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def iter_markdown_files(root: Path, extra_skip_dirs: set[str] | None = None) -> Iterable[Path]:
    skip = set(SKIP_DIRS)
    if extra_skip_dirs:
        skip |= extra_skip_dirs
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in filenames:
            if name.lower().endswith(".md"):
                yield Path(dirpath) / name


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
    if len(v) >= 2 and ((v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'")):
        return v[1:-1]
    return v


def parse_inline_list(value: str) -> list[str]:
    raw = value.strip()
    if not (raw.startswith("[") and raw.endswith("]")):
        return []
    inner = raw[1:-1].strip()
    if not inner:
        return []
    items: list[str] = []
    for part in inner.split(","):
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
        if ":" not in line:
            i += 1
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if not key:
            i += 1
            continue

        if raw == "":
            j = i + 1
            items: list[str] = []
            while j < len(lines) and lines[j].startswith("  - "):
                item = strip_quotes(lines[j][4:].strip())
                if item:
                    items.append(item)
                j += 1
            if items:
                data[key] = items
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


def format_list_inline(items: list[str]) -> str:
    escaped = [x.replace('"', '\\"') for x in items]
    return "[" + ", ".join(escaped) + "]"


def dump_frontmatter(data: dict[str, str | list[str]], order: list[str] | None = None) -> str:
    keys = order[:] if order else list(data.keys())
    for k in data.keys():
        if k not in keys:
            keys.append(k)

    lines = [FRONTMATTER_DELIM]
    for key in keys:
        if key not in data:
            continue
        val = data[key]
        if isinstance(val, list):
            lines.append(f"{key}: {format_list_inline([str(x) for x in val])}")
            continue
        sval = "" if val is None else str(val)
        if sval == "":
            lines.append(f"{key}:")
        elif re.search(r"[:#\[\]{}]|^\s|\s$", sval):
            escaped = sval.replace('"', '\\"')
            lines.append(f'{key}: "{escaped}"')
        else:
            lines.append(f"{key}: {sval}")

    lines.append(FRONTMATTER_DELIM)
    lines.append("")
    return "\n".join(lines)


def format_date(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def today_str() -> str:
    return dt.date.today().strftime("%Y-%m-%d")


def valid_date(value: str | None) -> bool:
    return bool(value and DATE_RE.match(value.strip()))


def sanitize_slug(text: str) -> str:
    value = text.strip().lower()
    value = re.sub(r"\.md$", "", value)
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "note"


def normalize_briefing_stem(stem: str) -> str:
    m2 = re.match(r"^(\d{4})_(\d{2})_(\d{2})(?:[_\-](.+))?$", stem)
    if m2:
        date = f"{m2.group(1)}-{m2.group(2)}-{m2.group(3)}"
        suffix = sanitize_slug(m2.group(4) or "briefing")
        return f"{date}_{suffix}" if suffix else date

    m = DATE_PREFIX_RE.match(stem)
    if not m:
        return sanitize_slug(stem)
    date = m.group(1)
    suffix = sanitize_slug(m.group(2) or "briefing")
    return f"{date}_{suffix}" if suffix else date


def is_external_link(target: str) -> bool:
    return target.startswith("http://") or target.startswith("https://") or target.startswith("mailto:")


def classify_note(rel_path: Path) -> tuple[str, str]:
    parts = rel_path.parts
    top = parts[0] if parts else ""

    if top == "40_knowledge":
        domain = parts[1] if len(parts) > 1 else "knowledge"
        return "knowledge", domain
    if top == "30_briefings":
        domain = parts[1].lower() if len(parts) > 1 else "briefings"
        return "briefing", domain
    if top == "20_daily":
        return "daily", "daily"
    if top == "50_projects":
        domain = parts[1] if len(parts) > 1 else "projects"
        return "project", domain
    if top == "00_system":
        return "system", "system"
    if top == "10_inbox":
        return "inbox", "inbox"
    if top == "90_archive":
        return "archive", "archive"

    # fallback for legacy/root notes
    return "system", top or "root"


def snake_case_stem_ok(stem: str, allow_date_prefix: bool = False) -> bool:
    if allow_date_prefix:
        m = DATE_PREFIX_RE.match(stem)
        if m:
            suffix = m.group(2)
            return suffix is None or bool(re.match(r"^[a-z0-9]+(?:_[a-z0-9]+)*$", suffix))
    return bool(re.match(r"^[a-z0-9]+(?:_[a-z0-9]+)*$", stem))
