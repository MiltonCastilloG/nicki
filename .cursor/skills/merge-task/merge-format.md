# Merge format

**YAML only** — one compact artifact after merging a task branch into a target branch, or after blocking on conflicts.

Default path: `current-task/merges/<slug>.yaml` under the **task worktree** (not the target checkout).

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

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Task worktree slug |
| `generated_by` | Yes | Always `merge-task` |
| `context` | No | Optional traceability path when the loading agent sets one |

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: merge-task

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
- Record every conflicted file and every user decision used for resolution.
- Handoff file lives under task worktree `current-task/merges/` — not target repo checkout.
- Do not push the target branch from merge-task.
