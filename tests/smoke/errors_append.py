from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from tests.smoke._helpers import rm_tree, run_py, script


def run(root: Path) -> None:
    append = script(root, ".cursor/skills/errors-recording/scripts/append-error.py")
    fixture = root / "tests/fixtures/smoke-worktree"
    errors = fixture / "current-task/specs/errors.yaml"
    archive_dir = fixture / "docs/archive/sheep-fallback"

    rm_tree(fixture)
    (fixture / "current-task/specs").mkdir(parents=True)

    proc = run_py(
        append,
        "--worktree",
        str(fixture),
        "--script-route",
        ".cursor/skills/nicki/scripts/check-gate.py",
        "--input",
        '{"argv":["--worktree","worktrees/nicki-sheep-fallback","--step","execute"]}',
        "--expected-output",
        '{"required_fields":["allowed","sheep","reason"]}',
        "--exit-code",
        "1",
        "--stdout",
        '{"allowed":false}',
        "--validation-errors",
        '["missing field: reason"]',
        cwd=root,
    )
    if proc.returncode != 0:
        raise AssertionError(f"fail: first append: {proc.stderr}")

    if not errors.is_file():
        raise AssertionError("fail: errors.yaml missing after first append")

    data = yaml.safe_load(errors.read_text(encoding="utf-8"))
    if len(data["failures"]) != 1:
        raise AssertionError("fail: expected one failure entry")
    f = data["failures"][0]
    for key in ("id", "recorded_at", "script_route", "input", "expected_output", "actual"):
        if key not in f:
            raise AssertionError(f"fail: missing key {key} in failure entry")
    a = f["actual"]
    for key in ("exit_code", "stdout", "stderr", "validation_errors"):
        if key not in a:
            raise AssertionError(f"fail: missing actual.{key}")
    print("ok")

    proc2 = run_py(
        append,
        "--worktree",
        str(fixture),
        "--script-route",
        ".cursor/skills/current-task-update/scripts/update-status.py",
        "--input",
        '{"argv":["--worktree","worktrees/foo"]}',
        "--expected-output",
        '{"required_fields":["written"]}',
        "--exit-code",
        "1",
        "--stdout",
        "not json",
        "--validation-errors",
        '["stdout is not valid JSON"]',
        cwd=root,
    )
    if proc2.returncode != 0:
        raise AssertionError(f"fail: second append: {proc2.stderr}")

    data = yaml.safe_load(errors.read_text(encoding="utf-8"))
    if len(data["failures"]) != 2:
        raise AssertionError("fail: expected two failure entries")
    if len({f["id"] for f in data["failures"]}) != 2:
        raise AssertionError("fail: expected unique failure ids")

    contract = {
        "worktree": "sheep-fallback",
        "completed_step": "execute",
        "completed_status": "blocked",
        "artifact": "current-task/specs/errors.yaml",
        "next_step": "execute",
        "open_questions": [],
        "summary": "Recorded harness failure.",
    }
    required = [
        "worktree",
        "completed_step",
        "completed_status",
        "artifact",
        "next_step",
        "open_questions",
        "summary",
    ]
    if not all(k in contract for k in required):
        raise AssertionError("fail: sheep return contract shape")

    rm_tree(archive_dir)
    archive_dir.mkdir(parents=True)
    shutil.copy(errors, archive_dir / "errors.yaml")
    archived = yaml.safe_load((archive_dir / "errors.yaml").read_text(encoding="utf-8"))
    if len(archived["failures"]) != 2:
        raise AssertionError("fail: archive copy should preserve failures")

    no_err = root / "tests/fixtures/no-errors-worktree"
    rm_tree(no_err)
    (no_err / "current-task/specs").mkdir(parents=True)
    if (no_err / "current-task/specs/errors.yaml").exists():
        raise AssertionError("fail: no-errors fixture should not have errors.yaml")

    print("smoke-errors-append: ok")
