from __future__ import annotations

import subprocess
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def test_briefing_extract_output(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    bdir = vault / "30_briefings" / "programming"
    bdir.mkdir(parents=True)

    briefing = bdir / "2026-02-07_programming_briefing.md"
    briefing.write_text(
        """---
title: test
note_type: briefing
domain: programming
tags: [briefing]
created: 2026-02-07
updated: 2026-02-07
status: active
source: briefing
date: 2026-02-07
---
# 2026-02-07
## AI
### Agent Compiler
Summary line.
Source: [HN](https://news.ycombinator.com)
""",
        encoding="utf-8",
    )

    out = vault / "10_inbox" / "briefing_candidates.md"
    cmd = [
        "python3",
        "/Users/wilson08/note/scripts/briefing_extract.py",
        "--root",
        str(vault),
        "--date",
        "2026-02-07",
        "--out",
        str(out),
    ]
    proc = run(cmd, cwd=vault)
    assert proc.returncode == 0
    assert out.exists()

    text = out.read_text(encoding="utf-8")
    assert "Agent Compiler" in text
    assert "news.ycombinator.com" in text
