# Skills vs Agents Separation Audit

## Purpose

Audit all Nicki `.cursor/skills/` and `.cursor/agents/` files against this principle:

| Layer | Owns |
|-------|------|
| **Skill** | Pure functionality — how to perform one job (analyze, write artifact, run git ops, resolve conflicts) |
| **Agent** | Workflow — when to run, what inputs to load from disk, output paths, handoffs to the next step, status/registry updates |

**Skills must not** reference workflow control artifacts (`status.json`, `global-status.json`), pipeline step names (`next_step`, `describe` → `spec` → …), or “Nicki will spawn X next” routing.

**Exception:** skills (and their agents) whose job *is* task/workflow state or lifecycle — `current-task-update`, `start-task` (registry), `close-task` / `close-scope` / `task-archive`, `hook-contract`.

Date: 2026-06-12. Read-only audit; no files changed except this report.

---

## Executive Summary

The split is **partially implemented**. Agents are thinner than skills but still duplicate much workflow text. **Skills carry the bulk of workflow leakage** — especially:

1. **Nicki / pipeline references** in “When to use”, report steps, and safety rules
2. **`status.json` as an auto-loaded input** and scope validator in almost every leaf skill
3. **Full `current-task/` directory trees** in format docs (pipeline map, not schema)
4. **`readiness` routing tables** in `validation-format.md` that describe Nicki gates, not triage logic alone
5. **`next.suggested`** fields in push/publish format files
6. **Cross-agent handoff chains** embedded in skills (`commit-task` → `push-task` → `merge-task` → `publish-task`)

**Agents that are closest to the target:** `current-task-update`, `review-execution`, `execute-plan` — workflow is thin; skill still bloated.

**Agents that still need workflow enrichment (from skills):** all git-tail agents, `spec-maker`, `subtask-maker`, `review-triage`, `start-task`.

**Skills correctly treated as workflow (keep as-is or minor cleanup):** `current-task-update/*`, `hook-contract`, `close-task`, `close-scope`, `task-archive`.

**Skills that are already mostly pure:** `caveman`, `conflict-resolution` (minor agent-name refs only).

---

## Target Shape (Reference)

```text
nicki.md                          # full pipeline, gates, status reads, spawn rules
.cursor/agents/<leaf>.md          # inputs to load, output path, scope, “do not touch status.json”
.cursor/skills/<leaf>/SKILL.md    # HOW: steps, algorithms, safety for the operation itself
.cursor/skills/<leaf>/*-format.md # schema for THIS skill’s output (+ direct inputs it consumes)
```

A leaf skill should be invocable without knowing Nicki exists. The agent adds:

- Which files to auto-load (spec path, review path, commit handoff, …)
- Whether `status.json` is passed for validation
- What Nicki summary fields to expect on return
- Pipeline position (“only after acceptance” belongs in agent + nicki, not skill)

---

## Exceptions (Workflow Skills — OK to Reference Status / Registry)

| Skill / file | Why it stays workflow-aware |
|--------------|----------------------------|
| `current-task-update/SKILL.md` | Writes `status.json`; defines Nicki summary ingestion |
| `current-task-update/status-format.md` | Per-task workflow state schema |
| `current-task-update/global-status-format.md` | Registry schema (read-only for this agent) |
| `current-task-update/current-task-context-format.md` | Deprecated; documents migration only |
| `start-task/SKILL.md` | Registers `global-status.json` (registry write is lifecycle) |
| `start-task/scripts/register-global-status.sh` | Registry mutation |
| `close-scope/SKILL.md` + `unregister-global-status.sh` | Registry teardown |
| `close-task/SKILL.md` | Orchestrates archive + unregister + delete; tail gates |
| `task-archive/SKILL.md` + `archive-format.md` | Reads `status.json` artifacts to build archive |
| `hook-contract/SKILL.md` | Resolves `global-status.json` → `status_path` → routing |

**Note:** `start-task` also contains non-exception content (full pipeline reminder, “next step describe”) — that portion should move to `agents/start-task.md` and `nicki.md`.

---

## Per-Skill Findings

### Pure / near-pure (good)

