# Current task context format (deprecated)

> **Deprecated.** Use [status-format.md](status-format.md) (`current-task/status.json`) and [global-status-format.md](global-status-format.md) (`global-status.json`). Do not write this file for new tasks.

`current-task/current-task-context.yaml` was the legacy task-local workflow context. It stores task identity, worktree scope, artifact paths, the current workflow step, blockers, and history so Nicki can orchestrate sheep without relying on chat memory.

The file lives inside the worktree:

```
current-task/
  status.json
  specs/<slug>.yaml
  subtasks/<slug>.md
  executions/<slug>.yaml
  reviews/<slug>.yaml
  review-validations/rN-validation.yaml
  review-inputs/rN-review.yaml
  next-steps/*.yaml
  syncs/<slug>.yaml
  integrates/<slug>.yaml
```

`sheep-status` (current-task-update skill) is the only writer for this file. Nicki and other sheep may read it; artifacts should reference it with `meta.context` when their schema allows metadata.

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
| `original` | Yes | Raw user task text from start (may be slug-level only) |
| `story` | No | Gherkin-style user story — required before `spec`; written during the `describe` step |
| `type` | No | `feature`, `fix`, `chore`, `docs`, `refactor`, `test`, or `perf` |
| `current_step` | Yes | Step Nicki is preparing or just handed off |
| `next_step` | Yes | Next step Nicki should propose |
| `last_completed_step` | No | Latest completed step |

Do not add a broad task-level `state` enum. `current_step`, `next_step`, `last_completed_step`, `open_questions`, and `history[].status` are the source of truth.

### `task.story` (Gherkin user story)

Set during the `describe` step, after the worktree and context file exist. Use a multi-line string with this shape:

```yaml
story: |
  Feature: Hero section redesign

  As a site visitor
  I want to see a clear headline, subcopy, and call-to-action on the home page
  So that I understand the product and know what to do next

  Scenario: Home page hero displays key content
    Given I am viewing the home page
    When the page loads above the fold
    Then I see a prominent headline
    And I see supporting subcopy beneath the headline
    And I see a primary call-to-action button
```

Rules:

- Include `Feature:` and the classic **As a / I want / So that** user story.
- Add at least one `Scenario:` with `Given` / `When` / `Then` (and `And` as needed).
- Keep scenarios testable and specific to the task outcome — not implementation steps.
- Do not proceed to `spec` until `task.story` is present and the user has approved it.

Step values:

- `start`
- `describe`
- `spec`
- `subtasks`
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
| `context` | Yes | `current-task/status.json` |
| `spec` | No | `current-task/specs/<slug>.yaml` |
| `subtasks` | No | `current-task/subtasks/<slug>.md` |
| `execution` | No | `current-task/executions/<slug>.yaml` |
| `review` | No | `current-task/reviews/<slug>.yaml` |
| `review_validation` | No | Latest `current-task/review-validations/rN-validation.yaml` |
| `review_input` | No | Latest `current-task/review-inputs/rN-review.yaml` |
| `next_steps` | No | List of follow-up specs under `current-task/next-steps/` |
| `sync` | No | `current-task/syncs/<slug>.yaml` |
| `integrate` | No | `current-task/integrates/<slug>.yaml` |
| `archive` | No | Root archive path, e.g. `docs/archive/<slug>/report.yaml` |

## `open_questions`

Use an empty list when Nicki can continue safely.

```yaml
open_questions: []
```

When blocked, keep entries compact and actionable:

```yaml
open_questions:
  - step: subtasks
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
  original: "redesign hero section"
  story: |
    Feature: Hero section redesign

    As a site visitor
    I want to see a clear headline, subcopy, and call-to-action on the home page
    So that I understand the product and know what to do next

    Scenario: Home page hero displays key content
      Given I am viewing the home page
      When the page loads above the fold
      Then I see a prominent headline
      And I see supporting subcopy beneath the headline
      And I see a primary call-to-action button
  type: feature
  current_step: subtasks
  next_step: execute
  last_completed_step: spec

git:
  branch: feature/hero-section
  base: main

scope:
  worktree: hero-section
  worktree_path: worktrees/hero-section

artifacts:
  context: current-task/status.json
  spec: current-task/specs/hero-section.yaml
  subtasks: current-task/subtasks/hero-section.md
  execution: current-task/executions/hero-section.yaml
  review: current-task/reviews/hero-section.yaml
  review_validation: current-task/review-validations/r1-validation.yaml
  sync: current-task/syncs/hero-section.yaml
  integrate: current-task/integrates/hero-section.yaml

constraints:
  - no-commit
  - no-new-deps

open_questions: []

history:
  - step: start
    status: complete
    artifact: current-task/status.json
    summary: Worktree was created and task context initialized.
  - step: describe
    status: complete
    summary: Gherkin user story captured and approved.
```
