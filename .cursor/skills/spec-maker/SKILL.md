---
name: spec-maker
description: "Analyze a task and write a YAML spec. Defines what to build — not how."
---

# Spec Maker

Analyze a task and produce a **YAML spec**. The spec defines **what** to build — not **how**. No file paths, no create/modify steps.

Spec schema: [spec-format.md](spec-format.md) (single source of truth).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Task description | Yes* | Gherkin story, free text, or `task.original` — passed in the prompt |
| Output path | No | Default `current-task/specs/<slug>.yaml` under scope root; agent may override |
| `meta.context` | No | Optional traceability path; set only when the agent passes one |

\*Ask when the description is missing or too vague to list testable requirements.

## Procedure

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Parse task description (ask if vague)
- [ ] Light context read (CONTRIBUTING if exists, project layout)
- [ ] Draft YAML spec
- [ ] Write spec file
- [ ] Report summary
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists.
3. Set the **scope root** to that absolute path. Derive `<slug>` from the final folder name (e.g. `worktrees/hero-section` → slug `hero-section`).
4. Default output: `current-task/specs/<slug>.yaml` relative to the scope root.
5. Infer `branch` from git when possible (e.g. `feature/hero-section`); omit if unknown.

**Scope rules (non-negotiable):**

- **Read** anywhere under the scope root and CONTRIBUTING.md.
- **Write** only to the spec output path (create parent directory if missing).
- Never edit `src/`, `app/`, config, tests, subtask files, or any application files.
- Never modify files outside the scope root.

### Step 2: Parse task description

When the input is Gherkin (`Feature:`, scenarios, **As a / I want / So that**), derive requirements and acceptance from it. Set `meta.task` to the full story text.

Otherwise extract what the user wants built or fixed. Ask if:

- The outcome is vague ("improve", "modernize", "clean up") with no measurable target
- Scope is unclear (which page, which component, which behavior)
- Multiple valid interpretations exist and the user has not chosen one
- A design fork affects requirements (CTA link, copy, visual approach)

Do not write the spec until requirements are clear enough to list testable `requirements` and `acceptance` criteria.

### Step 3: Light context read

Use read, grep, glob, or semantic_search **lightly** to bound scope realistically:

- Read [CONTRIBUTING.md](../../../CONTRIBUTING.md) when present — missing file OK; record assumptions inline in spec
- Skim top-level layout (`app/`, `src/components/`, `src/features/`) to know what areas exist
- Do **not** explore file-by-file or draft implementation subtasks

### Step 4: Draft the YAML spec

Follow the schema in [spec-format.md](spec-format.md). Output **YAML only**.

Include:

- `meta` — `worktree`, `generated_by: spec-maker`, `task`, optional `branch`, optional `context` when agent supplied
- `title` — short task name
- `type` — `feature`, `fix`, `chore`, `docs`, `refactor`, `test`, or `perf`
- `summary` — one-paragraph goal
- `requirements` — ordered, testable items with `id` and `description`
- `scope` — `in` / `out` lists bounding the work
- `constraints` — default to `no-commit` and `no-new-deps` unless the task requires otherwise
- `acceptance` — verifiable done criteria
- `assumptions` — defaults applied when the task was silent
- `open_questions` — empty list, or unresolved items

**Do not:**

- Name file paths or symbols
- Include create/modify/delete/run/verify steps
- Write implementation subtasks
- Guess on design forks — ask first or list in `open_questions`

### Step 5: Write the spec file

1. Create the output directory under the scope root if it does not exist.
2. Write the complete YAML to the output path.
3. Do not write any other files.

### Step 6: Report

Summarize:

- Scope root used
- Spec file path
- Task type and requirement count
- Scope in/out summary
- Constraints applied
- Any `open_questions` remaining

## Safety rules

- Never edit application code — only the spec YAML file
- Never write subtask files
- Never modify files outside the scope root
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- Do not commit or push unless the user explicitly asks
- When in doubt, ask — do not guess
