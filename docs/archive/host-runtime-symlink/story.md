# host-runtime-symlink — single source of truth for Cursor + Claude runtime

`install-claude.py` symlinks `.claude/agents` and `.claude/skills` into committed `.cursor/` (Approach A) so agent and skill edits need no reinstall. `CLAUDE.md` remains a generated adapter from the invocation rule. Scope is YAGNI symlink refactor only — not neutral-dir extract, not `install-cursor.py`.

---

## Design decisions (approved)

| Topic | Decision |
| --- | --- |
| Canonical source | `.cursor/agents/`, `.cursor/skills/` (committed, unchanged) |
| Claude agents | `.claude/agents` → `../.cursor/agents` (relative directory symlink) |
| Claude skills | `.claude/skills` → `../.cursor/skills` (relative directory symlink) |
| Claude rule | Generate `CLAUDE.md` from `.cursor/rules/nicki-default.mdc` (unchanged adapter) |
| Source-path knob | `RUNTIME_ROOT = .cursor` — sole constant for future Approach B migration |
| Link helper | Reusable `link_dir(src, dest)` — idempotent, self-repairing, relative symlinks |
| Re-run trigger | Fresh clone, or when `nicki-default.mdc` changes — not on agent/skill edits |
| Gitignore | `.claude/` and `CLAUDE.md` stay ignored (generated artifacts) |
| Symlink fallback | If OS rejects symlinks → copy with warning that re-runs are required after edits |
| Docs | README Claude quick-start + atomic-save warning; `docs/tasks.md` row for Approach B (#20) |

---

## Feature: install-claude.py symlinks Claude runtime to .cursor/

As a developer using Nicki in both Cursor and Claude Code  
I want `.claude/agents` and `.claude/skills` to mirror `.cursor/` via symlinks  
So that I edit runtime files once and both hosts stay current without reinstall

```gherkin
Background:
  Given I have cloned the Nicki repository
  And I am at the repository root
  And the repository contains the committed `.cursor/` Nicki runtime
```

### Scenario: First install creates symlinks and CLAUDE.md

```gherkin
When I run `python3 install-claude.py`
Then the command exits with code 0
And `.claude/agents` is a directory symlink resolving to `.cursor/agents`
And `.claude/skills` is a directory symlink resolving to `.cursor/skills`
And root `CLAUDE.md` is generated from `.cursor/rules/nicki-default.mdc` with opt-in Nicki routing
And the install prints guidance to edit `.cursor/`, not `.claude/`
```

### Scenario: Canonical edits propagate without reinstall

```gherkin
Given I have run a successful `python3 install-claude.py`
When I edit a file under `.cursor/agents/` or `.cursor/skills/`
Then the change is visible through the corresponding path under `.claude/agents/` or `.claude/skills/`
And I do not need to re-run `install-claude.py`
```

### Scenario: Re-run is idempotent

```gherkin
Given `.claude/agents` and `.claude/skills` are already correct symlinks into `.cursor/`
When I run `python3 install-claude.py` again
Then the command exits with code 0
And the symlinks remain valid directory links into `.cursor/`
And `CLAUDE.md` is regenerated from the invocation rule
```

### Scenario: Self-repair replaces broken or copied destinations

```gherkin
Given `.claude/agents` or `.claude/skills` exists as a regular directory or file (e.g. after atomic-save breakage or an old copy install)
When I run `python3 install-claude.py`
Then the command exits with code 0
And the destination is removed and recreated as a relative directory symlink into `.cursor/`
```

### Scenario: Symlink rejection falls back to copy

```gherkin
Given the operating system rejects creating directory symlinks
When I run `python3 install-claude.py`
Then the command exits with code 0
And agents and skills are installed by copy instead of symlink
And the install prints a warning that re-runs are required after runtime edits
```

### Scenario: Path prose and bootstrap scripts still resolve

```gherkin
Given `install-claude.py` completed successfully with symlinks
When I invoke Nicki skills or scripts via `.cursor/skills/...` paths referenced in runtime prose
Then those paths resolve because the `.cursor/` tree ships in every clone
And `check-gate.py` and `bootstrap-context.py` remain reachable through the canonical tree
```

---

## Feature: Documentation reflects symlink model

As a Nicki operator  
I want README and task backlog to describe the single-source layout  
So that I know where to edit and when to re-run install

### Scenario: README documents Claude symlink quick-start

```gherkin
Given I read the repository README Claude quick-start section
Then it states runtime edits belong in `.cursor/` and `.claude/` holds symlinks
And it states re-run `install-claude.py` only on fresh clone or after changing the invocation rule
And it warns that atomic-save editors can replace symlinks with regular files and to edit the canonical path
```

### Scenario: Task backlog records Approach B follow-up

```gherkin
Given I read `docs/tasks.md`
Then a follow-up row exists for Approach B (neutral-dir extract, #20) referencing the host-runtime single-source design
```

---

## Out of scope

- `nicki-workflow/` neutral canonical dir extract (Approach B / #20)
- `install-cursor.py` or symlinking `.cursor/` from install
- Cursor hooks parity in Claude
- Host registry or shared runtime-link module
- Committing `.claude/` symlinks to git
- Automated CI smoke script (manual fresh-install check only, consistent with prior host-bootstrap tasks)
