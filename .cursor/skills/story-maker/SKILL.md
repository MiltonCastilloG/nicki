---
name: story-maker
description: "Probe task intent and write a Gherkin story. Defines what to build — not how."
---

# Story Maker

Write the story at the **output path Nicki’s prompt gives** (usually `current-task/story.md` under the worktree). **What** to build — not **how**.

## Rules

1. Read `task.original` from the prompt; ask if missing or slug-only.
2. When detail is insufficient for testable Gherkin, ask organized questions **before** any draft. Do not invent unstated specifics.
3. Draft Gherkin (`Feature:`, As a / I want / So that, ≥1 `Scenario:`) in memory — do **not** write the story file on a first draft alone.
4. Revise until explicit user approval (`approve`, `continue`, `go`) or user confirms no gaps remain. Iterate scenario-by-scenario when partially approved.
5. Write only when `open_questions` would be `[]` and user approval is in the prompt — **only** at Nicki’s path.
6. When the human user is silent, pause — do not speculate or invent specifics.

**Write only** Nicki’s story path. Never edit application code, specs, subtasks, or `status.json`.
