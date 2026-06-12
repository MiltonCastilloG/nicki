---
name: current-task-update
description: "Update current-task/status.json from a compact Nicki workflow summary. Status-update writer — never touches global-status.json. Use when Nicki finishes a workflow step."
disable-model-invocation: true
---

# Status update (current-task-update)

Update per-task workflow state from Nicki summary. Invoked by **sheep-status**. Writes exactly one file: `current-task/status.json` under the task worktree.

**Never write `global-status.json`.** Registry is sheep-start / sheep-close only.

Schemas:

- Per-task: [status-format.md](status-format.md)
- Global registry (read only): [global-status-read.md](global-status-read.md)
- Legacy (deprecated): [current-task-context-format.md](current-task-context-format.md)

## When to use

- Nicki completed `start`, `describe`, `spec`, `subtasks`, `execute`, `review`, `acceptance`, `sync`, `integrate`, or fix-loop routing.
- Nicki needs next step, artifact pointers, open questions, or history persisted.
- Worktree exists; need init missing `current-task/status.json`.

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative |
| Nicki summary | Yes | Compact YAML summary of step result |

## Nicki summary format

```yaml
worktree: projects/foo/worktrees/hero-section
completed_step: spec
completed_status: complete
artifact: current-task/specs/hero-section.yaml
next_step: subtasks
open_questions: []
summary: Spec captured requirements and acceptance.
```

Optional: `task` (slug, title, original, story_artifact, type), `git`, `artifacts`, `constraints`.

For describe: set `task.story_artifact: current-task/story.md` and write story body terse per caveman skill when summary includes full story text — otherwise Nicki passes story for a dedicated write step.

## Workflow

```
Task Progress:
- [ ] Resolve worktree scope
- [ ] Load existing status.json if present
- [ ] Parse Nicki summary
- [ ] Validate transition
- [ ] Write current-task/status.json
- [ ] Report updated step and next step
```

### Step 1: Resolve scope

1. Resolve worktree to absolute path.
2. Derive `<slug>` from folder name.
3. Output: `current-task/status.json`.

**Scope rules:**

- Read `current-task/status.json` and artifact paths needed to validate.
- Write only `current-task/status.json`.
- **Never write `global-status.json`.**
- No shell commands.

### Step 2: Load and validate

- Validate against [status-format.md](status-format.md).
- `scope.worktree_path` must match command worktree.
- If missing: init from summary with `meta.schema: task-status.v1`, default `artifacts.status`, default `constraints: [no-commit, no-new-deps]`.
- Ask when summary conflicts with existing status.

### Step 3: Apply update

- `meta.updated_by: status-update`
- `task.current_step`, `task.next_step`, `task.last_completed_step` when complete
- Merge `artifacts`; after review set `artifacts.review_validation` to latest validation path from summary `artifact`
- Mirror spec `open_questions` into status when summary includes them
- Fix-loop: when `completed_step: fix` or review reruns after fix, append `history` with `step: fix` and validation path
- Acceptance: when `completed_step: acceptance`, record user accept/reject in `history`; reject may populate `open_questions`
- `open_questions` from summary; blocked when non-empty
- Append `history` event

### Step 4: Write and report

Report status path, completed step, next step, open questions.

## Safety rules

- Write only `current-task/status.json`.
- Never write `global-status.json`.
- Never write deprecated `status.json` for new tasks.