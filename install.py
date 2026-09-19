#!/usr/bin/env python3
"""Post-clone bootstrap for the Nicki repository (Cursor host adapter)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from install_common import (
    CURSOR_RULE_FRONTMATTER,
    REPO_ROOT,
    RUNTIME_ROOT,
    copy_fallback_used,
    link_dir,
    read_invocation_rule_body,
    reset_copy_fallback,
)

REGISTRY_PATH = REPO_ROOT / "nicki-workspace.yaml"
WORKTREES_DIR = REPO_ROOT / "worktrees"
CURSOR_DIR = REPO_ROOT / ".cursor"
CURSOR_AGENTS = CURSOR_DIR / "agents"
CURSOR_SKILLS = CURSOR_DIR / "skills"
CURSOR_RULE = CURSOR_DIR / "rules" / "nicki-default.mdc"

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


def verify_cursor_runtime() -> tuple[int, str, str]:
    """Repair committed .cursor/agents and .cursor/skills links into workflow-runtime/."""
    agent_mode = link_dir(RUNTIME_ROOT / "agents", CURSOR_AGENTS)
    skill_mode = link_dir(RUNTIME_ROOT / "skills", CURSOR_SKILLS)
    agent_count = len(list((RUNTIME_ROOT / "agents").glob("*.md")))
    return agent_count, agent_mode, skill_mode


def write_cursor_rule() -> None:
    """Generate .cursor/rules/nicki-default.mdc from the canonical rule + Cursor frontmatter."""
    body = read_invocation_rule_body()
    CURSOR_RULE.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_RULE.write_text(CURSOR_RULE_FRONTMATTER + body, encoding="utf-8")


def print_success(agent_count: int, agent_mode: str, skill_mode: str) -> None:
    if copy_fallback_used():
        print(
            "warning: directory symlinks unavailable; "
            "copied agents/skills — re-run install.py after runtime edits",
            file=sys.stderr,
        )
        print(f"Copied {agent_count} agents to .cursor/agents/ ({agent_mode})")
        print(f"Copied workflow-runtime/skills/ to .cursor/skills/ ({skill_mode})")
    else:
        print(f"Linked {agent_count} agents → .cursor/agents/ → workflow-runtime/agents/")
        print("Linked .cursor/skills/ → workflow-runtime/skills/")
    print(f"Wrote {CURSOR_RULE.relative_to(REPO_ROOT)} (opt-in Nicki routing)")
    print()
    print("Edit runtime under workflow-runtime/ (agents, skills, rules) — not under .cursor/.")
    print("Re-run python3 install.py only on a fresh clone or after changing")
    print("  workflow-runtime/rules/nicki-default.md (regenerates the Cursor rule).")
    if not copy_fallback_used():
        print("Agent/skill edits need no reinstall when using symlinks.")
    print()
    print("Next steps:")
    print("  1. Open this repository in Cursor.")
    print("  2. Invoke Nicki to start or continue a task:")
    print("       nicki start my-task")
    print("       nicki continue")


def main() -> None:
    reset_copy_fallback()
    check_git_prereq()
    ensure_worktrees()
    write_registry()
    agent_count, agent_mode, skill_mode = verify_cursor_runtime()
    write_cursor_rule()
    print_success(agent_count, agent_mode, skill_mode)


if __name__ == "__main__":
    main()
