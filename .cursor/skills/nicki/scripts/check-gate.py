#!/usr/bin/env python3
"""Evaluate a Nicki pipeline step gate from status.json + routing.json.

Usage:
  check-gate.py --worktree worktrees/nicki-my-task --step sync
                [--user-confirmed] [--mode normal|adhoc|jump]

Stdout JSON: allowed, sheep, reason, user_confirm, next_step, artifact, mode.
Denials are never waived. `--mode` is echoed for write forwarding only
(adhoc/jump change how update-status.py moves position). See routing.json
`gate_policy`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from gate_utils import (
    MODES,
    allow,
    deny,
    expected_artifact_for,
    load_routing,
    load_status,
    next_step_for,
    resolve_worktree,
)
from gates import GATES


def _policy_denial(step: str, cfg: dict[str, Any], mode: str, user_confirmed: bool):
    """Routing-declared checks, run before any per-step gate."""
    adhoc_allowed = bool(cfg.get("adhoc_allowed"))

    if mode == "jump" and step in {"start", "close", "done"}:
        return deny(f"{step} cannot be a jump target")
    if mode == "adhoc" and not adhoc_allowed:
        return deny(f"{step} cannot run out of band (routing: adhoc_allowed is not set)")
    if cfg.get("user_confirm_required") and not user_confirmed:
        sentence = cfg.get("user_confirm") or f"confirm {step}"
        return deny(f"{step} gate: user consent required — {sentence}")
    return None


def evaluate(
    worktree: Path,
    step: str,
    *,
    user_confirmed: bool = False,
    mode: str = "normal",
) -> dict[str, Any]:
    result = _evaluate(worktree, step, user_confirmed=user_confirmed, mode=mode)
    result["mode"] = mode
    return result


def _evaluate(
    worktree: Path,
    step: str,
    *,
    user_confirmed: bool,
    mode: str,
) -> dict[str, Any]:
    routing = load_routing()
    steps = routing.get("steps") or {}
    if step not in steps:
        return deny(f"unknown step: {step}")

    step_cfg = steps[step]
    user_confirm = step_cfg.get("user_confirm") or False
    sheep = step_cfg.get("sheep")

    fail = _policy_denial(step, step_cfg, mode, user_confirmed)
    if fail:
        return fail

    if step == "start":
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

    gate_fn = GATES.get(step)
    if gate_fn:
        fail = gate_fn(status, worktree, user_confirmed)
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
        "--mode",
        default="normal",
        choices=MODES,
        help="Echoed for write forwarding; adhoc/jump are not gate waivers",
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
            mode=args.mode,
        )
    except Exception as exc:  # noqa: BLE001 — contract must always print
        result = deny(f"gate harness error: {exc}")
        result["mode"] = args.mode
    print(json.dumps(result))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    sys.exit(main())
