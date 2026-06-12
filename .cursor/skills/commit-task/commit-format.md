# Commit format

**YAML only** — one compact artifact after creating a local git commit or blocking before commit.

Default path: `current-task/commits/<slug>.yaml` under the worktree scope root.

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

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug |
| `generated_by` | Yes | Always `commit-task` |
| `context` | No | Optional traceability path when the loading agent sets one |
| `review` | No | Review path used for pre-commit check |
| `triage` | No | Validation path used for pre-commit check |

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: commit-task
  review: current-task/reviews/hero-section.yaml
  triage: current-task/review-validations/r1-validation.yaml

status: committed

commit:
  sha: abc1234
  branch: feature/hero-section
  message: |
    good dog: add hero section

included_paths:
  - src/components/Hero/Hero.tsx

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
- The handoff itself is written after the commit and is not expected to be part of that commit.
