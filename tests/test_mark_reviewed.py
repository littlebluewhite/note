from __future__ import annotations

import sys
from pathlib import Path

# Make scripts importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from mark_reviewed import compute_next_interval, find_due_notes, update_note


def test_good_quality_interval():
    assert compute_next_interval(14, "good") == 21


def test_easy_quality_interval():
    assert compute_next_interval(14, "easy") == 35


def test_hard_quality_interval():
    assert compute_next_interval(14, "hard") == 7


def test_clamp_max_interval():
    assert compute_next_interval(100, "easy") == 180


def test_clamp_min_interval():
    assert compute_next_interval(1, "hard") == 1


def _make_note(tmp_path: Path, next_review: str, interval: int = 14) -> Path:
    vault = tmp_path / "vault"
    (vault / "40_knowledge/algorithm").mkdir(parents=True, exist_ok=True)
    note = vault / "40_knowledge/algorithm/sample.md"
    note.write_text(
        f"""---
title: sample
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-01-01
updated: 2026-01-01
status: active
source: test
complexity_time: O(n)
complexity_space: O(1)
review_interval_days: {interval}
next_review: {next_review}
---
# sample

Content here.
""",
        encoding="utf-8",
    )
    return note


def test_due_today_finds_overdue(tmp_path: Path):
    _make_note(tmp_path, "2020-01-01")
    vault = tmp_path / "vault"
    due = find_due_notes(vault, "2026-02-09")
    assert len(due) == 1


def test_due_today_skips_future(tmp_path: Path):
    _make_note(tmp_path, "2099-01-01")
    vault = tmp_path / "vault"
    due = find_due_notes(vault, "2026-02-09")
    assert len(due) == 0


def test_dry_run_does_not_modify(tmp_path: Path):
    note = _make_note(tmp_path, "2020-01-01")
    original = note.read_text(encoding="utf-8")
    update_note(note, "good", "2026-02-09", write=False)
    assert note.read_text(encoding="utf-8") == original


def test_write_modifies_note(tmp_path: Path):
    note = _make_note(tmp_path, "2020-01-01", interval=14)
    update_note(note, "good", "2026-02-09", write=True)
    text = note.read_text(encoding="utf-8")
    assert "review_interval_days: 21" in text
    assert "updated: 2026-02-09" in text
    assert "next_review: 2020-01-01" not in text


def test_hard_quality_write(tmp_path: Path):
    note = _make_note(tmp_path, "2020-01-01", interval=14)
    update_note(note, "hard", "2026-02-09", write=True)
    text = note.read_text(encoding="utf-8")
    assert "review_interval_days: 7" in text


def test_skip_note_without_interval(tmp_path: Path):
    vault = tmp_path / "vault"
    (vault / "40_knowledge/algorithm").mkdir(parents=True, exist_ok=True)
    note = vault / "40_knowledge/algorithm/no_interval.md"
    note.write_text(
        """---
title: no interval
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-01-01
updated: 2026-01-01
status: active
source: test
---
# no interval
""",
        encoding="utf-8",
    )
    result = update_note(note, "good", "2026-02-09", write=True)
    assert result["status"] == "skip"
