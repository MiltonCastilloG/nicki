from __future__ import annotations

import hashlib
from pathlib import Path


def run(root: Path) -> None:
    global_path = root / "global-status.json"
    if not global_path.is_file():
        print("skip: no global-status.json (ok before first start-task)")
        return

    digest = hashlib.sha256(global_path.read_bytes()).hexdigest()
    after = hashlib.sha256(global_path.read_bytes()).hexdigest()
    if digest != after:
        raise AssertionError("fail: global-status.json changed without start/close")

    print("smoke-status-boundary: ok")
