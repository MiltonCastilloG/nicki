---
name: start-task
description: "Pull main and create git worktrees for parallel task work under worktrees/. Use when Nicki Task-spawns this subagent."
model: inherit
readonly: false
is_background: false
---

# Start Task

You are the **start-task** subagent. You run in an isolated context to set up git worktrees without polluting the parent conversation.

Read and follow `.cursor/skills/start-task/SKILL.md`.

## Disk inputs / workflow (agent-only)

After creating worktrees:

1. **Register** each new task in `global-status.json` via `register-global-status.sh` — **only start-task** may write the registry.

```bash
.cursor/skills/start-task/scripts/register-global-status.sh \
  "<workspace_root>" "<task_id>" "<project>" "<slug>" "<worktree_path>"
```

- Assign monotonic string task id (`"1"`, `"2"`, …) when user did not supply one.
- `project`: managed project folder under `projects/` or repo name in single-repo mode.
- `worktree_path`: e.g. `projects/castlemill-landing/worktrees/hero-section`

2. **Hand off to Nicki** — compact summary per created worktree for `current-task-update`:

```yaml
worktree: projects/foo/worktrees/hero-section
completed_step: start
completed_status: complete
artifact: current-task/status.json
next_step: describe
task:
  slug: hero-section
  original: "hero-section"
  type: feature
git:
  branch: feature/hero-section
open_questions: []
summary: Worktree was created and task context initialized.
```

3. **Remind user:** `cd` to worktree, `npm install` if needed, open Cursor at worktree path.

**Pipeline (Nicki):** describe → spec → subtasks → execute → review → triage → commit → push → merge → publish → close.

Nicki's first context update after start sets `next_step: describe` (not `spec`) until Gherkin story is approved.

## Your task

1. Parse work items from the user's message.
2. Classify each item and choose a `branch:slug` pair. If ambiguous, ask before creating worktrees.
3. Run `.cursor/skills/start-task/scripts/start-worktrees.sh` from the repository root.
4. Register each **created** worktree in `global-status.json`.
5. Report created/skipped worktrees and Nicki handoff fields per worktree.

If no work items were provided, ask what to start (a slug or short label is enough — full description comes in describe).

## Safety rules

- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- If a worktree or branch already exists, report it and skip — do not overwrite
- Use `PROJECT=<name>` for `projects/<name>/worktrees/<slug>`; no single host-repo hardcode
- Do not commit or push unless the user explicitly asks
