"""--mode jump: adopt prerequisite artifact and point next_step at target."""

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


def run(root: Path) -> None:
    update = script(root, ".cursor/skills/current-task-update/scripts/update-status.py")

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)

        # Seed mid-describe → jump to subtasks with a user-provided spec path.
        wt = tmpdir / "to-subtasks"
        wt.mkdir()
        seed = _summary(
            wt,
            "seed.json",
            {
                "completed_step": "describe",
                "artifact": "current-task/story.md",
                "task": {"original": "demo"},
            },
        )
        proc, _ = _write(update, root, wt, seed, "--step", "describe")
        if proc.returncode != 0:
            raise AssertionError(f"fail: seed: {proc.stdout}{proc.stderr}")

        jump = _summary(
            wt,
            "jump.json",
            {"artifact": "current-task/specs/demo.json", "open_questions": []},
        )
        proc, out = _write(update, root, wt, jump, "--step", "subtasks", "--mode", "jump")
        if proc.returncode != 0 or out.get("written") is not True:
            raise AssertionError(f"fail: jump write: {proc.stdout}{proc.stderr}")
        if out.get("mode") != "jump" or out.get("next_step") != "subtasks":
            raise AssertionError(f"fail: jump stdout: {out}")
        task = _status(wt).get("task") or {}
        if task.get("current_step") != "spec":
            raise AssertionError(f"fail: jump current_step should be predecessor spec: {task}")
        if task.get("next_step") != "subtasks":
            raise AssertionError(f"fail: jump next_step: {task}")
        arts = _status(wt).get("artifacts") or {}
        if arts.get("spec") != "current-task/specs/demo.json":
            raise AssertionError(f"fail: jump must set artifacts.spec: {arts}")
        effects = task.get("side_effects") or []
        if not effects or effects[-1].get("mode") != "jump":
            raise AssertionError(f"fail: jump side_effects: {effects}")

        # Jump to review registers execution as prerequisite.
        wt2 = tmpdir / "to-review"
        wt2.mkdir()
        seed2 = _summary(
            wt2,
            "seed.json",
            {"completed_step": "subtasks", "artifact": "current-task/subtasks/x.md"},
        )
        proc, _ = _write(update, root, wt2, seed2, "--step", "subtasks")
        if proc.returncode != 0:
            raise AssertionError(f"fail: seed2: {proc.stdout}{proc.stderr}")
        jump2 = _summary(
            wt2,
            "jump.json",
            {"artifact": "current-task/executions/mine.json"},
        )
        proc, out = _write(update, root, wt2, jump2, "--step", "review", "--mode", "jump")
        if proc.returncode != 0:
            raise AssertionError(f"fail: jump review: {proc.stdout}{proc.stderr}")
        st2 = _status(wt2)
        if (st2.get("task") or {}).get("next_step") != "review":
            raise AssertionError(f"fail: jump review next_step: {st2}")
        if (st2.get("task") or {}).get("current_step") != "execute":
            raise AssertionError(f"fail: jump review current_step: {st2}")
        if (st2.get("artifacts") or {}).get("execution") != "current-task/executions/mine.json":
            raise AssertionError(f"fail: jump review artifact: {st2}")

        # Jump cannot target close; needs existing status.
        proc, out = _write(update, root, wt2, jump2, "--step", "close", "--mode", "jump")
        if proc.returncode != 1 or out.get("written") is not False:
            raise AssertionError(f"fail: jump close should be rejected: {out}")

        fresh = tmpdir / "fresh"
        fresh.mkdir()
        proc, out = _write(
            update, root, fresh, jump, "--step", "subtasks", "--mode", "jump"
        )
        if proc.returncode != 1:
            raise AssertionError("fail: jump on fresh worktree should fail")
        if (fresh / "current-task/status.json").exists():
            raise AssertionError("fail: jump must not init status.json")

    print("smoke-jump-mode: ok")
