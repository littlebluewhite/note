#!/usr/bin/env python3
"""Refactor vault folders + markdown filenames to snake_case and fix internal links.

Usage:
  python3 scripts/refactor_to_snake_case.py --root . --map reports/rename_map.csv
  python3 scripts/refactor_to_snake_case.py --root . --apply --map reports/rename_map.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import uuid
from pathlib import Path

from vault_utils_v2 import (
    MD_LINK_RE,
    WIKI_LINK_RE,
    is_external_link,
    iter_markdown_files,
    normalize_briefing_stem,
    sanitize_slug,
)

FOLDER_MAP: list[tuple[str, str]] = [
    ("algorithm", "40_knowledge/algorithm"),
    ("data_structure", "40_knowledge/data_structure"),
    ("leetcode", "40_knowledge/leetcode"),
    ("database", "40_knowledge/database"),
    ("rust_book", "40_knowledge/rust"),
    ("Briefings", "30_briefings"),
    ("Templates", "00_system/templates"),
    ("Bases", "00_system/bases"),
    ("prompt", "00_system/prompts"),
    ("service", "50_projects/service"),
]

TARGET_ROOT_DIRS = [
    "00_system",
    "10_inbox",
    "20_daily",
    "30_briefings",
    "40_knowledge",
    "50_projects",
    "90_archive",
]


def remap_prefix(rel: Path) -> Path:
    rel_posix = rel.as_posix()
    for src, dst in FOLDER_MAP:
        if rel_posix == src:
            return Path(dst)
        if rel_posix.startswith(src + "/"):
            return Path(dst) / Path(rel_posix[len(src) + 1 :])
    return rel


def normalize_stem(mapped_rel: Path) -> str:
    stem = mapped_rel.stem
    top = mapped_rel.parts[0] if mapped_rel.parts else ""

    if top == "30_briefings":
        return normalize_briefing_stem(stem)

    if top in {"40_knowledge", "50_projects", "00_system", "20_daily", "10_inbox", "90_archive"}:
        return sanitize_slug(stem)

    return stem


def build_md_plan(root: Path) -> tuple[dict[str, str], dict[str, str]]:
    old_to_candidate: dict[str, str] = {}
    reason: dict[str, str] = {}

    for p in sorted(iter_markdown_files(root)):
        old_rel = p.relative_to(root).as_posix()
        mapped_rel = remap_prefix(Path(old_rel))
        new_stem = normalize_stem(mapped_rel)
        candidate_rel = mapped_rel.with_name(new_stem + ".md").as_posix()

        old_to_candidate[old_rel] = candidate_rel
        moved = old_rel != mapped_rel.as_posix()
        renamed = mapped_rel.stem != new_stem
        if moved and renamed:
            reason[old_rel] = "move+rename"
        elif moved:
            reason[old_rel] = "move"
        elif renamed:
            reason[old_rel] = "rename"
        else:
            reason[old_rel] = "unchanged"

    # Resolve collisions after renaming
    used: set[str] = set()
    old_to_new: dict[str, str] = {}
    for old_rel in sorted(old_to_candidate.keys()):
        candidate = old_to_candidate[old_rel]
        if candidate not in used:
            used.add(candidate)
            old_to_new[old_rel] = candidate
            continue

        path = Path(candidate)
        idx = 2
        while True:
            alt = path.with_name(f"{path.stem}_{idx}{path.suffix}").as_posix()
            if alt not in used:
                used.add(alt)
                old_to_new[old_rel] = alt
                if reason[old_rel] == "unchanged":
                    reason[old_rel] = "rename"
                else:
                    reason[old_rel] += "+collision"
                break
            idx += 1

    return old_to_new, reason


def move_dir_merge(src: Path, dst: Path):
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.move(str(src), str(dst))
        return

    for child in sorted(src.iterdir(), key=lambda p: (not p.is_dir(), p.name)):
        target = dst / child.name
        if child.is_dir() and target.exists() and target.is_dir():
            move_dir_merge(child, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(child), str(target))
    src.rmdir()


def apply_directory_moves(root: Path):
    for d in TARGET_ROOT_DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    for src, dst in FOLDER_MAP:
        s = root / src
        d = root / dst
        if s.exists():
            move_dir_merge(s, d)


def apply_md_renames(root: Path, old_to_new: dict[str, str]):
    renames: list[tuple[Path, Path]] = []
    for old_rel, new_rel in old_to_new.items():
        mapped_rel = remap_prefix(Path(old_rel)).as_posix()
        src = root / mapped_rel
        dst = root / new_rel
        if src.resolve() != dst.resolve():
            renames.append((src, dst))

    temp_moves: list[tuple[Path, Path]] = []
    for src, dst in renames:
        if not src.exists():
            continue
        tmp = src.with_name(src.name + f".tmp_{uuid.uuid4().hex[:8]}")
        src.rename(tmp)
        temp_moves.append((tmp, dst))

    for tmp, dst in temp_moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            dst = dst.with_name(dst.stem + "_migrated" + dst.suffix)
        tmp.rename(dst)


def build_stem_map(old_to_new: dict[str, str]) -> dict[str, str | None]:
    stem_to_news: dict[str, set[str]] = {}
    for old_rel, new_rel in old_to_new.items():
        old_stem = Path(old_rel).stem
        new_stem = Path(new_rel).stem
        stem_to_news.setdefault(old_stem.lower(), set()).add(new_stem)

    out: dict[str, str | None] = {}
    for k, values in stem_to_news.items():
        if len(values) == 1:
            out[k] = next(iter(values))
        else:
            out[k] = None
    return out


def rewrite_links(root: Path, old_to_new: dict[str, str]):
    new_to_old = {v: k for k, v in old_to_new.items()}
    stem_map = build_stem_map(old_to_new)

    for p in iter_markdown_files(root):
        rel_new = p.relative_to(root).as_posix()
        old_source_rel = new_to_old.get(rel_new, rel_new)

        text = p.read_text(encoding="utf-8", errors="ignore")
        changed = False

        def repl_md(m: re.Match[str]) -> str:
            nonlocal changed
            raw = m.group(1).strip()
            if not raw or raw.startswith("#") or is_external_link(raw):
                return m.group(0)

            target = raw
            anchor = ""
            if "#" in raw:
                target, anchor = raw.split("#", 1)
                anchor = "#" + anchor

            old_src_parent = (root / old_source_rel).parent
            old_target_abs = (old_src_parent / target).resolve()
            try:
                old_target_rel = old_target_abs.relative_to(root).as_posix()
            except ValueError:
                return m.group(0)

            if old_target_rel not in old_to_new:
                return m.group(0)

            new_target_rel = old_to_new[old_target_rel]
            rel_link = os.path.relpath(root / new_target_rel, p.parent).replace(os.sep, "/")
            if rel_link == ".":
                rel_link = Path(new_target_rel).name
            changed = True
            return m.group(0).replace(m.group(1), rel_link + anchor)

        text2 = MD_LINK_RE.sub(repl_md, text)

        def repl_wiki(m: re.Match[str]) -> str:
            nonlocal changed
            content = m.group(1)

            alias = ""
            main = content
            if "|" in content:
                main, alias = content.split("|", 1)

            heading = ""
            target = main.strip()
            if "#" in target:
                target, heading = target.split("#", 1)
                heading = "#" + heading

            repl_target = target

            if "/" in target or target.endswith(".md"):
                cand = target if target.endswith(".md") else target + ".md"
                if cand in old_to_new:
                    new_rel = old_to_new[cand]
                    repl_target = new_rel[:-3] if not target.endswith(".md") else new_rel
            else:
                mapped = stem_map.get(target.lower())
                if mapped:
                    repl_target = mapped

            if repl_target == target:
                return m.group(0)

            changed = True
            rebuilt = repl_target + heading
            if alias:
                rebuilt += "|" + alias
            return "[[" + rebuilt + "]]"

        text3 = WIKI_LINK_RE.sub(repl_wiki, text2)

        if changed and text3 != text:
            p.write_text(text3, encoding="utf-8")


def write_csv_map(root: Path, map_path: Path, old_to_new: dict[str, str], reason: dict[str, str]):
    map_path.parent.mkdir(parents=True, exist_ok=True)
    with map_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["old_path", "new_path", "change_type"])
        for old_rel in sorted(old_to_new.keys()):
            writer.writerow([old_rel, old_to_new[old_rel], reason.get(old_rel, "")])


def main() -> int:
    parser = argparse.ArgumentParser(description="Refactor folders + snake_case markdown filenames.")
    parser.add_argument("--root", default=".", help="Vault root")
    parser.add_argument("--apply", action="store_true", help="Apply refactor changes")
    parser.add_argument("--map", dest="map_path", default="reports/rename_map.csv", help="CSV path for planned/applied mapping")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    old_to_new, reason = build_md_plan(root)

    write_csv_map(root, (root / args.map_path).resolve(), old_to_new, reason)

    if not args.apply:
        changed = sum(1 for o, n in old_to_new.items() if o != n)
        print(f"planned_changes={changed}")
        print(f"map={args.map_path}")
        return 0

    apply_directory_moves(root)
    apply_md_renames(root, old_to_new)
    rewrite_links(root, old_to_new)

    changed = sum(1 for o, n in old_to_new.items() if o != n)
    print(f"applied_changes={changed}")
    print(f"map={args.map_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
