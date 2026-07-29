# Nicki — completed tasks

Shipped work moved out of [`tasks.md`](tasks.md) to keep the backlog lean. Task archives: [`archive/`](archive/).

---

## P1 — Workflow correct functioning (done)

| # | Task | Notes |
|---|------|-------|
| 1 | `create-worktree.py` | Pull base branch, `git worktree add`, workspace `worktrees/<project>-<slug>`, copy gitignored locals from registry, `post_create`, scaffold `current-task/`, register `global-status.json`. Archive: [`archive/nicki/04/`](archive/nicki/04/). |
| 2 | Root `worktrees/` layout | Shipped with #1. **Unified:** `worktrees/<project>-<slug>` at workspace root (single hyphen). See `create-worktree.py` and `nicki-workspace.example.yaml`. |
| 3 | `post_create` copy list | Shipped with #1. Per-project `copy` and `post_create` in workspace registry; readable by `create-worktree.py`. |
| 4 | Migrate active task | `tetris-clone-frp` active at `worktrees/tetris-clone-frp-ghost-piece-rendering`; `global-status.json` and `status.json` use unified paths. No legacy `projects/tetris-clone-frp/worktrees/`. Archive: [`archive/ghost-piece-rendering/`](archive/ghost-piece-rendering/). |
| 5 | Wire `sheep-start` to new script | `sheep-start.md` invokes `create-worktree.py` per `start-task/SKILL.md`; legacy `start-worktrees.sh` retired from agent path. Archive: [`archive/wire-sheep-start/`](archive/wire-sheep-start/). |
| 6 | **Gherkin + spec mutual understanding** | Archive: [`archive/gherkin-spec-mutual-understanding/`](archive/gherkin-spec-mutual-understanding/). See below. |
| 15 | `nicki.code-workspace` sync | `scripts/generate-code-workspace.sh` wired into `create-worktree.py` (start) and `close-scope` (close). Warn on regen failure; skip on `--dry-run`. Archive: [`archive/code-workspace-sync/`](archive/code-workspace-sync/). |
| 16 | **Context handling** | Disk-first bootstrap in `nicki.md` + `nicki-default.mdc`. Archive: [`archive/context-handling/`](archive/context-handling/). |
| 18 | **`bootstrap-context.py`** | Script sibling to `check-gate.py`; Nicki reads orchestration context from stdout. Archive: [`archive/bootstrap-script/`](archive/bootstrap-script/) — merge `55dca0a`. |
| | **status.json YAGNI (v2)** | Simplify per-task status to task-status.v2: step pointers + `artifacts.*`, no verbose history. Originally shipped with `task.completed_steps`; that list was **removed 2026-07-29** (position is `current_step`/`next_step` only — see [`flexibility.md`](flexibility.md)). Archive: [`archive/status-json-yagni/`](archive/status-json-yagni/). |

Projects on disk: `castlemill-landing`, `project-psychic-lemon`, `tetris-clone-frp` (one active worktree). Gitignored env is copied by script — not a layout problem.

Worktree path rule: always `worktrees/<project>-<slug>` — e.g. `worktrees/nicki-create-worktree-py`, `worktrees/tetris-clone-frp-hero-section`. Never double hyphen.

Scripts: `.cursor/skills/start-task/scripts/create-worktree.py`, `register-global-status.py`, `WORKFLOW.md` (manual recovery).

### Gherkin + spec mutual understanding (#6)

**Goal:** Nicki and sheep do not advance past `describe` / `spec` until user and agent share the same understanding — not just formatted output.

| Step | Who | Behavior |
|------|-----|----------|
| `describe` | **sheep-describe** + **story-maker** | Ask before draft; do not invent specifics. Draft in relay until user approves. Write `story.md` only when clear and approved. |
| `describe` relay | **Nicki** | Relay blocked `open_questions` or draft `summary`; re-send sheep-describe with user context. Pause when user is silent. |
| `spec` | **sheep-spec** + **spec-maker** | Block without write when vague or forked; `open_questions` for Nicki relay. No spec file until resolved. |
| `spec` relay | **Nicki** | Present `open_questions`; re-send sheep-spec after user answers. No subtasks while spec `open_questions` non-empty. |
| Gate | **Harness** | `routing.yaml` / `check-gate.py`: block `spec` without `artifacts.story`; block `subtasks` while spec `open_questions` non-empty. |

