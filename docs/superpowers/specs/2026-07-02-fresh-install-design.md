# Fresh install design — Nicki repo clone bootstrap

**Status:** approved (2026-07-02)  
**Backlog:** [`tasks.md`](../../tasks.md) P0 **#19**  
**Implementation:** `install.py` at repo root (not yet built)

---

## Purpose

Post-clone bootstrap for the **Nicki repository itself** — the main project a user clones from GitHub. After `git clone` + `python3 install.py`, the repo is ready to run `nicki start …` in Cursor without manual file copying.

This is the **simplest P0 install path**. A separate **project install** (runtime into managed repos under a Nicki workspace) is **P1** and out of scope here.

---

## Success criteria

1. `git clone … && cd nicki && python3 install.py` exits `0` when `git` and `python3` are available.
2. `nicki-workspace.yaml` exists with a **nicki-only** registry (no managed project clones).
3. `worktrees/` exists (created if missing).
4. Re-run is safe: existing `nicki-workspace.yaml` is never overwritten.
5. Missing `git` → exit non-zero **before** any filesystem writes.
6. README documents: clone → `python3 install.py` → open in Cursor → `nicki …`.

---

## Locked decisions

| Topic | Decision |
|-------|----------|
| Install target | Nicki repo clone (not foreign app repos) |
| Host config | Nicki-owned files only — no merge into user host settings |
| Script | `install.py` at repo root (stdlib Python, matches other Nicki scripts) |
| Registry | Write minimal `nicki-workspace.yaml` with only `projects.nicki` |
| Existing yaml | Skip with notice — never overwrite |
| Prerequisites | Check `git` first; `python3` implied by invocation; hard-fail if `git` missing |
| `worktrees/` | `mkdir -p` if missing |
| `global-status.json` | Not created at install — first `sheep-start` / `create-worktree.py` |
| `.cursor/` runtime | Committed today; no install action until **#20** (`nicki-workflow/` symlinks) |
| Claude | Separate `install-claude.py` (P0 #21–#23) — not this script |
| Project install | P1 — install runtime into managed projects |

---

## Out of scope

- `install-claude.py` / `install-cursor.py` host adapters (**#23**)
- `nicki-workflow/` extract and symlink layout (**#20**)
- `global-status.json` scaffold
- `nicki-workspace.yaml` managed projects (tetris, landing, …)
- Version pin / `doctor` (**#28**)
- Permissions or hooks merge (repo owns all committed config)
- PyYAML dependency (stub yaml is a constant string)

---

## Fresh-install checklist (audit output for #19)

### Prerequisites

Checked **first**, before any writes.

| Tool | Check | On failure |
|------|-------|------------|
| `python3` | Script invocation | N/A (cannot run without it) |
| `git` | `shutil.which("git")` and `git --version` | Print error, exit `1` |

On success, print detected versions.

### Files and directories

| Path | Install action | Notes |
|------|----------------|-------|
| `nicki-workspace.yaml` | Write nicki-only stub if absent | Skip + notice if exists |
| `worktrees/` | `mkdir -p` | Touch `worktrees/.gitkeep` only when dir was created |
| `.gitignore` | None | Already committed |
| `.cursor/` | None | Committed; symlink hook added post-**#20** |
| `global-status.json` | None | Created on first task start |

### Present after clone (documented, not installed)

These ship in the repo; install does not copy or merge them:

| Component | Location |
|-----------|----------|
| Agents | `.cursor/agents/` |
| Skills + routing | `.cursor/skills/`, `.cursor/skills/nicki/routing.yaml` |
| Invocation rule | `.cursor/rules/nicki-default.mdc` |
| Permissions | `.cursor/permissions.json` |
| Hooks | `.cursor/hooks.json`, `.cursor/hooks/agent-permissions.json`, `.cursor/hooks/enforce-agent-tools.sh` |
| Gate scripts | `.cursor/skills/nicki/scripts/check-gate.py`, `gates.py`, `gate_utils.py` |
| Worktree scripts | `.cursor/skills/start-task/scripts/create-worktree.py`, `register-global-status.py` |

### `nicki-workspace.yaml` stub content

Not a copy of `nicki-workspace.example.yaml` (which lists managed projects). Install writes:

```yaml
version: 1

projects:
  nicki:
    path: .
    git:
      default_branch: main
      remote: origin
    copy: []
    post_create: []
```

User adds managed projects later via P1 project install or manual edit.

### Post-install user steps

1. Open the repo in Cursor.
2. Invoke Nicki: `nicki start my-task` or `nicki continue`.

---

## `install.py` behavior

```
install.py
├── prereq_check()      → git available; print versions
├── ensure_worktrees()  → mkdir -p worktrees/; .gitkeep if new
├── write_registry()    → nicki-workspace.yaml if absent; else skip + notice
├── print_success()     → next steps
└── main()              → run in order; no CLI flags in v1
```

### Properties

- **Stdlib only** — `pathlib`, `shutil`, `subprocess`, `sys`
- **Idempotent** — safe to re-run
- **Repo root** — resolve paths relative to `install.py` parent directory
- **No network, no sudo**
- **Exit codes:** `0` success; `1` prerequisite or unexpected error

### Future hook (#20)

When `nicki-workflow/` exists, add `link_cursor_runtime()`:

- Symlink `nicki-workflow/agents` → `.cursor/agents` (and skills, etc.)
- No-op until extract lands

Callable from `install.py` so one entrypoint remains after #20.

---

## Documentation updates (with implementation)

| Doc | Change |
|-----|--------|
| `README.md` | Replace `cp -r .cursor` quick start with `git clone` + `python3 install.py` |
| `docs/tasks.md` #19 | Mark audit complete; link this spec |
| `nicki-workspace.example.yaml` | Keep as multi-project reference; install does not copy it |

---

## P1 follow-up (not this spec)

- **Project install script** — install Nicki runtime into managed repos (`projects/<name>/`)
- **Workspace init** — full registry, clone/register flows (PLAN.md CLI)
- **Claude bootstrap** — `install-claude.py` + adapter files

---

## Brainstorm decision log

| Question | Answer |
|----------|--------|
| Install profile | Single-repo; Nicki repo is clone target; P1 for other projects |
| Host config merge | Nicki-owned files only |
| Post-clone script role | Minimal local setup (B) |
| Registry content | Nicki-only stub (B); no managed projects |
| Existing yaml | Skip with notice (B) |
| Missing prerequisites | Hard-fail; check git first (A) |
| Missing `worktrees/` | Create if missing (A) |
| Script format | `install.py` (approved over `install.sh`) |
