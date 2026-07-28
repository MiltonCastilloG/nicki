# clinical-profile

## Task

- **slug:** clinical-profile
- **title:** Clinical profile per patient
- **branch:** feature/clinical-profile
- **type:** feature

## Story

PatientDetail Generate control · completed-session-only synthesis · persisted profile + timestamp · full regeneration · no-completed-sessions error · dedicated profile page

## Outcome

`pending_integrate` — feature branch `feature/clinical-profile` synced and pushed (`0301b91`). Sync handoff: `current-task/syncs/clinical-profile.yaml`. Harness errors recorded during the run — see `docs/archive/clinical-profile/errors.yaml`. Integrate not run yet.

## Process

**describe** — Gherkin story for generating/updating a per-patient clinical profile from completed sessions' stored analysis only.

**spec** — Captured the profile control, completed-session-only synthesis scope, full-replace persistence, immediate display, and fetch/generate endpoints with not-found and no-completed-sessions handling.

**subtasks** — Fourteen checklist items for schema, data access, synthesis, endpoints, and frontend control/display/tests, plus a review-driven Fix item for the profile title/page.

**execute** — Complete (14/14 plus the Fix item). Changed `backend/src/db.ts`, `backend/src/agent.ts`, `backend/src/agent-prompts.ts`, `backend/src/patients-route.ts`, `ui/src/PatientDetail.tsx`, `ui/src/ClinicalProfile.tsx` (new), `ui/src/App.tsx`. Lint, typecheck, backend tests (16/16), and ui tests (16/16) all clean.

**review** — `ready_for_acceptance`. r3's focused re-review confirmed the r2 blocker resolved (profile title styling and the new dedicated `ClinicalProfile` page). One deferred, non-blocking scope note: the worktree was mid-merge with unrelated changes staged.

**sync** — Committed and pushed `feature/clinical-profile` (`0301b91`); `pre_push_merge` concluded an already-in-progress merge (`635b43f`) rather than starting a new one.

## Decisions

- Profile entry point: patient name + "Profile" title is red/non-clickable text with no profile yet, an underlined clickable link to a new minimal profile page once one exists; Generate button always visible, only disables/relabels while pending.
- Synthesis scope: only stored per-session analysis JSON from completed sessions, no session-count cap, never raw transcripts.
- Regeneration fully replaces the prior profile text and timestamp — no incremental merge.
- A synthesis failure shows a generic inline error and leaves any prior profile unchanged; a distinct inline error covers zero completed sessions.

## Suggestions

- Quote/rephrase spec acceptance bullets with a "Label: sentence" shape so a bare colon isn't parsed as an implicit YAML mapping key (see `errors.yaml`).
- Finish and commit any in-progress git merge before invoking sync, rather than letting sync conclude an unrelated pending merge as part of its own commit.
- When relaying user UI feedback into a fix subtask, capture the concrete design (element/styling/navigation) up front instead of a paraphrase, to avoid an extra fix-then-clarify review round trip.
