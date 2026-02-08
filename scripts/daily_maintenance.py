#!/usr/bin/env python3
"""Run daily maintenance pipeline.

Pipeline:
  1) vault_lint_v2
  2) rebuild_indexes
  3) briefing_extract
  4) review_reminder (informational)
  5) vault_lint_v2 (final)

Usage:
  python3 scripts/daily_maintenance.py --root . --dry-run
  python3 scripts/daily_maintenance.py --root . --write
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Daily maintenance pipeline")
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.write and args.dry_run:
        print("Cannot use --write and --dry-run together")
        return 2

    root = Path(args.root).resolve()
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    py = sys.executable
    dry = args.dry_run or (not args.write)

    steps: list[dict[str, object]] = []

    lint_before_json = reports / "vault_health_before.json"
    code, out = run([py, "scripts/vault_lint_v2.py", "--root", ".", "--json", str(lint_before_json)], root)
    steps.append({"step": "lint_before", "code": code, "output": out})

    rebuild_cmd = [py, "scripts/rebuild_indexes.py", "--root", "."]
    if args.write:
        rebuild_cmd.append("--write")
    code, out = run(rebuild_cmd, root)
    steps.append({"step": "rebuild_indexes", "code": code, "output": out})

    extract_cmd = [
        py,
        "scripts/briefing_extract.py",
        "--root",
        ".",
        "--date",
        "today",
        "--out",
        "10_inbox/briefing_candidates.md",
    ]
    if dry:
        extract_cmd.append("--dry-run")
    code, out = run(extract_cmd, root)
    steps.append({"step": "briefing_extract", "code": code, "output": out})

    review_cmd = [py, "scripts/mark_reviewed.py", "--root", ".", "--due-today", "--dry-run"]
    code, out = run(review_cmd, root)
    steps.append({"step": "review_reminder", "code": 0, "output": out})

    lint_after_json = reports / "vault_health_after.json"
    code, out = run([py, "scripts/vault_lint_v2.py", "--root", ".", "--json", str(lint_after_json)], root)
    steps.append({"step": "lint_after", "code": code, "output": out})

    summary = {
        "mode": "write" if args.write else "dry-run",
        "steps": steps,
    }

    summary_path = reports / "daily_maintenance_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    for s in steps:
        print(f"[{s['step']}] code={s['code']}")
        if s["output"]:
            print(s["output"])

    print(f"summary={summary_path.relative_to(root).as_posix()}")

    if any(int(s["code"]) != 0 for s in steps):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
