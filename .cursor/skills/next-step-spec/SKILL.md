---
name: next-step-spec
description: "Defines the YAML spec format for follow-up tasks created from validated review findings. Use when writing current-task/next-steps/*.yaml for plan-maker."
disable-model-invocation: true
---

# Next-Step Spec

Use this skill when an agent needs to write `current-task/next-steps/*.yaml`.

Next-step files are **normal spec YAML** created when a finding is important but outside the current task scope. They must follow [spec-format.md](../spec-maker/spec-format.md) so `/plan-maker` can consume them directly.

## Output location

Store next-step specs in the worktree under `current-task/next-steps/`:

```
current-task/next-steps/
  r1-footer-redesign.yaml
  r2-accessibility-followup.yaml
```

## Required shape

Use the same top-level fields as [spec-format.md](../spec-maker/spec-format.md):

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
- The file must be directly passable to `/plan-maker worktrees/<slug> @current-task/next-steps/<file>.yaml`.
- Do not write next-steps for wrong, duplicate, or non-actionable findings.
- Keep this as a spec, not an implementation plan: no file paths, no plan steps.
