"""Write path derives next_step and artifact keys from routing (flexibility step 7)."""

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
    routing = json.loads(
        (root / ".cursor/skills/nicki/routing.json").read_text(encoding="utf-8")
    )
    steps = routing.get("steps") or {}

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)

        # --step alone: no next_step in summary; routing supplies it.
        wt = tmpdir / "from-step"
        wt.mkdir()
        s = _summary(
            wt,
            "summary.json",
            {"artifact": "current-task/specs/foo.json", "completed_status": "complete"},
        )
        proc, out = _write(update, root, wt, s, "--step", "spec")
        if proc.returncode != 0 or out.get("written") is not True:
            raise AssertionError(f"fail: --step write: {proc.stdout}{proc.stderr}")
        if out.get("completed_step") != "spec":
            raise AssertionError(f"fail: --step should set completed_step: {out}")
        if out.get("next_step") != steps["spec"]["default_next_step"]:
            raise AssertionError(f"fail: expected routing next_step, got {out}")
        status = _status(wt)
        if (status.get("artifacts") or {}).get("spec") != "current-task/specs/foo.json":
            raise AssertionError("fail: artifact_key from routing should set artifacts.spec")
        if (status.get("task") or {}).get("next_step") != "subtasks":
            raise AssertionError("fail: status next_step should be subtasks")

        # Summary next_step is ignored when a step completed — routing wins.
        s = _summary(
            wt,
            "wrong-next.json",
            {
                "completed_step": "subtasks",
                "next_step": "close",
                "artifact": "current-task/subtasks/foo.md",
            },
        )
        proc, out = _write(update, root, wt, s)
        if proc.returncode != 0:
            raise AssertionError(f"fail: override attempt: {proc.stdout}{proc.stderr}")
        if out.get("next_step") != "execute":
            raise AssertionError(f"fail: routing must beat summary next_step: {out}")

        # Git tail: first sync → archive; second sync (archive set) → integrate.
        wt2 = tmpdir / "git-tail"
        wt2.mkdir()
        seed = _summary(
            wt2,
            "seed.json",
            {
                "completed_step": "acceptance",
                "artifact": None,
                "completed_status": "complete",
            },
        )
        # acceptance has no artifact_key; still advances.
        proc, out = _write(update, root, wt2, seed, "--step", "acceptance")
        if proc.returncode != 0 or out.get("next_step") != "sync":
            raise AssertionError(f"fail: acceptance → sync: {out}")

        first = _summary(
            wt2,
            "sync1.json",
            {"artifact": "current-task/syncs/foo.json", "completed_status": "complete"},
        )
        proc, out = _write(update, root, wt2, first, "--step", "sync")
        if out.get("next_step") != "archive":
            raise AssertionError(f"fail: first sync → archive: {out}")

        # Record archive pointer without advancing (simulate prior archive write).
        status = _status(wt2)
        status["artifacts"]["archive"] = "docs/archive/foo/report.json"
        (wt2 / "current-task/status.json").write_text(
            json.dumps(status, indent=2) + "\n", encoding="utf-8"
        )

        second = _summary(
            wt2,
            "sync2.json",
            {"artifact": "current-task/syncs/foo.json", "completed_status": "complete"},
        )
        proc, out = _write(update, root, wt2, second, "--step", "sync")
        if out.get("next_step") != "integrate":
            raise AssertionError(f"fail: second sync → integrate: {out}")

        # Review next_step comes from readiness_routing once validation is on disk.
        wt3 = tmpdir / "review"
        wt3.mkdir()
        val_rel = "current-task/review-validations/r1-validation.json"
        val_path = wt3 / val_rel
        val_path.parent.mkdir(parents=True)
        val_path.write_text(
            json.dumps({"readiness": {"status": "ready_for_acceptance"}}, indent=2) + "\n",
            encoding="utf-8",
        )
        # Seed so we have a status.json before review write.
        seed = _summary(
            wt3,
            "seed.json",
            {"completed_step": "execute", "completed_status": "complete"},
        )
        proc, _ = _write(update, root, wt3, seed, "--step", "execute")
        if proc.returncode != 0:
            raise AssertionError(f"fail: execute seed: {proc.stderr}")
        if (_status(wt3).get("artifacts") or {}).get("execution"):
            raise AssertionError("fail: execute must not set artifacts.execution")

        rev = _summary(
            wt3,
            "review.json",
            {"artifact": val_rel, "completed_status": "complete"},
        )
        proc, out = _write(update, root, wt3, rev, "--step", "review")
        if out.get("next_step") != "acceptance":
            raise AssertionError(f"fail: review + ready_for_acceptance → acceptance: {out}")
        if (_status(wt3).get("artifacts") or {}).get("review_validation") != val_rel:
            raise AssertionError("fail: review should set review_validation via artifact_key")

        # Blocked keeps position — does not apply default_next_step.
        wt4 = tmpdir / "blocked"
        wt4.mkdir()
        seed = _summary(
            wt4,
            "seed.json",
            {"completed_step": "spec", "artifact": "current-task/specs/a.json"},
        )
        _write(update, root, wt4, seed, "--step", "spec")
        before = (_status(wt4).get("task") or {}).get("next_step")
        blocked = _summary(
            wt4,
            "blocked.json",
            {
                "completed_status": "blocked",
                "open_questions": [{"question": "which CTA?"}],
            },
        )
        proc, out = _write(update, root, wt4, blocked, "--step", "subtasks")
        if proc.returncode != 0:
            raise AssertionError(f"fail: blocked write: {proc.stdout}{proc.stderr}")
        after = (_status(wt4).get("task") or {}).get("next_step")
        if after != before:
            raise AssertionError(f"fail: blocked must not advance next_step ({before} → {after})")
        if "completed_steps" in (_status(wt4).get("task") or {}):
            raise AssertionError("fail: status must not write completed_steps")

        # start has artifact_key null — must not invent artifacts.status.
        wt5 = tmpdir / "start"
        wt5.mkdir()
        s = _summary(
            wt5,
            "start.json",
            {
                "artifact": "current-task/status.json",
                "completed_status": "complete",
                "task": {"original": "demo", "type": "chore"},
            },
        )
        proc, out = _write(update, root, wt5, s, "--step", "start")
        if out.get("next_step") != "describe":
            raise AssertionError(f"fail: start → describe: {out}")
        if "status" in (_status(wt5).get("artifacts") or {}):
            raise AssertionError("fail: start must not set artifacts.status")

        # artifact_key comes from routing — every step with a key is declared.
        declared = {
            name: cfg.get("artifact_key")
            for name, cfg in steps.items()
            if cfg.get("artifact_key")
        }
        if declared.get("spec") != "spec" or declared.get("review") != "review_validation":
            raise AssertionError(f"fail: unexpected artifact_key map: {declared}")
        if declared.get("start") or declared.get("execute"):
            raise AssertionError("fail: start/execute must not declare an artifact_key")

    print("smoke-routing-write: ok")
