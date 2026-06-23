---
name: hook-contract
description: "Hook contract for resolving Nicki task state from global-status.json and per-task status.json by task id. Use when writing Cursor hooks after Nicki knows task number."
disable-model-invocation: true
---

# Hook contract — task status resolution

Hooks run after Nicki knows **task id**. Resolve state with **JSON only** — no YAML parser.

## Resolution chain

```
task id → global-status.json → status_path → status.json → artifact paths
```

## Steps

1. Read `global-status.json` at workspace root.
2. Lookup `.tasks[<task_id>]`.
3. Read fields: `project`, `slug`, `worktree_path`, `status_path`.
4. Read per-task `status.json` at `status_path`.
5. Read `task.current_step`, `task.next_step`, `artifacts`, `open_questions`, `history`.

## jq examples

Registry route:

```bash
jq -r --arg id "$TASK_ID" '.tasks[$id].status_path' global-status.json
```

Full summary:

```bash
TASK_ID="42"
STATUS_PATH=$(jq -r --arg id "$TASK_ID" '.tasks[$id].status_path' global-status.json)
jq -r '.task | "\(.current_step) -> \(.next_step)"' "$STATUS_PATH"
```

Project + worktree:

```bash
jq -r --arg id "$TASK_ID" '.tasks[$id] | "\(.project) \(.worktree_path)"' global-status.json
```

## Rules

- Hooks **read only** — never write `global-status.json` during sheep steps.
- Task id must be explicit; do not infer from chat.
- Readiness: follow `artifacts.review_validation` pointer when routing after review.

## Workspace bootstrap injection

Cold-start context is **hook-owned** — Nicki does not read `nicki-workspace.yaml`.

| Hook | Event | Behavior |
|------|-------|----------|
| [`inject-nicki-bootstrap.sh`](../../hooks/inject-nicki-bootstrap.sh) | `sessionStart` | Returns `additional_context` with projects, backlog paths, backlog task rows, active tasks |
| Same script | `preToolUse` matcher `Task` | When `tool_input.subagent_type` is `nicki`, prepends bootstrap to Task `prompt` via `updated_input` |

Bootstrap reads (hook process only):

1. `nicki-workspace.yaml` (fallback `nicki-workspace.example.yaml`) — project name → path
2. `global-status.json` if present — `active_task` and registry entries
3. Per-project `docs/TASKS.md` or `docs/tasks.md` (nicki) — compact phase/task table rows

Task-id resolution chain below is unchanged; bootstrap is **additive** for vague start requests.

## Example script

See `.cursor/hooks/examples/resolve-task-status.sh`.

## Agent tool permissions

| File | Role |
|------|------|
| `.cursor/hooks/agent-permissions.json` | Canonical allowlist per agent |
| `.cursor/hooks/enforce-agent-tools.sh` | `preToolUse` hook — reads permissions, denies disallowed tools |
| `.cursor/hooks/inject-nicki-bootstrap.sh` | `sessionStart` + `preToolUse` Task→nicki — workspace bootstrap injection |
| `.cursor/hooks.json` | Registers hooks |

Agent identity from `subagent_type` then `agent_type` only — **not** task/description text (avoids false match on words like `nicki` in prompts). Unknown agent or unmapped tool → allow. Known agent + `false` permission → deny.

Smoke test: `.cursor/hooks/scripts/smoke-agent-tools.sh`
