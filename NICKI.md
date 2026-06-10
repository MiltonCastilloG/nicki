# Nicki — workflow orchestrator context

**Nicki is a good dog.**

Nicki is the read-only orchestrator for the CastleMill current-task pipeline. Nicki controls workflow order, not implementation. Nicki asks before each leaf-agent transition, invokes the correct subagent, passes prior inputs and outputs, and calls `/current-task-update` after every step — except close, which deletes the task context folder.

Use this document as a rebuild guide: what Nicki is, what it controls, how the pieces fit together, and the key decisions that shaped the design.

---

## What Nicki does

| Nicki does | Nicki does not |
| ---------- | -------------- |
| Read workflow docs, `current-task/current-task-context.yaml`, and task artifacts | Write files |
| Invoke leaf subagents via the Task tool | Run shell commands |
| Ask for confirmation before each transition | Search or edit application source |
| Pass worktree path, context, and prior artifacts to leaf agents | Improvise workflow transitions |
| Call `/current-task-update` automatically after each leaf step (except close) | Spawn nested subagents from leaf workers |
| Track orchestration progress with todos | Commit, push, merge, or delete without explicit user confirmation |

Nicki is defined in `.cursor/agents/nicki.md`. It is a top-level subagent with `readonly: true` and a tightly scoped tool matrix: `read`, `task`, `ask_question`, and `todo_write` only.

---

## Architecture (three layers)

Every workflow step follows the same pattern:

| Layer | Path | Role |
| ----- | ---- | ---- |
| Subagent | `.cursor/agents/<name>.md` | Isolated execution; Cursor frontmatter: `name`, `description`, `model`, `readonly`, `is_background` |
| Command | `.cursor/commands/<name>.md` | Slash command — launches the subagent, not inline parent work; frontmatter: `name`, `description` |
| Skill | `.cursor/skills/<name>/` | Workflow instructions, `metadata.tools`, and format schemas |

**Frontmatter parsing:** Cursor uses a simplified YAML parser. Use single-line quoted `description: "..."` strings — do not use block scalars (`>-`, `>`, `|`) or the description may truncate to the first line only.

**Leaf workers** have `task: false` — they never delegate to other agents. Nicki is the only orchestrator; it invokes leaf agents one at a time.

**State writer** is a dedicated leaf agent: `/current-task-update` is the only writer for `current-task/current-task-context.yaml`. Nicki never writes that file directly.

---

## Canonical workflow

Nicki knows this step sequence:

```
start → describe → spec → subtasks → execute → review → triage → [fix loop] → commit → push → merge → close
```

With automatic context updates after each leaf step:

```
start-task
current-task-update
describe              ← Nicki-only: ask if needed, draft Gherkin user story, persist task.story
current-task-update
spec-maker
current-task-update
subtask-maker
current-task-update
execute-plan
current-task-update
review-execution
current-task-update
review-triage
current-task-update
commit-task          ← user confirmation required
current-task-update
push-task              ← user confirmation required
current-task-update
merge-task             ← user confirmation required
current-task-update
close-task             ← "Time for the feedback woof! Want?"
```

The `fix` step is not a separate agent. When review or triage surfaces blockers, Nicki asks whether to regenerate subtasks, execute remaining subtasks, rerun review with guidance, or start a follow-up task.

```mermaid
flowchart LR
  A[start-task] --> B[current-task-update]
  B --> C[describe]
  C --> D[current-task-update]
  D --> E[spec-maker]
  E --> F[current-task-update]
  F --> G[subtask-maker]
  G --> H[current-task-update]
  H --> I[execute-plan]
  I --> J[current-task-update]
  J --> K[review-execution]
  K --> L[current-task-update]
  L --> M[review-triage]
  M --> N[current-task-update]
  N --> O{ready?}
  O -->|blockers| P[fix loop]
  P --> G
  O -->|ready| Q[commit-task]
  Q --> R[current-task-update]
  R --> S[push-task]
  S --> T[current-task-update]
  T --> U[merge-task]
  U --> V[current-task-update]
  V --> W[close-task]
  W --> X[task-archive]
```

