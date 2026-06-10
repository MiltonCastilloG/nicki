---
name: execute-plan
description: Execute a structured YAML plan inside a git worktree with strict path scope.
---

# Execute plan in worktree

This command launches a **subagent**, not inline parent work.

Launch the **execute-plan** subagent (`.cursor/agents/execute-plan.md`) in an isolated context via the Task tool or `/execute-plan` subagent invocation. Pass all user text after this command as the subagent prompt. Do not execute the workflow in the parent agent.

The subagent reads `.cursor/skills/execute-plan/SKILL.md`, `.cursor/skills/execute-plan/plan-format.md`, `.cursor/skills/execute-plan/execution-format.md`, and optional `current-task/current-task-context.yaml`. Tool permissions live in `.cursor/skills/execute-plan/SKILL.md` metadata — the subagent must not use any tool marked `false`.

## Examples

```
/execute-plan worktrees/hero-section @current-task/plans/hero-section.yaml
```

```
/execute-plan worktrees/footer-bug

meta:
  worktree: footer-bug
  generated_by: plan-maker
  task: "fix mobile nav link href"

title: Fix footer mobile link
constraints:
  - no-commit
  - no-new-deps

steps:
  - id: fix-link
    action: modify
    path: src/components/Footer/Footer.tsx
    do: >
      Update the mobile nav link href from "/about-us" to "/about".
      Use the existing Link component pattern; do not change styling.

  - id: verify
    action: verify
    commands:
      - npm run lint
      - npm test -- Footer
```
