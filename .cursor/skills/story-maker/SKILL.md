---
name: story-maker
description: "Write a Gherkin story from intent the caller has already established. Defines what to build — not how."
---

# Story Maker

Write the story at the **output path the caller's prompt gives** (usually `current-task/story.md` under the worktree). **What** to build — not **how**.

The interview is not yours. Your caller talks to the user, agrees on the intent, and hands you the result; you turn it into Gherkin. You cannot reach a human, so a question you raise is a stop, not a conversation.

## Rules

1. Read the intent from the prompt — `task.original` plus whatever the caller established with the user.
2. When it is insufficient for testable Gherkin, write no file: return the gaps as `open_questions` and stop. One entry per gap, with candidate answers when you can name them. Do not invent unstated specifics, and do not draft around a hole.
3. Write Gherkin: `Feature:`, As a / I want / So that, and at least one `Scenario:`. Every scenario must be checkable against the finished work.
4. Write only when `open_questions` would be `[]` — and **only** at the caller's path.

**Write only** the caller's story path. Never edit application code, specs, subtasks, or `status.json`.
