# 01-0 — Review loop and orchestration routing

From `report.md`. Parallel with `01-1-stories.md`. Baseline: slice 00 JSON status done.

---

## Feature: Readiness routing in review validation

As a Nicki orchestrator  
I want machine-readable readiness in `review-validations/*.yaml`  
So that Nicki routes to acceptance, fix loop, or commit without inferring from review prose

```gherkin
Given per-task status.json points to the latest review-validation artifact
And review-triage writes review-validations under current-task/
```

### Scenario: Triage emits readiness block

```gherkin
When review-triage writes current-task/review-validations/<slug>.yaml
Then the artifact includes readiness.status, readiness.recommended_next_step, and readiness.blockers
And readiness.status is one of "ready_for_acceptance", "fix_required", "rerun_review", "blocked"
And blockers is non-empty only when status is "fix_required" or "blocked"
And status.json updates the validation artifact pointer
And Nicki does not offer commit-task while status is "fix_required" or "blocked"
```

### Scenario: Nicki resumes from disk

```gherkin
Given chat memory lost the routing decision
And status.json points to a validation artifact with a readiness block
When Nicki resumes orchestration
Then Nicki reads readiness from that artifact
And Nicki does not infer next step from review markdown alone
```

---

## Feature: Fix loop via appended subtasks

As a workflow operator  
I want valid findings turned into appended fix subtasks  
So that execute-plan reruns work without losing completed checklist history

```gherkin
Given readiness.status is "fix_required"
And current-task/subtasks/<slug>.md has completed "- [x]" lines
```

### Scenario: Append fix subtasks and rerun review

```gherkin
When Nicki or review-triage appends a fix section per policy
Then new lines are one-sentence actionable subtasks
And prior "- [x]" lines stay unchanged
And the fix section references the validation artifact path
And status.json next_step routes to execute per policy
When execute-plan, review-execution, and review-triage complete again
Then readiness may become "ready_for_acceptance"
And status.json history records the fix-loop iteration
```

---

## Feature: User acceptance before commit

As a workflow operator  
I want acceptance after triage and before git side effects  
So that commit runs only after I confirm outcomes

```gherkin
Given readiness.status is "ready_for_acceptance"
And Nicki orchestrates acceptance as a Nicki-only step
```

### Scenario: Acceptance gates commit

```gherkin
When Nicki reaches the acceptance checkpoint
Then Nicki shows a compact summary from disk artifacts
And Nicki does not invoke commit-task before explicit user acceptance
When the user accepts
Then Nicki records acceptance in status.json history or artifact pointer
And next_step may advance toward commit-task with separate git confirmation
When the user rejects
Then Nicki does not invoke commit-task
And status.json open_questions or blockers update
And next_step routes to fix loop or describe per user direction
```

---

## Feature: Partial execution and scoped review

As a Nicki orchestrator  
I want rules when execution was partial  
So that review and commit do not advance without explicit scope and user confirm

### Scenario: Full review by default

```gherkin
Given execution completed all subtasks or review_scope is absent
When Nicki routes after execute-plan
Then Nicki proceeds to review-execution with full scope
```

### Scenario: Partial scope needs confirm

```gherkin
Given execution handoff sets review_scope.mode to partial
When Nicki considers review-execution
Then Nicki asks the user to confirm scoped review
And review-execution limits findings to review_scope
And Nicki does not auto-advance to commit without full readiness
```

---

## Feature: Spec phase blocking on open questions

As a Nicki orchestrator  
I want unresolved spec questions to block downstream steps  
So that subtasks do not drift on ambiguous requirements

### Scenario: open_questions block and clear

```gherkin
Given spec-maker wrote non-empty open_questions in the spec handoff
When Nicki considers subtask-maker
Then Nicki blocks or asks before subtask-maker runs
And status.json mirrors non-empty open_questions
When the user resolves all open_questions and status-update runs
Then open_questions is empty in status.json
And next_step may advance to subtasks
```
