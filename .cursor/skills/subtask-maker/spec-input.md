# Spec input (read-only)

YAML spec at `current-task/specs/<slug>.yaml`. Subtask-maker **reads** specs; full writer schema: [spec-format.md](../spec-maker/spec-format.md).

## Gate

If `open_questions` is non-empty, **stop and ask** — do not write subtasks. Nicki blocks this step when questions remain.

## Fields to extract

| Field | Use |
|-------|-----|
| `title` | Subtask frontmatter `title` |
| `requirements` | Map each item to one or more checklist lines |
| `scope.in` / `scope.out` | Bound exploration and subtasks |
| `constraints` | Subtask frontmatter; respect during drafting |
| `acceptance` | Verification subtasks at end of checklist |
| `assumptions` | Context for realistic subtasks — do not expand scope |
| `meta.worktree` | Confirm slug matches worktree folder |

## Requirement items

Each `requirements` entry has `id` and `description`. Map every requirement and every acceptance item to at least one subtask.

## Minimal shape

```yaml
meta:
  worktree: hero-section
title: Hero section redesign
requirements:
  - id: hero-cta
    description: Include a primary CTA using existing link/button patterns.
scope:
  out:
    - Header, footer, and other pages
constraints:
  - no-commit
acceptance:
  - npm run lint passes
open_questions: []
```
