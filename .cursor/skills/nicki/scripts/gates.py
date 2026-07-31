"""Per-step gate checks for Nicki pipeline routing.

Every check returns a denial via `deny`. Denials are never waived — no
`--override`, no sequence class. Consent is enforced in `check-gate.py` from
`user_confirm_required` in routing before these run. The one exception is
`review`, whose confirm may depend on review-input scope rather than the step.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from gate_utils import (
    BLOCKED_READINESS,
    ArtifactParseError,
    artifact_path,
    deny,
    file_ok,
    load_artifact,
    readiness,
)

GateFn = Callable[[dict[str, Any], Path, bool], dict[str, Any] | None]

READINESS_STEPS = frozenset({"review", "acceptance", "sync", "fix"})


def gate_describe(status: dict, _: Path, __: bool) -> dict[str, Any] | None:
    original = ((status.get("task") or {}).get("original") or "").strip()
    if not original:
        return deny("describe gate: task.original missing")
    return None


def gate_spec(status: dict, worktree: Path, _: bool) -> dict[str, Any] | None:
    # Story file optional — informal jump / chat-first. Deny only on open questions
    # when a spec is already present (handled in subtasks). Spec itself: no hard pred.
    return None


def gate_subtasks(status: dict, worktree: Path, _: bool) -> dict[str, Any] | None:
    if status.get("open_questions"):
        return deny("subtasks gate: status open_questions non-empty")
    spec_path = artifact_path(worktree, status, "spec")
    if spec_path and spec_path.is_file():
        try:
            oq = load_artifact(spec_path).get("open_questions")
        except ArtifactParseError as exc:
            return deny(f"subtasks gate: spec parse error: {exc}")
        if oq:
            return deny("subtasks gate: spec open_questions non-empty")
    return None


def gate_execute(status: dict, worktree: Path, _: bool) -> dict[str, Any] | None:
    # Subtasks file optional — informal jump / chat-first.
    return None


def gate_review(status: dict, worktree: Path, user_confirmed: bool) -> dict[str, Any] | None:
    # Execution artifact dropped. Partial scope only from review-input when present.
    review_input = artifact_path(worktree, status, "review_input")
    if not file_ok(review_input):
        return None
    try:
        scope = load_artifact(review_input).get("review_scope") or {}
    except ArtifactParseError as exc:
        return deny(f"review gate: review_input parse error: {exc}")
    if scope.get("mode") == "partial" and not user_confirmed:
        return deny("review gate: partial review_scope needs user confirm")
    return None


def gate_acceptance(status: dict, worktree: Path, _: bool) -> dict[str, Any] | None:
    rs = readiness(status, worktree)
    if rs != "ready_for_acceptance":
        return deny(f"acceptance gate: readiness is {rs or 'unset'}, need ready_for_acceptance")
    return None


def gate_fix(status: dict, worktree: Path, _: bool) -> dict[str, Any] | None:
    if readiness(status, worktree) != "fix_required":
        return deny("fix gate: readiness is not fix_required")
    return None


def gate_sync(status: dict, worktree: Path, _: bool) -> dict[str, Any] | None:
    rs = readiness(status, worktree)
    if rs in BLOCKED_READINESS:
        return deny(f"sync gate: readiness is {rs}")
    return None


def gate_archive(status: dict, worktree: Path, _: bool) -> dict[str, Any] | None:
    sync_path = artifact_path(worktree, status, "sync")
    if not file_ok(sync_path):
        return deny("archive gate: sync artifact missing")
    try:
        ppm = (load_artifact(sync_path).get("pre_push_merge") or {}).get("status")
    except ArtifactParseError as exc:
        return deny(f"archive gate: sync parse error: {exc}")
    # Back-compat: early sync handoffs used "not_needed" when the base branch
    # was already up to date in the feature branch. Treat that as satisfying the
    # archive gate, since the intent is "base incorporated before archiving".
    if ppm not in {"merged", "not_needed"}:
        return deny("archive gate: pre_push_merge not satisfied on sync handoff")
    return None


def gate_integrate(status: dict, worktree: Path, _: bool) -> dict[str, Any] | None:
    if not file_ok(artifact_path(worktree, status, "sync")):
        return deny("integrate gate: sync artifact missing")
    if not file_ok(artifact_path(worktree, status, "archive")):
        return deny("integrate gate: archive artifact missing")
    return None


def gate_close(status: dict, worktree: Path, _: bool) -> dict[str, Any] | None:
    if not file_ok(artifact_path(worktree, status, "integrate")):
        return deny("close gate: integrate not recorded")
    return None


GATES: dict[str, GateFn] = {
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
}
