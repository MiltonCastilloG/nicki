---
name: integrate-task
description: "Merge feature into target branch and push target branch; write integrate handoff YAML in task worktree."
---

# Integrate Task

Merge a synced feature branch into a target branch (default `main`), then push the target branch to remote. Merge conflicts follow [conflict-resolution](../conflict-resolution/SKILL.md).

Schema: [integrate-format.md](integrate-format.md).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Task worktree path | Yes | Handoff write location |
| Sync handoff | Yes | Confirms feature branch pushed |
| Target branch worktree | Yes | Checkout where merge runs — agent resolves |
| Target branch | No | Defaults to `main` |
| Handoff output path | No | Default `<task_worktree>/current-task/integrates/<slug>.yaml` |

If task worktree path is missing, ask before starting.

If no sync handoff or sync `status` is not `synced`, stop and ask.

## Procedure

```
Task Progress:
- [ ] Resolve task worktree scope
- [ ] Load sync handoff
- [ ] Identify feature and target branches
- [ ] Inspect target branch state
- [ ] Merge feature into target branch
- [ ] Resolve conflicts with user input if needed
- [ ] Push target branch
- [ ] Write integrate handoff in task worktree
- [ ] Report summary
```

### Step 1: Resolve scope

1. Resolve task worktree to absolute path; derive `<slug>`.
2. Load sync handoff; feature branch from `remote.branch` or `commit.branch`.
3. Establish target branch worktree for git commands.
4. Handoff path: `current-task/integrates/<slug>.yaml` under **task worktree**.

**Scope rules:**

- Read task worktree; run merge and push in target branch worktree.
- Write only:
  - files changed by git merge under target branch worktree
  - conflicted files under target branch worktree (user-approved resolutions)
  - integrate handoff YAML under task worktree
- Never modify files outside task worktree or target branch worktree.

### Step 2: Inspect target git state

On the target branch worktree:

- `git status --porcelain`
- `git branch --show-current`
- `git rev-parse --show-toplevel`
- `git remote -v`

Stop and ask when:

- Current branch is not the target branch.
- Target working tree has uncommitted changes before merge, unless user explicitly allows.
- Merge already in progress and user has not asked to continue.
- Sync handoff missing or feature branch unknown.

### Step 3: Merge feature into target

```bash
git merge --no-ff <feature-branch>
```

Do not use rebase or strategy flags unless the user explicitly asks.

If "Already up to date", record `merge.status: no_op` and proceed to publish phase.

If conflicts occur, follow [conflict-resolution](../conflict-resolution/SKILL.md). Record every resolution.

Verify no conflict markers remain before completing merge.

### Step 4: Push target branch

Nicki may have pre-confirmed; still verify before pushing.

```bash
git push origin <target_branch>
```

Do not force push. Do not push the feature branch here.

If push fails, write handoff with `status: partial` (merge done, publish blocked).

### Step 5: Write handoff

Write per [integrate-format.md](integrate-format.md) under task worktree.

### Step 6: Report

Summarize merge result, target push result, handoff path.

## Safety rules

- Integrate only when explicitly invoked or the user explicitly asks.
- Never resolve conflicts without explicit user input.
- Never force push.
- Never push the feature branch from this skill.
- Never use destructive git commands without explicit user approval.
- When in doubt, ask.
