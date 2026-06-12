---
worktree: skills-sheep-separation
generated_by: subtask-maker
spec: 03-spec.yaml
title: Skills lock + sheep agents
constraints:
  - no-new-deps
  - global-registry-start-close-only
  - nicki-read-only-orchestrator
  - sheep-agents-atomic
  - skills-canonical-workflow
  - sheep-thin-shells-only
  - users-attach-skills-not-sheep
  - baseline-slices-00-02-done
  - caveman-md-default-lite
---

# Subtasks

## Phase 1 — skill lock + sheep voice

- [x] Remove disable-model-invocation and metadata.subagent from spec-maker, subtask-maker, execute-plan, review-execution, start-task, sync-task, integrate-task, and conflict-resolution SKILL frontmatter.
- [x] Keep disable-model-invocation on current-task-update, close-task, close-scope, task-archive, hook-contract, validation, and caveman.
- [x] Rewrite .cursor/skills/README.md with three-layer table, invocation policy, pure-functionality rules, and workflow-skill exceptions naming sheep bindings.
- [x] Author sheep-* agent bodies with "You are a sheep. Nicki sent you." voice and "Nicki sheep. Path only. Skill: …" descriptions.
- [x] Keep disk inputs, output paths, scope rules, and safety in each sheep agent; move full procedure checklists to skills only.

## Phase 2 — sheep rename + routing

- [x] Create sheep-start, sheep-spec, sheep-subtask, sheep-execute, sheep-review, sheep-sync, sheep-integrate, sheep-close, and sheep-status under .cursor/agents/.
- [x] Delete legacy leaf agent files start-task, spec-maker, subtask-maker, execute-plan, review-execution, close-task, and current-task-update.
- [x] Add .cursor/skills/nicki/routing.yaml with steps.*.sheep keys, gates, artifacts, readiness_routing, and sheep_return_contract.
- [x] Set status_update.sheep to sheep-status with skip_user_confirm in routing.yaml.
- [x] Rewrite nicki.md for sheep terminology, routing.yaml bootstrap, sheep map table, and forward sheep return YAML to sheep-status.
- [x] Document in nicki.md that Nicki never reads .cursor/agents/sheep-*.md — sheep load their own disk inputs.
- [x] Update README.md quick start and pipeline table for sheep-* subagent_type names and three-layer diagram.
- [x] Update NICKI.md architecture section for skills vs sheep vs Nicki and canonical workflow with sheep-status after each sheep.
- [x] Add complexity.md with sheep-* agent load scores and subtask-maker load-trim before/after table.

## Git tail simplification

- [x] Delete commit-task, push-task, merge-task, and publish-task agents and skills including format docs and publish smoke script.
- [x] Add sync-task skill with sync-format.md — local commit, merge main into feature branch, push feature branch.
- [x] Add integrate-task skill with integrate-format.md — merge feature into main, push main, handoff in task worktree.
- [x] Add sheep-sync and sheep-integrate agents binding disk inputs to sync-task and integrate-task skills plus conflict-resolution.
- [x] Wire sync and integrate steps in routing.yaml with user_confirm gates and artifact keys sync and integrate.
- [x] Update agent-permissions.json — sheep-* keys (sheep-start through sheep-close, sheep-status); remove commit/push/merge/publish/out-of-scope legacy keys.
- [x] Relocate smoke-git-tail.sh under integrate-task/scripts/ with sync/integrate path and removed four-step tail checks.
- [x] Update PLAN.md runtime table — sync/integrate replace commit/push/merge/publish; conflict-resolution note updated.

## Validation fold + review cleanup

- [x] Delete review-triage agent and skill including review-guidance-format under review-triage and smoke-readiness-routing.sh.
- [x] Add validation skill with validation-format.md and disable-model-invocation; move readiness and next-steps procedure there.
- [x] Move review-guidance-format.md under review-execution/ for sheep-review disk inputs.
- [x] Update review-execution SKILL to run validation inline and reference validation-format.md.
- [x] Configure sheep-review to load review-execution plus validation-format.md in one spawn.
- [x] Add validation/scripts/smoke-readiness-mapping.sh with routing.yaml review_validation checks and fix-loop fixture.
- [x] Add validation/scripts/fixtures for scope-only and verify-fail validation YAML examples.

## Skills stripped of pipeline leakage

- [x] Remove status.json, pipeline step name, and "spawn next" references from leaf skill SKILL bodies where present.
- [x] Ensure leaf skills declare explicit inputs table — worktree path and artifact paths from sheep prompt, not implicit disk discovery.
- [x] Trim format cross-references so each format file documents one artifact type without multi-agent maps.
- [x] Add subtask-maker/spec-input.md for read-only spec fields and open_questions gate without loading full spec-format.md.
- [x] Compress subtask-maker SKILL and subtask-format.md — drop triple-duplicated scope/safety; inline lite caveman voice in subtask-format.
- [x] Slim sheep-subtask.md to disk I/O and return contract only (~40 lines).

## Write boundaries and status formats

- [x] Update global-status-format.md write boundary — sheep-start register, sheep-close unregister only.
- [x] Update status-format.md write boundary — sheep-status sole writer for current-task/status.json.
- [x] Update close-scope SKILL — only sheep-close mutates global-status.json via unregister script.
- [x] Update current-task-update SKILL and format docs for sheep-status terminology and registry read-only rule.
- [x] Deprecate current-task-context-format.md pointer text toward status.json and global-status.json.

## Caveman and rule cleanup

- [x] Simplify caveman skill — default lite intensity, structured lite/full sections, disable-model-invocation retained.
- [x] Remove "ACTIVE EVERY RESPONSE" persistence block from caveman skill and nicki-default.mdc rule.
- [x] Delete next-step-spec skill superseded by validation next-steps YAML output.

## Docs, reports, and verification

- [x] Move report.md and report-2.md from repo root to nicki-contruction/; README links to nicki-contruction/report-2.md.
- [x] State in README and NICKI that parent agent must not Task-spawn sheep — ad-hoc work attaches skills directly.
- [x] Verify nine sheep-*.md agents exist and no legacy leaf pipeline agent files remain under .cursor/agents/.
- [x] Verify routing.yaml sheep keys match nicki.md sheep map for start through close plus sheep-status.
- [x] Verify pipeline skills lack disable-model-invocation and workflow-only skills retain it.
- [x] Verify commit/push/merge/publish skills absent; sync-task and integrate-task skills present with handoff schemas.
- [x] Verify review-triage skill absent; validation skill present with validation-format.md and smoke fixtures.
- [x] Update smoke-readiness-mapping.sh and smoke-git-tail.sh to assert sheep-review, sheep-sync, sheep-integrate paths.
- [x] Update nicki-default.mdc — ad-hoc skills only; parent must never Task-spawn sheep.
- [x] Update register-global-status.sh and unregister-global-status.sh comments — sheep-start / sheep-close only.
