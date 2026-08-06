# Design: Delete outputs nothing reads and sheep cannot know

Date: 2026-08-05  
Status: **designed**  
Slug: `delete-unread-outputs`  
Related: [`2026-08-05-adhoc-direct-sheep-invocation-design.md`](2026-08-05-adhoc-direct-sheep-invocation-design.md), [`2026-08-01-artifact-ownership-and-position-design.md`](2026-08-01-artifact-ownership-and-position-design.md), handoff [`docs/adhoc/adhoc-direct-sheep-invocation/output_problem_example.md`](../../adhoc/adhoc-direct-sheep-invocation/output_problem_example.md)

## Problem

Path ownership is settled: the caller packs where to read and where to write, and sheep obey. Output *shape* was the open half — the archive dogfood hit a hardcoded `outcome.status: pending_integrate`, a `story.md` the caller could not supply, an empty forced `process`, and a `meta.source_context` documented as one value.

The obvious fix is a caller-owned output contract, mirroring how inputs work. Auditing the fields first says otherwise. Most of them do not need an owner — they need deleting.

## Audit

### Nothing reads the archive report

No script, no test, no skill parses `report.json`. The pipeline uses only its **path**, stored as `status.artifacts.archive`, so `sync` can flip `next_step` from `archive` to `integrate` via `next_step_when_archived`. The report is a human document with a machine-checked filename.

Judged as "what does a human learn from this field", three fail:

| Field | Evidence |
|---|---|
| `meta.source_context` | `current-task/status.json` in 17 of 20 existing archives — a constant in-workflow, with no reader |
| `outcome.status` | Four vocabularies across archives (`archived`, `integrated`, `merged`, `pending_integrate`) with no enum. Archive runs at step 4 of `sync → archive → sync → integrate → close`, so the work provably has not integrated when the report is written. `pending_integrate` is the only truthful in-workflow value |
| `outcome.final_artifact` | Points at `current-task/integrates/<slug>.yaml`, a file that does not exist yet — a prediction recorded as fact |

Two reported frictions are smaller than they looked. The `story.md` problem is a self-contradiction inside one file: [`archive-format.md`](../../../.cursor/skills/task-archive/archive-format.md) line 10 says "copy from `artifacts.story` when present", line 143 lists it as required. The `suggestions.area` complaint was stale — `orchestration` is already in the enum.

### Sheep inventory

