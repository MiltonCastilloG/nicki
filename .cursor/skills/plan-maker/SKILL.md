---
name: plan-maker
description: "Read a YAML spec and explore a worktree to write current-task/plans/<slug>.yaml for /execute-plan. Use when the user runs /plan-maker or asks to plan work in a worktree before implementation."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: plan-maker
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

# Plan Maker

Read a **YAML spec** (from `/spec-maker`), explore the worktree codebase, and produce a **YAML plan** that `/execute-plan` can follow literally. The plan is the handoff artifact — be specific so the executor does not re-explore or improvise.

- Spec schema (input): [spec-format.md](../spec-maker/spec-format.md)
- Plan schema (output): [plan-format.md](../execute-plan/plan-format.md)

## When to use

- User invokes `/plan-maker` with a worktree path and a spec (`@current-task/specs/<slug>.yaml`)
- A spec was written via `/spec-maker` and needs an implementation plan
- User asks to plan (not implement) work inside an isolated worktree

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
- [ ] Explore relevant code and tests
- [ ] Draft ordered YAML plan from spec requirements
- [ ] Write current-task/plans/<slug>.yaml
- [ ] Report summary and next command
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists.
3. Set the **scope root** to that absolute path. Derive `<slug>` from the final folder name (e.g. `worktrees/hero-section` → slug `hero-section`).
4. Plan output path: `current-task/plans/<slug>.yaml` relative to the scope root.
5. Load `current-task/current-task-context.yaml` when present and validate its `scope.worktree_path` matches the worktree path.

**Scope rules (non-negotiable):**

- **Read** anywhere under the scope root (including `current-task/specs/<slug>.yaml`).
- **Write** only to `current-task/plans/<slug>.yaml` (create `current-task/plans/` directory if missing).
- Never edit `src/`, `app/`, config, tests, or any application files.
- Never modify files outside the scope root.

### Step 2: Load and parse the spec

1. Load the spec from `@current-task/specs/<slug>.yaml`, a path, or inline YAML.
2. Validate against [spec-format.md](../spec-maker/spec-format.md).
3. If `open_questions` is non-empty, **stop and ask** the user — do not write a plan until resolved.
4. Extract: `requirements`, `scope`, `constraints`, `acceptance`, `assumptions`.

Map each requirement to one or more plan steps during drafting. Carry `constraints` into the plan.

### Step 3: Explore the worktree

Use grep, glob, semantic_search, and read to find:

- Relevant pages under `app/`
- Components under `src/components/`
- Features under `src/features/`
- Config under `src/config/`
- Existing tests for areas the spec touches
- Patterns to follow (i18n via `useTranslations`, semantic Tailwind tokens, barrel exports)

Read [CONTRIBUTING.md](../../../CONTRIBUTING.md) for project conventions if not already familiar.

**Exploration discipline:**

- Stay inside the scope root.
- Respect spec `scope.out` — do not plan work outside bounds.
- Note exact file paths and symbol names for plan steps.
- Map spec `acceptance` criteria to the final `verify` step commands.

### Step 4: Draft the YAML plan

Follow the schema in [plan-format.md](../execute-plan/plan-format.md). Output **YAML only**.

Include:

- `meta` block with `worktree`, `generated_by: plan-maker`, `task` (from spec `meta.task`), and `spec: current-task/specs/<slug>.yaml`
- Include `meta.context: current-task/current-task-context.yaml` when a task context exists
- `title` — from spec title
- `constraints` — from spec constraints (default `no-commit`, `no-new-deps`)
- `steps` — ordered list covering every spec requirement with exact `action`, conditional required fields, and specific `do` text
- `covers` on steps when spec requirement IDs are available
- Final `verify` step mapping spec `acceptance` to commands (`npm run lint`, scoped `npm test`, etc.)

**Step granularity (typical 5–12 steps):**

- Split large work: create component → wire into page → add/update tests → verify
- Name symbols and patterns to copy (e.g. `LandingBanner`, `useTranslations`, `bg-primary`)
- Use `action: run` with `do: Ask user...` only for forks not resolved in the spec
- Describe expected outcomes, not motivations
- Every file path must be relative to the worktree root and must exist (or be created by an earlier `create` step)
- For `create`, `modify`, and `delete`, include `id`, `action`, `path`, and `do`
- For `verify`, include `id`, `action`, and `commands`; `do` is optional

**Do not:**

- Write implementation code in the plan — only instructions for execute-plan
- Plan work outside spec `scope.out`
- Use vague verbs without file lists
- Reference paths outside the worktree
- Include commit or push steps unless the spec or user explicitly requested them

### Step 5: Write the plan file

1. Create `current-task/plans/` under the scope root if it does not exist.
2. Write the complete YAML to `current-task/plans/<slug>.yaml`.
3. Do not write any other files.

### Step 6: Report

Summarize:

- Scope root used
- Spec file used (`current-task/specs/<slug>.yaml`)
- Plan file path (`current-task/plans/<slug>.yaml`)
- Step count and list of files referenced in steps
- How each spec requirement maps to plan steps
- Constraints applied

Remind the user to run:

```
/execute-plan worktrees/<slug> @current-task/plans/<slug>.yaml
```

Replace `worktrees/<slug>` with the actual worktree path the user provided.

## Safety rules

- Never edit application code — only `current-task/plans/*.yaml`
- Never edit `current-task/current-task-context.yaml`; Nicki updates it through `/current-task-update`
- Never modify files outside the scope root
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- Do not commit or push unless the user explicitly asks
- When in doubt, ask or add an explicit decision step — do not guess

## Examples

**Input:** `/plan-maker worktrees/hero-section @current-task/specs/hero-section.yaml`

**Output file:** `worktrees/hero-section/current-task/plans/hero-section.yaml`

**Next command:**

```
/execute-plan worktrees/hero-section @current-task/plans/hero-section.yaml
```
