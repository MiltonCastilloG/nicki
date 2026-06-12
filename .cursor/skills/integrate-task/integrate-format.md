# Integrate format

**YAML only** — one compact artifact after merge into target branch + push target branch (or blocked/partial).

Default path: `current-task/integrates/<slug>.yaml` in the **task worktree** (not the target checkout).

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Integrate identity and source context |
| `status` | Yes | `integrated`, `partial`, or `blocked` |
| `merge` | Yes | Merge phase result |
| `publish` | Yes | Push phase result |
| `conflicts` | No | Conflict files from merge |
| `user_resolutions` | No | User inputs for conflict resolution |
| `checks` | No | Post-merge or post-push commands |
| `blockers` | If blocked/partial | Why integrate did not fully complete |

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Task worktree slug |
| `generated_by` | Yes | Always `integrate-task` |
| `context` | No | Optional traceability path |
| `sync_handoff` | Yes | Path to sync handoff used as source |

## `merge` sub-object

| Field | Required | Description |
|-------|----------|-------------|
| `status` | Yes | `merged`, `conflicts_resolved`, `no_op`, or `blocked` |
| `source` | Yes | Feature branch merged |
| `target_branch` | Yes | Target branch (default `main`) |
| `merge_commit` | No | Whether merge commit was created |

## `publish` sub-object

| Field | Required | Description |
|-------|----------|-------------|
| `status` | Yes | `published` or `blocked` |
| `remote` | If published | Remote name |
| `branch` | If published | Target branch pushed |
| `sha` | No | HEAD SHA on target after push |

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: integrate-task
  sync_handoff: current-task/syncs/hero-section.yaml

status: integrated

merge:
  status: conflicts_resolved
  source: feature/hero-section
  target_branch: main
  merge_commit: true

publish:
  status: published
  remote: origin
  branch: main
  sha: fed9876

conflicts:
  - path: src/components/Hero/Hero.tsx
    status: resolved
    resolution_summary: Kept feature hero body and main import order.

user_resolutions:
  - path: src/components/Hero/Hero.tsx
    prompt: "Resolve conflict in Hero.tsx?"
    answer: "Keep feature hero body and main import order."

checks:
  - command: git status -sb
    passed: true

blockers: []
```

## Rules

- Write even when blocked or partial.
- `partial`: merge succeeded locally but publish push blocked.
- Handoff lives under task worktree `current-task/integrates/` — not target checkout.
- Push target branch only; do not push feature branch here.
- No force push.
