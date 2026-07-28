# Harness gate bugs — combined report

Date: 2026-07-28. Replaces the deleted per-bug notes (`bug_1`–`bug_3`).
Recurrence evidence for Finding 5: [`fallback_bug_investigation.md`](fallback_bug_investigation.md).

Scope: `check-gate.py`, `gates.py`, `gate_utils.py`, `bootstrap-context.py`,
`update-status.py`, `routing.json`, `test.py`, `tests/smoke/`.

## Summary

Four reported bugs, one shape. The harness has two halves: prose the agents
read, and Python that decides. They drifted apart, and nothing tests the
deciding half. `python3 test.py` passes all seven smoke modules today while a
gate bug in `main` makes `integrate` unreachable for every task.

| # | Finding | State |
|---|---------|-------|
| 1 | `gate_integrate` resolves the archive path against the worktree; archive is workspace-root-relative | Real, reproduced, unbypassable |
| 2 | `completed_status` must be the literal `"complete"` or `completed_steps` silently skips the append | Real, reproduced; reported mechanism was wrong |
| 3 | `routing.json` per-step fields are unread by any script | Real; caused a wrong root cause and a wasted investigation cycle |
| 4 | `bootstrap-context.py` still crashes on a malformed artifact | Real, reproduced; the 07-26 fix landed on one of two entry points |
| 5 | Sheep hand-author prose YAML with no quoting rule | Real, recurring; impact now capped at `check-gate.py` only |

## Finding 1 — integrate gate cannot see the archive

`gate_integrate` (`gates.py:120`) calls `artifact_path(worktree, status,
"archive")`. `artifact_path` (`gate_utils.py:86-88`) is unconditionally
`worktree / rel`. The archive value is workspace-root-relative by design — the
report must outlive the worktree — so the join builds a path that structurally
cannot exist.

`gate_integrate`'s fourth parameter is named `_` and never read, so
`--override` is silently discarded. No CLI bypass exists.

Verified: fixture with `artifacts.archive:
"docs/archive/demo/report.json"`, file present at the workspace root, both
`--user-confirmed --override` passed.

```
{"allowed": false, "reason": "integrate gate: archive artifact missing", ...}
```

Copy the same file to `<worktree>/docs/archive/demo/report.json` and it flips
to `allowed: true`. Systemic — every task hits it after a normal archive.

## Finding 2 — `completed_status` is an undocumented load-bearing enum

`update-status.py:212` appends to `completed_steps` only when
`completed_status == "complete"`, an exact string match. Verified against three
inputs on the same fixture:

| Input | `current_step` | `completed_steps` | stdout |
|-------|----------------|-------------------|--------|
| `completed_step: acceptance`, `completed_status: complete` | `acceptance` | `[review, acceptance]` | `written: true` |
| `completed_step: acceptance`, `completed_status: accepted` | `acceptance` | `[review]` | `written: true` |
| `next_step` only | `review` (preserved) | `[review]` | `written: true` |

Row 2 is the reported state exactly, and it reports success with no warning.
Downstream, `gate_sync` and `gate_done` read `completed_steps`, so an unknown
status value denies the rest of the pipeline.

The field is documented in five places as optional with an example value, and
nowhere as a closed set. `routing.json` `sheep_return_contract` lists it under
`optional_fields` with no allowed values; only `on_blocked` implies a second
value.

Aggravating factor, not the mechanism: `acceptance` has `sheep: null`, so there
is no sheep return to forward verbatim and Nicki hand-authors the field herself.
The one step with no sheep is the step whose bookkeeping the next gate depends
on.

## Finding 3 — `routing.json` looks like config, is mostly prose

Grep every `.py` in the repo for `expected_artifact`, `artifact_key`,
`default_next_step`, `nicki_only`, `secondary_artifact_key`, `also_writes`,
`skip_status_update` — zero hits. Only `sheep` and `user_confirm` are read
(`check-gate.py:44-45`, `bootstrap-context.py:69-76`). `gates.py` never imports
`load_routing`.

Consequence: an early investigation blamed the `integrate` deny on a stale
`expected_artifact` extension (`report.json` vs a then-actual `report.yaml`) —
a reasonable read of a file that presents as machine config. It cost a full
second investigation to retract. The extension is now consistent
post-migration; the finding is that the file's authority is fictional, not that
one string was stale.

## Finding 4 — bootstrap still fails open on a bad artifact

The 07-26 defensive-parse fix landed on `check-gate.py` only.
`bootstrap-context.py` calls the same `readiness()`; `ArtifactParseError`
subclasses `ValueError`, so it is caught at line 86 and returned as exit 1 with
a stderr string and empty stdout. Per `nicki.md`, empty/non-contract stdout is a
harness failure requiring `sheep-fallback`.

Verified side by side on a truncated validation artifact:

```
bootstrap-context.py → stderr "r1-validation.json: Expecting ',' delimiter…", exit 1, no stdout
check-gate.py        → {"allowed": false, "reason": "readiness parse error: …"}, exit 1
```

Bootstrap is a hard-gate on every Nicki response, so one malformed artifact
turns every turn into a fallback dispatch.

## Finding 5 — prose YAML quoting

