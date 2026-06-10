---
name: current-task-update
description: Update current-task/current-task-context.yaml from a compact workflow summary after a leaf step completes.
---

# Update current task context

This command launches a **subagent**, not inline parent work.

Launch the **current-task-update** subagent (`.cursor/agents/current-task-update.md`) in an isolated context via the Task tool or `/current-task-update` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/current-task-update/SKILL.md` and `.cursor/skills/current-task-update/current-task-context-format.md`. Tool permissions live in `.cursor/skills/current-task-update/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

```
/current-task-update worktrees/hero-section

worktree: worktrees/hero-section
completed_step: spec
completed_status: complete
artifact: current-task/specs/hero-section.yaml
next_step: subtasks
open_questions: []
summary: Spec captured requirements and acceptance criteria.
```

Output is:

```
current-task/current-task-context.yaml
```
