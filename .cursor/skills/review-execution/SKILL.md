---
name: review-execution
description: "Review worktree changes against spec, subtasks, and execution evidence; write a YAML review with approved and content."
---

# Review Execution

Review implementation in a worktree. Compare changes against the spec, subtask list, execution handoff, optional review guidance, and actual git diff; run verification checks; produce YAML with exactly `approved` and `content`.

- Review output: [review-format.md](review-format.md)
- Guidance input: [review-guidance-format.md](review-guidance-format.md)
- Post-review validation: [validation-format.md](../validation/validation-format.md)

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative |
| Spec | Preferred | Path or inline YAML |
| Subtask list | Preferred | Path or inline markdown |
| Execution | Preferred | Path or inline YAML when present |
| Review guidance | Optional | Path or inline YAML with `important-considerations` |
| Review output path | No | Default `current-task/reviews/<slug>.yaml` under scope root |

If worktree path is missing, ask before starting.

If spec or subtask list is missing, ask whether to proceed with partial review or stop.

Missing execution YAML is not a blocker when spec, subtasks, and diff are enough to review.

## Procedure

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load spec, subtask list, execution, optional guidance
- [ ] Discover changes (git diff)
- [ ] Check requirement coverage
- [ ] Check subtask list completion and adherence
- [ ] Run acceptance / verify commands
- [ ] Spot-check CONTRIBUTING conventions
- [ ] Decide approved true/false
- [ ] Write review YAML
- [ ] Validation per validation-format.md
- [ ] Append ## Fix when fix_required
- [ ] Report summary and echo both paths
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists.
3. Set the **scope root** to that absolute path. Derive `<slug>` from the final folder name.
4. Default review output: `current-task/reviews/<slug>.yaml`.

**Scope rules (non-negotiable):**

- **Read** anywhere under the scope root and CONTRIBUTING.md.
- **Write** review path, `current-task/review-validations/rN-validation.yaml`, and `current-task/next-steps/*.yaml` when deferred scope findings warrant follow-up.
- **Append** `## Fix` on subtask list only when `fix_required`.
- Never edit `src/`, `app/`, config, tests, specs, subtasks, or any application files.
- Never modify files outside the scope root.
- Run shell commands with `working_directory` set to the scope root.

### Step 2: Load inputs

1. Load spec from path or inline YAML.
2. Load subtask list from path or inline markdown.
3. Load execution handoff from path or inline YAML when present.
4. Load optional review guidance when provided.
5. If spec or subtask list is missing, ask before continuing with partial review.
6. Extract: `requirements`, `scope`, `acceptance`, `constraints` from spec; checklist lines and completion state from subtasks; touched paths, subtask statuses, verification evidence, deviations, and hotspots from execution.
7. Extract `important-considerations` from review guidance when present.
8. Treat execution handoff and review guidance as guidance only. The git diff, source files, and rerun verification decide approval.

### Step 2a: Apply important considerations

When review guidance is present:

- Keep each `important-considerations` item in scope while reviewing.
- Do not repeat findings that the guidance says were out of scope or wrong unless current source evidence proves they are real in-scope blockers.
- Still report build, lint, test, safety, correctness, requirement, subtask, and convention issues when supported by evidence.
- Do not copy `important-considerations` into the output YAML. The review output still has exactly `approved` and `content`.

### Step 3: Discover changes

From the scope root, inspect what changed:

- `git diff main...HEAD --name-only` (or `git diff --name-only` if no merge base with main)
- `git diff main...HEAD` for relevant files

Flag files changed that are:

- Listed in spec `scope.out`
- Not implied by any subtask line (possible scope creep)
- Missing from execution `paths` or marked `unplanned: []` despite appearing in the diff

### Step 4: Requirement coverage

For each spec `requirements[].id`:

- Read the implementation (and tests if applicable) in the worktree
- Confirm the requirement description is satisfied
- Record blocking gaps as `[req-<id>]` bullets for `content`

### Step 5: Subtask list adherence

For each subtask line:

- Confirm checked `- [x]` items are actually done in the diff and source
- Confirm unchecked `- [ ]` items are not silently skipped when execution claims `status: complete`
- Compare execution `subtasks` entries with checklist completion state
- Record skipped or incorrect subtasks as `[subtask:<index>]` bullets

If execution `deviations`, `open_questions`, or `review_scope.mode: triage` indicate partial or blocked work, do not approve unless the review scope explicitly excludes the incomplete work and the user asked for that narrower review.

### Step 6: Acceptance and verify

1. Run verification commands from unchecked verification subtasks or spec `acceptance` from the scope root.
2. If no verification subtasks exist, run CONTRIBUTING defaults: `npm run lint`, `npm test` (scoped to affected areas when possible).
3. Compare rerun results with execution `verify` evidence when present.
4. Map results to spec `acceptance` criteria.
5. Record failures as `[verify]` bullets with command output context.

### Step 7: Convention check

Spot-check [CONTRIBUTING.md](../../../CONTRIBUTING.md) rules relevant to the task:

- Semantic Tailwind tokens (no raw palette classes when spec requires tokens)
- i18n via `useTranslations` when strings were added
- `no-new-deps` constraint — inspect `package.json` diff if constrained
- Project layout expectations for new modules
- Execution `hotspots` when present

Record blocking violations as `[convention]` bullets.

### Step 8: Decide `approved`

- `approved: true` only when **no blocking issues** remain across requirements, subtasks, verify, and conventions.
- `[scope]` bullets alone do **not** force `approved: false` — list them under `[scope]` for deferred follow-up.
- Any blocking issue (`[req-`, `[subtask:`, `[verify]`, `[convention]`) → `approved: false`.
- Do not include non-blocking nits unless the user requested strict review.

### Step 9: Write review YAML

1. Create the review output directory if it does not exist.
2. Write the complete YAML per [review-format.md](review-format.md).
3. Echo the same YAML in the report.

### Step 10: Validation

Follow [validation-format.md](../validation/validation-format.md) on the review just written.

### Step 11: Report

Summarize: scope root, inputs used, files reviewed, commands run, review path, validation path, `readiness.status`, next-step paths.

## Safety rules

- Never edit application code — only review YAML files
- Never modify specs or subtask lists during review
- Never modify files outside the scope root
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- Do not commit or push unless the user explicitly asks
- When in doubt, ask — do not guess pass/fail
- Do not include `important-considerations` in review output; it is input-only
