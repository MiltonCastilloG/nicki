#!/usr/bin/env python3
"""Run Nicki harness and workflow smoke tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Allow `python3 test.py` from repo root without installing the package.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.smoke import (  # noqa: E402
    agent_tools,
    errors_append,
    git_tail,
    harness_failure,
    readiness_mapping,
    status_boundary,
    status_update,
)

MODULES = [
    ("agent_tools", agent_tools),
    ("harness_failure", harness_failure),
    ("errors_append", errors_append),
    ("status_update", status_update),
    ("status_boundary", status_boundary),
    ("readiness_mapping", readiness_mapping),
    ("git_tail", git_tail),
]


def main() -> int:
    for name, module in MODULES:
        print(f"==> {name}")
        module.run(ROOT)
    print("test: all smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
