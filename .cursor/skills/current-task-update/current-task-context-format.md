# Current task context format

`current-task/current-task-context.yaml` is the canonical task-local workflow context. It stores task identity, worktree scope, artifact paths, the current workflow step, blockers, and history so Nicki can orchestrate the leaf agents without relying on chat memory.

The file lives inside the worktree:

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
  commits/<slug>.yaml
  pushes/<slug>.yaml
  merges/<slug>.yaml
```

`/current-task-update` is the only writer for this file. Nicki and leaf agents may read it, and leaf artifacts should reference it with `meta.context` when their schema allows metadata.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Schema and writer metadata |
| `task` | Yes | Task identity and workflow step pointers |
| `git` | No | Branch/base information when known |
| `scope` | Yes | Worktree slug and path |
| `artifacts` | Yes | Known task artifact paths |
| `constraints` | No | Constraints inherited by downstream agents |
| `open_questions` | Yes | Blockers or user decisions needed before continuing |
| `history` | Yes | Append-only workflow events |

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `schema` | Yes | Always `current-task-context.v1` |
| `generated_by` | Yes | Always `current-task-update` |
| `updated_by` | Yes | Always `current-task-update` |

## `task`

| Field | Required | Description |
|-------|----------|-------------|
| `slug` | Yes | Worktree folder slug, e.g. `hero-section` |
| `title` | No | Short task title |
| `original` | Yes | Original user task text |
| `type` | No | `feature`, `fix`, `chore`, `docs`, `refactor`, `test`, or `perf` |
| `current_step` | Yes | Step Nicki is preparing or just handed off |
| `next_step` | Yes | Next step Nicki should propose |
| `last_completed_step` | No | Latest completed step |

Do not add a broad task-level `state` enum. `current_step`, `next_step`, `last_completed_step`, `open_questions`, and `history[].status` are the source of truth.

Step values:

- `start`
- `spec`
- `plan`
- `execute`
- `review`
- `triage`
- `fix`
- `commit`
- `push`
- `merge`
- `close`
- `done`

## `scope`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug |
| `worktree_path` | Yes | Repo-relative or absolute worktree path |

The command worktree path remains the hard scope source of truth. If an existing context file has a conflicting `scope.worktree_path`, stop and ask before writing.

## `artifacts`

Use paths relative to the worktree root.

| Field | Required | Description |
|-------|----------|-------------|
| `context` | Yes | `current-task/current-task-context.yaml` |
| `spec` | No | `current-task/specs/<slug>.yaml` |
| `plan` | No | `current-task/plans/<slug>.yaml` |
| `execution` | No | `current-task/executions/<slug>.yaml` |
| `review` | No | `current-task/reviews/<slug>.yaml` |
| `review_validation` | No | Latest `current-task/review-validations/rN-validation.yaml` |
| `review_input` | No | Latest `current-task/review-inputs/rN-review.yaml` |
| `next_steps` | No | List of follow-up specs under `current-task/next-steps/` |
| `commit` | No | `current-task/commits/<slug>.yaml` |
| `push` | No | `current-task/pushes/<slug>.yaml` |
| `merge` | No | `current-task/merges/<slug>.yaml` |
| `archive` | No | Root archive path, e.g. `task-archive/<slug>/summary.yaml` |

## `open_questions`

Use an empty list when Nicki can continue safely.

```yaml
open_questions: []
```

When blocked, keep entries compact and actionable:

```yaml
open_questions:
  - step: plan
    question: "Should the CTA link to /contact or /demo?"
    blocks_next_step: true
```

## `history`

Append one event per workflow result.

| Field | Required | Description |
|-------|----------|-------------|
| `step` | Yes | Step value |
| `status` | Yes | `complete`, `blocked`, `failed`, or `skipped` |
| `artifact` | No | Primary artifact produced |
| `summary` | Yes | One-line result summary |

## YAML example

```yaml
meta:
  schema: current-task-context.v1
  generated_by: current-task-update
  updated_by: current-task-update

task:
  slug: hero-section
  title: Hero section redesign
  original: "redesign hero section with headline, subcopy, CTA"
  type: feature
  current_step: spec
  next_step: plan
  last_completed_step: start

git:
  branch: feature/hero-section
  base: main

scope:
  worktree: hero-section
  worktree_path: worktrees/hero-section

artifacts:
  context: current-task/current-task-context.yaml
  spec: current-task/specs/hero-section.yaml
  plan: current-task/plans/hero-section.yaml
  execution: current-task/executions/hero-section.yaml
  review: current-task/reviews/hero-section.yaml
  review_validation: current-task/review-validations/r1-validation.yaml
  merge: current-task/merges/hero-section.yaml
  commit: current-task/commits/hero-section.yaml
  push: current-task/pushes/hero-section.yaml

constraints:
  - no-commit
  - no-new-deps

open_questions: []

history:
  - step: start
    status: complete
    artifact: current-task/current-task-context.yaml
    summary: Worktree was created and task context initialized.
```
