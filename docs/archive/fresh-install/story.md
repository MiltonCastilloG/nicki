# fresh-install — Post-clone bootstrap for the Nicki repository

After `git clone`, a developer runs `python3 install.py` at the repo root so the Nicki repo is ready to invoke `nicki start …` in Cursor without manual file copying. Scope is Nicki-repo bootstrap only — not host adapters, project install, or `nicki-workflow/` symlinks.

---

## Design decisions (approved)

| Topic | Decision |
| --- | --- |
| Install target | Nicki repo clone (not foreign app repos) |
| Script | `install.py` at repo root (stdlib Python) |
| Registry | Write minimal `nicki-workspace.yaml` with only `projects.nicki` |
| Existing yaml | Skip with notice — never overwrite |
| Prerequisites | Check `git` first; hard-fail before any filesystem writes if missing |
| `worktrees/` | Create if missing |
| `global-status.json` | Not created at install |
| `.cursor/` runtime | No install action (committed; symlink hook deferred to #20) |
| Claude/Cursor adapters | Out of scope (`install-claude.sh` / #23) |
| Project install | P1 — out of scope |

---

## Feature: Fresh install bootstraps a cloned Nicki repository

As a developer who cloned the Nicki repository  
I want a one-command post-clone install  
So that I can open the repo in Cursor and run `nicki start …` without manual setup

```gherkin
Background:
  Given I have cloned the Nicki repository
  And I am at the repository root
  And `python3` and `git` are available on my PATH
```

### Scenario: First install succeeds

```gherkin
When I run `python3 install.py`
Then the command exits with code 0
And `nicki-workspace.yaml` exists with a nicki-only registry containing only `projects.nicki` pointing at `.` with `default_branch: main` and `remote: origin`
And `worktrees/` exists
And the install prints detected tool versions and next-step guidance
```

### Scenario: Re-run is safe and idempotent

```gherkin
Given `nicki-workspace.yaml` already exists
When I run `python3 install.py` again
Then the command exits with code 0
And the existing `nicki-workspace.yaml` is unchanged
And the install prints a notice that the registry was skipped
And `worktrees/` still exists
```

### Scenario: Missing git fails before any writes

```gherkin
Given `git` is not available on my PATH
When I run `python3 install.py`
Then the command exits with code 1
And an error message explains that git is required
And `nicki-workspace.yaml` is not created
And `worktrees/` is not created
```

### Scenario: README documents the install flow

```gherkin
Given I read the repository README quick-start section
Then it documents clone → `python3 install.py` → open in Cursor → invoke Nicki (`nicki start …` or `nicki continue`)
And it does not instruct manual `.cursor` copying as the primary setup path
```

### Scenario: Post-install Nicki invocation is unblocked

```gherkin
Given I have completed a successful `python3 install.py`
When I open the repository in Cursor
Then I can invoke Nicki to start or continue a task without additional local bootstrap steps covered by this story
```

---

## Out of scope

- `install-claude.sh` / `install-cursor.sh` host adapters (#23)
- `nicki-workflow/` extract and symlink layout (#20)
- `global-status.json` scaffold at install time
- Managed projects in `nicki-workspace.yaml` (tetris, landing, …)
- Version pin / `doctor` (#28)
- PyYAML or other non-stdlib dependencies
