---
worktree: report-follow-up-01
generated_by: subtask-maker
spec: 01-spec.yaml
title: Report follow-up slice 01 — umbrella
constraints:
  - no-new-deps
  - slice-00-baseline-immutable
  - global-registry-start-close-only
  - status-update-only-writer
  - nicki-read-only-orchestrator
  - leaf-agents-atomic
  - parallel-tracks-no-serial-block
  - caveman-md-default-full
---

# Subtasks

- [x] Write pointer ownership doc: 01-0 own validation, acceptance, open_questions, fix-loop pointers; 01-1 own merge, publish, close, start path metadata.
- [x] Lock cross-track status.json field names additive per ownership; shared rename need both tracks OK first.
- [x] Confirm child specs own track deliverables — umbrella skip 01-0 and 01-1 impl dup.
- [x] Verify parallel 01-0 and 01-1 run concurrent — serial block only on field-name align gate.
- [x] Smoke both child tracks update status pointers — no duplicate writers, no leaf global-registry mutation.
- [x] Smoke combined disk workflow triage through acceptance, commit, merge, publish, close — no chat-inferred routing.
- [x] Verify Nicki bootstrap and decision table read status plus handoff paths only — not review prose or chat.
- [x] Verify report open list closed jointly across tracks: readiness, fix loop, acceptance, publish, paths, docs.
- [x] Regression check slice 00 baseline intact: registry start close only, per-task status each step, hook resolve by task id.
- [x] Regression check no YAML context canonical orchestration comeback in runtime docs or agents.
- [x] Verify status pointers coexist after both child specs pass — ownership boundaries hold.
- [x] Run umbrella constraint pass: tighten existing bundle only, no new leaf agents except publish-task per 01-1.
