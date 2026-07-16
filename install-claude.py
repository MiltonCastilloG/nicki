#!/usr/bin/env python3
"""Claude Code host bootstrap for the Nicki repository."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = REPO_ROOT / ".cursor"
INVOCATION_RULE = RUNTIME_ROOT / "rules" / "nicki-default.mdc"
CLAUDE_DIR = REPO_ROOT / ".claude"
CLAUDE_AGENTS = CLAUDE_DIR / "agents"
CLAUDE_SKILLS = CLAUDE_DIR / "skills"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

_COPY_FALLBACK = False


def _same_link(dest: Path, src: Path) -> bool:
    if not dest.is_symlink():
        return False
    try:
        return dest.resolve() == src.resolve()
    except OSError:
        return False


def _remove_dest(dest: Path) -> None:
    if dest.is_symlink() or dest.is_file():
        dest.unlink()
    elif dest.is_dir():
        shutil.rmtree(dest)
    elif dest.exists():
        dest.unlink()


def link_dir(src: Path, dest: Path) -> str:
    """Create-or-repair a relative directory symlink. Returns 'link' or 'copy'."""
    global _COPY_FALLBACK
    if not src.is_dir():
        print(f"error: {src.relative_to(REPO_ROOT)}/ not found", file=sys.stderr)
        sys.exit(1)
    if _same_link(dest, src):
        return "link"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        _remove_dest(dest)
    rel = os.path.relpath(src, start=dest.parent)
    try:
        dest.symlink_to(rel, target_is_directory=True)
        return "link"
    except OSError:
        shutil.copytree(src, dest)
        _COPY_FALLBACK = True
        return "copy"


def install_agents() -> int:
    link_dir(RUNTIME_ROOT / "agents", CLAUDE_AGENTS)
    return len(list((RUNTIME_ROOT / "agents").glob("*.md")))


def install_skills() -> None:
    link_dir(RUNTIME_ROOT / "skills", CLAUDE_SKILLS)


def generate_claude_md() -> None:
    if not INVOCATION_RULE.is_file():
        print("error: .cursor/rules/nicki-default.mdc not found", file=sys.stderr)
        sys.exit(1)
    raw = INVOCATION_RULE.read_text()
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        body = parts[2].lstrip("\n") if len(parts) >= 3 else raw
    else:
        body = raw
    body = body.replace(
        "invoke a **fresh** Task (`subagent_type: nicki`) — never `resume`.",
        "invoke a **fresh** `nicki` subagent via the Agent tool — never resume a prior Nicki session.",
    )
    body = body.replace(
        "keep invoking a fresh Task on every",
        "keep invoking a fresh `nicki` subagent on every",
    )
    body = body.replace("**Never Task-spawn sheep**", "**Never spawn sheep**")
    body = body.replace(
        "That selector is the *only* context you may forward, If",
        "That selector is the *only* context you may forward. If",
    )
    CLAUDE_MD.write_text(body)


def print_success(agent_count: int) -> None:
    if _COPY_FALLBACK:
        print(
            "warning: directory symlinks unavailable; "
            "copied agents/skills — re-run install-claude.py after runtime edits",
            file=sys.stderr,
        )
        print(f"Copied {agent_count} agents to .claude/agents/")
        print("Copied .cursor/skills/ to .claude/skills/")
    else:
        print(f"Linked {agent_count} agents → .claude/agents/ → .cursor/agents/")
        print("Linked .claude/skills/ → .cursor/skills/")
    print("Wrote CLAUDE.md (opt-in Nicki routing)")
    print()
    print("Edit runtime under .cursor/ (agents, skills, rules) — not under .claude/.")
    print("Re-run python3 install-claude.py only on a fresh clone or after changing")
    print("  .cursor/rules/nicki-default.mdc (regenerates CLAUDE.md).")
    if not _COPY_FALLBACK:
        print("Agent/skill edits need no reinstall when using symlinks.")
    print()
    print("Next steps:")
    print("  1. If you have not already, run repository bootstrap: python3 install.py")
    print("  2. Open this repository in Claude Code.")
    print("  3. Invoke Nicki by name:")
    print("       nicki start my-task")
    print("       nicki continue")
    print()
    print(
        "Note: Claude Code does not replicate Cursor hooks; "
        "Nicki pipeline work uses the installed agents and skills only."
    )


def main() -> None:
    agent_count = install_agents()
    install_skills()
    generate_claude_md()
    print_success(agent_count)


if __name__ == "__main__":
    main()
