#!/usr/bin/env python3
"""Rebuild vault indexes and base view files.

Usage:
  python3 scripts/rebuild_indexes.py --root . --write
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from vault_utils_v2 import dump_frontmatter, iter_markdown_files, parse_frontmatter, parse_frontmatter_map, today_str


def rel_link(from_file: Path, to_file: Path) -> str:
    return Path(".") / Path(to_file.relative_to(from_file.parent))


def make_index(root: Path) -> str:
    notes = sorted(iter_markdown_files(root))
    by_domain: dict[str, list[Path]] = defaultdict(list)
    briefings: list[Path] = []
    projects: list[Path] = []

    for p in notes:
        rel = p.relative_to(root)
        if rel.as_posix() in {"INDEX.md", "Property Dictionary.md"}:
            continue
        if rel.parts[0] == "40_knowledge" and p.name.lower() != "readme.md":
            domain = rel.parts[1] if len(rel.parts) > 1 else "knowledge"
            by_domain[domain].append(p)
        elif rel.parts[0] == "30_briefings" and p.name.lower() != "readme.md":
            briefings.append(p)
        elif rel.parts[0] == "50_projects" and p.name.lower() != "readme.md":
            projects.append(p)

    fm = {
        "title": "Vault Index",
        "note_type": "system",
        "domain": "system",
        "tags": ["system", "index"],
        "created": today_str(),
        "updated": today_str(),
        "status": "active",
        "source": "system",
    }
    out = [dump_frontmatter(fm, ["title", "note_type", "domain", "tags", "created", "updated", "status", "source"])]
    out.append("# Vault Index\n")

    out.append("## System")
    out.append("- [Property Dictionary](Property Dictionary.md)")
    out.append("- [Daily Workflow](00_system/runbooks/daily_workflow.md)")
    out.append("- [Templates](00_system/templates/system.md)")
    out.append("- [Knowledge README](40_knowledge/README.md)")
    out.append("- [Briefings README](30_briefings/README.md)")
    out.append("")

    out.append("## Knowledge")
    for domain in sorted(by_domain.keys()):
        out.append(f"### {domain}")
        for p in sorted(by_domain[domain]):
            rel = p.relative_to(root).as_posix()
            title = p.stem
            out.append(f"- [{title}]({rel})")
        out.append("")

    out.append("## Briefings")
    for p in sorted(briefings, reverse=True)[:40]:
        rel = p.relative_to(root).as_posix()
        out.append(f"- [{p.stem}]({rel})")
    out.append("")

    out.append("## Projects")
    for p in sorted(projects):
        rel = p.relative_to(root).as_posix()
        out.append(f"- [{p.stem}]({rel})")
    out.append("")

    return "\n".join(out).rstrip() + "\n"


def make_knowledge_readme(root: Path) -> str:
    notes = sorted((root / "40_knowledge").rglob("*.md")) if (root / "40_knowledge").exists() else []
    by_domain: dict[str, list[Path]] = defaultdict(list)
    for p in notes:
        rel = p.relative_to(root)
        if p.name.lower() == "readme.md":
            continue
        domain = rel.parts[1] if len(rel.parts) > 1 else "knowledge"
        by_domain[domain].append(p)

    fm = {
        "title": "Knowledge README",
        "note_type": "system",
        "domain": "knowledge",
        "tags": ["system", "knowledge"],
        "created": today_str(),
        "updated": today_str(),
        "status": "active",
        "source": "system",
    }
    out = [dump_frontmatter(fm, ["title", "note_type", "domain", "tags", "created", "updated", "status", "source"])]
    out.append("# Knowledge\n")

    for domain in sorted(by_domain.keys()):
        out.append(f"## {domain}")
        for p in sorted(by_domain[domain]):
            rel = p.relative_to(root / "40_knowledge").as_posix()
            out.append(f"- [{p.stem}]({rel})")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def make_briefings_readme(root: Path) -> str:
    notes = sorted((root / "30_briefings").rglob("*.md")) if (root / "30_briefings").exists() else []
    by_topic: dict[str, list[Path]] = defaultdict(list)
    for p in notes:
        rel = p.relative_to(root)
        if p.name.lower() == "readme.md":
            continue
        topic = rel.parts[1] if len(rel.parts) > 1 else "general"
        by_topic[topic].append(p)

    fm = {
        "title": "Briefings README",
        "note_type": "system",
        "domain": "briefings",
        "tags": ["system", "briefings"],
        "created": today_str(),
        "updated": today_str(),
        "status": "active",
        "source": "system",
    }
    out = [dump_frontmatter(fm, ["title", "note_type", "domain", "tags", "created", "updated", "status", "source"])]
    out.append("# Briefings\n")

    for topic in sorted(by_topic.keys()):
        out.append(f"## {topic}")
        for p in sorted(by_topic[topic], reverse=True):
            rel = p.relative_to(root / "30_briefings").as_posix()
            out.append(f"- [{p.stem}]({rel})")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def make_bases() -> dict[str, str]:
    bases: dict[str, str] = {}

    bases["all_notes.base"] = """filters:
  and:
    - file.ext == \"md\"
