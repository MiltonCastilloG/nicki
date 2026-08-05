# Approach B — neutral-dir extract checklist

**Task:** [`tasks.md`](tasks.md) **#20**

**Design:** [Single source of truth for Cursor + Claude runtime](superpowers/specs/2026-07-15-host-runtime-single-source-design.md)

**Fresh-install context:** [Fresh install design](superpowers/specs/2026-07-02-fresh-install-design.md) — `#20` (`nicki-workflow/` extract) and `#21`–`#23` (Claude / host adapters).

**Prerequisite:** Approach A shipped — `.cursor/` canonical, `RUNTIME_ROOT = .cursor`, Claude symlinks via `install-claude.py`. See [`tasks-done.md`](tasks-done.md).

**Goal:** One **neutral** committed canonical dir for agents/skills/rules; host dirs (`.cursor/`, `.claude/`) become adapters via symlinks + generated rule files. Approach B is mostly move + flip `RUNTIME_ROOT` + Cursor linker.

Reference A→B delta from the [single-source design](superpowers/specs/2026-07-15-host-runtime-single-source-design.md):

1. Move `.cursor/agents`, `.cursor/skills`, `.cursor/rules` into a neutral dir.
2. Flip `RUNTIME_ROOT` to that dir.
3. Add `.cursor/` (and keep `.claude/`) symlinking via the same `link_dir` helper.
4. Rewrite or compat-hardcoded `.cursor/skills/...` path prose.

---

## Choose / create neutral dir name

**Recommendation: `nicki-workflow/`** (not `.agents/`).

| Option | Pros | Cons |
|--------|------|------|
| **`nicki-workflow/`** (recommended) | Already named in fresh-install `#20` and PLAN-era docs; visible (not a hidden host clone); clearly Nicki's product, not Cursor/Claude; easy to reason about in git and docs | Longer paths; one more top-level dir |
| `.agents/` | Short; matches some ecosystem examples | Hidden; easy to confuse with host tooling; weaker "Nicki owns this" signal; not the name used in `#20` prose |

**Decision checklist**

- [ ] Confirm `nicki-workflow/` in a short design note (or tasks.md row) before moving files
- [ ] Layout target: `nicki-workflow/agents/`, `nicki-workflow/skills/`, `nicki-workflow/rules/` (rules stay canonical; hosts get generated adapters)
- [ ] Decide whether hooks / `permissions.json` stay under `.cursor/` only (host-specific) or also move — **recommend leave hooks + permissions under `.cursor/`** unless Claude needs them later (out of scope for B core)

## Move agents, skills, rules from `.cursor/` into neutral dir

- [ ] `git mv` `.cursor/agents` → `nicki-workflow/agents`
- [ ] `git mv` `.cursor/skills` → `nicki-workflow/skills`
- [ ] `git mv` `.cursor/rules` → `nicki-workflow/rules` (at least `nicki-default.mdc`)
- [ ] Leave host-only Cursor files in place if not moved: `permissions.json`, `hooks.json`, `hooks/` (unless a later task relocates them)
- [ ] Verify no stray copies of agents/skills remain as real directories under `.cursor/` after move

## Flip `RUNTIME_ROOT` in `install-claude.py`

- [ ] Set `RUNTIME_ROOT` from `.cursor` → `nicki-workflow` (or path constant matching chosen dir)
- [ ] Confirm `link_dir(RUNTIME_ROOT/agents → .claude/agents)` and skills still relative and self-repairing
- [ ] Confirm `generate_claude_md()` reads `nicki-workflow/rules/nicki-default.mdc`
- [ ] Re-run manual Claude install proof (idempotent + self-repair)

## Cursor installer: `install-cursor.py` or `install.py` `link_cursor_runtime`

Per fresh-install "Future hook (#20)" and single-source B delta:

- [ ] Prefer extending `install.py` with `link_cursor_runtime()` **or** add `install-cursor.py` that reuses the same `link_dir` helper — one shared implementation, no duplicate link logic
- [ ] Symlink: `nicki-workflow/agents` → `.cursor/agents`
- [ ] Symlink: `nicki-workflow/skills` → `.cursor/skills`
- [ ] Rule file: **generate** `.cursor/rules/nicki-default.mdc` from canonical rule (or keep a thin Cursor-only adapter) — **do not symlink the `.mdc` if that breaks Cursor's "no follow references" constraint**; generate-inline stays the safe pattern
- [ ] Fresh clone path: `python3 install.py` must create Cursor links so Cursor works without a manual second script (README must match)
- [ ] Claude path: still `python3 install-claude.py` after or documented beside install

## Gitignore / git tracking strategy

- [ ] **Canonical `nicki-workflow/`** — tracked in git (source of truth)
- [ ] **`.claude/`** — remain gitignored (generated symlinks + install artifact)
- [ ] **`CLAUDE.md`** — remain gitignored (generated adapter)
- [ ] **`.cursor/agents` and `.cursor/skills` after B** — become symlinks:
  - Option A (cleaner): stop tracking real trees; document that `install.py` creates links; optionally gitignore link targets if git cannot store them portably
  - Option B (compat): commit relative symlinks in git if the team accepts symlink-in-repo semantics for Linux/macOS
