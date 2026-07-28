"""Readiness structure: retired surfaces stay retired, validation fixtures stay valid.

Readiness *behavior* (which gate each status allows or denies) is covered by
gates_matrix. This module only guards structure that a regression would restore.
"""

from __future__ import annotations

import json
from pathlib import Path

STATUSES = ("ready_for_acceptance", "fix_required", "blocked", "rerun_review")
FIXTURES = {
    "scope-only-validation.json": ("ready_for_acceptance", True),
    "verify-fail-validation.json": ("fix_required", False),
}


def _routing(root: Path) -> dict:
    return json.loads(
        (root / ".cursor/skills/nicki/routing.json").read_text(encoding="utf-8")
    )


def run(root: Path) -> None:
    failures: list[str] = []

    routing = _routing(root)
    declared = routing.get("readiness_routing") or {}
    for status in STATUSES:
        if status not in declared:
            failures.append(f"fail: routing readiness_routing missing {status}")
    for status, cfg in declared.items():
        if not (cfg or {}).get("route_step"):
            failures.append(f"fail: readiness_routing.{status} has no route_step")
    if "out_of_scope" in (routing.get("steps") or {}):
        failures.append("fail: out_of_scope step should be removed")
    if not failures:
        print(f"ok: readiness_routing declares {len(declared)} statuses, each with a route_step")

    for rel in (
        ".cursor/agents/out-of-scope.md",
        ".cursor/skills/readiness-from-review",
    ):
        if (root / rel).exists():
            failures.append(f"fail: {rel} should be removed")

    fixture_dir = root / ".cursor/skills/validation/scripts/fixtures"
    for name, (expected_status, deferred) in FIXTURES.items():
        path = fixture_dir / name
        if not path.is_file():
            failures.append(f"fail: missing validation fixture {name}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        got = ((data.get("readiness") or {}).get("status"))
        if got != expected_status:
            failures.append(f"fail: {name} readiness {got!r}, expected {expected_status!r}")
        if bool((data.get("readiness") or {}).get("deferred_scope")) is not deferred:
            failures.append(f"fail: {name} deferred_scope should be {deferred}")
        else:
            print(f"ok: {name} → {expected_status}")

    if failures:
        raise AssertionError("\n".join(failures))

    print("smoke-readiness-mapping: ok")
