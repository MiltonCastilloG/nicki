# Status input (read-only)

Per-task `current-task/status.json`. Writer schema: [status-format.md](status-format.md).

**Nicki bootstrap:** `bootstrap-context.py` stdout supplies `next_step`, `completed_steps`, and `readiness` — do not re-read status fields during bootstrap.

## Gates (non-bootstrap)

- **`describe` → `spec`:** `artifacts.story` must exist and story file on disk.
- **`spec` → `subtasks`:** spec artifact `open_questions` must be empty (load spec file when checking).
- **Post-review routing:** `readiness` comes from bootstrap stdout (validation YAML via script).

## Readiness (from bootstrap stdout)

| `readiness` | Route | Sync |
|-------------|-------|------|
| `ready_for_acceptance` | acceptance | blocked |
| `fix_required` | execute | blocked |
| `blocked` | ask user | blocked |
