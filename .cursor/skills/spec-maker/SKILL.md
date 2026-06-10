---
name: spec-maker
description: "Analyze a task and write a YAML spec to current-task/specs/<slug>.yaml for /subtask-maker. Use when the user runs /spec-maker or asks to define requirements in a worktree before subtask breakdown."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: spec-maker
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

# Spec Maker

Analyze a task and produce a **YAML spec** that `/subtask-maker` uses to draft a build checklist. The spec defines **what** to build — not **how**. No file paths, no create/modify steps.

Spec schema: [spec-format.md](spec-format.md) (single source of truth).

## When to use

- User invokes `/spec-maker` with a worktree path and task description
- A worktree was created via `/start-task` and needs requirements defined before subtask breakdown
- User asks to spec (not subtask or implement) work inside an isolated worktree

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Task description | No* | Free text after the path — fallback when context has no `task.story` |
| Task context | Optional | `current-task/current-task-context.yaml` when orchestrated by Nicki |

\*When orchestrated by Nicki, prefer `task.story` from context. Ask only if neither context story nor command description is available.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load task.story from context (preferred) or parse task description (ask if vague)
- [ ] Light context read (CONTRIBUTING, project layout)
- [ ] Draft YAML spec
- [ ] Write current-task/specs/<slug>.yaml
- [ ] Report summary and next command
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists.
3. Set the **scope root** to that absolute path. Derive `<slug>` from the final folder name (e.g. `worktrees/hero-section` → slug `hero-section`).
4. Spec output path: `current-task/specs/<slug>.yaml` relative to the scope root.
5. Infer `branch` from git when possible (e.g. `feature/hero-section`); omit if unknown.
6. Load `current-task/current-task-context.yaml` when present and validate its `scope.worktree_path` matches the worktree path.
7. When context includes `task.story`, use it as the primary requirements source. Otherwise use the command-line task description or `task.original`.

**Scope rules (non-negotiable):**

- **Read** anywhere under the scope root and CONTRIBUTING.md.
- **Write** only to `current-task/specs/<slug>.yaml` (create `current-task/specs/` directory if missing).
- Never edit `src/`, `app/`, config, tests, `current-task/subtasks/`, or any application files.
- Never modify files outside the scope root.

### Step 2: Parse task description

When `task.story` is present in context, derive requirements and acceptance from the Gherkin user story (`Feature:`, scenarios, and **As a / I want / So that**). Set `meta.task` to the full `task.story` text.

Otherwise extract what the user wants built or fixed from the command description or `task.original`. Ask if:

- The outcome is vague ("improve", "modernize", "clean up") with no measurable target
- Scope is unclear (which page, which component, which behavior)
- Multiple valid interpretations exist and the user has not chosen one
- A design fork affects requirements (CTA link, copy, visual approach)

Do not write the spec until requirements are clear enough to list testable `requirements` and `acceptance` criteria.

### Step 3: Light context read

Use read, grep, glob, or semantic_search **lightly** to bound scope realistically:

- Read [CONTRIBUTING.md](../../../CONTRIBUTING.md) for project conventions
- Skim top-level layout (`app/`, `src/components/`, `src/features/`) to know what areas exist
- Do **not** explore file-by-file or draft implementation subtasks — that is subtask-maker's job

### Step 4: Draft the YAML spec

Follow the schema in [spec-format.md](spec-format.md). Output **YAML only**.

Include:

- `meta` — `worktree`, `generated_by: spec-maker`, `task`, optional `branch`
- Include `meta.context: current-task/current-task-context.yaml` when a task context exists
- `title` — short task name
- `type` — `feature`, `fix`, `chore`, `docs`, `refactor`, `test`, or `perf`
- `summary` — one-paragraph goal
- `requirements` — ordered, testable items with `id` and `description`
- `scope` — `in` / `out` lists bounding the work
- `constraints` — default to `no-commit` and `no-new-deps` unless the task requires otherwise
- `acceptance` — verifiable done criteria
- `assumptions` — defaults applied when the task was silent
- `open_questions` — empty list, or unresolved items (subtask-maker will ask)

**Do not:**

- Name file paths or symbols
- Include create/modify/delete/run/verify steps
- Write implementation subtasks
- Guess on design forks — ask first or list in `open_questions`

### Step 5: Write the spec file

1. Create `current-task/specs/` under the scope root if it does not exist.
2. Write the complete YAML to `current-task/specs/<slug>.yaml`.
3. Do not write any other files.

### Step 6: Report

Summarize:

- Scope root used
- Spec file path (`current-task/specs/<slug>.yaml`)
- Task type and requirement count
- Scope in/out summary
- Constraints applied
- Any `open_questions` remaining

Remind the user to run:

```
/subtask-maker worktrees/<slug> @current-task/specs/<slug>.yaml
```

Replace `worktrees/<slug>` with the actual worktree path the user provided.

## Safety rules

- Never edit application code — only `current-task/specs/*.yaml`
- Never write subtask files — only specs
- Never edit `current-task/current-task-context.yaml`; Nicki updates it through `/current-task-update`
- Never modify files outside the scope root
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- Do not commit or push unless the user explicitly asks
- When in doubt, ask — do not guess

## Examples

**Input:** `/spec-maker worktrees/hero-section redesign hero with headline, subcopy, and CTA using semantic Tailwind tokens`

**Output file:** `worktrees/hero-section/current-task/specs/hero-section.yaml`

**Next command:**

```
/subtask-maker worktrees/hero-section @current-task/specs/hero-section.yaml
```
