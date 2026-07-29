"""--mode jump: materialize prerequisite into current-task/ (same suffix only)."""

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

        # External JSON spec → copied to expected current-task/specs/demo.json
        external = tmpdir / "outside" / "my-spec.json"
        _put(external, '{"title": "demo", "open_questions": []}\n')
        jump = _summary(wt, "jump.json", {"artifact": str(external), "open_questions": []})
        proc, out = _write(update, root, wt, jump, "--step", "subtasks", "--mode", "jump")
        if proc.returncode != 0 or out.get("written") is not True:
            raise AssertionError(f"fail: jump write: {proc.stdout}{proc.stderr}")
        arts = _status(wt).get("artifacts") or {}
        if arts.get("spec") != "current-task/specs/to-subtasks.json":
            raise AssertionError(f"fail: expected specs/<worktree>.json pointer: {arts}")
        dest = wt / "current-task/specs/to-subtasks.json"
        if not dest.is_file() or dest.read_text(encoding="utf-8") != external.read_text(
            encoding="utf-8"
        ):
            raise AssertionError("fail: external JSON must be copied into current-task/")

        # Wrong suffix (brainstorm .md into spec slot) → input error, no conversion.
        bad_md = tmpdir / "outside" / "design.md"
        _put(bad_md, "# Design\n")
        bad = _summary(wt, "bad.json", {"artifact": str(bad_md)})
        proc, out = _write(update, root, wt, bad, "--step", "subtasks", "--mode", "jump")
        if proc.returncode != 1 or not any("must be .json" in e for e in out.get("errors", [])):
            raise AssertionError(f"fail: .md into spec slot should be rejected: {out}")

        # In-tree correct path kept; jump to review.
        wt2 = tmpdir / "in-tree"
        wt2.mkdir()
        _put(wt2 / "current-task/subtasks/x.md", "- [ ] a\n")
        seed2 = _summary(
            wt2,
            "seed.json",
            {
                "completed_step": "subtasks",
                "artifact": "current-task/subtasks/x.md",
                "task": {"slug": "x", "original": "x"},
            },
        )
        proc, _ = _write(update, root, wt2, seed2, "--step", "subtasks")
        if proc.returncode != 0:
            raise AssertionError(f"fail: seed2: {proc.stdout}{proc.stderr}")
        _put(wt2 / "current-task/executions/mine.json", '{"ok": true}\n')
        jump2 = _summary(
            wt2, "jump.json", {"artifact": "current-task/executions/mine.json"}
        )
        proc, out = _write(update, root, wt2, jump2, "--step", "review", "--mode", "jump")
        if proc.returncode != 0:
            raise AssertionError(f"fail: jump review: {proc.stdout}{proc.stderr}")
        if (_status(wt2).get("artifacts") or {}).get("execution") != (
            "current-task/executions/mine.json"
        ):
            raise AssertionError("fail: in-tree jump should keep execution path")

        proc, out = _write(update, root, wt2, jump2, "--step", "close", "--mode", "jump")
        if proc.returncode != 1:
            raise AssertionError(f"fail: jump close should be rejected: {out}")

        missing = _summary(wt2, "missing.json", {"artifact": str(tmpdir / "nope.json")})
        proc, out = _write(update, root, wt2, missing, "--step", "review", "--mode", "jump")
        if proc.returncode != 1 or not any("not found" in e for e in out.get("errors", [])):
            raise AssertionError(f"fail: missing artifact should error: {out}")

    print("smoke-jump-mode: ok")
