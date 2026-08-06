# Design: Sheep stop and ask

Date: 2026-08-06  
Status: **designed**  
Slug: `stop-and-ask`  
Related: [`2026-08-05-delete-unread-outputs-design.md`](2026-08-05-delete-unread-outputs-design.md), [`2026-08-05-adhoc-direct-sheep-invocation-design.md`](2026-08-05-adhoc-direct-sheep-invocation-design.md), [`2026-08-01-artifact-ownership-and-position-design.md`](2026-08-01-artifact-ownership-and-position-design.md)

## Problem

Roughly thirty instructions across twelve skills tell the running agent to ask the user. `story-maker`: "ask organized questions **before** any draft". `spec-maker`: "when in doubt, ask — do not guess". `execute-plan`: "stop and ask with a specific question. Do not guess or fill gaps with your own design choices." `subtask-maker`, `review-execution`, `sync-task`, `integrate-task`, `close-task`, and `close-scope` all say versions of the same thing.

Every one of those skills is run by a sheep, and a sheep is a one-shot subagent with no channel to a human.

The failure is not a deadlock. From the ad-hoc archive dogfood in [`report.md`](../../adhoc/adhoc-direct-sheep-invocation/report.md): *"'No status.json → ask' cannot be satisfied. A directly-spawned sheep has no chat channel, so that line deadlocks every ad-hoc archive. **Treated the prompt as the answer.**"* Told to ask and unable to, the sheep invented. That is the same failure as the hardcoded `pending_integrate` in the companion spec — an instruction that cannot be true, so the agent supplies something plausible.

Two cases are worse than wasteful:

- [`conflict-resolution/SKILL.md`](../../../.cursor/skills/conflict-resolution/SKILL.md) does not merely say "ask", it mandates the tool: *"Ask the user how to resolve it using `AskQuestion`."* Both `sheep-sync` and `sheep-integrate` run it. A sheep sits mid-merge with conflict markers in the tree and no way to reach anyone, while [`nicki.md`](../../../.cursor/agents/nicki.md) carries a hard gate saying conflicts must be resolved with user approval. Both cannot hold.
- [`story-maker/SKILL.md`](../../../.cursor/skills/story-maker/SKILL.md) specifies "revise until explicit user approval" — a multi-turn conversation, not a question. No one-shot subagent can run it.

## Constraint: one file, two hosts

`.claude/agents` and `.claude/skills` are **symlinks** to `.cursor/agents` and `.cursor/skills`. Every sheep file and every skill is the same file on Cursor and Claude Code. So no shared file may name a host-specific tool, and Cursor's Task `resume` parameter is unusable because Claude Code has no equivalent.

This forces the central move, which is the right one anyway: **the sheep emits question data, the orchestrator renders it.** Host specifics stay in the two files that are already host-specific, [`nicki-default.mdc`](../../../.cursor/rules/nicki-default.mdc) and `CLAUDE.md`.

## Decision summary

| Topic | Decision |
|---|---|
| Who asks the human | The orchestrator — Nicki on the pipeline, the parent agent ad-hoc. Never a sheep |
| How a question travels | Structured entries in the return's `open_questions` |
| Question entry | `question`, optional `options`, optional `context`. No schema, no validator |
| Host tool | Named only in `nicki-default.mdc` and `CLAUDE.md` |
| Continuation | Fresh spawn carrying the answers; disk carries the work state |
| Pause file | New `pause-context` skill; caller-named path; read only when the caller says resume; deleted on completion |
| `describe` | Escalates — Nicki interviews in chat, the sheep writes the approved story |
| Merge conflicts | Stay with the sheep — it pauses on the conflicted tree, the orchestrator relays hunks, the sheep applies the answers |
| Skill "ask" lines | Rewritten to "return the question in `open_questions` and stop" |
| `reviews/`, `review-validations/` | Deleted, including the `create-worktree.py` mkdir |

## Who asks, and how the question travels

A sheep that needs input returns it as a structured entry in `open_questions` and writes nothing. `update-status.py` already passes dict entries through untouched and wraps bare strings, so the carrier exists.

