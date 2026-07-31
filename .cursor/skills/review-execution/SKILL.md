---
name: review-execution
description: "Review worktree changes against available current-task files and the git diff; write a JSON review with approved and content."
---

# Review Execution

Review implementation in a worktree. Compare changes against available story/spec/subtasks, optional review guidance, and the **actual git diff**; run verification checks; produce JSON with exactly `approved` and `content`.

**Never load execution JSON.** Diff + whatever exists under `current-task/` is enough.

- Review output: [review-format.md](review-format.md)
- Guidance input: [review-guidance-format.md](review-guidance-format.md)
- Post-review validation: [validation-format.md](../validation/validation-format.md)

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative |
| Review material | Yes* | Diff under the worktree plus whatever the prompt / `current-task/` supplies |
| Review output path | No | Default `current-task/reviews/<slug>.json` under scope root |

\*Ask when the worktree path is missing, or when the diff alone is unclear and no usable planning files exist.

Never load execution JSON.

## Procedure

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load whatever the prompt and current-task/ supply (never execution JSON)
- [ ] Discover changes (git diff)
- [ ] Check requirement coverage when a spec is available
- [ ] Check subtask list completion when available
- [ ] Run acceptance / verify commands
- [ ] Spot-check CONTRIBUTING conventions
- [ ] Decide approved true/false
- [ ] Write review JSON
- [ ] Validation per validation-format.md
- [ ] Append ## Fix when fix_required
- [ ] Report summary and echo both paths
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists.
3. Set the **scope root** to that absolute path. Derive `<slug>` from the final folder name.
4. Default review output: `current-task/reviews/<slug>.json`.

**Scope rules (non-negotiable):**

- **Read** anywhere under the scope root and CONTRIBUTING.md.
- **Write** review path, `current-task/review-validations/rN-validation.json`, and `current-task/next-steps/*.json` when deferred scope findings warrant follow-up.
- **Append** `## Fix` on subtask list only when `fix_required`.
- Never edit `src/`, `app/`, config, tests, specs, subtasks, or any application files.
- Never modify files outside the scope root.
- Run shell commands with `working_directory` set to the scope root.

### Step 2: Load inputs

1. Load whatever the prompt and `current-task/` supply (spec, subtasks, story, review guidance) — never execution JSON.
2. Extract what exists: `requirements`, `scope`, `acceptance`, `constraints` from spec; checklist lines from subtasks; `important-considerations` from guidance; partial `review_scope` from the prompt when supplied.
3. Treat review guidance as guidance only. The git diff, source files, and rerun verification decide approval.

### Step 2a: Apply important considerations

When review guidance is present:

- Keep each `important-considerations` item in scope while reviewing.
- Do not repeat findings that the guidance says were out of scope or wrong unless current source evidence proves they are real in-scope blockers.
- Still report build, lint, test, safety, correctness, requirement, subtask, and convention issues when supported by evidence.
- Do not copy `important-considerations` into the output JSON. The review output still has exactly `approved` and `content`.

### Step 3: Discover changes

From the scope root, inspect what changed:

- `git diff main...HEAD --name-only` (or `git diff --name-only` if no merge base with main)
- `git diff main...HEAD` for relevant files

Flag files changed that are:

- Listed in spec `scope.out` when a spec is present
- Not implied by any subtask line when a checklist is present (possible scope creep)

### Step 4: Requirement coverage

When a spec is present, for each `requirements[].id`:

- Read the implementation (and tests if applicable) in the worktree
- Confirm the requirement description is satisfied
- Record blocking gaps as `[req-<id>]` bullets for `content`

### Step 5: Subtask list adherence

When a subtask list is present, for each line:

- Confirm checked `- [x]` items are actually done in the diff and source
- Confirm unchecked `- [ ]` items are not silently skipped when the user asked for a full review
- Record skipped or incorrect subtasks as `[subtask:<index>]` bullets

If the prompt or review-input supplies `review_scope.mode: partial` or triage, do not approve incomplete out-of-scope work unless that narrower review was confirmed.

### Step 6: Acceptance and verify

1. Run verification commands from unchecked verification subtasks or spec `acceptance` from the scope root when available.
2. If no verification subtasks exist, run CONTRIBUTING defaults: `npm run lint`, `npm test` (scoped to affected areas when possible).
3. Map results to spec `acceptance` criteria when present.
4. Record failures as `[verify]` bullets with command output context.

### Step 7: Convention check

Spot-check [CONTRIBUTING.md](../../../CONTRIBUTING.md) rules relevant to the task:

- Semantic Tailwind tokens (no raw palette classes when spec requires tokens)
- i18n via `useTranslations` when strings were added
- `no-new-deps` constraint — inspect `package.json` diff if constrained
- Project layout expectations for new modules

Record blocking violations as `[convention]` bullets.

### Step 8: Decide `approved`

- `approved: true` only when **no blocking issues** remain across requirements, subtasks, verify, and conventions.
- `[scope]` bullets alone do **not** force `approved: false` — list them under `[scope]` for deferred follow-up.
- Any blocking issue (`[req-`, `[subtask:`, `[verify]`, `[convention]`) → `approved: false`.
- Do not include non-blocking nits unless the user requested strict review.

### Step 9: Write review JSON

1. Create the review output directory if it does not exist.
2. Write the complete JSON per [review-format.md](review-format.md).
3. Echo the same JSON in the report.

### Step 10: Validation

Follow [validation-format.md](../validation/validation-format.md) on the review just written.

### Step 11: Report

Summarize: scope root, inputs used, files reviewed, commands run, review path, validation path, `readiness.status`, next-step paths.

## Safety rules

- Never edit application code — only review JSON files
- Never modify specs or subtask lists during review (except `## Fix` append when required)
- Never load or require `current-task/executions/*.json`
- Never modify files outside the scope root
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- Do not commit or push unless the user explicitly asks
- When in doubt, ask — do not guess pass/fail
- Do not include `important-considerations` in review output; it is input-only
