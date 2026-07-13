#!/usr/bin/env python3
"""Claude Code host bootstrap for the Nicki repository."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
CURSOR_AGENTS = REPO_ROOT / ".cursor" / "agents"
CURSOR_SKILLS = REPO_ROOT / ".cursor" / "skills"
INVOCATION_RULE = REPO_ROOT / ".cursor" / "rules" / "nicki-default.mdc"
CLAUDE_DIR = REPO_ROOT / ".claude"
CLAUDE_AGENTS = CLAUDE_DIR / "agents"
CLAUDE_SKILLS = CLAUDE_DIR / "skills"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"


def install_agents() -> int:
    if not CURSOR_AGENTS.is_dir():
        print("error: .cursor/agents/ not found", file=sys.stderr)
        sys.exit(1)
    if CLAUDE_AGENTS.exists():
        shutil.rmtree(CLAUDE_AGENTS)
    CLAUDE_AGENTS.mkdir(parents=True)
    agents = sorted(CURSOR_AGENTS.glob("*.md"))
    for path in agents:
        shutil.copy2(path, CLAUDE_AGENTS / path.name)
    return len(agents)


def install_skills() -> None:
    if not CURSOR_SKILLS.is_dir():
        print("error: .cursor/skills/ not found", file=sys.stderr)
        sys.exit(1)
    if CLAUDE_SKILLS.exists():
        shutil.rmtree(CLAUDE_SKILLS)
    shutil.copytree(CURSOR_SKILLS, CLAUDE_SKILLS)


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
    print(f"Synced {agent_count} agents to .claude/agents/")
    print("Synced .cursor/skills/ to .claude/skills/")
    print("Wrote CLAUDE.md (opt-in Nicki routing)")
    print()
    print("Next steps:")
    print("  1. If you have not already, run repository bootstrap: python3 install.py")
    print("  2. Open this repository in Claude Code.")
    print("  3. Invoke Nicki by name:")
    print("       nicki start my-task")
    print("       nicki continue")
    print()
    print("Note: Claude Code does not replicate Cursor hooks; Nicki pipeline work uses the installed agents and skills only.")


def main() -> None:
    agent_count = install_agents()
    install_skills()
    generate_claude_md()
    print_success(agent_count)


if __name__ == "__main__":
    main()
