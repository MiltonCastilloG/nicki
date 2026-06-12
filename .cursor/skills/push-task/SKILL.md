---
name: push-task
description: "Merge a base branch into a task branch, resolve conflicts with user input, push to remote, write push handoff YAML."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: push-task
---

# Push Task

Merge a base branch into an already committed task branch, then push it to remote. If the merge conflicts, follow [conflict-resolution](../conflict-resolution/SKILL.md). Do not open PRs.

Push schema: [push-format.md](push-format.md).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative |
| Commit handoff | Preferred | Path to commit YAML — confirms SHA/branch |
| Base branch | No | Defaults to `main`; merged into task branch before push |
| Handoff output path | No | Default `current-task/pushes/<slug>.yaml` |

If worktree path is missing, ask before starting.

If no commit handoff exists, inspect git state and ask before pushing.

## Procedure

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load commit handoff when provided
- [ ] Inspect branch, remote, status, and upstream
- [ ] Merge base branch into task branch
- [ ] Resolve conflicts with user input if needed
- [ ] Confirm push is allowed
- [ ] Push branch
- [ ] Write push handoff YAML
- [ ] Report summary
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an absolute path.
2. Confirm the directory exists and is a git worktree.
3. Set the scope root to that absolute path. Derive `<slug>` from the final folder name.
4. Default handoff path: `current-task/pushes/<slug>.yaml`.

**Scope rules:**

- Read only inside the scope root.
- Write only:
  - files changed by the pre-push merge under the worktree
  - conflicted files under the worktree, using user-approved resolutions
  - the push handoff YAML
- Run shell commands with `working_directory` set to the scope root.
- Never modify files outside the scope root.

### Step 2: Inspect git state

Run and inspect:

- `git status --porcelain`
- `git branch --show-current`
- `git remote -v`
- `git rev-parse HEAD`
- `git status -sb`
- `git fetch origin main` when `origin` exists

Stop and ask when:

- The branch is `main` or `master`.
- There is no local commit and the user did not explicitly ask to push.
- The working tree has uncommitted changes before the base merge (except expected local metadata the agent allows).
- The remote is missing or ambiguous.
- The branch appears already pushed and up to date.

### Step 3: Merge base branch before push

Default base branch: `main`. Prefer fetched remote base `origin/main` when available.

```bash
git fetch origin main
git merge origin/main
```

Use an explicit base branch if provided. If the remote base is missing or ambiguous, ask before falling back to a local base branch.

If conflicts occur, follow [conflict-resolution](../conflict-resolution/SKILL.md) for every conflicted file or hunk.

If the merge creates a merge commit automatically, record it in the push handoff. Complete the normal git merge flow after all user-approved resolutions are staged.

Do not use rebase or strategy flags (`ours`, `theirs`) unless the user explicitly asks.

### Step 4: Push

Default command:

```bash
git push -u origin HEAD
```

Use the tracked remote branch when it already exists and is unambiguous.

Do not force push. Do not push tags. Do not create commits except the required pre-push merge commit. Do not open PRs.

### Step 5: Write handoff

Write the handoff YAML per [push-format.md](push-format.md). Include:

- Remote and branch
- Commit SHA
- Base branch merged before push
- Conflict resolution summary, if any
- Upstream branch
- Blockers if no push was performed

### Step 6: Report

Summarize branch pushed and commit SHA, or blockers, and handoff file path.

## Safety rules

- Push only when explicitly invoked or the user explicitly asks to push.
- Never force push.
- Never push `main` or `master`.
- Never amend or rewrite commits.
- Only create a merge commit as the result of the required pre-push base merge.
- Never update git config.
- When in doubt, ask.
