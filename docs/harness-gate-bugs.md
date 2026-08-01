# Harness gate bugs — combined report

Date: 2026-07-28. Replaces the deleted per-bug notes (`bug_1`–`bug_3`).
Recurrence evidence for Finding 5: [`fallback_bug_investigation.md`](fallback_bug_investigation.md).
Target these fixes serve: [`flexibility.md`](flexibility.md).

**Note (2026-07-31):** `deny_sequence` / `gate_class` / `--override` / unused `irreversible` routing flag were removed — see [`2026-07-31-drop-sequence-and-override-design.md`](superpowers/specs/2026-07-31-drop-sequence-and-override-design.md). Historical sections below still describe the old waiver model.

Scope: `check-gate.py`, `gates.py`, `gate_utils.py`, `bootstrap-context.py`,
`update-status.py`, `routing.json`, `test.py`, `tests/smoke/`.

## Summary

Four reported bugs, one shape. The harness has two halves: prose the agents
read, and Python that decides. They drifted apart, and nothing tests the
deciding half. `python3 test.py` passes all seven smoke modules today while a
gate bug in `main` makes `integrate` unreachable for every task.

None of these are isolated defects. Each one sits on the path to the flexibility
goal, so fixing them is not cleanup before the real work — it is the first part
of the real work.

| # | Finding | State | Flexibility impact |
|---|---------|-------|--------------------|
| 1 | `gate_integrate` / archive path scope | **Corrected 2026-07-31** | 07-28 made archive Nicki-workspace-root-relative; that was wrong for multi-repo. Archive is worktree-relative again (project repo → main via integrate). |
| 2 | `completed_status` must be the literal `"complete"` or `completed_steps` silently skips the append | **Fixed 2026-07-29** (follow-up 3) | Closed enum plus a `--mode` axis; ad-hoc writes no longer move position. |
| 3 | `routing.json` per-step fields are unread by any script | **Mostly fixed / mitigated 2026-07-29** (follow-up 5) | Was a direct block; core fields (`default_next_step`, `artifact_key`, `adhoc_allowed`, `user_confirm_required`, `gate_class`, …) are now read. Residual drift risk is suite-guarded, not prose-only. |
| 4 | `bootstrap-context.py` still crashes on a malformed artifact | **Fixed 2026-07-29** (follow-up 4 — bootstrap soft-fail) | Was worse on every response; malformed readiness now yields contract JSON + `readiness_error`, exit 0 — not a harness failure. |
| 5 | Sheep hand-author prose YAML with no quoting rule | Open — optional polish; impact capped at `check-gate.py` | Sideways. `check-gate.py` denies cleanly; bootstrap no longer amplifies the same parse error (Finding 4 fixed). Sheep quoting rules remain optional hardening. |
| 6 | `sync` and `archive` gates allow with no user consent; the rule is prose-only | **Fixed 2026-07-29** (follow-up 6) | Consent is routing data enforced once; ad-hoc gets no exemption. |
| 7 | `rerun_review` readiness is documented but absent from `routing.json`; the gate crashed on it and it never blocked sync | **Fixed 2026-07-28** (follow-up 2) | Found by writing the gate matrix — the coverage gap was hiding it. |

## Finding 1 — integrate gate cannot see the archive

> **Correction 2026-07-31.** The original bug was writers putting archive under
> the Nicki workspace while gates joined `worktree / rel`. The 07-28 follow-up
> inverted that: gates looked at the Nicki root. Correct end state (skills always
> said this): archive is **worktree / project-repo** `docs/archive/<slug>/`, then
> second sync + integrate merge it to main. Do not write under the Nicki
> workspace `docs/archive/`.

Historical notes below describe the 07-28 diagnosis; see follow-up 1 for the
07-31 correction.

`gate_integrate` (`gates.py`) calls `artifact_path(worktree, status,
"archive")`. Pre-07-28, `artifact_path` was unconditionally `worktree / rel`.
When writers put the report only at the Nicki workspace root, the join missed it.

Verified then: fixture with `artifacts.archive:
"docs/archive/demo/report.json"`, file present at the workspace root, both
`--user-confirmed --override` passed.

```
{"allowed": false, "reason": "integrate gate: archive artifact missing", ...}
```

Copy the same file to `<worktree>/docs/archive/demo/report.json` and it flips
to `allowed: true`. That worktree location is the intended one.

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

**State (2026-07-29):** Mostly mitigated in follow-up 5. Scripts now read
`default_next_step`, `expected_artifact`, `artifact_key`, `adhoc_allowed`,
`user_confirm_required`, `gate_class`, and related policy fields; the gate
contract echoes `next_step` and `artifact`. The narrative below is the
pre-fix drift that caused a wasted investigation — kept for history.

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

