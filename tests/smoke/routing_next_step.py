"""Routing owns pipeline position: next_step_for resolves it."""

from __future__ import annotations

import sys
from pathlib import Path

SLUG = "routing-next"
SCRIPTS_REL = ".cursor/skills/current-task-update/scripts"


def _load_resolver(root: Path):
    path = str(root / SCRIPTS_REL)
    if path not in sys.path:
        sys.path.insert(0, path)
    from routing_write import next_step_for  # noqa: PLC0415 — path set above

    return next_step_for


def _check(resolve, step: str, status: dict, expected: str | None, label: str) -> None:
    got = resolve(step, status)
    if got != expected:
        raise AssertionError(f"fail: {label} expected {expected!r}, got {got!r}")
    print(f"ok: {label}")


def run(root: Path) -> None:
    resolve = _load_resolver(root)
    empty: dict = {"artifacts": {}}
    archived = {"artifacts": {"archive": f"docs/archive/{SLUG}/report.json"}}

    _check(resolve, "start", {}, "describe", "start → describe")
    _check(resolve, "describe", empty, "spec", "describe → spec")
    _check(resolve, "spec", empty, "subtasks", "spec → subtasks")
    _check(resolve, "execute", empty, "review", "execute → review")
    _check(resolve, "review", empty, "acceptance", "review → acceptance")
    _check(resolve, "acceptance", empty, "sync", "acceptance → sync")
    _check(resolve, "fix", empty, "execute", "fix → execute")
    _check(resolve, "archive", empty, "sync", "archive → sync (second pass)")
    _check(resolve, "integrate", empty, "close", "integrate → close")

    _check(resolve, "sync", empty, "archive", "first sync → archive")
    _check(resolve, "sync", archived, "integrate", "second sync → integrate")

    _check(resolve, "done", empty, None, "done has no successor")
    _check(resolve, "nonsense", empty, None, "unknown step resolves to None")
    print("smoke-routing-next-step: ok")
