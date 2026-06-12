# Publish format

**YAML only** — one compact artifact after user-confirmed push of merged target branch.

Default path: `current-task/publishes/<slug>.yaml` in the **task worktree**.

## Fields

| Field | Req | Description |
|-------|-----|-------------|
| `meta` | yes | Identity + source context |
| `status` | yes | `published` or `blocked` |
| `target` | if published | Remote + branch pushed |
| `merge` | yes | Source merge handoff path |
| `commit` | no | HEAD SHA on target after push |
| `checks` | no | Post-push commands |
| `blockers` | if blocked | Why no push |

## `meta`

| Field | Req | Description |
|-------|-----|-------------|
| `worktree` | yes | Task worktree slug |
| `generated_by` | yes | Always `publish-task` |
| `context` | no | Optional traceability path when the loading agent sets one |
| `merge_handoff` | yes | Merge handoff path used as publish source |

## Example

```yaml
meta:
  worktree: hero-section
  generated_by: publish-task
  merge_handoff: current-task/merges/hero-section.yaml

status: published

target:
  remote: origin
  branch: main

merge:
  source: feature/hero-section
  target_branch: main

commit:
  sha: abc1234

checks:
  - command: git status -sb
    passed: true

blockers: []
```

## Rules

- Write even when blocked
- Handoff lives in task worktree — not target checkout `current-task/`
- Push target branch only; task branch already pushed earlier
- No force push
