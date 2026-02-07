from __future__ import annotations

import subprocess
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def test_refactor_renames_and_rewrites_links(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "algorithm").mkdir()

    target = vault / "algorithm" / "My Fancy Note.md"
    target.write_text("# My Fancy Note\n", encoding="utf-8")

    source = vault / "README.md"
    source.write_text("[go](algorithm/My Fancy Note.md)\n", encoding="utf-8")

    cmd = [
        "python3",
        "/Users/wilson08/note/scripts/refactor_to_snake_case.py",
        "--root",
        str(vault),
        "--apply",
        "--map",
        "reports/rename_map.csv",
    ]
    proc = run(cmd, cwd=vault)
    assert proc.returncode == 0

    new_target = vault / "40_knowledge" / "algorithm" / "my_fancy_note.md"
    assert new_target.exists()

    rewritten = source.read_text(encoding="utf-8")
    assert "40_knowledge/algorithm/my_fancy_note.md" in rewritten
