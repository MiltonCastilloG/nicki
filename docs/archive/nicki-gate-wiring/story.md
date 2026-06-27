# P2 — Nicki gate-script wiring

## Feature: Nicki invokes check-gate.py before sheep spawn

As a Nicki operator
I want Nicki to run the gate script before spawning a sheep
So that pipeline step gates are enforced deterministically instead of by prompt interpretation alone

### Background

```gherkin
Given check-gate.py and its gates package exist at .cursor/skills/nicki/scripts/ (check-gate.py, gates.py, gate_utils.py)
And routing.yaml and task-status.v2 status.json are the gate script inputs
And actors are the user, Nicki, and sheep
And P2 #7 delivered the gate script; this task is P2 #8 Nicki wiring plus P2 #11 permissions
And the gate package may be modified when wiring requires it — not read-only
And sole primary deliverable is nicki.md gate wiring; permissions.json when entries are missing or incomplete
And existing gate prose in nicki.md stays in place — add harness wiring, do not delete Workflow, Transitions hard-gates, Bootstrap, or Readiness sections (P3 trim is out of scope)
And P2 #9 return YAML validator, P2 #10 smoke fixtures, routing.yaml edits, status-read.md, NICKI.md, and nicki-default.mdc are out of scope unless a minimal nicki.md cross-reference requires it
And constraints are no-commit and no-new-deps unless required for wiring
```

### Scenario: Gate runs after transition card and user confirm

```gherkin
Given Nicki has completed disk bootstrap per the Bootstrap section
And Nicki has shown the transition card for task.next_step
And the user confirmed the transition (or the step skips confirm per routing.yaml)
When Nicki is about to spawn a pipeline sheep via Task
Then Nicki runs check-gate.py from the workspace root with --worktree and --step for the current pipeline step
And --worktree is the task worktree path from global-status.json / status.json scope
And --step is task.next_step (or the step Nicki is attempting when routing differs)
And Nicki passes --user-confirmed when the user explicitly confirmed a git or close step in chat
And Nicki passes --override when the user explicitly overrides sync without acceptance
And Nicki does not run check-gate.py before sheep-status (status_update is automatic housekeeping after a sheep)
```

### Scenario: Denied gate blocks spawn and surfaces reason

```gherkin
Given Nicki ran check-gate.py for the pending step
When stdout JSON has allowed false
Then Nicki shows reason from the script output to the user
And Nicki does not spawn the sheep Task
And Nicki does not advance the pipeline past the blocked step
And existing gate prose in nicki.md remains authoritative fallback context for the operator
```

### Scenario: Allowed gate authorizes spawn from script output

```gherkin
Given Nicki ran check-gate.py for the pending step
When stdout JSON has allowed true
Then Nicki spawns Task with subagent_type equal to sheep from the script output
And Nicki respects user_confirm from the script when deciding whether confirm was required before the run
And Nicki-only steps with sheep null do not spawn a sheep Task when the gate passes
And after a sheep completes (except sheep-close), Nicki still sends sheep-status automatically per existing rules
```

### Scenario: Gate wiring complements P1-16 disk-first bootstrap

```gherkin
Given P1-16 context-handling requires Nicki to bootstrap from disk every response
When Nicki routes or prepares a sheep spawn
Then Nicki still reads global-status.json, status.json, and routing.yaml before acting — disk wins over chat and parent prompt
And check-gate.py is the authoritative spawn decision after bootstrap and user confirm — not a replacement for reading status position from disk
And Nicki does not re-derive gate outcomes from prompt prose when the script has been run for that transition
And the gate script loads validation YAML and spec artifacts only when that step's gate needs them — aligning with Bootstrap file-read limits
```

### Scenario: nicki.md documents the gate invocation block

```gherkin
Given nicki.md Transitions or an adjacent workflow section is updated for this task
When an operator or reviewer reads Nicki agent instructions
Then prose describes the sequence show transition card → user confirm when required → run check-gate.py → spawn sheep from output or show reason and stop
And the new block references check-gate.py by path under .cursor/skills/nicki/scripts/
And existing numbered Workflow, hard-gate tags, Bootstrap, and Readiness prose is preserved unchanged
And Nicki Safety allows running check-gate.py as the permitted gate-script invocation (read-only Nicki otherwise unchanged)
```

---

## Feature: Permissions allow Nicki to run the gate script

As a Nicki operator
I want agent permissions to allow check-gate.py invocations
So that Nicki can run the gate script without hook denial

### Scenario: permissions.json allows gate script

```gherkin
Given .cursor/permissions.json controls terminal allowlist and autoRun instructions
When permissions are verified or updated for this task
Then terminalAllowlist includes python3 invocation of .cursor/skills/nicki/scripts/check-gate.py with --worktree and --step arguments
And autoRun allow_instructions document check-gate.py alongside other Nicki Python scripts
And create-worktree.py permissions remain present per P2 #11
And no unrelated permissions entries are removed
```

### Scenario: Gate package tweaks in scope for wiring

```gherkin
Given check-gate.py wiring exposes a gap in CLI flags, stdout fields, or step coverage
When implementers need a small change to check-gate.py, gates.py, or gate_utils.py to complete Nicki wiring
Then that change is in scope for this task
And broader gate rewrites, new steps in routing.yaml, and smoke fixtures remain out of scope
```
