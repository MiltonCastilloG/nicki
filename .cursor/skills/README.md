# Nicki skills

Skills are **pure functionality** — portable operation manuals with no knowledge of the Nicki pipeline.

| Layer | Owns | Who uses it |
|-------|------|-------------|
| **Skill** (`SKILL.md` + `*-format.md`) | How to perform one job: algorithms, schemas, safety, default output shape | **Users** attach or invoke skills for ad-hoc work |
| **Sheep** (`.cursor/agents/sheep-*.md`) | Workflow binding: disk paths to load, gates, handoffs | **Nicki only** — Task `subagent_type: sheep-*` |
| **Nicki** (`.cursor/agents/nicki.md`) | Full pipeline, transitions, user confirmations | User says `nicki …` |

Pipeline leaf skills: `story-maker`, `spec-maker`, `subtask-maker`, `execute-plan`, `review-execution`, …

## Invocation policy

1. **Users use skills** — pipeline skills (`story-maker`, `spec-maker`, `execute-plan`, …) have model invocation enabled; attach the skill for one-off work outside the full pipeline.
2. **Users do not send sheep** — parent agent must not Task-spawn `sheep-*`; only Nicki sends sheep.
3. **Nicki sends sheep** — full current-task workflow goes through Nicki (`nicki fetch`, `nicki continue`, …).
4. **Workflow-only skills stay internal** — `current-task-update`, `close-task`, `close-scope`, `task-archive`, `hook-contract`, `validation` keep `disable-model-invocation: true`.

## Rules

1. Leaf skills do **not** reference `status.json`, `global-status.json`, pipeline step names, or “send sheep next”.
2. Leaf skills accept **inputs from the sheep prompt** (paths, inline YAML, story text) — no implicit disk discovery.
3. Format files document **one artifact type** each — no multi-agent directory maps.
4. Sheep load skills and pass concrete inputs; sheep own auto-load paths and Nicki summary expectations.

## Exceptions (workflow skills)

These skills intentionally own task/workflow state or lifecycle:

- `current-task-update/` — per-task `status.json` (sheep: `sheep-status`)
- `start-task/` skill — worktree creation; **sheep-start** calls `register-global-status.sh` (registry write)
- `close-task/`, `close-scope/`, `task-archive/` — archive, unregister, teardown (sheep: `sheep-close`)
- `hook-contract/` — resolve task id → status for hooks

## Shared utilities

- `caveman/` — markdown voice (not workflow)
- `conflict-resolution/` — merge conflict protocol (used by sheep-sync and sheep-integrate)
- `validation/` — review → validation YAML, readiness, and next-steps (used by sheep-review)
