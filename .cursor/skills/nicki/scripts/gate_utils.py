"""Shared helpers for Nicki check-gate scripts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
ROUTING_PATH = SCRIPT_DIR.parent / "routing.json"
BLOCKED_READINESS = frozenset({"fix_required", "blocked"})


class ArtifactParseError(ValueError):
    """Structured artifact could not be parsed as an object."""


def workspace_root() -> Path:
    override = os.environ.get("NICKI_WORKSPACE_ROOT")
    if override:
        return Path(override).resolve()
    p = SCRIPT_DIR
    for _ in range(12):
        git = p / ".git"
        if git.is_file():
            gitdir = Path(git.read_text(encoding="utf-8").split(":", 1)[1].strip())
            if "/worktrees/" in gitdir.as_posix():
                return gitdir.parent.parent.parent
        if (p / "worktrees").is_dir() and (p / "nicki-workspace.example.yaml").exists():
            return p
        p = p.parent
    return SCRIPT_DIR.parent.parent.parent.parent


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping. Prefer load_artifact for task artifacts."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_artifact(path: Path) -> dict[str, Any]:
    """Load a task artifact by suffix (.json or .yaml/.yml).

    Raises ArtifactParseError on malformed content so gates can deny cleanly.
    In-flight .yaml files still load; new writers emit .json only.
    """
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    try:
        if suffix == ".json":
            data = json.loads(text)
        elif suffix in {".yaml", ".yml"}:
            data = yaml.safe_load(text)
        else:
            raise ArtifactParseError(f"unsupported artifact suffix: {suffix or '(none)'}")
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ArtifactParseError(f"{path.name}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ArtifactParseError(f"{path.name}: root must be an object")
    return data


def load_routing() -> dict[str, Any]:
    if not ROUTING_PATH.is_file():
        raise FileNotFoundError(f"routing missing: {ROUTING_PATH}")
    return load_json(ROUTING_PATH)


def resolve_worktree(path: str) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p.resolve()
    return (workspace_root() / p).resolve()


def artifact_path(worktree: Path, status: dict[str, Any], key: str) -> Path | None:
    rel = (status.get("artifacts") or {}).get(key)
    return worktree / rel if rel else None


def file_ok(path: Path | None) -> bool:
    return path is not None and path.is_file()


def completed(status: dict[str, Any]) -> set[str]:
    return set((status.get("task") or {}).get("completed_steps") or [])


def readiness(status: dict[str, Any], worktree: Path) -> str | None:
    rel = (status.get("artifacts") or {}).get("review_validation")
    if not rel:
        return None
    path = worktree / rel
    if not path.is_file():
        return None
    return (load_artifact(path).get("readiness") or {}).get("status")


def deny(reason: str) -> dict[str, Any]:
    return {"allowed": False, "sheep": None, "reason": reason, "user_confirm": None}


def allow(sheep: str | None, user_confirm: Any) -> dict[str, Any]:
    return {"allowed": True, "sheep": sheep, "reason": "", "user_confirm": user_confirm or False}


def load_status(worktree: Path) -> dict[str, Any]:
    status_path = worktree / "current-task/status.json"
    if not status_path.is_file():
        raise FileNotFoundError("status.json missing in worktree")
    return json.loads(status_path.read_text(encoding="utf-8"))