An entry carries `question` (required), `options` (optional — short candidate answers, so the orchestrator can offer a choice rather than an essay prompt), and `context` (optional — what the sheep found that raised the question). Nothing parses these fields; the only consumer is the orchestrator, an LLM. Per the principle established in the companion spec, a vocabulary needs defining only where a script matches it exactly, so there is no schema and no validator here.

The orchestrator renders the entry with whatever its host provides and re-spawns the sheep with the answers. Asking one question at a time is an orchestrator rendering choice, not a sheep concern — the sheep returns what it knows, and if the answers raise more, the next round returns more.

This dovetails with the companion spec's position rule: non-empty `open_questions` holds `next_step`. A paused sheep therefore holds its own step automatically, and the re-spawn runs the same step again.

## The `pause-context` skill

A new skill at `.cursor/skills/pause-context/SKILL.md`, available to every sheep and used by the few that need it.

**Trigger is the caller, never the file.** The caller packs a pause path when it sends `spec` or `subtasks` — the two sheep whose exploration is expensive to repeat. The sheep writes that file only when it stops with a question, and **reads it only when the caller's prompt says to resume from it**. A file that merely exists means nothing. This keeps path ownership intact and removes the obvious hazard: a crashed run cannot leave a landmine that silently resumes stale work.

**Content is markdown with no schema** — what was explored, what was settled, what remains, and the question that stopped it.

**It is not a handoff.** The artifact-ownership change deleted `syncs/`, `integrates/`, and `review-validations/` because they recorded *completed* steps and duplicated position. A pause file records *incomplete* work. To keep the distinction from eroding: it exists only while a sheep is paused, the sheep deletes it on completion, it never appears in `status.artifacts`, and nothing downstream may read it. The day something reads it as a record, it has become a handoff.

**Most sheep will never use it.** `execute` already has one — the subtask checklist with `- [x]` marks survives the spawn and the next sheep resumes at the first unchecked line; `review` has `## Fix`. The git sheep have the conflicted tree. `start`, `close`, `status`, and `fallback` are atomic. `describe` escalates. The real users are `spec` and `subtasks`, whose exploration is expensive to repeat.

## `describe` escalates to the orchestrator

Nicki conducts the Gherkin interview in chat, drafts, and gets approval; then `sheep-describe` writes the approved story at her path. She is `readonly: true`, so she cannot write it herself — the division is exactly right.

This restores an archived intent rather than inventing one: the `nicki/05` work shipped "ask-before-draft · chat-only Gherkin", and `nicki.md` already relays review fix lines and waits for approval before sending `sheep-subtask`. Rules 2–4 of `story-maker` (ask organized questions, draft in memory, revise until approval) move to Nicki's side of the boundary; the skill keeps its writing rules and its refusal to invent unstated specifics.

## Merge conflicts stay with the sheep

`sheep-sync` and `sheep-integrate` stop at the first conflict with the working tree untouched, and return the conflict inventory as question entries — file, hunk, and a short summary of both sides, with `options` naming the candidate resolutions. The orchestrator relays them and collects decisions. The re-spawned sheep opens the same conflicted tree, which is still on disk, and applies the answers.

Nothing is lost between rounds because nothing was in the sheep's head. Git ownership stays in one agent instead of splitting a half-finished merge between the sheep that started it and someone else who finishes it.

`conflict-resolution/SKILL.md` drops the `AskQuestion` mandate and becomes: inventory the conflicts, return them as questions, stop; on resume, apply the caller's resolutions verbatim and never infer. The hard gate in `nicki.md` stays exactly as written — it is now satisfiable.

## The "ask" cleanup

