---
name: execute-plan
description: "Execute a structured YAML plan inside a git worktree with strict path scope. Use when the user runs /execute-plan, asks to run a task plan in a worktree, or wants plan-driven code generation without improvisation."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: execute-plan
  tools:
    read: true
    write: true
    delete: true
    shell: true
    grep: true
    glob: true
    semantic_search: true
    task: false
    web_search: false
    web_fetch: false
    mcp: false
    ask_question: true
    todo_write: true
    generate_image: false
    switch_mode: false
---

# Execute Plan

Generate and apply code changes by following a plan **inside one worktree**. The worktree path is a hard boundary: never modify files outside it.

## When to use

- User invokes `/execute-plan` with a worktree path and a plan
- User asks to implement a pre-written plan in an isolated worktree
- A parent workflow created a worktree via `/start-task` and now needs implementation

## Required inputs

| Input | Required | Notes |
|-------|----------|-------|
| Worktree path | Yes | Absolute or repo-relative (e.g. `worktrees/hero-section`) |
| Plan | Yes | Inline YAML, `@file`, or path to a `.yaml` plan file |
| Task context | Optional | `current-task/current-task-context.yaml` when orchestrated by Nicki |

If either is missing, ask before starting.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Resolve and validate worktree scope
- [ ] Parse plan into ordered steps
- [ ] Flag ambiguous or out-of-scope steps (ask user)
- [ ] Execute steps in order
- [ ] Run verification
- [ ] Write execution handoff
- [ ] Report summary
```

### Step 1: Resolve worktree scope

1. Resolve the worktree path to an **absolute** path.
2. Confirm the directory exists and is a git worktree (or at minimum a directory the user designated).
3. Set the **scope root** to that absolute path. All subsequent work happens here.
4. Derive `<slug>` from the final folder name and set the execution handoff path to `current-task/executions/<slug>.yaml` under the scope root.
5. Load `current-task/current-task-context.yaml` when present and validate its `scope.worktree_path` matches the worktree path.

**Scope rules (non-negotiable):**

- **Create, edit, delete** files only under the scope root.
- Run shell commands with `working_directory` set to the scope root unless a plan step specifies a subdirectory (still must stay under scope root).
- Do **not** read sibling worktrees or the parent repo for the purpose of copying changes into other trees.
- Do **not** modify `.cursor/`, parent-repo config, or paths outside the scope root — even if convenient.
- Relative paths in the plan are resolved from the scope root.
- If a plan step references a path that escapes the scope root, **stop and ask** — do not proceed with that step.

### Step 2: Parse the plan

Plans are **YAML only**. Full schema and examples: [plan-format.md](plan-format.md).

Extract:

- Ordered **steps** (each with `action`, targets, and instructions)
- Optional **verify** commands at the end
- Optional **constraints** (e.g. "do not commit")
- Optional `meta.worktree` and `covers` fields for scope and requirement traceability
- Optional `meta.context` pointing to `current-task/current-task-context.yaml`

**Before executing**, check each step for:

- Missing or vague instructions ("improve the footer", "clean up code")
- Conflicting steps (create then delete same file without explanation)
- Paths outside the scope root
- Dependencies on files that do not exist (unless the step creates them)
- Commands that would write outside the scope root
- `meta.worktree` that does not match the worktree slug from the scope path
- Missing final `verify` step

If anything is unclear, **stop and ask** with a specific question. Do not guess or fill gaps with your own design choices.

### Step 3: Execute steps

Follow the plan **literally**, in order:

| Action | Meaning |
|--------|---------|
| `create` | Create the file at `path` with the described content |
| `modify` | Edit the file at `path` as described |
| `delete` | Remove the file at `path` |
| `run` | Run the given command(s) from the scope root |
| `verify` | Run check commands; report pass/fail |

**Execution discipline:**

- One plan step at a time; mark complete before moving on.
- Match existing project conventions (read surrounding code in the worktree first).
- Minimize scope — only change what the step requires.
- Do **not** add steps, refactors, tests, or docs unless the plan says so.
- Do **not** commit or push unless the plan explicitly includes a commit step **and** the user has asked for commits in their rules/message.

If a step fails (tool error, test failure, missing file), stop and report. Do not silently skip or rewrite the plan unless the user approves.

### Step 4: Verify

If the plan includes verify steps, run them from the scope root and report results.

If there are no verify steps, ask whether to run the standard checks from [CONTRIBUTING.md](../../../CONTRIBUTING.md) (`npm run lint`, `npm test`, etc.) or stop.

### Step 5: Write execution handoff

Write `current-task/executions/<slug>.yaml` under the scope root using [execution-format.md](execution-format.md).

Write this file whenever execution reaches a terminal state:

- `status: complete` when all executable plan steps finished and verification ran or was explicitly skipped by user direction.
- `status: partial` when some steps completed but the plan did not finish.
- `status: blocked` when execution cannot continue without user input, a scope decision, or a failed required command.

The handoff must include:

- `meta` with `worktree`, `generated_by: execute-plan`, `plan`, optional `spec`, optional `context`, `status`, and honored constraints.
- `paths` grouped as `created`, `modified`, `deleted`, and `unplanned`.
- `steps` mirroring the plan order with each step status.
- `verify` command evidence when verification commands ran.
- `deviations`, `open_questions`, `hotspots`, or `review_scope` when useful for review.

Keep the handoff compact. Do not include diffs, transcripts, long logs, or approval language.

### Step 6: Report

Summarize:

- Scope root used
- Steps completed (with paths touched)
- Steps skipped or blocked (with reason)
- Verification results
- Execution handoff path written
- Any questions left for the user

Remind the user to run:

```
/review-execution worktrees/<slug>
```

Replace `worktrees/<slug>` with the actual worktree path the user provided.

## Safety rules

- Never modify files outside the scope root
- Never edit `current-task/current-task-context.yaml`; Nicki updates it through `/current-task-update`
- Never force-push, `reset --hard`, or delete worktrees/branches without explicit user approval
- Do not commit or push unless the plan requires it and the user explicitly asks
- When in doubt, ask — improvisation is a last resort, not a default

## Examples

See [plan-format.md](plan-format.md) for copy-paste plan templates.
