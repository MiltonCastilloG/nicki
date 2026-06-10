---
name: review-execution
description: "Review post-execute worktree changes against spec, plan, and execution handoff; write current-task/reviews/<slug>.yaml with approved status and review content. Use when the user runs /review-execution or asks to review implementation in a worktree."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: review-execution
  tools:
    read: true
    write: true
    delete: false
    shell: true
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

# Review Execution

Review implementation in a worktree **after** `/execute-plan`. Compare changes against the spec, plan, execution handoff, optional review guidance, and actual git diff; run verification checks; and produce a YAML review with exactly `approved` and `content`.

- Spec schema (input): [spec-format.md](../spec-maker/spec-format.md)
- Plan schema (input): [plan-format.md](../execute-plan/plan-format.md)
- Execution schema (input): [execution-format.md](../execute-plan/execution-format.md)
- Review schema (output): [review-format.md](review-format.md)

## When to use

- User invokes `/review-execution` with a worktree path after execution
- A plan was executed and needs a quality gate before merge or further workflow
- User asks to review (not fix or re-plan) work inside an isolated worktree

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Spec | Preferred | Auto-load `current-task/specs/<slug>.yaml` from worktree |
| Plan | Preferred | Auto-load `current-task/plans/<slug>.yaml` from worktree |
| Execution | Preferred | Auto-load `current-task/executions/<slug>.yaml` from worktree |
| Task context | Optional | Auto-load `current-task/current-task-context.yaml` from worktree |
| Review guidance | Optional | `current-task/review-inputs/rN-review.yaml` with `important-considerations` |

If worktree path is missing, ask before starting.

If spec or plan is missing, ask whether to proceed with partial review or stop.

If execution handoff is missing, continue with a warning in your summary. Missing execution YAML is not a blocker when spec, plan, and diff are enough to review.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load task context, spec, plan, execution handoff, and optional review guidance
- [ ] Discover changes (git diff)
- [ ] Check requirement coverage
- [ ] Check plan adherence
- [ ] Run acceptance / verify commands
- [ ] Spot-check CONTRIBUTING conventions
- [ ] Decide approved true/false
- [ ] Write current-task/reviews/<slug>.yaml
- [ ] Report summary and echo YAML
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists.
3. Set the **scope root** to that absolute path. Derive `<slug>` from the final folder name (e.g. `worktrees/hero-section` → slug `hero-section`).
4. Review output path: `current-task/reviews/<slug>.yaml` relative to the scope root.

**Scope rules (non-negotiable):**

- **Read** anywhere under the scope root and CONTRIBUTING.md.
- **Write** only to `current-task/reviews/<slug>.yaml` (create `current-task/reviews/` directory if missing).
- Never edit `src/`, `app/`, config, tests, specs, plans, or any application files.
- Never modify files outside the scope root.
- Run shell commands with `working_directory` set to the scope root.

### Step 2: Load inputs

1. Load spec from `@current-task/specs/<slug>.yaml`, a path, or inline YAML.
2. Load plan from `@current-task/plans/<slug>.yaml`, a path, or inline YAML.
3. Load task context from `@current-task/current-task-context.yaml` when present.
4. Load execution handoff from `@current-task/executions/<slug>.yaml`, a path, or inline YAML when present.
5. Load optional review guidance from `@current-task/review-inputs/rN-review.yaml`, a path, or inline YAML when provided.
6. If spec or plan is missing, ask before continuing with partial review.
7. Extract: `requirements`, `scope`, `acceptance`, `constraints` from spec; ordered `steps` and verify commands from plan; touched paths, step statuses, verification evidence, deviations, and hotspots from execution; workflow hints and open questions from task context.
8. Extract `important-considerations` from review guidance when present.
9. Treat task context, execution handoff, and review guidance as guidance only. The git diff, source files, and rerun verification decide approval.

### Step 2a: Apply important considerations

When review guidance is present:

