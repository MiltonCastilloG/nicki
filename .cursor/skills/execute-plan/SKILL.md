---
name: execute-plan
description: "Execute a markdown subtask checklist inside a git worktree with strict path scope."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: execute-plan
---

# Execute Plan

Implement work by following a **subtask checklist** inside one worktree — OpenSpec-style. Read unchecked `- [ ]` lines in order, implement each one-sentence subtask, then flip it to `- [x]` in the same file before moving on.

The worktree path is a hard boundary: never modify files outside it.

Subtask schema: [subtask-format.md](../subtask-maker/subtask-format.md).
Execution schema: [execution-format.md](execution-format.md).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Subtask list | Yes | Path, `@` reference, or inline markdown |
| Linked spec | No | Path when agent passes one — used for scope checks |
| Execution output path | No | Default `current-task/executions/<slug>.yaml` under scope root |

If either worktree or subtask list is missing, ask before starting.

## Procedure

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Parse subtask list and find unchecked items
- [ ] Flag ambiguous or out-of-scope subtasks (ask user)
- [ ] Execute unchecked subtasks in order, marking each complete
- [ ] Write execution handoff
- [ ] Report summary
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists and is a git worktree (or at minimum a directory the user designated).
3. Set the **scope root** to that absolute path. All subsequent work happens here.
4. Derive `<slug>` from the final folder name. Default execution output: `current-task/executions/<slug>.yaml`.

**Scope rules (non-negotiable):**

- **Create, edit, delete** files only under the scope root.
- Run shell commands with `working_directory` set to the scope root unless a subtask implies a subdirectory (still must stay under scope root).
- Do **not** read sibling worktrees or the parent repo for the purpose of copying changes into other trees.
- Do **not** modify `.cursor/`, parent-repo config, or paths outside the scope root — even if convenient.
- If a subtask would require changes outside the scope root, **stop and ask** — do not proceed.

### Step 2: Parse the subtask list

Load from path or inline markdown. Full schema: [subtask-format.md](../subtask-maker/subtask-format.md).

Extract:

- YAML **frontmatter** (`worktree`, `spec`, `constraints`, etc.)
- Ordered checklist lines (`- [ ]` pending, `- [x]` complete)

**Before executing**, check for:

- Missing or vague subtasks ("improve the footer", "clean up code")
- Subtasks outside linked spec `scope.out` when a spec path is available
- `meta.worktree` / frontmatter `worktree` that does not match the worktree slug
- No verification subtasks at the end when linked spec `acceptance` exists

If anything is unclear, **stop and ask** with a specific question. Do not guess or fill gaps with your own design choices.

### Step 3: Execute subtasks

Work through **unchecked** subtasks top to bottom:

1. Read the next `- [ ]` line.
2. Implement what that one sentence requires — explore the worktree as needed to decide files and approach.
3. When the subtask is done, change that line to `- [x]` and **save** the subtask markdown file immediately.
4. Continue until all subtasks are checked or execution blocks.

**Execution discipline:**

- One subtask at a time; mark complete before moving on.
- Match existing project conventions (read surrounding code in the worktree first).
- Minimize scope — only change what the current subtask requires.
- Do **not** add work beyond unchecked subtasks unless the user approves.
- Do **not** commit or push unless a subtask explicitly requires it **and** the user has asked for commits in their rules/message.
- Verification subtasks (`Run npm run lint`, `Run npm test`, etc.) — run the commands and fix failures before marking complete.

If a subtask fails (tool error, test failure, missing context), stop and report. Do not silently skip or rewrite the checklist unless the user approves.

**Resume:** If some lines are already `- [x]`, skip them and continue from the first unchecked line.

### Step 4: Write execution handoff

Write the execution YAML under the scope root using [execution-format.md](execution-format.md).

Write whenever execution reaches a terminal state:

- `status: complete` when all subtasks are checked and verification subtasks passed or were explicitly skipped by user direction.
- `status: partial` when some subtasks completed but the list did not finish.
- `status: blocked` when execution cannot continue without user input, a scope decision, or a failed required command.

### Step 5: Report

Summarize:

- Scope root used
- Subtasks completed (with paths touched)
- Subtasks skipped or blocked (with reason)
- Verification results
- Execution handoff path written
- Remaining unchecked subtasks, if any
- Any questions left for the user

## Safety rules

- Never modify files outside the scope root
- May edit the subtask markdown file only to flip checklist completion state
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- Do not commit or push unless the user explicitly asks
- When in doubt, ask — improvisation is a last resort, not a default
