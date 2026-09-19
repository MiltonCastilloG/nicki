# Nicki

**Nicki is a good dog.**

Workflow for Cursor and Claude Code. Nicki orchestrates the current-task pipeline (start → close) in project-local worktrees with YAML/Markdown handoffs on disk.

---

## What you get

| Component | Location | Role |
| --------- | -------- | ---- |
| Orchestrator | `workflow-runtime/agents/nicki.md` + `workflow-runtime/skills/nicki/routing.json` | Read-only conductor; routes from disk; sends sheep via Task in isolated context |
| Sheep | `workflow-runtime/agents/sheep-*.md` | Workflow binding — load disk inputs, invoke skills (Nicki on the pipeline; direct spawn for ad-hoc) |
| Skills | `workflow-runtime/skills/<name>/` | Pure functionality — how to perform one job; artifact schemas |
| Skill index | `workflow-runtime/skills/README.md` | Skills vs agents rules and exceptions |

Ad-hoc work outside the pipeline: Task-spawn the sheep directly with instructions and an output path (default `docs/adhoc/`), or attach the skill (e.g. `spec-maker`, `execute-plan`, `conflict-resolution`) to do the work inline. No task, worktree, or status write is involved. `sheep-start`, `sheep-close`, and `sheep-status` stay Nicki-only.

### Three layers

```text
Nicki (workflow-runtime/agents/nicki.md + routing.json)
  └─ sends sheep (child loads workflow-runtime/agents/sheep-*.md)
       └─ loads current-task/* from disk
       └─ follows skill (workflow-runtime/skills/<name>/SKILL.md)
       └─ returns compact YAML → Nicki → sheep-status
```

Leaf skills are **portable** — no `status.json`, no pipeline step names, no “spawn X next”. Sheep own auto-load paths and Nicki handoff expectations.

### Harness scripts (read / write)

Orchestration edges are invoke-and-exit Python — not a per-step schema validator:

| Type | Script | Role |
| ---- | ------ | ---- |
| Read | `workflow-runtime/skills/nicki/scripts/bootstrap-context.py` | Position, next step, intended sheep |
| Write | `workflow-runtime/skills/current-task-update/scripts/update-status.py` | Sole writer for `current-task/status.json` |

Missing required write fields → `written: false` + `errors[]` (retry JSON); not a harness crash. Spawn gate retired: [`docs/archive/retire-check-gate/report.md`](docs/archive/retire-check-gate/report.md).

---

## Quick start

### 1. Clone and install

```bash
git clone <repo-url> nicki
cd nicki
python3 install.py
```

