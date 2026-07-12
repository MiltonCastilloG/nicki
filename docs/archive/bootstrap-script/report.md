# Bootstrap script investigation

## Task

Slug `bootstrap-script`. Chore on branch `chore/bootstrap-script`. Original ask: bootstrap-context.py sibling to check-gate.py for Nicki disk routing.

## Story

bootstrap-context.py · disk read map · stdout JSON contract · Nicki wiring · fixture smoke · trimmed read companions

## Outcome

Pending integrate. Branch `chore/bootstrap-script` committed and pushed (3543ded); pre-push merge with `origin/main` succeeded. Final handoff: `current-task/syncs/bootstrap-script.yaml`.

## Process

**Describe.** P1 investigation approved dedicated `bootstrap-context.py` beside `check-gate.py`, shared `gate_utils`, six-field stdout contract, fixture smoke, and deferred nicki.md trim until proven.

**Spec.** `bootstrap_disk_reads` maps global-status, status.json, routing, and conditional validation reads. Requirements cover script, Nicki wiring, permissions, and post-smoke trim of redundant read companions.

**Subtasks.** Nineteen items from investigation confirmation through script, fixtures, permissions, Nicki agent updates, and read-doc trim.

**Execute.** All subtasks done. Added `bootstrap-context.py`, happy-path and missing-status fixtures, `nicki.md` bootstrap wiring, permissions allowlist, trimmed `global-status-read.md` and `status-read.md`. Harness validators passed on fixtures and live worktree.

**Review.** Validation `ready_for_acceptance`; review approved with no blockers.

**Sync.** Committed implementation paths, excluded `current-task/`, merged `origin/main`, pushed `chore/bootstrap-script`.

## Decisions

- `bootstrap-context.py` assembles routing context; `check-gate.py` keeps spawn veto.
- Stdout contract: six fields only; no gate-only extras.
- `--worktree` required; no `--task-id` in P1.
- Bootstrap skips spec YAML; check-gate owns spec open_questions gate.

## Suggestions

- Document `NICKI_WORKSPACE_ROOT` in `gate_utils` when adding harness fixtures — unplanned hook surfaced during fixture work.
- Grep sheep agents for bootstrap read prose before scheduling trim subtasks — subtask 18 found no sheep edits needed.
