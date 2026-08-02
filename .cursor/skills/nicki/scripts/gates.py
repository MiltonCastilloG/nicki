"""Per-step gate checks for Nicki pipeline routing.

Denials are never waived. Consent is enforced in `check-gate.py` from
`user_confirm_required` in routing before these run. Operational progress is
position (`current_step` / `next_step`); these gates only cover document/blocker
checks that position alone cannot express.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from gate_utils import ArtifactParseError, artifact_path, deny, load_artifact

GateFn = Callable[[dict[str, Any], Path, bool], dict[str, Any] | None]


def gate_describe(status: dict, _: Path, __: bool) -> dict[str, Any] | None:
    original = ((status.get("task") or {}).get("original") or "").strip()
    if not original:
        return deny("describe gate: task.original missing")
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


GATES: dict[str, GateFn] = {
    "describe": gate_describe,
    "subtasks": gate_subtasks,
}
