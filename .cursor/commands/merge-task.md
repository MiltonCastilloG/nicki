---
name: merge-task
description: Merge a pushed current-task branch into main, ask for every conflict resolution, and write current-task/merges/<slug>.yaml.
---

# Merge task

This command launches a **subagent**, not inline parent work.

Launch the **merge-task** subagent (`.cursor/agents/merge-task.md`) in an isolated context via the Task tool or `/merge-task` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/merge-task/SKILL.md`, `.cursor/skills/merge-task/merge-format.md`, and `.cursor/skills/conflict-resolution/SKILL.md`. Tool permissions live in `.cursor/skills/merge-task/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

Merge the pushed task branch into `main`:

```
/merge-task worktrees/hero-section
```

Merge into a specific target branch:

```
/merge-task worktrees/hero-section target: main
```

Output is:

```
current-task/merges/hero-section.yaml
```

Conflicts are resolved only from explicit user input.
