# Push format

**YAML only** — one compact artifact after pushing or blocking before push.

Default path: `current-task/pushes/<slug>.yaml` under the worktree scope root.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Push identity and source context |
| `status` | Yes | `pushed` or `blocked` |
| `remote` | If pushed | Remote name and branch |
| `commit` | If pushed | Commit SHA pushed |
| `pre_push_merge` | Yes | Base branch merge status before push |
| `conflicts` | No | Conflict files and resolution status |
| `user_resolutions` | No | Explicit user inputs used to resolve conflicts |
| `upstream` | No | Upstream tracking branch after push |
| `blockers` | If blocked | Why no push was performed |

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug |
| `generated_by` | Yes | Always `push-task` |
| `context` | No | Optional traceability path when the loading agent sets one |
| `commit_handoff` | No | Commit handoff path used as push source |

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: push-task
  commit_handoff: current-task/commits/hero-section.yaml

status: pushed

remote:
  name: origin
  branch: feature/hero-section

commit:
  sha: abc1234

pre_push_merge:
  base: origin/main
  status: merged
  merge_commit: def5678

conflicts: []
user_resolutions: []

upstream: origin/feature/hero-section

blockers: []
```

## Rules

- Write the artifact even when blocked.
- Merge the base branch before pushing.
- Do not create or amend commits except the required pre-push merge commit.
- Do not force push.
- Do not push `main` or `master`.