---

## Leaf agents and artifacts

Each leaf agent produces a YAML handoff. Artifacts live under `worktrees/<slug>/current-task/` during the active task.

| Step | Command | Writes code? | Primary output |
| ---- | ------- | ------------ | -------------- |
| Setup | `/start-task` | No | `worktrees/<slug>/` |
| State | `/current-task-update` | No (context YAML only) | `current-task/current-task-context.yaml` |
| Describe | Nicki (no command) | No | `task.story` in context (Gherkin user story) |
| Spec | `/spec-maker` | No | `current-task/specs/<slug>.yaml` |
| Subtasks | `/subtask-maker` | No | `current-task/subtasks/<slug>.md` |
| Execute | `/execute-plan` | Yes | Code changes + updated subtasks + `current-task/executions/<slug>.yaml` |
| Review | `/review-execution` | No | `current-task/reviews/<slug>.yaml` |
| Triage | `/review-triage` | No | `current-task/review-validations/rN-validation.yaml` |
| Commit | `/commit-task` | Yes (git commit only) | Local commit + `current-task/commits/<slug>.yaml` |
| Push | `/push-task` | Yes (pre-push merge + push) | Remote branch + `current-task/pushes/<slug>.yaml` |
| Merge | `/merge-task` | Yes (merge into `main`) | Merge result + `current-task/merges/<slug>.yaml` |
| Close | `/close-task` | Yes (archive + delete) | `task-archive/<slug>/summary.yaml`, then deletes `current-task/` |

### Artifact handoff chain

```
spec ──→ subtasks ──→ execution ──→ review ──→ validation
                                                   ├── next-steps/*.yaml  (follow-up specs for subtask-maker)
                                                   └── review-inputs/rN-review.yaml  (guidance for review rerun)
commit ──→ push ──→ merge ──→ archive
```

- **Spec** defines *what* to build — requirements, scope, acceptance. No file paths.
- **Subtask list** breaks spec into one-sentence build items with checkbox completion state (tests included).
- **Execute-plan** implements unchecked subtasks in order and marks each `- [x]` in place.
- **Execution** is an evidence map for review, not an approval.
- **Review** has exactly `approved` and `content`.
- **Triage** filters review findings against task scope; out-of-scope work becomes next-step specs.
- **Commit / push / merge** are separate, explicit git steps with their own handoff YAML.
- **Archive** is a compact root-level summary; the full `current-task/` tree is deleted after close.

Closed tasks are stored at:

```
task-archive/<slug>/summary.yaml
```

---

## State model: `current-task-context.yaml`

The canonical task-local state file lives inside the worktree at `current-task/current-task-context.yaml`.

**Only `/current-task-update` writes this file.** Nicki and all leaf agents may read it; leaf agents must not edit it.

### What it stores

| Section | Purpose |
| ------- | ------- |
| `task` | Identity + step pointers: `current_step`, `next_step`, `last_completed_step`, `story` (Gherkin user story) |
| `scope` | Worktree slug and path — hard scope boundary |
| `artifacts` | Paths to all known handoff files |
| `open_questions` | Blockers; empty list means Nicki can continue |
| `history` | Append-only workflow events |

### What it deliberately omits

There is **no broad task-level `state` enum**. Step pointers, `open_questions`, and `history[].status` are the source of truth. This avoids redundant state that could drift from reality.

### Step values

`start`, `describe`, `spec`, `subtasks`, `execute`, `review`, `triage`, `fix`, `commit`, `push`, `merge`, `close`, `done`

Schema: `.cursor/skills/current-task-update/current-task-context-format.md`

### Nicki summary → context update

After each leaf step, Nicki calls `/current-task-update` with a compact summary (no separate user confirmation needed):

```yaml
worktree: worktrees/hero-section
completed_step: spec
completed_status: complete
artifact: current-task/specs/hero-section.yaml
next_step: subtasks
open_questions: []
summary: Spec captured requirements and acceptance criteria.
```

Exception: **do not call `/current-task-update` after `/close-task`** — close deletes `current-task/`.

