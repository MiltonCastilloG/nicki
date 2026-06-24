---
name: close-scope
description: "Close path resolution, global-status unregister, worktree teardown. close-task only — after report.yaml, report.md, story.md exist."
disable-model-invocation: true
---

# Close Scope

Paths + registry teardown + worktree delete. Run **after** [task-archive](../task-archive/SKILL.md) writes `report.yaml`, `report.md`, and `story.md`.

## 1. Resolve paths

| Input | Req |
|-------|-----|
| Worktree path | yes |

Missing → ask. Stop.

1. Path → absolute. Dir exist?
2. `slug` = final folder name.
3. `repo_root` — project git root: parent of `projects/<project>/worktrees/<slug>`, or parent of legacy `worktrees/<slug>`. Ambiguous → ask.
4. `workspace_root` — dir with `global-status.json`.
5. `archive_dir` = `docs/archive/<slug>/` under `repo_root`.

## 2. Unregister

**Only sheep-close** mutates `global-status.json`. Schema: [global-status-format.md](../current-task-update/global-status-format.md).

Prereq: `docs/archive/<slug>/report.yaml`, `report.md`, and `story.md` exist.

```bash
.cursor/skills/close-scope/scripts/unregister-global-status.sh "<workspace_root>" "<task_id>"
```

`task_id` from status or registry. No file → script skips (exit 0).

## 3. Teardown

Prereq: archive written + unregister done (or skip). Nicki confirm: archive and delete worktree.

Capture the task branch from `git worktree list` **before** delete (needed when the folder is already gone but registration is `prunable`).

```bash
.cursor/skills/close-scope/scripts/teardown-worktree.sh "<workspace_root>" "<worktree_path>"
```

Script steps:

1. `rm -rf` the worktree path (skip if already missing)
2. `git worktree prune` at project git root
3. `git branch -D <branch>` when the branch is not checked out in any remaining worktree

Do **not** delete remote branches or run `git push origin --delete` — operator may push `main` only.

Whole worktree gone — not only `current-task/`.

## 4. Regenerate workspace

From `workspace_root` after teardown:

```bash
bash scripts/generate-code-workspace.sh
```

Regen failure: warn the operator; do not restore the deleted worktree.

## Never delete

`docs/archive/`, repo workflow docs, other worktrees.

## Report

Archive paths, unregister result, worktree removed, branch deleted (if any), prune result, suggestion count.
