# claude-adapter

## Task

Slug `claude-adapter`. Claude Code host bootstrap. Branch `feature/claude-adapter`.

## Story

install-claude.py · agent/skill mapping · CLAUDE.md opt-in routing · README quick-start · idempotent install

## Outcome

Pending integrate. Feature branch pushed to origin; sync handoff at `current-task/syncs/claude-adapter.yaml`. Commit f365298 on feature/claude-adapter; pre_push_merge not_needed. Harness errors recorded in `docs/archive/claude-adapter/errors.yaml`.

## Process

Story defined Claude Code bootstrap via install-claude.py mapping .cursor/ into .claude/ with YAGNI exclusions for hooks and nicki-workflow. Spec captured install script, mappings, invocation rules, idempotency, README, and manual proof requirements. Twelve subtasks covered implementation and verification; subtask 12 deferred to acceptance. Execution completed subtasks 1–11; subtask 12 blocked for manual Claude Code nicki start; install-claude.py recreated after acceptance rejection. R2 re-review approved Python entrypoint; subtask 12 skipped per review scope. Sync committed and pushed feature/claude-adapter.

## Decisions

install-claude.py at repo root, stdlib only; generated .claude/ and CLAUDE.md gitignored. Agents copied; skills synced verbatim. CLAUDE.md generated from nicki-default.mdc. Independent of install.py bootstrap. No nicki-workflow, hooks parity, or settings.json unless proof requires.

## Suggestions

Run subtask 12 in Claude Code on fresh clone before integrate. Align worktree registry paths with bootstrap-context --worktree argument. Batch install-claude.py naming updates in fresh-install archive and superpowers spec when editing related bootstrap docs.
