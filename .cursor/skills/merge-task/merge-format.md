# Merge format

Merges are the handoff from `/merge-task` after merging a pushed task branch into `main` or another target branch, or after blocking on conflicts. **YAML only**.

Store merge handoffs in the worktree under `current-task/merges/`:

```
current-task/merges/<slug>.yaml
```

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Merge identity and source context |
| `status` | Yes | `merged`, `conflicts_resolved`, `blocked`, or `no_op` |
| `merge` | Yes | Task/source branch and target branch |
| `conflicts` | Yes | Conflict files and resolution status |
| `user_resolutions` | Yes | Explicit user inputs used to resolve conflicts |
| `checks` | No | Commands run after merge |
| `blockers` | If blocked | Why merge did not finish |

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: merge-task
  context: current-task/current-task-context.yaml

status: conflicts_resolved

merge:
  source: feature/hero-section
  target_branch: main
  strategy: merge
  merge_commit: true

conflicts:
  - path: src/components/Hero/Hero.tsx
    status: resolved
    resolution_summary: Kept feature hero structure and accepted main branch import order.

user_resolutions:
  - path: src/components/Hero/Hero.tsx
    prompt: "Resolve conflict in Hero.tsx: keep feature hero body, main import order?"
    answer: "Yes, keep feature hero body and main import order."

checks:
  - command: git status --porcelain
    passed: true
    note: No unresolved conflict markers.

blockers: []
```

## Rules

- Write this artifact even when blocked.
- Record every conflicted file.
- Record every user decision used for resolution.
- Do not push; `/push-task` owns publishing task branches.
