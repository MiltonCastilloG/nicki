---
name: close-task
description: "Archive task, unregister global-status, delete worktree. After merge + status-update + Nicki close confirm."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: close-task
---

# Close Task

Two helpers. Order fixed.

| Helper | Role |
|--------|------|
| [task-archive](../task-archive/SKILL.md) | `summary.yaml` + `report.md` |
| [close-scope](../close-scope/SKILL.md) | unregister + delete worktree |

## When

- `publish-task` done (or tail override approved)
- `current-task-update` recorded publish (or override)
- User yes to `Time for the feedback woof! Want?`

## Inputs

| Input | Req |
|-------|-----|
| Worktree path | yes |
| `current-task/status.json` | preferred |

Missing path → ask.

## Tail gate

Before archive, verify via `status.json` `artifacts` + disk:

- `current-task/merges/<slug>.yaml` exists (or `artifacts.merge` resolves)
- `current-task/publishes/<slug>.yaml` exists (or `artifacts.publish` resolves)

Missing both handoffs → **block** unless user approves override. Record override in `summary.yaml` `meta.tail_override` + `report.md` (caveman). Then proceed archive → unregister → teardown.

Order fixed: archive files first, unregister, `rm -rf` worktree last.

## Checklist

```
- [ ] close-scope §1 — paths
- [ ] Tail gate (merge + publish or override)
- [ ] task-archive
- [ ] close-scope §2–3 — unregister + teardown
- [ ] Report
```

## Safety

- No close without Nicki confirm.
- No teardown before archive files exist.
- No `task: true`.
- No full logs/diffs/transcripts in archive.
