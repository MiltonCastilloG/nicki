# Design: Ad-hoc is direct sheep invocation

Date: 2026-08-05  
Status: **designed**  
Slug: `adhoc-direct-sheep-invocation`  
Related: [`2026-08-05-retire-check-gate-design.md`](2026-08-05-retire-check-gate-design.md), [`2026-08-01-artifact-ownership-and-position-design.md`](2026-08-01-artifact-ownership-and-position-design.md), [`docs/flexibility.md`](../../flexibility.md)

## Problem

`--mode adhoc` was built as a *write shape* on the task path: run a step out of band, record the artifact pointer, append `task.side_effects[]`, leave position untouched. That makes ad-hoc a strictly-more-demanding form of normal work — it needs a registered task, a worktree, and an existing `status.json` (`update-status.py` fails with "adhoc mode needs an existing status.json").

    10|Ad-hoc exists for the opposite reason: to run a sheep at any time, with no prerequisite beyond instructions. Normal and jump are the modes that legitimately require a task.

Framed correctly, ad-hoc is not a mode at all. It is **invoking a sheep directly** — a decision made *before* any pipeline routing, not a variant of pipeline routing.

## Goal

- Ad-hoc requires **nothing** but instructions: no task, no worktree, no `status.json`, no bootstrap, no status write.
- Move ad-hoc out of Nicki: the **parent agent** spawns the sheep directly.
- Nicki keeps only the modes that need a task: `normal` and `jump`.
- Delete `--mode adhoc` from the harness rather than leaving a second meaning alive.
    20|
## Decision summary

| Topic | Decision |
|---|---|
| What ad-hoc means | Direct sheep invocation by the parent agent |
| Who dispatches | Parent agent (not Nicki) |
| Preroute | The existing "Nicki or not" rule; ad-hoc is the not-Nicki branch, upgraded from "attach a skill" to "spawn the sheep" |
| Pipeline state on ad-hoc | None written — no bootstrap, no `sheep-status`, no `side_effects` |
| Consent | Card-free spawn, except an explicit yes before git sheep (`sheep-sync`, `sheep-integrate`) |
| Document output path | User's path when given, else under `docs/adhoc/`; **archive** always `<prefix>/docs/archive/<slug>/` (caller passes `prefix` + `slug`) |
    30|| Nicki modes | `normal`, `jump` only |
| `--mode adhoc` | **Removed** from `MODES` and `update-status.py` |
| `task.side_effects[]` | Kept — jump still logs there; historical ad-hoc rows stay readable |

## Two disjoint paths

| Path | Driver | Flow | Needs a task |
|---|---|---|---|
| **Pipeline** | Nicki | `bootstrap-context.py` → card → spawn sheep → `sheep-status` → `update-status.py` (`normal` \| `jump`) | Yes |
| **Ad-hoc** | Parent agent | pick sheep → pack instructions + output path → Task-spawn → relay return in chat | No |
    40|
The paths never mix. Ad-hoc never touches bootstrap or status; pipeline never pretends to be task-free.

### Why sheep and not skill attachment

The parent agent could always attach a skill (`spec-maker`, `execute-plan`) for ad-hoc work. Spawning the sheep instead gives isolated context and a fixed return JSON, without the parent inheriting the skill's full text. Sheep are already caller-agnostic: each is a short shell that runs one skill, writes only at the path its prompt gives, and returns a fixed JSON shape. Nothing in a sheep reads routing, position, or `status.json` — that was settled by the artifact-ownership work.

## Which sheep may be invoked directly

| Sheep | Direct invoke | Why |
|---|---|---|
    50|| `sheep-describe`, `sheep-spec`, `sheep-subtask`, `sheep-archive` | Yes | Document sheep; write only at the caller's path |
| `sheep-execute`, `sheep-review` | Yes | Operational; no handoff files |
| `sheep-sync`, `sheep-integrate` | Yes, after explicit user yes | Git side effects |
| `sheep-fallback` | Yes | Error recording |
| `sheep-start` | **No** | Creates worktree and registers in `global-status.json` |
| `sheep-close` | **No** | Deletes worktree and unregisters |
| `sheep-status` | **No** | Sole writer of per-task `status.json`; meaningless without a task |

The three excluded sheep own registry or pipeline state and stay Nicki-only.
    60|
## Ad-hoc prompt shape

The parent agent packs:

