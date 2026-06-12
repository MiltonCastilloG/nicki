# global-status.json format

Workspace-root task registry. **JSON only.** Source of truth for which tasks exist and where per-task status lives.

**Write boundary:** only `start-task` (register) and `close-task` (unregister). No leaf step or status-update agent may modify this file.

Default path: `global-status.json` at Nicki workspace root (repo root in single-repo mode).

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `version` | Yes | Schema version; use `1` |
| `active_task` | No | Task id Nicki or hook should prefer when user did not specify id |
| `tasks` | Yes | Map of task id → registry entry |

## Task registry entry

Each key in `tasks` is a stable string id (numeric string recommended, e.g. `"42"`).

| Field | Required | Description |
|-------|----------|-------------|
| `project` | Yes | Managed project name (e.g. `castlemill-landing`) |
| `slug` | Yes | Worktree folder slug (e.g. `hero-section`) |
| `worktree_path` | Yes | Repo-relative path to task worktree |
| `status_path` | Yes | Repo-relative path to per-task `status.json` |

## Example

```json
{
  "version": 1,
  "active_task": "42",
  "tasks": {
    "42": {
      "project": "castlemill-landing",
      "slug": "hero-section",
      "worktree_path": "projects/castlemill-landing/worktrees/hero-section",
      "status_path": "projects/castlemill-landing/worktrees/hero-section/current-task/status.json"
    }
  }
}
```

## Resolved defaults (status-architecture task)

| Decision | Choice |
|----------|--------|
| Task id | Numeric string key; `slug` duplicated in entry |
| `active_task` | Present when multiple tasks may be open |
| Registry filename | `global-status.json` (not root `status.json`) |
| Close unregister | Remove entry after archive; clear or re-point `active_task` |

## Hook resolution

```bash
jq -r --arg id "42" '.tasks[$id].status_path' global-status.json
```
