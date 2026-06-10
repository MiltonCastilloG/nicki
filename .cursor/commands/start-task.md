---
name: start-task
description: Pull main and create git worktrees for parallel task work under worktrees/.
---

# Start task worktrees

This command launches a **subagent**, not inline parent work.

Launch the **start-task** subagent (`.cursor/agents/start-task.md`) in an isolated context via the Task tool or `/start-task` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/start-task/SKILL.md` for the full workflow. Tool permissions live in `.cursor/skills/start-task/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

- `/start-task footer redesign, fix broken mobile nav`
- `/start-task chore: bump vitest`
- `/start-task redesign hero section`
