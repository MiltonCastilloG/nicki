---
name: spec-maker
description: Analyze a task and write a YAML spec to current-task/specs/<slug>.yaml for /plan-maker.
---

# Spec maker

This command launches a **subagent**, not inline parent work.

Launch the **spec-maker** subagent (`.cursor/agents/spec-maker.md`) in an isolated context via the Task tool or `/spec-maker` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/spec-maker/SKILL.md`, `.cursor/skills/spec-maker/spec-format.md`, and optional `current-task/current-task-context.yaml`. Tool permissions live in `.cursor/skills/spec-maker/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

```
/spec-maker worktrees/hero-section redesign hero with headline, subcopy, and CTA using semantic Tailwind tokens
```

```
/spec-maker worktrees/footer-bug fix mobile nav link href from /about-us to /about
```

After the spec is written, run:

```
/plan-maker worktrees/hero-section @current-task/specs/hero-section.yaml
```
