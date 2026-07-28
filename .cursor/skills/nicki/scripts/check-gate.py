#!/usr/bin/env python3
"""Evaluate a Nicki pipeline step gate from status.json + routing.json.

Usage:
  check-gate.py --worktree worktrees/nicki-my-task --step sync [--user-confirmed] [--override]

Stdout JSON: allowed, sheep, reason, user_confirm
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from gate_utils import (
    BLOCKED_READINESS,
    ArtifactParseError,
    allow,
    deny,
    expected_artifact_for,
    load_routing,
    load_status,
    next_step_for,
    readiness,
    resolve_worktree,
)
from gates import GATES, READINESS_STEPS, gate_start


def evaluate(
    worktree: Path,
    step: str,
    *,
    user_confirmed: bool = False,
    override: bool = False,
) -> dict[str, Any]:
    routing = load_routing()
    steps = routing.get("steps") or {}
    if step not in steps:
        return deny(f"unknown step: {step}")

    step_cfg = steps[step]
    user_confirm = step_cfg.get("user_confirm") or False
    sheep = step_cfg.get("sheep")

    if step == "start":
        fail = gate_start({}, worktree, user_confirmed, override)
        if fail:
            return fail
        return allow(
            sheep,
            user_confirm,
            next_step=next_step_for(step, {}),
            artifact=expected_artifact_for(step, {}),
        )

    try:
        status = load_status(worktree)
    except FileNotFoundError as exc:
        return deny(str(exc))

    if step in READINESS_STEPS and step != "review":
        try:
            rs = readiness(status, worktree)
        except ArtifactParseError as exc:
            return deny(f"readiness parse error: {exc}")
        rr = (routing.get("readiness_routing") or {}).get(rs or "")
        if rs and rr.get("sync_blocked") and step == "sync" and rs in BLOCKED_READINESS:
            return deny(f"sync gate: readiness routing blocks sync ({rs})")

    gate_fn = GATES.get(step)
    if gate_fn:
        fail = gate_fn(status, worktree, user_confirmed, override)
        if fail:
            fail["user_confirm"] = user_confirm
            return fail

    return allow(
        sheep,
        user_confirm,
        next_step=next_step_for(step, status),
        artifact=expected_artifact_for(step, status),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Nicki pipeline step gate check.")
    parser.add_argument("--worktree", required=True, help="Task worktree path")
    parser.add_argument("--step", required=True, help="Pipeline step name")
    parser.add_argument(
        "--user-confirmed",
        action="store_true",
        help="User confirmed git/close step in chat",
    )
    parser.add_argument(
        "--override",
        action="store_true",
        help="User override for sync without acceptance",
    )
    parser.add_argument(
        "--smoke-contract-fail",
        action="store_true",
        help="Smoke/review only: emit contract-invalid stdout and exit 1",
    )
    args = parser.parse_args()

    if args.smoke_contract_fail:
        print(json.dumps({"allowed": False}))
        return 1

    try:
        result = evaluate(
            resolve_worktree(args.worktree),
            args.step,
            user_confirmed=args.user_confirmed,
            override=args.override,
        )
    except Exception as exc:  # noqa: BLE001 — contract must always print
        result = deny(f"gate harness error: {exc}")
    print(json.dumps(result))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    sys.exit(main())
