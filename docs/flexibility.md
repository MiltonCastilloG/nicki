# Nicki flexibility — spec

Date: 2026-07-28. Prerequisites and gate bugs: [`harness-gate-bugs.md`](harness-gate-bugs.md).

## Goal

Nicki stops being a strict linear march.

1. **Run a step out of band.** Sync mid-`execute`, without acceptance, without
   moving workflow state.
2. **Accept a source of truth from outside the workflow.** E.g. a spec produced
   by the `brainstorm` skill.

## Constraints

Standing. Do not trade these for convenience.

| Constraint | Means |
|---|---|
| Scripts stay authoritative | `check-gate.py`, `update-status.py`, `bootstrap-context.py` keep the veto. No decision moves back into prose. |
| `status.json` stays source of truth for pipeline state | External input supplies *content*, never position. |
| Safety gates never waive | Push to main, merge, worktree delete stay hard-confirmed. |
| Flexibility is not `--override` | New flag, new reason string. Reusing the blunt flag hides the next bug — see `harness-gate-bugs.md`, "Why these recur". |

## Capability A — out-of-band steps

### Current behavior

`--override` allows the sheep, then the write clobbers position.

| Layer | Behavior today | Evidence |
|---|---|---|
| Gate | `gate_sync` waives the acceptance check on `--override`, not the readiness block | `gates.py:94-101` |
| Sheep | `sheep-sync` blocks itself: "invoke only after user acceptance" | `sheep-sync.md:26-31` |
| Sheep | `sheep-sync` returns `next_step: archive` (or `integrate`) — the sheep decides position | `sheep-sync.md:40` |
| Write | `next_step` is the *only* required field; there is no way to say "do not move" | `update-status.py:31` |

Net: sync mid-`execute` leaves the task believing it is in the git tail with
implementation half done.

### Target behavior

An ad-hoc invocation that is gated for safety, runs the sheep, and leaves
`current_step`, `next_step`, and `completed_steps` untouched.

### Blockers

**A1 — no no-advance write mode.** `REQUIRED_SUMMARY_FIELDS = ("next_step",)`.
Ad-hoc is unexpressible in the write contract. Needs an explicit mode where
position is preserved and only the artifact pointer plus a side-effect record
are written.

**A2 — sheep hardcode position.** `sheep-sync` says `archive`/`integrate`,
`sheep-execute` says `review` (`sheep-execute.md:42`), `sheep-spec` says
`subtasks` (`sheep-spec.md:35`). **Decided (B):** sheep stop returning
`next_step`; routing supplies it on normal completion; ad-hoc skips applying it.
**Half built 2026-07-28:** `gate_utils.next_step_for()` now resolves position
from routing and `check-gate.py` echoes it. Remaining: the write path must call
it (step 7) and the sheep must stop sending it (step 6).

**A3 — gates live in three layers.** `check-gate.py`, prose `Gate:` lines in
every `sheep-*.md` (`sheep-sync`, `sheep-spec`, `sheep-subtask`,
`sheep-archive`, `sheep-integrate`, `sheep-close`), and hard-gates in
`nicki.md`. The script can allow ad-hoc and the sheep will still refuse — mid
`execute` there is no validation artifact for `sheep-sync` to satisfy its own
prose with. **Decided (4):** sequence gating leaves the sheep entirely; the
script is the only authority on whether a sheep runs.

**A4 — safety vs sequence is unnamed.** The split half-exists and is applied
inconsistently: `gate_sync` waives acceptance on override but not readiness,
`gate_integrate` discards its override argument entirely, `close`/`integrate`
use `--user-confirmed` for the same job. Name the two classes, mark each gate,
apply uniformly.

**A5 — no side-effect trail.** If state does not advance, ad-hoc git work leaves
no record. `archive-format.md` derives `process` from artifact handoffs, so the
archive report will silently omit it. Needs a log — e.g. `task.side_effects[]`
with step, timestamp, artifact.

**A6 — per-step metadata is unread.** Ad-hoc needs `irreversible`,
`sequence_gate`, `adhoc_allowed` per step. Adding fields to a `routing.json`
that no script reads makes the Finding 3 trap worse. Resolve read-or-move first.

### Acceptance checks

- Ad-hoc sync during `execute`: gate allows, sheep runs, `status.json`
  `current_step`/`next_step`/`completed_steps` byte-identical before and after.
- Artifact pointer for the ad-hoc sync is recorded; side effect appears in the
  log and in the archive report.
- Ad-hoc integrate: **denied** — safety gate, no waiver.
- Fixture per case, through `check-gate.py`, in `test.py`.