| Skill | Workflow leakage | Verdict |
|-------|------------------|---------|
| `caveman/SKILL.md` | None | **Clean** |
| `conflict-resolution/SKILL.md` | Names `merge-task` / `push-task` as callers; handoff record is generic | **Acceptable** — optional: rename to “calling agent” |

---

### Leaf skills — workflow leakage (needs refactor)

#### `spec-maker`

| Location | Issue |
|----------|-------|
| `SKILL.md` description | “Use when Nicki Task-spawns” |
| `SKILL.md` § Required inputs | `current-task/status.json` optional orchestration input |
| `SKILL.md` § Step 1 | Load/validate `status.json`; `task.story` from context |
| `SKILL.md` § Step 4 | `meta.context: current-task/status.json` |
| `SKILL.md` § Safety | “Never edit status.json; Nicki updates via current-task-update” |
| `SKILL.md` § Report | Next command `subtask-maker …` |
| `spec-format.md` L7–22 | Full `current-task/` tree with agent lineage |
| `spec-format.md` L11, L49 | `status.json` as “workflow context” |

**Keep in skill:** spec schema, how to derive requirements from story text, scope bounding, `open_questions` rules, write path `current-task/specs/<slug>.yaml` (own output).

**Move to agent:** status loading, `task.story` preference, `meta.context` population, next-step hint.

---

#### `subtask-maker`

| Location | Issue |
|----------|-------|
| `SKILL.md` | Nicki spawn refs; `status.json` load/validate; “Nicki mirrors block in status open_questions” |
| `SKILL.md` § Report | `execute-plan` next command |
| `subtask-format.md` L7–22 | Full pipeline tree; `status.json` in frontmatter |

**Keep in skill:** spec → checklist algorithm, caveman voice, open_questions stop rule (as spec gate, not status gate).

**Move to agent:** status.json input; open_questions mirror note; execute-plan routing.

---

#### `execute-plan`

| Location | Issue |
|----------|-------|
| `SKILL.md` | Nicki refs; `status.json` validate; parent workflow via start-task |
| `SKILL.md` § Safety | status.json + Nicki current-task-update |
| `SKILL.md` § Report | `review-execution` next command |
| `execution-format.md` L7–22 | Full pipeline tree |

**Keep in skill:** subtask execution loop, scope boundary, execution YAML schema, flip `- [ ]` → `- [x]`.

**Move to agent:** status.json; review next step.

---

#### `review-execution`

| Location | Issue |
|----------|-------|
| `SKILL.md` | Auto-load status.json; “workflow hints from task context” |
| `SKILL.md` § Safety | status.json / Nicki |
| `review-format.md` L7–21 | Full pipeline tree; status.json comment |

**Keep in skill:** review algorithm, `approved` + `content` only, verification rerun, guidance consumption rules.

**Move to agent:** which paths to auto-load; optional status for hints.

**Good:** skill already says “Do not mention downstream agents or routing” (L170) — inconsistent with other sections.

---

#### `review-triage`

| Location | Issue |
|----------|-------|
| `SKILL.md` L149 | “Nicki Task-spawns current-task-update … `artifacts.review_validation`” |
| `SKILL.md` § Step 2 | “workflow step, open questions, artifact paths, history” from task context |
| `validation-format.md` L14–29 | Full pipeline tree |
| `validation-format.md` L54 | `context` as “workflow source” |
| `validation-format.md` L100–111 | **`readiness` routing table for Nicki** (`acceptance` / `execute` / `review` / `commit-task` blocked) |
| `review-guidance-format.md` | (not fully audited — likely cross-refs to pipeline) |

**Keep in skill:** finding classification, next-step spec writing, review guidance writing, `decision` / findings structure, append `## Fix` behavior.

**Move to agent + nicki:** how Nicki consumes `readiness`; status pointer updates; commit gating.

**Gray area:** `readiness` block is both triage *output* and orchestration *signal*. Recommend: keep field **definitions** in `validation-format.md`, move **routing table and commit gates** to `agents/review-triage.md` and `nicki.md`.

---

#### `commit-task`

