# Review triage validation format

Review triage validations are the output of `/review-triage`. **YAML only** — write one compact artifact per triaged review.

Store validations in the worktree under `current-task/review-validations/` using sequential names:

```
current-task/review-validations/
  r1-validation.yaml
  r2-validation.yaml
  r3-validation.yaml
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
| `meta` | Yes | Source review and task context |
| `decision` | Yes | Overall result of triaging the review |
| `valid_findings` | Yes | Review findings that are in-scope and correct |
| `discarded_findings` | Yes | Findings rejected as wrong, duplicate, or out of scope |
| `next_steps` | Yes | Follow-up specs written for important out-of-scope findings |
| `review_inputs` | Yes | Review guidance files written when the review should be rerun |
| `summary` | Yes | Short human-readable explanation |

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug |
| `generated_by` | Yes | Always `review-triage` |
| `review` | Yes | Review file or inline review label that was triaged |
| `spec` | No | Spec path used as scope source |
| `plan` | No | Plan path used as scope source |
| `execution` | No | Execution handoff path used as scope source |
| `context` | No | Task context path used as workflow source |

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
| `evidence` | No | Spec requirement, plan step, diff path, or file reference supporting the verdict |

## `next_steps`

Each entry records an important out-of-scope finding that was converted into a separate spec YAML that `/plan-maker` can consume directly.

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
| `reason` | Yes | Why review-execution should consume the guidance |

Use an empty list when no review guidance was written.

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: review-triage
  review: current-task/reviews/hero-section.yaml
  spec: current-task/specs/hero-section.yaml
  plan: current-task/plans/hero-section.yaml
  execution: current-task/executions/hero-section.yaml
  context: current-task/current-task-context.yaml

decision: partially_valid

valid_findings:
  - id: finding-1
    source: "[verify] npm run lint failed"
    verdict: valid
    reason: Verify failure is part of this task acceptance criteria.
    evidence: "plan step verify"

discarded_findings:
  - id: footer-redesign
    source: "Footer should be redesigned to match the new hero."
    verdict: out_of_scope
    reason: Spec scope is limited to the home page hero and explicitly excludes footer changes.
    evidence: "spec.scope.out: Header, footer, and other pages"

next_steps:
  - id: footer-redesign
    path: current-task/next-steps/r1-footer-redesign.yaml
    reason: Potentially useful follow-up spec, but outside this task scope.

review_inputs:
  - id: rerun-review
    path: current-task/review-inputs/r1-review.yaml
    reason: Previous review mixed in out-of-scope footer blockers.

summary: |
  Review is partially valid. Keep the verify finding for this task.
  Discard the footer redesign finding from this review and track it as a next-step spec.
```

## Triage rules

- Keep findings that map to spec requirements, plan steps, execution deviations, changed paths, verify failures, or relevant CONTRIBUTING constraints.
- Discard findings about files, features, or improvements outside spec `scope.in`, inside spec `scope.out`, or unrelated to changed paths.
- Discard plainly wrong findings when the current-task artifacts or code contradict them.
- Convert important out-of-scope findings into `current-task/next-steps/*.yaml` specs instead of blocking the current task.
- When the review is discarded or mostly invalid, write `current-task/review-inputs/rN-review.yaml` using [review-guidance-format.md](review-guidance-format.md).
- Do not mutate the original review file.
