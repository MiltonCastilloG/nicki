#!/usr/bin/env python3
"""Post-clone bootstrap for the Nicki repository."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = REPO_ROOT / "nicki-workspace.yaml"
WORKTREES_DIR = REPO_ROOT / "worktrees"

REGISTRY_STUB = """version: 1

projects:
  nicki:
    path: .
    git:
      default_branch: main
      remote: origin
    copy: []
    post_create: []
"""


def check_git_prereq() -> None:
    git = shutil.which("git")
    if git is None:
        print("error: git is required but was not found on PATH", file=sys.stderr)
        sys.exit(1)
    result = subprocess.run([git, "--version"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print("error: git is required but could not determine version", file=sys.stderr)
        sys.exit(1)
    print(result.stdout.strip())


def ensure_worktrees() -> None:
    if WORKTREES_DIR.exists():
        return
    WORKTREES_DIR.mkdir(parents=True)
    (WORKTREES_DIR / ".gitkeep").touch()


def write_registry() -> None:
    if REGISTRY_PATH.exists():
        print("nicki-workspace.yaml already exists — registry skipped")
        return
    REGISTRY_PATH.write_text(REGISTRY_STUB)


def print_success() -> None:
    print()
    print("Next steps:")
    print("  1. Open this repository in Cursor.")
    print("  2. Invoke Nicki to start or continue a task:")
    print("       nicki start my-task")
    print("       nicki continue")


def main() -> None:
    check_git_prereq()
    ensure_worktrees()
    write_registry()
    print_success()


if __name__ == "__main__":
    main()
