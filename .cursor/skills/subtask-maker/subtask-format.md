# Subtask list format

**Markdown only** — subtask-maker writes; execute-plan reads via [subtask-input.md](subtask-input.md).

Default path: `current-task/subtasks/<slug>.md` under the worktree scope root.

## File structure

1. YAML frontmatter — scope and traceability.
2. `# Subtasks` heading — required.
3. Checklist body — ordered `- [ ]` lines.

## Frontmatter fields

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug (e.g. `hero-section`) |
| `generated_by` | Yes | Always `subtask-maker` |
| `spec` | Yes when a spec exists | Path to the spec file |
| `context` | No | Traceability path when agent sets one |
| `title` | No | Short task name from the spec |
| `constraints` | No | Default `no-commit`, `no-new-deps` |

## Checklist line rules

One **terse sentence** per line — no filler (just, basically, really); keep technical terms exact.

**Do:** one buildable outcome per line; dependencies first; **verify-before-build** when existing code may already satisfy a requirement; **refactor-to-share** when similar logic exists instead of duplicating it; test subtasks when spec implies coverage; verification subtasks last from spec `acceptance`; map every requirement and acceptance item.

**Don't:** multiple sentences on one line; symbol names in text (verification may name checks, e.g. "Run npm run lint on changed files"); vague lines; skip implied tests;  drop a requirement because you think it is already done — write a verify line instead.

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
- [ ] Run npm run lint on changed files and fix any issues.
- [ ] Run npm test for Hero and home page test suites.
```

When exploration finds existing coverage, prefer lines like:

```markdown
- [ ] Confirm the home page hero already meets headline, subcopy, and CTA requirements and change nothing if it does.
- [ ] Extract shared CTA button styling from the footer component and reuse it in the hero instead of duplicating button logic.
- [ ] Wire the existing Hero component into the home page only where the hero area is still missing it.
```

Spec input (read): [spec-input.md](spec-input.md). Execute input (read): [subtask-input.md](subtask-input.md). Full spec schema: [spec-format.md](../spec-maker/spec-format.md).
