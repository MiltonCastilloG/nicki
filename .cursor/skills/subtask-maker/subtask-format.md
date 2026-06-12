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

**Do:** one buildable outcome per line; dependencies first; test subtasks when spec implies coverage; verification subtasks last from spec `acceptance`; map every requirement and acceptance item.

**Don't:** multiple sentences on one line; file paths or symbol names in text (verification may name checks, e.g. "Run npm run lint on changed files"); vague lines; skip implied tests.

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

Spec input (read): [spec-input.md](spec-input.md). Execute input (read): [subtask-input.md](subtask-input.md). Full spec schema: [spec-format.md](../spec-maker/spec-format.md).
