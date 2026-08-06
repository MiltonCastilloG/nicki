# Design: Outputs shrink to what is knowable and read

Date: 2026-08-05  
Status: **designed**  
Slug: `knowable-outputs`  
Related: [`2026-08-05-adhoc-direct-sheep-invocation-design.md`](2026-08-05-adhoc-direct-sheep-invocation-design.md), [`2026-08-01-artifact-ownership-and-position-design.md`](2026-08-01-artifact-ownership-and-position-design.md), handoff [`docs/adhoc/adhoc-direct-sheep-invocation/output_problem_example.md`](../../adhoc/adhoc-direct-sheep-invocation/output_problem_example.md)

## Problem

Path ownership is settled: the caller packs where to read and where to write, and sheep obey. Output *shape* was the open half — the archive dogfood hit a hardcoded `outcome.status: pending_integrate`, a `story.md` the caller could not supply, an empty forced `process`, and a `meta.source_context` documented as one value.

The obvious fix is a caller-owned output contract, mirroring how inputs work. Auditing the fields first says otherwise. Most of them do not need an owner — they need deleting.

## Audit

Nothing in the repo parses `report.json`. No script, no test, no skill. The pipeline uses only its **path**, stored as `status.artifacts.archive`, so `sync` can flip `next_step` from `archive` to `integrate` via `next_step_when_archived`. The report is a human document with a machine-checked filename.

Judged as "what does a human learn from this field", three fail:

| Field | Evidence |
|---|---|
| `meta.source_context` | `current-task/status.json` in 17 of 20 existing archives — a constant in-workflow, with no reader |
| `outcome.status` | Four vocabularies across archives (`archived`, `integrated`, `merged`, `pending_integrate`) with no enum. Archive runs at step 4 of `sync → archive → sync → integrate → close`, so the work provably has not integrated when the report is written. `pending_integrate` is the only truthful in-workflow value |
| `outcome.final_artifact` | Points at `current-task/integrates/<slug>.yaml`, a file that does not exist yet — a prediction recorded as fact |

Two reported frictions are smaller than they looked. The `story.md` problem is a self-contradiction inside one file: [`archive-format.md`](../../../.cursor/skills/task-archive/archive-format.md) line 10 says "copy from `artifacts.story` when present", line 143 lists it as required. The `suggestions.area` complaint was stale — `orchestration` is already in the enum.

`completed_status` fails the same test from the other direction. `completed_steps` is dropped on every write ("position + artifacts are enough"), and `_init_status` discards the field. Its one surviving effect is that `blocked` makes `_derive_next_step` hold `next_step` instead of advancing — which is a sheep naming pipeline position by proxy, the one act every sheep file forbids.

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

`completed_status` is removed everywhere it appears.

**[`routing.json`](../../../.cursor/skills/nicki/routing.json)** — drop `completed_status` from `sheep_return_contract.optional_fields`, drop `completed_status_values`, and rewrite `on_blocked` to: populate `open_questions`; position holds.

**[`update-status.py`](../../../.cursor/skills/current-task-update/scripts/update-status.py)** — delete `COMPLETED_STATUSES`, its validation branch, the module docstring line, the unused `_init_status` parameter, and both call-site arguments. `_derive_next_step` takes `open_questions` in place of `completed_status` and applies this precedence:

1. An explicit `next_step` in the summary wins. This is Nicki's review verdict (`acceptance` / `execute` / `review`) and must keep working — a review that reports findings *and* routes to `execute` still advances.
2. Otherwise, non-empty `open_questions` returns the existing `next_step`, falling back to the completed step.
3. Otherwise, routing derives the next step.

Order matters. Today `blocked` is checked before the explicit override; inverting the first two is what protects review. Document sheep never send `next_step`, so they freeze exactly as they do now.

Jump mode and position-only writes are untouched — neither reaches `_derive_next_step`. Jump sets `next_step` to its target directly; position-only writes take `next_step` from the summary as the authority.

**Sheep files** — the Return section of all twelve `.cursor/agents/sheep-*.md` drops `completed_status`. What stays is what each sheep already says about `artifact` (a path, or none) plus `open_questions` and `summary`.

**[`sheep-fallback.md`](../../../.cursor/agents/sheep-fallback.md)** — today it returns `completed_status: blocked` with `open_questions: []`, which under the new rule would advance. It records the harness failure as its open question instead. Nicki still holds the blocked step via `--step`.

The `"success"` value returned by the first live dogfood becomes unrepresentable: there is no enum left to invent.

## Docs and tests

Remove the enum from the four live files that teach it: [`current-task-update/SKILL.md`](../../../.cursor/skills/current-task-update/SKILL.md) (the return field list, the closed-set paragraph, the JSON example), [`status-format.md`](../../../.cursor/skills/current-task-update/status-format.md), [`docs/flexibility.md`](../../flexibility.md), and [`docs/NICKI.md`](../../NICKI.md).

Frozen records keep their history and are not rewritten: `docs/archive/**`, earlier specs in `docs/superpowers/specs/`, and the superseded write-ups (`docs/harness-alignment-subagents.md`, `docs/harness-gate-bugs.md`).

`tests/smoke/status_vocabulary.py` replaces its enum coverage with the freeze rule: non-empty `open_questions` holds `next_step`; an explicit summary `next_step` still wins; empty `open_questions` advances by routing. `tests/smoke/routing_write.py` and `tests/smoke/jump_mode.py` drop the field from their fixtures. `python3 test.py` stays the entrypoint and must pass.

## Non-goals

- No caller-owned output contract, in `routing.json` `prompt` strings or anywhere else.
- No contract fields for `describe`, `spec`, or `subtasks` — none of them showed friction, and inventing contracts to prove a pattern is the speculation this audit avoided.
- No validation of returns or artifacts.
- No change to `process`, `decisions`, `suggestions`, or the archive path.
- No reopening of ad-hoc dispatch, `--mode adhoc`, or check-gate.

## Acceptance

- A new archive report contains no `meta.source_context`, `outcome.status`, or `outcome.final_artifact`, and `outcome` carries `target` and `pushed_branch`.
- Archiving a task with no `artifacts.story` succeeds and writes no `story.md`.
- `completed_status` appears nowhere in `.cursor/`, `tests/`, or the four live files named above.
- A sheep return with non-empty `open_questions` and no `next_step` leaves `task.next_step` unchanged.
- A review return with `open_questions` and `next_step: execute` advances to `execute`.
- A sheep return with empty `open_questions` advances by routing.
- `sheep-fallback` returns its harness failure as an open question and position holds.
- `python3 test.py` passes.

## Archive

This spec is part of the change set and must be included when the task is archived. Archiving it is also the dogfood: the run must produce a report with the shrunken `meta` and `outcome`, and must not block on a missing `story.md`.
