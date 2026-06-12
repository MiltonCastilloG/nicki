# Nicki skills

Skills are **pure functionality** — portable operation manuals with no knowledge of the Nicki pipeline.

| Layer | Owns |
|-------|------|
| **Skill** (`SKILL.md` + `*-format.md`) | How to perform one job: algorithms, schemas, safety, default output shape |
| **Agent** (`.cursor/agents/<name>.md`) | Workflow binding: disk paths to load, gates, handoffs, status/registry updates |
| **Nicki** (`.cursor/agents/nicki.md`) | Full pipeline, transitions, user confirmations |

## Rules

1. Leaf skills do **not** reference `status.json`, `global-status.json`, pipeline step names, or “spawn X next”.
2. Leaf skills accept **inputs from the agent prompt** (paths, inline YAML, story text) — no implicit disk discovery.
3. Format files document **one artifact type** each — no multi-agent directory maps.
4. Agents load skills and pass concrete inputs; agents own auto-load paths and Nicki summary expectations.

## Exceptions (workflow skills)

These skills intentionally own task/workflow state or lifecycle:

- `current-task-update/` — per-task `status.json`
- `start-task/` skill — worktree creation; **agent** calls `register-global-status.sh` (registry write)
- `close-task/`, `close-scope/`, `task-archive/` — archive, unregister, teardown
- `hook-contract/` — resolve task id → status for hooks

## Shared utilities

- `caveman/` — markdown voice (not workflow)
- `conflict-resolution/` — merge conflict protocol (used by push-task and merge-task agents)
- `next-step-spec/` — follow-up spec shape (used by review-triage)
