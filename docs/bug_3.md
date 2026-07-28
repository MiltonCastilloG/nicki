# check-gate.py bug: integrate gate joins workspace-root-relative archive path against worktree

Date: 2026-07-28. Task: `project-jung/clinical-profile`
(`worktrees/project-jung-clinical-profile`).

## Summary

The `integrate` gate denies with `"integrate gate: archive artifact missing"`
even though the archived report genuinely exists. `gate_integrate` never
reads `routing.json`; it resolves `status.json`'s `artifacts.archive`
(`"docs/archive/clinical-profile/report.yaml"`) via `artifact_path()`, which
joins that value against the **worktree** root. The archive path is
deliberately workspace-root-relative (the file must survive worktree
deletion at close), so the join always misses. `--override` cannot help:
`gate_integrate`'s trailing parameter is unused.

## Reproduction

1. Run the pipeline through `sync` and `archive` for `project-jung/clinical-profile`.
2. `status.json` records `artifacts.archive:
   "docs/archive/clinical-profile/report.yaml"`. Confirmed on disk at the
   workspace root: `docs/archive/clinical-profile/report.yaml`, 4738 bytes.
3. `check-gate.py --step integrate` → `"allowed": false`, reason
   `"integrate gate: archive artifact missing"`.
4. `worktrees/project-jung-clinical-profile/docs/archive/clinical-profile/report.yaml`
   does not exist and cannot — nothing ever writes archive output under the
   worktree.
5. Re-running with `--override` produces the identical deny.

## Root cause

`gates.py:120` — `gate_integrate(status, worktree, user_confirmed, _)` — the
fourth parameter (override) is named `_` and never referenced in the
function body. Line 123 calls `artifact_path(worktree, status, "archive")`.
`gate_utils.py:86-88` — `artifact_path()` is `worktree / rel` for any `rel`
found at `status["artifacts"][key]`. It has no awareness that `archive`'s
value is workspace-root-relative by design, so it builds
`worktrees/project-jung-clinical-profile/docs/archive/clinical-profile/report.yaml`,
a path that structurally can never exist. `gates.py` does not import or call
`load_routing()` anywhere — `routing.json`'s `expected_artifact` field is
never consulted by any gate.

## Impact

Systemic, not task-specific: every task's `integrate` gate will deny after a
normal `archive` step, because `artifacts.archive` is root-relative for all
tasks by convention (the report must outlive the worktree). Worse than the
`sync`/`archive` gates' override paths — this deny cannot be bypassed via
CLI at all, since `gate_integrate` silently discards its override argument.

## Correction of bug_2.md

`docs/bug_2.md` attributed this same symptom (integrate gate denying after
archive) to a `routing.json` `expected_artifact` extension mismatch
(`report.json` vs actual `report.yaml`). Direct inspection shows `gates.py`
never reads `expected_artifact` or `routing.json` at all — the extension
field is unused dead data as far as gating is concerned. The extension
mismatch may still be worth fixing for documentation accuracy, but it is not
the cause of any gate deny. The actual cause is the worktree-vs-workspace-root
path join described above.

## Workaround

None via CLI flags — `--override` has no effect on `gate_integrate` since
the parameter is unused. Required manually confirming the file's existence
at the workspace-root path and proceeding directly, bypassing the gate
script's check entirely.

## Suggested fix

Fix `artifact_path()` (or add a dedicated path for `gate_integrate`'s
archive lookup) to resolve workspace-root-relative artifact paths against
the workspace root, not the worktree — e.g. detect that `archive` values
live outside the worktree's own tree, or adopt an explicit convention
(root-relative prefix, or a second `artifacts.archive_root` field) so
resolution doesn't have to guess. Separately, either wire up
`gate_integrate`'s override parameter so `--override` is honored like other
gates, or drop it from the signature if override is intentionally
unsupported here — a silently-ignored CLI flag is its own bug. Add a
regression fixture — "archive artifact recorded as workspace-root-relative,
integrate gate should resolve and allow" — to the smoke-fixture matrix
tracked in `docs/tasks.md` item #10 (fixtures exercised through
`check-gate.py`).
