"""Every gate, allow and deny, exercised through check-gate.py.

Per-step checks in `gates.py` are document/blocker only. Consent and adhoc/jump
bookends live in `gate_policy` / POLICY_CASES. Operational progress is position.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from tests.smoke._helpers import json_line, run_py, script

SLUG = "matrix"

SPEC = f"current-task/specs/{SLUG}.json"
BROKEN_JSON = '{"open_questions": ['
CONFIRMED = ("--user-confirmed",)
ADHOC = ("--mode", "adhoc")


def _status(**over: Any) -> dict[str, Any]:
    task = {
        "slug": SLUG,
        "original": over.pop("original", "add a demo widget"),
        "current_step": over.pop("current_step", "start"),
        "next_step": over.pop("next_step", "describe"),
    }
    task.update(over.pop("task_extra", {}))
    status = {
        "meta": {"schema": "task-status.v2"},
        "task": task,
        "artifacts": dict(over.pop("artifacts", {})),
        "open_questions": list(over.pop("open_questions", ())),
    }
    status.update(over)
    return status


# label, step, cli args, status, files, expected allowed, reason needle
CASES: list[tuple[str, str, tuple[str, ...], dict | None, dict, bool, str]] = [
    ("start allows without confirmation", "start", (), None, {}, True, ""),
    ("describe needs task.original", "describe", (), _status(original=" "), {}, False, "task.original missing"),
    ("describe with task.original", "describe", (), _status(), {}, True, ""),
    ("spec allows without story", "spec", (), _status(), {}, True, ""),
    (
        "subtasks blocked by status open_questions",
        "subtasks",
        (),
        _status(artifacts={"spec": SPEC}, open_questions=[{"question": "which CTA?"}]),
        {SPEC: {"open_questions": []}},
        False,
        "status open_questions non-empty",
    ),
    ("subtasks allows without spec file", "subtasks", (), _status(), {}, True, ""),
    (
        "subtasks blocked by spec open_questions",
        "subtasks",
        (),
        _status(artifacts={"spec": SPEC}),
        {SPEC: {"open_questions": ["which CTA?"]}},
        False,
        "spec open_questions non-empty",
    ),
    (
        "subtasks denies cleanly on unparseable spec",
        "subtasks",
        (),
        _status(artifacts={"spec": SPEC}),
        {SPEC: BROKEN_JSON},
        False,
        "spec parse error",
    ),
    (
        "subtasks with clean spec",
        "subtasks",
        (),
        _status(artifacts={"spec": SPEC}),
        {SPEC: {"open_questions": []}},
        True,
        "",
    ),
    ("execute allows", "execute", (), _status(), {}, True, ""),
    ("review allows", "review", (), _status(), {}, True, ""),
    ("acceptance allows (chat consent)", "acceptance", (), _status(), {}, True, ""),
    ("fix allows (position)", "fix", (), _status(), {}, True, ""),
    ("sync with confirmation", "sync", CONFIRMED, _status(), {}, True, ""),
    ("archive with confirmation", "archive", CONFIRMED, _status(), {}, True, ""),
    ("integrate with confirmation", "integrate", CONFIRMED, _status(), {}, True, ""),
    ("close with confirmation", "close", CONFIRMED, _status(), {}, True, ""),
    ("done allows", "done", (), _status(), {}, True, ""),
    ("unknown step denies", "bogus", (), _status(), {}, False, "unknown step: bogus"),
]

POLICY_CASES: list[tuple[str, str, tuple[str, ...], dict | None, dict, bool, str]] = [
    ("sync denies without consent", "sync", (), _status(), {}, False, "push feature branch"),
    ("archive denies without consent", "archive", (), _status(), {}, False, "write task archive"),
    ("integrate denies without consent", "integrate", (), _status(), {}, False, "push main"),
    ("close denies without consent", "close", (), _status(), {}, False, "delete worktree"),
    ("start allows without consent", "start", (), None, {}, True, ""),
    (
        "ad-hoc cannot buy consent",
        "sync",
        ADHOC,
        _status(),
        {},
        False,
        "user consent required",
    ),
    (
        "jump cannot target close",
        "close",
        ("--mode", "jump", "--user-confirmed"),
        _status(),
        {},
        False,
        "cannot be a jump target",
    ),
    (
        "adhoc denied on start",
        "start",
        ADHOC,
        None,
        {},
        False,
        "cannot run out of band",
    ),
]


def _materialize(worktree: Path, status: dict | None, files: dict) -> None:
    if status is not None:
        st = dict(status)
        task = dict(st.get("task") or {})
        task.setdefault("slug", SLUG)
        st["task"] = task
        st.setdefault("scope", {"worktree_path": str(worktree)})
        st.setdefault("meta", {"schema": "task-status.v2"})
        path = worktree / "current-task/status.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")
    for rel, body in files.items():
        p = worktree / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(body, str):
            p.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")
        else:
            p.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")


def _run_case(
    root: Path,
    label: str,
    step: str,
    cli: tuple[str, ...],
    status: dict | None,
    files: dict,
    expect_allow: bool,
    needle: str,
) -> None:
    with tempfile.TemporaryDirectory() as td:
        workspace = Path(td)
        worktree = workspace / "worktrees" / SLUG
        worktree.mkdir(parents=True)
        _materialize(worktree, status, files)
        env = {**os.environ, "NICKI_WORKSPACE_ROOT": str(workspace)}
        proc = run_py(
            script(root, ".cursor/skills/nicki/scripts/check-gate.py"),
            "--worktree",
            str(worktree),
            "--step",
            step,
            *cli,
            env=env,
        )
        out = json_line(proc.stdout) if proc.stdout.strip() else {}
        allowed = out.get("allowed")
        reason = out.get("reason") or ""
        if expect_allow:
            if allowed is not True:
                raise AssertionError(f"fail: {label}: expected allow, got {out}")
        else:
            if allowed is not False or (needle and needle not in reason):
                raise AssertionError(f"fail: {label}: expected deny ({needle!r}), got {out}")
        print(f"ok: {label}")


def run(root: Path) -> None:
    for case in CASES:
        _run_case(root, *case)
    for case in POLICY_CASES:
        _run_case(root, *case)
    print("smoke-gates-matrix: ok")
