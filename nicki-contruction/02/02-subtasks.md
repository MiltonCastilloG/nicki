---
worktree: commandless-orchestration
generated_by: subtask-maker
spec: 02-spec.yaml
title: Task-spawn orchestration without leaf commands
constraints:
  - no-new-deps
  - global-registry-start-close-only
  - nicki-read-only-orchestrator
  - leaf-agents-atomic
  - skills-canonical-workflow
  - agents-thin-shells-only
  - no-hook-permission-changes
  - no-artifact-schema-changes
  - baseline-slices-00-01-done
  - caveman-md-default-full
---

# Subtasks

- [x] Rewrite Nicki orchestration doc so every leaf step and status update uses Task subagent_type spawn language with no slash-command examples.
- [x] Add explicit Nicki invocation section listing subagent_type values, prompt payload fields, and resume behavior for leaf transitions.
- [x] Update nicki-default rule so Nicki entry depends on Task spawn and name routing only, not on a nicki command file existing.
- [x] Tighten parent-agent rule so non-Nicki chats do not improvise multi-step pipeline transitions and may suggest Nicki instead.
- [x] Remove all leaf pipeline slash command files under commands directory including start, status update, spec, subtasks, execute, review, triage, commit, push, merge, publish, and close.
- [x] Remove nicki command file when rule-only routing fully replaces it.
- [x] Strip slash-command references from every leaf agent frontmatter description and body while keeping scope and safety rules.
- [x] Ensure each leaf agent doc points only to its skill and format schemas without duplicating skill checklists.
- [x] Replace slash-command wording in leaf skill SKILL files with subagent or Nicki Task-spawn triggers where invocation is described.
- [x] Replace slash-command cross-references in shared format docs with agent names or artifact paths only.
- [x] Document ad-hoc skill attachment as the operator escape hatch in README without adding new command files for helper skills.
- [x] Retire three-layer architecture in NICKI and replace with canonical agent plus skill table per pipeline step.
- [x] Remove slash-command-first quick start and step-by-step examples from README in favor of Nicki name or Task entry.
- [x] Align PLAN runtime layout so commands directory is not required for Nicki operation.
- [x] Sweep remaining runtime docs and agent cross-links for stale command paths or slash examples including report and construction notes where they describe current runtime.
- [x] Verify commands directory contains no leaf pipeline commands after cleanup.
- [x] Verify Nicki doc has zero canonical slash-command invocation examples for leaf steps or status update.
- [x] Verify each pipeline step is reachable as agent plus skill pair with handoff chain and state writer boundaries unchanged.
- [x] Verify nicki-default rule and README describe Nicki entry without requiring a nicki command file.
- [x] Verify helper skills remain consumable by path reference only with no new commands added this slice.
