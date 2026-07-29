"""Artifact path scope: archive is workspace-root-relative, the rest worktree-relative.

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
    archive_at_root: bool,
    archive_in_worktree: bool = False,
    sync_at_root: bool = False,
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
    sync_base = workspace if sync_at_root else worktree
    _write(sync_base / SYNC_REL, {"pre_push_merge": {"status": "merged"}})
    if archive_at_root:
        _write(workspace / ARCHIVE_REL, {"task": SLUG})
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

        ws, wt = _fixture(tmp / "a", archive_at_root=True)
        _expect_allow(
            _gate(root, ws, wt, "--user-confirmed"),
            "archive at workspace root resolves",
        )

        ws, wt = _fixture(tmp / "b", archive_at_root=False)
        _expect_deny(
            _gate(root, ws, wt, "--user-confirmed"),
            "archive artifact missing",
            "archive genuinely absent still denies",
        )

        ws, wt = _fixture(tmp / "c", archive_at_root=False, archive_in_worktree=True)
        _expect_deny(
            _gate(root, ws, wt, "--user-confirmed"),
            "archive artifact missing",
            "archive under worktree is not accepted",
        )

        ws, wt = _fixture(tmp / "d", archive_at_root=True, sync_at_root=True)
        _expect_deny(
            _gate(root, ws, wt, "--user-confirmed"),
            "sync artifact missing",
            "worktree-scoped sync is not read from workspace root",
        )

    print("smoke-gate-paths: ok")
