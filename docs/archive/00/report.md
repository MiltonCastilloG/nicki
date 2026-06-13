# Task archive — 00

## Task

Slug `00`. JSON status architecture migration. Branch `main`.

## Story

global-status.json registry · per-task status.json · hook task-id resolution · registry start/close write boundary · status-update sole writer · artifact pointers only · deprecated context YAML · blocked open_questions · close archive before delete · smoke boundary scripts

## Outcome

Shipped to `main`. Archived at `docs/archive/00/`. All 26 subtasks complete.

## Process

**Spec** captured two-layer JSON model, write boundaries, and caveman default for workflow Markdown.

**Subtasks** decomposed schema work, agent/skill migration, hook contract, smoke checks, and doc alignment.

**Execute** created `global-status-format.md`, `status-format.md`, hook-contract skill, register/unregister scripts, example JSON files, and updated Nicki bootstrap chain.

**Close** archived to `docs/archive/00/`; construction source torn down.

## Decisions

Registry touched only at start and close. Status-update sole per-task writer. Handoff bodies stay YAML/Markdown. Context YAML deprecated.

## Suggestions

Run first real worktree close to validate archive-then-delete policy end-to-end.
