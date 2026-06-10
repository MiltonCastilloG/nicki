# Subtask list format

Subtask lists drive `/execute-plan`. **Markdown only** — `/subtask-maker` writes the file; `/execute-plan` reads it, implements unchecked items in order, and flips `- [ ]` to `- [x]` as each subtask completes.

Store subtask lists in the worktree under `current-task/subtasks/` (e.g. `current-task/subtasks/hero-section.md`).

All agent artifacts for the active task live under `current-task/`:

```
current-task/
  current-task-context.yaml   # workflow context from /current-task-update
  specs/<slug>.yaml           # from /spec-maker
  subtasks/<slug>.md          # from /subtask-maker
  executions/<slug>.yaml      # from /execute-plan
  reviews/<slug>.yaml         # from /review-execution
  review-validations/         # from /review-triage
  review-inputs/
  next-steps/                 # follow-up specs consumable by /subtask-maker
  merges/
  commits/
  pushes/
```

Subtask lists define **what to build**, one atomic sentence per line — not file paths or create/modify steps. `/execute-plan` decides how to implement each line.

## File structure

1. **YAML frontmatter** — metadata for scope and traceability.
2. **`# Subtasks` heading** — required.
3. **Checklist body** — ordered `- [ ]` lines; executor marks `- [x]` when done.

## Frontmatter fields

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug (e.g. `hero-section`) |
| `generated_by` | Yes | Always `subtask-maker` |
| `spec` | Yes when a spec exists | Path to the spec file (e.g. `current-task/specs/hero-section.yaml`) |
| `context` | No | Path to task context (e.g. `current-task/current-task-context.yaml`) |
| `title` | No | Short task name from the spec |
| `constraints` | No | Rules for downstream agents (default `no-commit`, `no-new-deps`) |

## Checklist line rules

Each subtask is exactly **one sentence** on its own line:

```markdown
- [ ] Implement a Hero component with headline, subcopy, and a primary CTA using semantic Tailwind tokens only.
```

**Do:**

- Write one clear, buildable outcome per line.
- Order subtasks for sequential implementation (dependencies first).
- Include **test subtasks** — unit, integration, or component tests the spec implies.
- Include **verification subtasks** at the end (`npm run lint`, scoped `npm test`, etc.) mapped from spec `acceptance`.
- Map every spec `requirement` and `acceptance` item to at least one subtask.
- Start every unchecked item with `- [ ]` and every completed item with `- [x]`.

**Don't:**

- Use multiple sentences on one line.
- Name file paths or shell commands in the subtask text (except verification subtasks may name the check, e.g. "Run npm run lint on changed files").
- Split one requirement across vague lines ("improve hero", "clean up code").
- Skip tests when the spec or acceptance criteria imply them.

## Example

```markdown
---
worktree: hero-section
generated_by: subtask-maker
spec: current-task/specs/hero-section.yaml
context: current-task/current-task-context.yaml
title: Hero section redesign
constraints:
  - no-commit
  - no-new-deps
---

# Subtasks

- [ ] Implement a Hero component with headline, subcopy, and a primary CTA using semantic Tailwind tokens only.
- [ ] Replace the home page hero with the new Hero component above the fold.
- [ ] Add unit tests asserting the Hero renders headline, subcopy, and CTA.
- [ ] Add or update home page tests to cover the hero section.
- [ ] Run npm run lint on changed files and fix any issues.
- [ ] Run npm test for Hero and home page test suites.
```

After partial execution:

```markdown
- [x] Implement a Hero component with headline, subcopy, and a primary CTA using semantic Tailwind tokens only.
- [x] Replace the home page hero with the new Hero component above the fold.
- [ ] Add unit tests asserting the Hero renders headline, subcopy, and CTA.
```

## Authoring for subtask-maker

When `/subtask-maker` writes a subtask list:

1. **Load the spec** — stop if `open_questions` is non-empty.
2. **Light exploration** — skim project layout so subtasks are realistic; do not draft file-level steps.
3. **One sentence per line** — each line is an atomic build or verify unit.
4. **Include tests** — separate subtasks for tests implied by requirements and acceptance.
5. **End with verification** — lint/test subtasks from spec `acceptance`.
6. **Write to `current-task/subtasks/<slug>.md`** — slug matches the worktree folder name.
7. **Hand off to execute-plan**:

   ```
   /execute-plan worktrees/<slug> @current-task/subtasks/<slug>.md
   ```

Spec schema (input): [spec-format.md](../spec-maker/spec-format.md).
