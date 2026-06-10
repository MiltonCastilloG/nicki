# Commit format

Commits are the handoff from `/commit-task` to `/push-task`. **YAML only** — write one compact artifact after creating a local git commit or blocking before commit.

Store commit handoffs in the worktree under `current-task/commits/`:

```
current-task/commits/<slug>.yaml
```

All agent YAML artifacts for the active task live under `current-task/`:

```
current-task/
  current-task-context.yaml
  specs/<slug>.yaml
  plans/<slug>.yaml
  executions/<slug>.yaml
  reviews/<slug>.yaml
  review-validations/rN-validation.yaml
  review-inputs/rN-review.yaml
  next-steps/*.yaml
  merges/<slug>.yaml
  commits/<slug>.yaml
  pushes/<slug>.yaml
```

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Commit identity and source context |
| `status` | Yes | `committed` or `blocked` |
| `commit` | If committed | Commit SHA, branch, and message |
| `included_paths` | Yes | Paths staged for commit |
| `excluded_paths` | No | Paths intentionally not committed |
| `checks` | No | Verification or pre-commit evidence |
| `blockers` | If blocked | Why no commit was created |

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: commit-task
  context: current-task/current-task-context.yaml
  review: current-task/reviews/hero-section.yaml
  triage: current-task/review-validations/r1-validation.yaml
  merge: current-task/merges/hero-section.yaml

status: committed

commit:
  sha: abc1234
  branch: feature/hero-section
  message: |
    Add hero section workflow.

included_paths:
  - src/components/Hero/Hero.tsx
  - current-task/specs/hero-section.yaml

excluded_paths: []

checks:
  - command: git status --porcelain
    passed: true
    note: Only post-commit handoff metadata remains after commit.

blockers: []
```

## Rules

- Write the artifact even when blocked.
- Do not include secrets or ignored files.
- Record excluded paths when user changes are intentionally left unstaged.
- The commit handoff itself is written after the commit and is not expected to be part of that commit.
- Do not record push state here; `/push-task` owns that.
