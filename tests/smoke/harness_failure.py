from __future__ import annotations

import json
from pathlib import Path

import yaml

from tests.smoke._helpers import json_line, run_py, script


def run(root: Path) -> None:
    gate = script(root, ".cursor/skills/nicki/scripts/check-gate.py")
    validate = script(root, ".cursor/skills/nicki/scripts/validate-harness-stdout.py")
    append = script(root, ".cursor/skills/errors-recording/scripts/append-error.py")
    step = "acceptance"
    script_route = ".cursor/skills/nicki/scripts/check-gate.py"
    errors_yaml = root / "current-task/specs/errors.yaml"

    gate_proc = run_py(
        gate,
        "--smoke-contract-fail",
        "--worktree",
        ".",
        "--step",
        step,
        cwd=root,
    )
    if gate_proc.returncode != 1:
        raise AssertionError("fail: expected check-gate exit 1")
    if not gate_proc.stdout.strip():
        raise AssertionError("fail: empty stdout")

    val_proc = run_py(
        validate,
        "--script",
        "check-gate.py",
        "--stdout",
        gate_proc.stdout.strip(),
        "--exit-code",
        str(gate_proc.returncode),
        cwd=root,
    )
    if val_proc.returncode != 1:
        raise AssertionError("fail: validator should reject contract")

    val_json = json_line(val_proc.stdout)
    if val_json.get("valid") is not False or not val_json.get("errors"):
        raise AssertionError(f"fail: expected contract-invalid, got {val_json}")
    print("contract-invalid:", val_json["errors"])

    deny_proc = run_py(
        gate,
        "--worktree",
        "/nonexistent-wt",
        "--step",
        step,
        cwd=root,
    )
    if deny_proc.returncode != 1:
        raise AssertionError("fail: expected gate deny exit 1")

    deny_val = run_py(
        validate,
        "--script",
        "check-gate.py",
        "--stdout",
        deny_proc.stdout.strip(),
        "--exit-code",
        str(deny_proc.returncode),
        cwd=root,
    )
    deny_json = json_line(deny_val.stdout)
    if deny_json.get("valid") is not True:
        raise AssertionError("fail: gate-deny should have valid contract")
    print("gate-deny-valid-contract: ok")

    input_json = json.dumps(
        {
            "argv": [
                "--worktree",
                "worktrees/nicki-sheep-fallback",
                "--step",
                step,
                "--smoke-contract-fail",
            ]
        }
    )
    validation_json = json.dumps(val_json["errors"])

    append_proc = run_py(
        append,
        "--worktree",
        str(root),
        "--script-route",
        script_route,
        "--input",
        input_json,
        "--expected-output",
        '{"required_fields":["allowed","sheep","reason"]}',
        "--exit-code",
        str(gate_proc.returncode),
        "--stdout",
        gate_proc.stdout.strip(),
        "--validation-errors",
        validation_json,
        cwd=root,
    )
    if append_proc.returncode != 0:
        raise AssertionError(f"fail: append-error failed: {append_proc.stderr}")

    if not errors_yaml.is_file():
        raise AssertionError("fail: errors.yaml not created")

    data = yaml.safe_load(errors_yaml.read_text(encoding="utf-8"))
    assert data["meta"]["schema"] == "errors.v1"
    assert len(data["failures"]) >= 1
    last = data["failures"][-1]
    assert last["script_route"] == script_route
    assert last["actual"]["exit_code"] == 1
    assert "missing field" in " ".join(last["actual"]["validation_errors"] or [])
    print("errors.yaml harness entry: ok")
    print("smoke-harness-failure: ok")
