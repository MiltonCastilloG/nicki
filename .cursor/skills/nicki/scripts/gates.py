"""Per-step gate checks for Nicki pipeline routing."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from gate_utils import (
    BLOCKED_READINESS,
    artifact_path,
    completed,
    deny,
    file_ok,
    load_yaml,
    readiness,
)

GateFn = Callable[[dict[str, Any], Path, bool, bool], dict[str, Any] | None]

READINESS_STEPS = frozenset({"review", "acceptance", "sync", "fix"})


def gate_start(_: dict, __: Path, user_confirmed: bool, ___: bool) -> dict[str, Any] | None:
    if not user_confirmed:
        return deny("start requires user confirmation")
    return None


def gate_describe(status: dict, _: Path, __: bool, ___: bool) -> dict[str, Any] | None:
    original = ((status.get("task") or {}).get("original") or "").strip()
    if not original:
        return deny("describe gate: task.original missing")
    return None


def gate_spec(status: dict, worktree: Path, _: bool, __: bool) -> dict[str, Any] | None:
    story = artifact_path(worktree, status, "story")
    if not story:
        return deny("spec gate: artifacts.story unset")
    if not file_ok(story):
        return deny("spec gate: story file missing on disk")
    return None


def gate_subtasks(status: dict, worktree: Path, _: bool, __: bool) -> dict[str, Any] | None:
    if status.get("open_questions"):
        return deny("subtasks gate: status open_questions non-empty")
    spec_path = artifact_path(worktree, status, "spec")
    if not spec_path or not spec_path.is_file():
        return deny("subtasks gate: spec artifact missing")
    oq = load_yaml(spec_path).get("open_questions")
    if oq:
        return deny("subtasks gate: spec open_questions non-empty")
    return None


def gate_execute(status: dict, worktree: Path, _: bool, __: bool) -> dict[str, Any] | None:
    sub = artifact_path(worktree, status, "subtasks")
    if not file_ok(sub):
        return deny("execute gate: subtasks artifact missing")
    return None


def gate_review(status: dict, worktree: Path, user_confirmed: bool, _: bool) -> dict[str, Any] | None:
    exe = artifact_path(worktree, status, "execution")
    if not file_ok(exe):
        return deny("review gate: execution artifact missing")
    scope = load_yaml(exe).get("review_scope") or {}
    if scope.get("mode") == "partial" and not user_confirmed:
        return deny("review gate: partial review_scope needs user confirm")
    return None


def gate_acceptance(status: dict, worktree: Path, _: bool, __: bool) -> dict[str, Any] | None:
    rs = readiness(status, worktree)
    if rs != "ready_for_acceptance":
        return deny(f"acceptance gate: readiness is {rs or 'unset'}, need ready_for_acceptance")
    return None


def gate_fix(status: dict, worktree: Path, _: bool, __: bool) -> dict[str, Any] | None:
    if readiness(status, worktree) != "fix_required":
        return deny("fix gate: readiness is not fix_required")
    return None


def gate_sync(status: dict, worktree: Path, _: bool, override: bool) -> dict[str, Any] | None:
    rs = readiness(status, worktree)
    if rs in BLOCKED_READINESS:
        return deny(f"sync gate: readiness is {rs}")
    done = completed(status)
    if "acceptance" not in done and not override:
        return deny("sync gate: acceptance not recorded and no override")
    return None


def gate_archive(status: dict, worktree: Path, _: bool, __: bool) -> dict[str, Any] | None:
    sync_path = artifact_path(worktree, status, "sync")
    if not file_ok(sync_path):
        return deny("archive gate: sync artifact missing")
    ppm = (load_yaml(sync_path).get("pre_push_merge") or {}).get("status")
    if ppm != "merged":
        return deny("archive gate: pre_push_merge not merged on sync handoff")
    return None


def gate_integrate(status: dict, worktree: Path, user_confirmed: bool, _: bool) -> dict[str, Any] | None:
    if not file_ok(artifact_path(worktree, status, "sync")):
        return deny("integrate gate: sync artifact missing")
    if not file_ok(artifact_path(worktree, status, "archive")):
        return deny("integrate gate: archive artifact missing")
    if not user_confirmed:
        return deny("integrate gate: merge-into-main consent not recorded")
    return None


def gate_close(status: dict, worktree: Path, user_confirmed: bool, _: bool) -> dict[str, Any] | None:
    integrate_ok = "integrate" in completed(status) or file_ok(
        artifact_path(worktree, status, "integrate")
    )
    if not integrate_ok:
        return deny("close gate: integrate not recorded")
    if not user_confirmed:
        return deny("close gate: close consent not satisfied")
    return None


def gate_done(status: dict, _: Path, __: bool, ___: bool) -> dict[str, Any] | None:
    if "close" not in completed(status):
        return deny("done gate: close not completed")
    return None


GATES: dict[str, GateFn] = {
    "start": gate_start,
    "describe": gate_describe,
    "spec": gate_spec,
    "subtasks": gate_subtasks,
    "execute": gate_execute,
    "review": gate_review,
    "acceptance": gate_acceptance,
    "fix": gate_fix,
    "sync": gate_sync,
    "archive": gate_archive,
    "integrate": gate_integrate,
    "close": gate_close,
    "done": gate_done,
}
