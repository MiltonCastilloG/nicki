# Nicki

**Nicki is a good dog.**

Cursor workflow for structured agent-driven development. Nicki orchestrates the current-task pipeline (start → close) in project-local worktrees with YAML/Markdown handoffs on disk.

---

## What you get

| Component | Location | Role |
| --------- | -------- | ---- |
| Orchestrator | `.cursor/agents/nicki.md` + `.cursor/skills/nicki/routing.yaml` | Read-only conductor; routes from disk; sends sheep via Task in isolated context |
| Sheep | `.cursor/agents/sheep-*.md` | Workflow binding — load disk inputs, enforce gates, invoke skills (Nicki only) |
| Skills | `.cursor/skills/<name>/` | Pure functionality — how to perform one job; artifact schemas |
| Skill index | `.cursor/skills/README.md` | Skills vs agents rules and exceptions |

Ad-hoc work outside the pipeline: attach a skill (e.g. `spec-maker`, `execute-plan`, `conflict-resolution`) — no slash commands. Do not Task-spawn sheep from the parent agent.

### Three layers

```text
Nicki (.cursor/agents/nicki.md + routing.yaml)
  └─ sends sheep (child loads .cursor/agents/sheep-*.md)
       └─ loads current-task/* from disk
       └─ follows skill (.cursor/skills/<name>/SKILL.md)
       └─ returns compact YAML → Nicki → sheep-status
```

Leaf skills are **portable** — no `status.json`, no pipeline step names, no “spawn X next”. Sheep own auto-load paths and Nicki handoff expectations.

---

## Quick start

### 1. Clone and install

```bash
git clone <repo-url> nicki
cd nicki
python3 install.py
```

This writes a minimal `nicki-workspace.yaml` (nicki-only registry) and ensures `worktrees/` exists. Committed `.cursor/` agents, skills, rules, and hooks ship with the clone — no manual copying.

### Claude Code quick start

Use this path when working in Claude Code instead of Cursor:

```bash
git clone <repo-url> nicki
cd nicki
python3 install.py          # repository bootstrap (worktrees + registry)
python3 install-claude.py   # map .cursor/ runtime into Claude Code layout
```

Then open the cloned repository in Claude Code. The install script writes `.claude/agents/`, `.claude/skills/`, and root `CLAUDE.md` (opt-in Nicki routing). Generated Claude layout is gitignored — re-run `python3 install-claude.py` after pulling agent or skill updates.

Invoke Nicki by name:

```text
nicki start my-task
nicki continue
```

Claude Code does not replicate Cursor hooks; Nicki pipeline work uses the installed agents and skills only.

### 2. Open in Cursor

Open the cloned repository folder in Cursor.

### 3. Run with Nicki

Address Nicki by name:

```text
nicki start my-task
nicki continue
```

The parent agent Task-spawns the `nicki` subagent (see `.cursor/rules/nicki-default.mdc`). Nicki asks before each step and sends sheep (`sheep-start`, `sheep-describe`, `sheep-spec`, `sheep-execute`, …). After every sheep except close, Nicki sends `sheep-status` to update `current-task/status.json`.

Git steps (`sync`, `integrate`) need explicit confirmation. Archive and close need separate confirms. Close asks to confirm worktree delete only.

---

## Pipeline

```
start → describe → spec → subtasks → execute → review → [fix] → acceptance → sync → archive → sync → integrate → close
```

Post-review routing comes from validation YAML (`readiness.status`), not from review markdown:

| `readiness.status` | Next |
| ------------------ | ---- |
| `fix_required` | `execute` again (`## Fix` appended to subtasks by review) |
| `ready_for_acceptance` | Nicki `acceptance` checkpoint — sync blocked until user accepts |
| `blocked` | Nicki asks user |

Nicki-only steps: `acceptance`, `fix`. Validation (readiness + deferred next-steps) runs inside `sheep-review`.

`sheep-start` / `sheep-close` own `global-status.json`; `sheep-status` owns per-task `status.json`.

| Step | Sheep | Loads (typical) | Primary output |
| ---- | ----- | --------------- | -------------- |
| Setup | `sheep-start` | — (creates worktree + registry) | worktree + `global-status.json` entry |
| Describe | `sheep-describe` | status, `task.original` | `current-task/story.md` (Gherkin) |
| Spec | `sheep-spec` | status, story | `current-task/specs/<slug>.yaml` |
| Subtasks | `sheep-subtask` | status, spec | `current-task/subtasks/<slug>.md` |
| Execute | `sheep-execute` | status, subtasks, spec | code + `current-task/executions/<slug>.yaml` |
| Review | `sheep-review` | spec, subtasks, execution | `current-task/reviews/<slug>.yaml` + `current-task/review-validations/rN-validation.yaml` + optional `current-task/next-steps/*.yaml` |
| Sync / archive / integrate | `sheep-sync`, `sheep-archive`, `sheep-integrate` | status, review validation | `current-task/syncs/<slug>.yaml`, `docs/archive/<slug>/`, `current-task/integrates/<slug>.yaml` |
| Close | `sheep-close` | status, integrate handoff | worktree deleted; unregister `global-status.json` |

**Subtasks** map spec requirements to ordered one-line checklist items. Subtask-maker explores for existing coverage and prefers verify-before-build or refactor-to-share over default “build X” when the spec is already satisfied or logic can be reused.

---

## State on disk

```text
global-status.json                         # workspace root; sheep-start / sheep-close only
  tasks[<id>].status_path → current-task/status.json

worktrees/<path>/current-task/
  status.json                              # sheep-status only
  story.md
  specs/<slug>.yaml
  subtasks/<slug>.md
  executions/<slug>.yaml
  reviews/<slug>.yaml
  review-validations/rN-validation.yaml
  next-steps/*.yaml
  syncs/<slug>.yaml
  integrates/<slug>.yaml
```

Writer schemas: `.cursor/skills/current-task-update/status-format.md`, `global-status-format.md`. Nicki and readers use slim `status-read.md` / `global-status-read.md`.

---

## Layout

```text
nicki/
├── README.md
├── docs/
│   ├── NICKI.md              # workflow semantics (rebuild guide)
│   ├── WORKFLOW-DIAGRAMS.md  # mermaid pipeline maps
│   ├── complexity.md         # agent load analysis
│   ├── PLAN.md               # multi-project workspace plan
│   ├── tasks.md              # actionable backlog
│   └── archive/<slug>/       # closed task archives
└── .cursor/
    ├── agents/               # nicki + sheep workflow binding
    ├── rules/
    ├── hooks/
    └── skills/               # pure functionality + README.md
```

Design rationale: [`docs/NICKI.md`](docs/NICKI.md). Diagrams: [`docs/WORKFLOW-DIAGRAMS.md`](docs/WORKFLOW-DIAGRAMS.md). Multi-project workspace: [`docs/PLAN.md`](docs/PLAN.md). Backlog: [`docs/tasks.md`](docs/tasks.md).
