# Status architecture task — Gherkin user stories

Draft task definition for replacing `current-task-context.yaml` with JSON status files and adding a workspace-level registry. Pick scope from here for `/start-task`, `/spec-maker`, or manual implementation.

---

## Feature: Workspace task registry (`global-status.json`)

As a Nicki workflow operator  
I want a workspace-root registry of active tasks  
So that hooks and Nicki can resolve a task id to project, worktree, and per-task status without reading chat memory

### Background

```gherkin
Given the Nicki workspace root contains global-status.json
And global-status.json is the only workspace-level task index
And global-status.json is written only at task start and task close
And per-task workflow state lives in each task's status.json
And step handoff artifacts remain YAML/Markdown under current-task/
```

### Scenario: Register a new task at start

```gherkin
Given no active task exists with id "42"
When start-task creates worktree "projects/castlemill-landing/worktrees/hero-section"
And start-task initializes per-task status at "projects/castlemill-landing/worktrees/hero-section/current-task/status.json"
Then global-status.json gains an entry for task "42"
And the entry includes project "castlemill-landing"
And the entry includes slug "hero-section"
And the entry includes worktree_path "projects/castlemill-landing/worktrees/hero-section"
And the entry includes status_path "projects/castlemill-landing/worktrees/hero-section/current-task/status.json"
And global-status.json may set active_task to "42"
And no leaf step other than start-task or close-task modifies global-status.json
```

### Scenario: Resolve task by id for a hook

```gherkin
Given global-status.json contains task "42"
And Nicki or a hook knows task id "42"
When a post-step hook reads global-status.json
Then it can resolve status_path without parsing YAML
And it can resolve project and worktree_path programmatically
And it can read current_step and next_step from the per-task status.json at status_path
```

### Scenario: Unregister task at close

```gherkin
Given task "42" is registered in global-status.json
And the task worktree has been merged, published, and archived
When close-task completes successfully
Then task "42" is removed from global-status.json or marked closed per schema
And active_task is cleared or points to another open task
And the archived task report preserves enough context to reconstruct the task without global-status.json
```

### Scenario: Multiple concurrent tasks

```gherkin
Given tasks "41" and "42" are both registered in global-status.json
When a hook receives explicit task id "42"
Then it reads only the status_path for task "42"
And it does not infer task id from chat transcript
And global-status.json lists both tasks with distinct project, slug, worktree_path, and status_path
```

---

## Feature: Per-task workflow status (`status.json`)

As a Nicki orchestrator  
I want per-task status in JSON inside the active worktree  
So that step pointers, artifact paths, and blockers survive compaction and are easy for hooks to parse

### Background

```gherkin
Given each active task has current-task/status.json
And status.json replaces the role of current-task/current-task-context.yaml
And only status-update (formerly current-task-update) writes status.json
And Nicki and leaf agents may read status.json but must not edit it directly
And long narrative content such as task.story stays in artifacts, not inlined in status.json when possible
```

### Scenario: Initialize per-task status after start

```gherkin
Given start-task created worktree "projects/castlemill-landing/worktrees/hero-section"
When the first status update runs after start
Then current-task/status.json exists
And status.json records slug "hero-section"
And status.json records current_step "start" or "describe"
And status.json records next_step "describe" or "spec" per workflow rules
And status.json records artifact pointers for context, spec, subtasks, execution, review, triage, commit, push, merge, publish, and archive when known
And status.json records open_questions as an empty array when unblocked
And status.json records append-only history for workflow events
```

### Scenario: Update status after each workflow step

```gherkin
Given an active task with current-task/status.json
When a leaf step such as spec-maker, execute-plan, or review-triage completes
And Nicki invokes status-update with a compact summary
Then status.json updates current_step, next_step, and last_completed_step
And status.json updates artifact paths for the completed step
And status.json appends one history event with step, status, artifact, and summary
And global-status.json is not modified during this update
```

### Scenario: Nicki resumes from disk after compaction

```gherkin
Given chat memory of current_step is lost after compaction
And global-status.json points to the task's status_path
When Nicki activates for task "42"
Then Nicki reads global-status.json first when task id is known
Or Nicki reads status_path from global-status.json before any leaf transition
And Nicki derives workflow position only from status.json fields and artifact evidence
And Nicki does not trust chat for current_step, next_step, or git-transition consent
```

### Scenario: Blocked task records open questions