properties:
  file.name:
    displayName: File
  title:
    displayName: Title
  note_type:
    displayName: Type
  domain:
    displayName: Domain
  status:
    displayName: Status
  tags:
    displayName: Tags
  date:
    displayName: Date
  next_review:
    displayName: Next Review
  review_interval_days:
    displayName: Review Days
  complexity_time:
    displayName: Time
  complexity_space:
    displayName: Space
  created:
    displayName: Created
  updated:
    displayName: Updated
  source:
    displayName: Source
  canonical:
    displayName: Canonical
views:
  - type: table
    name: All Notes
    order:
      - file.name
      - title
      - note_type
      - domain
      - status
      - tags
      - date
      - next_review
      - review_interval_days
      - complexity_time
      - complexity_space
      - updated
      - source
"""
    bases["all_notes_dashboard.base"] = bases["all_notes.base"]

    bases["algorithm_topics.base"] = """filters:
  and:
    - file.inFolder(\"40_knowledge/algorithm\")
    - file.ext == \"md\"
properties:
  file.name:
    displayName: File
  note_type:
    displayName: Type
  title:
    displayName: Title
  tags:
    displayName: Tags
  complexity_time:
    displayName: Time
  complexity_space:
    displayName: Space
  review_interval_days:
    displayName: Review
  next_review:
    displayName: Next
  status:
    displayName: Status
  updated:
    displayName: Updated
views:
  - type: table
    name: Algorithm Topics
    order:
      - file.name
      - note_type
      - title
      - complexity_time
      - complexity_space
      - tags
      - next_review
      - review_interval_days
      - status
      - updated
"""

    bases["data_structure_topics.base"] = """filters:
  and:
    - file.inFolder(\"40_knowledge/data_structure\")
    - file.ext == \"md\"
properties:
  file.name:
    displayName: File
  note_type:
    displayName: Type
  title:
    displayName: Title
  tags:
    displayName: Tags
  complexity_time:
    displayName: Time
  complexity_space:
    displayName: Space
  review_interval_days:
    displayName: Review
  next_review:
    displayName: Next
  status:
    displayName: Status
  updated:
    displayName: Updated
views:
  - type: table
    name: Data Structure Topics
    order:
      - file.name
      - note_type
      - title
      - complexity_time
      - complexity_space
      - tags
      - next_review
      - review_interval_days
      - status
      - updated
"""

    bases["leetcode_topics.base"] = """filters:
  and:
    - file.inFolder(\"40_knowledge/leetcode\")
    - file.ext == \"md\"
properties:
  file.name:
    displayName: File
  note_type:
    displayName: Type
  title:
    displayName: Title
  tags:
    displayName: Tags
  complexity_time:
    displayName: Time
  complexity_space:
    displayName: Space
  review_interval_days:
    displayName: Review
  next_review:
    displayName: Next
  status:
    displayName: Status
  updated:
    displayName: Updated
views:
  - type: table
    name: LeetCode Topics
    order:
      - file.name
      - note_type
      - title
      - complexity_time
      - complexity_space
      - tags
      - next_review
      - review_interval_days
      - status
      - updated
"""

    bases["database_topics.base"] = """filters:
  and:
    - file.inFolder(\"40_knowledge/database\")
    - file.ext == \"md\"
properties:
  file.name:
    displayName: File
  note_type:
    displayName: Type
  title:
    displayName: Title
  tags:
    displayName: Tags
  status:
    displayName: Status
  updated:
    displayName: Updated
  source:
    displayName: Source
views:
  - type: table
    name: Database Topics
    order:
      - file.name
      - note_type
      - title
      - tags
      - source
      - status
      - updated
"""

    bases["rust_topics.base"] = """filters:
  and:
    - file.inFolder(\"40_knowledge/rust\")
    - file.ext == \"md\"
properties:
  file.name:
    displayName: File
  note_type:
    displayName: Type
  title:
    displayName: Title
  tags:
    displayName: Tags
  status:
    displayName: Status
  updated:
    displayName: Updated
views:
  - type: table
    name: Rust Topics
    order:
      - file.name
      - note_type
      - title
      - tags
      - status
      - updated
"""

    bases["programming_briefings.base"] = """filters:
  and:
    - file.inFolder(\"30_briefings/programming\")
    - file.ext == \"md\"
properties:
  file.name:
    displayName: File
  note_type:
    displayName: Type
  title:
    displayName: Title
  date:
    displayName: Date
  tags:
    displayName: Tags
  status:
    displayName: Status
  updated:
    displayName: Updated
views:
  - type: table
    name: Programming Briefings
    order:
      - file.name
      - note_type
      - date
      - title
      - tags
      - status
      - updated
"""

    bases["news_briefings.base"] = """filters:
  and:
    - file.inFolder(\"30_briefings/news\")
    - file.ext == \"md\"
properties:
  file.name:
    displayName: File
  note_type:
    displayName: Type
  title:
    displayName: Title
  date:
    displayName: Date
  tags:
    displayName: Tags
  status:
    displayName: Status
  updated:
    displayName: Updated
views:
  - type: table
    name: News Briefings
    order:
      - file.name
      - note_type
      - date
      - title
      - tags
      - status
      - updated
"""

    bases["inbox_candidates.base"] = """filters:
  and:
    - file.inFolder(\"10_inbox\")
    - file.ext == \"md\"
properties:
  file.name:
    displayName: File
  note_type:
    displayName: Type
  title:
    displayName: Title
  date:
    displayName: Date
  status:
    displayName: Status
  updated:
    displayName: Updated
views:
  - type: table
    name: Inbox Candidates
    order:
      - file.name
      - note_type
      - title
      - date
      - status
      - updated
"""

    bases["projects_service.base"] = """filters:
  and:
    - file.inFolder(\"50_projects/service\")
    - file.ext == \"md\"
properties:
  file.name:
    displayName: File
  note_type:
    displayName: Type
  title:
    displayName: Title
  status:
    displayName: Status
  updated:
    displayName: Updated
  canonical:
    displayName: Canonical
views:
  - type: table
    name: Service Project
    order:
      - file.name
      - note_type
      - title
      - status
      - canonical
      - updated
"""

    bases["review_queue.base"] = """filters:
  and:
    - file.inFolder(\"40_knowledge\")
    - file.ext == \"md\"
properties:
  file.name:
    displayName: File
  note_type:
    displayName: Type
  title:
    displayName: Title
  domain:
    displayName: Domain
  next_review:
    displayName: Next Review
  review_interval_days:
    displayName: Interval
  status:
    displayName: Status
  updated:
    displayName: Updated
views:
  - type: table
    name: Review Queue
    order:
      - file.name
      - note_type
      - domain
      - title
      - next_review
      - review_interval_days
      - status
      - updated
"""

    return bases


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild vault indexes and base files")
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    index_text = make_index(root)
    knowledge_readme = make_knowledge_readme(root)
    briefings_readme = make_briefings_readme(root)

    outputs = {
        root / "INDEX.md": index_text,
        root / "40_knowledge/README.md": knowledge_readme,
        root / "30_briefings/README.md": briefings_readme,
    }

    base_defs = make_bases()
    for name, content in base_defs.items():
        outputs[root / "00_system/bases" / name] = content.rstrip() + "\n"

    changed = 0
    for path, content in outputs.items():
        old = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else None
        if old == content:
            continue
        changed += 1
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    # Remove legacy base files not managed by v2.
    legacy_deleted = 0
    base_dir = root / "00_system/bases"
    if args.write and base_dir.exists():
        keep = set(base_defs.keys())
        for p in base_dir.glob("*.base"):
            if p.name not in keep:
                p.unlink()
                legacy_deleted += 1

    print(f"files={len(outputs)} changed={changed} legacy_deleted={legacy_deleted} write={args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
