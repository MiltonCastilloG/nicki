# sheep-fallback — record harness script failures

## Feature: sheep-fallback captures failed script context

As a Nicki operator
I want a thin fallback agent that records harness script failures into an errors spec
So that failure context survives the task lifecycle and is available after archive

### Background

```gherkin
Given actors are the human user, Nicki, sheep-fallback, and sheep-status
And sheep-fallback is a really thin agent — wiring only, no creative feature work beyond recording failures
And sheep-fallback receives three inputs: the route of the failed script, the script input, and the expected output
And the errors artifact lives at current-task/specs/errors.yaml under the active worktree
And each failure appends a new entry — errors.yaml is not replaced wholesale per failure
And Nicki spawns sheep-fallback when a Nicki harness script fails validation — sheep-status does not spawn sheep-fallback
And candidate scripts that may trigger fallback include check-gate.py, validate-sheep-return.py, bootstrap-context.py, and update-status.py — spec pins the authoritative list
And constraints are no-commit, no-new-deps, and YAGNI — minimal agent definition plus errors spec write and archive conservation only
And fixing the underlying script bug, automatic retry, and changing sheep creative behavior are out of scope
```

### Scenario: Nicki spawns sheep-fallback on harness script failure

```gherkin
Given Nicki has invoked a Nicki harness script for the active worktree
And the script exits non-zero or returns output that does not match the expected contract
When Nicki routes to fallback instead of advancing the pipeline step
Then Nicki spawns sheep-fallback with the failed script route, the input passed to the script, and the expected output shape
And sheep-fallback does not modify source code or retry the failed script
```

### Scenario: sheep-fallback appends a failure record to errors.yaml

```gherkin
Given sheep-fallback received a failed script route, input, and expected output
When sheep-fallback completes its run
Then it writes or updates current-task/specs/errors.yaml in the worktree
And the file records the script route, input, expected output, and actual failure context from the invocation
And a subsequent failure appends another entry without erasing prior entries
And sheep-fallback returns the standard sheep return contract YAML for Nicki to relay to sheep-status
And sheep-fallback never writes current-task/status.json
```

### Scenario: errors spec schema is defined in spec step

```gherkin
Given story.md is approved and the pipeline reaches spec
When sheep-spec writes current-task/specs/sheep-fallback.yaml
Then it also documents the errors.yaml field schema and entry shape
And spec resolves which harness scripts invoke fallback if the story probe list differs from implementation
And spec open_questions is empty before subtasks proceed
```

---

## Feature: errors spec is conserved on archive

As a Nicki operator
I want the errors spec copied into the task archive
So that failure records are not lost when ephemeral spec files are cleaned up

### Background

```gherkin
Given task-archive today copies story.md and deletes the main task spec and subtasks from the worktree
And errors.yaml is a separate diagnostic artifact — not the task requirements spec
And archive output root is docs/archive/<slug>/ under the repo root
```

### Scenario: archive copies errors.yaml into docs/archive

```gherkin
Given current-task/specs/errors.yaml exists in a task worktree with one or more failure entries
When sheep-archive runs for that task
Then docs/archive/<slug>/errors.yaml is written as a copy of the worktree errors spec
And the archived errors file preserves all appended failure entries
And task-archive still deletes the main task spec and subtasks per existing archive rules
And report.yaml or report.md may reference that errors were recorded without pasting full failure bodies
```

### Scenario: tasks without failures omit errors archive copy

```gherkin
Given a task worktree has no current-task/specs/errors.yaml
When sheep-archive runs
Then docs/archive/<slug>/errors.yaml is not required
And archive completes without error for the missing errors artifact
```

---

## Probes for spec (resolve before subtasks)

The following forks are intentionally deferred from story to spec. Defaults above apply until spec confirms otherwise.

| Probe | Default in story | Spec must resolve |
|-------|------------------|-------------------|
| Which scripts invoke fallback? | check-gate.py, validate-sheep-return.py, bootstrap-context.py, update-status.py (candidates) | Authoritative trigger list and spawn conditions per script |
| Who spawns sheep-fallback? | Nicki only | Confirm sheep-status never spawns fallback |
| errors spec path and schema | current-task/specs/errors.yaml; append per failure | Entry fields, IDs, timestamps, and validation rules |
| Archive conservation | copy to docs/archive/<slug>/errors.yaml | Confirm task-archive skill/format change scope |
| YAGNI boundary | thin agent + wiring only | Explicit out-of-scope list in spec scope.out |

---

## Feature: YAGNI scope boundary

As a Nicki operator
I want sheep-fallback limited to failure recording wiring
So that the agent stays maintainable and does not absorb orchestration logic

### Scenario: out of scope for sheep-fallback

```gherkin
Given this chore scopes sheep-fallback and errors archive conservation only
When implementers plan subtasks
Then they do not implement fixes inside the failing harness scripts in this task
And they do not add automatic retry, self-healing, or alternate spawn paths beyond Nicki routing
And they do not expand sheep-fallback into general error triage or user-facing diagnostics beyond writing errors.yaml
And routing.yaml changes are limited to registering sheep-fallback as a spawn target when spec requires it
```
