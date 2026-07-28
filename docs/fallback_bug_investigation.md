# sheep-fallback investigation: expectation mismatch + malformed-YAML root cause

Date: 2026-07-26. Scope: this session's therapy-type-selection incident, plus a search for
recurrence across the repo and worktrees.

## Summary

Two distinct things happened this session, and they should not be merged into one bug:

1. **An expectation mismatch, not a bug in sheep-fallback.** The live Nicki orchestrator told
   sheep-fallback to "fix the malformed YAML ... and record the incident." sheep-fallback is
   documented, unambiguously, as record-only. It correctly refused to fix anything and returned
   `blocked`. Nicki then had to improvise a second, narrowly-scoped `sheep-execute` dispatch to
   fix the file. This cost one extra round trip, but nothing was corrupted and the pipeline
   self-corrected using an existing, in-scope sheep (`sheep-execute` owns
   `current-task/executions/<slug>.yaml`).
2. **A real, reproducible defect class**: sheep-authored YAML files containing hand-typed prose
   with an unquoted `Label: text` colon sequence, which `yaml.safe_load` misparses as a nested
   mapping key, and which `check-gate.py` has no exception handling around — so the gate script
   hard-crashes with a Python traceback instead of failing cleanly.

**Is it recurring?** Yes, for the YAML-quoting defect — I found a near-identical incident 8 days
earlier in a different worktree, different task, different sheep (spec vs. execute), same root
cause and same failure signature (`yaml.scanner.ScannerError`, gate script crash, `sheep-fallback`
dispatched to record it). See "Evidence of recurrence" below. **No**, for "sheep-fallback failing
to fix things" — I found no prior incident where anyone expected sheep-fallback to fix an artifact
and was surprised when it didn't. This session's "nicki said it would fix the YAML" is the first
documented instance of that specific expectation gap.

## What sheep-fallback is actually scoped to do

`.cursor/agents/sheep-fallback.md` (mirrored at `.claude/agents/sheep-fallback.md`):

> "Only job: follow path Nicki gave — load failed harness inputs from Nicki prompt, append one
> failure record, return YAML contract."
>
> Output: "**Write:** `current-task/specs/errors.yaml` only — append one `errors.v1` failure
> entry. **Never write:** `current-task/status.json`, harness script source, **or any other
> artifact**."

`.cursor/skills/errors-recording/SKILL.md` reinforces this at the skill layer:

> "Write only `current-task/specs/errors.yaml`. Never write `status.json` or modify harness
> script source."

There is no ambiguity in either document: sheep-fallback is a pure incident-logger. It has no
instruction, example, or fallback path that touches any file other than `errors.yaml`. This
session's sheep-fallback run behaved exactly per spec — it appended the failure entry and
returned `completed_status: blocked`, and explicitly said fixing the YAML was out of scope. That
is correct behavior, not a bug.

## Why it was invoked this session, and what went wrong with expectations

