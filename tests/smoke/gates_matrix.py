"""Every gate, allow and deny, exercised through check-gate.py.

CASES cover the per-step checks in `gates.py`. POLICY_CASES cover what
`routing.json` `gate_policy` decides before those run — consent, ad-hoc
admission, jump bookends — and assert `mode` the gate contract echoes back.
Denials are never waived.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from tests.smoke._helpers import json_line, run_py, script

SLUG = "matrix"

STORY = "current-task/story.md"
SPEC = f"current-task/specs/{SLUG}.json"
SUBTASKS = f"current-task/subtasks/{SLUG}.md"
VALIDATION = "current-task/review-validations/r1-validation.json"
SYNC = f"current-task/syncs/{SLUG}.json"
INTEGRATE = f"current-task/integrates/{SLUG}.json"
ARCHIVE = f"docs/archive/{SLUG}/report.json"

MERGED = {"pre_push_merge": {"status": "merged"}}
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


def _readiness(value: str) -> dict[str, Any]:
    return {"readiness": {"status": value}}


def _validation(value: str) -> dict[str, Any]:
    return {"artifacts": {"review_validation": VALIDATION}, "files": {VALIDATION: _readiness(value)}}


# label, step, cli args, status, files, expected allowed, reason needle
CASES: list[tuple[str, str, tuple[str, ...], dict | None, dict, bool, str]] = [
    ("start allows without confirmation", "start", (), None, {}, True, ""),
    ("start with confirmation still allows", "start", ("--user-confirmed",), None, {}, True, ""),
    ("describe needs task.original", "describe", (), _status(original=" "), {}, False, "task.original missing"),
    ("describe with task.original", "describe", (), _status(), {}, True, ""),
    ("spec allows without story", "spec", (), _status(), {}, True, ""),
    (
        "spec still allows when story present",
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
        "subtasks allows without spec file",
        "subtasks",
        (),
        _status(),
        {},
        True,
        "",
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
    ("execute allows without subtasks", "execute", (), _status(), {}, True, ""),
    (
        "execute with subtasks still allows",
        "execute",
        (),
        _status(artifacts={"subtasks": SUBTASKS}),
        {SUBTASKS: "- [ ] work\n"},
        True,
        "",
    ),
    ("review allows without execution", "review", (), _status(), {}, True, ""),
    (
        "review denies cleanly on unparseable review_input",
        "review",
        (),
        _status(artifacts={"review_input": "current-task/review-inputs/r1-review.json"}),
        {"current-task/review-inputs/r1-review.json": BROKEN_JSON},
        False,
        "review_input parse error",
    ),
    (
        "partial review needs confirmation",
        "review",
        (),
        _status(artifacts={"review_input": "current-task/review-inputs/r1-review.json"}),
        {
            "current-task/review-inputs/r1-review.json": {
                "approved": False,
                "content": "n",
                "important-considerations": [],
                "review_scope": {"mode": "partial"},
            }
        },
        False,
        "partial review_scope needs user confirm",
    ),
    (
        "partial review with confirmation",
        "review",
        ("--user-confirmed",),
        _status(artifacts={"review_input": "current-task/review-inputs/r1-review.json"}),
        {
            "current-task/review-inputs/r1-review.json": {
                "approved": False,
                "content": "n",
                "important-considerations": [],
                "review_scope": {"mode": "partial"},
            }
        },
        True,
        "",
    ),
    (
        "full review needs no confirmation",
        "review",
        (),
        _status(artifacts={"review_input": "current-task/review-inputs/r1-review.json"}),
        {
            "current-task/review-inputs/r1-review.json": {
                "approved": False,
                "content": "n",
                "important-considerations": [],
                "review_scope": {"mode": "full"},
            }
        },
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
        CONFIRMED,
        _status(artifacts={"review_validation": VALIDATION}, current_step="acceptance"),
        {VALIDATION: _readiness("fix_required")},
        False,
        "readiness is fix_required",
    ),
    (
        "sync blocked while a review rerun is pending",
        "sync",
        CONFIRMED,
        _status(artifacts={"review_validation": VALIDATION}, current_step="acceptance"),
        {VALIDATION: _readiness("rerun_review")},
        False,
        "readiness is rerun_review",
    ),
    (
        "sync without acceptance allows when confirmed",
        "sync",
        CONFIRMED,
        _status(artifacts={"review_validation": VALIDATION}),
        {VALIDATION: _readiness("ready_for_acceptance")},
        True,
        "",
    ),
    (
        "sync with acceptance current_step",
        "sync",
        CONFIRMED,
        _status(artifacts={"review_validation": VALIDATION}, current_step="acceptance"),
        {VALIDATION: _readiness("ready_for_acceptance")},
        True,
        "",
    ),
    (
        "second sync allowed when archive exists",
        "sync",
        CONFIRMED,
        _status(
            artifacts={"review_validation": VALIDATION, "archive": ARCHIVE},
            current_step="archive",
        ),
        {
            VALIDATION: _readiness("ready_for_acceptance"),
            ARCHIVE: {"task": SLUG},
        },
        True,
        "",
    ),
    ("archive needs sync handoff", "archive", CONFIRMED, _status(), {}, False, "sync artifact missing"),
    (
        "archive needs pre_push_merge satisfied",
        "archive",
        CONFIRMED,
        _status(artifacts={"sync": SYNC}),
        {SYNC: {"pre_push_merge": {"status": "skipped"}}},
        False,
        "pre_push_merge not satisfied",
    ),
    (
        "archive denies cleanly on unparseable sync",
        "archive",
        CONFIRMED,
        _status(artifacts={"sync": SYNC}),
        {SYNC: BROKEN_JSON},
        False,
        "sync parse error",
    ),
    (
        "archive after merged sync",
        "archive",
        CONFIRMED,
        _status(artifacts={"sync": SYNC}),
        {SYNC: MERGED},
        True,
        "",
    ),
    (
        "archive accepts not_needed merge",
        "archive",
        CONFIRMED,
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
        {ARCHIVE: {"task": SLUG}},
        False,
        "sync artifact missing",
    ),
    ("close needs integrate", "close", ("--user-confirmed",), _status(), {}, False, "integrate not recorded"),
    (
        "close needs confirmation",
        "close",
        (),
        _status(artifacts={"integrate": INTEGRATE}),
        {},
        False,
        "user consent required",
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
    ("done allows without close", "done", (), _status(), {}, True, ""),
    ("done after close", "done", (), _status(current_step="close"), {}, True, ""),
    ("unknown step denies", "bogus", (), _status(), {}, False, "unknown step: bogus"),
    (
        "legacy v1 status allows spec without story pointer",
        "spec",
        (),
        _status(task_extra={"story_artifact": STORY}, history=[{"step": "describe"}]),
        {STORY: "# Story\n"},
        True,
        "",
    ),
]


READY = {VALIDATION: _readiness("ready_for_acceptance")}
MID_EXECUTE = _status(next_step="review", current_step="execute")

# label, step, cli args, status, files, expected allowed, reason needle
POLICY_CASES: list[tuple[str, str, tuple[str, ...], dict | None, dict, bool, str]] = [
    # Consent comes from routing user_confirm_required, and the routing sentence
    # is the reason. Every step that declares it denies without the flag.
    (
        "sync denies without consent",
        "sync",
        (),
        _status(artifacts={"review_validation": VALIDATION}, current_step="acceptance"),
        READY,
        False,
        "push feature branch",
    ),
    (
        "archive denies without consent",
        "archive",
        (),
        _status(artifacts={"sync": SYNC}),
        {SYNC: MERGED},
        False,
        "write task archive",
    ),
    (
        "integrate denies without consent",
        "integrate",
        (),
        _status(artifacts={"sync": SYNC, "archive": ARCHIVE}),
        {SYNC: MERGED, ARCHIVE: {"task": SLUG}},
        False,
        "push main",
    ),
    (
        "close denies without consent",
        "close",
        (),
        _status(artifacts={"integrate": INTEGRATE}),
        {},
        False,
        "delete worktree",
    ),
    (
        "start allows without consent",
        "start",
        (),
        None,
        {},
        True,
        "",
    ),
    # Consent is a safety check — no mode flag reaches it.
    (
        "missing confirm cannot buy consent",
        "integrate",
        (),
        _status(artifacts={"sync": SYNC, "archive": ARCHIVE}),
        {SYNC: MERGED, ARCHIVE: {"task": SLUG}},
        False,
        "user consent required",
    ),
    (
        "ad-hoc cannot buy consent",
        "sync",
        ADHOC,
        MID_EXECUTE,
        {},
        False,
        "user consent required",
    ),
    # Ad-hoc admission is routing data: every step except start/close/done opts in.
    # Mode does not waive denials; write semantics are separate.
    (
        "ad-hoc sync mid-execute allows",
        "sync",
        CONFIRMED + ADHOC,
        MID_EXECUTE,
        {},
        True,
        "",
    ),
    (
        "ad-hoc archive allows when sync handoff is ready",
        "archive",
        CONFIRMED + ADHOC,
        _status(artifacts={"sync": SYNC}),
        {SYNC: MERGED},
        True,
        "",
    ),
    (
        "ad-hoc integrate allows when inputs present",
        "integrate",
        CONFIRMED + ADHOC,
        _status(artifacts={"sync": SYNC, "archive": ARCHIVE}),
        {SYNC: MERGED, ARCHIVE: {"task": SLUG}},
        True,
        "",
    ),
    (
        "ad-hoc execute allows when subtasks exist",
        "execute",
        ADHOC,
        _status(artifacts={"subtasks": SUBTASKS}),
        {SUBTASKS: "- [ ] work\n"},
        True,
        "",
    ),
    (
        "ad-hoc start is refused",
        "start",
        CONFIRMED + ADHOC,
        None,
        {},
        False,
        "cannot run out of band",
    ),
    (
        "ad-hoc close is refused",
        "close",
        CONFIRMED + ADHOC,
        _status(artifacts={"integrate": INTEGRATE}),
        {},
        False,
        "cannot run out of band",
    ),
    # Readiness and missing inputs still hold under adhoc/jump.
    (
        "ad-hoc sync still blocked by fix_required",
        "sync",
        CONFIRMED + ADHOC,
        _status(artifacts={"review_validation": VALIDATION}),
        {VALIDATION: _readiness("fix_required")},
        False,
        "readiness is fix_required",
    ),
    (
        "no flag clears status open_questions",
        "subtasks",
        ADHOC,
        _status(open_questions=[{"question": "which CTA?"}]),
        {},
        False,
        "status open_questions non-empty",
    ),
    (
        "no flag skips integrate before close",
        "close",
        CONFIRMED + ADHOC,
        _status(),
        {},
        False,
        "cannot run out of band",
    ),
    # Jump: bookends refused; denials never waived; sync mid-execute ok when confirmed.
    (
        "jump sync mid-execute allows",
        "sync",
        CONFIRMED + ("--mode", "jump"),
        MID_EXECUTE,
        {},
        True,
        "",
    ),
    (
        "jump cannot target close",
        "close",
        CONFIRMED + ("--mode", "jump"),
        _status(artifacts={"integrate": INTEGRATE}),
        {INTEGRATE: {"merged": True}},
        False,
        "cannot be a jump target",
    ),
    (
        "jump cannot skip missing integrate before close",
        "close",
        CONFIRMED + ("--mode", "jump"),
        _status(),
        {},
        False,
        "cannot be a jump target",
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
        _put(worktree / rel, payload)
    return workspace, worktree


def _policy_declarations(root: Path) -> list[str]:
    """routing.json gate_policy must describe the gates that actually exist."""
    bad: list[str] = []
    routing = json.loads((root / ".cursor/skills/nicki/routing.json").read_text(encoding="utf-8"))
    steps = routing.get("steps") or {}
    policy = routing.get("gate_policy") or {}

    for name, cfg in steps.items():
        if cfg.get("user_confirm") and not cfg.get("user_confirm_required"):
            bad.append(f"fail: {name} has a user_confirm sentence but does not require it")
        if cfg.get("user_confirm_required") and not cfg.get("user_confirm"):
            bad.append(f"fail: {name} requires consent with no sentence to show the user")
        if cfg.get("irreversible"):
            bad.append(f"fail: {name} must not set irreversible (unused)")

    # Ad-hoc is open by default; only bookends (and the terminal marker) stay out.
    never_adhoc = {"start", "close", "done"}
    for name, cfg in steps.items():
        allowed = bool(cfg.get("adhoc_allowed"))
        if name in never_adhoc and allowed:
            bad.append(f"fail: {name} must not set adhoc_allowed")
        if name not in never_adhoc and not allowed:
            bad.append(f"fail: {name} should set adhoc_allowed")

    if "classes" in policy or "sequence_denials" in policy:
        bad.append("fail: gate_policy must not declare classes or sequence_denials")
    return bad


def _put(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = payload if isinstance(payload, str) else json.dumps(payload, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


def run(root: Path) -> None:
    gate = script(root, ".cursor/skills/nicki/scripts/check-gate.py")
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        cases = list(CASES) + list(POLICY_CASES)
        for i, (label, step, args, status, files, want_allow, needle) in enumerate(cases):
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
            expect_mode = "normal"
            if "--mode" in args:
                mi = args.index("--mode")
                expect_mode = args[mi + 1] if mi + 1 < len(args) else "normal"
            if result.get("allowed") is not want_allow:
                failures.append(f"fail: {label}: expected allowed={want_allow}, got {result}")
            elif needle and needle not in reason:
                failures.append(f"fail: {label}: reason {reason!r} lacks {needle!r}")
            elif "gate harness error" in reason:
                failures.append(f"fail: {label}: leaked internal error: {reason}")
            elif result.get("mode") != expect_mode:
                failures.append(f"fail: {label}: mode {result.get('mode')!r} != {expect_mode!r}")
            elif "gate_class" in result:
                failures.append(f"fail: {label}: gate_class must be absent from contract, got {result}")

        bad_mode = run_py(
            gate,
            "--worktree",
            str(Path(td) / "c0/workspace/worktrees" / SLUG),
            "--step",
            "sync",
            "--mode",
            "sideways",
            env={**os.environ, "NICKI_WORKSPACE_ROOT": str(Path(td) / "c0/workspace")},
        )
        if bad_mode.returncode == 0:
            failures.append("fail: unknown --mode should be rejected")

        failures.extend(_policy_declarations(root))

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

    print(
        f"ok: {len(CASES)} gate cases + {len(POLICY_CASES)} policy cases "
        "through check-gate.py"
    )
    print("smoke-gates-matrix: ok")