- **Instructions** — the user's request, verbatim where possible, plus any context they named (paths, diffs, prior chat).
- **Output path** for document sheep — the user's path when given, otherwise under `docs/adhoc/` with a sensible file name matching that sheep's format (story `.md`, spec `.json`, subtasks `.md`, archive directory).
- **Working directory** for operational sheep — the repo or path the user named. Ask once when it is not clear; do not guess.

The sheep returns its normal JSON. The parent agent relays it in chat and stops. No status write, no follow-up sheep.

    70|## Changes

### Rules (the core change)

`.cursor/rules/nicki-default.mdc` and `CLAUDE.md` currently say: *"Never Task-spawn sheep from the parent agent — only Nicki sends sheep"*, with ad-hoc defined as attaching skills. Replace with: ad-hoc work spawns the sheep directly, using the prompt shape above and the allowed-sheep list; `sheep-start` / `sheep-close` / `sheep-status` remain Nicki-only; full pipeline still means invoking Nicki.

### Sheep files

All twelve carry Nicki-specific framing — "You are a **sheep**. Nicki sent you." and "the output path Nicki's prompt gives". Reword caller-neutrally (the prompt / your caller) so a directly-invoked sheep is not told a falsehood about who sent it. Mechanical, one or two lines per file. The three Nicki-only sheep keep language stating they run under Nicki.
    80|
### Nicki

`.cursor/agents/nicki.md`: drop the ad-hoc sentence from Transitions; modes are `normal` and `jump`. Mid-pipeline "sync now" is either a normal `sync` step or a direct `sheep-sync` invoke outside her — she no longer has an out-of-band write.

### Harness

- `routing_write.py`: `MODES = ("normal", "jump")`.
- `update-status.py`: delete the `--mode adhoc` branch (artifact pointer + `_append_side_effect(mode="adhoc")` + position freeze) and the adhoc arm of the "needs an existing `status.json`" check; update the module docstring and `--mode` help. `argparse` `choices` then rejects `--mode adhoc` on its own.
- Keep `_append_side_effect` and `task.side_effects[]` for jump.
    90|
### Skills and formats

- `current-task-update/SKILL.md`, `status-format.md`: ad-hoc is not a status write; `side_effects` documents jump (plus legacy ad-hoc rows).
- `task-archive/archive-format.md`: keep the `side_effects` → `process` rows; drop wording that presents ad-hoc sync as a live write path.

### Tests

- `tests/smoke/status_vocabulary.py`: remove the ad-hoc no-advance and adhoc-on-fresh-worktree cases; keep the `completed_status` enum coverage.
- `tests/smoke/archive_side_effects.py`: drop the assertion that `nicki.md` contains `--mode adhoc`.
   100|- Jump smokes unchanged. `python3 test.py` stays the entrypoint and must pass.

### Docs

`docs/NICKI.md`, `docs/flexibility.md`, `docs/flexibility_next_steps.md`, `README.md`, `.cursor/skills/README.md` — align the live story: two paths, ad-hoc is direct invocation, modes are `normal` and `jump`. Frozen `docs/archive/**` stories are not rewritten.

## Non-goals

- Reintroducing `check-gate.py`, `adhoc_allowed`, or any spawn veto.
- Giving Nicki a second, task-free orchestration loop.
   110|- Synthesizing a fake task or `status.json` so ad-hoc runs can be logged.
- Changing `normal` or `jump` write semantics beyond removing the ad-hoc branch.
- Recording ad-hoc runs anywhere in pipeline state.

## Acceptance

- A sheep can be spawned with instructions alone, in a repo with no registered task, and it runs.
- No `adhoc` in `MODES`, `update-status.py`, `nicki.md`, or live docs; `--mode adhoc` is rejected by `argparse`.
- `sheep-start` / `sheep-close` / `sheep-status` are documented as Nicki-only and not directly invocable.
- Document sheep invoked ad-hoc without a path write under `docs/adhoc/`.
   120|- Jump still logs `side_effects` and sets `next_step`; archive still renders those rows.
- `python3 test.py` passes.

## Archive

This spec is part of the change set and must be included when the task is archived.

**First live test of the new behavior:** immediately after the edits land, invoke `sheep-archive` **directly** — parent agent, no Nicki, no task — passing this spec as input and an output path under `docs/adhoc/`. A successful archive report is the acceptance evidence that ad-hoc direct invocation works end to end. Record the outcome (and any friction) in the archive report.
