from __future__ import annotations

import json
import subprocess
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def test_vault_lint_v2_missing_required(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "40_knowledge/algorithm").mkdir(parents=True)

    note = vault / "40_knowledge/algorithm" / "sample.md"
    note.write_text(
        """---
title: sample
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-02-01
updated: 2026-02-01
status: active
source: test
---
# sample
""",
        encoding="utf-8",
    )

    report = vault / "reports" / "vault_health.json"
    cmd = ["python3", "/Users/wilson08/note/scripts/vault_lint_v2.py", "--root", str(vault), "--json", str(report)]
    proc = run(cmd, cwd=vault)

    assert proc.returncode == 1
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["summary"]["missing_required_fields"] >= 1
    missing = data["missing_required_fields"][0]["missing"]
    assert "complexity_time" in missing
    assert "next_review" in missing
