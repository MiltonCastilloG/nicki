---
name: close-task
description: "Unregister global-status, delete worktree. After integrate + Nicki close confirm."
disable-model-invocation: true
---

# Close Task

[close-scope](../close-scope/SKILL.md) — unregister + delete worktree.

## When

- `integrate-task` done (or tail override approved)
- status-update recorded integrate (or override)
- User confirms worktree delete

## Inputs

| Input | Req |
|-------|-----|
| Worktree path | yes |
| `current-task/status.json` | preferred |

Missing path → ask.

## Tail gate

- `current-task/integrates/<slug>.yaml` exists (or `artifacts.integrate` resolves)

Missing integrate handoff → **block** unless user approves override. Then unregister → teardown.

## Checklist

```
- [ ] close-scope §1 — paths
- [ ] Tail gate (integrate or override)
- [ ] close-scope §2–3 — unregister + teardown
- [ ] Report
```

## Safety

- No close without Nicki confirm.
- No teardown before integrate handoff (or override).
- No `task: true`.