```gherkin
Given spec-maker or subtask-maker stops for user input
When Nicki invokes status-update with completed_status blocked
Then status.json records non-empty open_questions
And status.json sets next_step to the blocked step or fix step as defined by Nicki rules
And downstream agents do not proceed until open_questions is empty or user overrides explicitly
```

---

## Feature: Hook integration after task id is known

As a workflow automation author  
I want hooks to read JSON status by task number  
So that programmatic follow-up does not depend on YAML parsers or chat state

### Background

```gherkin
Given hooks exchange JSON with Cursor
And hooks run after Nicki knows the task id
And global-status.json lives at the workspace root
And per-task status.json lives at the path referenced by global-status.json
```

### Scenario: Hook loads task route from global registry

```gherkin
Given task id "42"
When a hook executes jq against global-status.json
Then it obtains status_path, project, slug, and worktree_path for task "42"
And it can open current-task/status.json without searching the filesystem
```

### Scenario: Hook reads readiness and next step

```gherkin
Given per-task status.json records next_step "triage"
And review-validations artifact includes readiness routing when implemented
When the hook reads status.json and the latest validation artifact path from status.json
Then it can determine whether to chain execute, review, acceptance, commit, or fix loop
And it does not need to parse current-task-context.yaml
```

---

## Feature: Replace current-task-context.yaml

As a Nicki maintainer  
I want a single clear source of truth for orchestration state  
So that global indexing and per-task step state do not compete or drift

### Background

```gherkin
Given the current runtime treats current-task/current-task-context.yaml as canonical
And the target runtime treats global-status.json plus per-task status.json as canonical
And YAML artifacts under current-task/ remain step handoffs, not global authority
```

### Scenario: Deprecate context YAML in runtime docs and agents

```gherkin
Given the status migration is implemented
When an agent or skill references workflow state
Then it reads global-status.json and/or current-task/status.json
And it does not write current-task/current-task-context.yaml
And meta.context in handoff artifacts points to current-task/status.json when present
And NICKI.md, nicki.md, and status-update skill document the new model explicitly
```

### Scenario: Preserve artifact chain while changing state model

```gherkin
Given status.json stores pointers, not full handoff bodies
When spec-maker writes current-task/specs/<slug>.yaml
And subtask-maker writes current-task/subtasks/<slug>.md
And execute-plan writes current-task/executions/<slug>.yaml
Then status.json records paths to those artifacts
And downstream agents still consume prior artifacts plus status.json
And the handoff chain remains inspectable on disk
```

---

## Feature: Global vs per-task write boundaries

As a workflow designer  
I want strict write permissions on status files  
So that hooks always see a stable registry and step updates do not corrupt task indexing

### Scenario: Only start-task writes global registry on create

```gherkin
When start-task succeeds
Then start-task may append or update global-status.json
And start-task creates initial per-task status.json
And no other agent modifies global-status.json during create
```

### Scenario: Only close-task writes global registry on teardown

```gherkin
When close-task succeeds after archive write
Then close-task removes or closes the task entry in global-status.json
And close-task deletes the task worktree after archive confirmation when close policy requires it
And status-update never deletes global-status.json entries
```

### Scenario: status-update writes only per-task status.json

```gherkin
When Nicki completes describe, spec, subtasks, execute, review, triage, commit, push, merge, publish, or fix routing
Then status-update writes only current-task/status.json under the task worktree
And status-update never writes global-status.json
And Nicki never writes status files directly
```

---

## Feature: Standalone workspace path model

As a multi-project Nicki operator  
I want status paths to follow project-local worktrees  
So that one workspace can orchestrate many repositories safely

### Background

```gherkin
Given the target layout is projects/<project>/worktrees/<slug>
And global-status.json lives at the Nicki workspace root
And archives live per project unless centralized later
```

### Scenario: Global registry records project and worktree

```gherkin
Given task "42" belongs to project "castlemill-landing"
When the task is registered
Then global-status.json stores project "castlemill-landing"
And global-status.json stores worktree_path "projects/castlemill-landing/worktrees/hero-section"
And status_path remains inside that worktree under current-task/status.json
```

---

## Feature: Readiness and routing in status artifacts

As Nicki  
I want deterministic post-triage routing  
So that acceptance, fix loop, and commit transitions do not rely on inference alone

### Scenario: Triage writes readiness consumed via status pointers

```gherkin
Given review-triage completes
When validation artifact includes readiness status and recommended_next_step
Then status.json records the latest review_validation artifact path
And Nicki uses validation readiness plus status.json next_step to propose acceptance, fix loop, or commit
And hooks may read readiness indirectly via status.json artifact pointers
```

