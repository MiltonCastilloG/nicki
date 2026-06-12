---
name: commit-task
description: "Create a local git commit for one worktree and write a commit handoff YAML."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: commit-task
---

# Commit Task

Create a **local git commit only** for one worktree. Do not push. Write a commit handoff YAML when done or blocked.

Commit schema: [commit-format.md](commit-format.md).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative |
| Commit instruction | Optional | Message preference or explicit include/exclude paths |
| Paths to stage | Optional | Agent may pass explicit list; else infer from git status |
| Handoff output path | No | Default `current-task/commits/<slug>.yaml` |

If worktree path is missing, ask before starting.

## Procedure

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Inspect git status, diff, and recent log
- [ ] Confirm commit is allowed
- [ ] Stage relevant paths
- [ ] Create local commit
- [ ] Write commit handoff YAML
- [ ] Report summary
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an absolute path.
2. Confirm the directory exists and is a git worktree.
3. Set the scope root to that absolute path. Derive `<slug>` from the final folder name.
4. Default handoff path: `current-task/commits/<slug>.yaml`.

**Scope rules:**

- Read only inside the scope root.
- Write only the commit handoff YAML.
- Run shell commands with `working_directory` set to the scope root.
- Never modify files outside the scope root.

### Step 2: Inspect git state

Run and inspect:

- `git status --porcelain`
- `git diff`
- `git diff --staged`
- `git log --oneline -5`

Stop and ask when:

- No changes exist to commit.
- Changes include likely secrets (`.env`, credentials, private keys).
- There are unrelated changes and the user did not say to include them.
- The branch is `main` or `master`.

### Step 3: Stage relevant paths

Stage only paths belonging to this task:

- Application/source changes from work
- Tests and docs created for this task
- Task metadata paths when the agent instructs inclusion

Do not stage ignored files, local env files, logs, build outputs, or unrelated user changes.

### Step 4: Commit

Draft a concise commit message from the task title or agent instruction.

**Message style: small dog, caveman-full-ish.**

- Prefer one tiny subject line, usually 3-7 words.
- Dog-like more than caveman-like: loyal, eager, plain, task-focused.
- Drop articles and filler. Keep technical nouns exact.
- Use small-dog wording when it stays clear, e.g. `good dog: fix nav links`, `small dog: add hero card`.
- If repo log uses a strict convention, keep that convention and make wording tiny/dog-like inside it.
- Add a body only when the commit needs real context.

Use a heredoc for the commit message:

```bash
git commit -m "$(cat <<'EOF'
Commit message here.

EOF
)"
```

Do not amend, push, force push, skip hooks, or update git config.

If hooks modify files and the commit succeeds, inspect status and ask before making any follow-up commit unless the repository hook clearly only formatted already staged files.

### Step 5: Write handoff

Write the handoff YAML per [commit-format.md](commit-format.md). Include:

- Commit SHA and branch when committed
- Included paths
- Excluded paths
- Check summaries
- Blockers if no commit was created

### Step 6: Report

Summarize:

- Commit SHA and message, or blockers
- Included/excluded paths
- Handoff file path

## Safety rules

- Create commits only when explicitly invoked or the user explicitly asks to commit.
- Never push.
- Never amend unless the user explicitly asks and all git-safety conditions are satisfied.
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval.
- Never commit secrets.
- When in doubt, ask.
