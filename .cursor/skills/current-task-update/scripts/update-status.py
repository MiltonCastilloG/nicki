#!/usr/bin/env python3
"""Write current-task/status.json from Nicki summary YAML.

Required inputs:
  --worktree (CLI)
  summary YAML: completed_step, next_step

Optional summary fields (defaults applied):
  artifact — skip artifact pointer when absent
  completed_status — default "complete"
  open_questions — default []
  summary, task.* — ignored or derived

Success stdout: {"written": true, "path", "completed_step", "next_step", "blockers"}
Input error stdout: {"written": false, "errors": ["missing required field: <name>"]}
Exit 0 on success, 1 on input error or write failure.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_SUMMARY_FIELDS = ("completed_step", "next_step")


def _fail(errors: list[str]) -> None:
    print(json.dumps({"written": False, "errors": errors}))
    raise SystemExit(1)


def _read_text(yaml_path: str | None) -> str:
    if yaml_path:
        return Path(yaml_path).read_text(encoding="utf-8")
    return sys.stdin.read()


def _parse_yaml(text: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError("PyYAML is required (import yaml failed)") from e

    obj = yaml.safe_load(text)
    if not isinstance(obj, dict):
        _fail(["summary YAML root must be a mapping/object"])
    return obj


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _init_status(worktree_path: str, slug: str, summary: dict[str, Any]) -> dict[str, Any]:
    task = summary.get("task") if isinstance(summary.get("task"), dict) else {}
    original = task.get("original") if isinstance(task.get("original"), str) else slug
    return {
        "meta": {"schema": "task-status.v2"},
        "task": {
            "id": task.get("id"),
            "slug": slug,
            "project": task.get("project"),
            "title": task.get("title"),
            "original": original,
            "type": task.get("type"),
            "current_step": summary["completed_step"],
            "next_step": summary["next_step"],
            "completed_steps": [],
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


def _validate_required(summary: dict[str, Any]) -> None:
    errors: list[str] = []
    for field in REQUIRED_SUMMARY_FIELDS:
        value = summary.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"missing required field: {field}")
        elif not isinstance(value, str):
            errors.append(f"required field must be a string: {field}")
    if errors:
        _fail(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worktree", required=True, help="Repo-relative or absolute worktree path")
    parser.add_argument("--yaml-path", help="Path to Nicki summary YAML; if omitted, read stdin")
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

    summary = _parse_yaml(_read_text(args.yaml_path))
    _validate_required(summary)

    completed_step = summary["completed_step"]
    next_step = summary["next_step"]
    completed_status = summary.get("completed_status", "complete")
    artifact = summary.get("artifact")
    open_questions = summary.get("open_questions", [])

    if artifact is not None and not isinstance(artifact, str):
        _fail(["optional field must be a string when present: artifact"])
    if not isinstance(open_questions, list):
        _fail(["optional field must be a list when present: open_questions"])

    status = _load_json(status_path)
    if status is None:
        status = _init_status(str(Path(worktree_arg)), slug, summary)

    status["meta"] = {"schema": "task-status.v2"}

    task = status.setdefault("task", {})
    if not isinstance(task, dict):
        task = {}
        status["task"] = task
    task["slug"] = task.get("slug") or slug
    task["current_step"] = completed_step
    task["next_step"] = next_step

    completed_steps = task.get("completed_steps")
    if not isinstance(completed_steps, list):
        completed_steps = []
    if completed_status == "complete" and completed_step not in completed_steps:
        completed_steps.append(completed_step)
    task["completed_steps"] = completed_steps

    scope = status.setdefault("scope", {})
    if not isinstance(scope, dict):
        scope = {}
        status["scope"] = scope
    scope["worktree_path"] = scope.get("worktree_path") or str(Path(worktree_arg))

    status["open_questions"] = open_questions
    _set_artifact_pointer(status, completed_step, artifact if isinstance(artifact, str) else None)

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
                "blockers": blockers,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