Unchanged from `fallback_bug_investigation.md`: `spec-maker` and `execute-plan`
hand-author YAML with no quoting rule, so a `Label: sentence` scalar parses as a
nested mapping. Two real incidents, two sheep, two gates, 8 days apart.
`check-gate.py` now denies cleanly on it, so blast radius is capped there — but
Finding 4 means the same content still hard-blocks bootstrap. The JSON migration
(`8fa5569`) reduces exposure; it does not remove it, since sheep still
hand-author artifacts against a schema.

## Why these recur

- **Gates are untested.** 12 of 13 gate functions have zero coverage. The one
  tested gate is `gate_archive` — the one that had a bug before — and its test
  (`scripts/smoke-archive-gate.py`) is not imported by `test.py`, so it runs only
  by hand.
- **The suite that runs tests the wrong layer.** `git_tail.py` and
  `readiness_mapping.py` are mostly file-exists and doc-substring assertions.
  `readiness_mapping.py` writes a temp file and counts the string it just wrote.
  Its fixture checks are guarded by `if path.is_file()`, so they vanish instead
  of failing. No CI. The `./test.sh` entrypoint referenced in
  `harness-alignment-subagents.md:290` does not exist.
- **Bug reports replaced fixes.** All four docs close with "add a fixture to
  `docs/tasks.md` #10." #10 is the only open P2 harness item and stayed open
  across every incident.
- **`--override` keeps broken gates alive.** Findings 1 and 2 were both worked
  around with `--override`; the task archived and closed. The only gate that got
  a correct root cause is the one whose override is broken.
- **Path scope is unwritten.** `archive` is workspace-root-relative; every other
  artifact is worktree-relative. `artifact_path()` knows one rule. No format doc
  states the difference.
- **Migrations go big-bang mid-flight.** `8fa5569` flipped every artifact and
  return contract from YAML to JSON across 39 files on the same day as these
  reports, with a task in flight holding `.yaml` artifacts.

## Follow-ups

Ordered. Each is a prerequisite for the direction below.

1. **Fix `gate_integrate` archive resolution.** Teach artifact resolution about
   scope (worktree-relative vs workspace-root-relative) instead of one blind
   join. Wire the override parameter or drop it from the signature. Hard blocker
   in `main` today.
2. **Close `docs/tasks.md` #10 with real gate fixtures.** One per finding above,
   run through `check-gate.py`, pass and fail cases. Import them plus
   `smoke-archive-gate.py` into `test.py`. Delete or rewrite the
   doc-substring assertions in `git_tail.py` and `readiness_mapping.py`; drop the
   `if path.is_file()` guards so a missing fixture fails.
3. **Validate `completed_status` in `update-status.py`.** Closed set, unknown
   value returns `written: false` with an error naming the field. Document the
   set in `status-format.md` and `routing.json`.
4. **Give `bootstrap-context.py` a contract-safe failure path**, same as
   `check-gate.py`: always print contract JSON, carry the parse error in a field.
5. **Resolve the `routing.json` fiction.** Either read the per-step fields in the
   scripts or move them to Markdown. Do not leave prose shaped like config.

## Direction — flexibility without losing the harness

Goal: Nicki stops being a strict linear march. Two capabilities, both built on
the existing scripts. `status.json` stays the source of truth for pipeline
state; `check-gate.py`, `update-status.py`, `bootstrap-context.py` stay
authoritative. Nothing moves back into prose.

### A. Out-of-band steps that do not move the workflow

Case: sync mid-`execute`. Today `--override` allows the sheep, then
`sheep-status` writes `completed_step: sync` / `next_step: archive` and the task
believes it is in the git tail with implementation half done. The step and the
bookkeeping are welded together.

Needed: an explicit ad-hoc invocation that is still gated but does not advance
state.

- Split gates into two classes. **Safety** gates guard irreversible effects
  (push to main, merge, worktree delete) and always hold. **Sequence** gates
  guard bookkeeping (`acceptance` recorded before `sync`) and are waivable in
  ad-hoc mode. The split half-exists already and is never named: `gate_sync`
  lets `--override` waive the acceptance check but not the readiness block,
  `gate_integrate` ignores override entirely, and `close`/`integrate` lean on
  `--user-confirmed` for the same job. Name the two classes and apply them
  uniformly.
- Add per-step metadata for this — `irreversible`, `sequence_gate`,
  `adhoc_allowed` — and actually read it. Same work as follow-up 5.
- Add an ad-hoc write mode: record the artifact pointer and the side effect,
  leave `current_step`, `next_step`, and `completed_steps` untouched. Depends on
  follow-up 3 having a real status vocabulary to say "ran, did not advance".

### B. Source of truth from outside the workflow

Case: a spec produced by the `brainstorm` skill, outside the pipeline. Today
`gate_subtasks` wants `artifacts.spec` under the worktree with empty
`open_questions`, so an external spec means faking `describe` and `spec`.

Needed: artifact adoption.

- Register an external path as an artifact pointer with provenance (origin,
  external flag). Gates validate **shape** — parses, root is an object,
  `open_questions` empty — not provenance.
- Requires scope-aware artifact resolution, so follow-up 1 is the foundation
  here, not just a bug fix. External sources of truth and the archive path have
  the same underlying need.
- Mark the producing step satisfied-by-adoption rather than completed by a
  sheep. Again a status-vocabulary change (follow-up 3).

### Sequencing

Both features multiply gate paths. Adding them on top of an untested gate layer
with a blunt override reproduces exactly the failure mode this report documents.
Follow-ups 1–3 first, then A, then B.
