# sheep-fallback — bare notes

> **Historical.** Spawn gate retired 2026-08-05; Finding 5 impact on check-gate no longer applies. See [`harness-gate-bugs.md`](harness-gate-bugs.md).

Date: 2026-07-26. Detail folded into [`harness-gate-bugs.md`](harness-gate-bugs.md)
Finding 5. Kept for recurrence evidence only.

## Not a bug

`sheep-fallback` is record-only. Writes `errors.json` (was `.yaml`), never fixes
artifacts. Nicki once asked it to fix malformed YAML; it correctly returned
`blocked`. That was an expectation mismatch, not a sheep defect.

After fallback returns blocked: re-invoke the sheep that owns the broken
artifact. Do not expand fallback scope.

## Real defect

Sheep hand-author YAML against a schema with no quoting rule. Unquoted
`Label: sentence` parses as a nested mapping. Gate then crashed (pre-fix) or
denies cleanly (post-fix on `check-gate.py`).

## Recurrence

| Date | Task | Sheep | Gate | Signature |
|------|------|-------|------|-----------|
| 2026-07-18 | `project-jung/clinical-profile` | `sheep-spec` | `subtasks` | `yaml.scanner.ScannerError`, empty gate stdout |
| 2026-07-26 | therapy-type-selection | `sheep-execute` | `review` | same |

Two sheep, two gates, eight days apart. Systemic, not a typo.

Archive trail: `docs/archive/clinical-profile/errors.yaml` (live incident).
`docs/archive/sheep-fallback/errors.yaml` is smoke-only — ignore.

## Fix status

| Item | Status |
|------|--------|
| Defensive parse in `check-gate.py` | Done |
| Same for `bootstrap-context.py` | Open — see harness-gate-bugs Finding 4 |
| Quoting rule in format docs | Open |
| Post-fallback recovery line in `nicki.md` | Open |