**State (2026-07-29):** Fixed in follow-up 4. Bootstrap soft-fails: contract
JSON on stdout with `readiness` null and optional `readiness_error`, exit 0 —
not a harness failure. Nicki keeps routing from the same stdout.

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
`check-gate.py` now denies cleanly on it, so blast radius is capped there.
Bootstrap no longer hard-blocks on the same readiness parse error (Finding 4
fixed). Optional polish remains: a quoting rule for sheep-authored YAML would
reduce incidents at the gate. The JSON migration (`8fa5569`) reduces exposure;
sheep still hand-author artifacts against a schema.

## Finding 6 — consent is declared everywhere, enforced almost nowhere

Three layers hold the consent rule and none of them agree.

| Layer | Holds |
|---|---|
| `nicki.md` | "NEVER DO THIS STEP WITHOUT USER EXPLICITLY SAYING" for `sync`. Prose only. |
| `routing.json` `user_confirm` | The sentence to say. Returned in the gate contract as advice (`check-gate.py:44`), never enforced. |
| `gates.py` | Hardcoded `user_confirmed` checks in 4 of 13 gates: `start`, `review` (partial only), `integrate`, `close`. |

`gate_sync` and `gate_archive` check nothing. Verified on a fixture with
`acceptance` in `completed_steps` and `readiness: ready_for_acceptance`, with no
`--user-confirmed`:

```
--step sync    → {"allowed": true, "sheep": "sheep-sync", "user_confirm": "local commit, merge main into feature branch, push feature branch"}
--step archive → {"allowed": true, "sheep": "sheep-archive", "user_confirm": "write task archive to docs/archive"}
```

The loudest rule in the system is the one the harness does not enforce. Purest
instance of this report's thesis: prose shouts, script shrugs.

## Finding 7 — a documented readiness value routing never knew about

`status-format.md` lists four readiness values and states that `rerun_review`
blocks `sync-task`. `routing.json` `readiness_routing` declared three, and
`gate_utils.BLOCKED_READINESS` held two. Two consequences, both found by writing
the follow-up 2 matrix rather than by hitting them in a run:

- `check-gate.py` looked up the missing key and called `.get()` on `None`, so any
  readiness step with `rerun_review` denied with
  `gate harness error: 'NoneType' object has no attribute 'get'` — a contract-shaped
  deny carrying a Python error instead of a reason.
- `sync` did not block on `rerun_review`, contradicting the documented table.

Fixed by defaulting the routing lookup, adding the `rerun_review` route
(`route_step: review`, `sync_blocked: true`), and adding it to
`BLOCKED_READINESS`. The matrix asserts both the clean deny and the sync block,
and `readiness_mapping.py` now asserts every documented status has a route.

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
  a correct root cause is the one whose override is broken. (Addressed in
  follow-up 7: a denial now says whether a waiver can even reach it.)
- **Path scope (resolved 2026-07-31).** All artifact pointers including `archive`
  are worktree-relative; see `status-format.md` and follow-up 1.
- **Migrations go big-bang mid-flight.** `8fa5569` flipped every artifact and
  return contract from YAML to JSON across 39 files on the same day as these
  reports, with a task in flight holding `.yaml` artifacts.

## Follow-ups

Ordered. Each is a prerequisite for [`flexibility.md`](flexibility.md), and
names the blocker there it clears. Each states current behavior, target, and a
done-when check so a future session can pick one up cold.

### 1. Scope-aware artifact resolution — **done 2026-07-28; corrected 2026-07-31**

Unblocked flexibility B1.

- **Was (pre-07-28):** `artifact_path()` was `worktree / rel` for every key, but
  some writers put archive under the Nicki workspace root.
- **Was (07-28 “fix”):** `ROOT_SCOPED_ARTIFACTS` forced `archive` to resolve
  against the Nicki workspace root so the report “outlived the worktree.” That
  matched Nicki-as-only-project and broke multi-repo (e.g. jung): sheep correctly
  write `docs/archive/` in the project worktree; integrate then denied missing
  archive at the Nicki root.
- **Now (07-31):** every artifact pointer is worktree-relative, including
  archive. Archive reaches main via second sync + integrate. No
  `ROOT_SCOPED_ARTIFACTS`.
- **Documented:** path-scope rule in `status-format.md` `artifacts`.
- **Proven:** `tests/smoke/gate_paths.py` — archive in worktree allows; absent
  denies; archive only at Nicki workspace root is *not* accepted; worktree-scoped
  `sync` is *not* read from the workspace root.

### 2. Real gate fixtures in `test.py` — **done 2026-07-28**

Closes `docs/tasks.md` #10. Guards every later step.

