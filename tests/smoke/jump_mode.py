"""--mode jump: position-only (next_step = target; current_step untouched)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tests.smoke._helpers import run_py, script


def _summary(tmp: Path, name: str, payload: dict) -> Path:
    path = tmp / name
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _write(update: Path, root: Path, worktree: Path, summary: Path, *extra: str):
    proc = run_py(
        update, "--worktree", str(worktree), "--json-path", str(summary), *extra, cwd=root
    )
    out = json.loads(proc.stdout.strip()) if proc.stdout.strip() else {}
    return proc, out


def _status(worktree: Path) -> dict:
    return json.loads((worktree / "current-task/status.json").read_text(encoding="utf-8"))


def _put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(root: Path) -> None:
    update = script(root, ".cursor/skills/current-task-update/scripts/update-status.py")

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)

        wt = tmpdir / "to-subtasks"
        wt.mkdir()
        _put(wt / "current-task/story.md", "# Story\n")
        seed = _summary(
            wt,
            "seed.json",
            {
                "completed_step": "describe",
                "artifact": "current-task/story.md",
                "task": {"original": "demo", "slug": "demo"},
            },
        )
        proc, _ = _write(update, root, wt, seed, "--step", "describe")
        if proc.returncode != 0:
            raise AssertionError(f"fail: seed: {proc.stdout}{proc.stderr}")

        before = _status(wt)
        before_current = (before.get("task") or {}).get("current_step")
        before_arts = dict(before.get("artifacts") or {})
        before_tree = {
            p.relative_to(wt).as_posix()
            for p in (wt / "current-task").rglob("*")
            if p.is_file()
        }

        # No summary artifact — jump still succeeds; current_step unchanged.
        jump = _summary(wt, "jump.json", {"open_questions": []})
        proc, out = _write(update, root, wt, jump, "--step", "subtasks", "--mode", "jump")
        if proc.returncode != 0 or out.get("written") is not True:
            raise AssertionError(f"fail: jump write: {proc.stdout}{proc.stderr}")
        if out.get("next_step") != "subtasks":
            raise AssertionError(f"fail: jump should set next_step to target: {out}")

        after = _status(wt)
        if (after.get("task") or {}).get("current_step") != before_current:
            raise AssertionError(
                f"fail: current_step must be byte-identical "
                f"({before_current!r} → {(after.get('task') or {}).get('current_step')!r})"
            )
        if (after.get("task") or {}).get("next_step") != "subtasks":
            raise AssertionError(f"fail: next_step should be subtasks: {after.get('task')}")
        if dict(after.get("artifacts") or {}) != before_arts:
            raise AssertionError("fail: jump must not register artifact pointers")

        after_tree = {
            p.relative_to(wt).as_posix()
            for p in (wt / "current-task").rglob("*")
            if p.is_file() and p.name != "status.json"
        }
        materialize_hits = [
            p
            for p in after_tree
            if (p.startswith("current-task/specs/") or p.startswith("current-task/executions/"))
            and p not in before_tree
        ]
        if materialize_hits:
            raise AssertionError(f"fail: jump must not copy files into current-task/: {materialize_hits}")

        effects = (after.get("task") or {}).get("side_effects") or []
        if not effects or effects[-1].get("mode") != "jump" or effects[-1].get("artifact") is not None:
            raise AssertionError(f"fail: jump side_effect should log artifact null: {effects}")

        # Jump to close still rejected.
        proc, out = _write(update, root, wt, jump, "--step", "close", "--mode", "jump")
        if proc.returncode != 1:
            raise AssertionError(f"fail: jump close should be rejected: {out}")

        # Execute normal write with omitted artifact does not create executions/*.json.
        wt2 = tmpdir / "no-execution"
        wt2.mkdir()
        seed2 = _summary(
            wt2,
            "seed.json",
            {
                "completed_step": "subtasks",
                "artifact": "current-task/subtasks/x.md",
                "task": {"slug": "x", "original": "x"},
            },
        )
        _put(wt2 / "current-task/subtasks/x.md", "- [ ] a\n")
        proc, _ = _write(update, root, wt2, seed2, "--step", "subtasks")
        if proc.returncode != 0:
            raise AssertionError(f"fail: seed2: {proc.stdout}{proc.stderr}")
        exe = _summary(wt2, "exe.json", {"completed_status": "complete", "open_questions": []})
        proc, out = _write(update, root, wt2, exe, "--step", "execute")
        if proc.returncode != 0 or out.get("written") is not True:
            raise AssertionError(f"fail: execute omit artifact: {proc.stdout}{proc.stderr}")
        if (_status(wt2).get("artifacts") or {}).get("execution"):
            raise AssertionError("fail: execute must not set artifacts.execution")
        if (wt2 / "current-task/executions").exists():
            raise AssertionError("fail: execute must not create executions/")

    print("smoke-jump-mode: ok")
