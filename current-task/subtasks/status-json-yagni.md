---
worktree: nicki-status-json-yagni
generated_by: subtask-maker
spec: current-task/specs/status-json-yagni.yaml
context: current-task/status.json
title: YAGNI simplify per-task status.json
constraints:
  - no-commit
  - no-new-deps
---

# Subtasks

- [x] Choose the trimmed history shape (omit, completed_steps, or last_event) and document it in current-task-update write rules.
- [x] Rewrite status-format.md for the simplified canonical schema with essential routing fields, single schema identifier, no ceremony meta, no duplicate pointers, and optional-or-absent history.
- [x] Align status-read.md with status-format.md so gates and the minimal read surface match — one story pointer, review_validation as sole review gate, no redundant slug or step duplicates.
- [x] Update current-task-update apply rules to emit the simplified shape, shorten task.original after describe, stop verbose history append, and migrate legacy status on write without copying old history forward.
- [x] Update create-worktree scaffold initial status.json to match the simplified schema without duplicate pointers, ceremony meta, or verbose history.
- [x] Update status.example.json to match the simplified schema example from status-format.md.
- [x] Update task-archive and archive-format rules to derive report process from artifact presence and handoff meta under current-task, not from status history.
- [x] Confirm describe-to-spec gate still works via the single canonical story pointer documented in status-read.
- [x] Confirm spec-to-subtasks gate still reads open_questions from the spec artifact file only.
- [x] Confirm post-review routing still reads readiness from the review_validation artifact only.
- [x] Dogfood simplified status through this worktree pipeline updates without breaking documented readers.
- [x] Verify Nicki and sheep routing gates work with simplified status for describe, spec, and review paths.
- [x] Verify duplicate pointers, ceremony meta, and verbose history are absent from docs, scaffold, example, and this worktree status.json.
- [x] Verify task-archive can draft report process without reading status history.

## Fix
<!-- ref: current-task/review-validations/r1-validation.yaml -->
- [ ] Align completed_steps placement in status-format.md and status-read.md with task.completed_steps used by example, scaffold, and writers
