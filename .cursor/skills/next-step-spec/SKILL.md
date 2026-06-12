---
name: next-step-spec
description: "YAML spec format for follow-up tasks created from triaged out-of-scope review findings."
disable-model-invocation: true
---

# Next-Step Spec

Follow-up spec YAML when a review finding is important but outside the current task scope. Uses the same schema as [spec-format.md](../spec-maker/spec-format.md).

## Output location

Default path: `current-task/next-steps/<name>.yaml` under the worktree scope root.

## Required shape

Same top-level fields as [spec-format.md](../spec-maker/spec-format.md):

- `meta`
- `title`
- `type`
- `summary`
- `requirements`
- `scope`
- `constraints`
- `acceptance`
- `assumptions`
- `open_questions`

For next-step specs, set `meta.generated_by: review-triage` and include `meta.source_review`, `meta.source_validation`, and `meta.source_finding` for traceability.

## YAML example

```yaml
meta:
  worktree: footer-redesign
  generated_by: review-triage
  task: "Footer visual alignment follow-up from hero-section review"
  source_validation: current-task/review-validations/r1-validation.yaml
  source_review: current-task/reviews/hero-section.yaml
  source_task: hero-section
  source_finding: "Footer should be redesigned to match the new hero."

title: Footer visual alignment follow-up
type: feature
summary: >
  The review raised footer visual alignment concerns that are unrelated to the
  hero task but may be worth handling separately.

requirements:
  - id: footer-visual-alignment
    description: Define the desired footer visual alignment as a separate task.

scope:
  in:
    - Footer visual alignment
  out:
    - Hero implementation
    - Header or navigation behavior

constraints:
  - no-commit
  - no-new-deps

acceptance:
  - Footer visual changes are specified in a dedicated spec.
  - Existing hero task remains unchanged.

assumptions:
  - This follow-up should not change the completed hero task.

open_questions: []
```

## Rules

- Write a next-step only for out-of-scope findings that are plausible and valuable.
- Do not write next-steps for wrong, duplicate, or non-actionable findings.
- Keep this as a spec, not implementation detail: no file paths, no subtask lines.
