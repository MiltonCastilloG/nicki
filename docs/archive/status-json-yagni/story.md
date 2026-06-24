# status-json-yagni — simplify per-task status.json

## Feature: Minimal status.json for routing and gates

As a Nicki operator
I want per-task status.json to hold only fields Nicki and sheep actually read
So that orchestration state stays small, single-purpose, and free of ceremony

### Background

```gherkin
Given actors are the human user, Nicki, sheep-status, and pipeline sheep
And current-task/status.json is the per-task orchestration store under each worktree
And only sheep-status writes status.json; other sheep and Nicki read via status-read.md
And handoff bodies stay in separate YAML/Markdown artifacts — status holds pointers and step position only
And status-read.md already documents the minimal read surface: task step pointers, scope.worktree_path, artifacts.*, open_questions
And check-gate.py does not exist yet — this task aligns docs and writers; harness enforcement is deferred
And priority when goals conflict is correct routing and gates, then doc alignment, then byte trimming
And constraints are no-commit and no-new-deps
And this task touches status schema docs, current-task-update skill, create-worktree scaffold, status.example.json, and task-archive sourcing — not application project code
```

### Scenario: Essential fields remain for Nicki routing

```gherkin
Given a task worktree with current-task/status.json
When Nicki or a sheep reads status for routing
Then task.current_step and task.next_step are present
And task.slug identifies the task
And scope.worktree_path resolves the worktree root
And artifacts holds paths to story, spec, subtasks, execution, review_validation, sync, integrate, and archive as they exist
And open_questions is present and empty when the pipeline may continue
And describe-to-spec gate still works via a single story pointer on disk
And spec-to-subtasks gate still reads open_questions from the spec artifact file
And post-review routing still reads readiness from artifacts.review_validation — not from status history or review markdown
```

### Scenario: Redundant duplicate pointers are collapsed

```gherkin
Given status.json before this task may duplicate the same path in multiple fields
When the simplified schema is applied
Then scope.worktree slug duplicate of task.slug is removed — slug lives under task only
And task.story_artifact duplicate of artifacts.story is removed — one canonical story pointer remains
And artifacts.status self-pointer to current-task/status.json is removed — path is implicit
And artifacts.review is removed when artifacts.review_validation is the only pointer used for review gates
And last_completed_step is removed when derivable from current_step and optional completed_steps
And readers documented in status-read.md use the surviving canonical fields only
```

### Scenario: Ceremony and double versioning are removed

```gherkin
Given status.json may carry meta.generated_by, meta.updated_by, version, and meta.schema
When the simplified schema is applied
Then meta.generated_by and meta.updated_by are dropped
And double versioning is collapsed to a single schema identifier (meta.schema only, or equivalent one field)
And constraints duplicated in spec, subtasks, and execution frontmatter are not required on status.json
And status.example.json and create-worktree.py scaffold match the simplified shape
```

### Scenario: task.original is trimmed after describe

```gherkin
Given describe completed and current-task/story.md exists on disk
When sheep-status records the describe step
Then task.original is replaced with a short label (slug or one-line title) — not the full audit prose
And the full user intent remains in story.md and archive story copy
And new worktrees may still seed task.original from the start slug until describe runs
```

---

## Feature: Trim history and source archive process elsewhere

As a Nicki operator
I want status.json history to stop duplicating handoff YAML summaries
So that disk stays small and archive process lines come from authoritative artifact files

### Background

```gherkin
Given verbose history[] has been the main YAGNI offender in long-running tasks
And history duplicates summaries already in spec, execution, review-validation, and integrate handoffs
And status-read.md does not list history as a field Nicki uses for gates
And task-archive currently loads history for report.yaml process section
And archive-format.md documents process as step plus one-line summary
```

### Scenario: History is dropped or reduced to completed step names

```gherkin
Given a task progresses through spec, subtasks, execute, and review
When sheep-status updates status.json after each step
Then status.json does not append verbose history events with artifact summaries
And either history is omitted entirely
Or status keeps only completed_steps as a string array of step names (e.g. ["start", "describe", "spec"])
Or status keeps at most one optional last_event one-liner without duplicating handoff bodies
And current-task-update SKILL.md documents the chosen shape and sheep-status write rules
```

### Scenario: Archive process is sourced from artifact files

```gherkin
Given close-task runs task-archive for a completed task
When report.yaml process section is drafted
Then process steps are derived from artifact presence and handoff meta under current-task/ — not from status.json history[]
And each process entry remains step plus one-line summary per archive-format.md
And report.yaml still includes task, story, outcome, decisions, open_questions, and suggestions
And archived story.md is still copied from artifacts.story
```

### Scenario: Existing tasks can migrate on next status update

```gherkin
Given an in-flight worktree still has legacy history[] and duplicate pointers
When sheep-status next writes that status.json
Then the writer emits the simplified shape
And essential routing fields and artifact pointers are preserved
And verbose history is not copied forward
```

---

## Feature: Docs and examples stay aligned

As a Nicki operator
I want one documented minimal status shape
So that readers, scaffolds, and status-update behave consistently

### Scenario: status-format.md matches status-read.md minimal shape

```gherkin
When an implementer reads status-format.md and status-read.md
Then both describe the same canonical fields and gates
And history is optional or absent per the trimmed design
And review_validation is documented as the sole review gate pointer
And the full JSON example in status-format.md reflects the simplified schema
```

### Scenario: Out of scope for this task

```gherkin
Given this chore scopes YAGNI simplification only
When implementers plan work
Then they do not implement check-gate.py or change routing.yaml gates in this task
And they do not add new dependencies
And global-status.json registry shape is unchanged unless a field directly duplicates per-task status
```

### Scenario: Acceptance — dogfood status-json-yagni worktree

```gherkin
Given this task's own worktree at worktrees/nicki-status-json-yagni
When describe completes with approved story.md
And spec, subtasks, and execute update status through the pipeline
Then status.json in that worktree uses the simplified schema throughout
And no reader documented in status-read.md breaks
And task-archive can produce report.yaml process without status history[]
And the verification run may stop after subtasks or execute without integrate when used as a harness check
```
