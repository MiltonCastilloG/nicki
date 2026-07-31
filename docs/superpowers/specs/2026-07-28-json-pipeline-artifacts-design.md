# Design: JSON-native pipeline artifacts

Date: 2026-07-28  
Status: implemented in `.cursor/` (`.claude/` sync is automatic / out of scope here)

## Problem

Sheep hand-author YAML with prose scalars. Unquoted `: ` crashes `yaml.safe_load`. Gates had no parse error handling, so a content bug became a harness failure → `sheep-fallback` (record-only) → extra recovery round-trip.

## Goal

Reliability first, operator ease second. Same schemas and pipeline — change only the serialization format. No backfill migration of existing worktrees.

## Decision

**Option A — JSON everywhere for machine-structured pipeline files.**

| Surface | Format |
|---------|--------|
| Specs, executions, reviews, review guidance, validations, next-steps, sync/integrate handoffs, archive reports, errors | `.json` |
| Sheep return contract → `update-status.py` | JSON |
| `routing.yaml` | `routing.json` |
| Story (`story.md`), subtask checklist (`subtasks/*.md`) | markdown (unchanged) |
| `status.json`, `global-status.json` | JSON (unchanged) |
| `nicki-workspace.yaml` | YAML (workspace registry; not sheep-authored prose) |

> **Later:** execute no longer writes `executions/*.json` — see [`2026-07-30-informal-jump-and-drop-execution-design.md`](2026-07-30-informal-jump-and-drop-execution-design.md).

## Non-goals

- Do not expand `sheep-fallback` to fix artifacts.
- Do not migrate existing on-disk `.yaml` task files.
- Do not change field schemas — translate examples and paths only.
- Do not touch `.claude/` in this change set (automatic mirror).

## Compatibility

`status.json` artifact pointers already store the full relative path including extension. Readers use suffix-aware `load_artifact()`:

- `.json` → `json.loads`
- `.yaml` / `.yml` → `yaml.safe_load` (in-flight tasks only)
- Parse failures → clean gate `deny(...)`, not traceback

New writers emit `.json` only.

## Components changed

### Harness scripts

- `gate_utils.py` — `load_artifact`, `load_routing`, `ArtifactParseError`; `ROUTING_PATH` → `routing.json`
- `gates.py` — parse errors become denies on subtasks/review/archive
- `check-gate.py` — top-level exception → contract-shaped deny JSON
- `bootstrap-context.py` — reads `routing.json`
- `validate-harness-stdout.py` — reads `routing.json` via `load_routing`
- `update-status.py` — primary `--json-path`; optional deprecated `--yaml-path`
- `append-error.py` — writes `current-task/specs/errors.json`
- `smoke-archive-gate.py` — JSON sync fixtures

### Config / docs / agents

- `routing.yaml` removed; `routing.json` added (same structure, JSON paths)
- Format docs, SKILL.md files, sheep agents, `nicki.md` — paths and examples → JSON
- Live docs: `README.md`, `docs/NICKI.md`, `docs/WORKFLOW-DIAGRAMS.md`

### Tests

- Smoke tests updated for JSON paths and summary input

## Error handling

1. Malformed task artifact at a gate → `allowed: false` with parse reason (not harness failure).
2. Malformed sheep summary → `update-status.py` `written: false` + `errors[]` (retry status, not fallback).
3. Unexpected gate crash → still prints deny JSON so Nicki can treat as harness failure only when contract is broken.

## Success criteria

- `python3 test.py` passes.
- New sheep writes never use `.yaml` for task artifacts or return contract.
- Colon-containing prose in notes/acceptance cannot break the gate via YAML plain-scalar rules.

## Out of scope follow-ups (optional)

- Remove YAML back-compat from `load_artifact` once no in-flight YAML worktrees remain.
- Drop deprecated `--yaml-path` on `update-status.py`.
- JSON Schema validation of artifact shapes (typed guarantees — not required for this fix).