- Keep each `important-considerations` item in scope while reviewing.
- Do not repeat findings that the guidance says were out of scope or wrong unless current source evidence proves they are real in-scope blockers.
- Still report build, lint, test, safety, correctness, requirement, plan, and convention issues when supported by evidence.
- Do not copy `important-considerations` into the output YAML. The review output still has exactly `approved` and `content`.

### Step 3: Discover changes

From the scope root, inspect what changed:

- `git diff main...HEAD --name-only` (or `git diff --name-only` if no merge base with main)
- `git diff main...HEAD` for relevant files

Flag files changed that are:

- Listed in spec `scope.out`
- Not referenced by any plan step `path` (possible scope creep)
- Missing from execution `paths` or marked `unplanned: []` despite appearing in the diff

### Step 4: Requirement coverage

For each spec `requirements[].id`:

- Read the implementation (and tests if applicable) in the worktree
- Confirm the requirement description is satisfied
- Record blocking gaps as `[req-<id>]` bullets for `content`

### Step 5: Plan adherence

For each plan step with a `path`:

- Confirm the file exists (or was created then removed per plan)
- Confirm changes match the step `do` instructions
- Compare the execution `steps` status and `paths` with the actual diff
- Record skipped or incorrect steps as `[plan:<step-id>]` bullets

Note plan steps with no `path` (`run`, `verify`) via their reported outcome or re-run where appropriate.

If execution `deviations`, `open_questions`, or `review_scope.mode: triage` indicate partial or blocked work, do not approve unless the review scope explicitly excludes the incomplete work and the user asked for that narrower review.

### Step 6: Acceptance and verify

1. Run commands from the plan's final `verify` step(s) from the scope root.
2. If the plan has no verify step, run CONTRIBUTING defaults: `npm run lint`, `npm test` (scoped to affected areas when possible).
3. Compare rerun results with execution `verify` evidence when present.
4. Map results to spec `acceptance` criteria.
5. Record failures as `[verify]` bullets with command output context.

### Step 7: Convention check

Spot-check [CONTRIBUTING.md](../../../CONTRIBUTING.md) rules relevant to the task:

- Semantic Tailwind tokens (no raw palette classes when spec requires tokens)
- i18n via `useTranslations` when strings were added
- `no-new-deps` constraint — inspect `package.json` diff if constrained
- Project layout expectations for new modules
- Execution `hotspots` from `current-task/executions/<slug>.yaml`

Record blocking violations as `[convention]` bullets.

### Step 8: Decide `approved`

- `approved: true` only when **no blocking issues** remain across requirements, plan, scope, verify, and conventions.
- Any blocking issue → `approved: false`.
- Do not include non-blocking nits unless the user requested strict review.

### Step 9: Write and report

1. Create `current-task/reviews/` under the scope root if it does not exist.
2. Write the complete YAML to `current-task/reviews/<slug>.yaml` per [review-format.md](review-format.md).
3. Echo the same YAML in the report.
4. Summarize: scope root, spec/plan/execution/guidance paths used, files reviewed, commands run, issue count, review file path.

## Safety rules

- Never edit application code — only `current-task/reviews/*.yaml`
- Never edit `current-task/current-task-context.yaml`; Nicki updates it through `/current-task-update`
- Never modify specs or plans during review
- Never modify files outside the scope root
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- Do not commit or push unless the user explicitly asks
- Do not spawn subagents (`task: false`)
- When in doubt, ask — do not guess pass/fail
- Do not mention downstream agents or routing in prompts or output
- Do not include `important-considerations` in review output; it is input-only

## Examples

**Input:** `/review-execution worktrees/hero-section`

**Output file:** `worktrees/hero-section/current-task/reviews/hero-section.yaml`

**Input with explicit refs:**

```
/review-execution worktrees/hero-section @current-task/specs/hero-section.yaml @current-task/plans/hero-section.yaml
```

**Input with review guidance from `/review-triage`:**

```
/review-execution worktrees/hero-section @current-task/review-inputs/r1-review.yaml
```