Inputs are what the caller packs (`routing.json` `prompt` strings plus each skill's Inputs table); writes are effects on disk or git; returns are the JSON handed back.

| Sheep | Inputs the caller packs | Writes | Returns |
|---|---|---|---|
| `start` *(Nicki-only)* | work items / slugs; per item `--project`, `--slug`, `--type`, optional `--original` | worktree + branch, `global-status.json` registration, initial `current-task/status.json` — all inside `create-worktree.py` | `worktree`, `artifact`, `completed_status`, `task{}`, `git{}`, `open_questions`, `summary` |
| `describe` | output path, task id, chat; `task.original`; user approval | story markdown at the given path | `artifact`, `completed_status`, `open_questions`, `summary` |
| `spec` | output path, task id, chat; worktree path; task description; optional `meta.context` | spec JSON at the given path — no write when `open_questions` would be non-empty | blocked → `completed_status: blocked` + `open_questions`; clear → `artifact` + `completed_status: complete` |
| `subtasks` | output path, task id, chat; worktree path; spec by path or inline | checklist markdown at the given path | `artifact`, `completed_status`, `open_questions`, `summary` |
| `execute` | worktree path, task id, chat; plan (path, inline, or free text) | app code in the worktree; flips `- [ ]` to `- [x]` | no `artifact`; `completed_status`, `open_questions`, `summary` |
| `review` | worktree path, task id, chat; diff plus whatever planning files exist | **nothing** — suggestions stay in the return; Nicki may later send `sheep-subtask` to append `## Fix` after user approval | no `artifact`; `completed_status`, `open_questions`, `summary` carrying the verdict |
| `sync` | worktree path, task id; optional base branch; optional commit instruction | git — commit, merge base into feature, push feature branch | no `artifact`; `completed_status`, `open_questions`, `summary` carrying `merged` / `not_needed` |
| `archive` | `prefix`, `slug`, status/artifact paths **or** `source_document`, optional errors path, task id | `report.json`, `report.md`, `story.md` when present, `errors.json` when named; deletes the pointed spec and subtask files | `artifact` = `report.json`, `completed_status`, `open_questions`, `summary` |
| `integrate` | worktree path, task id; target worktree; target branch; feature branch | git — `merge --no-ff` into target, push target | no `artifact`; `completed_status`, `open_questions`, `summary` |
| `close` *(Nicki-only)* | worktree path, task id; `status.json` preferred | unregisters from `global-status.json`, deletes worktree, prunes, deletes branch | prose teardown result — no JSON contract stated |
| `status` *(Nicki-only)* | Nicki's summary JSON, `--step`, `--mode`, worktree | `current-task/status.json` via `update-status.py`; temp file created and deleted | passes through script stdout: `written`, `path`, `completed_step`, `next_step`, `mode`, `blockers` |
| `fallback` | worktree path, failed script route, script input, expected output contract, actual failure, blocked step | appends one `errors.v1` entry to the errors file | `artifact` = the errors file, `completed_status: blocked`, `open_questions: []` |

Four problems fall out of the inventory.

**`completed_status` is position by proxy.** `completed_steps` is dropped on every write ("position + artifacts are enough"), and `_init_status` discards the field. Its one surviving effect is that `blocked` makes `_derive_next_step` hold `next_step` instead of advancing — the one act every sheep file forbids in its next sentence.

**`fallback` corrupts artifact pointers.** It returns `artifact` = the errors file while borrowing another step's `--step`. `_set_artifact_pointer` looks up that step's `artifact_key` and skips only keys in `NON_ARTIFACT_KEYS`, which is `{"status", ""}`. A harness failure during `spec` therefore sets `artifacts.spec` to the errors file, overwriting the real pointer. Steps with a null `artifact_key` are unaffected, so this bites describe, spec, subtasks, and archive.

**`sheep-start`'s return is unread, and the status write after it is a no-op.** `create-worktree.py` writes a complete `status.json` — including `current_step: start` and `next_step: describe` — before the sheep returns. `_init_status` therefore never runs, so the `task{}` block that feeds it is read by nobody; `git{}` is read by nobody; `artifact` is discarded because `start.artifact_key` is `null`. Only `worktree` matters, and not to the script — it is how Nicki learns the path just created. The subsequent `sheep-status` call rewrites the two values the script already wrote.

**`close`'s tail gate is dead.** [`close-task/SKILL.md`](../../../.cursor/skills/close-task/SKILL.md) blocks teardown unless `current-task/integrates/<slug>.json` exists or `artifacts.integrate` resolves. `sheep-integrate` writes no handoff by design and `integrate` carries `artifact_key: null`, so neither can ever be true. The guard on the only irreversible step checks for a file that was designed out.

### What is not a problem

`sheep-status` passing through script stdout is correct — it reports a harness result rather than doing sheep work. `sheep-close` returning prose is fine because nothing follows it; no status write happens after close.

Review's verdict (`acceptance` / `execute` / `review`) and sync's `merged` / `not_needed` are closed vocabularies carried in prose, but their consumer is Nicki reading a sentence, not a script matching a string. That is the line: **a vocabulary needs defining only where a script matches it exactly.** `completed_status` crossed it; these do not. Review's vocabulary is already written down once, on the consumer's side, in `nicki.md` step 3.

## Decision summary

| Topic | Decision |
|---|---|
| Caller-owned output contract | **Not built.** The audit removed the fields that would have needed one |
| `meta.source_context` | Deleted |
| `outcome.status`, `outcome.final_artifact` | Deleted; `outcome` keeps `target` and `pushed_branch` |
| `story.md` | Optional — copied when `artifacts.story` exists, never required |
| `completed_status` | Deleted from the return contract and the harness |
| "Do not advance" signal | Non-empty `open_questions` holds `next_step` |
| Precedence in `_derive_next_step` | Explicit summary `next_step` → `open_questions` hold → routing advance |
| `fallback` `artifact` | Dropped — the errors file is named in `summary` and the open question |
| `sheep-start` return | Trimmed to `worktree`, `open_questions`, `summary` |
| `sheep-status` after `start` | Dropped — the write is a no-op |
| `close` tail gate | Deleted — routing already makes `close` unreachable before `integrate` |
| Phantom handoff docs | Corrected wherever `syncs/` and `integrates/` are still presented as live outputs |
| Review verdict, sync outcome | Stay prose |
| Validation | None added anywhere |

## Archive output

In [`archive-format.md`](../../../.cursor/skills/task-archive/archive-format.md):

- `meta` keeps `schema` and `generated_by`. Drop `source_context` from the field table and the JSON example.
- `outcome` keeps `target` and `pushed_branch` — both are facts by archive time, since the first `sync` has run. Drop `status` and `final_artifact` from the table and the example.
- `report.md` section 3 becomes target branch and pushed branch, not "merged/pushed; final handoff path".
- The rule on line 143 requires `report.json` and `report.md` before the second sync and integrate. `story.md` comes off that list. Line 10 is already correct and stays.

In [`task-archive/SKILL.md`](../../../.cursor/skills/task-archive/SKILL.md), step 3 — "Set `outcome.status: pending_integrate` — integrate has not run yet" — is deleted. Its own justification is the proof that the field can say nothing else.

`process`, `decisions`, `open_questions`, `suggestions`, `story`, and `task` are unchanged. They carry real content a human reads.

## Return contract

### `completed_status` is removed everywhere

**[`routing.json`](../../../.cursor/skills/nicki/routing.json)** — drop `completed_status` from `sheep_return_contract.optional_fields`, drop `completed_status_values`, and rewrite `on_blocked` to: populate `open_questions`; position holds.

**[`update-status.py`](../../../.cursor/skills/current-task-update/scripts/update-status.py)** — delete `COMPLETED_STATUSES`, its validation branch, the module docstring line, the unused `_init_status` parameter, and both call-site arguments. `_derive_next_step` takes `open_questions` in place of `completed_status` and applies this precedence:

1. An explicit `next_step` in the summary wins. This is Nicki's review verdict and must keep working — a review that reports findings *and* routes to `execute` still advances.
2. Otherwise, non-empty `open_questions` returns the existing `next_step`, falling back to the completed step.
3. Otherwise, routing derives the next step.

Order matters. Today `blocked` is checked before the explicit override; inverting the first two is what protects review. Document sheep never send `next_step`, so they freeze exactly as they do now.

Jump mode and position-only writes are untouched — neither reaches `_derive_next_step`. Jump sets `next_step` to its target directly; position-only writes take `next_step` from the summary as the authority.

`_init_status` is already unreachable on the pipeline, because `create-worktree.py` always writes `status.json` first. It stays for the smoke tests that exercise a fresh worktree; only its dead parameter goes.

**Sheep files** — the Return section of all twelve `.cursor/agents/sheep-*.md` drops `completed_status`. What stays is what each sheep already says about `artifact` (a path, or none) plus `open_questions` and `summary`.

### `fallback` stops returning an artifact

[`sheep-fallback.md`](../../../.cursor/agents/sheep-fallback.md) returns no `artifact`, matching `execute` and `review`. The errors file is named in `summary` and in the open question it now records — the harness failure itself, replacing today's `completed_status: blocked` with `open_questions: []`, which under the new rule would advance. Nicki still holds the blocked step via `--step`.

Nothing consumes an errors pointer: `task-archive` takes the errors path from the caller's prompt, never from `status.artifacts`. `routing.json` `harness_failure.artifact` stays as caller-facing documentation of where errors land.

### `sheep-start` returns three fields

[`sheep-start.md`](../../../.cursor/agents/sheep-start.md) returns `worktree`, `open_questions`, and `summary`. The `task{}` block, `git{}` block, and `artifact` are removed from the example and from the "Stdout → handoff" mapping paragraph, which reduces to `worktree_path` → `worktree`.

## Position writes

`sheep-status` is no longer sent after `start`. `create-worktree.py` has already written `current_step: start` and `next_step: describe`; the write repeats them and changes nothing else, because `start.artifact_key` is `null` and the summary carries no `next_step`.

The invariant becomes: **after every sheep except `start` and `close`, send `sheep-status`.** Update [`nicki.md`](../../../.cursor/agents/nicki.md) (the Ownership paragraph and the Safety bullet), [`README.md`](../../../README.md), [`docs/NICKI.md`](../../NICKI.md) (the intro, the control table, the step-order paragraph, and design note 9), and [`docs/PLAN.md`](../../PLAN.md).

## Dead gates and phantom handoffs

The tail gate in [`close-task/SKILL.md`](../../../.cursor/skills/close-task/SKILL.md) is deleted — both the `## Tail gate` section and the checklist line that references it. Routing already guarantees the ordering it was trying to enforce: `next_step: close` is reachable only through `integrate`'s `default_next_step`, and `update-status.py` refuses to jump to `close` (`jump mode cannot target start/close/done`). The "No teardown before integrate handoff" safety bullet goes with it; "No close without Nicki confirm" stays.

That gate was the last consumer of a file the artifact-ownership change removed. Four live files still present `current-task/syncs/<slug>.json` and `current-task/integrates/<slug>.json` as real outputs, and they are corrected here:

| File | What is stale |
|---|---|
| [`README.md`](../../../README.md) | the sync/archive/integrate artifact row and the `current-task/` tree |
| [`docs/NICKI.md`](../../NICKI.md) | the integrate row in the step table, and design note 10 ("close-task checks integrate handoff") |
| [`docs/WORKFLOW-DIAGRAMS.md`](../../WORKFLOW-DIAGRAMS.md) | the `integrates/slug.json` diagram node and the sheep-integrate table row |
| [`current-task-context-format.md`](../../../.cursor/skills/current-task-update/current-task-context-format.md) | the directory tree, the artifacts table row, and the JSON example |

Operational steps write no handoff files. Position plus the document artifacts is the whole record.

## Docs and tests

Remove the `completed_status` enum from the four live files that teach it: [`current-task-update/SKILL.md`](../../../.cursor/skills/current-task-update/SKILL.md) (the return field list, the closed-set paragraph, the JSON example), [`status-format.md`](../../../.cursor/skills/current-task-update/status-format.md), [`docs/flexibility.md`](../../flexibility.md), and [`docs/NICKI.md`](../../NICKI.md).

Frozen records keep their history and are not rewritten: `docs/archive/**`, earlier specs in `docs/superpowers/specs/`, and the superseded write-ups (`docs/harness-alignment-subagents.md`, `docs/harness-gate-bugs.md`).

Tests:

- `tests/smoke/status_vocabulary.py` replaces its enum coverage with the freeze rule: non-empty `open_questions` holds `next_step`; an explicit summary `next_step` still wins; empty `open_questions` advances by routing.
- `tests/smoke/routing_write.py` and `tests/smoke/jump_mode.py` drop `completed_status` from their fixtures.
- A new case covers the fallback pointer: a summary with an `artifact` and `--step spec` is the corrupting shape, so the fixed `fallback` return must leave `artifacts.spec` untouched.

`python3 test.py` stays the entrypoint and must pass.

## Non-goals

- No caller-owned output contract, in `routing.json` `prompt` strings or anywhere else.
- No contract fields for `describe`, `spec`, or `subtasks` — none showed friction, and inventing contracts to prove a pattern is the speculation this audit avoided.
- No typed field for the review verdict or the sync outcome.
- No validation of returns or artifacts.
- No change to `process`, `decisions`, `suggestions`, or the archive path.
- No new consent gate on `close`, and no restored integrate handoff file.
- No reopening of ad-hoc dispatch, `--mode adhoc`, or check-gate.

## Acceptance

- A new archive report contains no `meta.source_context`, `outcome.status`, or `outcome.final_artifact`, and `outcome` carries `target` and `pushed_branch`.
- Archiving a task with no `artifacts.story` succeeds and writes no `story.md`.
- `completed_status` appears nowhere in `.cursor/`, `tests/`, or the four live files named above.
- A sheep return with non-empty `open_questions` and no `next_step` leaves `task.next_step` unchanged.
- A review return with `open_questions` and `next_step: execute` advances to `execute`.
- A sheep return with empty `open_questions` advances by routing.
- `sheep-fallback` returns its harness failure as an open question, returns no `artifact`, and position holds.
- A fallback during `spec` leaves `artifacts.spec` pointing at the spec file.
- `sheep-start` returns only `worktree`, `open_questions`, and `summary`, and no `sheep-status` runs after it; `bootstrap-context.py` still reports `next_step: describe`.
- No live file presents `current-task/syncs/` or `current-task/integrates/` as a written output.
- `close` runs without a tail gate and still refuses to run without Nicki's confirm.
- `python3 test.py` passes.

## Archive

This spec is part of the change set and must be included when the task is archived. Archiving it is also the dogfood: the run must produce a report with the shrunken `meta` and `outcome`, and must not block on a missing `story.md`.
