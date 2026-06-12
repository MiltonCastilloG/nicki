# Per-task status.json format

Per-task workflow state inside the active worktree. **JSON only.** Replaces the orchestration role of `status.json`.

Path: `current-task/status.json` relative to task worktree root.

**Write boundary:** only status-update agent (`current-task-update` command). Nicki and leaf agents read only.

Handoff YAML/Markdown bodies stay separate; status holds pointers and step position only.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `version` | Yes | Schema version; use `1` |
| `meta` | Yes | Writer metadata |
| `task` | Yes | Identity and step pointers |
| `scope` | Yes | Worktree slug and path |
| `artifacts` | Yes | Paths to handoff files (relative to worktree) |
| `constraints` | No | Inherited rules (e.g. `no-commit`, `no-new-deps`) |
| `open_questions` | Yes | Blockers; empty array when unblocked |
| `history` | Yes | Append-only workflow events |

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `schema` | Yes | `task-status.v1` |
| `generated_by` | Yes | `status-update` |
| `updated_by` | Yes | `status-update` |

## `task`

| Field | Required | Description |
|-------|----------|-------------|
| `id` | No | Task id from global registry when known |
| `slug` | Yes | Worktree folder slug |
| `project` | No | Managed project name |
| `title` | No | Short title |
| `original` | Yes | Raw user task text from start |
| `story_artifact` | No | Path to Gherkin story markdown (preferred over inline story) |
| `type` | No | `feature`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf` |
| `current_step` | Yes | Step Nicki is on or just completed |
| `next_step` | Yes | Next step Nicki should propose |
| `last_completed_step` | No | Latest completed step |

Step values: `start`, `describe`, `spec`, `subtasks`, `execute`, `review`, `triage`, `fix`, `acceptance`, `commit`, `push`, `merge`, `publish`, `close`, `done`.

## `scope`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Slug |
| `worktree_path` | Yes | Repo-relative or absolute worktree path |

## `artifacts`

| Field | Required | Description |
|-------|----------|-------------|
| `status` | Yes | `current-task/status.json` |
| `story` | No | `current-task/story.md` |
| `spec` | No | Spec YAML path |
| `subtasks` | No | Subtask markdown path |
| `execution` | No | Execution YAML path |
| `review` | No | Review YAML path |
| `review_validation` | No | Latest validation YAML |
| `review_input` | No | Latest review guidance YAML |
| `next_steps` | No | Array of follow-up spec paths |
| `commit` | No | Commit handoff path |
| `push` | No | Push handoff path |
| `merge` | No | Merge handoff path |
| `publish` | No | Publish handoff path when used |
| `archive` | No | Archive path at project root |

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

## `history`

Append one event per status update:

```json
{
  "step": "spec",
  "status": "complete",
  "artifact": "current-task/specs/hero-section.yaml",
  "summary": "Spec captured requirements and acceptance."
}
```

Status values: `complete`, `blocked`, `failed`, `skipped`.

## Readiness routing

After triage, status-update sets `artifacts.review_validation` to latest validation YAML. Nicki + hooks read `readiness` from that file — **not** review markdown, **not** chat.

| `readiness.status` | `task.next_step` typical | `commit-task` |
|--------------------|--------------------------|---------------|
| `ready_for_acceptance` | `acceptance` | blocked until user accepts |
| `fix_required` | `execute` | blocked |
| `rerun_review` | `review` | blocked |
| `blocked` | `blocked` or ask user | blocked |

### Validation pointer

`artifacts.review_validation` → `current-task/review-validations/rN-validation.yaml`. Refresh on every triage complete.

### Fix-loop history

When triage reruns after fix execute, append history:

```json
{ "step": "fix", "status": "complete", "artifact": "current-task/review-validations/r2-validation.yaml", "summary": "Fix loop iteration 2." }
```

### Acceptance

Nicki-only step after `ready_for_acceptance`. On user accept, history records `step: acceptance`; `next_step` may advance to `commit` (still needs git confirm). On reject, update `open_questions` / blockers; route `execute` or `describe` per user.

### Spec `open_questions` mirror

When spec handoff has non-empty `open_questions`, status-update mirrors into `open_questions` and blocks `next_step: subtasks` until cleared.

## Resolved defaults (status-architecture task)

| Decision | Choice |
|----------|--------|
| User story | `current-task/story.md` + `task.story_artifact` pointer |
| Blocked state | Non-empty `open_questions` + blocking `next_step` until cleared or override |
| Caveman MD | Full intensity for workflow Markdown handoffs per caveman skill |

## Example

```json
{
  "version": 1,
  "meta": {
    "schema": "task-status.v1",
    "generated_by": "status-update",
    "updated_by": "status-update"
  },
  "task": {
    "id": "42",
    "slug": "hero-section",
    "project": "castlemill-landing",
    "original": "hero-section",
    "story_artifact": "current-task/story.md",
    "type": "feature",
    "current_step": "spec",
    "next_step": "subtasks",
    "last_completed_step": "describe"
  },
  "scope": {
    "worktree": "hero-section",
    "worktree_path": "projects/castlemill-landing/worktrees/hero-section"
  },
  "artifacts": {
    "status": "current-task/status.json",
    "story": "current-task/story.md",
    "spec": "current-task/specs/hero-section.yaml"
  },
  "constraints": ["no-commit", "no-new-deps"],
  "open_questions": [],
  "history": [
    {
      "step": "start",
      "status": "complete",
      "artifact": "current-task/status.json",
      "summary": "Worktree created. Task registered in global-status.json."
    }
  ]
}
```

## Handoff meta scopes

| Root | Role |
|------|------|
| Workspace | `global-status.json`, `task-archive/` |
| Project | `projects/<project>/` git repo root |
| Task worktree | `projects/<project>/worktrees/<slug>/`, `current-task/*` |
| Target branch | project checkout for merge/publish (`main` default) |
