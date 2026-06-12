# Review triage validation format

**YAML only** — one compact artifact per triaged review.

Default path: `current-task/review-validations/rN-validation.yaml` (`r1`, `r2`, …) under the worktree scope root.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Source review and scope inputs used |
| `decision` | Yes | Overall result of triaging the review |
| `valid_findings` | Yes | Review findings that are in-scope and correct |
| `discarded_findings` | Yes | Findings rejected as wrong, duplicate, or out of scope |
| `next_steps` | Yes | Follow-up specs written for important out-of-scope findings |
| `review_inputs` | Yes | Review guidance files written when the review should be rerun |
| `readiness` | Yes | Structured outcome for orchestration |
| `summary` | Yes | Short human-readable explanation |

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug |
| `generated_by` | Yes | Always `review-triage` |
| `review` | Yes | Review file or inline review label that was triaged |
| `spec` | No | Spec path used as scope source |
| `subtasks` | No | Subtask list path used as scope source |
| `execution` | No | Execution handoff path used as scope source |
| `context` | No | Optional traceability path when the loading agent sets one |

## `decision`

Allowed values:

- `valid` — the review is in scope and substantially correct.
- `partially_valid` — some findings are valid, but others were discarded.
- `discarded` — no review findings should be acted on for this task.

## Finding fields

Use the same structure for `valid_findings` and `discarded_findings`.

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Stable label (`finding-1`, `scope-footer`) |
| `source` | No | Original review prefix or excerpt |
| `verdict` | Yes | `valid`, `wrong`, `out_of_scope`, `duplicate`, or `not_actionable` |
| `reason` | Yes | Why this finding was kept or discarded |
| `evidence` | No | Spec requirement, subtask line, diff path, or file reference supporting the verdict |

## `next_steps`

Each entry records an important out-of-scope finding converted into a separate spec YAML.

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Stable label |
| `path` | Yes | Spec path written under `current-task/next-steps/` |
| `reason` | Yes | Why the follow-up belongs outside this task |

Use an empty list when no follow-up specs were written.

## `review_inputs`

Each entry records review guidance written because the original review was invalid enough to rerun.

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Stable label |
| `path` | Yes | Path written under `current-task/review-inputs/` |
| `reason` | Yes | Why review should consume the guidance |

Use an empty list when no review guidance was written.

## `readiness`

Required on every validation write.

| Field | Required | Description |
|-------|----------|-------------|
| `status` | Yes | `ready_for_acceptance`, `fix_required`, `rerun_review`, or `blocked` |
| `recommended_next_step` | Yes | `acceptance`, `execute`, `review`, or `blocked` — must pair with `status` |
| `blockers` | Yes | Non-empty **only** for `fix_required` or `blocked`; else `[]` |
| `fix_subtasks` | No | One-line fix descriptions when `fix_required`; agent appends `## Fix` on subtask list |

### When to set each `status`

- `ready_for_acceptance` — no in-scope fix needed; scope clean.
- `fix_required` — valid in-scope findings need code change; populate `blockers` and optional `fix_subtasks`.
- `rerun_review` — review was discarded or mostly invalid; `review_inputs` non-empty.
- `blocked` — user/spec ambiguity stops progress; populate `blockers`.

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: review-triage
  review: current-task/reviews/hero-section.yaml
  spec: current-task/specs/hero-section.yaml
  subtasks: current-task/subtasks/hero-section.md
  execution: current-task/executions/hero-section.yaml

decision: partially_valid

valid_findings:
  - id: finding-1
    source: "[verify] npm run lint failed"
    verdict: valid
    reason: Verify failure is part of this task acceptance criteria.
    evidence: "subtask verification item"

discarded_findings:
  - id: footer-redesign
    verdict: out_of_scope
    reason: Outside spec scope.in.
    evidence: spec.scope.out

next_steps:
  - id: footer-redesign
    path: current-task/next-steps/r1-footer-redesign.yaml
    reason: Follow-up outside this task.

review_inputs: []

readiness:
  status: fix_required
  recommended_next_step: execute
  blockers:
    - "npm run lint failed — fix before acceptance"
  fix_subtasks:
    - "Fix lint errors from verify finding"

summary: |
  Partially valid. Keep verify finding; footer → next-step spec.
```

## Triage rules

- Keep findings mapping spec, subtasks, execution, verify failures, changed paths.
- Discard out-of-scope, wrong, duplicate, non-actionable findings.
- Out-of-scope but important → `current-task/next-steps/*.yaml`.
- Discarded/mostly invalid review → `review_inputs` + `readiness.status: rerun_review`.
- Always emit `readiness`; never mutate original review file.
