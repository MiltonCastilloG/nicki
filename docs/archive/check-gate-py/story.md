# P2 — check-gate.py and permissions

## Feature: check-gate.py enforces pipeline step gates

As a Nicki operator
I want a deterministic gate script before sheep spawn
So that `routing.yaml` gates are enforced deterministically by script

### Background

```gherkin
Given P1 groundwork is done — routing.yaml, task-status.v2, and create-worktree.py exist
And check-gate.py does not exist yet at .cursor/skills/nicki/scripts/check-gate.py
And sole deliverables are check-gate.py and permissions.json — no other files unless required to implement the gate script
And actors are the user and check-gate.py
And the script reads current-task/status.json and .cursor/skills/nicki/routing.yaml
And the script reads validation YAML and/or spec artifacts only when a step gate needs them
And the script owns the spawn decision in its stdout JSON — callers are out of scope here
And nicki.md is out of scope — zero changes, no gate wiring, no "run check-gate.py" block (P2 #8)
And P2 #10 smoke fixtures and P3 nicki.md trim are out of scope
And existing gate prose in nicki.md stays untouched — this task does not edit nicki.md at all
And constraints are no-commit and no-new-deps unless required for the script
```

### Scenario: stdout contract

```gherkin
When check-gate.py is invoked for a worktree and a pipeline step
Then it loads task-status.v2 status.json from that worktree
And it loads routing.yaml from .cursor/skills/nicki/routing.yaml
And it prints JSON to stdout with keys allowed, sheep, reason, and user_confirm
And allowed is a boolean — true only when the step gate passes
And sheep is the routing.yaml subagent_type for that step when spawn is permitted (or null for Nicki-only steps)
And reason is a human-readable denial when allowed is false
And user_confirm reflects whether the step requires explicit user git or close confirmation per routing.yaml
```

### Scenario: git tail gates implemented first

```gherkin
Given implementation prioritizes git tail steps from routing.yaml
When gates for sync, archive, integrate, and close are implemented
Then sync is denied when readiness is fix_required or blocked and when acceptance or override is missing
And archive is denied when sync artifact is missing or pre_push_merge is not satisfied on the sync handoff
And integrate is denied when sync or archive artifacts are missing or merge-into-main consent is not recorded
And close is denied when integrate is not recorded or close consent is not satisfied
And these git tail gates are delivered before or as the first tranche of remaining step gates
```

### Scenario: all pipeline step gates

```gherkin
When check-gate.py is invoked for any step defined in routing.yaml
Then it evaluates that step's gate against status.json and routing.yaml
And describe is denied without task.original present or collected
And spec is denied when artifacts.story is unset or story.md is missing on disk
And subtasks is denied when status or spec open_questions is non-empty
And execute is denied when subtasks artifact is missing
And review is denied when execution artifact is missing
And acceptance is denied unless readiness.status is ready_for_acceptance and user acceptance is recorded
And fix routes only when readiness.status is fix_required
And done is allowed only after close completed
And denied gates set allowed to false with an actionable reason
And passing gates return the correct sheep from routing.yaml
```

### Scenario: readiness and spec inputs when gates need them

```gherkin
Given status.json points at artifacts.review_validation
When check-gate.py gates review, acceptance, sync, or readiness-routed steps
Then it loads the validation YAML to resolve readiness.status
And readiness_routing in routing.yaml determines acceptance, execute fix loop, or blocked

Given a subtasks gate check requires spec open_questions
When check-gate.py evaluates the subtasks step
Then it loads the spec artifact referenced in status.json
And denies spawn while spec open_questions is non-empty
```

### Scenario: gate output is the spawn decision

```gherkin
When check-gate.py evaluates a step and the gate fails
Then allowed is false in stdout JSON
And reason is actionable for a caller to surface to the operator

When check-gate.py evaluates a step and the gate passes
Then allowed is true
And sheep matches the routing.yaml subagent_type for that step
```

---

## Feature: permissions allow gate and worktree scripts

As a Nicki operator
I want agent permissions to allow the gate and worktree Python scripts
So that those scripts can run without hook denial

### Scenario: permissions.json allows Python invocations

```gherkin
Given .cursor/permissions.json controls terminal allowlist and autoRun instructions
When permissions are updated for this task
Then terminalAllowlist includes python3 invocation of .cursor/skills/nicki/scripts/check-gate.py
And terminalAllowlist includes python3 invocation of .cursor/skills/start-task/scripts/create-worktree.py
And autoRun allow_instructions document both scripts where other Nicki Python scripts are listed
And no unrelated permissions entries are removed
```
