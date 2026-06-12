# Nicki

**Nicki is a good dog.**

Cursor workflow for structured agent-driven development. Nicki orchestrates the current-task pipeline (describe → close) in project-local worktrees with YAML/Markdown handoffs.

---

## What you get

| Component | Location | Role |
| --------- | -------- | ---- |
| Orchestrator | `.cursor/agents/nicki.md` | Read-only conductor; Task-spawns leaf subagents; owns pipeline and gates |
| Leaf subagents | `.cursor/agents/<step>.md` | Workflow binding — load disk inputs, enforce gates, invoke skills |
| Skills | `.cursor/skills/<name>/` | Pure functionality — how to perform one job; artifact schemas |
| Skill index | `.cursor/skills/README.md` | Skills vs agents rules and exceptions |

Ad-hoc work outside the pipeline: attach a skill (e.g. `conflict-resolution`, `caveman`) — no slash commands.

### Three layers

```text
Nicki (.cursor/agents/nicki.md)
  └─ Task-spawns agent (.cursor/agents/<leaf>.md)
       └─ loads current-task/* from disk
       └─ follows skill (.cursor/skills/<name>/SKILL.md)
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
task-archive/
global-status.json
```

### 2. Run with Nicki

Open the project in Cursor. Address Nicki by name:

```text
nicki hero-section
nicki continue
```

Parent agent Task-spawns the `nicki` subagent (see `.cursor/rules/nicki-default.mdc`). Nicki asks before each leaf step and Task-spawns workers (`start-task`, `spec-maker`, `execute-plan`, …).

Git steps (commit, push, merge, publish) need explicit confirmation. Close asks: *Time for the feedback woof! Want?*

---

## Pipeline

```
start → describe → spec → subtasks → execute → review → triage → [fix] → acceptance → commit → push → merge → publish → close
```

Nicki Task-spawns `current-task-update` after each leaf step except close. `start-task` / `close-task` own `global-status.json`; `current-task-update` owns per-task `status.json`.

| Step | Subagent | Agent loads (typical) | Primary output |
| ---- | -------- | --------------------- | -------------- |
| Setup | `start-task` | — (creates worktree + registry) | worktree + `global-status.json` entry |
| Describe | Nicki only | `status.json` | `current-task/story.md` |
| Spec | `spec-maker` | status, story | `current-task/specs/<slug>.yaml` |
| Subtasks | `subtask-maker` | status, spec | `current-task/subtasks/<slug>.md` |
| Execute | `execute-plan` | status, subtasks, spec | code + `current-task/executions/<slug>.yaml` |
| Review | `review-execution` | spec, subtasks, execution, optional guidance | `current-task/reviews/<slug>.yaml` |
| Triage | `review-triage` | review, spec, subtasks, execution, status | `current-task/review-validations/rN-validation.yaml` |
| Commit / push / merge / publish | git leaf agents | prior handoffs + status | handoffs under `current-task/` |
| Close | `close-task` | status, merge/publish handoffs | `task-archive/<slug>/` |

---

## State on disk

```text
global-status.json                    # workspace root; start-task / close-task only
  tasks[<id>].status_path → current-task/status.json
    artifacts.* → YAML/Markdown handoffs under current-task/
```

Authoritative schemas: `.cursor/skills/current-task-update/status-format.md`, `global-status-format.md`.

---

## Layout

```text
nicki/
├── README.md
├── NICKI.md
├── PLAN.md
└── .cursor/
    ├── agents/          # workflow binding per leaf step
    ├── rules/
    └── skills/          # pure functionality + README.md
```

Design rationale: [`NICKI.md`](NICKI.md). Multi-project workspace: [`PLAN.md`](PLAN.md). Skills/agents audit: [`report-2.md`](report-2.md).
