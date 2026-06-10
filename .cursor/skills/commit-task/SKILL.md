---
name: commit-task
description: "Create a local git commit for a completed current-task worktree and write current-task/commits/<slug>.yaml. Use when the user runs /commit-task or asks to commit task work after review/triage."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: commit-task
  tools:
    read: true
    write: true
    delete: false
    shell: true
    grep: false
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

# Commit Task

Create a **local git commit only** for one completed worktree. Do not push. Write `current-task/commits/<slug>.yaml` as the handoff to `/push-task`.

Commit schema: [commit-format.md](commit-format.md).

## When to use

- User invokes `/commit-task` with a worktree path
- Review and triage are complete, and the user wants a local commit
- Nicki is moving a task from `triage` to `commit`

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Commit instruction | Optional | Message preference or explicit include/exclude paths |

If worktree path is missing, ask before starting.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Load current-task context and latest review/triage artifacts
- [ ] Inspect git status, diff, and recent log
- [ ] Confirm commit is allowed
- [ ] Stage relevant paths
- [ ] Create local commit
- [ ] Write current-task/commits/<slug>.yaml
- [ ] Report summary and next command
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an absolute path.
2. Confirm the directory exists and is a git worktree.
3. Set the scope root to that absolute path. Derive `<slug>` from the final folder name.
4. Commit handoff path: `current-task/commits/<slug>.yaml`.

**Scope rules:**

- Read only inside the scope root.
- Write only `current-task/commits/<slug>.yaml`.
- Run shell commands with `working_directory` set to the scope root.
- Never modify files outside the scope root.

### Step 2: Load task state

Read when present:

- `current-task/current-task-context.yaml`
- `current-task/reviews/<slug>.yaml`
- latest `current-task/review-validations/rN-validation.yaml`
- `current-task/merges/<slug>.yaml` when present
- `current-task/next-steps/*.yaml` only to know they exist, not to include automatically unless relevant

If the latest review is not approved, or latest triage has valid blocking findings, ask before committing.

### Step 3: Inspect git state

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
- The task state indicates unresolved blockers.

### Step 4: Stage relevant paths

Stage only paths belonging to this task:

- Application/source changes from execution
- Tests and docs created for this task
- `current-task/` artifacts for the task (`current-task-context.yaml`, `specs`, `plans`, `executions`, `reviews`, `review-validations`, `review-inputs`, `next-steps`, `merges`)

Do not stage ignored files, local env files, logs, build outputs, or unrelated user changes.

### Step 5: Commit

Draft a concise commit message from the task title/spec/review summary.

**Message style: small dog, caveman-full-ish.**

- Prefer one tiny subject line, usually 3-7 words.
- Dog-like more than caveman-like: loyal, eager, plain, task-focused.
- Drop articles and filler. Keep technical nouns exact.
- Use small-dog wording when it stays clear, e.g. `good dog: fix nav links`, `small dog: add hero card`, `pup: tidy review notes`.
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

### Step 6: Write handoff

Write `current-task/commits/<slug>.yaml` following [commit-format.md](commit-format.md). Include:

- Commit SHA and branch when committed
- Included paths
- Excluded paths
- Check summaries
- Blockers if no commit was created

The commit handoff is written after the commit, so it is expected to remain as local metadata unless the user later chooses to commit workflow metadata separately.

### Step 7: Report

Summarize:

- Commit SHA and message, or blockers
- Included/excluded paths
- Handoff file path
- Next command:

```
/push-task worktrees/<slug> @current-task/commits/<slug>.yaml
```

## Safety rules

- Create commits only when `/commit-task` is explicitly invoked, Nicki invokes it after explicit user confirmation, or the user explicitly asks to commit.
- Never push.
- Never amend unless the user explicitly asks and all git-safety conditions are satisfied.
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval.
- Never commit secrets.
- When in doubt, ask.
