# 03 — Skills lock + sheep agents

Operator policy: skills are portable manuals users attach for ad-hoc work; sheep are Nicki-only workflow binders loaded in isolated Task context. Baseline: slices 00–02 (JSON status, commandless Task-spawn orchestration).

---

## Feature: Pipeline skills unlocked for users

As a workflow operator  
I want to attach pipeline skills directly in chat  
So that I can run one job outside the full Nicki sequence without a sheep spawn

```gherkin
Given user-facing pipeline skills exist under .cursor/skills/
And workflow-only skills stay internal to Nicki and sheep
```

### Scenario: User-facing skills have model invocation enabled

```gherkin
When slice 03 Phase 1 is implemented
Then these skills do NOT set disable-model-invocation: true
  | skill |
  | spec-maker |
  | subtask-maker |
  | execute-plan |
  | review-execution |
  | start-task |
  | sync-task |
  | integrate-task |
  | conflict-resolution |
And none of them declare metadata.subagent in frontmatter
```

### Scenario: Workflow-only skills stay locked

```gherkin
When slice 03 Phase 1 is implemented
Then these skills keep disable-model-invocation: true
  | skill |
  | current-task-update |
  | close-task |
  | close-scope |
  | task-archive |
  | hook-contract |
  | validation |
  | caveman |
And users invoke them only via sheep or Nicki orchestration, not as ad-hoc attachments
```

### Scenario: Skills README states invocation policy

```gherkin
When an operator reads .cursor/skills/README.md
Then the doc describes three layers: skill, sheep, Nicki
And it states users attach skills for ad-hoc work
And it states only Nicki Task-spawns sheep-* subagents
And it states the parent agent must not send sheep
And leaf skills must not reference status.json or pipeline step names
```

---

## Feature: Sheep agents with Nicki voice

As Nicki orchestrator  
I want thin sheep agents that bind disk paths to skills  
So that isolated child contexts load inputs and return compact YAML without choosing workflow

```gherkin
Given each pipeline step has a matching sheep under .cursor/agents/sheep-*.md
And each sheep points at one or more skills under .cursor/skills/
```

### Scenario: Sheep body and description pattern

```gherkin
When a maintainer opens any sheep agent file
Then frontmatter description matches "Nicki sheep. Path only. Skill: …" or "Skills: …"
And the body opens with "You are a sheep. Nicki sent you."
And the body lists disk inputs, output paths, scope rules, and safety rules
And the body does not duplicate the full skill procedure checklist
```

### Scenario: Legacy leaf agents removed

```gherkin
When slice 03 Phase 2 is implemented
Then .cursor/agents/ contains no files named
  | removed agent |
  | start-task.md |
  | spec-maker.md |
  | subtask-maker.md |
  | execute-plan.md |
  | review-execution.md |
  | sync-task.md |
  | integrate-task.md |
  | close-task.md |
  | current-task-update.md |
  | commit-task.md |
  | push-task.md |
  | merge-task.md |
  | publish-task.md |
  | review-triage.md |
And sheep-* agents exist for start, spec, subtask, execute, review, sync, integrate, close, and status
```

---

## Feature: Nicki routes via routing.yaml and sheep map

As Nicki orchestrator  
I want an authoritative routing file instead of reading sheep agent docs  
So that transitions, gates, and artifacts stay in one place

```gherkin
Given .cursor/skills/nicki/routing.yaml exists
And nicki.md references routing.yaml as authoritative
And Nicki does not read .cursor/agents/sheep-*.md
```

### Scenario: routing.yaml uses sheep keys

```gherkin
When Nicki resolves a pipeline step
Then routing.yaml steps.*.sheep names a sheep-* subagent_type or null for Nicki-only steps
And status_update.sheep is sheep-status
And sheep_return_contract defines required YAML fields for sheep → sheep-status handoff
And readiness_routing maps validation readiness to acceptance, execute fix loop, or blocked
And git tail steps are sync then integrate then close — not commit, push, merge, publish
```

### Scenario: Nicki sheep map and confirmations

```gherkin
When Nicki docs describe the pipeline
Then nicki.md lists subagent_type sheep-start through sheep-close plus sheep-status after each sheep
And Nicki-only steps describe, acceptance, and fix are documented separately
And sync and integrate require explicit user confirmation naming git side effects
And close requires archive and worktree delete confirmation
```

---

## Feature: Simplified git tail (sync + integrate)

As a workflow operator  
I want two git steps instead of four  
So that feature-branch sync and main integration are clear and confirmable

```gherkin
Given commit-task, push-task, merge-task, and publish-task are retired
And sync-task and integrate-task skills replace them
```

### Scenario: Sync skill and sheep-sync