| Location | Issue |
|----------|-------|
| `SKILL.md` § When | “Nicki moving triage → commit” |
| `SKILL.md` § Step 2 | Loads status.json, reviews, validations, merges — **workflow gating** |
| `SKILL.md` § Step 4 | Stages `current-task/` metadata including status.json |
| `SKILL.md` § Report | `push-task` next command |
| `commit-format.md` L11–26 | Full pipeline tree |
| `commit-format.md` L46–48 | status/review/triage/merge in meta example |

**Keep in skill:** git inspect, stage, commit message style, commit YAML schema, secret/branch guards.

**Move to agent:** pre-commit readiness checks (approved review, triage blockers); which handoffs to load.

---

#### `push-task`

| Location | Issue |
|----------|-------|
| `SKILL.md` § When | commit handoff prerequisite; Nicki commit → push |
| `SKILL.md` § Step 2 | Loads status.json |
| `SKILL.md` § Report | “merge-task” suggested next |
| `push-format.md` L24, L56–57 | `next.suggested: merge` workflow hint |

**Keep in skill:** pre-push merge, push, conflict protocol, push YAML schema.

**Move to agent:** load commit handoff + optional status; drop `next` from format or mark agent-only.

---

#### `merge-task`

| Location | Issue |
|----------|-------|
| `SKILL.md` L12 | “first workflow step that touches main” |
| `SKILL.md` § Step 2 | status.json + push handoff |
| `SKILL.md` L142 | **Nicki current-task-update** with `completed_step`, `artifacts.merge`, `next_step: publish` |
| `SKILL.md` § Report | status-update → publish-task |
| `merge-format.md` L63 | “publish-task owns push” |

**Keep in skill:** merge into target branch, conflict resolution, merge YAML schema.

**Move to agent:** push handoff load; all Nicki/status-update instructions; publish routing.

---

#### `publish-task`

| Location | Issue |
|----------|-------|
| `SKILL.md` | “Slot: after merge-task, before close-task”; Nicki `next_step: publish` |
| `SKILL.md` L66 | Nicki current-task-update with `next_step: close` |
| `publish-format.md` L52–53 | `next.suggested: close` |

**Keep in skill:** user-confirmed target branch push, publish YAML schema.

**Move to agent:** merge handoff load; pipeline slot; status-update payload.

---

#### `close-task` + helpers

| Component | Verdict |
|-----------|---------|
| `close-task/SKILL.md` | **Exception** — tail gate via status `artifacts` is correct here |
| `close-scope/SKILL.md` | **Exception** — registry + teardown |
| `task-archive/SKILL.md` | **Exception** — reads status for archive content |

Minor cleanup: tail gate could be duplicated in `agents/close-task.md` only, with skill focusing on archive/unregister/teardown mechanics.

---

#### `next-step-spec`

| Location | Issue |
|----------|-------|
| `SKILL.md` | Paths under `current-task/next-steps/`; traceability to review/validation paths |

**Verdict:** **Mostly OK** — defines artifact shape for review-triage output. References to `source_validation` / `source_review` are traceability fields, not pipeline routing. Optional: strip “passable to subtask-maker” command example to agent.

---

#### `start-task`

| Location | Issue |
|----------|-------|
| `SKILL.md` L29, L79–91 | `global-status.json` registration — **exception** |
| `SKILL.md` L106–113 | Full pipeline list + `task-archive` verify |
| `SKILL.md` L100–106 | Nicki handoff + describe → status.json narrative |

**Move to agent:** pipeline reminder, describe next step, Nicki handoff field list.

**Keep in skill:** worktree script, branch taxonomy, register script (registry exception).

---

## Per-Agent Findings

Agents are the right home for workflow, but most are **stubs that defer to skills** — so workflow lives in the wrong layer today.

