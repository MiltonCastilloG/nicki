---
name: merge-task
description: "Merge a task branch into a target branch with user-resolved conflicts; write merge handoff YAML."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: merge-task
---

# Merge Task

Merge a task branch into a target branch (default `main`). If conflicts occur, follow [conflict-resolution](../conflict-resolution/SKILL.md). Do not push.

Merge schema: [merge-format.md](merge-format.md).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Task worktree path | Yes | Where the handoff YAML is written |
| Task branch | Yes | Branch to merge (from push handoff or git) |
| Target branch worktree | Yes | Checkout where merge runs — agent resolves |
| Target branch | No | Defaults to `main` |
| Push handoff | Preferred | Confirms pushed branch |
| Handoff output path | No | Default `<task_worktree>/current-task/merges/<slug>.yaml` |

If task worktree path is missing, ask before starting.

## Procedure

```
Task Progress:
- [ ] Resolve task worktree scope
- [ ] Identify task branch and target branch
- [ ] Inspect target branch state
- [ ] Start merge into target branch
- [ ] Detect conflicts
- [ ] Ask user for every conflict resolution
- [ ] Apply user-approved resolutions
- [ ] Verify no conflict markers remain
- [ ] Write merge handoff YAML in task worktree
- [ ] Report summary
```

### Step 1: Resolve scope

1. Resolve task worktree to absolute path; derive `<slug>`.
2. Establish target branch worktree for git commands.
3. Handoff path: `current-task/merges/<slug>.yaml` under **task worktree** — not target checkout.

**Scope rules:**

- Read task worktree; run merge in target branch worktree.
- Write only:
  - files changed by git merge under target branch worktree
  - conflicted files under target branch worktree (user-approved resolutions)
  - merge handoff YAML under task worktree
- Never modify files outside task worktree or target branch worktree.

### Step 2: Inspect git state

On the target branch worktree:

- `git status --porcelain`
- `git branch --show-current`
- `git rev-parse --show-toplevel`

Stop and ask when:

- Current branch is not the target branch.
- Target working tree has uncommitted changes before merge, unless user explicitly allows.
- Merge already in progress and user has not asked to continue.

### Step 3: Start merge

```bash
git merge --no-ff <task-branch>
```

Do not use rebase or strategy flags unless the user explicitly asks.

If "Already up to date", write `no_op` handoff and report.

If merge applies without conflicts, write handoff and report.

### Step 4–6: Conflicts

Follow [conflict-resolution](../conflict-resolution/SKILL.md). Record every resolution in `user_resolutions`.

Verify no conflict markers remain; complete merge per normal git flow. **Do not push.**

### Step 7: Write handoff

Write merge handoff YAML per [merge-format.md](merge-format.md) under task worktree.

### Step 8: Report

Summarize task/target branch, conflict resolution, handoff path.

## Safety rules

- Merge only when explicitly invoked or the user explicitly asks to merge.
- Never resolve conflicts without explicit user input.
- Never use destructive git commands without explicit user approval.
- Never push or force-push.
- When in doubt, ask.
