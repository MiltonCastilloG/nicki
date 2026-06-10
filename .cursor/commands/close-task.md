---
name: close-task
description: Archive completed current-task context to task-archive/<slug>/summary.yaml and delete current-task/.
---

# Close task

This command launches a **subagent**, not inline parent work.

Launch the **close-task** subagent (`.cursor/agents/close-task.md`) in an isolated context via the Task tool or `/close-task` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/close-task/SKILL.md` and `.cursor/skills/close-task/archive-format.md`. Tool permissions live in `.cursor/skills/close-task/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

```
/close-task worktrees/hero-section
```

Output is:

```
task-archive/hero-section/summary.yaml
```

After writing the archive, the subagent deletes:

```
worktrees/hero-section/current-task/
```
