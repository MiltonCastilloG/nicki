---
name: current-task-update
description: "Update current-task/status.json from a compact Nicki workflow summary. Status-update writer — never touches global-status.json. Use when Nicki finishes a workflow step."
disable-model-invocation: true
---

# Status update (current-task-update)

Update per-task workflow state from Nicki summary. Writes exactly one file: `current-task/status.json` under the task worktree.

**Never write `global-status.json`.** Registry write boundary: [global-status-format.md](global-status-format.md).

Schemas:

- Per-task: [status-format.md](status-format.md)
- Global registry (read only): [global-status-read.md](global-status-read.md)
- Legacy (deprecated): [current-task-context-format.md](current-task-context-format.md)

## When to use

- Nicki completed `start`, `describe`, `spec`, `subtasks`, `execute`, `review`, `acceptance`, `sync`, `integrate`, or fix-loop routing.
- Nicki needs next step, artifact pointers, or open questions persisted.
- Worktree exists; need init missing `current-task/status.json`.

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative |
| Nicki summary | Yes | Compact JSON summary of step result |

## Nicki summary format

**Required:** `next_step` only (plus worktree via CLI). Not required with `--mode adhoc`.

**Optional:** `completed_step`, `artifact`, `completed_status`, `open_questions`, `summary`.

**`completed_status` is a closed set:** `complete` or `blocked`. Any other value is an
input error — nothing is written. Only `complete` appends to `completed_steps`.

**CLI:** `--step <name>` names the dispatched step and wins over summary
`completed_step`. `--mode normal|adhoc` selects whether the write moves the task.

Minimal write (valid — advances next step only):

```json
{
  "next_step": "describe"
}
```

Full write (when a step completed):

```json
{
  "worktree": "projects/foo/worktrees/hero-section",
  "completed_step": "spec",
  "completed_status": "complete",
  "artifact": "current-task/specs/hero-section.json",
  "next_step": "subtasks",
  "open_questions": [],
  "summary": "Spec captured requirements and acceptance."
}
```

**`completed_step` semantics:** when present, updates `task.current_step`, may append `completed_steps`, and may set artifact pointer; when absent, only advances `next_step` but **always writes `task.current_step`** (preserve existing, or `"start"` on fresh init).

Also optional: `task` (slug, title, original, type), `git`, `artifacts`.

For describe: set `artifacts.story: current-task/story.md` and write story body terse per caveman skill when summary includes full story text — otherwise Nicki passes story for a dedicated write step.

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
- If missing: init from summary with `meta.schema: task-status.v2`.
- Ask when summary conflicts with existing status.

### Step 3: Apply update

Emit simplified shape on every write. **Legacy migration:** when loading v1 status, drop `version`, `meta.generated_by`, `meta.updated_by`, `scope.worktree`, `task.story_artifact`, `artifacts.status`, `artifacts.review`, `task.last_completed_step`, `constraints`, and `history` — preserve essential routing fields and artifact pointers.

- `meta.schema: task-status.v2` only — do not write `meta.updated_by` or other ceremony fields
- `task.current_step`, `task.next_step`
- Merge `artifacts`; after review set `artifacts.review_validation` to latest validation path from summary `artifact`
- **Describe:** replace `task.original` with slug or one-line title; set `artifacts.story`
- **completed_steps:** append `completed_step` name when `completed_status: complete` (init `[]` when absent); omit verbose `history`
- Fix-loop: when `completed_step: fix` or review reruns after fix, append `fix` to `completed_steps`
- Acceptance: when `completed_step: acceptance`, append `acceptance` to `completed_steps`; reject may populate `open_questions`
- **Ad-hoc (`--mode adhoc`):** leave `current_step`, `next_step`, and `completed_steps` untouched; record the artifact pointer and append one `task.side_effects` entry. Needs an existing `status.json` — ad-hoc never initialises a task.
- `open_questions` from summary; blocked when non-empty

### Step 4: Write and report

Report status path, completed step, next step, open questions.

## Safety rules

- Write only `current-task/status.json`.
- Never write `global-status.json`.
- Never write deprecated `status.json` for new tasks.
