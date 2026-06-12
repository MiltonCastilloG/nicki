# 02 — Task-spawn orchestration (no leaf commands)

Operator policy: Nicki drives the pipeline; leaf slash commands are not used. Skills remain for ad-hoc work outside the usual workflow. Baseline: slices 00–01 runtime exists (agents, commands, skills).

---

## Feature: Nicki spawns leaf subagents via Task

As a Nicki orchestrator  
I want every leaf step invoked with the Task tool and `subagent_type`  
So that workflow runs in isolated subagent contexts without slash-command routing

```gherkin
Given Nicki is the only orchestrator that may invoke other agents
And each leaf step has a matching entry under .cursor/agents/
And each leaf step has canonical workflow under .cursor/skills/
```

### Scenario: Leaf transition uses Task spawn

```gherkin
When Nicki advances a confirmed leaf step such as spec, execute, review, triage, commit, push, merge, or publish
Then Nicki invokes Task with subagent_type matching the leaf agent name
And Nicki passes worktree path, task id, status path, and prior artifact pointers in the prompt
And Nicki does not reference or require a slash command for that step
And Nicki does not execute the leaf workflow inline in the Nicki context
```

### Scenario: Status update uses Task spawn

```gherkin
When a leaf step completes and Nicki must persist workflow state
Then Nicki invokes Task with subagent_type current-task-update
And Nicki passes a compact YAML summary in the prompt
And Nicki does not call a slash command named current-task-update
```

### Scenario: Start and close use Task spawn

```gherkin
When Nicki needs a new worktree or must archive and delete a finished task
Then Nicki invokes Task with subagent_type start-task or close-task respectively
And Nicki follows the same confirmation rules as today for git and close side effects
```

---

## Feature: No leaf slash commands in operator workflow

As a workflow operator  
I want the runtime to stop treating slash commands as part of the Nicki path  
So that agents and skills are the only step definitions I maintain

```gherkin
Given the operator does not use .cursor/commands/ for pipeline steps
And Nicki orchestrates all normal workflow transitions
```

### Scenario: Leaf command files removed or archived

```gherkin
When slice 02 is implemented
Then .cursor/commands/ contains no leaf pipeline commands
  | excluded leaf commands |
  | start-task |
  | current-task-update |
  | spec-maker |
  | subtask-maker |
  | execute-plan |
  | review-execution |
  | review-triage |
  | commit-task |
  | push-task |
  | merge-task |
  | publish-task |
  | close-task |
And optional nicki command file may remain or be replaced entirely by nicki-default rule routing
```

### Scenario: Docs describe agent + skill only for steps

```gherkin
When an operator reads NICKI.md or README workflow sections
Then each pipeline step is documented as agent + skill (+ format schema)
And docs do not present slash commands as the primary or recommended invocation path
And docs state that Nicki Task-spawns leaf subagents after user confirmation
```

---

## Feature: Skills for work outside Nicki

As a workflow operator  
I want to attach or invoke skills directly when I step outside the pipeline  
So that ad-hoc help does not require fake slash commands or duplicate agent shells

```gherkin
Given .cursor/skills/ holds canonical procedures and schemas
And Nicki is not running or the operator intentionally bypasses orchestration
```

### Scenario: Manual skill use without a command

```gherkin
When the operator needs help outside the usual Nicki sequence
Then they may attach a skill such as conflict-resolution or caveman to the chat
Or ask the parent agent to read a skill path and follow it in the current context
And no matching .cursor/commands/ file is required for that skill to be usable
```

### Scenario: Shared skills stay commandless

```gherkin
Given skills exist without a dedicated subagent
  | skill | role |
  | conflict-resolution | shared merge conflict protocol |
  | next-step-spec | follow-up spec format |
  | close-scope | close helper paths |
  | task-archive | archive summary format |
  | hook-contract | hook resolution contract |
  | caveman | communication style |
When the operator or a leaf agent needs them
Then consumption is by skill path reference only
And slice 02 does not add slash commands for those helpers
```

---

## Feature: Nicki agent doc uses spawn language

As a maintainer  
I want Nicki orchestration docs free of slash-command shorthand  
So that implementers and Nicki herself do not confuse commands with Task spawn

### Scenario: nicki.md invocation section

```gherkin
Given .cursor/agents/nicki.md defines orchestration behavior
When Nicki docs describe invoking a leaf step or current-task-update
Then wording uses "invoke Task subagent_type <name>" or equivalent
And examples do not use /current-task-update or other /leaf-name prefixes as the canonical mechanism
```

### Scenario: Leaf agent docs stay thin

```gherkin
Given each .cursor/agents/<leaf>.md file
When slice 02 is complete
Then the agent file defines identity, scope, safety, and a pointer to .cursor/skills/<name>/SKILL.md
And the agent file does not duplicate the full workflow already in the skill
And the agent file does not tell the operator to run a slash command
```

---

## Feature: Parent agent routes to Nicki without command dependency

As a workflow operator  
I want to start Nicki by name or rule  
So that /nicki is optional like other leaf commands

```gherkin
Given .cursor/rules/nicki-default.mdc is always applied
And the operator may say "nicki continue" or similar at message start
```

### Scenario: Entry without slash command

```gherkin
When the user addresses Nicki by name or uses natural-language orchestration intent
Then the parent agent invokes Task with subagent_type nicki
And resume uses the prior Nicki subagent id in the same chat
And behavior does not depend on .cursor/commands/nicki.md existing
```

### Scenario: Parent does not orchestrate pipeline inline

```gherkin
When the user asks for pipeline orchestration without naming Nicki
Then the parent agent does not improvise multi-step workflow transitions
And the parent may suggest invoking Nicki rather than running leaf steps inline
```

---

## Feature: Two-layer step model in architecture docs

As a maintainer  
I want architecture docs to describe agents + skills as the runtime pair  
So that the three-layer command duplication story is retired

### Scenario: NICKI.md architecture table

```gherkin
When NICKI.md documents runtime layout
Then the canonical pattern is subagent under .cursor/agents/ plus skill under .cursor/skills/
And commands are omitted from the canonical architecture table or marked deprecated/removed
And the handoff chain, state writers, and Nicki readonly rules stay unchanged
```

### Scenario: PLAN.md and README alignment

```gherkin
When PLAN.md or README lists .cursor/ layout
Then commands directory is not listed as required for Nicki operation
And quick-start examples show Nicki Task invocation or "nicki …" routing
And step-by-step slash-command examples are removed or moved to archived operator notes
```

---

## Out of scope (slice 02)

- Changing skill workflow semantics, artifact schemas, or hook permission maps
- Removing `.cursor/agents/` — subagents remain required for Task isolation
- Auto-attaching skills during Nicki orchestration (Nicki still points leaf agents at skills via agent docs)
- Custom Cursor mode picker (future; not promised)
