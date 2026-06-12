# Sync format

**YAML only** — one compact artifact after commit + pre-push merge + feature-branch push (or blocked/partial).

Default path: `current-task/syncs/<slug>.yaml` under the task worktree scope root.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Sync identity and source context |
| `status` | Yes | `synced`, `partial`, or `blocked` |
| `commit` | Yes | Commit phase result |
| `pre_push_merge` | Yes | Base branch merge into feature before push |
| `remote` | If synced | Remote name and feature branch |
| `push` | If synced | Pushed commit SHA and upstream |
| `conflicts` | No | Conflict files and resolution status |
| `user_resolutions` | No | User inputs for conflict resolution |
| `blockers` | If blocked/partial | Why sync did not fully complete |

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug |
| `generated_by` | Yes | Always `sync-task` |
| `context` | No | Optional traceability path |
| `review` | No | Review path used for pre-sync gate |
| `validation` | No | Validation path used for pre-sync gate |

## `commit` sub-object

| Field | Required | Description |
|-------|----------|-------------|
| `status` | Yes | `committed`, `skipped`, or `blocked` |
| `sha` | If committed | Commit SHA |
| `branch` | If committed | Feature branch name |
| `message` | No | Commit message |
| `included_paths` | No | Paths staged |
| `excluded_paths` | No | Paths left unstaged |

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: sync-task
  review: current-task/reviews/hero-section.yaml
  validation: current-task/review-validations/r1-validation.yaml

status: synced

commit:
  status: committed
  sha: abc1234
  branch: feature/hero-section
  message: add hero section
  included_paths:
    - src/components/Hero/Hero.tsx
  excluded_paths: []

pre_push_merge:
  base: origin/main
  status: merged
  merge_commit: def5678

remote:
  name: origin
  branch: feature/hero-section

push:
  sha: abc1234
  upstream: origin/feature/hero-section

conflicts: []
user_resolutions: []
blockers: []
```

## Rules

- Write the artifact even when blocked or partial.
- `partial`: commit succeeded but push blocked, or merge blocked before push.
- Do not push `main` or `master`.
- Do not force push.
- Handoff is written after commit; it is not part of that commit.
