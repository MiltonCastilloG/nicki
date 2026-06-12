---
worktree: review-routing
generated_by: subtask-maker
spec: 01-0-spec.yaml
title: Review loop and orchestration routing
constraints:
  - no-new-deps
  - nicki-read-only-orchestrator
  - leaf-agents-atomic
  - parallel-with-01-1
  - global-registry-start-close-only
  - status-update-writes-per-task-only
  - caveman-md-default-full
---

# Subtasks

- [x] Extend validation-format readiness block — status enum, recommended_next_step, blockers non-empty only for fix_required or blocked.
- [x] Wire review-triage emit readiness on each validation write; status-update refresh validation artifact pointer after triage.
- [x] Nicki resume read readiness from validation pointer — block commit-task on fix_required or blocked; never infer next step from review markdown alone.
- [x] fix_required fix loop append one-sentence subtasks — keep prior [x], ref validation artifact; status history record iteration; next_step route execute.
- [x] ready_for_acceptance Nicki-only acceptance checkpoint — show disk summary; no commit-task until user accepts; reject update blockers and route fix or describe.
- [x] All subtasks done or no review_scope → full review; partial review_scope need user confirm, limit findings, no commit without full readiness.
- [x] Non-empty spec open_questions block subtask-maker — mirror in status open_questions; cleared empty advance next_step subtasks.
- [x] Grep workflow bundle for readiness routing, fix loop, acceptance gate, partial scope, open_questions gate — align 01-0-stories Gherkin.
- [x] Smoke fix-loop append keep [x] and validation pointer round-trip readiness without chat inference.
