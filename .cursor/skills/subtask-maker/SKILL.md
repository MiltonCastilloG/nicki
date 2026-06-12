---
name: subtask-maker
description: "Read a YAML spec and write a markdown subtask checklist. One sentence per line, OpenSpec-style."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: subtask-maker
---

# Subtask Maker

Read a **YAML spec**, explore the worktree lightly, and produce a **markdown subtask checklist** — one sentence per line with `- [ ]` / `- [x]` completion state.

Subtask schema: [subtask-format.md](subtask-format.md) (single source of truth).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Spec | Preferred | Path, `@` reference, or inline YAML per [spec-format.md](../spec-maker/spec-format.md) |
| Task description | Fallback | Free text only when no spec is provided |
| Output path | No | Default `current-task/subtasks/<slug>.md` under scope root |
| Frontmatter `context` | No | Optional traceability path; set only when the agent passes one |

If worktree path is missing, ask before starting.

If no spec is provided, ask for a spec or whether to accept free-text as fallback.

## Procedure

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load and parse spec (stop on open_questions)
- [ ] Explore relevant code and tests lightly
- [ ] Draft ordered subtask checklist from spec requirements
- [ ] Write subtask file
- [ ] Report summary
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists.
3. Set the **scope root** to that absolute path. Derive `<slug>` from the final folder name.
4. Default output: `current-task/subtasks/<slug>.md` relative to the scope root.

**Scope rules (non-negotiable):**

- **Read** anywhere under the scope root (including spec files).
- **Write** only to the subtask output path (create parent directory if missing).
- Never edit `src/`, `app/`, config, tests, or any application files.
- Never modify files outside the scope root.

### Step 2: Load and parse the spec

1. Load the spec from path or inline YAML.
2. Validate against [spec-format.md](../spec-maker/spec-format.md).
3. If `open_questions` is non-empty, **stop and ask** — do not write subtasks.
4. Extract: `requirements`, `scope`, `constraints`, `acceptance`, `assumptions`.

Map each requirement and acceptance item to one or more subtask lines during drafting.

### Step 3: Explore the worktree lightly

Use grep, glob, semantic_search, and read to understand:

- Relevant pages, components, features, and existing tests
- Patterns to follow (i18n, semantic Tailwind tokens, barrel exports)

Read [.cursor/skills/caveman/SKILL.md](../caveman/SKILL.md) for markdown voice. Skim project layout for realistic subtasks.

**Exploration discipline:**

- Stay inside the scope root.
- Respect spec `scope.out`.
- Do **not** draft file paths or create/modify steps — only enough context to write realistic one-line subtasks.

### Step 4: Draft the subtask checklist

Write checklist body in **caveman full** — terse lines, technical terms exact, no filler.

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

1. Create the output directory under the scope root if it does not exist.
2. Write the complete markdown to the output path.
3. Do not write any other files.

### Step 6: Report

Summarize:

- Scope root used
- Spec file used
- Subtask file path and line count
- How spec requirements map to subtasks
- Constraints applied

## Safety rules

- Never edit application code — only subtask markdown files
- Never modify files outside the scope root
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- Do not commit or push unless the user explicitly asks
- When in doubt, ask — do not guess
