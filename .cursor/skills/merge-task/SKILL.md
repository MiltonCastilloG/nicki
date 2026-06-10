---
name: merge-task
description: "Merge a pushed current-task branch into main, ask the user for every conflict resolution, and write current-task/merges/<slug>.yaml. Use when the user runs /merge-task or asks to integrate a pushed task branch."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: merge-task
  tools:
    read: true
    write: true
    delete: false
    shell: true
    grep: true
    glob: true
    semantic_search: false
    task: false
    web_search: false
    web_fetch: false
    mcp: false
    ask_question: true
    todo_write: true
    generate_image: false
    switch_mode: false
---

# Merge Task

Merge a pushed task branch into `main` (or an explicit target branch). This is the first workflow step that touches `main`. If conflicts occur, follow the shared [conflict-resolution](../conflict-resolution/SKILL.md) protocol. Write `current-task/merges/<slug>.yaml`.

Merge schema: [merge-format.md](merge-format.md).
Conflict protocol: [conflict-resolution](../conflict-resolution/SKILL.md).

## When to use

- User invokes `/merge-task` with a worktree path after `/push-task`
- A pushed task branch needs to be integrated into `main`
- A merge or rebase conflict must be resolved with user decisions
- Nicki is moving a task through a merge/conflict-resolution step

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Target branch | No | Defaults to `main`; user may specify another target branch |

If worktree path is missing, ask before starting.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load push handoff and identify pushed task branch
- [ ] Inspect target branch state
- [ ] Start merge into target branch
- [ ] Detect conflicts
- [ ] Ask user for every conflict resolution
- [ ] Apply user-approved resolutions
- [ ] Verify no conflict markers remain
- [ ] Write current-task/merges/<slug>.yaml
- [ ] Report summary and next command
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an absolute path.
2. Confirm the directory exists and is a git worktree for the task branch.
3. Set the scope root to that absolute path. Derive `<slug>` from the final folder name.
4. Merge handoff path: `current-task/merges/<slug>.yaml`.

**Scope rules:**

- Read only inside the task worktree scope root before checkout/merge.
- Write only:
  - files changed by the git merge under the target branch worktree
  - conflicted files under the target branch worktree, using user-approved resolutions
  - `current-task/merges/<slug>.yaml`
- Run shell commands with `working_directory` set to the target branch worktree after the target checkout is established.
- Never modify files outside the task worktree or target branch worktree.

### Step 2: Load task branch and target

Read when present:

- `current-task/current-task-context.yaml`
- `current-task/pushes/<slug>.yaml`

Identify:

- Task branch from push handoff `remote.branch`, context `git.branch`, or current task worktree branch.
- Target branch from input, default `main`.

Stop and ask when:

- The pushed task branch is missing or ambiguous.
- The target branch is missing or ambiguous.
- No push handoff exists and the user did not explicitly identify the branch to merge.

### Step 3: Inspect git state

Run and inspect on the target branch worktree:

- `git status --porcelain`
- `git branch --show-current`
- `git rev-parse --show-toplevel`
- `git merge-base --is-ancestor <task-branch> HEAD` when useful

Stop and ask when:

- The current branch is not the target branch.
- The target branch working tree has uncommitted changes before merge, unless the user explicitly asks to merge with them present.
- A merge is already in progress and user has not asked to continue it.

### Step 4: Start merge

Default target branch: `main`.

Run:

```bash
git merge --no-ff <task-branch>
```

This merge integrates the already pushed task branch into the target branch. Do not use rebase unless the user explicitly asks. Do not use strategy flags (`ours`, `theirs`) unless the user explicitly asks.

If the merge reports "Already up to date", write a `no_op` merge handoff and report.

If merge applies without conflicts, write the merge handoff and report.

### Step 5: Detect conflicts

When conflicts occur:

1. Run `git status --porcelain`.
2. Identify unmerged files.
3. Follow [conflict-resolution](../conflict-resolution/SKILL.md) for every conflicted file or hunk.

### Step 6: Apply user-approved resolutions

Apply only resolutions collected through [conflict-resolution](../conflict-resolution/SKILL.md). Record the prompt and answer in `user_resolutions`.

### Step 7: Verify merge state

Run:

- `git status --porcelain`
- Search for conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) inside changed files

If no conflicts remain, continue the merge according to the normal git merge flow. Do not push from `/merge-task`; publishing target branch updates belongs to a later workflow decision.

### Step 8: Write handoff

Write `current-task/merges/<slug>.yaml` following [merge-format.md](merge-format.md). Include:

- Task branch and target branch
- Conflict files and status
- Every user resolution
- Checks
- Blockers if unresolved

### Step 9: Report

Summarize:

- Task and target branch
- Whether conflicts were resolved
- Files resolved
- Handoff path
- Next step: Nicki updates context, then asks `Time for the feedback woof! Want?` before invoking close-task.

## Safety rules

- Merge only when `/merge-task` is explicitly invoked, Nicki invokes it after explicit user confirmation, or the user explicitly asks to merge.
- Never resolve conflicts without explicit user input.
- Never use destructive git commands (`reset --hard`, `checkout --`, `merge --abort`) unless the user explicitly approves.
- Never push.
- Never force-push.
- Never modify files outside the worktree scope root.
- When in doubt, ask.
