---
name: subtask-maker
description: "Read a YAML spec and write a markdown subtask checklist to current-task/subtasks/<slug>.md for /execute-plan. Use when the user runs /subtask-maker or asks to break a spec into buildable subtasks before implementation."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: subtask-maker
  tools:
    read: true
    write: true
    delete: false
    shell: false
    grep: true
    glob: true
    semantic_search: true
    task: false
    web_search: false
    web_fetch: false
    mcp: false
    ask_question: true
    todo_write: true
    generate_image: false
    switch_mode: false
---

# Subtask Maker

Read a **YAML spec** (from `/spec-maker`), explore the worktree lightly, and produce a **markdown subtask checklist** that `/execute-plan` works through in order — OpenSpec-style, one sentence per line with `- [ ]` / `- [x]` completion state.

Subtask schema: [subtask-format.md](subtask-format.md) (single source of truth).

## When to use

- User invokes `/subtask-maker` with a worktree path and a spec (`@current-task/specs/<slug>.yaml`)
- A spec was written via `/spec-maker` and needs a build checklist before implementation
- User asks to break spec work into subtasks (not implement) inside an isolated worktree

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Spec | Preferred | `@current-task/specs/<slug>.yaml` or inline YAML per [spec-format.md](../spec-maker/spec-format.md) |
| Task context | Optional | `current-task/current-task-context.yaml` when orchestrated by Nicki |
| Task description | Fallback | Free text only when no spec is provided |

If worktree path is missing, ask before starting.

If no spec is provided, ask whether to run `/spec-maker` first or accept a free-text task description as a fallback.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load and parse spec (ask on open_questions)
- [ ] Explore relevant code and tests lightly
- [ ] Draft ordered subtask checklist from spec requirements
- [ ] Write current-task/subtasks/<slug>.md
- [ ] Report summary and next command
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists.
3. Set the **scope root** to that absolute path. Derive `<slug>` from the final folder name.
4. Subtask output path: `current-task/subtasks/<slug>.md` relative to the scope root.
5. Load `current-task/current-task-context.yaml` when present and validate its `scope.worktree_path` matches the worktree path.

**Scope rules (non-negotiable):**

- **Read** anywhere under the scope root (including `current-task/specs/<slug>.yaml`).
- **Write** only to `current-task/subtasks/<slug>.md` (create `current-task/subtasks/` if missing).
- Never edit `src/`, `app/`, config, tests, or any application files.
- Never modify files outside the scope root.

### Step 2: Load and parse the spec

1. Load the spec from `@current-task/specs/<slug>.yaml`, a path, or inline YAML.
2. Validate against [spec-format.md](../spec-maker/spec-format.md).
3. If `open_questions` is non-empty, **stop and ask** the user — do not write subtasks until resolved.
4. Extract: `requirements`, `scope`, `constraints`, `acceptance`, `assumptions`.

Map each requirement and acceptance item to one or more subtask lines during drafting.

### Step 3: Explore the worktree lightly

Use grep, glob, semantic_search, and read to understand:

- Relevant pages, components, features, and existing tests
- Patterns to follow (i18n, semantic Tailwind tokens, barrel exports)

Read [CONTRIBUTING.md](../../../CONTRIBUTING.md) for project conventions if not already familiar.

**Exploration discipline:**

- Stay inside the scope root.
- Respect spec `scope.out`.
- Do **not** draft file paths or create/modify steps — only enough context to write realistic one-line subtasks.

### Step 4: Draft the subtask checklist

Follow [subtask-format.md](subtask-format.md).

Include:

- YAML frontmatter with `worktree`, `generated_by: subtask-maker`, `spec`, optional `context`, `title`, and `constraints`
- `# Subtasks` heading
- Ordered `- [ ]` lines — **one sentence each**
- **Test subtasks** for every requirement that implies test coverage
- **Verification subtasks** at the end from spec `acceptance` (lint, scoped test runs)

Typical checklist size: 6–15 lines covering implementation, tests, and verification.

**Do not:**

- Use file paths or symbol names in subtask text
- Combine multiple outcomes on one line
- Include work outside spec `scope.out`
- Skip test subtasks when acceptance or requirements imply them

### Step 5: Write the subtask file

1. Create `current-task/subtasks/` under the scope root if it does not exist.
2. Write the complete markdown to `current-task/subtasks/<slug>.md`.
3. Do not write any other files.

### Step 6: Report

Summarize:

- Scope root used
- Spec file used
- Subtask file path and line count
- How spec requirements map to subtasks
- Constraints applied

Remind the user to run:

```
/execute-plan worktrees/<slug> @current-task/subtasks/<slug>.md
```

## Safety rules

- Never edit application code — only `current-task/subtasks/*.md`
- Never edit `current-task/current-task-context.yaml`; Nicki updates it through `/current-task-update`
- Never modify files outside the scope root
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- Do not commit or push unless the user explicitly asks
- When in doubt, ask — do not guess

## Examples

**Input:** `/subtask-maker worktrees/hero-section @current-task/specs/hero-section.yaml`

**Output file:** `worktrees/hero-section/current-task/subtasks/hero-section.md`

**Next command:**

```
/execute-plan worktrees/hero-section @current-task/subtasks/hero-section.md
```
