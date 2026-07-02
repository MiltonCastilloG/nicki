# fresh-install

## Task

Slug `fresh-install`. Post-clone bootstrap for the Nicki repository. Branch `chore/fresh-install`.

## Story

install.py · nicki-workspace stub · worktrees/ · README quick-start · git prerequisite

## Outcome

Pending integrate. Feature branch pushed to origin; sync handoff at `current-task/syncs/fresh-install.yaml`. Commit c3a3006 merged with origin/main; push at 5a00d96.

## Process

Story captured first-install, idempotent re-run, missing-git failure, README flow, and post-install Nicki readiness. Spec defined stdlib-only install.py with nicki-only registry stub and worktrees directory. Thirteen subtasks covered install.py, README quick-start, and verification runs. Execution completed all subtasks in install.py and README.md. Review found no blockers; ready for acceptance. Sync committed, merged main, and pushed chore/fresh-install.

## Decisions

install.py at repo root, stdlib only. nicki-workspace.yaml written once then skipped. Git checked before any writes. global-status.json not created at install. Committed .cursor runtime untouched (deferred #20).
