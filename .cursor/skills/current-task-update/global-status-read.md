# Global status input (read-only)

Workspace `global-status.json` — task registry. **Read** for `active_task` and `status_path`. Writer schema: [global-status-format.md](global-status-format.md).

## Fields to read

| Field | Use |
|-------|-----|
| `active_task` | Preferred task id when user did not specify |
| `tasks[id].project` | Managed project name |
| `tasks[id].slug` | Worktree slug |
| `tasks[id].worktree_path` | Path to task worktree |
| `tasks[id].status_path` | Path to per-task `status.json` |

Resolve status path:

```bash
jq -r --arg id "42" '.tasks[$id].status_path' global-status.json
```

## Minimal shape

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
