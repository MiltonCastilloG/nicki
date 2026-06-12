---
name: review-triage
description: "Triage a review YAML against spec scope; keep valid findings, discard invalid ones; write validation YAML."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: review-triage
---

# Review Triage

Triage a review against spec, subtasks, and execution evidence. Keep only findings that are correct and in scope. Discard findings that are wrong, duplicate, non-actionable, or outside task scope. Important out-of-scope findings become follow-up spec YAML files. Invalid reviews may produce review guidance with `important-considerations` for a future review run.

- Review input: [review-format.md](../review-execution/review-format.md)
- Validation output: [validation-format.md](validation-format.md)
- Follow-up spec: [next-step-spec](../next-step-spec/SKILL.md)
- Review guidance: [review-guidance-format.md](review-guidance-format.md)

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative |
| Review | Preferred | Path or inline YAML |
| Spec | Preferred | Path or inline YAML |
| Subtask list | Preferred | Path or inline markdown |
| Execution | Preferred | Path or inline YAML when present |
| Validation output path | No | Next sequential `current-task/review-validations/rN-validation.yaml` |

If worktree path is missing, ask before starting.

If review is missing, ask for a review file or inline review YAML.

## Procedure

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load review and scope inputs
- [ ] Split review content into findings
- [ ] Triage each finding against scope and evidence
- [ ] Write next-step specs for important out-of-scope findings
- [ ] Write review guidance when review should be rerun
- [ ] Write validation YAML
- [ ] Append ## Fix subtasks when readiness is fix_required
- [ ] Report summary
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists.
3. Set the **scope root** to that absolute path. Derive `<slug>` from the final folder name.
4. Default validation path: next sequential `current-task/review-validations/rN-validation.yaml` (`r1`, `r2`, …).

**Scope rules (non-negotiable):**

- **Read** anywhere under the scope root.
- **Write** only to:
  - `current-task/review-validations/rN-validation.yaml` (always include `readiness` block)
  - `current-task/next-steps/*.yaml` for important out-of-scope specs
  - `current-task/review-inputs/rN-review.yaml` for rerun-review guidance
  - subtask list — **append only** `## Fix` when `readiness.status: fix_required`; never change prior `- [x]` lines
- Never edit application code, specs, plans, executions, or reviews.
- Never modify files outside the scope root.
- Do not run shell commands; triage using artifacts, reads, grep/glob/search, and source inspection.

### Step 2: Load inputs

Load available inputs passed by the agent:

- Spec: requirements, `scope.in`, `scope.out`, constraints, acceptance
- Subtask list: checklist items, completion state, test/verification subtasks
- Execution: touched paths, deviations, hotspots, verify evidence
- Review: exactly `approved` and `content`

If spec or subtask list is missing, ask whether to proceed with partial triage or stop. Missing execution is a warning, not a blocker.

### Step 3: Split review findings

Parse `content` into review findings:

- Bullets with prefixes such as `[req-*]`, `[subtask:*]`, `[scope]`, `[verify]`, `[convention]`
- Short pass summaries when `approved: true`
- Any sentence that asks for or implies a change

Do not rewrite the original review.

### Step 4: Triage each finding

For each finding, classify it:

- `valid` — directly supported by spec, subtask list, execution, diff evidence, verification evidence, changed files, or CONTRIBUTING constraints.
- `out_of_scope` — useful but outside spec `scope.in`, explicitly inside `scope.out`, unrelated to changed paths, or belongs to a separate concern.
- `wrong` — contradicted by source files, artifacts, subtask completion state, or verification evidence.
- `duplicate` — same actionable issue already represented by another finding.
- `not_actionable` — too vague to drive a fix or future task.

Keep the review strict but fair:

- A finding does not need to be worded perfectly to be valid if the underlying issue is real and in scope.
- Do not reject safety, correctness, or build-breaking issues just because they were not named in the subtasks.
- Do reject style preferences, redesign requests, unrelated refactors, and broad improvements outside the task scope.

### Step 5: Write next-step specs

For each `out_of_scope` finding that is plausible, important, and actionable:

1. Create `current-task/next-steps/` if needed.
2. Write compact YAML per [next-step-spec](../next-step-spec/SKILL.md) / [spec-format.md](../spec-maker/spec-format.md).
3. Reference the spec in `next_steps` inside the validation YAML.

Do not write next-step specs for wrong, duplicate, or non-actionable findings.

### Step 6: Write review guidance

When the review is `discarded` or mostly invalid:

1. Create `current-task/review-inputs/` if needed.
2. Write `rN-review.yaml` per [review-guidance-format.md](review-guidance-format.md).
3. Include `important-considerations` with concrete context for the next review.
4. Reference the guidance file in `review_inputs` inside the validation YAML.

Do not write review guidance when the review is simply valid or partially valid with clear discarded findings that do not require a rerun.

### Step 7: Write validation + readiness

1. Create `current-task/review-validations/` if needed.
2. Write `rN-validation.yaml` per [validation-format.md](validation-format.md).
3. Set `decision`: `valid`, `partially_valid`, or `discarded`.
4. Emit `readiness` on every write per validation-format rules.
5. `blockers` non-empty **only** for `fix_required` or `blocked`.
6. When `fix_required`, optional `readiness.fix_subtasks` — one sentence each; append `## Fix` to subtask list (ref validation path in section header). Prior `- [x]` untouched.

### Step 8: Report

Summarize:

- Scope root used
- Review file triaged
- Validation file path
- `readiness.status` and `recommended_next_step`
- Counts: valid, discarded, next-step specs, review guidance files
- Any missing context or assumptions

## Safety rules

- Never edit application code
- Never edit the original review
- Never edit the original task spec, subtask list, or executions (except append `## Fix`)
- Never edit review guidance once written; create a new numbered file instead
- Never modify files outside the worktree scope root
- When in doubt, ask — do not silently keep or discard ambiguous findings
