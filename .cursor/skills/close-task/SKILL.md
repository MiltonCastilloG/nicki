---
name: close-task
description: "Archive compact current-task context into task-archive/<slug>/summary.yaml and delete current-task/. Use after merge-task and current-task-update have recorded the final merge result."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: close-task
  tools:
    read: true
    write: true
    delete: true
    shell: true
    grep: false
    glob: true
    semantic_search: false
    task: false
    web_search: false
    web_fetch: false
    mcp: false
    ask_question: true
    todo_write: true
    generate_image: false
    switch_mode: false
---

# Close Task

Close a completed task by writing a compact root-level archive and deleting the worktree-local `current-task/` folder.

Archive schema: [archive-format.md](archive-format.md).

## When to use

- Nicki has completed `/merge-task`.
- Nicki has invoked `/current-task-update` after merge, so `current-task/current-task-context.yaml` includes the final merge result.
- The user confirmed Nicki's close prompt: `Time for the feedback woof! Want?`

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Task context | Preferred | Auto-load `current-task/current-task-context.yaml` |

If worktree path is missing, ask before starting.

If task context is missing, ask whether to archive from available `current-task/` artifacts or stop.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load current-task artifacts
- [ ] Draft compact archive YAML
- [ ] Write task-archive/<slug>/summary.yaml
- [ ] Delete current-task/
- [ ] Report archive path and deletion summary
```

### Step 1: Resolve scope

1. Resolve the worktree path to an absolute path.
2. Confirm the directory exists.
3. Derive `<slug>` from the final folder name.
4. Resolve the repository root for the archive:
   - If the worktree path is `worktrees/<slug>`, use the parent repository that contains `worktrees/`.
   - If the worktree path is itself the repository root, use that directory.
   - If the repository root is ambiguous, ask before writing.
5. Archive output path: `task-archive/<slug>/summary.yaml` relative to the repository root.

**Scope rules:**

- Read only the task worktree's `current-task/` artifacts and general workflow docs when needed.
- Write only `task-archive/<slug>/summary.yaml`.
- Delete only the task worktree's `current-task/` directory after the archive is written.
- Never delete source files, app files, git metadata, worktrees, or root workflow docs.
- Run shell commands only when needed to delete `<worktree>/current-task/` after the archive is written.
- Do not invoke other agents (`task: false`).

### Step 2: Load artifacts

Load compactly from `current-task/` when present:

- `current-task/current-task-context.yaml`
- Spec
- Subtask list
- Execution
- Review
- Review validation
- Review inputs
- Next-step specs
- Commit handoff
- Push handoff
- Merge handoff

Read only what is needed to summarize task definition, process, decisions, open questions, and suggestions. Do not copy full artifacts into the archive.

### Step 3: Draft archive

Write `task-archive/<slug>/summary.yaml` following [archive-format.md](archive-format.md).

Include:

- Compact task definition from context/spec.
- Final outcome from merge, push, and commit artifacts.
- Process summary from context history and artifacts.
- Decision-making from open questions, review triage, review inputs, conflict resolutions, user resolutions, blockers, and deviations.
- `open_questions`, even when empty.
- Suggestions for smoother task development.

Suggestions should use close-task judgment plus open questions and artifacts. Focus on what would make future tasks clearer, smaller, safer, or faster.

### Step 4: Delete current-task

After successfully writing the archive:

1. Delete only `<worktree>/current-task/`.
2. Do not delete `task-archive/`.
3. If deletion fails, report the archive path and the deletion blocker.

Allowed deletion command shape:

```bash
rm -rf -- current-task
```

Run it only with `working_directory` set to the worktree scope root, after verifying the archive exists.

### Step 5: Report

Summarize:

- Archive file path.
- Whether `current-task/` was deleted.
- Top suggestions count.
- Any blockers.

## Safety rules

- Only run after explicit close confirmation from Nicki.
- Never delete `current-task/` before writing the archive.
- Never delete anything outside `<worktree>/current-task/`.
- Never run shell commands except the allowed `rm -rf -- current-task` deletion from the worktree root after archive write.
- Never include full logs, raw diffs, or transcripts in the archive.
- When in doubt, ask.
