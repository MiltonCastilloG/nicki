---
name: subtask-maker
description: Read a YAML spec and write a markdown subtask checklist to current-task/subtasks/<slug>.md for /execute-plan.
---

# Subtask maker

This command launches a **subagent**, not inline parent work.

Launch the **subtask-maker** subagent (`.cursor/agents/subtask-maker.md`) in an isolated context via the Task tool or `/subtask-maker` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/subtask-maker/SKILL.md`, `.cursor/skills/subtask-maker/subtask-format.md`, `.cursor/skills/spec-maker/spec-format.md`, and optional `current-task/current-task-context.yaml`. Tool permissions live in `.cursor/skills/subtask-maker/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

```
/subtask-maker worktrees/hero-section @current-task/specs/hero-section.yaml
```

```
/subtask-maker worktrees/footer-bug @current-task/specs/footer-bug.yaml
```

After the subtask list is written, run:

```
/execute-plan worktrees/hero-section @current-task/subtasks/hero-section.md
```
