---
name: review-triage
description: Triage review-execution output against current-task scope and write current-task/review-validations/rN-validation.yaml.
---

# Review triage

This command launches a **subagent**, not inline parent work.

Launch the **review-triage** subagent (`.cursor/agents/review-triage.md`) in an isolated context via the Task tool or `/review-triage` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/review-triage/SKILL.md`, `.cursor/skills/review-triage/validation-format.md`, `.cursor/skills/review-triage/review-guidance-format.md`, `.cursor/skills/next-step-spec/SKILL.md`, optional `current-task/current-task-context.yaml`, and the current-task spec/subtask/execution/review schemas. Tool permissions live in `.cursor/skills/review-triage/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

Auto-load review and current-task context from the worktree:

```
/review-triage worktrees/hero-section
```

Explicit review:

```
/review-triage worktrees/hero-section @current-task/reviews/hero-section.yaml
```

Output is the next sequential validation file:

```
current-task/review-validations/r1-validation.yaml
current-task/review-validations/r2-validation.yaml
current-task/review-validations/r3-validation.yaml
```

Important out-of-scope findings become spec YAML under `current-task/next-steps/`, directly consumable by `/subtask-maker`.

Invalid reviews can also produce rerun guidance:

```
current-task/review-inputs/r1-review.yaml
```
