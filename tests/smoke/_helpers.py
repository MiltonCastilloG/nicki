from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def script(root: Path, rel: str) -> Path:
    return root / rel


def run_py(path: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path), *args],
        cwd=cwd or path.parent,
        capture_output=True,
        text=True,
    )


def json_line(stdout: str) -> dict:
    line = stdout.strip().splitlines()[-1]
    return json.loads(line)


def run_hook(hook: Path, payload: dict) -> dict:
    proc = subprocess.run(
        [str(hook)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def rm_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def assert_contains(path: Path, needle: str, label: str | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        raise AssertionError(f"fail: {label or needle} missing in {path}")


def assert_missing(path: Path, label: str | None = None) -> None:
    if path.exists():
        raise AssertionError(f"fail: {label or path} should not exist")
