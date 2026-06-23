#!/usr/bin/env bash
# Regenerate nicki.code-workspace from worktrees/ — run after add/remove worktrees.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(".")
folders = [{"name": "Shared", "path": "."}]

worktrees = root / "worktrees"
if worktrees.is_dir():
    for p in sorted(worktrees.iterdir()):
        if p.is_dir() and (p / ".git").exists():
            folders.append({"name": p.name, "path": f"worktrees/{p.name}"})

workspace = {
    "folders": folders,
    "settings": {
        "git.autoRepositoryDetection": True,
    },
}

out = root / "nicki.code-workspace"
out.write_text(json.dumps(workspace, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {out} — Shared + {len(folders) - 1} worktree(s)")
PY
