"""Routing owns pipeline position: next_step_for resolves it, the gate echoes it."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

from tests.smoke._helpers import json_line, run_py, script

SCRIPTS_REL = ".cursor/skills/nicki/scripts"
SLUG = "routing-next"


def _load_resolver(root: Path):
    path = str(root / SCRIPTS_REL)
    if path not in sys.path:
        sys.path.insert(0, path)
    from gate_utils import next_step_for  # noqa: PLC0415 — path set above

    return next_step_for


def _check(resolve, step: str, status: dict, expected: str | None, label: str, **kw) -> None:
    got = resolve(step, status, **kw)
    if got != expected:
        raise AssertionError(f"fail: {label} expected {expected!r}, got {got!r}")
    print(f"ok: {label}")


def _resolver_cases(root: Path) -> None:
    resolve = _load_resolver(root)
    empty: dict = {"artifacts": {}}
    archived = {"artifacts": {"archive": f"docs/archive/{SLUG}/report.json"}}

    _check(resolve, "start", {}, "describe", "start → describe")
    _check(resolve, "describe", empty, "spec", "describe → spec")
    _check(resolve, "spec", empty, "subtasks", "spec → subtasks")
    _check(resolve, "execute", empty, "review", "execute → review")
    _check(resolve, "acceptance", empty, "sync", "acceptance → sync")
    _check(resolve, "fix", empty, "execute", "fix → execute")
    _check(resolve, "archive", empty, "sync", "archive → sync (second pass)")
    _check(resolve, "integrate", empty, "close", "integrate → close")

    _check(resolve, "sync", empty, "archive", "first sync → archive")
    _check(resolve, "sync", archived, "integrate", "second sync → integrate")

    _check(resolve, "review", empty, None, "review unresolved without readiness")
    _check(
        resolve,
        "review",
        empty,
        "acceptance",
        "review + ready_for_acceptance → acceptance",
        readiness_status="ready_for_acceptance",
    )
    _check(
        resolve,
        "review",
        empty,
        "execute",
        "review + fix_required → execute",
        readiness_status="fix_required",
    )

    _check(resolve, "done", empty, None, "done has no successor")
    _check(resolve, "nonsense", empty, None, "unknown step resolves to None")


def _gate_echo(root: Path) -> None:
    with tempfile.TemporaryDirectory() as td:
        workspace = Path(td)
        worktree = workspace / "worktrees" / SLUG
        status_path = worktree / "current-task/status.json"
        status_path.parent.mkdir(parents=True, exist_ok=True)
        subtasks = worktree / f"current-task/subtasks/{SLUG}.md"
        subtasks.parent.mkdir(parents=True, exist_ok=True)
        subtasks.write_text("- [ ] work\n", encoding="utf-8")
        status_path.write_text(
            json.dumps(
                {
                    "meta": {"schema": "task-status.v2"},
                    "task": {
                        "slug": SLUG,
                        "current_step": "subtasks",
                        "next_step": "execute",
                    },
                    "scope": {"worktree_path": str(worktree)},
                    "artifacts": {"subtasks": f"current-task/subtasks/{SLUG}.md"},
                    "open_questions": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        env = {**os.environ, "NICKI_WORKSPACE_ROOT": str(workspace)}
        gate = script(root, f"{SCRIPTS_REL}/check-gate.py")

        allowed = json_line(
            run_py(gate, "--worktree", str(worktree), "--step", "execute", env=env).stdout
        )
        if allowed.get("allowed") is not True or allowed.get("next_step") != "review":
            raise AssertionError(f"fail: allow should echo next_step review, got {allowed}")
        print("ok: gate allow echoes routing next_step")

        if allowed.get("artifact") != f"current-task/executions/{SLUG}.json":
            raise AssertionError(f"fail: allow should echo resolved artifact, got {allowed}")
        print("ok: gate allow echoes expected_artifact with <slug> resolved")

        denied = json_line(
            run_py(gate, "--worktree", str(worktree), "--step", "integrate", env=env).stdout
        )
        if denied.get("allowed") is not False or "next_step" not in denied:
            raise AssertionError(f"fail: deny should carry next_step key, got {denied}")
        if denied["next_step"] is not None:
            raise AssertionError(f"fail: deny next_step should be null, got {denied}")
        print("ok: gate deny carries null next_step")


def run(root: Path) -> None:
    _resolver_cases(root)
    _gate_echo(root)
    print("smoke-routing-next-step: ok")
