# Nicki

**Nicki is a good dog.**

Cursor workflow for structured agent-driven development. Nicki orchestrates the current-task pipeline (start → close) in project-local worktrees with YAML/Markdown handoffs on disk.

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

This writes a minimal `nicki-workspace.yaml` (nicki-only registry), ensures `worktrees/` exists, and verifies committed `.cursor/agents` and `.cursor/skills` symlinks into `workflow-runtime/`. For multi-project workspaces, managed clones live under `projects/<name>/` (see [`docs/PLAN.md`](docs/PLAN.md)). Canonical runtime ships under `workflow-runtime/`; Cursor adapters are committed symlinks plus a committed `.cursor/rules/nicki-default.mdc` (regenerated from the canonical rule when that file changes).

### Claude Code quick start

Use this path when working in Claude Code instead of Cursor:

```bash
git clone <repo-url> nicki
cd nicki
python3 install.py          # repository bootstrap + Cursor adapter
python3 install-claude.py   # symlink .claude/ agents+skills into workflow-runtime/; generate CLAUDE.md
```

Then open the cloned repository in Claude Code.

- **Edit runtime in `workflow-runtime/`** (agents, skills, rules). That tree is canonical and committed.
- **`.cursor/agents` and `.cursor/skills`** are committed directory symlinks into `workflow-runtime/` (Track 1). Fresh checkouts and new git worktrees get them with no extra step.
- **`.claude/agents` and `.claude/skills`** are directory symlinks into `workflow-runtime/` (created by `install-claude.py`).
- **`.cursor/rules/nicki-default.mdc`** is generated from `workflow-runtime/rules/nicki-default.md` and **committed** so fresh worktrees carry the invocation rule without `install.py`. Re-run `install.py` after editing the canonical rule, then commit the refreshed `.mdc`.
- **`CLAUDE.md`** is generated the same way (with Claude vocabulary swaps) and remains gitignored.
- **Re-run installers** on a fresh clone (Claude), or after changing the invocation rule (regenerates host rule files). Agent/skill edits need no reinstall when using symlinks.
- **Atomic-save warning:** some editors save via write-temp-then-rename and can replace a symlink with a regular file or directory. Always edit under `workflow-runtime/`, never through the `.cursor/` or `.claude/` symlink path. Re-run the matching installer to self-repair if a link is severed.

Generated Claude layout is gitignored. If the OS rejects directory symlinks, the installer falls back to copying and warns that re-runs are required after runtime edits.

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

The parent agent Task-spawns the `nicki` subagent (see `.cursor/rules/nicki-default.mdc`, generated from `workflow-runtime/rules/nicki-default.md`). Nicki asks before execute and sync and sends sheep (`sheep-start`, `sheep-spec`, `sheep-gherkin`, `sheep-execute`, …). After every sheep except start and close, Nicki sends `sheep-status` to update `current-task/status.json`.

Git steps (`sync`, `integrate`) need explicit confirmation. Archive and close need separate confirms. Close asks to confirm worktree delete only.

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
│   ├── OWNERSHIP.md
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

Design rationale: [`docs/NICKI.md`](docs/NICKI.md). Diagrams: [`docs/WORKFLOW-DIAGRAMS.md`](docs/WORKFLOW-DIAGRAMS.md). Multi-project workspace: [`docs/PLAN.md`](docs/PLAN.md). Backlog: [`docs/tasks/tasks.md`](docs/tasks/tasks.md). Ownership / fork map: [`docs/OWNERSHIP.md`](docs/OWNERSHIP.md).
