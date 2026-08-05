"""completed_status enum + write-mode surface (normal / jump only)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tests.smoke._helpers import run_py, script

ENUM = ("complete", "blocked")


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

    declared = _enum_from_source(update)
    if declared != list(ENUM):
        raise AssertionError(f"fail: COMPLETED_STATUSES drifted: {declared}")

    routing = json.loads(
        (root / ".cursor/skills/nicki/routing.json").read_text(encoding="utf-8")
    )
    routed = (routing.get("sheep_return_contract") or {}).get("completed_status_values")
    if routed != list(ENUM):
        raise AssertionError(f"fail: routing completed_status_values drifted: {routed}")

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)

        # Enum members are accepted; unknown values are rejected loudly.
        # complete advances next_step; blocked keeps next_step at the completed step.
        for value in ENUM:
            wt = tmpdir / f"enum-{value}"
            wt.mkdir()
            s = _summary(
                wt,
                "summary.json",
                {"completed_step": "spec", "next_step": "subtasks", "completed_status": value},
            )
            proc, out = _write(update, root, wt, s)
            if proc.returncode != 0 or out.get("written") is not True:
                raise AssertionError(f"fail: {value} should write: {proc.stdout}{proc.stderr}")
            task = _status(wt).get("task") or {}
            if "completed_steps" in task:
                raise AssertionError("fail: status must not write completed_steps")
            if task.get("current_step") != "spec":
                raise AssertionError(f"fail: {value} current_step {task.get('current_step')!r}")
            want_next = "subtasks" if value == "complete" else "spec"
            if task.get("next_step") != want_next:
                raise AssertionError(
                    f"fail: {value} next_step {task.get('next_step')!r} != {want_next!r}"
                )

        for value in ("done", "COMPLETE", "", None, 1):
            wt = tmpdir / f"bad-{value!r}".replace("/", "_")
            wt.mkdir()
            s = _summary(
                wt,
                "summary.json",
                {"completed_step": "spec", "next_step": "subtasks", "completed_status": value},
            )
            proc, out = _write(update, root, wt, s)
            if proc.returncode != 1 or out.get("written") is not False:
                raise AssertionError(f"fail: completed_status {value!r} should be rejected")
            if not any("completed_status" in e for e in out.get("errors", [])):
                raise AssertionError(f"fail: error should name completed_status: {out}")
            if (wt / "current-task/status.json").exists():
                raise AssertionError("fail: rejected write must not create status.json")

        wt = tmpdir / "modes"
        wt.mkdir()
        seed = _summary(
            wt,
            "seed.json",
            {
                "completed_step": "execute",
                "next_step": "review",
            },
        )
        proc, _ = _write(update, root, wt, seed)
        if proc.returncode != 0:
            raise AssertionError(f"fail: seed write: {proc.stderr}")

        # Ad-hoc is a directly-invoked sheep, not a write mode — the CLI must refuse it.
        # Unknown modes go the same way: argparse rejects before anything is written.
        thin = _summary(wt, "thin.json", {"completed_status": "complete"})
        for mode in ("adhoc", "sideways"):
            proc = run_py(
                update,
                "--worktree",
                str(wt),
                "--json-path",
                str(thin),
                "--step",
                "describe",
                "--mode",
                mode,
                cwd=root,
            )
            if proc.returncode == 0:
                raise AssertionError(f"fail: --mode {mode} should be rejected")

        if ((_status(wt).get("task")) or {}).get("side_effects"):
            raise AssertionError("fail: rejected modes must not log side effects")

        # With a completed step, next_step comes from routing — summary may omit it.
        s = _summary(wt, "no-next.json", {"completed_step": "spec", "artifact": "current-task/specs/x.json"})
        proc, out = _write(update, root, wt, s)
        if proc.returncode != 0 or out.get("next_step") != "subtasks":
            raise AssertionError(
                f"fail: completed step should derive next_step from routing: {out}"
            )

        # Position-only normal write (no completed step) still requires next_step.
        s = _summary(wt, "pos-only-bad.json", {"open_questions": []})
        proc, out = _write(update, root, wt, s)
        if proc.returncode != 1 or not any(
            "next_step" in e for e in out.get("errors", [])
        ):
            raise AssertionError("fail: position-only write must still require next_step")

    print("smoke-status-vocabulary: ok")


def _enum_from_source(update: Path) -> list[str]:
    for line in update.read_text(encoding="utf-8").splitlines():
        if line.startswith("COMPLETED_STATUSES"):
            return [p.strip().strip('"') for p in line.split("(", 1)[1].rstrip(")").split(",") if p.strip()]
    raise AssertionError("fail: COMPLETED_STATUSES not declared")