Every instruction telling a sheep-run skill to ask the user is rewritten to "return the question in `open_questions` and stop". This covers [`story-maker`](../../../.cursor/skills/story-maker/SKILL.md), [`spec-maker`](../../../.cursor/skills/spec-maker/SKILL.md) and its [`spec-format.md`](../../../.cursor/skills/spec-maker/spec-format.md), [`subtask-maker`](../../../.cursor/skills/subtask-maker/SKILL.md) with `spec-input.md` and `subtask-input.md`, [`execute-plan`](../../../.cursor/skills/execute-plan/SKILL.md), [`review-execution`](../../../.cursor/skills/review-execution/SKILL.md) and its `review-format.md`, [`sync-task`](../../../.cursor/skills/sync-task/SKILL.md), [`integrate-task`](../../../.cursor/skills/integrate-task/SKILL.md), [`close-task`](../../../.cursor/skills/close-task/SKILL.md), [`close-scope`](../../../.cursor/skills/close-scope/SKILL.md), [`conflict-resolution`](../../../.cursor/skills/conflict-resolution/SKILL.md), [`current-task-update`](../../../.cursor/skills/current-task-update/SKILL.md), and [`start-task`](../../../.cursor/skills/start-task/SKILL.md).

Missing-input cases ("ask if worktree path is missing") are the same rule: return the question, write nothing.

The three sheep files carrying "ask if you cannot proceed" — `sheep-start`, `sheep-close`, and `sheep-fallback` — get the same treatment.

## The `reviews/` and `review-validations/` graveyard

Nothing has written either directory since the artifact-ownership change, and the stale references now actively contradict each other.

| Where | What is stale |
|---|---|
| [`create-worktree.py`](../../../.cursor/skills/start-task/scripts/create-worktree.py) line 439 | still creates `reviews/` and `review-validations/` in every new worktree |
| [`current-task-update/SKILL.md`](../../../.cursor/skills/current-task-update/SKILL.md) line 122 | instructs setting `artifacts.review_validation` after review, while `tests/smoke/routing_write.py` line 104 asserts review must **not** set it |
| [`archive-format.md`](../../../.cursor/skills/task-archive/archive-format.md) line 31 | builds a `process` row from `artifacts.review_validation`, which can never exist |
| [`review-format.md`](../../../.cursor/skills/review-execution/review-format.md) line 5 | declares a default path `current-task/reviews/<slug>.json`, though review writes no file |
| [`current-task-context-format.md`](../../../.cursor/skills/current-task-update/current-task-context-format.md) | the tree, both artifact table rows, and the JSON example |
| [`README.md`](../../../README.md), [`docs/NICKI.md`](../../NICKI.md), [`docs/WORKFLOW-DIAGRAMS.md`](../../WORKFLOW-DIAGRAMS.md) | review artifact rows, diagram nodes, and the `current-task/` tree |

`validation/SKILL.md` already marks itself and `validation-format.md` as historical reference; both stay as they are.

## Non-goals

- No host-specific tool named in any shared agent or skill file.
- No reliance on Cursor's Task `resume`, or on any form of subagent interactivity.
- No schema, enum, or validator for question entries or the pause file.
- The pause file never becomes a handoff and never appears in `status.artifacts`.
- No reintroduction of `reviews/`, `review-validations/`, or any operational handoff.
- No change to the execute and sync consent gates, or to the conflict hard gate.
- No pause mechanism for `execute` — the subtask checklist already is one.

## Acceptance

- No shared agent or skill file names a host-specific ask tool; the tool is named only in `nicki-default.mdc` and `CLAUDE.md`.
- Every "ask the user" instruction in a sheep-run skill reads "return the question and stop".
- A sheep needing input returns a structured `open_questions` entry, writes no artifact, and its step holds.
- The orchestrator renders the question with its host's tool and re-spawns with the answers.
- A `spec` sheep resumes from a caller-named pause file without re-exploring, and the file is gone once it completes.
- A pause file present on disk but not named in the prompt is ignored.
- `describe` produces an approved story where Nicki ran the interview and the sheep wrote the file.
- A merge conflict returns the conflict set as questions with the tree intact; the re-spawned sheep applies the resolutions.
- A newly created worktree contains no `reviews/` or `review-validations/` directory.
- No live file references `artifacts.review_validation`.
- `python3 test.py` passes.

## Archive

This spec is part of the change set and must be included when the task is archived.
