# status.json pointer ownership — slice 01

Two parallel tracks. One writer: `current-task-update` only. Tracks own which pointers they set — additive, no overwrite.

## 01-0 — review routing (`review-routing`)

Own:
- `artifacts.review_validation`, `artifacts.review`, `artifacts.review_input`
- `open_questions` — spec mirror, acceptance reject, triage blockers
- fix-loop `history` (`step: fix`)
- `task.current_step` / `next_step` for triage → acceptance → execute-fix routes

Child spec: `01-0-spec.yaml`. Execution: `executions/review-routing.yaml`.

## 01-1 — git tail + layout (`git-tail-workspace`)

Own:
- `artifacts.merge`, `artifacts.publish`, `artifacts.commit`, `artifacts.push`
- `scope.worktree_path`, `task.project` (start-task register)
- tail step pointers: merge → publish → close

Child spec: `01-1-spec.yaml`. Execution: `executions/git-tail-workspace.yaml`.

## Cross-track lock

| Rule | Detail |
|------|--------|
| Additive | Track add own pointer field — never clobber other track field |
| Shared rename | Both child specs OK before `status-format.md` key change |
| Registry | `global-status.json` — start-task register, close-task unregister only |
| Nicki route | Read `status.json` + handoff paths — not review prose, not chat |

Serial gate: field-name align only. Tracks else concurrent.

## Umbrella skip

Umbrella no dup 01-0 / 01-1 impl. Coordination + integration verify only.
