#!/usr/bin/env python3
"""Append one errors.v1 failure entry to current-task/specs/errors.yaml."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def _slug(worktree: Path) -> str:
    name = worktree.name
    if "-" in name:
        return name.split("-", 1)[1]
    return name


def _now_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _unique_id(existing: list[dict], base: str) -> str:
    ids = {e.get("id") for e in existing}
    if base not in ids:
        return base
    n = 2
    while f"{base}-{n}" in ids:
        n += 1
    return f"{base}-{n}"


def append_failure(
    worktree: Path,
    *,
    script_route: str,
    input_data: object,
    expected_output: object,
    exit_code: int | None,
    stdout: str | None,
    stderr: str | None,
    validation_errors: list[str] | None,
) -> Path:
    path = worktree / "current-task/specs/errors.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if path.is_file():
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            data = loaded
    meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
    meta.setdefault("schema", "errors.v1")
    meta["worktree"] = _slug(worktree)
    failures = list(data.get("failures") or [])
    ts = _now_id()
    failures.append(
        {
            "id": _unique_id(failures, ts),
            "recorded_at": ts,
            "script_route": script_route,
            "input": input_data,
            "expected_output": expected_output,
            "actual": {
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "validation_errors": validation_errors,
            },
        }
    )
    path.write_text(
        yaml.safe_dump({"meta": meta, "failures": failures}, sort_keys=False),
        encoding="utf-8",
    )
    return path


def main() -> int:
    p = argparse.ArgumentParser(description="Append errors.v1 failure entry.")
    p.add_argument("--worktree", required=True)
    p.add_argument("--script-route", required=True)
    p.add_argument("--input", required=True, help="JSON input payload")
    p.add_argument("--expected-output", required=True, help="JSON expected contract")
    p.add_argument("--exit-code", type=int, default=None)
    p.add_argument("--stdout", default=None)
    p.add_argument("--stderr", default=None)
    p.add_argument("--validation-errors", default=None, help="JSON array of strings")
    args = p.parse_args()
    wt = Path(args.worktree).resolve()
    ve = json.loads(args.validation_errors) if args.validation_errors else None
    out = append_failure(
        wt,
        script_route=args.script_route,
        input_data=json.loads(args.input),
        expected_output=json.loads(args.expected_output),
        exit_code=args.exit_code,
        stdout=args.stdout,
        stderr=args.stderr,
        validation_errors=ve,
    )
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