| Agent | Workflow in agent | Workflow still trapped in skill | Gap |
|-------|-------------------|----------------------------------|-----|
| `nicki.md` | Full pipeline, gates, status bootstrap | — | **Correct** orchestrator |
| `current-task-update.md` | Thin; points to skill | Skill is workflow by design | **OK** |
| `start-task.md` | Partial handoff | Pipeline in skill Step 4 | Add registry + handoff; strip pipeline from skill |
| `spec-maker.md` | status optional, story preference | Most steps in skill | Add output path, artifact list, no status in skill |
| `subtask-maker.md` | open_questions block note | status + Nicki in skill | Agent owns spec gate + inputs |
| `execute-plan.md` | Thin | status + next review in skill | Agent lists inputs explicitly |
| `review-execution.md` | Good input list | status in skill | **Near target** |
| `review-triage.md` | Good write scope | readiness routing in validation-format | Agent owns readiness → Nicki mapping |
| `commit-task.md` | “Nicki spawns push next” | Gating in skill Step 2 | Agent owns readiness/handoff loads |
| `push-task.md` | commit handoff input | Chain in skill | Agent owns merge next step |
| `merge-task.md` | Thin | Nicki status-update in skill L142 | Agent owns post-merge spawn hints |
| `publish-task.md` | merge + status load | Slot + status-update in skill | **Reasonable**; enrich agent |
| `close-task.md` | Thin checklist | Tail gate in skill | **OK** for exception class |

**Pattern to apply:** agent front-matter should name **concrete input paths** and **gates**; skill should not say “when Nicki Task-spawns”.

---

## Format Files — Cross-Cutting Issues

These files appear in multiple skills and repeat the same workflow documentation:

| Pattern | Files affected | Recommendation |
|---------|----------------|----------------|
| Full `current-task/` tree with agent names | `spec-format.md`, `subtask-format.md`, `execution-format.md`, `review-format.md`, `validation-format.md`, `commit-format.md` | **Remove** from skills; one canonical map in `nicki.md` or `current-task-update/status-format.md` § artifacts |
| `meta.context: current-task/status.json` in examples | Most `*-format.md` | Make **optional** in examples; agent instructs when to set |
| `next.suggested` | `push-format.md`, `publish-format.md` | **Remove** from skill formats; Nicki derives next step from disk |
| “Handoff from X to Y” intro lines | `commit-format.md`, `push-format.md`, `merge-format.md`, `publish-format.md` | Shorten to “output of `<agent>`” without naming consumer |
| `readiness` routing table | `validation-format.md` L100–111 | Split: field defs in skill; routing in `agents/review-triage.md` + `nicki.md` |

---

## Scripts

| Script | Workflow? | Verdict |
|--------|-----------|---------|
| `start-task/scripts/start-worktrees.sh` | No — git worktrees | **Pure** |
| `start-task/scripts/register-global-status.sh` | Yes — registry | **Exception** (stay with start-task) |
| `close-scope/scripts/unregister-global-status.sh` | Yes — registry | **Exception** |
| `review-triage/scripts/smoke-readiness-routing.sh` | Yes — tests routing | Belongs with hook/nicki tests, not review-triage skill |
| `current-task-update/scripts/smoke-status-boundary.sh` | Yes | **OK** with current-task-update |
| `publish-task/scripts/smoke-git-tail.sh` | Yes | Could live under integration tests |

---

## Quantitative Snapshot

Grep for workflow terms in `.cursor/skills/**/*.md` (approximate hit counts per file from audit):

| High-count files | Terms |
|------------------|-------|
| `current-task-update/SKILL.md` | Nicki, status, workflow — **expected** |
| `review-triage/SKILL.md`, `validation-format.md` | readiness, Nicki, status, artifacts |
| `start-task/SKILL.md` | global-status, pipeline, Nicki |
| `merge-task/SKILL.md`, `publish-task/SKILL.md` | Nicki, next_step, status |
| All leaf `*-format.md` | `current-task/` trees, status.json |

Leaf skills average **4–10 workflow references each** beyond their own output path.

---

## Recommended Remediation (Prioritized)

### P0 — Principle doc

Add `.cursor/skills/README.md` or a section in `NICKI.md`:

- Skills = portable operations
- Agents = Nicki bindings (paths, gates, spawn)
- Exceptions list (short)

### P1 — Strip duplicate pipeline trees

Remove “All agent YAML artifacts…” blocks from leaf `*-format.md` files. Single canonical artifact map already exists in `status-format.md` / `nicki.md`.

### P2 — Move auto-load rules to agents

