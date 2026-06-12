# Status input (read-only)

Per-task `current-task/status.json`. Nicki and other sheep **read** for routing and gates. Writer schema: [status-format.md](status-format.md).

## Fields Nicki uses

| Section | Fields |
|---------|--------|
| `task` | `slug`, `title`, `original`, `story_artifact`, `current_step`, `next_step`, `last_completed_step` |
| `scope` | `worktree`, `worktree_path` |
| `artifacts` | Paths to story, spec, subtasks, execution, review, `review_validation`, sync, integrate, archive |
| `open_questions` | Blockers — empty array when pipeline can continue |
| `constraints` | Inherited rules when present |

Step values: `start`, `describe`, `spec`, `subtasks`, `execute`, `review`, `fix`, `acceptance`, `sync`, `integrate`, `close`, `done`.

## Gates

- **`describe` → `spec`:** `task.story_artifact` must exist.
- **`spec` → `subtasks`:** spec artifact `open_questions` must be empty (load spec file when checking).
- **Post-review routing:** read `readiness` from validation YAML at `artifacts.review_validation` — not from status or review markdown.

## Readiness (from validation YAML)

| `readiness.status` | Route | Sync |
|--------------------|-------|------|
| `ready_for_acceptance` | acceptance | blocked |
| `fix_required` | execute | blocked |
| `blocked` | ask user | blocked |

## Minimal shape

```json
{
  "task": {
    "slug": "hero-section",
    "original": "hero-section",
    "story_artifact": "current-task/story.md",
    "current_step": "spec",
    "next_step": "subtasks"
  },
  "scope": {
    "worktree": "hero-section",
    "worktree_path": "projects/foo/worktrees/hero-section"
  },
  "artifacts": {
    "spec": "current-task/specs/hero-section.yaml",
    "review_validation": "current-task/review-validations/r1-validation.yaml"
  },
  "open_questions": []
}
```
