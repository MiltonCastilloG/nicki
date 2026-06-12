---
name: close-scope
description: "Close path resolution, global-status unregister, worktree teardown. close-task only — after archive written."
disable-model-invocation: true
---

# Close Scope

Paths + registry teardown + worktree delete. Run **after** [task-archive](../task-archive/SKILL.md) writes both files.

## 1. Resolve paths

| Input | Req |
|-------|-----|
| Worktree path | yes |

Missing → ask. Stop.

1. Path → absolute. Dir exist?
2. `slug` = final folder name.
3. `repo_root` — project git root: parent of `projects/<project>/worktrees/<slug>`, or parent of legacy `worktrees/<slug>`. Ambiguous → ask.
4. `workspace_root` — dir with `global-status.json`.
5. `archive_dir` = `task-archive/<slug>/` under `repo_root`.

## 2. Unregister

**Only close-task** mutates `global-status.json`. Schema: [global-status-format.md](../current-task-update/global-status-format.md).

Prereq: `task-archive/<slug>/summary.yaml` + `report.md` exist.

```bash
.cursor/skills/close-scope/scripts/unregister-global-status.sh "<workspace_root>" "<task_id>"
```

`task_id` from status or registry. No file → script skips (exit 0).

## 3. Teardown

Prereq: archive written + unregister done (or skip). Nicki confirm: `Time for the feedback woof! Want?`

```bash
rm -rf -- "<worktree_path>"
```

Whole worktree gone — not only `current-task/`.

## Never delete

`task-archive/`, repo workflow docs, other worktrees.

## Report

Archive paths, unregister result, worktree removed, suggestion count.