### Scenario: Fix loop appends subtasks without resetting global registry

```gherkin
Given triage returns fix_required for in-scope findings
When Nicki routes back through subtask append and execute-plan
Then per-task status.json updates steps and artifact pointers
And global-status.json remains unchanged except at start or close
```

---

## Feature: Close, archive, and preserved report

As a task operator  
I want close to preserve enough task history before deleting the worktree  
So that specs and decisions are not lost when the task worktree is removed

### Scenario: Close archives before destructive cleanup

```gherkin
Given merge and publish handoffs exist or user recorded explicit override
When close-task runs
Then a durable archive/report is written before worktree deletion
And the archive preserves story, spec, subtasks summary, execution summary, review, triage, git outcomes, acceptance, next-step specs, and close notes
And global-status.json is updated to unregister the task
And the whole task worktree may be deleted only after archive write succeeds
```

---

## Proposed file shapes (informative)

These are draft shapes for spec-maker; not implemented yet.

### `global-status.json` (workspace root)

```json
{
  "version": 1,
  "active_task": "42",
  "tasks": {
    "42": {
      "project": "castlemill-landing",
      "slug": "hero-section",
      "worktree_path": "projects/castlemill-landing/worktrees/hero-section",
      "status_path": "projects/castlemill-landing/worktrees/hero-section/current-task/status.json"
    }
  }
}
```

### `current-task/status.json` (per task)

```json
{
  "version": 1,
  "task": {
    "id": "42",
    "slug": "hero-section",
    "project": "castlemill-landing",
    "original": "hero-section",
    "story_artifact": "current-task/story.md",
    "type": "feature",
    "current_step": "spec",
    "next_step": "subtasks",
    "last_completed_step": "describe"
  },
  "scope": {
    "worktree_path": "projects/castlemill-landing/worktrees/hero-section"
  },
  "artifacts": {
    "status": "current-task/status.json",
    "spec": "current-task/specs/hero-section.yaml",
    "subtasks": "current-task/subtasks/hero-section.md"
  },
  "open_questions": [],
  "history": [
    {
      "step": "start",
      "status": "complete",
      "artifact": "current-task/status.json",
      "summary": "Worktree created and task registered."
    }
  ]
}
```

---

## Suggested implementation slices (pick one or combine)

### Slice A — Schema and docs only

- Define `global-status.json` and `current-task/status.json` schemas
- Update NICKI.md and nicki.md bootstrap rules
- No runtime agent changes yet

### Slice B — Global registry at start/close

- `start-task` registers task in `global-status.json`
- `close-task` unregisters task from `global-status.json`
- Per-task status still minimal or stubbed

### Slice C — Replace context YAML with status.json

- Rename/repurpose `current-task-update` → status writer for `current-task/status.json`
- Update all agent/skill reads from `current-task-context.yaml` to `status.json`
- Remove or stop writing context YAML

### Slice D — Hook path

- Document hook contract: task id → `global-status.json` → `status_path` → `status.json`
- Add example hook script using `jq`

### Slice E — Full migration

- Slices A + B + C + D
- Readiness pointers, acceptance step, publish step, and close/archive alignment from report.md

---

## Out of scope (unless explicitly added)

- Replacing YAML spec/review/execution handoffs with JSON
- Making hooks write global-status.json during leaf steps
- Deleting remote task branches automatically at close
- Requiring CONTRIBUTING.md for status migration

---

## Open questions

1. Should task id be numeric only, or numeric plus slug in global-status.json?
2. Should `active_task` live in global-status.json when multiple tasks can be open?
3. Should `story` stay inline in status.json or always move to `current-task/story.md`?
4. Should global-status.json file name be `global-status.json` or root `status.json`? This draft uses **`global-status.json`** for the registry and **`current-task/status.json`** per task to avoid one name meaning two things.
5. Should close delete the whole worktree immediately, or only after archive verification and explicit confirmation?

---

## Acceptance (when this task is done)

- A hook with task id can resolve project, worktree, and per-task status using JSON only
- Global registry changes only at start and close
- Per-task status changes after every orchestrated step except close deletion
- Nicki bootstrap uses disk status, not chat memory
- Runtime docs no longer describe `current-task-context.yaml` as canonical authority
- Existing YAML artifact chain still works with status.json as pointer layer
