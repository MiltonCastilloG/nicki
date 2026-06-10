---
name: execute-plan
description: Execute a markdown subtask checklist inside a git worktree with strict path scope.
---

# Execute subtask checklist

This command launches a **subagent**, not inline parent work.

Launch the **execute-plan** subagent (`.cursor/agents/execute-plan.md`) in an isolated context via the Task tool or `/execute-plan` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/execute-plan/SKILL.md`, `.cursor/skills/subtask-maker/subtask-format.md`, `.cursor/skills/execute-plan/execution-format.md`, and optional `current-task/current-task-context.yaml`. Tool permissions live in `.cursor/skills/execute-plan/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

```
/execute-plan worktrees/hero-section @current-task/subtasks/hero-section.md
```

```
/execute-plan worktrees/footer-bug @current-task/subtasks/footer-bug.md
```

Output includes code changes under the worktree and:

```
current-task/executions/<slug>.yaml
```

The subtask file is updated in place — each completed line becomes `- [x]`.

Next step:

```
/review-execution worktrees/hero-section
```
