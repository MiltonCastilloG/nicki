# P1-6 — Gherkin and spec mutual understanding

## Feature: Describe step asks before inventing

As a Nicki operator
I want Nicki to ask the human user about task details before drafting Gherkin
So that the story reflects shared understanding instead of invented specifics

### Background

```gherkin
Given actors are the human user, Nicki, and sheep (no parent-agent behavior change)
And mutual understanding means asking the user about details instead of inventing specifics
And Nicki performs describe in chat only (Nicki does not write files directly)
And sheep-status writes story.md once after explicit user approval
And task.current_step stays "describe" until story.md exists on disk
And status.json open_questions is not updated during describe (chat is enough)
And disk open_questions may record blockers for compaction or new-chat recovery
And vague task.original is probed until implementation intent is clear enough to draft
And the user may approve scenario-by-scenario before the full story is accepted
And there is no user override to force advance past unresolved describe gaps
And when the user is silent, Nicki pauses and does not burn tokens speculating
And after spec begins, story is not re-opened for describe — gaps are repaired in spec
And priority when goals conflict is correct functioning, then harness, then trimming
And this task touches only nicki.md, sheep-spec.md, and spec-maker/SKILL.md with minimal diffs
And check-gate.py, routing.yaml, status-read.md, status-format.md, current-task-update/SKILL.md, story-format.md, and spec gate smoke are out of scope
And constraints are no-commit and no-new-deps
```

### Scenario: Nicki asks before first Gherkin draft

```gherkin
Given sheep-start completed and task.original is present in status.json
And Nicki is on the describe step
When task.original is missing detail needed for testable scenarios
Then Nicki asks the human user organized questions in chat
And Nicki does not draft Gherkin until questions are answered or Nicki has no gaps to fill
And Nicki does not write story.md on a first draft alone
```

### Scenario: Questions first, then draft, then revise

```gherkin
Given Nicki has gathered answers from the human user
When Nicki drafts Gherkin with Feature, As a / I want / So that, and at least one Scenario
Then Nicki shows the draft in chat without persisting story.md
And the human user may reject and request revision
And Nicki revises in chat across multiple rounds until approval
And Nicki sends sheep-status to write story.md only once after approval
```

### Scenario: Explicit approval of story meaning

```gherkin
Given Nicki has shown a Gherkin draft in chat
When the human user replies with "approve", "continue", or "go"
Or Nicki has no remaining gaps to fill and the user confirms
Then the story meaning is considered approved
And Nicki may send sheep-status to persist current-task/story.md
And task.story_artifact points to current-task/story.md
And last_completed_step advances to describe with next_step spec
```

### Scenario: Scenario-by-scenario approval

```gherkin
Given a Gherkin draft with multiple scenarios
When the human user approves one scenario but not others
Then Nicki iterates only on unapproved scenarios in chat
And Nicki does not persist story.md until all scenarios are approved or explicitly waived by the user
```

### Scenario: Nicki does not advance with gaps to fill

```gherkin
Given Nicki still has unanswered questions about scope, actors, or acceptance
When Nicki would show a transition card for a downstream sheep
Then Nicki does not proceed until gaps are resolved in chat with the human user
```

### Scenario: Acceptance test — describe on tetris ghost piece task

```gherkin
Given an agent invokes Nicki to start a worktree for tetris-clone-frp
And task.original references NEXT_STEPS.MD item "3) Implement ghost piece rendering"
When Nicki runs describe for that task
Then Nicki asks about details not stated in NEXT_STEPS (e.g. ghost alpha, game.js vs board.js wiring, recompute triggers)
And Nicki does not invent those specifics in the draft
And after user answers and approves, story.md is persisted and the pipeline may continue to spec
And the test stops at subtasks without execute when used as a verification run
```

---

## Feature: Spec step asks before writing YAML

As a Nicki operator
I want sheep-spec to resolve ambiguities with the human user before writing a spec file
So that subtasks breakdown starts from a complete requirements document

### Background

```gherkin
Given actors are the human user, Nicki, and sheep-spec
And Nicki relays sheep-spec questions to the human user in chat
And the human user answers in chat to unblock the pipeline
And multiple question rounds are allowed
And sheep-spec does not write current-task/specs/<slug>.yaml until open_questions would be empty
And when requirements fork, sheep-spec lists options and Nicki presents them to the human user
And open_questions must be [] before subtasks may proceed
And Nicki persists resolutions via sheep-status with user permission
And status open_questions during spec is secondary to chat (answered in chat)
And subtask-maker needs only the written spec document — no additional user Q&A loop
And spec-maker/SKILL.md enforces ask-first and no spec file while questions remain
And sheep-spec.md may receive minimal alignment; blocked-return contract prose is deferred to future P2 harness work
And there is no user override to force subtasks with non-empty spec open_questions
And when the user is silent, the pipeline stays blocked at spec
And gaps discovered after describe are repaired in spec, not by re-running describe
```

### Scenario: sheep-spec asks before writing spec file

```gherkin
Given an approved story.md exists and Nicki transitions to spec
When sheep-spec finds vague requirements or design forks in the approved story
Then sheep-spec does not write a spec YAML file
And sheep-spec returns blocked handoff with open_questions populated
And Nicki presents those questions to the human user in chat
```

### Scenario: Nicki relays answers and re-runs spec

```gherkin
Given sheep-spec blocked with open_questions
And the human user answered in chat
When Nicki has user permission to persist resolution
Then Nicki sends sheep-status as needed and re-sends sheep-spec
And sheep-spec writes the spec file only when all open_questions are resolved
```

### Scenario: Subtasks gate requires empty open_questions

```gherkin
Given a spec file exists at current-task/specs/<slug>.yaml
When spec open_questions is non-empty
Then subtasks step does not proceed
And Nicki does not send sheep-subtask until open_questions is []
```

### Scenario: Fork presented as options

```gherkin
Given the approved story allows multiple valid implementations
When sheep-spec detects a requirements fork
Then sheep-spec lists the options in open_questions
And Nicki shows each option to the human user in chat
And the human user picks one before sheep-spec writes the spec file
```

### Scenario: Acceptance test — spec on tetris ghost piece task

```gherkin
Given describe completed for NEXT_STEPS.MD ghost piece task with approved story.md
When Nicki runs spec for that task
Then sheep-spec asks via Nicki about any remaining ambiguities (e.g. alpha value, hard-drop parity checks)
And no spec file is written until those are resolved
And after resolution the spec has open_questions: []
And the pipeline reaches subtasks without running execute
And the verification worktree may be deleted if the happy path passes
```

### Scenario: Out of scope for this feature

```gherkin
Given this P1-6 story
When implementers scope the work
Then they do not implement check-gate.py or change routing.yaml in this task
And they do not add story-format.md or spec gate smoke fixtures
And harness enforcement of these rules is documented for P2 check-gate.py and P2 Nicki gate-script wiring
```
