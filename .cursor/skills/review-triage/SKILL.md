---
name: review-triage
description: "Triage review-execution output against current-task context, keep valid findings, discard wrong or out-of-scope findings, and write current-task/review-validations/rN-validation.yaml. Use when the user runs /review-triage or asks to triage review feedback."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: review-triage
  tools:
    read: true
    write: true
    delete: false
    shell: false
    grep: true
    glob: true
    semantic_search: true
    task: false
    web_search: false
    web_fetch: false
    mcp: false
    ask_question: true
    todo_write: true
    generate_image: false
    switch_mode: false
---

# Review Triage

Triage a `/review-execution` YAML review against the full `current-task/` context. Keep only review findings that are correct and in scope. Discard findings that are plainly wrong, duplicate, non-actionable, or outside the task scope. Important out-of-scope findings become normal spec YAML files under `current-task/next-steps/` so `/plan-maker` can consume them. Invalid reviews can also produce review guidance under `current-task/review-inputs/` with `important-considerations` for a future `/review-execution`.

- Review input schema: [review-format.md](../review-execution/review-format.md)
- Validation output schema: [validation-format.md](validation-format.md)
- Next-step spec schema: [next-step-spec](../next-step-spec/SKILL.md)
- Review guidance schema: [review-guidance-format.md](review-guidance-format.md)

## When to use

- User invokes `/review-triage` after `/review-execution`
- Review feedback needs sorting before deciding whether to fix, re-plan, or create a new task
- User asks whether a review stayed within task scope

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Review | Preferred | Auto-load `current-task/reviews/<slug>.yaml` from worktree or accept an explicit review path/inline YAML |
| Spec | Preferred | Auto-load `current-task/specs/<slug>.yaml` |
| Plan | Preferred | Auto-load `current-task/plans/<slug>.yaml` |
| Execution | Preferred | Auto-load `current-task/executions/<slug>.yaml` when present |
| Task context | Optional | Auto-load `current-task/current-task-context.yaml` when present |

If worktree path is missing, ask before starting.

If review is missing, ask for a review file or inline review YAML.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load current-task context and review
- [ ] Split review content into findings
- [ ] Triage each finding against scope and evidence
- [ ] Write next-step specs for important out-of-scope findings
- [ ] Write review guidance when review should be rerun
- [ ] Write current-task/review-validations/rN-validation.yaml
- [ ] Report summary and next command options
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists.
3. Set the **scope root** to that absolute path. Derive `<slug>` from the final folder name.
4. Validation output path: next sequential `current-task/review-validations/rN-validation.yaml`.

Use `r1-validation.yaml`, `r2-validation.yaml`, `r3-validation.yaml`, and so on. If an explicit review file indicates a number (for example `r2.yaml`), use the matching `r2-validation.yaml` when it does not already exist; otherwise use the next available number.

**Scope rules (non-negotiable):**

- **Read** anywhere under the scope root, especially `current-task/`.
- **Write** only to:
  - `current-task/review-validations/rN-validation.yaml`
  - `current-task/next-steps/*.yaml` for important out-of-scope specs
  - `current-task/review-inputs/rN-review.yaml` for rerun-review guidance
- Never edit application code, specs, plans, executions, or reviews.
- Never modify files outside the scope root.
- Do not run shell commands; triage using artifacts, reads, grep/glob/search, and source inspection.

### Step 2: Load context

Load available artifacts from `current-task/`:

- Spec: requirements, `scope.in`, `scope.out`, constraints, acceptance
- Plan: steps, paths, requirement coverage, verify commands
- Execution: touched paths, deviations, hotspots, verify evidence
- Review: exactly `approved` and `content`
- Task context: current workflow step, open questions, artifact paths, history

If spec or plan is missing, ask whether to proceed with partial triage or stop. Missing execution is a warning, not a blocker.

### Step 3: Split review findings

Parse `content` into review findings:

- Bullets with prefixes such as `[req-*]`, `[plan:*]`, `[scope]`, `[verify]`, `[convention]`
- Short pass summaries when `approved: true`
- Any sentence that asks for or implies a change

Do not rewrite the original review.

### Step 4: Triage each finding

For each finding, classify it:

- `valid` — directly supported by spec, plan, execution, diff evidence, verification evidence, changed files, or CONTRIBUTING constraints.
- `out_of_scope` — useful but outside spec `scope.in`, explicitly inside `scope.out`, unrelated to changed paths, or belongs to a separate concern.
- `wrong` — contradicted by source files, artifacts, plan status, or verification evidence.
- `duplicate` — same actionable issue already represented by another finding.
- `not_actionable` — too vague to drive a fix or future task.

Keep the review strict but fair:

- A finding does not need to be worded perfectly to be valid if the underlying issue is real and in scope.
- Do not reject safety, correctness, or build-breaking issues just because they were not named in the plan.
- Do reject style preferences, redesign requests, unrelated refactors, and broad improvements outside the task scope.

### Step 5: Write next-step specs

For each `out_of_scope` finding that is plausible, important, and actionable:

1. Create `current-task/next-steps/` if needed.
2. Write a compact YAML spec following [next-step-spec](../next-step-spec/SKILL.md), which uses the same schema as [spec-format.md](../spec-maker/spec-format.md).
3. Reference the spec in `next_steps` inside the validation YAML.

Do not write next-step specs for wrong, duplicate, or non-actionable findings.

### Step 6: Write review guidance

When the review is `discarded` or mostly invalid:

1. Create `current-task/review-inputs/` if needed.
2. Write `rN-review.yaml` following [review-guidance-format.md](review-guidance-format.md).
3. Include `important-considerations` with concrete context the next `/review-execution` should keep in mind.
4. Reference the guidance file in `review_inputs` inside the validation YAML.

Do not write review guidance when the review is simply valid or partially valid with clear discarded findings that do not require a rerun.

### Step 7: Write validation

1. Create `current-task/review-validations/` if needed.
2. Write `rN-validation.yaml` following [validation-format.md](validation-format.md).
3. Set `decision`:
   - `valid` when all findings should stand.
   - `partially_valid` when at least one finding stands and at least one is discarded.
   - `discarded` when no finding should stand.

### Step 8: Report

Summarize:

- Scope root used
- Review file triaged
- Validation file path
- Counts: valid, discarded, next-step specs, review guidance files
- Any missing context or assumptions

## Safety rules

- Never edit application code
- Never edit `current-task/current-task-context.yaml`; Nicki updates it through `/current-task-update`
- Never edit the original review
- Never edit the original task spec, plans, or executions
- Never edit review guidance once written; create a new numbered file instead
- Never modify files outside the worktree scope root
- Do not spawn subagents (`task: false`)
- When in doubt, ask — do not silently keep or discard ambiguous findings

## Examples

**Input:**

```
/review-triage worktrees/hero-section
```

**Explicit review:**

```
/review-triage worktrees/hero-section @current-task/reviews/hero-section.yaml
```

**Output file:**

```
worktrees/hero-section/current-task/review-validations/r1-validation.yaml
```
