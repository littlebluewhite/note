#!/usr/bin/env python3
"""Extract daily briefing candidates into inbox note.

Usage:
  python3 scripts/briefing_extract.py --root . --date today --out 10_inbox/briefing_candidates.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from vault_utils_v2 import dump_frontmatter, parse_frontmatter, today_str

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
H2_RE = re.compile(r"^##\s+(.+)$")
H3_RE = re.compile(r"^###\s+(.+)$")
STEM_DATE_RE = re.compile(r"^(\d{4}[-_]\d{2}[-_]\d{2})")

DOMAIN_RULES = [
    ("rust", "algorithm"),
    ("leetcode", "leetcode"),
    ("database", "database"),
    ("postgres", "database"),
    ("sql", "database"),
    ("android", "mobile"),
    ("ios", "mobile"),
    ("devops", "devops"),
    ("kubernetes", "devops"),
    ("security", "security"),
    ("ai", "ai"),
    ("agent", "ai"),
]


def infer_domain(text: str) -> str:
    low = text.lower()
    for key, domain in DOMAIN_RULES:
        if key in low:
            return domain
    return "general"


def pick_date(date_arg: str) -> str:
    if date_arg == "today":
        return today_str()
    return date_arg


def collect_candidates(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    _fm, body = parse_frontmatter(text)
    lines = body.splitlines()

    section = ""
    current_title = ""
    current_lines: list[str] = []
    out: list[dict[str, object]] = []

    def flush():
        nonlocal current_title, current_lines, section
        if not current_title:
            return
        joined = "\n".join(current_lines)
        sources = [{"label": m.group(1), "url": m.group(2)} for m in LINK_RE.finditer(joined)]
        out.append(
            {
                "title": current_title,
                "section": section,
                "summary": joined.strip()[:240],
                "sources": sources,
                "domain": infer_domain(section + " " + current_title + " " + joined),
                "origin": path,
            }
        )
        current_title = ""
        current_lines = []

    for line in lines:
        m2 = H2_RE.match(line)
        if m2:
            flush()
            section = m2.group(1).strip()
            continue

        m3 = H3_RE.match(line)
        if m3:
            flush()
            current_title = m3.group(1).strip()
            current_lines = []
            continue

        if current_title:
            current_lines.append(line)

    flush()
    return out


def build_output(date_str: str, candidates: list[dict[str, object]]) -> str:
    fm = {
        "title": f"briefing_candidates_{date_str}",
        "note_type": "inbox",
        "domain": "briefing_extract",
        "tags": ["inbox", "briefing", "candidates"],
        "created": date_str,
        "updated": date_str,
        "status": "active",
        "source": "briefing_extract",
        "date": date_str,
    }
    out = [
        dump_frontmatter(
            fm,
            ["title", "note_type", "domain", "tags", "created", "updated", "status", "source", "date"],
        )
    ]
    out.append(f"# Briefing Candidates - {date_str}\n")

    if not candidates:
        out.append("- No candidates found for this date.\n")
        return "\n".join(out)

    out.append("## Candidate Queue")
    for idx, item in enumerate(candidates, start=1):
        title = str(item["title"])
        section = str(item["section"])
        domain = str(item["domain"])
        origin = Path(item["origin"]).as_posix()
        summary_raw = str(item["summary"]).replace("\n", " ").strip()
        summary_plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", summary_raw)
        summary = summary_plain[:180].strip()
        out.append(f"### {idx}. {title}")
        out.append(f"- suggested_domain: `{domain}`")
        out.append(f"- section: `{section}`")
        out.append(f"- origin: `{origin}`")
        out.append(f"- summary: {summary}")

        srcs = item.get("sources") or []
        if srcs:
            out.append("- sources:")
            for src in srcs[:5]:
                out.append(f"  - [{src['label']}]({src['url']})")
        else:
            out.append("- sources: (none)")
        out.append("")

    out.append("## Action")
    out.append("- Convert high-value candidates into `40_knowledge/*` notes and add backlinks.")
    out.append("")

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract briefing candidates")
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default="today", help="YYYY-MM-DD or 'today'")
    parser.add_argument("--out", default="10_inbox/briefing_candidates.md")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    date_str = pick_date(args.date)

    briefing_root = root / "30_briefings"
    if not briefing_root.exists():
        print("candidates=0 (30_briefings not found)")
        return 0

    briefing_files = [p for p in sorted(briefing_root.rglob("*.md")) if p.name.lower() != "readme.md"]

    candidates: list[dict[str, object]] = []
    for p in briefing_files:
        if date_str in p.stem:
            candidates.extend(collect_candidates(p))

    if not candidates and briefing_files:
        dated: list[tuple[str, Path]] = []
        for p in briefing_files:
            m = STEM_DATE_RE.match(p.stem)
            if not m:
                continue
            dated.append((m.group(1).replace("_", "-"), p))

        if dated:
            fallback_date = sorted(dated, key=lambda x: x[0])[-1][0]
            for d, p in dated:
                if d == fallback_date:
                    candidates.extend(collect_candidates(p))
            if candidates:
                date_str = fallback_date
                print(f"fallback_date={fallback_date}")

    print(f"candidates={len(candidates)}")
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = root / out_path

    if args.dry_run:
        print(f"out={out_path.relative_to(root).as_posix()} (dry-run)")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_output(date_str, candidates), encoding="utf-8")
    print(f"out={out_path.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
