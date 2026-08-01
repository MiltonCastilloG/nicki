---
name: close-task
description: "Unregister global-status, delete worktree. After integrate + Nicki close confirm."
disable-model-invocation: true
---

# Close Task

[close-scope](../close-scope/SKILL.md) — unregister + delete worktree.

## When

- `integrate-task` done
- status-update recorded integrate
- User confirms worktree delete

## Inputs

| Input | Req |
|-------|-----|
| Worktree path | yes |
| `current-task/status.json` | preferred |

Missing path → ask.

## Tail gate

- `current-task/integrates/<slug>.json` exists (or `artifacts.integrate` resolves)

Missing integrate handoff → **block**. Do not unregister or teardown.

## Checklist

```
- [ ] close-scope §1 — paths
- [ ] Tail gate (integrate handoff on disk)
- [ ] close-scope §2–3 — unregister + teardown
- [ ] Report
```

## Safety

- No close without Nicki confirm.
- No teardown before integrate handoff.
- No `task: true`.
