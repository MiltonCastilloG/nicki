---
name: subtask-maker
description: "Read a YAML spec and write a markdown subtask checklist. One sentence per line, OpenSpec-style."
---

# Subtask Maker

Read a **YAML spec**, explore the worktree lightly, write a **markdown subtask checklist** — one sentence per `- [ ]` line.

Output schema: [subtask-format.md](subtask-format.md). Spec input: [spec-input.md](spec-input.md).

## Procedure

```
- [ ] Resolve worktree scope
- [ ] Load spec (stop on open_questions)
- [ ] Explore
- [ ] Draft ordered checklist from spec
- [ ] Write subtask file
- [ ] Report summary
```

### 1. Resolve worktree scope

Resolve path to absolute; confirm exists. Scope root = that path; `<slug>` = final folder name. Default output: `current-task/subtasks/<slug>.md`.

**Scope:** read anywhere under scope root; write only the subtask output path (create parent dir if needed). Never edit application code or files outside the scope root.

### 2. Load and parse the spec

Load from path or inline YAML. Validate per [spec-input.md](spec-input.md). Extract `requirements`, `scope`, `constraints`, `acceptance`, `assumptions`. Map each requirement and acceptance item to subtask lines.

If worktree path or spec is missing, ask before starting.

### 3. Explore

Use grep, glob, semantic_search, read — relevant pages, components, tests, project patterns. Stay inside scope root; respect `scope.out`.

Look for:

- Code or tests that **already satisfy** a spec requirement or acceptance item
- **Duplicated or near-duplicated logic** that could be shared instead of rebuilt
- Partial implementations worth **extending or wiring**, not replacing
- Ask user when something is not CLEAR.

Enough context for realistic one-line subtasks — no file paths or create/modify steps in checklist text.

### 4. Draft checklist

Follow [subtask-format.md](subtask-format.md): frontmatter, `# Subtasks`, ordered `- [ ]` lines. Typical size 6–15 lines — verify, refactor, implementation, tests, verification from `acceptance`.

**Avoid unnecessary build work.** For each requirement, pick the smallest compliant action:

1. **Verify first** — when exploration suggests the requirement may already be met, write a subtask to confirm against the spec and **leave behavior unchanged** if it passes.
2. **Refactor to share** — when similar logic already exists, write extraction or reuse subtasks.
3. **Build only gaps** — net-new implementation subtasks only for requirements not already satisfied and not solvable by reuse.

Every spec `requirements` and `acceptance` item still maps to at least one subtask line — but that line may verify, refactor, or implement. Do not drop requirements because existing code might cover them; make execute prove compliance or make the minimal change.

### 5. Write and report

Write only the subtask file. Report scope root, spec path, subtask path, line count, requirement mapping.

## Safety

Never force-push, `reset --hard`, or delete worktrees/branches without explicit approval. Do not commit or push unless asked. When in doubt, ask.
