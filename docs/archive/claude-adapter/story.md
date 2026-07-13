# claude-adapter — Claude Code host bootstrap for the Nicki repository

After `git clone`, a developer runs `install-claude.py` at the repo root so the committed `.cursor/` Nicki runtime is available under Claude Code's `.claude/` layout and `nicki start …` works without manual file copying. Scope is YAGNI host mapping only — not `nicki-workflow/` extract, not Cursor hooks parity.

---

## Design decisions (approved)

| Topic | Decision |
| --- | --- |
| Install target | Nicki repo clone (same as `install.py`) |
| Script | `install-claude.py` at repo root |
| Source runtime | Committed `.cursor/` agents, skills, and rules |
| Agents | Map `.cursor/agents/*.md` → `.claude/agents/` |
| Skills | Map `.cursor/skills/<name>/` → `.claude/skills/<name>/` |
| Invocation rules | Map `.cursor/rules/nicki-default.mdc` intent into root `CLAUDE.md` (opt-in Nicki routing) |
| Prerequisite | Assumes clone is present; `install.py` may run before or as part of the fresh-clone proof path |
| Hooks | Out of scope — no `.cursor/hooks.json` parity in Claude |
| `nicki-workflow/` extract | Out of scope (#20) |
| Success criterion | `nicki start …` completes the start step in Claude Code on a fresh clone |

---

## Feature: install-claude.py maps Nicki runtime into Claude Code layout

As a developer who cloned the Nicki repository  
I want a one-command Claude Code bootstrap  
So that I can open the repo in Claude and invoke `nicki start …` without manually copying agents or skills

```gherkin
Background:
  Given I have cloned the Nicki repository
  And I am at the repository root
  And the repository contains the committed `.cursor/` Nicki runtime
```

### Scenario: First install maps agents and skills

```gherkin
When I run `./install-claude.py`
Then the command exits with code 0
And `.claude/agents/` contains the Nicki orchestrator and sheep agent definitions derived from `.cursor/agents/`
And `.claude/skills/` contains the Nicki skill tree derived from `.cursor/skills/`
And root `CLAUDE.md` documents opt-in Nicki invocation equivalent to `.cursor/rules/nicki-default.mdc`
And the install prints next-step guidance for opening the repo in Claude Code
```

### Scenario: Re-run is safe

```gherkin
Given I have already run a successful `./install-claude.py`
When I run `./install-claude.py` again
Then the command exits with code 0
And the Claude layout remains usable for Nicki invocation
And the install does not corrupt or duplicate agent or skill definitions
```

### Scenario: Hooks and nicki-workflow are not in scope

```gherkin
Given this story's approved scope
When `./install-claude.py` completes
Then it does not extract or symlink a `nicki-workflow/` tree
And it does not replicate `.cursor/hooks.json` or Cursor hook scripts under `.claude/hooks/`
And README or install output does not claim hooks parity with Cursor
```

---

## Feature: Fresh clone proves nicki start in Claude Code

As a Nicki operator using Claude Code  
I want the post-clone install path to unblock the start pipeline  
So that I can begin a task without Cursor-specific bootstrap steps

### Scenario: End-to-end fresh clone to nicki start

```gherkin
Given I have cloned the Nicki repository into a clean directory
And I have run the repository bootstrap needed for worktrees and registry (e.g. `python3 install.py`)
And I have run `./install-claude.py`
When I open the repository in Claude Code
And I invoke Nicki with `nicki start <slug>` for a new task slug
Then Nicki is routed via the CLAUDE.md invocation rules
And the start pipeline step completes successfully
And a task worktree exists under `worktrees/`
And `current-task/status.json` exists in that worktree with start completed and next step describe
```

### Scenario: README documents the Claude install path

```gherkin
Given I read the repository README
Then it documents a Claude Code quick-start path: clone → repository bootstrap → `./install-claude.py` → open in Claude → invoke Nicki (`nicki start …` or `nicki continue`)
And it does not instruct manual copying of `.cursor/` or `.claude/` as the primary Claude setup path
```

---

## Out of scope

- `nicki-workflow/` extract and symlink layout (#20)
- Cursor hooks parity (`.cursor/hooks.json`, hook scripts, agent-permissions hooks)
- `install-cursor.sh` or other host adapters beyond Claude
- Managed-project install into foreign repos (P1)
- Rewriting Nicki orchestration prose for Claude-specific semantics beyond invocation routing
- Version pin / doctor tooling

---

## Probes for spec (resolve before subtasks)

| Probe | Default in story | Spec must resolve |
| --- | --- | --- |
| Mapping mechanism | Script produces `.claude/` and `CLAUDE.md` from `.cursor/` | Copy, symlink, or generated adapter files — and what is gitignored vs committed |
| `install.py` coupling | Fresh-clone proof may run both scripts | Whether `install-claude.py` calls `install.py`, documents it as prerequisite, or stays independent |
| Agent frontmatter | Map Cursor agent markdown as-is where possible | Any Claude-specific frontmatter or naming adjustments required for subagent discovery |
| Skill layout | One folder per skill with `SKILL.md` | Whether nested skill assets (scripts, format docs) copy verbatim or subset |
| Permissions for scripts | Not in approved mapping list | Minimal Claude `settings.json` permissions only if required for `nicki start` / `create-worktree.py` to succeed |
| Verification | Manual fresh-clone proof in Claude | Whether an automated smoke script is YAGNI or required for acceptance |
