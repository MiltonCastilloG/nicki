---
name: push-task
description: "Merge main into a committed current-task worktree branch, resolve conflicts only with user input, push to remote, and write current-task/pushes/<slug>.yaml. Use when the user runs /push-task or asks to publish task work after /commit-task."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: push-task
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

# Push Task

Merge `main` into an already committed task branch, then push it to remote. If the merge conflicts, follow the shared [conflict-resolution](../conflict-resolution/SKILL.md) protocol. Do not open PRs. Write `current-task/pushes/<slug>.yaml`.

Push schema: [push-format.md](push-format.md).
Conflict protocol: [conflict-resolution](../conflict-resolution/SKILL.md).

## When to use

- User invokes `/push-task` with a worktree path
- `/commit-task` has created `current-task/commits/<slug>.yaml`
- Nicki is moving a task from `commit` to `push`

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Commit handoff | Preferred | `@current-task/commits/<slug>.yaml`; auto-load when omitted |
| Base branch | No | Defaults to `main`; merge this into the task branch before push |

If worktree path is missing, ask before starting.

If no commit handoff exists, inspect git state and ask before pushing.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load commit handoff and current-task context
- [ ] Inspect branch, remote, status, and upstream
- [ ] Merge base branch into task branch
- [ ] Resolve conflicts with user input if needed
- [ ] Confirm push is allowed
- [ ] Push branch
- [ ] Write current-task/pushes/<slug>.yaml
- [ ] Report summary and next step
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an absolute path.
2. Confirm the directory exists and is a git worktree.
3. Set the scope root to that absolute path. Derive `<slug>` from the final folder name.
4. Push handoff path: `current-task/pushes/<slug>.yaml`.

**Scope rules:**

- Read only inside the scope root.
- Write only:
  - files changed by the pre-push merge under the worktree
  - conflicted files under the worktree, using user-approved resolutions
  - `current-task/pushes/<slug>.yaml`
- Run shell commands with `working_directory` set to the scope root.
- Never modify files outside the scope root.

### Step 2: Load and inspect

Read when present:

- `current-task/current-task-context.yaml`
- `current-task/commits/<slug>.yaml`

Run and inspect:

- `git status --porcelain`
- `git branch --show-current`
- `git remote -v`
- `git rev-parse HEAD`
- `git status -sb`
- `git fetch origin main` when `origin` exists

Stop and ask when:

- The branch is `main` or `master`.
- There is no local commit handoff and the user did not explicitly ask to push.
- The working tree has uncommitted changes before the base merge other than expected local metadata (`current-task/current-task-context.yaml`, `current-task/commits/<slug>.yaml`, and the push handoff you will write).
- The remote is missing or ambiguous.
- The branch appears already pushed and up to date.

### Step 3: Merge base branch before push

Default base branch: `main`. Prefer the fetched remote base `origin/main` when available so the task branch is current before publish.

Run:

```bash
git fetch origin main
git merge origin/main
```

Use an explicit base branch if provided by the user. If the remote base is missing or ambiguous, ask before falling back to a local base branch.

If conflicts occur, follow [conflict-resolution](../conflict-resolution/SKILL.md) for every conflicted file or hunk. Do not infer a resolution.

If the merge creates a merge commit automatically, record it in the push handoff. If the merge requires manual conflict resolution, complete the normal git merge flow after all user-approved resolutions are staged.

Do not use rebase or strategy flags (`ours`, `theirs`) unless the user explicitly asks.

### Step 4: Push

Default command:

```bash
git push -u origin HEAD
```

Use the tracked remote branch when it already exists and is unambiguous.

Do not force push. Do not push tags. Do not create commits except the required pre-push merge commit. Do not open PRs.

### Step 5: Write handoff

Write `current-task/pushes/<slug>.yaml` following [push-format.md](push-format.md). Include:

- Remote and branch
- Commit SHA
- Base branch merged before push
- Conflict resolution summary, if any
- Upstream branch
- Blockers if no push was performed

### Step 6: Report

Summarize:

- Branch pushed and commit SHA, or blockers
- Handoff file path
- Suggested next step: merge the pushed task branch into `main` with `/merge-task`

## Safety rules

- Push only when `/push-task` is explicitly invoked, Nicki invokes it after explicit user confirmation, or the user explicitly asks to push.
- Never force push.
- Never push `main` or `master`.
- Never amend or rewrite commits.
- Only create a merge commit as the result of the required pre-push base merge.
- Never update git config.
- When in doubt, ask.
