# Validation format

After review: emit `current-task/review-validations/rN-validation.yaml`, optional `current-task/next-steps/*.yaml`, optional `## Fix` on subtasks. Trust review prefixes — no source re-read.

## Procedure

1. Parse review `content` bullets by prefix.
2. Blocking → `valid_findings`: `[req-`, `[subtask:`, `[verify]`, `[convention]`. `[scope]` → `deferred_findings`.
3. Set `readiness` (table below). `blockers` = blocking text when `fix_required`.
4. Important deferred findings → write next-step YAML (shape below); record in `next_steps`.
5. `fix_required` → `fix_subtasks` + append `## Fix` on subtask list (keep prior `- [x]`).
6. Write validation YAML. `discarded_findings: []`, `review_inputs: []`.

## Readiness

| Condition | `status` | `recommended_next_step` |
|-----------|----------|-------------------------|
| `approved: true` | `ready_for_acceptance` | `acceptance` |
| `approved: false`, only `[scope]` | `ready_for_acceptance` | `acceptance` + `deferred_scope: true` |
| any blocking prefix | `fix_required` | `execute` |
| missing review | `blocked` | `blocked` |

## Validation fields

| Field | Required | Notes |
|-------|----------|-------|
| `meta` | Yes | `worktree`, `generated_by: validation`, `review` path |
| `decision` | Yes | `valid`, `partially_valid`, or `discarded` |
| `valid_findings` | Yes | Blocking bullets |
| `deferred_findings` | Yes | `[scope]` bullets |
| `discarded_findings` | Yes | `[]` |
| `next_steps` | Yes | `{id, path, reason}` per next-step file written |
| `review_inputs` | Yes | `[]` |
| `readiness` | Yes | `status`, `recommended_next_step`, `blockers`, optional `deferred_scope`, `fix_subtasks` |
| `summary` | Yes | One short paragraph |

## Next-step YAML (`current-task/next-steps/<name>.yaml`)

Compact follow-up spec — no file paths, no subtasks.

`meta`: `worktree`, `generated_by: validation`, `source_validation`, `source_review`, `source_finding`

Plus: `title`, `type`, `summary`, `requirements[]`, `scope`, `constraints`, `acceptance`, `assumptions`, `open_questions`

## Fix append

```markdown

## Fix
<!-- ref: current-task/review-validations/rN-validation.yaml -->
- [ ] <one-line fix>
```

## Example

```yaml
meta:
  worktree: hero-section
  generated_by: validation
  review: current-task/reviews/hero-section.yaml
decision: partially_valid
valid_findings:
  - id: f1
    source: "[verify] lint failed"
    prefix: verify
    reason: Blocking from review.
deferred_findings: []
discarded_findings: []
next_steps: []
review_inputs: []
readiness:
  status: fix_required
  recommended_next_step: execute
  blockers: ["lint failed"]
  fix_subtasks: ["Fix lint errors"]
summary: One blocking verify finding.
```
