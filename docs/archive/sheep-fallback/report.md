# sheep-fallback

## Task

Slug `sheep-fallback`. Title sheep-fallback failure recording. Branch `chore/sheep-fallback`.

## Story

sheep-fallback agent · errors.v1 append · harness routing · archive errors copy · Nicki-only spawn

## Outcome

Pending integrate. Feature branch `chore/sheep-fallback` synced and pushed. Sync handoff at `current-task/syncs/sheep-fallback.yaml`. Harness errors recorded — see `docs/archive/sheep-fallback/errors.yaml` (two smoke-test entries; bodies not pasted here).

## Process

Gherkin story defined a thin sheep-fallback agent that appends harness script failures to errors.yaml, Nicki-only spawn, and archive conservation of the errors artifact. Spec locked four authoritative harness triggers, errors.v1 schema, append semantics, and task-archive copy rules. Fourteen subtasks covered agent definition, errors-recording skill, routing registration, nicki.md harness failure wiring, archive extension, and verification. Execute completed all deliverables; smoke-harness-failure.sh passed E2E contract-mismatch recording. Review approved at ready_for_acceptance with gate-deny vs harness-failure distinction verified. First sync committed 64792b4, merged main, pushed feature branch.

## Suggestions

Land bootstrap-context.py, validate-sheep-return.py, and update-status.py before claiming full four-script fallback E2E coverage — three are routing-only today. Keep smoke-harness-failure.sh as regression guard when changing check-gate stdout or harness-failure routing.
