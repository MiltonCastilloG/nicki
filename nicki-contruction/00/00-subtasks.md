---
worktree: status-architecture
generated_by: subtask-maker
spec: 00-spec.yaml
title: JSON status architecture migration
constraints:
  - no-new-deps
  - global-registry-start-close-only
  - nicki-read-only-orchestrator
  - leaf-agents-atomic
  - caveman-md-default-full
  - caveman-skill-required-for-md-writes
---

# Subtasks

- [x] Lock open_questions in 00-spec.yaml or document chosen defaults in status schemas before runtime migration.
- [x] Define global-status.json schema: version, active_task, tasks map with project, slug, worktree_path, status_path per task id.
- [x] Define per-task status.json schema: task step pointers, scope, artifact pointers, open_questions, append-only history.
- [x] Write schema docs for both JSON status files alongside current-task-update skill area.
- [x] Evolve current-task-update into status-update agent: write only per-task status.json, never global-status.json.
- [x] Wire start-task: register task in global-status.json, init per-task status.json with start or describe next pointers.
- [x] Enforce global registry write boundary: only start-task and close-task may mutate global-status.json.
- [x] Wire close-task: unregister task in global-status.json after archive write, update active_task when needed.
- [x] Update close-task archive step: durable report before worktree delete, preserve spec and process summary per close policy.
- [x] Deprecate current-task-context.yaml as canonical authority across NICKI.md and nicki agent bootstrap rules.
- [x] Update nicki.md bootstrap: read global-status.json when task id known, then per-task status.json from status_path; chat not authoritative.
- [x] Migrate leaf agent and skill reads from context YAML to per-task status.json and artifact pointers.
- [x] Keep YAML and Markdown handoff bodies unchanged; status.json stores paths only, not handoff content.
- [x] Add readiness routing: per-task status records latest review-validation artifact pointer for Nicki and hooks.
- [x] Implement blocked-state in status.json: non-empty open_questions and blocking next_step until cleared or override.
- [x] Generalize path language for standalone workspace: projects per project name with project-local worktrees.
- [x] Document hook contract: task id → global-status.json → status_path → status.json with example jq resolution.
- [x] Add example hook script or doc snippet that resolves project, worktree, current_step, next_step via JSON only.
- [x] Update runtime docs: NICKI.md, nicki agent, status-update skill describe JSON model, write boundaries, bootstrap order.
- [x] Wire caveman skill into subtask-maker and other MD-writing workflow agents as required read before Markdown output.
- [x] Apply caveman full style to Markdown handoffs this migration touches: subtasks, story artifacts, archive report prose.
- [x] Add smoke checks that global-status.json unchanged after simulated leaf step status-update.
- [x] Add smoke checks that per-task status.json updates step pointers and history without touching global registry.
- [x] Verify no runtime doc still calls current-task-context.yaml canonical orchestration source of truth.
- [x] Verify documented jq path resolves status_path from global-status.json by task id.
- [x] Run grep or manual pass on changed runtime files for stale context YAML references where status.json should win.
- [x] Run lint or doc consistency check on changed workflow bundle if project lint covers markdown or yaml in .cursor.