**Shipped:** `story-maker/SKILL.md`, `sheep-describe.md`, `nicki.md` (Describe + Spec relay), `sheep-spec.md`, `spec-maker/SKILL.md`, `routing.yaml` (describe → `sheep-describe`).

### status.json YAGNI (v2)

**Goal:** Per-task `status.json` holds only fields Nicki and sheep read — step pointers, artifact paths, `open_questions` — without verbose history or duplicate gates.

| Area | Shipped |
|------|---------|
| Schema | `task-status.v2` — originally included `task.completed_steps`; **removed 2026-07-29**. Now `current_step`/`next_step` + `artifacts.*` pointers, lean `meta` |
| Writers | `current-task-update` emits v2 only; `create-worktree.py` scaffolds v2 example |
| Readers | `status-read.md`, `routing.yaml`, `nicki.md`, sheep disk-inputs use `artifacts.story` |
| Archive | `task-archive` sources process from artifact handoffs, not status history |

---

## P2 — Harness and guardrails (done)

| # | Task | Notes |
|---|------|-------|
| 7 | `check-gate.py` | `.cursor/skills/nicki/scripts/check-gate.py` — `status.json` + `routing.yaml` (+ validation/spec when needed). Stdout: `allowed`, `sheep`, `reason`, `user_confirm`. All steps; git tail first. Archive: [`archive/check-gate-py/`](archive/check-gate-py/). |
| 8 | Nicki **calls** gate script | Nicki runs gate before spawn; on fail shows `reason`, does not spawn. Archive: [`archive/nicki-gate-wiring/`](archive/nicki-gate-wiring/) — merge `0f57668`. |
| 11 | Permissions | `.cursor/permissions.json` allows `check-gate.py`, `create-worktree.py`, `bootstrap-context.py`. |
| | **`update-status.py`** | Authoritative write for `current-task/status.json` via `sheep-status`. Required summary field: `next_step` only; always writes `task.current_step`; `written: false` = input error (retry), not harness failure. Per-step `validate-sheep-return.py` deleted — see [harness ADR](superpowers/specs/2026-07-17-harness-read-write-types-design.md). |

| | **sheep-fallback** | Failure recording + harness-failure routing. Archive: [`archive/sheep-fallback/`](archive/sheep-fallback/). |

---

## P3 — Trimming (done)

| # | Task | Notes |
|---|------|-------|
| 12 | Trim `nicki.md` | Dropped numbered workflow, readiness table, sheep map, duplicated gate prose; kept Bootstrap, Transitions (`check-gate.py`), Describe/Spec relay, harness failure. ~168→117 lines. Brief: [`harness-alignment-subagents.md`](harness-alignment-subagents.md) step 4. |
| 14 | Shorten `NICKI.md` | Shell allowlist for bootstrap/gate; harness read/gate/write table + ADR link; session vs disk bootstrap chain; cut duplicated readiness/transition prose. |

---

## Host runtime (done)

| # | Task | Notes |
|---|------|-------|
| 19 | Fresh-install `install.py` | Post-clone registry + `worktrees/` bootstrap; `.cursor/` untouched (Cursor link hook deferred to #20). Archive: [`archive/fresh-install/`](archive/fresh-install/). |
| | **Claude adapter (copy model)** | `install-claude.py` maps `.cursor/` → `.claude/` via copy; generates `CLAUDE.md`. Superseded by Approach A symlink. Archive: [`archive/claude-adapter/`](archive/claude-adapter/). |
| | **Approach A: host-runtime symlink** | `RUNTIME_ROOT = .cursor`, `link_dir`, symlink `.claude/agents` + `.claude/skills`, generate `CLAUDE.md`. Archive: [`archive/host-runtime-symlink/`](archive/host-runtime-symlink/) — merge `302772d`. Design: [`superpowers/specs/2026-07-15-host-runtime-single-source-design.md`](superpowers/specs/2026-07-15-host-runtime-single-source-design.md). |