```gherkin
When readiness allows sync after user acceptance
Then Nicki sends sheep-sync
And sheep-sync loads sync-task skill and conflict-resolution when needed
And sync-task commits locally, merges main into feature branch, pushes feature branch
And output is current-task/syncs/<slug>.yaml handoff YAML
```

### Scenario: Integrate skill and sheep-integrate

```gherkin
When sync handoff exists and user confirms merge into main
Then Nicki sends sheep-integrate
And sheep-integrate loads integrate-task skill and conflict-resolution when needed
And integrate-task merges feature into main and pushes main
And output is current-task/integrates/<slug>.yaml in the task worktree
```

---

## Feature: Validation folded into review spawn

As a workflow operator  
I want review and validation in one sheep-review step  
So that readiness routing and next-steps do not require a separate triage agent

```gherkin
Given review-triage skill and agent are removed
And validation skill lives under .cursor/skills/validation/
```

### Scenario: sheep-review loads review and validation

```gherkin
When Nicki sends sheep-review after execute
Then sheep-review loads review-execution SKILL and validation-format.md
And review-execution procedure includes validation per validation-format.md
And outputs include current-task/reviews/<slug>.yaml and review-validations/rN-validation.yaml
And optional current-task/next-steps/*.yaml for deferred scope findings
And fix_required appends ## Fix to subtasks without mutating prior - [x] lines
```

### Scenario: Nicki routes from validation not review prose

```gherkin
When review completes
Then Nicki reads validation YAML readiness.status only for acceptance, fix, or blocked routing
And sync is blocked when readiness is fix_required or blocked
And spec open_questions gate still blocks subtasks before execute
```

---

## Feature: Pure skills without pipeline leakage

As a maintainer  
I want leaf skills to describe one job only  
So that the same skill works ad-hoc and inside sheep without orchestration knowledge

```gherkin
Given .cursor/skills/README.md pure-functionality rules
And sheep own disk auto-load paths and Nicki handoff expectations
```

### Scenario: Leaf skills accept prompt inputs

```gherkin
When a pipeline skill SKILL.md describes inputs
Then inputs are worktree path, artifact paths, or inline YAML from the sheep prompt
And the skill does not instruct "update status.json" or "spawn next agent"
And format files document one artifact type without multi-agent directory maps
```

### Scenario: Subtask-maker load trimmed

```gherkin
When subtask-maker runs inside sheep-subtask
Then it reads spec via spec-input.md for read-only fields and open_questions gate
And it does not require full spec-format.md or caveman skill in its load list
And subtask-format.md carries lite voice rules inline
```

---

## Feature: Write boundaries name sheep writers

As a maintainer  
I want explicit JSON write boundaries  
So that registry and per-task status cannot be corrupted by wrong sheep

```gherkin
Given global-status.json and current-task/status.json are authoritative orchestration stores
```

### Scenario: Registry writers

```gherkin
When global-status-format.md documents write boundary
Then only sheep-start may register and sheep-close may unregister global-status.json
And sheep-status and other pipeline sheep must not write global-status.json
And close-scope documents sheep-close as the registry mutator during teardown
```

### Scenario: Per-task status writer

```gherkin
When status-format.md documents write boundary
Then only sheep-status writes current-task/status.json
And Nicki and other sheep read status only
And sheep-status loads current-task-update skill and never writes other artifacts
```

---

## Feature: Docs and permissions align with sheep model

As a workflow operator  
I want README and NICKI to match runtime layout  
So that I know when to say nicki versus attach a skill

```gherkin
Given README.md, NICKI.md, and complexity.md describe the post-slice runtime
```

### Scenario: Parent routes to Nicki not sheep

```gherkin
When the user addresses Nicki by name
Then parent agent Task-spawns subagent_type nicki per nicki-default.mdc
And README and NICKI state ad-hoc work uses skills — parent must not Task-spawn sheep-*
And Nicki sends sheep one at a time with user confirmation before each step
```

### Scenario: Hook permissions match sheep names

```gherkin
When agent-permissions.json is loaded for a sheep run
Then keys use sheep-* names (sheep-start, sheep-spec, sheep-sync, sheep-integrate, …)
And commit-task, push-task, merge-task, and publish-task keys are absent
And sheep-sync and sheep-integrate grant shell for git operations
```

### Scenario: Construction reports relocated

```gherkin
When slice 03 completes
Then report.md and report-2.md live under nicki-contruction/ not repo root
And complexity.md scores sheep-* agents with line counts and load-trim notes
```

---

## Out of scope (slice 03)

- Renaming skill folder names (subtask-maker, execute-plan, etc. keep legacy names)
- Auto-attaching skills during Nicki orchestration (sheep still point at skills via agent docs)
- Nicki custom Cursor mode picker (deferred)
- Host application feature code outside Nicki runtime bundle