This writes a minimal `nicki-workspace.yaml` (nicki-only registry), ensures `worktrees/` exists, and verifies committed `.cursor/agents` and `.cursor/skills` symlinks into `workflow-runtime/`. For multi-project workspaces, managed clones live under `projects/<name>/` (see [`docs/PLAN.md`](docs/PLAN.md)). How to edit the runtime: [Editing the runtime](#editing-the-runtime).

### Claude Code quick start

```bash
git clone <repo-url> nicki
cd nicki
python3 install.py
python3 install-claude.py
```

Open the cloned repository in Claude Code. Claude Code does not replicate Cursor hooks; pipeline work uses the installed agents and skills only. How to edit the runtime (both hosts): [Editing the runtime](#editing-the-runtime).

### 2. Open in Cursor

Open the cloned repository folder in Cursor.

### 3. Run with Nicki

Address Nicki by name:

```text
nicki start my-task
nicki continue
```

The parent agent Task-spawns the `nicki` subagent (see `.cursor/rules/nicki-default.mdc`, generated from `workflow-runtime/rules/nicki-default.md`). Nicki asks before execute and sync and sends sheep (`sheep-start`, `sheep-spec`, `sheep-gherkin`, `sheep-execute`, …). After every sheep except start and close, Nicki sends `sheep-status` to update `current-task/status.json`.

Git steps (`sync`, `integrate`) need explicit confirmation. Archive and close need separate confirms. Close asks to confirm worktree delete only.

---

## Editing the runtime

One real copy; both hosts read it through shortcuts.

```text
workflow-runtime/agents/   ← edit here
workflow-runtime/skills/   ← edit here
workflow-runtime/rules/    ← edit here

.cursor/agents, .cursor/skills   → symlinks (committed)
.claude/agents, .claude/skills   → symlinks (install-claude.py)
```

Agent and skill edits are visible to Cursor and Claude the moment you save. No reinstall.

**One special case — the invocation rule.** Cursor and Claude need it as two
different files, so they are generated, not linked:

```text
workflow-runtime/rules/nicki-default.md
  → python3 install.py          writes .cursor/rules/nicki-default.mdc (committed)
  → python3 install-claude.py   writes CLAUDE.md (gitignored)
```

After editing the rule, run both and commit the refreshed `.mdc`. If you forget,
`python3 test.py` fails on `rule_drift`.

**Never edit through `.cursor/` or `.claude/`.** Some editors save by
write-temp-then-rename, which turns a symlink into a real folder. If a link
breaks, re-run the matching installer; it self-repairs. CI runs both installers
and the smokes on every push.

---

## Pipeline

```
start → spec → gherkin → subtasks → execute → review → [fix] → acceptance → sync → archive → sync → integrate → close
```

Post-review routing comes from the review sheep's return `summary`, not from a file on disk:

| Verdict | Next |
| ------- | ---- |
| fixes required | Nicki asks approval of the suggested fix lines → `sheep-subtask` appends `## Fix` → `execute` again |
| ready | Nicki `acceptance` checkpoint — sync blocked until user accepts |
| blocked | Nicki asks user |

Nicki-only steps: `acceptance`, `fix`.

`sheep-start` / `sheep-close` own `global-status.json`; `sheep-status` owns per-task `status.json`.

| Step | Sheep | Loads (typical) | Primary output |
| ---- | ----- | --------------- | -------------- |
| Setup | `sheep-start` | — (creates worktree + registry) | worktree + `global-status.json` entry |
| Spec | `sheep-spec` | status, free text / `task.original` | `current-task/specs/<slug>.json` |
| Gherkin | `sheep-gherkin` | spec path | `current-task/story.md` (Gherkin checklist) |
| Subtasks | `sheep-subtask` | status, spec | `current-task/subtasks/<slug>.md` |
| Execute | `sheep-execute` | status, subtasks, spec (optional) | code changes in worktree (no execution JSON) |
| Review | `sheep-review` | worktree diff + available current-task files | no file — verdict in the return `summary` |
| Sync / archive / integrate | `sheep-sync`, `sheep-archive`, `sheep-integrate` | status, worktree | git side effects; `docs/archive/<slug>/` from archive only |
| Close | `sheep-close` | status | worktree deleted; unregister `global-status.json` |

**Subtasks** map spec requirements to ordered one-line checklist items. Subtask-maker explores for existing coverage and prefers verify-before-build or refactor-to-share over default “build X” when the spec is already satisfied or logic can be reused.

---

## State on disk

```text
global-status.json                         # workspace root; sheep-start / sheep-close only
  tasks[<id>].status_path → current-task/status.json

worktrees/<path>/current-task/
  status.json                              # sheep-status only
  story.md
  specs/<slug>.json
  subtasks/<slug>.md
```

Operational steps write no handoff files. Position plus these document artifacts is the whole record.

Writer schemas: `workflow-runtime/skills/current-task-update/status-format.md`, `global-status-format.md`. Nicki and readers use slim `status-read.md` / `global-status-read.md`.

---

## Layout

```text
nicki/
├── README.md
├── install.py / install-claude.py / install_common.py
├── workflow-runtime/          # canonical host-neutral runtime
│   ├── agents/                # nicki + sheep (flat)
│   ├── skills/                # pure functionality + README.md
│   └── rules/                 # nicki-default.md (no host frontmatter)
├── docs/
│   ├── NICKI.md
│   ├── WORKFLOW-DIAGRAMS.md
│   ├── PLAN.md
│   ├── tasks/                 # backlog + designs
│   └── archive/<slug>/
├── .cursor/                   # Cursor host adapter
│   ├── agents -> ../workflow-runtime/agents
│   ├── skills -> ../workflow-runtime/skills
│   ├── rules/                 # committed nicki-default.mdc (from canonical rule)
│   ├── hooks/
│   └── permissions.json
└── .claude/                   # Claude host adapter (generated, gitignored)
    ├── agents -> ../workflow-runtime/agents
    └── skills -> ../workflow-runtime/skills
```

Design rationale: [`docs/NICKI.md`](docs/NICKI.md). Diagrams: [`docs/WORKFLOW-DIAGRAMS.md`](docs/WORKFLOW-DIAGRAMS.md). Multi-project workspace: [`docs/PLAN.md`](docs/PLAN.md). Backlog: [`docs/tasks/tasks.md`](docs/tasks/tasks.md).
