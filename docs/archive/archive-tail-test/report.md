# archive-tail-test

E2E test of sync → archive → sync → integrate → close. Archive written after first sync merge; pending integrate.

## Task

- **slug:** `archive-tail-test`
- **title:** Archive tail workflow review test
- **branch:** `chore/archive-tail-test`
- **type:** chore

## Story

gitignore current-task · sheep-archive · sync→archive→sync→integrate→close

## Outcome

`pending_integrate`. Target `main`. Feature branch `chore/archive-tail-test`. Sync handoff was `current-task/syncs/archive-tail-test.yaml`.

## Process

- **spec** — Six requirements for archive tail workflow.
- **review** — ready_for_acceptance — static review approved.
- **sync** — First sync committed workflow changes; merged main; current-task excluded.
- **archive** — Joined leftover source `docs/e2e-archive-tail-marker.md` into this archive as `e2e-archive-tail-marker.md`.
