---
name: plan-maker
description: Read a YAML spec and write a YAML plan to current-task/plans/<slug>.yaml for /execute-plan.
---

# Plan maker

This command launches a **subagent**, not inline parent work.

Launch the **plan-maker** subagent (`.cursor/agents/plan-maker.md`) in an isolated context via the Task tool or `/plan-maker` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/plan-maker/SKILL.md`, `.cursor/skills/spec-maker/spec-format.md`, `.cursor/skills/execute-plan/plan-format.md`, and optional `current-task/current-task-context.yaml`. Tool permissions live in `.cursor/skills/plan-maker/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

```
/plan-maker worktrees/hero-section @current-task/specs/hero-section.yaml
```

```
/plan-maker worktrees/footer-bug @current-task/specs/footer-bug.yaml
```

After the plan is written, run:

```
/execute-plan worktrees/hero-section @current-task/plans/hero-section.yaml
```
