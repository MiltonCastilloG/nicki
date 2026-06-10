# Execution format

Executions are the handoff from `/execute-plan` to `/review-execution`. **YAML only** — write one compact artifact after executing, partially executing, or blocking on a plan.

Store executions in the worktree under `current-task/executions/` (e.g. `current-task/executions/hero-section.yaml`).

All agent YAML artifacts for the active task live under `current-task/`:

```
current-task/
  current-task-context.yaml              # workflow context from /current-task-update
  specs/<slug>.yaml                    # from /spec-maker
  plans/<slug>.yaml                    # from /plan-maker
  executions/<slug>.yaml               # from /execute-plan
  reviews/<slug>.yaml                  # from /review-execution
  review-validations/rN-validation.yaml # from /review-triage
  review-inputs/rN-review.yaml         # optional guidance input for /review-execution
  next-steps/*.yaml                    # follow-up specs consumable by /plan-maker
  merges/<slug>.yaml                   # from /merge-task
  commits/<slug>.yaml                  # from /commit-task
  pushes/<slug>.yaml                   # from /push-task
```

The execution file is a map for review, not an approval. `/review-execution` still reads the diff and reruns verification independently.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Routing, source plan, and execution status |
| `paths` | Yes | Touched paths grouped by change type |
| `steps` | Yes | One result entry per plan step, in plan order |
| `verify` | If verify ran | Command evidence from execution |
| `deviations` | No | Approved or blocked departures from the plan |
| `open_questions` | No | Questions left unresolved at handoff time |
| `hotspots` | No | Reviewer focus areas |
| `review_scope` | No | Hints for full, triage, or focused review |

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug (e.g. `hero-section`) |
| `generated_by` | Yes | Always `execute-plan` |
| `plan` | Yes | Plan path used (e.g. `current-task/plans/hero-section.yaml`) |
| `spec` | No | Spec path when known |
| `context` | No | Path to task context (e.g. `current-task/current-task-context.yaml`) |
| `status` | Yes | `complete`, `partial`, or `blocked` |
| `constraints` | No | Constraints honored from the plan |

## `paths`

Use paths relative to the worktree root.

| Field | Required | Description |
|-------|----------|-------------|
| `created` | No | Files created during execution |
| `modified` | No | Files modified during execution |
| `deleted` | No | Files deleted during execution |
| `unplanned` | No | Files touched but not named by a plan step |

At least one list should be non-empty unless execution blocked before edits.

## `steps`

Mirror plan order. Do not copy the full plan body; reference `id` and summarize the result.

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Plan step ID |
| `status` | Yes | `done`, `partial`, `skipped`, or `blocked` |
| `action` | No | Plan action (`create`, `modify`, `delete`, `run`, `verify`) |
| `paths` | No | Paths touched by this step |
| `note` | No | One-line outcome, blocker, or user decision |

## `verify`

Include one entry per command run by `/execute-plan`.

| Field | Required | Description |
|-------|----------|-------------|
| `command` | Yes | Shell command |
| `exit` | Yes | Exit code |
| `passed` | Yes | `true` or `false` |
| `tail` | No | Last few relevant output lines for failures only |

## Optional detail blocks

### `deviations`

Use when execution differed from the plan.

| Field | Required | Description |
|-------|----------|-------------|
| `kind` | Yes | `user_approved`, `plan_gap`, `blocked`, or `out_of_scope` |
| `step_id` | No | Related plan step |
| `note` | Yes | What changed and why |

### `hotspots`

Use for focused review attention, not for full explanations.

| Field | Required | Description |
|-------|----------|-------------|
| `path` | Yes | File or area to review closely |
| `reason` | Yes | Short reason (e.g. `semantic-tokens`, `i18n-strings`, `new-deps-risk`) |

### `review_scope`

Use when review should be partial or focused.

| Field | Required | Description |
|-------|----------|-------------|
| `mode` | No | `full` (default), `triage`, or `verify_only` |
| `focus_paths` | No | Paths to prioritize |
| `skip_steps` | No | Step IDs that are not reviewable yet |

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: execute-plan
  plan: current-task/plans/hero-section.yaml
  spec: current-task/specs/hero-section.yaml
  context: current-task/current-task-context.yaml
  status: complete
  constraints: [no-commit, no-new-deps]

paths:
  created: [src/components/Hero/Hero.tsx]
  modified: [app/page.tsx]
  deleted: []
  unplanned: []

steps:
  - id: create-hero
    status: done
    action: create
    paths: [src/components/Hero/Hero.tsx]
    note: Hero with headline, subcopy, CTA, and semantic tokens.
  - id: wire-hero
    status: done
    action: modify
    paths: [app/page.tsx]
    note: Replaced landing banner with Hero.
  - id: verify
    status: done
    action: verify
    note: All verify commands passed.

verify:
  - command: npm run lint
    exit: 0
    passed: true
  - command: npm test -- Hero
    exit: 0
    passed: true

deviations: []
open_questions: []

hotspots:
  - path: src/components/Hero/Hero.tsx
    reason: semantic-tokens

review_scope:
  mode: full
```

## Writing good execution files

**Do:**

- Write the file even when execution blocks or stops partially.
- Keep notes short; point to plan step IDs instead of repeating plan instructions.
- Record all changed paths, including unplanned paths.
- Include failure output only when a command fails, and keep it short.

**Don't:**

- Include diffs, transcripts, or long logs.
- Mark review approval here; that belongs only in `current-task/reviews/<slug>.yaml`.
- Hide scope changes. If an unplanned path changed, list it under `paths.unplanned`.
