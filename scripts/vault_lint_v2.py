#!/usr/bin/env python3
"""Vault lint v2: schema, links, orphan notes, snake_case, index coverage.

Usage:
  python3 scripts/vault_lint_v2.py --root .
  python3 scripts/vault_lint_v2.py --root . --json reports/vault_health.json
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from vault_utils_v2 import (
    MD_LINK_RE,
    WIKI_LINK_RE,
    classify_note,
    is_external_link,
    iter_markdown_files,
    parse_frontmatter,
    parse_frontmatter_map,
    sanitize_slug,
    snake_case_stem_ok,
)

REQUIRED_BASE = ["title", "note_type", "domain", "tags", "created", "updated", "status", "source"]
ALLOWED_NOTE_TYPES = {"knowledge", "briefing", "daily", "project", "system", "inbox", "archive"}


def should_skip_wiki_target(target: str) -> bool:
    if not target:
        return True
    if target.replace(" ", "").replace(",", "").isdigit():
        return True
    return False


def load_md_files(root: Path) -> list[Path]:
    return sorted(iter_markdown_files(root))


def link_issues(md_files: list[Path], root: Path) -> list[dict[str, str]]:
    md_set = {p.resolve() for p in md_files}
    by_name: dict[str, list[Path]] = {}
    for p in md_files:
        by_name.setdefault(p.name, []).append(p.resolve())

    out: list[dict[str, str]] = []

    for p in md_files:
        text = p.read_text(encoding="utf-8", errors="ignore")

        for m in MD_LINK_RE.finditer(text):
            target = m.group(1).strip()
            if not target or target.startswith("#") or is_external_link(target):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            tpath = (p.parent / target).resolve()
            if not tpath.exists():
                out.append({"file": p.relative_to(root).as_posix(), "target": target, "type": "markdown"})

        for m in WIKI_LINK_RE.finditer(text):
            target = m.group(1).strip()
            if "|" in target:
                target = target.split("|", 1)[0].strip()
            if "#" in target:
                target = target.split("#", 1)[0].strip()
            if should_skip_wiki_target(target):
                continue

            candidates: list[Path] = []
            if target.endswith(".md") or "/" in target:
                if not target.endswith(".md"):
                    target = target + ".md"
                candidates.append((root / target).resolve())
            else:
                candidates.extend(by_name.get(target + ".md", []))
                candidates.append((root / (target + ".md")).resolve())

            if not any(c in md_set for c in candidates):
                out.append({"file": p.relative_to(root).as_posix(), "target": target, "type": "wiki"})

    return out


def index_coverage(md_files: list[Path], root: Path) -> dict[str, object]:
    index_path = root / "INDEX.md"
    if not index_path.exists():
        return {"indexed": 0, "total": 0, "percent": 0.0, "missing": []}

    text = index_path.read_text(encoding="utf-8", errors="ignore")
    links: set[str] = set()
    for m in MD_LINK_RE.finditer(text):
        target = m.group(1).split("#", 1)[0].strip()
        if not target.endswith(".md"):
            continue
        t = (index_path.parent / target).resolve()
        try:
            links.add(t.relative_to(root).as_posix())
        except ValueError:
            pass

    include: list[str] = []
    for p in md_files:
        rel = p.relative_to(root).as_posix()
        parts = p.relative_to(root).parts
        top = parts[0] if parts else ""
        if rel in {"INDEX.md", "Property Dictionary.md"}:
            continue
        if top in {"00_system", "10_inbox", "20_daily", "90_archive"}:
            continue
        if p.name.lower() == "readme.md":
            continue
        include.append(rel)

    indexed = sum(1 for rel in include if rel in links)
    missing = sorted([rel for rel in include if rel not in links])
    percent = round((indexed / len(include) * 100.0), 2) if include else 100.0
    return {"indexed": indexed, "total": len(include), "percent": percent, "missing": missing}


def non_snake_case(md_files: list[Path], root: Path) -> list[str]:
    out: list[str] = []
    for p in md_files:
        rel = p.relative_to(root)
        name = p.stem

        # Briefing accepts YYYY-MM-DD_suffix
        allow_date = rel.parts and rel.parts[0] == "30_briefings"

        # Ignore legacy root index/property names for now
        if rel.as_posix() in {"INDEX.md", "Property Dictionary.md"}:
            continue

        if not snake_case_stem_ok(name, allow_date_prefix=allow_date):
            # exclude readmes in system folder from strict snake_case
            if p.name.lower() == "readme.md":
                continue
            out.append(rel.as_posix())
    return sorted(out)


def orphan_notes(md_files: list[Path], root: Path) -> list[str]:
    md_set = {p.resolve() for p in md_files}
    by_name: dict[str, list[Path]] = {}
    for p in md_files:
        by_name.setdefault(p.stem.lower(), []).append(p.resolve())

    inbound = {p.resolve(): 0 for p in md_files}

    for p in md_files:
        text = p.read_text(encoding="utf-8", errors="ignore")

        for m in MD_LINK_RE.finditer(text):
            target = m.group(1).strip()
            if not target or target.startswith("#") or is_external_link(target):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            tpath = (p.parent / target).resolve()
            if tpath in md_set:
                inbound[tpath] += 1

        for m in WIKI_LINK_RE.finditer(text):
            target = m.group(1).strip()
            if "|" in target:
                target = target.split("|", 1)[0].strip()
            if "#" in target:
                target = target.split("#", 1)[0].strip()
            if should_skip_wiki_target(target):
                continue

            if target.endswith(".md") or "/" in target:
                if not target.endswith(".md"):
                    target += ".md"
                t = (root / target).resolve()
                if t in md_set:
                    inbound[t] += 1
            else:
                for t in by_name.get(target.lower(), []):
                    inbound[t] += 1

    out: list[str] = []
    for p in md_files:
        rel = p.relative_to(root).as_posix()
        parts = p.relative_to(root).parts
        top = parts[0] if parts else ""

        if rel in {"INDEX.md", "Property Dictionary.md"}:
            continue
        if top in {"00_system", "10_inbox", "20_daily"}:
            continue
        if p.name.lower() == "readme.md":
            continue

        if inbound[p.resolve()] == 0:
            out.append(rel)

    return sorted(out)


def required_fields_for(note_type: str, domain: str) -> list[str]:
    req = list(REQUIRED_BASE)
    if note_type in {"daily", "briefing"}:
        req.append("date")
    if note_type == "knowledge" and domain in {"algorithm", "data_structure", "leetcode"}:
        req.extend(["complexity_time", "complexity_space", "review_interval_days", "next_review"])
    return req


def main() -> int:
    parser = argparse.ArgumentParser(description="Vault lint v2")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", dest="json_path", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    md_files = load_md_files(root)

    missing_frontmatter: list[str] = []
    missing_required_fields: list[dict[str, object]] = []

    for p in md_files:
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm_text, _body = parse_frontmatter(text)
        if fm_text is None:
            missing_frontmatter.append(rel)
            continue

        fm = parse_frontmatter_map(fm_text)

        note_type, domain_guess = classify_note(Path(rel))
        note_type_val = str(fm.get("note_type", note_type)).strip()
        domain_val = str(fm.get("domain", domain_guess)).strip()

        if note_type_val not in ALLOWED_NOTE_TYPES:
            missing_required_fields.append({"file": rel, "missing": ["note_type(valid allowed)"]})
            continue

        req = required_fields_for(note_type_val, domain_val)
        missing = [k for k in req if (k not in fm or str(fm.get(k, "")).strip() == "")]
        if missing:
            missing_required_fields.append({"file": rel, "missing": missing})

    broken = link_issues(md_files, root)
    orphan = orphan_notes(md_files, root)
    non_snake = non_snake_case(md_files, root)
    coverage = index_coverage(md_files, root)

    summary = {
        "md_files": len(md_files),
        "missing_frontmatter": len(missing_frontmatter),
        "missing_required_fields": len(missing_required_fields),
        "broken_links": len(broken),
        "orphan_notes": len(orphan),
        "non_snake_case": len(non_snake),
        "index_coverage_percent": coverage["percent"],
    }

    report = {
        "summary": summary,
        "missing_frontmatter": missing_frontmatter,
        "missing_required_fields": missing_required_fields,
        "broken_links": broken,
        "orphan_notes": orphan,
        "non_snake_case": non_snake,
        "index_coverage": coverage,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.json_path:
        out = Path(args.json_path)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"json={out.relative_to(root).as_posix()}")

    critical = summary["missing_frontmatter"] + summary["missing_required_fields"] + summary["broken_links"]
    return 1 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
