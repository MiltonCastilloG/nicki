---
name: commit-task
description: Create a local git commit for a completed current-task worktree and write current-task/commits/<slug>.yaml.
---

# Commit task

This command launches a **subagent**, not inline parent work.

Launch the **commit-task** subagent (`.cursor/agents/commit-task.md`) in an isolated context via the Task tool or `/commit-task` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/commit-task/SKILL.md` and `.cursor/skills/commit-task/commit-format.md`. Tool permissions live in `.cursor/skills/commit-task/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

Auto-load current-task context and commit task changes:

```
/commit-task worktrees/hero-section
```

With an explicit message hint:

```
/commit-task worktrees/hero-section message: Add hero section workflow
```

After the commit is written, run:

```
/push-task worktrees/hero-section @current-task/commits/hero-section.yaml
```
