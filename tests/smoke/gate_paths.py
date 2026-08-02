"""Integrate/sync gates are consent-only; archive path scope is document-only."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from tests.smoke._helpers import json_line, run_py, script

SLUG = "gate-paths"
ARCHIVE_REL = f"docs/archive/{SLUG}/report.json"


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _fixture(tmp: Path, *, archive_in_worktree: bool) -> tuple[Path, Path]:
    workspace = tmp / "workspace"
    worktree = workspace / "worktrees" / SLUG
    arts = {"archive": ARCHIVE_REL} if archive_in_worktree else {}
    _write(
        worktree / "current-task/status.json",
        {
            "meta": {"schema": "task-status.v2"},
            "task": {
                "slug": SLUG,
                "current_step": "archive",
                "next_step": "integrate",
            },
            "scope": {"worktree_path": str(worktree)},
            "artifacts": arts,
            "open_questions": [],
        },
    )
    if archive_in_worktree:
        _write(worktree / ARCHIVE_REL, {"task": SLUG})
    return workspace, worktree


def _gate(root: Path, workspace: Path, worktree: Path, *args: str) -> dict:
    proc = run_py(
        script(root, ".cursor/skills/nicki/scripts/check-gate.py"),
        "--worktree",
        str(worktree),
        "--step",
        "integrate",
        *args,
        env={**os.environ, "NICKI_WORKSPACE_ROOT": str(workspace)},
    )
    return json_line(proc.stdout)


def run(root: Path) -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        ws, wt = _fixture(tmp / "a", archive_in_worktree=True)
        got = _gate(root, ws, wt, "--user-confirmed")
        if got.get("allowed") is not True:
            raise AssertionError(f"fail: integrate with consent should allow: {got}")
        print("ok: integrate allows with consent (archive optional)")

        ws, wt = _fixture(tmp / "b", archive_in_worktree=False)
        got = _gate(root, ws, wt, "--user-confirmed")
        if got.get("allowed") is not True:
            raise AssertionError(f"fail: integrate without archive file should allow: {got}")
        print("ok: integrate does not require archive handoff")

        got = _gate(root, ws, wt)
        if got.get("allowed") is not False:
            raise AssertionError(f"fail: integrate without consent should deny: {got}")
        print("ok: integrate still needs consent")

    print("smoke-gate-paths: ok")
