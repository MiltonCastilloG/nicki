# P1 — Bootstrap script investigation

## Design decisions (approved)

| Topic | Decision |
| --- | --- |
| Script name | `bootstrap-context.py` — sibling to `check-gate.py` under `.cursor/skills/nicki/scripts/` |
| Shared helpers | Reuse `gate_utils.py` (workspace root, worktree resolve, YAML/JSON load, readiness) — do not fork read logic |
| Separation | `bootstrap-context.py` owns **position and routing context**; `check-gate.py` owns **spawn veto** — no gate duplication |
| Stdout contract | JSON: `active_task`, `status_path`, `next_step`, `completed_steps`, `readiness`, `sheep` (per `nicki.md` Harness failure table and `routing.yaml` `harness_failure.scripts`) |
| Investigation artifact | Mapping doc in spec step — which disk files, fields, and conditionals Nicki bootstrap prose currently implies |
| Nicki wiring | Replace manual bootstrap file reads with run-script → parse stdout; preserve transition card and `check-gate.py` sequence |
| Trimming | P3 — do not delete Bootstrap prose in `nicki.md` until script is proven on a real task |
| Harness failure | `bootstrap-context.py` already listed in `routing.yaml` — script must satisfy contract or trigger `sheep-fallback` |
| Smoke | Fixtures exercised through the script (pass + fail contract cases) — align with P2 #10 pattern, not a parallel smoke script |
| Permissions | Add `bootstrap-context.py` to `.cursor/permissions.json` when Nicki wiring lands |

### Approaches considered

| Approach | Trade-off | Verdict |
| --- | --- | --- |
| **A. Dedicated `bootstrap-context.py`** | Clear boundary with `check-gate.py`; matches existing harness contract | **Recommended** |
| B. Extend `check-gate.py` with `--mode bootstrap` | One entry point; mixes context assembly with gate veto | Reject — violates single responsibility |
| C. Per-file micro-scripts | Fine-grained; Nicki orchestrates many calls | Reject — fragmentation, no shared contract |

---

## Feature: Investigation maps Nicki bootstrap disk reads

As a Nicki maintainer
I want a documented map of how bootstrap prose derives orchestration context from disk
So that the bootstrap script reproduces the same reads without prompt interpretation drift

### Background

```gherkin
Given P1-16 context-handling shipped disk-first bootstrap prose in nicki.md Bootstrap section
And P2 nicki-gate-wiring shipped check-gate.py invocation before sheep spawn
And bootstrap-context.py is referenced in nicki.md and routing.yaml harness_failure but does not exist on disk yet
And actors are the user, Nicki, and sheep
And the three standing goals apply in priority order: correct functioning, harness and guardrails, trimming
And constraints are no-commit from sheep, no-new-deps unless required, and YAGNI
```

### Scenario: Map global-status and status.json read surface

```gherkin
Given an implementer reviews nicki.md Bootstrap, global-status-read.md, and status-read.md
When the investigation artifact is produced in the spec step
Then it lists every field Nicki bootstrap derives from global-status.json (active_task, status_path, worktree_path resolution)
And it lists every field derived from current-task/status.json (task.next_step, task.current_step, task.completed_steps, scope.worktree_path, artifacts pointers, open_questions)
And it notes when active_task is absent or status_path is missing — expected Nicki behavior today
```

### Scenario: Map routing.yaml and conditional artifact reads

```gherkin
Given routing.yaml steps.*.sheep defines the sheep map per pipeline step
When the investigation maps bootstrap reads
Then it documents how next_step routes to sheep via routing.yaml
And it documents validation YAML read only when artifacts.review_validation is set — readiness.status for post-review routing
And it documents spec artifact read only for the open_questions gate before subtasks — not for general bootstrap
And it documents readiness routing sync_blocked semantics (fix_required, blocked) that bootstrap context must surface
And it explicitly excludes reading story, execution, review markdown, or app source during bootstrap
```

---

## Feature: bootstrap-context.py emits orchestration context on stdout

As a Nicki operator
I want a deterministic script that assembles bootstrap context from disk
So that Nicki does not re-interpret prose file-read rules each response

### Scenario: Script runs from workspace root with worktree argument

```gherkin
Given global-status.json and a task worktree with current-task/status.json exist
When an operator runs python3 .cursor/skills/nicki/scripts/bootstrap-context.py --worktree <scope.worktree_path> from workspace root
Then the script exits 0
And stdout is a single JSON object
And required fields are present: active_task, status_path, next_step, completed_steps, readiness, sheep
And sheep matches routing.yaml steps[task.next_step].sheep when that step exists
And completed_steps reflects status.json task.completed_steps (empty array when absent)
```

