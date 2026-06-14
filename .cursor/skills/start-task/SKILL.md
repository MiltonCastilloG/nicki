---
name: start-task
description: "Pull main and create git worktrees for parallel task work."
---

# Start Task

Set up git worktrees. Pull `main` first. Path: `projects/<project>/worktrees/<slug>` when `PROJECT` env set; else legacy `worktrees/<slug>`.

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Work items | Yes | One or more tasks — slug-level labels are enough |
| `PROJECT` env | No | Selects `projects/<project>/worktrees/<slug>` |
| Workspace root | For registry | Agent passes when registering tasks |

## Procedure

```
Task Progress:
- [ ] Parse work items from the user message
- [ ] Classify each item and choose branch prefix + slug
- [ ] Confirm ambiguous classifications with the user
- [ ] Run start-worktrees.sh with branch:slug pairs
- [ ] Report results
```

### Step 1: Parse work items

Split the message into distinct work items (comma-separated, line breaks, or explicit prefixes like `fix:` / `chore:`).

A work item may be **minimal** — enough to classify the branch and derive a slug (e.g. `hero-section`, `fix footer`). A full job description is not required at start.f

If the user provides a fuller description, pass it through in the report as original task text.

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

**Worktree path:** `projects/<project>/worktrees/<slug>` (preferred) or `worktrees/<slug>` (legacy). Prefix omitted from folder name.

If classification is ambiguous, ask before creating worktrees.

### Step 3: Run the script

From project repo root (or workspace project checkout), run:

```bash
PROJECT=castlemill-landing .cursor/skills/start-task/scripts/start-worktrees.sh \
  "feature/hero-section:hero-section" \
  "fix/footer-bug:footer-bug"
```

Pass one `branch:slug` argument per work item. The script:

1. Checks out `main` and runs `git pull origin main`
2. Creates `projects/<project>/worktrees/<slug>` when `PROJECT` set, else `worktrees/<slug>`
3. Skips items where the path or branch already exists (no overwrite)


### Step 4: Report

Summarize:

- Whether `main` was updated (before/after SHA if changed)
- Created worktrees (path → branch)
- Skipped items (if any)
- Per created worktree: path, slug, branch, original task text, task type

## Safety rules

- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- If a worktree or branch already exists, report it and skip — do not overwrite
- No single host-repo hardcode; `PROJECT` selects `projects/<project>/worktrees/`
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
