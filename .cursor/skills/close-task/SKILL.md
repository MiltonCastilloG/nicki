---
name: close-task
description: "Archive task, unregister global-status, delete worktree. After integrate + status-update + Nicki close confirm."
disable-model-invocation: true
---

# Close Task

Two helpers. Order fixed.

| Helper | Role |
|--------|------|
| [task-archive](../task-archive/SKILL.md) | `summary.yaml` + `report.md` |
| [close-scope](../close-scope/SKILL.md) | unregister + delete worktree |

## When

- `integrate-task` done (or tail override approved)
- `sheep-status` recorded integrate (or override)
- User confirms archive and worktree delete

## Inputs

| Input | Req |
|-------|-----|
| Worktree path | yes |
| `current-task/status.json` | preferred |

Missing path → ask.

## Tail gate

Before archive, verify via `status.json` `artifacts` + disk:

- `current-task/integrates/<slug>.yaml` exists (or `artifacts.integrate` resolves)

Missing integrate handoff → **block** unless user approves override. Record override in `summary.yaml` `meta.tail_override` + `report.md`. Then proceed archive → unregister → teardown.

Order fixed: archive files first, unregister, `rm -rf` worktree last.

## Checklist

```
- [ ] close-scope §1 — paths
- [ ] Tail gate (integrate or override)
- [ ] task-archive
- [ ] close-scope §2–3 — unregister + teardown
- [ ] Report
```

## Safety

- No close without Nicki confirm.
- No teardown before archive files exist.
- No `task: true`.
- No full logs/diffs/transcripts in archive.
