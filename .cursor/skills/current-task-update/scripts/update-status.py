#!/usr/bin/env python3
"""Write current-task/status.json from Nicki summary JSON.

Required inputs:
  --worktree (CLI)
  summary JSON: next_step — required in normal mode, ignored in adhoc mode

Modes (--mode):
  normal — default; advances task.current_step / next_step / completed_steps
  adhoc  — step ran out of band: position fields are left untouched, the artifact
           pointer is still recorded, and one task.side_effects entry is appended

Optional summary fields (defaults applied):
  completed_step — when present, sets task.current_step, may append completed_steps,
    and may set artifact pointer; when absent, current_step is still written
    (preserved from existing status, or "start" on fresh init). --step overrides it.
  artifact — skip artifact pointer when absent or when the step is unknown
  completed_status — default "complete"; must be one of COMPLETED_STATUSES
  open_questions — default []
  summary, task.* — ignored or derived

Success stdout: {"written": true, "path", "completed_step", "next_step", "mode", "blockers"}
  completed_step is the JSON value or null when omitted.
Input error stdout: {"written": false, "errors": ["missing required field: next_step"]}
Exit 0 on success, 1 on input error or write failure.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_SUMMARY_FIELDS = ("next_step",)

# Closed set. "complete" is the only value that appends to task.completed_steps;
# anything unknown used to skip the append silently and still report success.
COMPLETED_STATUSES = ("complete", "blocked")

MODES = ("normal", "adhoc")


def _fail(errors: list[str]) -> None:
    print(json.dumps({"written": False, "errors": errors}))
    raise SystemExit(1)


def _read_text(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def _parse_summary(text: str, *, source_path: str | None) -> dict[str, Any]:
    suffix = Path(source_path).suffix.lower() if source_path else ".json"
    try:
        if suffix in {".yaml", ".yml"}:
            import yaml  # type: ignore

            obj = yaml.safe_load(text)
        else:
            obj = json.loads(text)
    except Exception as e:  # noqa: BLE001 — surface as input error
        _fail([f"summary parse error: {e}"])
    if not isinstance(obj, dict):
        _fail(["summary root must be a mapping/object"])
    return obj


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _init_status(
    worktree_path: str,
    slug: str,
    summary: dict[str, Any],
    completed_step: str | None,
    next_step: str,
    completed_status: str,
) -> dict[str, Any]:
    task = summary.get("task") if isinstance(summary.get("task"), dict) else {}
    original = task.get("original") if isinstance(task.get("original"), str) else slug
    completed_steps: list[str] = []
    if completed_step is not None and completed_status == "complete":
        completed_steps = [completed_step]
    return {
        "meta": {"schema": "task-status.v2"},
        "task": {
            "id": task.get("id"),
            "slug": slug,
            "project": task.get("project"),
            "title": task.get("title"),
            "original": original,
            "type": task.get("type"),
            "current_step": completed_step if completed_step is not None else "start",
            "next_step": next_step,
            "completed_steps": completed_steps,
        },
        "scope": {"worktree_path": worktree_path},
        "artifacts": {},
        "open_questions": [],
    }


def _set_artifact_pointer(
    status: dict[str, Any], completed_step: str, artifact_path: str | None
) -> None:
    if not artifact_path:
        return

    artifacts = status.setdefault("artifacts", {})
    if not isinstance(artifacts, dict):
        status["artifacts"] = {}
        artifacts = status["artifacts"]

    key_by_step = {
        "describe": "story",
        "spec": "spec",
        "subtasks": "subtasks",
        "execute": "execution",
        "review": "review_validation",
        "sync": "sync",
        "archive": "archive",
        "integrate": "integrate",
    }
    key = key_by_step.get(completed_step)
    if key:
        artifacts[key] = artifact_path


def _validate_required(summary: dict[str, Any], *, mode: str) -> None:
    errors: list[str] = []
    if mode == "normal":
        for field in REQUIRED_SUMMARY_FIELDS:
            value = summary.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"missing required field: {field}")
            elif not isinstance(value, str):
                errors.append(f"required field must be a string: {field}")
    status = summary.get("completed_status", "complete")
    if status not in COMPLETED_STATUSES:
        errors.append(
            f"completed_status must be one of {list(COMPLETED_STATUSES)}: got {status!r}"
        )
    if errors:
        _fail(errors)


def _append_side_effect(status: dict[str, Any], step: str | None, artifact: str | None) -> None:
    task = status.setdefault("task", {})
    effects = task.get("side_effects")
    if not isinstance(effects, list):
        effects = []
    effects.append(
        {
            "step": step,
            "mode": "adhoc",
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "artifact": artifact,
        }
    )
    task["side_effects"] = effects


def _optional_completed_step(summary: dict[str, Any]) -> str | None:
    raw = summary.get("completed_step")
    if raw is None:
        return None
    if not isinstance(raw, str):
        _fail(["optional field must be a string when present: completed_step"])
    stripped = raw.strip()
    return stripped or None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worktree", required=True, help="Repo-relative or absolute worktree path")
    parser.add_argument(
        "--json-path",
        help="Path to Nicki summary JSON; if omitted with no --yaml-path, read stdin as JSON",
    )
    parser.add_argument(
        "--yaml-path",
        help="Deprecated: path to Nicki summary YAML (in-flight only)",
    )
    parser.add_argument(
        "--step",
        help="Pipeline step Nicki dispatched; overrides summary completed_step",
    )
    parser.add_argument(
        "--mode",
        default="normal",
        choices=MODES,
        help="normal advances position; adhoc leaves position untouched",
    )
    args = parser.parse_args()

    if not args.worktree.strip():
        _fail(["missing required field: worktree"])

    worktree_arg = args.worktree
    worktree = Path(worktree_arg)
    if not worktree.is_absolute():
        worktree = (Path.cwd() / worktree).resolve()

    slug = worktree.name
    status_path = worktree / "current-task" / "status.json"
    status_path.parent.mkdir(parents=True, exist_ok=True)

    source = args.json_path or args.yaml_path
    summary = _parse_summary(_read_text(source), source_path=source)
    _validate_required(summary, mode=args.mode)

    completed_step = (args.step or "").strip() or _optional_completed_step(summary)
    next_step = summary.get("next_step")
    completed_status = summary.get("completed_status", "complete")
    artifact = summary.get("artifact")
    open_questions = summary.get("open_questions", [])

    if artifact is not None and not isinstance(artifact, str):
        _fail(["optional field must be a string when present: artifact"])
    if not isinstance(open_questions, list):
        _fail(["optional field must be a list when present: open_questions"])

    status = _load_json(status_path)
    if status is None:
        if args.mode == "adhoc":
            _fail(["adhoc mode needs an existing status.json"])
        status = _init_status(
            str(Path(worktree_arg)),
            slug,
            summary,
            completed_step,
            next_step,
            completed_status if isinstance(completed_status, str) else "complete",
        )

    status["meta"] = {"schema": "task-status.v2"}

    task = status.setdefault("task", {})
    if not isinstance(task, dict):
        task = {}
        status["task"] = task
    task["slug"] = task.get("slug") or slug

    if args.mode == "adhoc":
        # Out-of-band run: record what happened, leave pipeline position alone.
        _set_artifact_pointer(status, completed_step or "", artifact if isinstance(artifact, str) else None)
        _append_side_effect(status, completed_step, artifact if isinstance(artifact, str) else None)
        next_step = task.get("next_step")
    else:
        task["next_step"] = next_step

    if args.mode == "normal" and completed_step is not None:
        task["current_step"] = completed_step
        completed_steps = task.get("completed_steps")
        if not isinstance(completed_steps, list):
            completed_steps = []
        if completed_status == "complete" and completed_step not in completed_steps:
            completed_steps.append(completed_step)
        task["completed_steps"] = completed_steps
        _set_artifact_pointer(status, completed_step, artifact if isinstance(artifact, str) else None)
    elif args.mode == "normal":
        existing = task.get("current_step")
        if not isinstance(existing, str) or not existing.strip():
            task["current_step"] = "start"
        # Preserve completed_steps / artifacts when completed_step omitted.

    scope = status.setdefault("scope", {})
    if not isinstance(scope, dict):
        scope = {}
        status["scope"] = scope
    scope["worktree_path"] = scope.get("worktree_path") or str(Path(worktree_arg))

    if args.mode == "normal" or "open_questions" in summary:
        status["open_questions"] = open_questions

    try:
        status_path.write_text(
            json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    except OSError as e:
        _fail([f"failed to write status.json: {e}"])

    blockers: list[dict[str, Any]] = []
    for q in open_questions:
        if isinstance(q, dict):
            blockers.append(q)
        else:
            blockers.append({"step": next_step, "question": str(q), "blocks_next_step": True})

    print(
        json.dumps(
            {
                "written": True,
                "path": str(status_path),
                "completed_step": completed_step,
                "next_step": next_step,
                "mode": args.mode,
                "blockers": blockers,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
