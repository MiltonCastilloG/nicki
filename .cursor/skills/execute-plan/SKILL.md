---
name: execute-plan
description: "Execute a markdown subtask checklist inside a git worktree with strict path scope."
---

# Execute Plan

Implement work inside one worktree — OpenSpec-style when a checklist exists. Prefer unchecked `- [ ]` lines in order; flip each to `- [x]` before moving on. Treat the prompt’s plan (checklist path, inline markdown, or free text) as authoritative.

The worktree path is a hard boundary: never modify files outside it.

Subtask input: [subtask-input.md](../subtask-maker/subtask-input.md).

**Do not write** `current-task/executions/<slug>.json`. Evidence for review is the git diff plus whatever exists under `current-task/`.

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Plan | Yes* | Whatever the prompt supplies — checklist path/`@`/inline, or free text |

\*Ask when the prompt does not yield a usable plan.

## Procedure

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Parse plan from the prompt
- [ ] Flag ambiguous or out-of-scope items (ask user)
- [ ] Execute work in order, marking checklist items when a list exists
- [ ] Report summary (omit execution artifact)
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists and is a git worktree (or at minimum a directory the user designated).
3. Set the **scope root** to that absolute path. All subsequent work happens here.
4. Derive `<slug>` from the final folder name.

**Scope rules (non-negotiable):**

- **Create, edit, delete** files only under the scope root.
- Run shell commands with `working_directory` set to the scope root unless a subtask implies a subdirectory (still must stay under scope root).
- Do **not** read sibling worktrees or the parent repo for the purpose of copying changes into other trees.
- Do **not** modify `.cursor/`, parent-repo config, or paths outside the scope root — even if convenient.
- If work would require changes outside the scope root, **stop and ask** — do not proceed.

### Step 2: Parse the plan

When a subtask list is present, load from path or inline markdown. Parse per [subtask-input.md](../subtask-maker/subtask-input.md).

Extract:

- YAML **frontmatter** (`worktree`, `spec`, `constraints`, etc.)
- Ordered checklist lines (`- [ ]` pending, `- [x]` complete)

When only free text is present, derive an ordered work list from that text. Do not invent pipeline position.

**Before executing**, check for:

- Missing or vague items ("improve the footer", "clean up code")
- Items outside linked spec `scope.out` when a spec is available in the prompt or worktree
- `meta.worktree` / frontmatter `worktree` that does not match the worktree slug
- No verification items when linked spec `acceptance` exists

If anything is unclear, **stop and ask** with a specific question. Do not guess or fill gaps with your own design choices.

### Step 3: Execute

Work through **unchecked** checklist lines top to bottom when a list exists; otherwise follow the chat plan:

1. Read the next item.
2. Implement what it requires — explore the worktree as needed to decide files and approach.
3. When a checklist item is done, change that line to `- [x]` and **save** the subtask markdown immediately.
4. Continue until the plan is done or execution blocks.

**Execution discipline:**

- One item at a time; mark complete before moving on when using a checklist.
- Match existing project conventions (read surrounding code in the worktree first).
- Minimize scope — only change what the current item requires.
- Do **not** add work beyond the plan unless the user approves.
- Do **not** commit or push unless an item explicitly requires it **and** the user has asked for commits in their rules/message.
- Verification items (`Run npm run lint`, `Run npm test`, etc.) — run the commands and fix failures before marking complete.

If an item fails (tool error, test failure, missing context), stop and report. Do not silently skip or rewrite the checklist unless the user approves.

**Resume:** If some lines are already `- [x]`, skip them and continue from the first unchecked line.

### Step 4: Report

Summarize:

- Scope root used
- Work completed (with paths touched)
- Items skipped or blocked (with reason)
- Verification results
- Remaining unchecked subtasks, if any
- Any questions left for the user

Do **not** write an execution handoff JSON. Omit `artifact` from the sheep return.

## Safety rules

- Never modify files outside the scope root
- May edit the subtask markdown file only to flip checklist completion state
- Never write `current-task/executions/*.json`
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- Do not commit or push unless the user explicitly asks
- When in doubt, ask — improvisation is a last resort, not a default
