# check-gate.py bug: archive expected_artifact extension mismatch

Date: 2026-07-28. Task: `project-jung/clinical-profile`
(`worktrees/project-jung-clinical-profile`).

## Summary

After `sheep-archive` ran, `status.json` correctly recorded
`artifacts.archive: "docs/archive/clinical-profile/report.yaml"`, and that
file genuinely exists on disk at
`docs/archive/clinical-profile/report.yaml`. However, `routing.json`'s
`archive` step declares `expected_artifact:
"docs/archive/<slug>/report.json"` — a `.json` extension, not `.yaml`.
`check-gate.py --step integrate` denied the transition with reason
`"integrate gate: archive artifact missing"`, even though the artifact is
present under its actual (recorded) name. A false negative, not a real
missing artifact.

## Reproduction

1. Run the pipeline through `sheep-archive` for `project-jung/clinical-profile`.
2. Observe `status.json`: `artifacts.archive:
   "docs/archive/clinical-profile/report.yaml"`. Confirm the file exists —
   `ls docs/archive/clinical-profile/` shows `report.yaml` on disk (plus
   `report.md`, `story.md`, `errors.yaml` from earlier steps).
3. Run `check-gate.py --step integrate`. Result: `"allowed": false`, reason
   `"integrate gate: archive artifact missing"` — despite the file
   genuinely existing at the path `status.json` itself recorded.

## Root cause

Hypothesis: `routing.json`'s `expected_artifact` for the `archive` step is
stale/wrong — it declares `report.json`, but the actual `sheep-archive`
implementation (skill `task-archive`) writes `report.yaml`, matching this
task's established convention of `.yaml` for every other generated artifact
(spec, execution, sync all end in `.yaml`). `check-gate.py`'s integrate gate
(`"gate": "sync artifact exists; archive artifact exists; ..."` in
`routing.json`) checks a literal path built from `expected_artifact` against
the filesystem, rather than trusting `status.json`'s own
`artifacts.archive` value — so a correct write plus a stale routing string
produces a hard deny.

## Impact

The `integrate` gate always denies immediately after a normal `archive` step
unless overridden. Likely systemic, not specific to this one task:
`sheep-archive` appears to consistently write `.yaml`, so every task that
reaches `integrate` via a normal archive step should hit the same false
deny.

## Workaround

Re-ran `check-gate.py --step integrate` with `--override`.

## Suggested fix

Either:
- Update `routing.json`'s `expected_artifact` for `archive` to
  `docs/archive/<slug>/report.yaml`, matching actual `sheep-archive` output, or
- Make `check-gate.py`'s artifact-existence check extension-agnostic, or
  have it read the actual recorded `artifacts.archive` path from
  `status.json` instead of reconstructing a path from a hardcoded
  `expected_artifact` string.

Add a regression fixture for this exact case — "archive artifact written as
`.yaml`, `expected_artifact` says `.json`, integrate gate should still
allow" — to the smoke-fixture matrix tracked in `docs/tasks.md` item #10
(fixtures exercised through `check-gate.py`).
