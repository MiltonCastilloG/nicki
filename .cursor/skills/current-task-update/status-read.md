# Status input (read-only)

Per-task `current-task/status.json`. Writer schema: [status-format.md](status-format.md).

**Nicki bootstrap:** `bootstrap-context.py` stdout supplies `next_step`, `completed_steps`, and `readiness` — do not re-read status fields during bootstrap.

## Fields Nicki uses

| Section | Fields |
|---------|--------|
| `task` | `slug`, `title`, `original`, `current_step`, `next_step`, `completed_steps` (optional) |
| `scope` | `worktree_path` |
| `artifacts` | Paths to story, spec, subtasks, execution, `review_validation`, sync, integrate, archive |
| `open_questions` | Blockers — empty array when pipeline can continue |

Step values: `start`, `describe`, `spec`, `subtasks`, `execute`, `review`, `fix`, `acceptance`, `sync`, `archive`, `integrate`, `close`, `done`.

## Minimal shape

```json
{
  "task": {
    "slug": "hero-section",
    "original": "hero-section",
    "current_step": "spec",
    "next_step": "subtasks"
  },
  "scope": {
    "worktree_path": "projects/foo/worktrees/hero-section"
  },
  "artifacts": {
    "story": "current-task/story.md",
    "spec": "current-task/specs/hero-section.yaml",
    "review_validation": "current-task/review-validations/r1-validation.yaml"
  },
  "open_questions": []
}
```