- **Was:** 12 of 13 gates untested; the one gate test
  (`scripts/smoke-archive-gate.py`) was not imported by `test.py`, so it ran only
  by hand.
- **Now:** `tests/smoke/gates_matrix.py` drives 44 gate cases through
  `check-gate.py` — every one of the 13 gates with at least one allow and one
  deny, plus unparseable artifacts at three gates, a legacy v1 status shape
  (`task.story_artifact` + `history`), a missing `status.json`, and an unknown
  step. Any reason containing `gate harness error` fails the case, so leaked
  internal errors cannot pass as denies. `smoke-archive-gate.py` is deleted — its
  three `pre_push_merge` cases are in the matrix and now actually run.
- **Weak modules rewritten:** `readiness_mapping.py` dropped the doc greps and
  the temp-file test that asserted its own write; it now checks that every
  documented readiness status has a route and that the validation fixtures hold
  the readiness they claim, unguarded. `git_tail.py` dropped the prose greps for
  routing's git-tail sheep assignments. `errors_append.py` lost two assertions
  that tested `shutil.copy` and a dict literal it had just built.
- **Hygiene:** the suite no longer dirties the tree. `errors_append.py` and
  `harness_failure.py` write to temp dirs instead of `tests/fixtures/` and the
  workspace's own `current-task/`; the accidentally-committed fixture output and
  the tracked `__pycache__` are untracked (`.gitignore` already covered both).
- **Proven:** reverting follow-up 1's resolution change, or the Finding 7
  routing default, turns the suite red. Both verified by reverting.
- **Left open:** no CI, so the suite still runs only when someone types
  `python3 test.py`. The `./test.sh` reference in
  `harness-alignment-subagents.md:290` remains stale — `test.py` is the entrypoint.

### 3. Status vocabulary — **done 2026-07-29**

Cleared flexibility A1, A5, B5.

- **Was:** `completed_status` was an open string; anything but `"complete"`
  silently skipped the `completed_steps` append and still reported
  `written: true`.
- **Now:** closed set `complete` | `blocked`, validated before any write. An
  unknown value — including `"COMPLETE"`, `""`, and non-strings — returns
  `written: false` with an error naming the field, and does not create
  `status.json`. Declared in `update-status.py` `COMPLETED_STATUSES`,
  `routing.json` `sheep_return_contract.completed_status_values`, and
  `current-task-update/SKILL.md`; the fixture asserts all three agree.
- **Enum did not grow.** The plan said to add members for "ran, did not advance"
  and "satisfied by external artifact". That would have put position back in a
  field the sheep owns, against flexibility Decisions 1 and 4. Those two cases
  became the `--mode` axis instead — recorded as flexibility Decision 5.
- **`--mode adhoc`** writes the artifact pointer and appends one
  `task.side_effects` entry (step, mode, UTC timestamp, artifact) while leaving
  `current_step`, `next_step`, and `completed_steps` byte-identical. `next_step`
  is not required in that mode, and ad-hoc refuses to initialise a fresh
  `status.json`. `--step` was added in the same pass so the dispatched step name
  can come from Nicki rather than the sheep.
- **Proven:** `tests/smoke/status_vocabulary.py`, wired into `test.py` — both enum
  members, five rejected values, no-advance semantics, side-effect append across
  two runs, unknown `--mode`, and normal mode still requiring `next_step`.

### 4. Contract-safe bootstrap failure — **done 2026-07-29**

- **Was:** `bootstrap-context.py` returned exit 1 with stderr and empty stdout
  on a malformed readiness artifact, which `nicki.md` classified as a harness
  failure — on a script that runs every response.
- **Now:** soft-fail on readiness parse only — always print contract JSON
  (`active_task`, `status_path`, `current_step`, `next_step`, `readiness`,
  `sheep`); set `readiness` null and optional `readiness_error` with the parse
  message; exit 0. Registry / status failures still exit 1 with empty stdout.
  Nicki shows `readiness_error` and continues from the same stdout — no
  `sheep-fallback` dispatch.
- **Proven:** `tests/smoke/bootstrap_contract.py`, wired into `test.py` —
  truncated validation artifact yields contract stdout, `readiness_error` set,
  exit 0; clean readiness omits `readiness_error`.

### 5. Resolve the `routing.json` fiction — **mostly done 2026-07-29**

Implements [`flexibility.md`](flexibility.md) Decision 1 (routing owns
`next_step`). Unblocks A6.

- **Was:** only `sheep` and `user_confirm` were read. Seven other per-step fields
  were prose in a file shaped like config.
