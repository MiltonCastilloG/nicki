---
name: close-task
description: "Archive to docs/archive/<slug>/, unregister global-status, delete worktree. After integrate + status-update + Nicki close confirm."
disable-model-invocation: true
---

# Close Task

Two helpers. Order fixed.

| Helper | Role |
|--------|------|
| [task-archive](../task-archive/SKILL.md) | Write `docs/archive/<slug>/` — `report.yaml`, `report.md`, `story.md`; erase spec + subtasks |
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

Missing integrate handoff → **block** unless user approves override. Record override in `report.yaml` `meta.tail_override` + `report.md`. Then proceed archive → unregister → teardown.

Order fixed: `docs/archive/<slug>/` written → story copied → spec/subtasks erased → unregister → teardown.

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
- No teardown before `docs/archive/<slug>/report.yaml`, `report.md`, and `story.md` exist.
- No `task: true`.
- No full logs/diffs/transcripts in archive.