`.cursor/agents/nicki.md`, "Harness failure" section, is equally specific about what gets sent
*to* sheep-fallback (worktree path, failed script route, script input, expected output contract,
actual failure context, blocked pipeline step) and what happens on return ("Relay sheep-fallback
return YAML to `sheep-status` as usual"). **It never states or implies that sheep-fallback fixes
anything.** `routing.yaml`'s `harness_failure:` block is the same — it lists the prompt fields and
the three authoritative scripts' contracts, and nothing else.

So the "nicki will fix the YAML via sheep-fallback" framing that appeared in this session's live
transcript was not sourced from `nicki.md` or `routing.yaml` — it was the orchestrating agent's
own improvisation/misstatement in the moment, not a documented capability that got misread. That
said, there is a real **documentation gap** worth naming: neither `nicki.md` nor `routing.yaml`
describes what to do *after* sheep-fallback returns still-blocked. The Harness failure section
ends at "relay to sheep-status" — it doesn't say "then re-invoke the sheep that owns the broken
artifact to regenerate/fix it," even though that's the only sane recovery and is exactly what
happened here (a second `sheep-execute` dispatch, scoped to the artifact `sheep-execute` already
owns). Making that implicit recovery step explicit would prevent a future orchestrator instance
from either (a) assuming sheep-fallback will fix things, or (b) stalling because it doesn't know
what comes next after a `blocked`-with-errors-recorded return.

## Evidence of recurrence

I checked every `errors.yaml` and `next-steps/*.yaml` I could find under
`worktrees/*/current-task/` and `docs/archive/sheep-fallback/`.

**`docs/archive/sheep-fallback/errors.yaml`** — two entries, both from
`--smoke-contract-fail`, i.e. synthetic smoke-test invocations used while building the
sheep-fallback feature itself (commit `64792b4`, 2026-07-02). Not real production incidents —
this is the feature's own test fixture, not evidence of the bug recurring in live task work.

**`worktrees/project-jung-clinical-profile/current-task/specs/errors.yaml`** (2026-07-18,
8 days before this session) — a **real, independent occurrence of the same defect class**:

- Gate: `subtasks` (`gate_subtasks` reading `current-task/specs/clinical-profile.yaml` for
  `open_questions`).
- Cause: `spec-maker`-authored acceptance-criteria lines of the shape
  `"Patient with at least one completed session: pressing the control persists..."` — an
  unquoted `Label: sentence` colon, same trap as this session's, just in a spec file written by
  `sheep-spec` instead of an execution file written by `sheep-execute`. The recorded
  `validation_errors` even note the pattern repeats across five consecutive acceptance items
  (lines 100–113), i.e. it wasn't a one-off typo, it was the writer's habitual phrasing style
  colliding with YAML syntax five times in one file.
- Same failure signature: `yaml.scanner.ScannerError`, `check-gate.py` exits with a raw traceback
  and empty stdout, `sheep-fallback` dispatched to record it.
- Same resolution shape: the file was manually fixed (the on-disk `clinical-profile.yaml` today
  has the acceptance items correctly double-quoted) and the task proceeded to
  `current_step: review` per its `status.json` — i.e., someone/something had to hand-fix a
  YAML-quoting bug outside the normal pipeline steps, exactly like this session's therapy-type-
  selection incident.

**Therapy-type-selection** (this session, 2026-07-26): same signature again, third time
counting the pattern, second time as a real (non-smoke) incident — `gate_review` reading
`review_scope` from `current-task/executions/therapy-type-selection.yaml`, an unquoted
`"Therapy type: <value>"` phrase inside a `note:` field written by `sheep-execute` at line 83.

**Conclusion on recurrence:** the user's instinct is correct, but the recurring element is
specifically *"sheep-authored prose YAML with an unquoted colon crashes check-gate.py, and
sheep-fallback gets dispatched to record — not fix — it."* That pattern has now hit two different
sheep (spec-maker and execute-plan), two different gates (subtasks and review), and two different
tasks, 8 days apart. It is a systemic gap in how these skills produce YAML, not a one-off typo.
By contrast, the *"nicki expected sheep-fallback to fix things"* expectation mismatch has no
prior instance in the artifacts I could find — this session appears to be its first occurrence.

## Bottom line

sheep-fallback isn't broken — it's a record-only logger, and it did exactly that. The real bug
lives upstream: sheep like sheep-execute and sheep-spec hand-author YAML with no quoting
discipline, so ordinary prose containing a colon trips the parser, and `check-gate.py` has no
exception handling around that parse, so a malformed artifact crashes the gate outright instead of
failing cleanly. This has now happened twice — this session's therapy-type-selection task and, 8
days earlier, project-jung-clinical-profile — at two different gates, written by two different
sheep, which rules out a one-off typo and confirms a systemic gap. The highest-leverage fix is
wrapping the YAML load in `check-gate.py`/`gate_utils.py` in a try/except so a bad artifact
produces a clean deny instead of a crash; adding quoting discipline to the format docs is the
second most important fix, since it addresses the root cause of the malformed YAML itself.

## Root cause of the malformed YAML

Both `execute-plan/execution-format.md` and `spec-maker/spec-format.md` instruct the sheep to
hand-author YAML directly (via the Write tool) against a documented schema — there is no library
call, no `yaml.dump`, no serialization script in the loop. Both format docs give a YAML example
and prose writing guidance ("Keep notes short," "Make every requirement testable"), but **neither
document mentions quoting, escaping, or the fact that a colon-space in a plain scalar is
YAML-significant**. The example blocks happen to avoid colons in scalar values, so nothing in the
skill's own reference material would tip off the writer that `note: ...subheader reading
"Therapy type: <value>".` or `- "Patient with...: pressing the control..."` needs explicit
quoting.

This is exactly the shape of both real incidents:
- `sheep-spec` writing an `acceptance` item as `Label: sentence.` (clinical-profile, 07-18).
- `sheep-execute` writing a `note` field as `...subheader reading "Therapy type: <value>".`
  (therapy-type-selection, 07-26) — note this one is *also* nested inside an already-hazardous
  construct (embedded literal quotes plus a colon), which is why the fixed version had to become
  a fully single-quoted scalar.

Because both skills route arbitrary prose (acceptance criteria, execution notes) into YAML
scalars with no quoting rule and no safe-serialization tooling, **any future prose sentence with a
colon in it will trip the same failure**, regardless of which sheep writes it, until either the
writing convention or the writing mechanism changes.

Separately, `check-gate.py` / `gate_utils.py` compounds the impact: `load_yaml()` calls
`yaml.safe_load()` with no `try/except`, and `check-gate.py`'s `main()` has no top-level exception
handling either. This has been true since the gate script's introduction (`3a1709d`, `check-gate.py`
routing gate) — it is not a regression, it's a gap baked in from the start. The practical effect:
a content bug in a sheep-authored artifact (attacker-free, purely internal) turns into a hard
Python crash with a raw traceback on stdout/stderr instead of a clean, contract-compliant `deny`.
That's *why* this surfaces as a "harness failure" requiring `sheep-fallback` at all, rather than a
normal gate deny that Nicki could show the user and route around without an extra sheep dispatch.

## Recommended fixes, ranked by durability

1. **Make `check-gate.py` defensive around YAML parsing (most structural, fixes both incidents'
   symptom in one place).** Wrap `load_yaml()` — or at minimum the call sites in `gates.py` that
   read sheep-authored artifacts (`gate_review`, `gate_subtasks`, etc.) — in a `try/except
   yaml.YAMLError`, and return a clean `deny(...)` with the parse error in `reason` instead of
   letting the exception propagate. This doesn't fix the underlying malformed YAML, but it turns
   every future instance of this defect class from a "harness failure requiring sheep-fallback +
   manual fix + extra round trip" into a normal, single-step gate deny that Nicki can show the
   user directly (per `nicki.md`'s existing "not harness failure: gate returning valid contract
   JSON with `allowed: false`" carve-out). This is the single highest-leverage change: it doesn't
   require touching every YAML-writing skill, and it directly shortens the recovery path that cost
   the extra round trip this session.

2. **Add an explicit quoting rule to `execution-format.md` and `spec-format.md`.** One line in
   each: "Quote any scalar value that contains a colon followed by a space (`: `) — wrap it in
   double quotes." This directly targets the observed pattern (`Label: sentence` acceptance items,
   `"...reading "X: <value>"."` notes) and costs nothing structurally, but relies on the writing
   agent remembering and applying it correctly every time — the same class of gap that caused the
   bug, just pushed one layer up. Should be paired with fix 1, not relied on alone.

3. **Document the post-sheep-fallback recovery step in `nicki.md`.** Add one line to "Harness
   failure": after relaying sheep-fallback's `blocked` return to `sheep-status`, if the failure
   was a parse/content error in an artifact owned by a specific sheep, re-invoke that sheep
   (scoped to the fix) rather than assuming sheep-fallback resolves it. This directly targets the
   expectation-mismatch half of this session's incident and prevents a future orchestrator
   instance from stalling or re-asserting the wrong capability for sheep-fallback.

4. **(Not recommended) Expand sheep-fallback's scope to fix trivial syntax errors.** Considered
   and rejected: sheep-fallback's value is being a minimal, single-purpose logger that Nicki can
   trust never to touch task artifacts — widening its write boundary "just for trivial fixes"
   reintroduces exactly the judgment-call surface (what counts as trivial?) that the current design
   deliberately avoids, and duplicates functionality that `sheep-execute`/`sheep-spec` already own
   for their respective artifacts. Fix 1 (defensive gate) and fix 3 (documented recovery path)
   achieve the same outcome — less pipeline friction — without blurring sheep-fallback's contract.

**Priority order for implementation:** 1 (defensive gate parsing) first — it's the one change that
caps the blast radius of *any* future YAML-authoring slip, not just this specific colon pattern.
Then 3 (recovery-path documentation), since it's a small, low-risk doc addition that resolves the
actual expectation-mismatch complaint. Fix 2 (quoting rule in the format docs) is worth adding
alongside but should not be treated as sufficient on its own, since it depends on an LLM writer
consistently remembering a syntax rule rather than removing the hazard structurally.