For `spec-maker`, `subtask-maker`, `execute-plan`, `review-execution`, `review-triage`, `commit-task`, `push-task`, `merge-task`, `publish-task`:

1. Delete `status.json` load/validate from skills
2. Add explicit “Inputs to load” table in matching `agents/*.md`
3. Skills accept **inline content or paths passed in prompt** — no implicit disk discovery

### P3 — Move routing / spawn text

- Delete “Nicki Task-spawns …” from skill descriptions (use neutral “Use when invoked to …”)
- Delete “Report next command: …” from skills
- Delete `next.suggested` from push/publish formats
- Move `validation-format.md` readiness routing table to `nicki.md` + `agents/review-triage.md`

### P4 — Git-tail gating

`commit-task` skill Step 2 (review/triage gating) → `agents/commit-task.md` + `nicki.md` acceptance gate (avoid duplication: gate lives in Nicki; agent double-checks handoffs exist).

### P5 — start-task split

Skill: classification + scripts only. Agent: Nicki handoff YAML shape, `describe` next step, pipeline reminder.

### P6 — Smoke tests

Move `smoke-readiness-routing.sh` out of `review-triage` skill or label it integration/orchestration test.

---

## File-by-File Checklist

| File | Status | Action |
|------|--------|--------|
| `skills/caveman/SKILL.md` | Clean | — |
| `skills/conflict-resolution/SKILL.md` | Clean | Optional caller-neutral wording |
| `skills/spec-maker/*` | Leaks | P1, P2, P3 |
| `skills/subtask-maker/*` | Leaks | P1, P2, P3 |
| `skills/execute-plan/*` | Leaks | P1, P2, P3 |
| `skills/review-execution/*` | Leaks | P1, P2 |
| `skills/review-triage/*` | Leaks | P1, P2, P3, P6 |
| `skills/next-step-spec/SKILL.md` | Minor | Optional |
| `skills/commit-task/*` | Leaks | P1, P2, P4 |
| `skills/push-task/*` | Leaks | P1, P2, P3 |
| `skills/merge-task/*` | Leaks | P1, P2, P3 |
| `skills/publish-task/*` | Leaks | P1, P2, P3 |
| `skills/start-task/SKILL.md` | Mixed | P5 (exception: register script) |
| `skills/current-task-update/*` | Workflow skill | Keep; trim deprecated doc over time |
| `skills/close-task/SKILL.md` | Exception | Minor agent/skill dedup |
| `skills/close-scope/*` | Exception | — |
| `skills/task-archive/*` | Exception | — |
| `skills/hook-contract/SKILL.md` | Exception | — |
| `agents/nicki.md` | Orchestrator | Keep as canonical workflow |
| `agents/current-task-update.md` | OK | — |
| `agents/start-task.md` | Thin | Enrich per P5 |
| `agents/spec-maker.md` | Thin | Enrich per P2 |
| `agents/subtask-maker.md` | Partial | Enrich per P2 |
| `agents/execute-plan.md` | Thin | Enrich per P2 |
| `agents/review-execution.md` | Good | Minor |
| `agents/review-triage.md` | Partial | Add readiness routing per P3 |
| `agents/commit-task.md` | Partial | Add gating per P4 |
| `agents/push-task.md` | Partial | Enrich |
| `agents/merge-task.md` | Thin | Enrich per P3 |
| `agents/publish-task.md` | Partial | Enrich |
| `agents/close-task.md` | OK | — |

---

## Definition of Done (Separation Complete)

1. Any leaf skill reads as a **standalone operation manual** with no Nicki name, no `status.json`, no `global-status.json`, no pipeline step names.
2. Matching agent lists **all disk inputs/outputs** and **gates** for that step.
3. `nicki.md` remains the **only** full pipeline narrative.
4. `status-format.md` + `global-status-format.md` remain the **only** workflow state schemas.
5. `validation-format.md` defines `readiness` **fields**; Nicki/agent define **routing**.
6. Format files document **one artifact type** each — no multi-agent directory posters.

---

## Related

- Prior workflow review: [report.md](report.md)
- Orchestrator: `.cursor/agents/nicki.md`
- Status schemas: `.cursor/skills/current-task-update/status-format.md`, `global-status-format.md`
