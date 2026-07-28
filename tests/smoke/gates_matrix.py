"""Every gate, allow and deny, exercised through check-gate.py.

Consent enforcement for `sync` and `archive` is deliberately not asserted here:
those gates ignore `--user-confirmed` today (harness-gate-bugs Finding 6) and
flexibility step 5 owns the fix plus its cases.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from tests.smoke._helpers import json_line, run_py, script

SLUG = "matrix"
ROOT_PREFIX = "root:"

STORY = "current-task/story.md"
SPEC = f"current-task/specs/{SLUG}.json"
SUBTASKS = f"current-task/subtasks/{SLUG}.md"
EXECUTION = f"current-task/executions/{SLUG}.json"
VALIDATION = "current-task/review-validations/r1-validation.json"
SYNC = f"current-task/syncs/{SLUG}.json"
INTEGRATE = f"current-task/integrates/{SLUG}.json"
ARCHIVE = f"docs/archive/{SLUG}/report.json"

MERGED = {"pre_push_merge": {"status": "merged"}}
BROKEN_JSON = '{"open_questions": ['


def _status(**over: Any) -> dict[str, Any]:
    task = {
        "slug": SLUG,
        "original": over.pop("original", "add a demo widget"),
        "current_step": "start",
        "next_step": over.pop("next_step", "describe"),
        "completed_steps": list(over.pop("completed", ())),
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


def _readiness(value: str) -> dict[str, Any]:
    return {"readiness": {"status": value}}


def _validation(value: str) -> dict[str, Any]:
    return {"artifacts": {"review_validation": VALIDATION}, "files": {VALIDATION: _readiness(value)}}


# label, step, cli args, status, files, expected allowed, reason needle
CASES: list[tuple[str, str, tuple[str, ...], dict | None, dict, bool, str]] = [
    ("start needs confirmation", "start", (), None, {}, False, "start requires user confirmation"),
    ("start with confirmation", "start", ("--user-confirmed",), None, {}, True, ""),
    ("describe needs task.original", "describe", (), _status(original=" "), {}, False, "task.original missing"),
    ("describe with task.original", "describe", (), _status(), {}, True, ""),
    ("spec needs story pointer", "spec", (), _status(), {}, False, "artifacts.story unset"),
    (
        "spec needs story on disk",
        "spec",
        (),
        _status(artifacts={"story": STORY}),
        {},
        False,
        "story file missing on disk",
    ),
    (
        "spec with story present",
        "spec",
        (),
        _status(artifacts={"story": STORY}),
        {STORY: "# Story\n"},
        True,
        "",
    ),
    (
        "subtasks blocked by status open_questions",
        "subtasks",
        (),
        _status(artifacts={"spec": SPEC}, open_questions=[{"question": "which CTA?"}]),
        {SPEC: {"open_questions": []}},
        False,
        "status open_questions non-empty",
    ),
    (
        "subtasks needs spec on disk",
        "subtasks",
        (),
        _status(artifacts={"spec": SPEC}),
        {},
        False,
        "spec artifact missing",
    ),
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
    ("execute needs subtasks", "execute", (), _status(), {}, False, "subtasks artifact missing"),
    (
        "execute with subtasks",
        "execute",
        (),
        _status(artifacts={"subtasks": SUBTASKS}),
        {SUBTASKS: "- [ ] work\n"},
        True,
        "",
    ),
    ("review needs execution", "review", (), _status(), {}, False, "execution artifact missing"),
    (
        "review denies cleanly on unparseable execution",
        "review",
        (),
        _status(artifacts={"execution": EXECUTION}),
        {EXECUTION: BROKEN_JSON},
        False,
        "execution parse error",
    ),
    (
        "partial review needs confirmation",
        "review",
        (),
        _status(artifacts={"execution": EXECUTION}),
        {EXECUTION: {"review_scope": {"mode": "partial"}}},
        False,
        "partial review_scope needs user confirm",
    ),
    (
        "partial review with confirmation",
        "review",
        ("--user-confirmed",),
        _status(artifacts={"execution": EXECUTION}),
        {EXECUTION: {"review_scope": {"mode": "partial"}}},
        True,
        "",
    ),
    (
        "full review needs no confirmation",
        "review",
        (),
        _status(artifacts={"execution": EXECUTION}),
        {EXECUTION: {"review_scope": {"mode": "full"}}},
        True,
        "",
    ),
    ("acceptance needs readiness", "acceptance", (), _status(), {}, False, "readiness is unset"),
    (
        "acceptance denies on fix_required",
        "acceptance",
        (),
        _status(artifacts={"review_validation": VALIDATION}),
        {VALIDATION: _readiness("fix_required")},
        False,
        "readiness is fix_required",
    ),
    (
        "acceptance denies on readiness absent from routing",
        "acceptance",
        (),
        _status(artifacts={"review_validation": VALIDATION}),
        {VALIDATION: _readiness("rerun_review")},
        False,
        "readiness is rerun_review",
    ),
    (
        "acceptance denies cleanly on unparseable validation",
        "acceptance",
        (),
        _status(artifacts={"review_validation": VALIDATION}),
        {VALIDATION: BROKEN_JSON},
        False,
        "readiness parse error",
    ),
    (
        "acceptance when ready",
        "acceptance",
        (),
        _status(artifacts={"review_validation": VALIDATION}),
        {VALIDATION: _readiness("ready_for_acceptance")},
        True,
        "",
    ),
    (
        "fix denies unless fix_required",
        "fix",
        (),
        _status(artifacts={"review_validation": VALIDATION}),
        {VALIDATION: _readiness("ready_for_acceptance")},
        False,
        "readiness is not fix_required",
    ),
    (
        "fix when fix_required",
        "fix",
        (),
        _status(artifacts={"review_validation": VALIDATION}),
        {VALIDATION: _readiness("fix_required")},
        True,
        "",
    ),
    (
        "sync blocked by readiness routing",
        "sync",
        (),
        _status(artifacts={"review_validation": VALIDATION}, completed=["acceptance"]),
        {VALIDATION: _readiness("fix_required")},
        False,
        "readiness routing blocks sync",
    ),
    (
        "sync blocked while a review rerun is pending",
        "sync",
        (),
        _status(artifacts={"review_validation": VALIDATION}, completed=["acceptance"]),
        {VALIDATION: _readiness("rerun_review")},
        False,
        "readiness routing blocks sync",
    ),
    (
        "sync needs acceptance recorded",
        "sync",
        (),
        _status(artifacts={"review_validation": VALIDATION}),
        {VALIDATION: _readiness("ready_for_acceptance")},
        False,
        "acceptance not recorded",
    ),
    (
        "sync with override instead of acceptance",
        "sync",
        ("--override",),
        _status(artifacts={"review_validation": VALIDATION}),
        {VALIDATION: _readiness("ready_for_acceptance")},
        True,
        "",
    ),
    (
        "sync with acceptance recorded",
        "sync",
        (),
        _status(artifacts={"review_validation": VALIDATION}, completed=["acceptance"]),
        {VALIDATION: _readiness("ready_for_acceptance")},
        True,
        "",
    ),
    ("archive needs sync handoff", "archive", (), _status(), {}, False, "sync artifact missing"),
    (
        "archive needs pre_push_merge satisfied",
        "archive",
        (),
        _status(artifacts={"sync": SYNC}),
        {SYNC: {"pre_push_merge": {"status": "skipped"}}},
        False,
        "pre_push_merge not satisfied",
    ),
    (
        "archive denies cleanly on unparseable sync",
        "archive",
        (),
        _status(artifacts={"sync": SYNC}),
        {SYNC: BROKEN_JSON},
        False,
        "sync parse error",
    ),
    (
        "archive after merged sync",
        "archive",
        (),
        _status(artifacts={"sync": SYNC}),
        {SYNC: MERGED},
        True,
        "",
    ),
    (
        "archive accepts not_needed merge",
        "archive",
        (),
        _status(artifacts={"sync": SYNC}),
        {SYNC: {"pre_push_merge": {"status": "not_needed"}}},
        True,
        "",
    ),
    (
        "integrate needs sync handoff",
        "integrate",
        ("--user-confirmed",),
        _status(artifacts={"archive": ARCHIVE}),
        {ROOT_PREFIX + ARCHIVE: {"task": SLUG}},
        False,
        "sync artifact missing",
    ),
    ("close needs integrate", "close", ("--user-confirmed",), _status(), {}, False, "integrate not recorded"),
    (
        "close needs confirmation",
        "close",
        (),
        _status(completed=["integrate"]),
        {},
        False,
        "close consent not satisfied",
    ),
    (
        "close accepts integrate handoff on disk",
        "close",
        ("--user-confirmed",),
        _status(artifacts={"integrate": INTEGRATE}),
        {INTEGRATE: {"merged": True}},
        True,
        "",
    ),
    ("done needs close", "done", (), _status(), {}, False, "close not completed"),
    ("done after close", "done", (), _status(completed=["close"]), {}, True, ""),
    ("unknown step denies", "bogus", (), _status(), {}, False, "unknown step: bogus"),
    (
        "legacy v1 status denies without story pointer",
        "spec",
        (),
        _status(task_extra={"story_artifact": STORY}, history=[{"step": "describe"}]),
        {STORY: "# Story\n"},
        False,
        "artifacts.story unset",
    ),
]


def _build(base: Path, status: dict | None, files: dict[str, Any]) -> tuple[Path, Path]:
    workspace = base / "workspace"
    worktree = workspace / "worktrees" / SLUG
    worktree.mkdir(parents=True, exist_ok=True)
    if status is not None:
        status = {**status, "scope": {"worktree_path": str(worktree)}}
        _put(worktree / "current-task/status.json", status)
    for rel, payload in files.items():
        root_scoped = rel.startswith(ROOT_PREFIX)
        target = (workspace if root_scoped else worktree) / rel.removeprefix(ROOT_PREFIX)
        _put(target, payload)
    return workspace, worktree


def _put(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = payload if isinstance(payload, str) else json.dumps(payload, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


def run(root: Path) -> None:
    gate = script(root, ".cursor/skills/nicki/scripts/check-gate.py")
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        for i, (label, step, args, status, files, want_allow, needle) in enumerate(CASES):
            workspace, worktree = _build(Path(td) / f"c{i}", status, files)
            proc = run_py(
                gate,
                "--worktree",
                str(worktree),
                "--step",
                step,
                *args,
                env={**os.environ, "NICKI_WORKSPACE_ROOT": str(workspace)},
            )
            if not proc.stdout.strip():
                failures.append(f"fail: {label}: empty stdout ({proc.stderr.strip()})")
                continue
            result = json_line(proc.stdout)
            reason = result.get("reason") or ""
            if result.get("allowed") is not want_allow:
                failures.append(f"fail: {label}: expected allowed={want_allow}, got {result}")
            elif needle and needle not in reason:
                failures.append(f"fail: {label}: reason {reason!r} lacks {needle!r}")
            elif "gate harness error" in reason:
                failures.append(f"fail: {label}: leaked internal error: {reason}")

        missing_status = Path(td) / "no-status/workspace/worktrees" / SLUG
        missing_status.mkdir(parents=True)
        proc = run_py(
            gate,
            "--worktree",
            str(missing_status),
            "--step",
            "spec",
            env={**os.environ, "NICKI_WORKSPACE_ROOT": str(missing_status.parents[1])},
        )
        result = json_line(proc.stdout)
        if result.get("allowed") is not False or "status.json missing" not in (result.get("reason") or ""):
            failures.append(f"fail: missing status.json should deny cleanly, got {result}")

    if failures:
        raise AssertionError("\n".join(failures))

    print(f"ok: {len(CASES) + 1} gate cases through check-gate.py")
    print("smoke-gates-matrix: ok")
