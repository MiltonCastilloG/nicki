---
name: start-task
description: "Pull main and create git worktrees for parallel task work under worktrees/. Use when the user runs /start-task or asks to start task branches with worktrees."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: start-task
  tools:
    read: true
    write: false
    delete: false
    shell: true
    grep: false
    glob: false
    semantic_search: false
    task: false
    web_search: false
    web_fetch: false
    mcp: false
    ask_question: true
    todo_write: false
    generate_image: false
    switch_mode: false
---

# Start Task

Set up isolated git worktrees for one or more work items. Always pull `main` first, then create worktrees under `worktrees/<slug>`.

## When to use

- User invokes `/start-task` with one or more work items
- User asks to start parallel task work with worktrees

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Parse work items from the user message
- [ ] Classify each item and choose branch prefix + slug
- [ ] Confirm ambiguous classifications with the user
- [ ] Run start-worktrees.sh with branch:slug pairs
- [ ] Report results and next steps
```

### Step 1: Parse work items

Split the user's message into distinct work items (comma-separated, line breaks, or explicit prefixes like `fix:` / `chore:`).

### Step 2: Classify and name branches

Pick a prefix and kebab-case slug for each item:

| Type | Prefix | When to use | Example |
|------|--------|-------------|---------|
| Feature | `feature/` | New user-facing behavior or UI | `feature/hero-section` |
| Fix | `fix/` | Bug fix | `fix/footer-link-404` |
| Chore | `chore/` | Tooling, deps, config, housekeeping | `chore/update-eslint` |
| Docs | `docs/` | Documentation-only | `docs/contributing-worktrees` |
| Refactor | `refactor/` | Behavior-preserving restructure | `refactor/extract-footer` |
| Test | `test/` | Test-only additions/fixes | `test/hero-coverage` |
| Perf | `perf/` | Performance improvement | `perf/lazy-load-images` |

**Slug rules:** lowercase, hyphens, no spaces. Derive from the description (e.g. "footer bug" → slug `footer-bug`, branch `fix/footer-bug`).

**Worktree path:** `worktrees/<slug>` (prefix omitted from folder name).

If classification is ambiguous, ask before creating worktrees.

### Step 3: Run the script

From the repository root, run:

```bash
.cursor/skills/start-task/scripts/start-worktrees.sh \
  "feature/hero-section:hero-section" \
  "fix/footer-bug:footer-bug"
```

Pass one `branch:slug` argument per work item. The script:

1. Checks out `main` and runs `git pull origin main`
2. Creates `worktrees/<slug>` for each item
3. Skips items where the path or branch already exists (no overwrite)

Make the script executable first if needed: `chmod +x .cursor/skills/start-task/scripts/start-worktrees.sh`

### Step 4: Report and next steps

Summarize:

- Whether `main` was updated (before/after SHA if changed)
- Created worktrees (path → branch)
- Skipped items (if any)
- For each created worktree, report a compact handoff summary for Nicki:
  - `worktree`
  - `slug`
  - `branch`
  - original task text
  - task type
  - next expected artifact: `current-task/current-task-context.yaml`

Remind the user:

1. `cd worktrees/<slug> && npm install` in each **new** worktree (worktrees do not share `node_modules`)
2. Open a new Cursor window rooted at the worktree path for isolated agent sessions
3. When orchestrated by Nicki, it will call `/current-task-update` next to initialize `current-task/current-task-context.yaml`
4. Run `/spec-maker worktrees/<slug> <task description>` to write `current-task/specs/<slug>.yaml`
5. Run `/plan-maker worktrees/<slug> @current-task/specs/<slug>.yaml` then `/execute-plan worktrees/<slug> @current-task/plans/<slug>.yaml` to write `current-task/executions/<slug>.yaml`
6. Run `/review-execution worktrees/<slug>` to review the diff with spec, plan, execution handoff, and write `current-task/reviews/<slug>.yaml`
7. Run `/review-triage worktrees/<slug>` to filter review findings against task scope and write `current-task/review-validations/rN-validation.yaml`
8. Run `/commit-task worktrees/<slug>` to create a local commit and write `current-task/commits/<slug>.yaml`
9. Run `/push-task worktrees/<slug> @current-task/commits/<slug>.yaml` to merge `main`, publish the branch, and write `current-task/pushes/<slug>.yaml`
10. Run `/merge-task worktrees/<slug> target: main` to merge the pushed task branch into `main`, with user input for every conflict resolution
11. Run `/close-task worktrees/<slug>` after Nicki asks `Time for the feedback woof! Want?` to write `task-archive/<slug>/summary.yaml` and delete `current-task/`
12. Verify the archive exists and the task context folder was removed

## Safety rules

- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- If a worktree or branch already exists, report it and skip — do not overwrite
- Only operate on this repository (`castlemill-landing`)
- Do not commit or push unless the user explicitly asks

## Examples

**Input:** `redesign hero section, fix broken mobile nav, chore: bump vitest`

**Classification:**

| Item | Branch | Slug |
|------|--------|------|
| redesign hero section | `feature/hero-section` | `hero-section` |
| fix broken mobile nav | `fix/mobile-nav` | `mobile-nav` |
| bump vitest | `chore/bump-vitest` | `bump-vitest` |

**Command:**

```bash
.cursor/skills/start-task/scripts/start-worktrees.sh \
  "feature/hero-section:hero-section" \
  "fix/mobile-nav:mobile-nav" \
  "chore/bump-vitest:bump-vitest"
```
