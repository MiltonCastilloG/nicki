# Per-task status.json format

Per-task workflow state inside the active worktree. **JSON only.**

Path: `current-task/status.json` relative to task worktree root.

**Write boundary:** only `current-task-update`. Readers use [status-read.md](status-read.md).

Handoff YAML/Markdown bodies stay separate; status holds pointers and step position only.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Schema identifier only |
| `task` | Yes | Identity and step pointers |
| `scope` | Yes | Worktree path |
| `artifacts` | Yes | Paths to handoff files (relative to worktree) |
| `open_questions` | Yes | Blockers; empty array when unblocked |

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `schema` | Yes | `task-status.v2` |

## `task`

| Field | Required | Description |
|-------|----------|-------------|
| `id` | No | Task id from global registry when known |
| `slug` | Yes | Worktree folder slug |
| `project` | No | Managed project name |
| `title` | No | Short title |
| `original` | Yes | Short slug or one-line title after describe; start slug until then |
| `type` | No | `feature`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf` |
| `current_step` | Yes | Step Nicki is on or just completed |
| `next_step` | Yes | Next step Nicki should propose |
| `completed_steps` | No | Step names completed so far (e.g. `["start", "describe", "spec"]`) |

Step values: `start`, `describe`, `spec`, `subtasks`, `execute`, `review`, `fix`, `acceptance`, `sync`, `archive`, `integrate`, `close`, `done`.

## `scope`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree_path` | Yes | Repo-relative or absolute worktree path |

## `artifacts`

| Field | Required | Description |
|-------|----------|-------------|
| `story` | No | `current-task/story.md` |
| `spec` | No | Spec YAML path |
| `subtasks` | No | Subtask markdown path |
| `execution` | No | Execution YAML path |
| `review_validation` | No | Latest validation YAML — sole review gate pointer |
| `review_input` | No | Latest review guidance YAML |
| `next_steps` | No | Array of follow-up spec paths |
| `sync` | No | Sync handoff path (`current-task/syncs/<slug>.yaml`) |
| `integrate` | No | Integrate handoff path (`current-task/integrates/<slug>.yaml`) |
| `archive` | No | `docs/archive/<slug>/report.yaml` (dir also holds `report.md`, `story.md`) |

## `open_questions`

Empty when Nicki can continue:

```json
"open_questions": []
```

Blocked example:

```json
"open_questions": [
  {
    "step": "subtasks",
    "question": "CTA link /contact or /demo?",
    "blocks_next_step": true
  }
]
```

## Readiness routing

After review, status-update sets `artifacts.review_validation` to latest validation YAML. Nicki + hooks read `readiness` from that file — **not** review markdown, **not** status history.

| `readiness.status` | `task.next_step` typical | `sync-task` |
|--------------------|--------------------------|-------------|
| `ready_for_acceptance` | `acceptance` | blocked until user accepts |
| `fix_required` | `execute` | blocked |
| `rerun_review` | `review` | blocked |
| `blocked` | `blocked` or ask user | blocked |

### Validation pointer

`artifacts.review_validation` → `current-task/review-validations/rN-validation.yaml`. Refresh on every review complete.

### Acceptance

Nicki-only step after `ready_for_acceptance`. On user accept, append `acceptance` to `completed_steps`; `next_step` may advance to `sync` (still needs git confirm). On reject, update `open_questions` / blockers; route `execute` or `describe` per user.

### Spec `open_questions` gate

Spec-to-subtasks gate reads `open_questions` from the spec artifact file — not mirrored on status.

## Example

```json
{
  "meta": { "schema": "task-status.v2" },
  "task": {
    "id": "42",
    "slug": "hero-section",
    "project": "castlemill-landing",
    "original": "hero-section",
    "type": "feature",
    "current_step": "spec",
    "next_step": "subtasks",
    "completed_steps": ["start", "describe"]
  },
  "scope": {
    "worktree_path": "worktrees/castlemill-landing-hero-section"
  },
  "artifacts": {
    "story": "current-task/story.md",
    "spec": "current-task/specs/hero-section.yaml"
  },
  "open_questions": []
}
```

## Handoff meta scopes

| Root | Role |
|------|------|
| Workspace | `global-status.json`, `docs/archive/` |
| Project | `projects/<project>/` git repo root |
| Task worktree | `worktrees/<project>-<slug>/`, `current-task/*` |
| Target branch | project checkout for integrate (`main` default) |
