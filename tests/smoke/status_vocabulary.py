"""completed_status enum + --mode adhoc no-advance write (flexibility step 4)."""

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
            steps = (_status(wt).get("task") or {}).get("completed_steps") or []
            expected = ["spec"] if value == "complete" else []
            if steps != expected:
                raise AssertionError(f"fail: {value} completed_steps {steps} != {expected}")

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

        # --mode adhoc: artifact recorded, position untouched, side effect logged.
        wt = tmpdir / "adhoc"
        wt.mkdir()
        seed = _summary(
            wt,
            "seed.json",
            {
                "completed_step": "execute",
                "next_step": "review",
                "artifact": "current-task/executions/foo.json",
            },
        )
        proc, _ = _write(update, root, wt, seed)
        if proc.returncode != 0:
            raise AssertionError(f"fail: seed write: {proc.stderr}")
        before = _status(wt)

        adhoc = _summary(
            wt,
            "adhoc.json",
            {"artifact": "current-task/syncs/foo.json", "completed_status": "complete"},
        )
        proc, out = _write(update, root, wt, adhoc, "--step", "sync", "--mode", "adhoc")
        if proc.returncode != 0 or out.get("written") is not True:
            raise AssertionError(f"fail: adhoc write: {proc.stdout}{proc.stderr}")
        if out.get("mode") != "adhoc":
            raise AssertionError("fail: stdout should echo mode")
        if out.get("next_step") != "review":
            raise AssertionError(f"fail: adhoc must echo unchanged next_step: {out}")

        after = _status(wt)
        task_before, task_after = before.get("task") or {}, after.get("task") or {}
        for field in ("current_step", "next_step", "completed_steps"):
            if task_after.get(field) != task_before.get(field):
                raise AssertionError(f"fail: adhoc changed task.{field}")
        if (after.get("artifacts") or {}).get("sync") != "current-task/syncs/foo.json":
            raise AssertionError("fail: adhoc should record artifact pointer")
        effects = task_after.get("side_effects") or []
        if len(effects) != 1:
            raise AssertionError(f"fail: expected one side effect: {effects}")
        effect = effects[0]
        if effect.get("step") != "sync" or effect.get("mode") != "adhoc":
            raise AssertionError(f"fail: side effect fields: {effect}")
        if not effect.get("at") or not effect.get("artifact"):
            raise AssertionError(f"fail: side effect needs at + artifact: {effect}")

        # adhoc needs no next_step, and repeated runs append rather than replace.
        again = _summary(wt, "again.json", {"artifact": "current-task/syncs/bar.json"})
        proc, out = _write(update, root, wt, again, "--step", "sync", "--mode", "adhoc")
        if proc.returncode != 0:
            raise AssertionError(f"fail: second adhoc write: {proc.stdout}{proc.stderr}")
        effects = ((_status(wt).get("task")) or {}).get("side_effects") or []
        if len(effects) != 2:
            raise AssertionError(f"fail: side effects should append: {effects}")

        # adhoc on a worktree with no status.json is an input error, not an init.
        fresh = tmpdir / "adhoc-fresh"
        fresh.mkdir()
        s = _summary(fresh, "summary.json", {"artifact": "current-task/syncs/x.json"})
        proc, out = _write(update, root, fresh, s, "--step", "sync", "--mode", "adhoc")
        if proc.returncode != 1 or out.get("written") is not False:
            raise AssertionError("fail: adhoc on fresh worktree should fail")
        if (fresh / "current-task/status.json").exists():
            raise AssertionError("fail: adhoc must not initialise status.json")

        # Unknown --mode is rejected by argparse before anything is written.
        proc = run_py(
            update,
            "--worktree",
            str(wt),
            "--json-path",
            str(again),
            "--mode",
            "sideways",
            cwd=root,
        )
        if proc.returncode == 0:
            raise AssertionError("fail: unknown mode should be rejected")

        # normal mode still requires next_step.
        s = _summary(wt, "no-next.json", {"completed_step": "spec"})
        proc, out = _write(update, root, wt, s)
        if proc.returncode != 1 or not any(
            "next_step" in e for e in out.get("errors", [])
        ):
            raise AssertionError("fail: normal mode must still require next_step")

    print("smoke-status-vocabulary: ok")


def _enum_from_source(update: Path) -> list[str]:
    for line in update.read_text(encoding="utf-8").splitlines():
        if line.startswith("COMPLETED_STATUSES"):
            return [p.strip().strip('"') for p in line.split("(", 1)[1].rstrip(")").split(",") if p.strip()]
    raise AssertionError("fail: COMPLETED_STATUSES not declared")
