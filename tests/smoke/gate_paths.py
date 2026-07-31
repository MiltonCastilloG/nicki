"""Artifact path scope: every pointer (including archive) is worktree-relative.

Consent on `integrate` is no longer asserted here — it left the gate for
`routing.json`, and `gates_matrix.POLICY_CASES` covers it for every step at once.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from tests.smoke._helpers import json_line, run_py, script

SLUG = "gate-paths"
ARCHIVE_REL = f"docs/archive/{SLUG}/report.json"
SYNC_REL = f"current-task/syncs/{SLUG}.json"


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _fixture(
    tmp: Path,
    *,
    archive_in_worktree: bool,
    archive_at_workspace: bool = False,
    sync_at_workspace: bool = False,
) -> tuple[Path, Path]:
    workspace = tmp / "workspace"
    worktree = workspace / "worktrees" / SLUG
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
            "artifacts": {"sync": SYNC_REL, "archive": ARCHIVE_REL},
            "open_questions": [],
        },
    )
    sync_base = workspace if sync_at_workspace else worktree
    _write(sync_base / SYNC_REL, {"pre_push_merge": {"status": "merged"}})
    if archive_in_worktree:
        _write(worktree / ARCHIVE_REL, {"task": SLUG})
    if archive_at_workspace:
        _write(workspace / ARCHIVE_REL, {"task": SLUG})
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
    if not proc.stdout.strip():
        raise AssertionError(f"fail: empty gate stdout (stderr: {proc.stderr})")
    return json_line(proc.stdout)


def _expect_allow(result: dict, label: str) -> None:
    if result.get("allowed") is not True:
        raise AssertionError(f"fail: {label} should allow, got {result}")
    print(f"ok: {label}")


def _expect_deny(result: dict, needle: str, label: str) -> None:
    if result.get("allowed") is not False or needle not in (result.get("reason") or ""):
        raise AssertionError(f"fail: {label} should deny with {needle!r}, got {result}")
    print(f"ok: {label}")


def run(root: Path) -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        ws, wt = _fixture(tmp / "a", archive_in_worktree=True)
        _expect_allow(
            _gate(root, ws, wt, "--user-confirmed"),
            "archive in worktree resolves",
        )

        ws, wt = _fixture(tmp / "b", archive_in_worktree=False)
        _expect_deny(
            _gate(root, ws, wt, "--user-confirmed"),
            "archive artifact missing",
            "archive genuinely absent still denies",
        )

        ws, wt = _fixture(
            tmp / "c", archive_in_worktree=False, archive_at_workspace=True
        )
        _expect_deny(
            _gate(root, ws, wt, "--user-confirmed"),
            "archive artifact missing",
            "archive at Nicki workspace root is not accepted",
        )

        ws, wt = _fixture(
            tmp / "d", archive_in_worktree=True, sync_at_workspace=True
        )
        _expect_deny(
            _gate(root, ws, wt, "--user-confirmed"),
            "sync artifact missing",
            "worktree-scoped sync is not read from workspace root",
        )

    print("smoke-gate-paths: ok")
