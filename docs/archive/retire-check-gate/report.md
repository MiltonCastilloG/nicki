# retire-check-gate

## Task

Slug `retire-check-gate`. Title retire spawn-time check-gate; chat consent only. Branch `main` (direct).

## Story

Delete check-gate · consent SoT Nicki chat · execute + sync only · bootstrap_utils · routing_write · archive report

## Outcome

Landed on `main` at `30c16b8`. Design: `docs/superpowers/specs/2026-08-05-retire-check-gate-design.md`. Full Nicki pipeline (worktree / sync / integrate / close) was not run for this task — archive report written manually after the removal commit.

## Process

Analysis showed gate no longer enforced progress: only thin document/consent bookends remaining, while hard stops the user cared about were user confirmation before execute and before sync. Chose hard delete of the spawn veto (not soft retire). Implement removed `check-gate.py` / `gates.py` / gate smokes, stripped routing gate/consent/adhoc flags, renamed thinned helpers to `bootstrap_utils.py` (bootstrap-only) and `routing_write.py` (writer `next_step_for` / `MODES`), updated Nicki prose and live docs. `python3 test.py` passed. Commit `30c16b8` records the removal.

## Decisions

- Consent source of truth: Nicki chat only; explicit yes for **execute** and **sync** only.
- No gate invocation on normal, adhoc, or jump.
- Jump bookends (`start` / `close` / `done`) stay in `update-status.py`.
- Open questions: sheep + status; no script spawn re-check.

## Suggestions

- Optional follow-up: trim leftover historical gate mentions in investigation/flexibility backlog docs.
- Consider renaming sheep prose that still says “enforce gates” if that language confuses operators.
