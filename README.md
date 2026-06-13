# Nicki

**Nicki is a good dog.**

Cursor workflow for structured agent-driven development. Nicki orchestrates the current-task pipeline (describe → close) in project-local worktrees with YAML/Markdown handoffs.

---

## What you get

| Component | Location | Role |
| --------- | -------- | ---- |
| Orchestrator | `.cursor/agents/nicki.md` + `.cursor/skills/nicki/routing.yaml` | Read-only conductor; routes from disk; sends sheep via Task in isolated context |
| Sheep | `.cursor/agents/sheep-*.md` | Workflow binding — load disk inputs, enforce gates, invoke skills (Nicki only) |
| Skills | `.cursor/skills/<name>/` | Pure functionality — how to perform one job; artifact schemas |
| Skill index | `.cursor/skills/README.md` | Skills vs agents rules and exceptions |

Ad-hoc work outside the pipeline: attach a skill (e.g. `conflict-resolution`, `caveman`) — no slash commands.

### Three layers

```text
Nicki (.cursor/agents/nicki.md + routing.yaml)
  └─ sends sheep (child loads .cursor/agents/sheep-*.md)
       └─ loads current-task/* from disk
       └─ follows skill (.cursor/skills/<name>/SKILL.md)
       └─ returns compact YAML → Nicki → sheep-status
```

Leaf skills are **portable** — no `status.json`, no pipeline step names, no “spawn X next”. Agents own auto-load paths and Nicki handoff expectations.

---

## Quick start

### 1. Install

```bash
cp -r /path/to/nicki/.cursor /path/to/your-project/.cursor
```

Add to `.gitignore`:

```gitignore
worktrees/
projects/*/worktrees/
global-status.json
```

### 2. Run with Nicki

Open the project in Cursor. Address Nicki by name:

```text
nicki hero-section
nicki continue
```

Parent agent Task-spawns the `nicki` subagent (see `.cursor/rules/nicki-default.mdc`). Nicki asks before each step and sends sheep (`sheep-start`, `sheep-spec`, `sheep-execute`, …). Ad-hoc work: attach skills directly — do not send sheep from the parent agent.

Git steps (`sync`, `integrate`) need explicit confirmation. Close asks to confirm archive and worktree delete.

---

## Pipeline

```
start → describe → spec → subtasks → execute → review → [fix] → acceptance → sync → integrate → close
```

Nicki sends `sheep-status` after each sheep except close. `sheep-start` / `sheep-close` own `global-status.json`; `sheep-status` owns per-task `status.json`.

| Step | Sheep | Loads (typical) | Primary output |
| ---- | ----- | --------------- | -------------- |
| Setup | `sheep-start` | — (creates worktree + registry) | worktree + `global-status.json` entry |
| Describe | Nicki only | `status.json` | `current-task/story.md` |
| Spec | `sheep-spec` | status, story | `current-task/specs/<slug>.yaml` |
| Subtasks | `sheep-subtask` | status, spec | `current-task/subtasks/<slug>.md` |
| Execute | `sheep-execute` | status, subtasks, spec | code + `current-task/executions/<slug>.yaml` |
| Review | `sheep-review` | spec, subtasks, execution, validation skill | `reviews/<slug>.yaml` + `review-validations/rN-validation.yaml` + optional `next-steps/*.yaml` |
| Sync / integrate | `sheep-sync`, `sheep-integrate` | status, review validation | `syncs/`, `integrates/` handoffs |
| Close | `sheep-close` | status, integrate handoff | `docs/archive/<slug>/` |

---

## State on disk

```text
global-status.json                    # workspace root; sheep-start / sheep-close only
  tasks[<id>].status_path → current-task/status.json
    artifacts.* → YAML/Markdown handoffs under current-task/
```

Authoritative schemas: `.cursor/skills/current-task-update/status-format.md`, `global-status-format.md`.

---

## Layout

```text
nicki/
├── README.md
├── docs/
│   ├── NICKI.md         # workflow semantics
│   ├── PLAN.md          # multi-project workspace plan
│   └── archive/         # closed task archives (00, 01, …)
└── .cursor/
    ├── agents/          # sheep workflow binding (Nicki only)
    ├── rules/
    └── skills/          # pure functionality + README.md
```

Design rationale: [`docs/NICKI.md`](docs/NICKI.md). Multi-project workspace: [`docs/PLAN.md`](docs/PLAN.md). Skills/agents audit: [`nicki-contruction/report-2.md`](nicki-contruction/report-2.md).
