#!/usr/bin/env python3
"""Smoke test for archive gate pre_push_merge semantics.

This is intentionally dependency-free and runnable as:
  python3 .cursor/skills/nicki/scripts/smoke-archive-gate.py
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import yaml

from gates import gate_archive


def _write_status(worktree: Path, *, sync_rel: str) -> None:
    (worktree / "current-task").mkdir(parents=True, exist_ok=True)
    (worktree / "current-task" / "status.json").write_text(
        json.dumps(
            {
                "meta": {"schema": "task-status.v2"},
                "task": {"slug": worktree.name, "current_step": "sync", "next_step": "archive"},
                "scope": {"worktree_path": str(worktree)},
                "artifacts": {"sync": sync_rel},
                "open_questions": [],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_sync(worktree: Path, rel: str, *, ppm_status: str) -> None:
    path = worktree / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump({"pre_push_merge": {"status": ppm_status}}, sort_keys=False),
        encoding="utf-8",
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        worktree = Path(td) / "wt"
        worktree.mkdir(parents=True, exist_ok=True)

        sync_rel = "current-task/syncs/wt.yaml"
        _write_status(worktree, sync_rel=sync_rel)

        _write_sync(worktree, sync_rel, ppm_status="merged")
        assert gate_archive(json.loads((worktree / "current-task/status.json").read_text()), worktree, False, False) is None

        _write_sync(worktree, sync_rel, ppm_status="not_needed")
        assert gate_archive(json.loads((worktree / "current-task/status.json").read_text()), worktree, False, False) is None

        _write_sync(worktree, sync_rel, ppm_status="skipped")
        fail = gate_archive(json.loads((worktree / "current-task/status.json").read_text()), worktree, False, False)
        assert fail and fail["allowed"] is False

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