## Capability B — external source of truth

### Current behavior

`gate_subtasks` needs `artifacts.spec` under the worktree, parseable, with empty
`open_questions` (`gates.py:46-58`). `sheep-spec` refuses without
`artifacts.story` (`sheep-spec.md:27`). So an external spec means faking
`describe` and `spec`.

### Blockers

**B1 — path scope. Cleared 2026-07-28.** `artifact_path()` now resolves per-key
scope via `gate_utils.ROOT_SCOPED_ARTIFACTS`. Adding an external source of truth
means declaring its key's scope there (or extending the mechanism to absolute /
outside-workspace paths), not rewriting resolution.

**B2 — cannot register a pointer without claiming a step.**
`_set_artifact_pointer` is keyed by `completed_step`
(`update-status.py:110-119`). `current-task-update/SKILL.md:62` documents
optional `git` and `artifacts` summary fields; the script never reads them
(`task` is read only on fresh init). So adoption today requires
`completed_step: spec`, which lies about what happened.

**B3 — brainstorm output does not fit the spec slot.** `brainstorm` writes
`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` (`brainstorm/SKILL.md:106`)
— markdown, root-relative, no `open_questions` key. `load_artifact` rejects
`.md` outright: `unsupported artifact suffix` (`gate_utils.py:60-63`).

**B4 — provenance and staleness.** The external doc sits outside the task's git
scope and can change after adoption. Record path plus commit or hash, else the
spec drifts and nothing notices.

**B5 — status vocabulary.** Needs a way to say "satisfied by external artifact"
rather than "completed by a sheep". Same enum work as bug-doc follow-up 3.

### Two paths

**Cheap — design doc as sheep input.** The brainstorm doc becomes a disk input
to `sheep-spec`, like the story. Sheep still writes the schema-shaped spec, with
provenance in `meta`. Clears B3 without touching gates; needs B1 and B4 only.

**Full — artifact adoption.** Register the external path as `artifacts.spec`
directly. Gates validate **shape** — parses, root is an object,
`open_questions` empty — not provenance. Needs all of B1–B5 plus a shape adapter
or front matter for markdown.

**Recommendation: cheap first.** It gets external intent into the pipeline in
one change. Go full only if the sheep round trip proves to add nothing.

### Acceptance checks

- Spec step run with an external design doc as input: spec artifact written,
  `meta` records origin path and commit.
- `gate_subtasks` passes on the resulting spec without any override.
- Design doc at workspace root resolves correctly from inside a worktree.
- Doc changed after adoption: staleness is detectable.
- Fixture per case in `test.py`.

## Sequencing

Prerequisites are bug-doc follow-ups. They are not optional warm-up — both
capabilities multiply gate paths, and adding paths to an untested gate layer with
a blunt override reproduces the exact failure this project just documented.

| Order | Work | Source |
|---|---|---|
| ~~1~~ | ~~Scope model for artifact paths~~ — **done 2026-07-28** | bug doc follow-up 1 · cleared B1 |
| ~~2~~ | ~~Resolve `routing.json`: read `default_next_step`~~ — **done 2026-07-28**; `artifact_key`/`secondary_artifact_key` deferred to step 7 | bug doc follow-up 5 · unblocks A6 · implements Decision 1 |
| ~~3~~ | ~~Gate fixtures in `test.py`~~ — **done 2026-07-28**, 45 cases | bug doc follow-up 2 · guards everything after |
| 4 | Status vocabulary: enum, no-advance mode, side-effect log | bug doc follow-up 3 · A1, A5, B5 |
| 5 | Consent from routing + name safety vs sequence gates, enforced in `check-gate.py` only | A4 · Decisions 2, 3 · bug doc follow-up 6 |
| 6 | Strip workflow knowledge from every `sheep-*.md`; shrink the return contract | A3 · Decision 4 |
| 7 | Write path takes `--step`/`--mode`; calls `next_step_for()` on normal, leaves position on ad-hoc; wire `artifact_key` to replace `key_by_step` | A1, A2 · Decisions 1, 2, 4 |
| 8 | Ad-hoc sync end to end | Capability A complete |
| 9 | External spec as `sheep-spec` input, with provenance | B3 cheap path, B4 |

## Decisions

### 1. Who owns `next_step` — **routing** (option B)

Decided 2026-07-28.

- Sheep return handoff only: `completed_step`, artifact, `completed_status`,
  blockers — **not** `next_step`.