---

## Transition discipline

Before invoking any leaf agent except `/current-task-update`, Nicki shows a compact state view and asks for confirmation:

```markdown
Current task: `hero-section` — Hero section redesign
Progress: `describe` → `spec` → `subtasks`
Next action: invoke `spec-maker`
Expected output: `current-task/specs/hero-section.yaml`
```

If the user declines, Nicki stops.

### Git side effects require explicit confirmation

| Agent | Must name this side effect |
| ----- | -------------------------- |
| `commit-task` | Creating a local git commit |
| `push-task` | Merging `main` into the task branch, resolving conflicts only with user input, and pushing to remote |
| `merge-task` | Merging the pushed task branch into `main` |

### Close requires the feedback prompt

Before `/close-task`, Nicki asks exactly:

```text
Time for the feedback woof! Want?
```

And shows:

- Archive output: `task-archive/<slug>/summary.yaml`
- Delete scope: `<worktree>/current-task/`

---

## Key design decisions

These decisions are load-bearing. Changing them requires updating Nicki, leaf agents, and docs together.

### 1. Nicki is read-only; state has a dedicated writer

Nicki orchestrates but never writes files. A separate `/current-task-update` agent is the sole writer for `current-task-context.yaml`. This prevents the orchestrator from accidentally corrupting workflow state while improvising.

### 2. Leaf agents are atomic; no nested delegation

Every workflow step agent has `task: false`. Nicki is the only agent that invokes other agents. This keeps scope, permissions, and accountability clear.

### 3. Commands launch subagents, not inline parent work

Each `/command` delegates to an isolated subagent context. The parent agent (including Nicki when invoking via Task) passes the prompt and does not execute the workflow inline.

### 4. YAML handoffs between steps, not chat memory

Each step produces a compact YAML artifact. Downstream agents consume prior artifacts plus `current-task-context.yaml`. This makes the pipeline reproducible and inspectable outside the chat transcript.

### 5. No broad state enum — step pointers + open questions

Instead of a `state: in_progress | blocked | done` field, the context file uses `current_step`, `next_step`, `last_completed_step`, and `open_questions`. Blockers live in `open_questions`; history is append-only.

### 6. Worktree path is the hard scope boundary

All task work happens inside `worktrees/<slug>/`. `/execute-plan` treats the worktree as a hard boundary — no edits outside it. Nicki validates that the requested worktree matches `scope.worktree_path` in context.

### 7. Git workflow: never touch `main` until merge

Task work runs on a feature branch in an isolated worktree. The sequence is:

1. **Commit** — local commit on the task branch (`/commit-task`)
2. **Push** — merge `main` into the task branch, resolve conflicts with user input, push (`/push-task`)
3. **Merge** — merge the pushed task branch into `main` (`/merge-task`); this is the **first step that touches `main`**

Merge is **mandatory**, not optional. Commit and push are intentionally separate so publishing remains an explicit step after local review.

### 8. Shared conflict-resolution protocol

`/push-task` and `/merge-task` both reference `.cursor/skills/conflict-resolution/SKILL.md`. Agents summarize conflicts but must ask the user for every resolution. No inferring, no strategy flags unless the user explicitly asks.

### 9. Automatic context update after every step — except close

`/current-task-update` runs automatically after each leaf step without asking. The one exception is `/close-task`, which deletes `current-task/` and therefore cannot be followed by a context write.

### 10. Close archives compactly, then deletes task context

`/close-task` writes `task-archive/<slug>/summary.yaml` at the repository root with compact context, process, decisions, open questions, and suggestions for smoother future tasks. It does **not** copy the full artifact tree. Then it deletes `<worktree>/current-task/`.

### 11. Spec/subtask/execution separation

- **Spec-maker** defines requirements — no file paths, no implementation subtasks.
- **Subtask-maker** maps requirements to one-sentence checklist items, including tests and verification.
- **Execute-plan** follows unchecked subtasks in order, marks completed items `- [x]`, and asks on ambiguity.
- **Review-execution** independently inspects the diff; execution YAML is a map, not an approval.

