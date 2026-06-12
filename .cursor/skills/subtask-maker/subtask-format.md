# Subtask list format

**Markdown only** — subtask-maker writes; execute-plan reads, implements unchecked items in order, and flips `- [ ]` to `- [x]` as each completes.

Default path: `current-task/subtasks/<slug>.md` under the worktree scope root.

Subtask lists define **what to build**, one atomic sentence per line — not file paths or create/modify steps.

## File structure

1. **YAML frontmatter** — metadata for scope and traceability.
2. **`# Subtasks` heading** — required.
3. **Checklist body** — ordered `- [ ]` lines; executor marks `- [x]` when done.

## Frontmatter fields

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug (e.g. `hero-section`) |
| `generated_by` | Yes | Always `subtask-maker` |
| `spec` | Yes when a spec exists | Path to the spec file |
| `context` | No | Optional traceability path when the loading agent sets one |
| `title` | No | Short task name from the spec |
| `constraints` | No | Rules for execution (default `no-commit`, `no-new-deps`) |

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

Spec schema (input): [spec-format.md](../spec-maker/spec-format.md).
