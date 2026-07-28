# Harness gate bugs — combined report

Date: 2026-07-28. Replaces the deleted per-bug notes (`bug_1`–`bug_3`).
Recurrence evidence for Finding 5: [`fallback_bug_investigation.md`](fallback_bug_investigation.md).
Target these fixes serve: [`flexibility.md`](flexibility.md).

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
| 1 | `gate_integrate` resolves the archive path against the worktree; archive is workspace-root-relative | **Fixed 2026-07-28** (follow-up 1) | Foundation. External sources of truth need the same scope model. |
| 2 | `completed_status` must be the literal `"complete"` or `completed_steps` silently skips the append | Real, reproduced; reported mechanism was wrong | Vocabulary grows: needs "ran, did not advance" and "satisfied by external". |
| 3 | `routing.json` per-step fields are unread by any script | Real; caused a wrong root cause and a wasted investigation cycle | Direct block. Ad-hoc needs per-step metadata; adding unread fields deepens the trap. |
| 4 | `bootstrap-context.py` still crashes on a malformed artifact | Real, reproduced; the 07-26 fix landed on one of two entry points | Worse. External input is less controlled, and bootstrap runs every response. |
| 5 | Sheep hand-author prose YAML with no quoting rule | Real, recurring; impact now capped at `check-gate.py` only | Sideways. New surface: user-authored markdown instead of sheep YAML. |
| 6 | `sync` and `archive` gates allow with no user consent; the rule is prose-only | Real, reproduced | Fixed by flexibility Decision 3 — consent becomes a routing property the script enforces. |
| 7 | `rerun_review` readiness is documented but absent from `routing.json`; the gate crashed on it and it never blocked sync | **Fixed 2026-07-28** (follow-up 2) | Found by writing the gate matrix — the coverage gap was hiding it. |

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
  a correct root cause is the one whose override is broken.
- **Path scope is unwritten.** `archive` is workspace-root-relative; every other
  artifact is worktree-relative. `artifact_path()` knows one rule. No format doc
  states the difference.
- **Migrations go big-bang mid-flight.** `8fa5569` flipped every artifact and
  return contract from YAML to JSON across 39 files on the same day as these
  reports, with a task in flight holding `.yaml` artifacts.

## Follow-ups

Ordered. Each is a prerequisite for [`flexibility.md`](flexibility.md), and
names the blocker there it clears. Each states current behavior, target, and a
done-when check so a future session can pick one up cold.

### 1. Scope-aware artifact resolution — **done 2026-07-28**

Unblocked flexibility B1.

- **Was:** `artifact_path()` was `worktree / rel` for every key.
  `gate_integrate` discarded its override argument.
- **Now:** `gate_utils.ROOT_SCOPED_ARTIFACTS` declares which pointers are
  workspace-root-relative (`archive`); everything else resolves against the
  worktree. `readiness()` goes through `artifact_path()` instead of its own join.
  `gate_integrate`'s consent deny states that `--override` does not apply, since
  integrate is a safety gate — full safety/sequence classing is follow-up 6 and
  flexibility step 5.
- **Documented:** path-scope rule in `status-format.md` `artifacts`.
- **Proven:** `tests/smoke/gate_paths.py`, wired into `test.py`. Six cases:
  archive at root resolves; archive genuinely absent still denies; archive under
  the worktree is *not* accepted; worktree-scoped `sync` is *not* read from the
  root; integrate without consent denies; `--override` cannot buy consent.
  Reverting the resolution change turns the suite red.

### 2. Real gate fixtures in `test.py` — **done 2026-07-28**

Closes `docs/tasks.md` #10. Guards every later step.

- **Was:** 12 of 13 gates untested; the one gate test
  (`scripts/smoke-archive-gate.py`) was not imported by `test.py`, so it ran only
  by hand.
- **Now:** `tests/smoke/gates_matrix.py` drives 45 cases through
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

### 3. Status vocabulary

Unblocks flexibility A1, A5, B5.

- **Now:** `completed_status` is an open string; anything but `"complete"`
  silently skips the `completed_steps` append and still reports
  `written: true` (`update-status.py:212`).
- **Target:** closed set, validated. Unknown value returns `written: false` with
  an error naming the field. Document the set in `status-format.md` and
  `routing.json`.
- **Design with flexibility in mind:** the same enum needs members for "ran, did
  not advance" and "satisfied by external artifact". Add them in this pass rather
  than reopening the contract twice.
- **Done when:** a bad `completed_status` fails loudly, and a fixture covers it.

### 4. Contract-safe bootstrap failure

- **Now:** `bootstrap-context.py` returns exit 1 with stderr and empty stdout on
  a malformed artifact, which `nicki.md` classifies as a harness failure — on a
  script that runs every response.
- **Target:** always print contract JSON, carry the parse error in a field, same
  as `check-gate.py` already does.
- **Done when:** a truncated validation artifact yields contract stdout, not a
  `sheep-fallback` dispatch.

### 5. Resolve the `routing.json` fiction — **mostly done 2026-07-28**

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
- **Remainder:** `artifact_key` and `secondary_artifact_key` are still unread.
  They are the intended source for `update-status.py`'s hardcoded `key_by_step`
  map (`update-status.py:110-119`) — duplication today. Wire them in flexibility
  step 7, when the write path gains `--step`/`--mode`; that pass must also settle
  how a script outside `.cursor/skills/nicki/scripts/` reads routing.
- **Not done here, deliberately:** `nicki.md` still documents the old four-field
  gate contract and does not mention the echoed `next_step`/`artifact`. Agent
  prose changes land together in flexibility step 6.

### 6. Enforce consent from routing

Implements [`flexibility.md`](flexibility.md) Decision 3.

- **Now:** `sync` and `archive` allow with no `--user-confirmed`. Consent is
  hardcoded in 4 of 13 gates and shouted in `nicki.md` prose for a step the
  script does not check.
- **Target:** per-step `user_confirm_required` in `routing.json`, enforced once
  in `check-gate.py` using routing's own `user_confirm` sentence as the deny
  reason. Drop the hardcoded checks from `gate_start`, `gate_review`,
  `gate_integrate`, `gate_close`.
- **Watch:** this is a behavior change — `sync` and `archive` start denying
  without the flag. Nicki must pass it after every confirm.
- **Done when:** every step with a `user_confirm` string denies without the flag,
  proven by a fixture per step.
