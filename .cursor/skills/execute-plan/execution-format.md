# Execution format (deprecated)

**Deprecated as a live writer schema.** `execute-plan` / `sheep-execute` no longer write
`current-task/executions/<slug>.json`. Review uses the git diff plus available
`current-task/` files. Kept only so archive/readers can interpret legacy handoffs.

Default path (legacy): `current-task/executions/<slug>.json` under the worktree scope root.

## Top-level fields (legacy)

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Source subtask list and execution status |
| `paths` | Yes | Touched paths |
| `subtasks` | Yes | Per-item status |
| `verify` | If verify ran | Command evidence from execution |
| `deviations` | No | Intentional departures |
| `open_questions` | No | Blockers |
| `hotspots` | No | Review focus hints |
| `review_scope` | No | Hints for full, triage, or focused review |

See git history for full examples. Do not create new execution files.
