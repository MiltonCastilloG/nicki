---
name: current-task-update
description: "Update current-task/current-task-context.yaml from a compact Nicki workflow summary. Use when Nicki finishes a workflow step and needs to persist the next step, artifact paths, blockers, or history."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: current-task-update
  tools:
    read: true
    write: true
    delete: false
    shell: false
    grep: false
    glob: false
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

# Current Task Update

Update the canonical task context file from Nicki's compact workflow summary. This agent writes exactly one file: `current-task/current-task-context.yaml` under the worktree scope root.

Schema: [current-task-context-format.md](current-task-context-format.md).

## When to use

- Nicki has completed `start-task`, `describe`, `spec`, `subtasks`, `execute`, `review`, `triage`, `merge`, `commit`, `push`, or a fix-loop step.
- Nicki needs to persist the next workflow step, artifact paths, open questions, or history.
- A worktree already exists and Nicki needs to initialize missing `current-task/current-task-context.yaml`.

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Nicki summary | Yes | Compact YAML summary of the step result and next intended step |

If either input is missing, ask before writing.

## Nicki summary format

```yaml
worktree: worktrees/hero-section
completed_step: spec
completed_status: complete
artifact: current-task/specs/hero-section.yaml
next_step: subtasks
open_questions: []
summary: Spec captured requirements and acceptance criteria.
```

Optional fields:

- `task`: `slug`, `title`, `original`, `story`, `type`
- `git`: `branch`, `base`
- `artifacts`: paths to merge into the existing context
- `constraints`: constraints to set or carry forward

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load existing context if present
- [ ] Parse Nicki summary
- [ ] Validate transition and scope
- [ ] Write current-task/current-task-context.yaml
- [ ] Report updated step and next step
```

### Step 1: Resolve scope

1. Resolve the worktree path to an absolute path.
2. Confirm the directory exists.
3. Derive `<slug>` from the final folder name.
4. Context output path: `current-task/current-task-context.yaml` relative to the scope root.

**Scope rules:**

- Read only `current-task/current-task-context.yaml` and Nicki-provided artifact paths needed to validate the update.
- Write only `current-task/current-task-context.yaml`.
- Never edit specs, subtasks, executions, reviews, validations, source files, config, or files outside the scope root.
- Do not run shell commands.

### Step 2: Load and validate

If `current-task/current-task-context.yaml` exists:

- Validate it follows [current-task-context-format.md](current-task-context-format.md).
- Validate `scope.worktree_path` matches the command worktree path or equivalent absolute path.
- Preserve existing task fields unless Nicki summary explicitly updates them.

If the file is missing:

- Require enough Nicki summary data to initialize `task.slug`, `task.original`, `scope.worktree`, and `scope.worktree_path`.
- Default `artifacts.context` to `current-task/current-task-context.yaml`.
- Default `constraints` to `[no-commit, no-new-deps]` unless Nicki summary provides constraints.

Stop and ask when summary and existing context conflict.

### Step 3: Apply update

Update:

- `meta.schema: current-task-context.v1`
- `meta.generated_by: current-task-update` when creating the file
- `meta.updated_by: current-task-update`
- `task.current_step` to the completed step or current workflow position
- `task.next_step` to Nicki's next intended step
- `task.last_completed_step` when `completed_status: complete`
- `artifacts` with any produced artifact paths
- `open_questions` from the summary
- `history` by appending one compact event for this update

History event:

```yaml
- step: spec
  status: complete
  artifact: current-task/specs/hero-section.yaml
  summary: Spec captured requirements and acceptance criteria.
```

Use `complete`, `blocked`, `failed`, or `skipped` for `history[].status`.

### Step 4: Write and report

1. Create `current-task/` under the scope root if needed.
2. Write the full context YAML to `current-task/current-task-context.yaml`.
3. Report:
   - Context path
   - Completed step and status
   - Next step
   - Open questions, if any

## Safety rules

- Write only `current-task/current-task-context.yaml`.
- Do not infer missing workflow transitions from code or git.
- Do not invoke other agents (`task: false`).
- Ask before writing if the summary conflicts with existing context.
