"""bootstrap-context.py: contract JSON on readiness parse soft-fail (Finding 4)."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from tests.smoke._helpers import json_line, run_py, script

SLUG = "bootstrap-soft"
BROKEN = '{"readiness": {"status": "ready_for_acceptance"'


def _put(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = payload if isinstance(payload, str) else json.dumps(payload, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


def _fixture(base: Path, *, validation: object | None) -> tuple[Path, Path]:
    workspace = base / "workspace"
    worktree = workspace / "worktrees" / SLUG
    worktree.mkdir(parents=True)
    status_rel = "current-task/status.json"
    status = {
        "meta": {"schema": "task-status.v2"},
        "task": {
            "slug": SLUG,
            "original": "demo",
            "current_step": "review",
            "next_step": "acceptance",
            "completed_steps": ["review"],
        },
        "scope": {"worktree_path": str(worktree)},
        "artifacts": {},
        "open_questions": [],
    }
    if validation is not None:
        val_rel = "current-task/review-validations/r1-validation.json"
        status["artifacts"]["review_validation"] = val_rel
        _put(worktree / val_rel, validation)
    _put(worktree / status_rel, status)
    _put(
        workspace / "global-status.json",
        {
            "active_task": f"t-{SLUG}",
            "tasks": {
                f"t-{SLUG}": {
                    "worktree_path": str(worktree),
                    "status_path": status_rel,
                }
            },
        },
    )
    # nicki-workspace marker so gate_utils.workspace_root can find us via env
    _put(workspace / "nicki-workspace.example.yaml", {"name": "test"})
    (workspace / "worktrees").mkdir(exist_ok=True)
    return workspace, worktree


def _boot(root: Path, workspace: Path, worktree: Path):
    boot = script(root, ".cursor/skills/nicki/scripts/bootstrap-context.py")
    return run_py(
        boot,
        "--worktree",
        str(worktree),
        env={**os.environ, "NICKI_WORKSPACE_ROOT": str(workspace)},
        cwd=workspace,
    )


def run(root: Path) -> None:
    validate = script(root, ".cursor/skills/nicki/scripts/validate-harness-stdout.py")
    required = (
        "active_task",
        "status_path",
        "next_step",
        "completed_steps",
        "readiness",
        "sheep",
    )

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        # Clean readiness → no readiness_error, exit 0, contract valid.
        ws, wt = _fixture(tmp / "ok", validation={"readiness": {"status": "ready_for_acceptance"}})
        proc = _boot(root, ws, wt)
        if proc.returncode != 0:
            raise AssertionError(f"fail: clean bootstrap should exit 0: {proc.stderr}")
        out = json_line(proc.stdout)
        for field in required:
            if field not in out:
                raise AssertionError(f"fail: clean missing {field}: {out}")
        if out.get("readiness") != "ready_for_acceptance":
            raise AssertionError(f"fail: readiness value: {out}")
        if "readiness_error" in out:
            raise AssertionError("fail: clean run must not set readiness_error")
        val = run_py(
            validate,
            "--script",
            "bootstrap-context.py",
            "--stdout",
            proc.stdout.strip(),
            "--exit-code",
            "0",
            cwd=root,
        )
        if val.returncode != 0:
            raise AssertionError(f"fail: clean contract: {val.stdout}")

        # Truncated validation → contract stdout, readiness null, readiness_error set, exit 0.
        ws, wt = _fixture(tmp / "bad", validation=BROKEN)
        proc = _boot(root, ws, wt)
        if proc.returncode != 0:
            raise AssertionError(
                f"fail: soft-fail must exit 0 (got {proc.returncode}): stderr={proc.stderr!r}"
            )
        if not proc.stdout.strip():
            raise AssertionError("fail: soft-fail must print contract stdout (no sheep-fallback)")
        out = json_line(proc.stdout)
        for field in required:
            if field not in out:
                raise AssertionError(f"fail: soft-fail missing {field}: {out}")
        if out.get("readiness") is not None:
            raise AssertionError(f"fail: soft-fail readiness should be null: {out}")
        err = out.get("readiness_error") or ""
        if "readiness parse error" not in err:
            raise AssertionError(f"fail: readiness_error missing parse message: {out}")
        if out.get("next_step") != "acceptance":
            raise AssertionError(f"fail: soft-fail must keep next_step from status: {out}")
        val = run_py(
            validate,
            "--script",
            "bootstrap-context.py",
            "--stdout",
            proc.stdout.strip(),
            "--exit-code",
            "0",
            cwd=root,
        )
        if val.returncode != 0:
            raise AssertionError(f"fail: soft-fail must still pass harness contract: {val.stdout}")

        # No validation pointer → readiness null, no readiness_error, exit 0.
        ws, wt = _fixture(tmp / "none", validation=None)
        proc = _boot(root, ws, wt)
        out = json_line(proc.stdout)
        if proc.returncode != 0 or out.get("readiness") is not None or "readiness_error" in out:
            raise AssertionError(f"fail: absent validation should be quiet null: {out}")

        # Hard failure: no registry entry → exit 1, empty stdout (still harness failure).
        orphan = tmp / "orphan/workspace/worktrees" / SLUG
        orphan.mkdir(parents=True)
        _put(orphan.parents[1] / "global-status.json", {"tasks": {}})
        _put(orphan.parents[1] / "nicki-workspace.example.yaml", {"name": "test"})
        proc = _boot(root, orphan.parents[1], orphan)
        if proc.returncode != 1:
            raise AssertionError(f"fail: missing registry should exit 1: {proc}")
        if proc.stdout.strip():
            raise AssertionError("fail: hard failure must not print contract stdout")

    print("smoke-bootstrap-contract: ok")
