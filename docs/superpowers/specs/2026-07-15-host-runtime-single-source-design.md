# Single source of truth for Cursor + Claude runtime

**Status:** proposed (2026-07-15)
**Approach:** A (symlink `.claude/` → `.cursor/`); designed to migrate cheaply to B (neutral canonical dir) later
**Implementation:** `install-claude.py` at repo root (edit copy → symlink)

---

## Problem

Nicki's runtime (agents, skills, invocation rule) must work in both Cursor and Claude Code.

- **Cursor** reads `.cursor/` committed in git — no install, always current after `git pull`.
- **Claude** reads `.claude/` + root `CLAUDE.md`, which `install-claude.py` **copies** from `.cursor/` (gitignored).

Because Claude's layout is a **copy**, any change to a Nicki agent or skill requires re-running `install-claude.py` or Claude goes stale. We want to **edit one file and have both hosts current**.

---

## Ecosystem consensus (research 2026)

Multi-agent dotfile setups converge on one pattern:

1. One **canonical** folder holds the real files.
2. **Symlink** the shareable parts (`agents/`, `skills/`) into each host dir — edit once, both hosts see it.
3. **Generate, not symlink,** the rule/invocation file. Cursor `.mdc` and `CLAUDE.md` must be self-contained; Cursor docs say `.mdc` cannot follow file references. Each host gets an **independent adapter** for its rule file.

Sources: rushis.com symlink guide; brandonwie.dev "One Folder, Three Agents"; iannuttall/dotagents; Medium "Unifying AI skills across Cursor and Claude Code"; orieken/ai-assistant-dot-files ARCHITECTURE.md ("symlink agents/skills, generate-inline for rules").

**Known gotcha — atomic saves break symlinks.** Editors that save via write-temp-then-rename replace the *symlink itself* with a regular file, silently severing it from the source. Mitigations: document "edit the canonical file, never the `.claude/` symlink"; make the installer self-repairing.

---

## Decision: Approach A

Keep `.cursor/` as the canonical source. `install-claude.py` **symlinks** instead of copying.

| Topic | Decision |
|-------|----------|
| Canonical source | `.cursor/agents/`, `.cursor/skills/` (committed, unchanged) |
| Claude agents | `.claude/agents` → `../.cursor/agents` (directory symlink) |
| Claude skills | `.claude/skills` → `../.cursor/skills` (directory symlink) |
| Claude rule | Generate `CLAUDE.md` from `.cursor/rules/nicki-default.mdc` (independent adapter — unchanged) |
| Path prose | Unchanged. `.claude/skills → .cursor/skills` keeps `.cursor/skills/...` commands resolvable under Claude because the `.cursor/` tree ships in every clone |
| Re-run trigger | Only on fresh clone, or when `nicki-default.mdc` changes (CLAUDE.md regen). Agent/skill edits need **no** reinstall |
| Gitignore | `.claude/` and `CLAUDE.md` stay ignored (generated artifacts) |

### Why A over B/C

- **B (neutral canonical dir)** is the correct long-term extract (#20) but requires moving all committed runtime, touching path prose, and building both installers now — large churn for the same daily benefit.
- **C (doctor / post-pull re-copy)** never delivers "edit once"; it just automates copying.
- **A** is the smallest change that fully removes the staleness problem and matches the ecosystem pattern.

---

## `install-claude.py` behavior (target)

```
install-claude.py
├── RUNTIME_ROOT = .cursor        # single knob; B flips this to nicki-workflow/.agents
├── link_dir(src, dest)           # create-or-repair a directory symlink (reusable)
├── install_agents()  → link_dir(RUNTIME_ROOT/agents, .claude/agents)
├── install_skills()  → link_dir(RUNTIME_ROOT/skills, .claude/skills)
├── generate_claude_md()          # adapter: RUNTIME_ROOT/rules/nicki-default.mdc → CLAUDE.md
├── print_success()               # guidance + "edit .cursor/, never .claude/" note
└── main()
```

### `link_dir(src, dest)` semantics

1. If `dest` is already a symlink to `src` → no-op (idempotent).
2. If `dest` exists as a regular dir/file (atomic-save breakage or old copy) → remove and recreate the symlink (**self-repair**).
3. Create `dest` as a relative directory symlink to `src`.
4. If the OS rejects symlinks (e.g. Windows without privilege) → fall back to copy and print a warning that re-runs are required after edits.

### Properties

- **Stdlib only** — `pathlib`, `shutil`, `os`, `sys`
- **Idempotent + self-repairing**
- **Relative links** — portable across clone locations
- **No network, no sudo**

---

## B-alignment (baked in now, no extra work)

These make the future A→B migration a small diff, and cost nothing today:

- **`RUNTIME_ROOT` constant** — the only thing B changes for the source path.
- **`link_dir(src, dest)` helper** — reused verbatim by a future `install-cursor.py`; only the source path differs.
- **Isolated `generate_claude_md()`** — in B it reads the rule from the neutral dir; same adapter shape.

### Explicit A→B delta (future, not this task)

1. Move `.cursor/agents`, `.cursor/skills`, `.cursor/rules` into a neutral `nicki-workflow/` (or `.agents/`).
2. Flip `RUNTIME_ROOT` to the neutral dir.
3. Add `.cursor/agents`/`.cursor/skills` symlinking to `install.py` (or a new `install-cursor.py`) using the same `link_dir` helper.
4. Rewrite hardcoded `.cursor/skills/...` path prose to the neutral path (or keep `.cursor/` as a compatibility symlink).

### Deliberately NOT done now (YAGNI / would be B or over-engineering)

- Creating the neutral dir or moving committed runtime.
- A host registry / plugin abstraction.
- Making `install.py` symlink `.cursor/`.
- A shared runtime-link module before `install-cursor.py` exists.

---

## Out of scope

- `nicki-workflow/` extract itself (#20 / Approach B).
- `install-cursor.py`.
- Cursor hooks parity in Claude.
- Windows-first support (symlink fallback to copy is enough).
- Committing `.claude/` symlinks (stays gitignored; created by install).

---

## Documentation updates (with implementation)

| Doc | Change |
|-----|--------|
| `README.md` | Claude quick-start: note edits go in `.cursor/`; `.claude/` is symlinks; re-run `install-claude.py` only after changing the invocation rule or on fresh clone; add atomic-save warning |
| `docs/tasks.md` | Add follow-up row for Approach B (neutral-dir extract, #20) referencing this design |

---

## Testing (YAGNI, manual)

Extend the existing fresh-install temp-clone check:

1. `python3 install.py` then `python3 install-claude.py` → exit 0.
2. Assert `.claude/agents` and `.claude/skills` are **symlinks** resolving into `.cursor/`.
3. Edit a canonical skill file under `.cursor/skills/…`; confirm the change is visible through the `.claude/skills/…` path **without** reinstall.
4. Re-run `install-claude.py` → exit 0 (idempotent).
5. Replace `.claude/agents` with a regular dir, re-run → link repaired (self-repair).
6. `check-gate.py` / `bootstrap-context.py` invoked via `.cursor/skills/...` still resolve.

No automated CI smoke script (consistent with prior host-bootstrap tasks).

---

## Success criteria

1. After one `install-claude.py`, editing any `.cursor/agents/*` or `.cursor/skills/*` updates Claude with **no reinstall**.
2. `.claude/agents` and `.claude/skills` are symlinks into `.cursor/`.
3. Re-run is idempotent and repairs a broken/replaced link.
4. `CLAUDE.md` still generated from the invocation rule (only re-run trigger left).
5. `RUNTIME_ROOT` is the single source-path knob for a future B migration.