- **Now read:** `default_next_step` and a new `next_step_when_archived` via
  `gate_utils.next_step_for(step, status, readiness_status)`, which is the single
  authority on position — including the git tail (first `sync` → `archive`,
  second `sync` → `integrate`) and `review`, whose successor comes from
  `readiness_routing` and is `None` until validation exists.
  `expected_artifact` is read by `gate_utils.expected_artifact_for()` with
  `<slug>` resolved.
- **Echoed:** `check-gate.py` output gained `next_step` and `artifact`, so
  position and output path travel in the gate contract instead of being
  re-derived. Both keys appear on allow and deny (null on deny); required fields
  are unchanged, so `validate-harness-stdout.py` is unaffected.
- **Deleted as duplicates** (content verified present elsewhere): `nicki_only`
  (duplicates `sheep: null`), `also_writes` (in `review-execution/SKILL.md` and
  `review-format.md`), `skip_status_update` (in `nicki.md` twice).
- **Proven:** `tests/smoke/routing_next_step.py`, wired into `test.py` — 15
  resolver cases plus three gate-contract cases.
- **Remainder:** none. `artifact_key` is now read by `update-status.py`
  (`_artifact_key_for`); `secondary_artifact_key` was renamed to the real status
  key `review_input` and remains unused until a sheep returns a second path.
  `start.artifact_key` is `null` (status.json is not an artifacts pointer).
- **Not done here, deliberately:** none — agent prose for the return contract
  landed with flexibility steps 6–7.

### 6. Enforce consent from routing — **done 2026-07-29**

Implements [`flexibility.md`](flexibility.md) Decision 3, and closes Finding 6.

- **Was:** `sync` and `archive` allowed with no `--user-confirmed`. Consent was
  hardcoded in 4 of 13 gates and shouted in `nicki.md` prose for steps the script
  did not check.
- **Now:** `user_confirm_required` per step in `routing.json`, enforced once in
  `check-gate.py` before any gate runs, with that step's `user_confirm` sentence
  as the deny reason. `gate_start` is gone entirely (consent was its only check);
  `gate_integrate` and `gate_close` lost theirs. (`start` briefly gained a
  `user_confirm` sentence; dropped 2026-07-30 — see amendment below.)
- **Kept in code, deliberately:** `gate_review`'s confirm depends on the
  execution artifact's `review_scope`, not on the step, so it cannot be declared
  per step without inventing a condition language in JSON.
  **Amended 2026-07-30:** execution artifact dropped; partial scope (when any)
  comes from Nicki prompt / review-input only — see
  [`2026-07-30-informal-jump-and-drop-execution-design.md`](superpowers/specs/2026-07-30-informal-jump-and-drop-execution-design.md).
- **Behavior change, as warned:** `sync` and `archive` now deny without
  the flag. `nicki.md` says to pass it after any confirm, and
  `permissions.json` lists it. (**Amended 2026-07-30:** `start` does *not*
  require `--user-confirmed` — the user's start request is the confirm;
  hard-gating it caused a double ask with the transition card.)
- **Proven:** `gates_matrix.POLICY_CASES` — four consent denials, two cases
  showing no flag buys consent, plus a declaration check asserting that every
  step with a `user_confirm` sentence requires it and vice versa.

### 7. Name safety and sequence gates — **done 2026-07-29**

Implements [`flexibility.md`](flexibility.md) A4 and Decision 2.

- **Was:** the split half-existed and was applied by accident. `gate_sync`
  waived acceptance on `--override` but not readiness, `gate_integrate` took an
  override argument and discarded it, and no output said whether a denial was
  waivable — so `--override` was tried on everything (see "Why these recur").
- **Now:** every denial is classed. `deny()` is `safety` and never waives;
  `deny_sequence()` is ordering only. `check-gate.py` applies the waiver
  centrally — a `sequence` denial waives on `--override` or on an ad-hoc run of a
  step routing marks `adhoc_allowed`, and the allow reason names what was waived.
  Exactly two sequence denials exist: `sync`'s missing acceptance and `done`'s
  missing close.
- **In the contract:** stdout gained `gate_class` (null on allow) and `mode`, so
  Nicki can tell "fix the cause" from "ask the user for a waiver" instead of
  guessing. `--mode normal|adhoc` is the third flag, per Decision 2.
- **New routing data, all read:** `user_confirm_required`, `adhoc_allowed`,
  `irreversible`, plus a `gate_policy` block naming the two classes and listing
  the sequence denials. `irreversible` and `adhoc_allowed` together are a routing
  error the gate reports rather than resolving.
- **Proven:** 15 policy cases, plus a drift check that fails if
  `gate_policy.sequence_denials` and the `deny_sequence` calls in `gates.py`
  disagree — the same class of drift as Finding 3, now caught by the suite.