### 12. Review triage filters scope

Review findings that are valid but out-of-scope become `current-task/next-steps/*.yaml` specs (consumable by subtask-maker). Invalid reviews produce `current-task/review-inputs/rN-review.yaml` guidance for a rerun.

---

## File map for rebuilding

### Orchestrator

| File | Role |
| ---- | ---- |
| `.cursor/agents/nicki.md` | Nicki subagent definition |
| `NICKI.md` | This context overview |

### State

| File | Role |
| ---- | ---- |
| `.cursor/agents/current-task-update.md` | State writer subagent |
| `.cursor/commands/current-task-update.md` | `/current-task-update` command |
| `.cursor/skills/current-task-update/SKILL.md` | State writer workflow |
| `.cursor/skills/current-task-update/current-task-context-format.md` | Context schema |

### Leaf agents (agent + command + skill + format)

| Step | Agent | Command | Skill | Format schema |
| ---- | ----- | ------- | ----- | ------------- |
| Start | `start-task.md` | `start-task.md` | `start-task/SKILL.md` | — |
| Spec | `spec-maker.md` | `spec-maker.md` | `spec-maker/SKILL.md` | `spec-format.md` |
| Subtasks | `subtask-maker.md` | `subtask-maker.md` | `subtask-maker/SKILL.md` | `subtask-format.md` |
| Execute | `execute-plan.md` | `execute-plan.md` | `execute-plan/SKILL.md` | `execution-format.md` |
| Review | `review-execution.md` | `review-execution.md` | `review-execution/SKILL.md` | `review-format.md` |
| Triage | `review-triage.md` | `review-triage.md` | `review-triage/SKILL.md` | `validation-format.md`, `review-guidance-format.md` |
| Commit | `commit-task.md` | `commit-task.md` | `commit-task/SKILL.md` | `commit-format.md` |
| Push | `push-task.md` | `push-task.md` | `push-task/SKILL.md` | `push-format.md` |
| Merge | `merge-task.md` | `merge-task.md` | `merge-task/SKILL.md` | `merge-format.md` |
| Close | `close-task.md` | `close-task.md` | `close-task/SKILL.md` | `archive-format.md` |

### Shared

| File | Role |
| ---- | ---- |
| `.cursor/skills/conflict-resolution/SKILL.md` | Shared merge conflict protocol for push and merge |
| `.cursor/skills/next-step-spec/SKILL.md` | Follow-up spec format (same schema as spec) |
| `.cursor/skills/start-task/scripts/start-worktrees.sh` | Worktree creation script |
| `CONTRIBUTING.md` | Full contributor workflow documentation |

---

## Tool permission pattern