### Scenario: Readiness populated only when validation pointer set

```gherkin
Given status.json has artifacts.review_validation pointing at an on-disk validation YAML
When bootstrap-context.py runs for that worktree
Then readiness in stdout equals readiness.status from the validation file
And when artifacts.review_validation is absent readiness is null in stdout
And the script does not load spec or other artifacts unless the open_questions gate path requires it per investigation map
```

### Scenario: Contract failure is harness failure not silent fallback

```gherkin
Given bootstrap-context.py cannot resolve worktree, status.json is missing, or stdout would omit a required contract field
When the script exits or emits incomplete JSON
Then Nicki treats the outcome as harness failure per nicki.md — not a normal pipeline block
And sheep-fallback may be spawned with failed script route, input, and expected contract
```

### Scenario: Smoke fixtures exercise the script

```gherkin
Given fixture worktrees or status.json files under .cursor/skills/nicki/scripts/fixtures/ or equivalent harness path
When smoke runs bootstrap-context.py against a minimal v2 happy-path fixture
Then stdout satisfies the contract with expected next_step and sheep
And at least one fixture exercises missing status.json or malformed global-status and expects non-zero exit or contract failure
And smoke reuses the same fixture layout pattern as check-gate.py where practical
```

---

## Feature: Nicki invokes bootstrap-context.py every response

As a Nicki operator
I want Nicki to run the bootstrap script before routing or spawning
So that orchestration context comes from script stdout instead of manual multi-file reads

### Background

```gherkin
Given nicki.md Bootstrap hard-gate requires disk bootstrap before routing or spawning any sheep
And check-gate.py runs after transition card and user confirm — not before bootstrap
And existing Bootstrap numbered read list in nicki.md stays until P3 trim after script is proven
```

### Scenario: Bootstrap script replaces manual read sequence

```gherkin
Given Nicki is activated for any pipeline response
When Nicki performs bootstrap
Then Nicki runs bootstrap-context.py with --worktree from resolved task scope before routing or spawning
And Nicki derives active_task, status_path, next_step, completed_steps, readiness, and intended sheep from script stdout — not from re-reading global-status.json, status.json, and routing.yaml separately
And Nicki still shows transition cards and runs check-gate.py per existing Transitions rules after bootstrap
And Nicki does not use resume; disk wins over chat and parent prompt
```

### Scenario: nicki.md documents bootstrap script invocation

```gherkin
Given nicki.md Bootstrap section is updated for this task
When an operator reads Nicki agent instructions
Then prose describes run bootstrap-context.py → parse stdout contract → then existing transition and check-gate sequence
And the block references bootstrap-context.py by path under .cursor/skills/nicki/scripts/
And existing gate and readiness prose remains until P3 trim — add harness wiring, do not delete yet
And Nicki Safety allows running bootstrap-context.py as a permitted script invocation
```

### Scenario: Permissions allow bootstrap script

```gherkin
Given .cursor/permissions.json controls terminal allowlist
When permissions are verified or updated for this task
Then terminalAllowlist includes python3 invocation of bootstrap-context.py with --worktree
And check-gate.py and create-worktree.py entries remain present
```

---

## Feature: YAGNI scope boundary

As a Nicki maintainer
I want bootstrap-script work bounded to investigation, script, Nicki wiring, and smoke
So that gate logic and prompt trimming do not expand this chore

### Scenario: Out of scope for bootstrap-script

```gherkin
Given this chore completes P1 #18 bootstrap script investigation
When implementers plan subtasks
Then they do not move check-gate.py gate rules into bootstrap-context.py
And they do not trim nicki.md Bootstrap or Readiness sections (P3 #12–#14)
And they do not implement validate-sheep-return.py or update-status.py unless a minimal wiring gap forces a one-line cross-reference
And they do not add a long-lived server, CLI nicki continue, or rewrite sheep agents
And investigation mapping lives in spec artifacts — not a permanent duplicate of status-read.md field tables
```

---

## Probes for spec (resolve before subtasks)

| Probe | Default in story | Spec must resolve |
| --- | --- | --- |
| Investigation output shape | Section in spec YAML referencing file→field map | Exact artifact path and whether a standalone markdown appendix is needed |
| `--worktree` vs `--task-id` CLI | `--worktree` required; resolve from global-status when user omits task | Whether optional `--task-id` resolves worktree via global-status.json |
| Extra stdout fields | Contract fields only | Whether worktree_path, current_step, or sync_blocked belong in contract or stay gate-only |
| open_questions gate in bootstrap | Script loads spec only when next_step is subtasks and gate needs it | Exact condition mirroring check-gate gates.py |
| Fixture location | Beside check-gate fixtures | Exact paths and fixture names |
