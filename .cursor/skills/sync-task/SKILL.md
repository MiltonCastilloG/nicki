---
name: sync-task
description: "Local commit, merge main into feature branch, push feature branch; write sync handoff YAML."
---

# Sync Task

Commit locally, merge base branch into the feature branch, then push the feature branch to remote. If the pre-push merge conflicts, follow [conflict-resolution](../conflict-resolution/SKILL.md).

Schema: [sync-format.md](sync-format.md).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative — task worktree |
| Base branch | No | Defaults to `main`; merged into feature before push |
| Commit instruction | Optional | Message preference or explicit include/exclude paths |
| Handoff output path | No | Default `current-task/syncs/<slug>.yaml` |

If worktree path is missing, ask before starting.

## Procedure

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Inspect git state
- [ ] Confirm sync is allowed (gates)
- [ ] Stage and create local commit
- [ ] Merge base branch into feature branch
- [ ] Resolve conflicts with user input if needed
- [ ] Push feature branch
- [ ] Write sync handoff YAML
- [ ] Report summary
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an absolute path.
2. Confirm the directory exists and is a git worktree.
3. Set the scope root to that absolute path. Derive `<slug>` from the final folder name.
4. Default handoff path: `current-task/syncs/<slug>.yaml`.

**Scope rules:**

- Read only inside the scope root.
- Write only:
  - the sync handoff YAML
  - files changed by the pre-push merge under the worktree
  - conflicted files under the worktree (user-approved resolutions)
- Run shell commands with `working_directory` set to the scope root.
- Never modify files outside the scope root.

### Step 2: Inspect git state

Run and inspect:

- `git status --porcelain`
- `git diff` / `git diff --staged`
- `git branch --show-current`
- `git remote -v`
- `git log --oneline -5`

Stop and ask when:

- The branch is `main` or `master`.
- Changes include likely secrets (`.env`, credentials, private keys).
- There are unrelated changes and the user did not say to include them.
- No changes exist to commit and user did not ask to push only.
- Remote is missing or ambiguous.

### Step 3: Commit phase

Stage only paths belonging to this task (application changes, tests, docs, task metadata when policy requires).

Draft a concise commit message — short subject (3–10 words), plain and technical. Match repo convention when present.

```bash
git commit -m "$(cat <<'EOF'
Commit message here.

EOF
)"
```

Do not amend, skip hooks, or update git config.

If commit phase fails, write handoff with `status: blocked` and stop.

### Step 4: Pre-push merge

Default base branch: `main`. Prefer fetched remote base `origin/main` when available.

```bash
git fetch origin main
git merge origin/main
```

If conflicts occur, follow [conflict-resolution](../conflict-resolution/SKILL.md).

If merge succeeds but push not yet run, record progress in handoff — use `status: partial` if stopping before push.

### Step 5: Push feature branch

```bash
git push -u origin HEAD
```

Do not force push. Do not push `main` or `master`. Do not push tags.

If push fails, write handoff with `status: partial` (commit + merge done, push blocked).

### Step 6: Write handoff

Write per [sync-format.md](sync-format.md). Include commit phase, pre_push_merge, remote/push, conflicts, blockers.

### Step 7: Report

Summarize commit SHA, branch pushed, or blockers and handoff path.

## Safety rules

- Sync only when explicitly invoked or the user explicitly asks.
- Never force push.
- Never push `main` or `master`.
- Never amend unless the user explicitly asks and all git-safety conditions are satisfied.
- Never commit secrets.
- Never update git config.
- When in doubt, ask.
