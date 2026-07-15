from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tests.smoke._helpers import run_py, script


def run(root: Path) -> None:
    update = script(root, ".cursor/skills/current-task-update/scripts/update-status.py")
    validate = script(root, ".cursor/skills/nicki/scripts/validate-harness-stdout.py")

    with tempfile.TemporaryDirectory() as tmp:
        fixture = Path(tmp)

        yaml_ok = fixture / "summary-ok.yaml"
        yaml_ok.write_text(
            "\n".join(
                [
                    "completed_step: spec",
                    "next_step: subtasks",
                    "artifact: current-task/specs/foo.yaml",
                    "open_questions: []",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        proc = run_py(
            update, "--worktree", str(fixture), "--yaml-path", str(yaml_ok), cwd=root
        )
        if proc.returncode != 0:
            raise AssertionError(f"fail: valid summary: {proc.stderr}")
        out = json.loads(proc.stdout.strip())
        if out.get("written") is not True:
            raise AssertionError("fail: expected written true")
        if out.get("completed_step") != "spec" or out.get("next_step") != "subtasks":
            raise AssertionError("fail: unexpected step fields")

        val = run_py(
            validate,
            "--script",
            "update-status.py",
            "--stdout",
            proc.stdout.strip(),
            "--exit-code",
            "0",
            cwd=root,
        )
        if val.returncode != 0:
            raise AssertionError("fail: harness contract validation")

        status_path = fixture / "current-task/status.json"
        if not status_path.is_file():
            raise AssertionError("fail: status.json not written")

        yaml_acc = fixture / "summary-acc.yaml"
        yaml_acc.write_text(
            "\n".join(["completed_step: acceptance", "next_step: sync"]) + "\n",
            encoding="utf-8",
        )
        proc_acc = run_py(
            update, "--worktree", str(fixture), "--yaml-path", str(yaml_acc), cwd=root
        )
        if proc_acc.returncode != 0:
            raise AssertionError(f"fail: acceptance without artifact: {proc_acc.stderr}")
        if json.loads(proc_acc.stdout.strip()).get("written") is not True:
            raise AssertionError("fail: acceptance should write")

        status_before = status_path.read_text(encoding="utf-8")

        yaml_bad = fixture / "summary-bad.yaml"
        yaml_bad.write_text("completed_step: spec\n", encoding="utf-8")
        proc_bad = run_py(
            update, "--worktree", str(fixture), "--yaml-path", str(yaml_bad), cwd=root
        )
        if proc_bad.returncode != 1:
            raise AssertionError("fail: expected exit 1 for missing next_step")
        bad = json.loads(proc_bad.stdout.strip())
        if bad.get("written") is not False:
            raise AssertionError("fail: expected written false")
        if not any("next_step" in e for e in bad.get("errors", [])):
            raise AssertionError("fail: error should name next_step")
        if status_path.read_text(encoding="utf-8") != status_before:
            raise AssertionError("fail: status.json changed on input error")

    print("smoke-status-update: ok")
