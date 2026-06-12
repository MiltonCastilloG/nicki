# Nicki Workflow Review Report

## Purpose

Project-lead review of Nicki current-task workflow. Three read-only subagent passes (spec, execute/review/triage, commit/push/merge/close) plus direct read of agents, skills, schemas, scripts.

Original review wrote only this file. Status architecture migration (`00-*`) and slice 01 follow-up (`01-0`, `01-1`, umbrella) shipped runtime changes below.

## Executive Summary

Core design solid: Nicki orchestrates, leaf agents bounded, disk handoffs under `current-task/`, state writer after each step.

**Slice 00 (done):** two-layer JSON — `global-status.json` (start/close only) + per-task `current-task/status.json` (every step). Hooks resolve task id → registry → `status_path`. YAML/Markdown handoffs stay; status holds paths only. `current-task-context.yaml` deprecated.

**Slice 01 (done):** readiness in validation YAML, fix-loop append, acceptance gate, `publish-task` leaf, project-local worktrees in start scripts, CONTRIBUTING optional, `/nicki` command file. Pointer ownership: `nicki-contruction/01/status-pointer-ownership.md`.

**Remain:** prove close/archive on first real task close (policy encoded).

## Agreed Direction

| Decision | Choice |
|----------|--------|
| Workspace model | Standalone Nicki; `projects/<project>/worktrees/<slug>` |
| Nicki entry | Subagent; `/nicki` command; future custom mode noted not promised |
| Orchestration state | JSON status (registry + per-task); not YAML context |
| Registry writes | `start-task` + `close-task` only |
| Per-task writes | `current-task-update` → `status.json` only |
| Readiness | `review-validations/*.yaml` + pointer in status |
| User acceptance | Nicki checkpoint after triage, before `commit-task` |
| Publish | `publish-task` after `merge-task`, before close |
| Close | Archive first; delete whole worktree; merge/publish handoffs or override |
| Markdown voice | Caveman full per `.cursor/skills/caveman/SKILL.md` |

## Status Architecture (Slice 00)

Source: `00-spec.yaml`, `00-subtasks.md` (26/26). Execution: `current-task/executions/status-architecture.yaml`.

```text
global-status.json          # workspace root; start/close only
  tasks[<id>].status_path → current-task/status.json
    artifacts.* → YAML/Markdown handoffs
```

Shipped: schemas, agents/skills, hook contract, smoke scripts, runtime docs, archive format, examples.

## Slice 01 Follow-up (Implemented)

| Track | Scope | Execution |
|-------|-------|-----------|
| 01-0 | Readiness routing, fix loop, acceptance, partial review, spec gate | `nicki-contruction/01/executions/review-routing.yaml` |
| 01-1 | publish-task, merge/close tail, project worktrees, docs | `nicki-contruction/01/executions/git-tail-workspace.yaml` |
| Umbrella | Pointer ownership, integration verify | `nicki-contruction/01/executions/report-follow-up-01.yaml` |

## Required Workflow Changes

| # | Change | Status |
|---|--------|--------|
| 1 | JSON status: registry + per-task, hook resolution | **Done** |
| 2 | Close: full archive + whole worktree delete | **Done** (docs/skills); prove on real close |
| 3 | Readiness in `review-validations/*.yaml` | **Done** (01-0) |
| 4 | Fix loop append subtasks | **Done** (01-0) |
| 5 | User acceptance before commit | **Done** (01-0) |
| 6 | `publish-task` after merge | **Done** (01-1) |
| 7 | `projects/.../worktrees/...` paths | **Done** (01-1 scripts + docs) |
| 8 | Nicki invocation clarity | **Done** (`/nicki` command + docs) |
| 9 | CONTRIBUTING optional | **Done** (spec-maker) |
| 10 | Caveman default for workflow Markdown | **Done** |

## Final Assessment

Nicki credible as standalone multi-project orchestrator: disk routing triage → acceptance → commit → merge → publish → close. No new leaf agents beyond `publish-task`. Validate close teardown on first production close.
