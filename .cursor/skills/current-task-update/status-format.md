# Per-task status.json format

Per-task workflow state inside the active worktree. **JSON only.**

Path: `current-task/status.json` relative to task worktree root.

**Write boundary:** only `current-task-update`. Readers use [status-read.md](status-read.md).

Handoff JSON/Markdown bodies stay separate; status holds pointers and step position only.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Schema identifier only |
| `task` | Yes | Identity and step pointers |
| `scope` | Yes | Worktree path |
| `artifacts` | Yes | Paths to handoff files — see [scope](#artifacts) |
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
| `side_effects` | No | Append-only log of out-of-band runs — see below |

Step values: `start`, `describe`, `spec`, `subtasks`, `execute`, `review`, `fix`, `acceptance`, `sync`, `archive`, `integrate`, `close`, `done`.

### `side_effects`

An ad-hoc step (`update-status.py --mode adhoc`) runs without moving the task:
`current_step` and `next_step` are left exactly as they were.
The artifact pointer is still recorded, and one entry is appended here so the run
is not invisible. A jump (`--mode jump`) also appends here: sets `next_step` to
the target and leaves `current_step` untouched; `artifact` is always `null` on
the jump log entry (jump carries no file). Position fields stay the source of
truth for *where the task is*; this log is the source of truth for *what else
happened*.

```json
"side_effects": [
  {"step": "sync", "mode": "adhoc", "at": "2026-07-29T08:14:02Z", "artifact": "current-task/syncs/foo.json"},
  {"step": "review", "mode": "jump", "at": "2026-07-30T12:00:00Z", "artifact": null}
]
```

## `scope`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree_path` | Yes | Repo-relative or absolute worktree path |

## `artifacts`

**Path scope.** Every pointer is **worktree-relative** (project repo under the
feature worktree). That includes `archive`: `docs/archive/<slug>/` is written in
the worktree, committed on the second sync, and lands on the target branch via
integrate. Gates always resolve `worktree / artifacts.<key>` — never against the
Nicki workspace root (historical mistake when Nicki was the only project).

| Field | Required | Description |
|-------|----------|-------------|
| `story` | No | `current-task/story.md` |
| `spec` | No | Spec JSON path |
| `subtasks` | No | Subtask markdown path |
| `review_validation` | No | Latest validation JSON — sole review gate pointer |
| `review_input` | No | Latest review guidance JSON |
| `next_steps` | No | Array of follow-up spec paths |
| `sync` | No | Sync handoff path (`current-task/syncs/<slug>.json`) |
| `integrate` | No | Integrate handoff path (`current-task/integrates/<slug>.json`) |
| `archive` | No | `docs/archive/<slug>/report.json` — worktree-relative (dir also holds `report.md`, `story.md`) |

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

After review, status-update sets `artifacts.review_validation` to latest validation JSON. Nicki + hooks read `readiness` from that file — **not** review markdown, **not** status history.

| `readiness.status` | `task.next_step` typical | `sync-task` |
|--------------------|--------------------------|-------------|
| `ready_for_acceptance` | `acceptance` | blocked until user accepts |
| `fix_required` | `execute` | blocked |
| `rerun_review` | `review` | blocked |
| `blocked` | `blocked` or ask user | blocked |

### Validation pointer

`artifacts.review_validation` → `current-task/review-validations/rN-validation.json`. Refresh on every review complete.

### Acceptance

Nicki-only step after `ready_for_acceptance`. On user accept, set `current_step` to
`acceptance` and derive `next_step` to `sync` (still needs git confirm). On reject,
update `open_questions` / blockers; route `execute` or `describe` per user.

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
    "next_step": "subtasks"
  },
  "scope": {
    "worktree_path": "worktrees/castlemill-landing-hero-section"
  },
  "artifacts": {
    "story": "current-task/story.md",
    "spec": "current-task/specs/hero-section.json"
  },
  "open_questions": []
}
```

## Handoff meta scopes

| Root | Role |
|------|------|
| Workspace | `global-status.json` (Nicki orchestrator) |
| Project / task worktree | git repo checkout: `worktrees/<project>-<slug>/`, `current-task/*`, `docs/archive/` |
| Target branch | project checkout for integrate (`main` default) |