- [ ] Document Windows: symlink may fail → copy fallback (same as Approach A); re-run required after edits in that mode
- [ ] Ensure `git status` after install is clean for ignored generated hosts; no accidental commit of `.claude/` copies

## Hardcoded `.cursor/skills/...` paths — rewrite or compatibility

Paths appear widely (agents, skills, hooks, permissions, routing, smokes, archives).

**Recommended strategy (pick one explicitly):**

1. **Compatibility first (lower churn):** After Cursor links exist, leave prose as `.cursor/skills/...` — resolvable because `.cursor/skills` → `nicki-workflow/skills`. Fastest B land.
2. **Rewrite later (clarity):** Second pass to `nicki-workflow/skills/...` (or a single helper constant) once A/B install is stable.

Checklist:

- [ ] Inventory grep: `nicki.md`, sheep agents, skills (`start-task`, `nicki/routing.yaml`, smoke scripts), hooks, `permissions.json`, tests
- [ ] Either verify every command still resolves via `.cursor/` symlinks **or** batch-rewrite to neutral paths
- [ ] Update `permissions.json` allowlist strings to match the chosen path style
- [ ] Update hook script paths if they invoke skills by string path
- [ ] Re-run gate/bootstrap smokes after path decision

## Host adapters: `CLAUDE.md` + `nicki-default.mdc`

- [ ] Keep **generate, don't symlink** for host rule/invocation files
- [ ] Canonical rule lives under `nicki-workflow/rules/nicki-default.mdc`
- [ ] `install-claude.py` → generates root `CLAUDE.md`
- [ ] Cursor install → generates/refreshes `.cursor/rules/nicki-default.mdc` (or leaves a Cursor-specific wrapper that embeds the same opt-in Nicki text)
- [ ] Document: edit the canonical rule; re-run host install(s) when the invocation rule changes (agent/skill edits still need **no** reinstall if symlinks)

## Docs updates

- [ ] `README.md` — canonical dir is `nicki-workflow/`; edit there; host dirs are adapters; atomic-save warning applies to **both** `.cursor/` and `.claude/` symlink trees
- [ ] `docs/PLAN.md` — replace "workflow lives in `.cursor/`" / `package/.cursor/` language with neutral runtime + install-into-host
- [ ] Fresh-install design / archive notes — optional batch rename `install-claude` naming (claude-adapter suggestion) when touching bootstrap docs

## Manual verification checklist (Cursor + Claude after extract)

- [ ] Clean clone → `python3 install.py` → `.cursor/agents` and `.cursor/skills` are symlinks into `nicki-workflow/`
- [ ] `python3 install-claude.py` → `.claude/agents` and `.claude/skills` are symlinks into `nicki-workflow/` (via `RUNTIME_ROOT`)
- [ ] Edit a skill under `nicki-workflow/skills/…`; change visible in Cursor path **and** Claude path without reinstall
- [ ] Re-run both installers → idempotent; no error
- [ ] Break a host link (replace with a regular directory) → re-run installer → link repaired
- [ ] `bootstrap-context.py` invoked with documented paths still works
- [ ] Cursor: `nicki start …` / `nicki continue` opt-in still works
- [ ] Claude: same after `CLAUDE.md` present
- [ ] Atomic-save warning: editing through the host symlink path must not replace the symlink (document; spot-check editor behavior)

## Migration risks

| Risk | Mitigation |
|------|------------|
| **Atomic saves break symlinks** | Document "edit canonical `nicki-workflow/`, never host symlink path"; installers self-repair |
| **Windows symlink privilege / failure** | Keep copy fallback + warning that re-runs are required after edits |
| **Worktrees inheriting `.cursor/`** | Worktrees created from a branch that already has Cursor links (or real trees) inherit them; after B, ensure default branch has correct layout / install step before new worktrees |
| **Git and symlinks** | Decide track-vs-gitignore before merge; avoid half-tracked copy leftovers |
| **Path prose drift** | Grep gate + permissions + smoke in the same PR as the move |
| **Hooks stay Cursor-only** | Do not assume Claude gets hook parity in B (explicitly out of scope) |
| **Large simultaneous churn** | B is mostly move + flip `RUNTIME_ROOT` + Cursor linker |

## Out of scope for Approach B

- Cursor hooks parity in Claude
- `nicki doctor` / version pin (`#28` in fresh-install out-of-scope list)
- Managed-project runtime install (`nicki runtime install <project>`) unless required to unblock the Nicki-repo extract
- Host registry / plugin abstraction
- Shared runtime-link package extraction beyond what's needed to share `link_dir` between installers
- Full PLAN.md multi-project CLI (workspace init, clone, etc.)
