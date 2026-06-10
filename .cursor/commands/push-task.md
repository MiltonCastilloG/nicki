---
name: push-task
description: Merge main into a committed current-task branch, resolve conflicts with user input, push, and write current-task/pushes/<slug>.yaml.
---

# Push task

This command launches a **subagent**, not inline parent work.

Launch the **push-task** subagent (`.cursor/agents/push-task.md`) in an isolated context via the Task tool or `/push-task` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/push-task/SKILL.md`, `.cursor/skills/push-task/push-format.md`, and `.cursor/skills/conflict-resolution/SKILL.md`. Tool permissions live in `.cursor/skills/push-task/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

Auto-load commit handoff, merge `main`, and push the branch:

```
/push-task worktrees/hero-section
```

Explicit commit handoff:

```
/push-task worktrees/hero-section @current-task/commits/hero-section.yaml
```

Output is:

```
current-task/pushes/hero-section.yaml
```