Cursor subagent frontmatter supports only `name`, `description`, `model`, `readonly`, and `is_background` ([Subagents docs](https://cursor.com/docs/subagents)). Per-tool restrictions live in each skill's `metadata.tools` block (`.cursor/skills/<agent>/SKILL.md`) and in the agent prompt body. Agents must not use tools marked `false`.

| Agent | read | write | delete | shell | grep/glob/search | task |
| ----- | ---- | ----- | ------ | ----- | ---------------- | ---- |
| Nicki | yes | no | no | no | no | yes |
| current-task-update | yes | yes (context only) | no | no | no | no |
| start-task | yes | no | no | yes | no | no |
| spec-maker | yes | yes | no | no | yes | no |
| subtask-maker | yes | yes | no | no | yes | no |
| execute-plan | yes | yes | yes | yes | yes | no |
| review-execution | yes | yes (review YAML) | no | yes | yes | no |
| review-triage | yes | yes | no | no | yes | no |
| commit-task | yes | yes | no | yes | yes | no |
| push-task | yes | yes | no | yes | yes | no |
| merge-task | yes | yes | no | yes | yes | no |
| close-task | yes | yes (archive only) | yes (current-task/) | yes (delete only) | glob | no |

Per-tool `true`/`false` is prompt-enforced today; Cursor native support is limited to `readonly`.

---

## Quick invocation example

```bash
# 1. Create worktree (slug or short label is enough)
/start-task hero-section

# 2. Nicki initializes context, asks for job description if needed,
#    drafts a Gherkin user story, then continues through the pipeline
/spec-maker worktrees/hero-section
/subtask-maker worktrees/hero-section @current-task/specs/hero-section.yaml
/execute-plan worktrees/hero-section @current-task/subtasks/hero-section.md
/review-execution worktrees/hero-section
/review-triage worktrees/hero-section
/commit-task worktrees/hero-section
/push-task worktrees/hero-section @current-task/commits/hero-section.yaml
/merge-task worktrees/hero-section target: main

# 3. Nicki asks "Time for the feedback woof! Want?" then:
/close-task worktrees/hero-section
```

When orchestrated by Nicki, you invoke Nicki once and confirm each transition. The slash commands above remain usable directly without Nicki.

---

## Cursor mode picker (future)

Cursor 2.1+ removed user-defined custom modes from the chat mode dropdown (Plan, Agent, Build, etc.). Today Nicki is only available as `.cursor/agents/nicki.md` — a subagent the parent invokes via Task, not a selectable primary mode.

**Add when Cursor supports repo-defined custom modes again** (or Copilot-style `.agent.md` / `user-invocable` agents in the mode picker):

| Goal | Notes |
| ---- | ----- |
| Nicki in the mode dropdown | Same persona as `.cursor/agents/nicki.md`; user picks Nicki like Plan or Agent |
| Read-only orchestrator tools | `read`, `task`, `ask_question`, `todo_write` only — no write, shell, or source search |
| Not a slash command | Mode selection starts a Nicki-governed conversation; leaf steps still use `/start-task`, `/spec-maker`, etc. |
| Optional handoffs | Copilot-style buttons after each step (e.g. “Run spec-maker”, “Update context”) if the platform supports `handoffs` |

Until then, run Nicki by invoking the subagent or asking the parent agent to follow `.cursor/agents/nicki.md`.

---

## Surviving context compaction (Cursor 3.7+)

Cursor **3.7.27** still compacts parent chats automatically when the context window fills. Summarization is **lossy**: early turns, exact tool output, unpersisted yes/no approvals, and in-flight describe drafts may vanish from what the model sees. Raw bubbles remain on disk in Cursor storage; orchestration must not depend on them.

| Survives compaction | Does not survive (unless persisted) |
| ------------------- | ----------------------------------- |
| `current-task/current-task-context.yaml` | Chat memory of `current_step` / `next_step` |
| Step artifacts (`specs/`, `subtasks/`, executions, etc.) | Unapproved describe drafts |
| `.cursor/agents/nicki.md` on disk | Parent chat following nicki rules from memory |
| Rules injected every turn (if configured) | Pending git-transition confirmations |

**Patterns:**

1. **Disk-first** — `current-task-context.yaml` and artifacts are the source of truth (design decision #4).
2. **Reload on activation** — Nicki re-reads context YAML before every transition; see **Session bootstrap** in `.cursor/agents/nicki.md`.
3. **Re-invoke Nicki as a subagent** — each Task spawn reloads the full `.cursor/agents/nicki.md` prompt; prefer this over long inline parent orchestration.
4. **Re-confirm transitions** — treat chat approvals as lost unless recorded in `history` or `open_questions` on disk.

Custom modes: Cursor 3.7 still has internal `modes4` storage and **Export Custom Modes**, but no **Add custom mode** UI — mode-picker entry for Nicki remains future work (see above).

---

## Further reading

- Full contributor workflow: [`CONTRIBUTING.md`](CONTRIBUTING.md) — agent workflow pipeline section
- Nicki agent definition: [`.cursor/agents/nicki.md`](.cursor/agents/nicki.md)
- Context schema: [`.cursor/skills/current-task-update/current-task-context-format.md`](.cursor/skills/current-task-update/current-task-context-format.md)
- Archive schema: [`.cursor/skills/close-task/archive-format.md`](.cursor/skills/close-task/archive-format.md)