- On normal completion, `update-status.py` (or bootstrap/gate path that owns
  the write) sets `task.next_step` from `routing.json` `default_next_step` for
  the completed step.
- Git-tail nuance (first sync → `archive`, second sync → `integrate` when
  `artifacts.archive` is set) lives in the script/routing, not sheep prose.
- Ad-hoc: write mode does **not** apply `default_next_step`; position fields
  stay byte-identical.
- Bug-doc follow-up 5: **read** `default_next_step`; do not delete it. Other
  unread routing fields still read-or-move.

### 2. How ad-hoc is spelled — **`--mode` enum** (option C)

Decided 2026-07-28.

- `check-gate.py` takes `--mode normal|adhoc` (default `normal`) and **echoes
  the resolved mode in stdout**, so the mode travels in the gate contract rather
  than in Nicki's memory.
- Nicki forwards the mode to `sheep-status`; `update-status.py` accepts it and
  applies routing's `default_next_step` only when mode is `normal`.
- One axis, extensible: capability B adds `adopt` on the same flag instead of a
  third boolean. Do not add `--adhoc`/`--adopt` booleans alongside `--override`.
- Step names stay as they are; no `adhoc-sync` duplicates in `routing.json`.
- Gate contract gains a field, so bug-doc follow-up 2 fixtures must assert the
  echoed mode.

### 3. Consent lives in routing, required every time (option D + strict)

Decided 2026-07-28.

- Add a per-step property next to the existing `user_confirm` string —
  `user_confirm_required: true|false` — and have `check-gate.py` enforce it
  generically: required and `--user-confirmed` absent → deny, with routing's own
  sentence as the reason.
- Remove the hardcoded `user_confirmed` checks from `gate_start`, `gate_review`,
  `gate_integrate`, `gate_close`. One check, one place.
- **Strict:** every step that has a `user_confirm` string declares
  `user_confirm_required: true`. Ad-hoc included — no session grants, no
  exemptions. "Sync now" from the user is itself the confirm, so the cost is one
  keystroke.
- Ad-hoc consent is therefore data, not Python: tuning it later means editing a
  routing field.
- Side effect: fixes bug-doc Finding 6 (sync and archive currently allow with no
  consent at all). Behavior change — both steps begin denying without the flag,
  so fixtures are required and Nicki must pass it after every confirm.

### 4. Sheep hold no workflow knowledge (option B, strict)

Decided 2026-07-28. Only Nicki and the scripts know the pipeline.

A sheep does one job inside a scope root. It does not know what came before, what
comes after, or where it sits in the map.

**Strip from every `sheep-*.md`:**

- Sequence gate prose — `sheep-sync`'s "invoke only after user acceptance",
  `sheep-spec`'s story gate, `sheep-subtask`'s spec gate, `sheep-archive`'s
  "after first sync", `sheep-integrate`'s artifact preconditions,
  `sheep-close`'s integrate precondition. `check-gate.py` already decided.
- `next_step` from the return contract (Decision 1).
- `completed_step` from the return contract — the sheep should not name its own
  pipeline step. Nicki dispatched it; Nicki and routing know which step it was.
- Cross-step narration: "Nicki sends `sheep-status` after this step", "next_step
  is `archive` after first sync", "tell Nicki the spec step is needed first",
  `Gate` labels in disk-input tables.

**Keep:** which skill to read, scope root, what it may write, safety rules (never
push main, never force push, never write `status.json`, no secrets), and the
handoff shape.

**Resulting sheep return:** `artifact`, `completed_status`, `open_questions`,
`summary`. Position-free.

**Implication for the write path.** Someone must still supply position.
`update-status.py` takes `--step <dispatched step>` and `--mode normal|adhoc`
from Nicki, then derives `completed_step` from `--step` and `next_step` from
routing's `default_next_step` — or leaves position untouched when mode is
`adhoc`. So `REQUIRED_SUMMARY_FIELDS = ("next_step",)` and
`routing.json` `sheep_return_contract.required_fields` both change in this pass.
`nicki.md`'s "forward sheep return JSON verbatim" becomes "forward the return
plus the step and mode you dispatched".

**Cost accepted:** sheep lose their independent veto, so a `check-gate.py` bug
reaches further. That is why gate fixtures (bug-doc follow-up 2) come first.
Benefit beyond flexibility: every sheep file gets shorter, which serves the
trimming goal in `docs/tasks.md`.

## Open decisions

None. All four decided 2026-07-28.
4. Do sheep learn the ad-hoc concept, or does Nicki pass it as a prompt flag and
   the prose gates get rewritten to defer to the script?
