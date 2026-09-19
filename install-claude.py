#!/usr/bin/env python3
"""Claude Code host bootstrap for the Nicki repository."""

from __future__ import annotations

import sys

from install_common import (
    CLAUDE_SUBSTITUTIONS,
    REPO_ROOT,
    RUNTIME_ROOT,
    apply_substitutions,
    copy_fallback_used,
    link_dir,
    read_invocation_rule_body,
    reset_copy_fallback,
)

CLAUDE_DIR = REPO_ROOT / ".claude"
CLAUDE_AGENTS = CLAUDE_DIR / "agents"
CLAUDE_SKILLS = CLAUDE_DIR / "skills"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"


def install_agents() -> int:
    link_dir(RUNTIME_ROOT / "agents", CLAUDE_AGENTS)
    return len(list((RUNTIME_ROOT / "agents").glob("*.md")))


def install_skills() -> None:
    link_dir(RUNTIME_ROOT / "skills", CLAUDE_SKILLS)


def generate_claude_md() -> None:
    body = apply_substitutions(read_invocation_rule_body(), CLAUDE_SUBSTITUTIONS)
    CLAUDE_MD.write_text(body, encoding="utf-8")


def print_success(agent_count: int) -> None:
    if copy_fallback_used():
        print(
            "warning: directory symlinks unavailable; "
            "copied agents/skills — re-run install-claude.py after runtime edits",
            file=sys.stderr,
        )
        print(f"Copied {agent_count} agents to .claude/agents/")
        print("Copied workflow-runtime/skills/ to .claude/skills/")
    else:
        print(f"Linked {agent_count} agents → .claude/agents/ → workflow-runtime/agents/")
        print("Linked .claude/skills/ → workflow-runtime/skills/")
    print("Wrote CLAUDE.md (opt-in Nicki routing)")
    print()
    print("Edit runtime under workflow-runtime/ (agents, skills, rules) — not under .claude/.")
    print("Re-run python3 install-claude.py only on a fresh clone or after changing")
    print("  workflow-runtime/rules/nicki-default.md (regenerates CLAUDE.md).")
    if not copy_fallback_used():
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
    reset_copy_fallback()
    agent_count = install_agents()
    install_skills()
    generate_claude_md()
    print_success(agent_count)


if __name__ == "__main__":
    main()
