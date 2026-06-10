---
name: review-execution
description: Review post-execute work against spec, plan, and execution handoff; write current-task/reviews/<slug>.yaml.
---

# Review execution in worktree

This command launches a **subagent**, not inline parent work.

Launch the **review-execution** subagent (`.cursor/agents/review-execution.md`) in an isolated context via the Task tool or `/review-execution` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/review-execution/SKILL.md`, `.cursor/skills/review-execution/review-format.md`, `.cursor/skills/spec-maker/spec-format.md`, `.cursor/skills/execute-plan/plan-format.md`, `.cursor/skills/execute-plan/execution-format.md`, optional `.cursor/skills/review-triage/review-guidance-format.md`, and optional `current-task/current-task-context.yaml`. Tool permissions live in `.cursor/skills/review-execution/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

Auto-load task context, spec, plan, and execution handoff from the worktree:

```
/review-execution worktrees/hero-section
```

Explicit spec, plan, and execution references:

```
/review-execution worktrees/hero-section @current-task/specs/hero-section.yaml @current-task/plans/hero-section.yaml @current-task/executions/hero-section.yaml
```

With review guidance from `/review-triage`:

```
/review-execution worktrees/hero-section @current-task/review-inputs/r1-review.yaml
```

Output is `current-task/reviews/<slug>.yaml` with exactly `approved` and `content`.
