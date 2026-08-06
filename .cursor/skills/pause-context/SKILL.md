---
name: pause-context
description: "Save work-in-progress to a caller-named file when stopping with a question, and resume from it when the caller says to."
disable-model-invocation: true
---

# Pause context

You cannot reach a human mid-run. When you need an answer before you can finish, you stop and return the question — see `open_questions` in [status-format.md](../current-task-update/status-format.md). Everything you learned before stopping dies with the spawn unless you write it down. This skill is where you write it down.

Use it only when the pause is expensive to repeat — you explored the codebase, settled several decisions, and one unanswered question is blocking the rest. A cheap question needs no file.

## Inputs

| Input | Required |
|-------|----------|
| Pause path — the caller names it, as with every other file you write | Yes |
| Resume instruction — the caller's prompt says to read the pause file and the answers to your questions | Only when resuming |

You never choose the path. When the caller gave you no pause path, you have no pause file; return the question and stop.

## Stopping

1. Write the pause file at the path you were given.
2. Return your questions in `open_questions` and stop. Name the pause path in `summary` so the caller can hand it back.

Markdown, no schema. Cover four things:

- **Explored** — what you read and what you found, so the next spawn does not repeat the search.
- **Settled** — decisions already made and why, so they are not reopened.
- **Remaining** — what is left once the question is answered.
- **Stopped on** — the question, restated with enough context to be re-read cold.

Write for a reader who has none of your context, because that is exactly who reads it: yourself, in a fresh spawn.

## Resuming

Read the pause file **only when the caller's prompt tells you to**. A file sitting at a path you were not pointed at is not yours to read.

Then: treat "explored" and "settled" as already done, apply the answers the caller relayed, finish the work, and **delete the pause file**. It does not survive the step it belongs to.

## Write boundary

- Write only the pause path you were given, plus your normal output artifact.
- Never write `status.json`, and never add the pause path to `status.artifacts`.
- Nothing downstream reads this file — not review, not archive, not the next step. It records *incomplete* work, which is what separates it from a handoff. The day something reads it as a record, it has become one.
