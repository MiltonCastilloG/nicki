---
name: conflict-resolution
description: "Protocol for resolving git merge conflicts: the user decides every conflicted file or hunk, never the agent."
---

# Conflict Resolution

Use whenever a git merge encounters conflict markers.

This skill defines the **only** allowed conflict-resolution protocol. You may summarize conflicts. You may not choose resolutions.

You cannot reach a human. So the protocol is two passes: you stop and report the conflicts, your caller gets the answers, and your caller re-spawns you with them.

## Pass one — stop on the conflicted tree

1. Run `git status --porcelain` and list every unmerged path.
2. Read each conflicted file and identify each conflict region.
3. Return one `open_questions` entry per conflicted file or hunk. Each entry carries the path, enough surrounding context for the user to decide without opening the file, and the candidate resolutions as `options`.
4. **Leave the working tree exactly as it is** — conflict markers in place, nothing staged, merge in progress. That state is what lets pass two finish the same merge.
5. Say in `summary` that the merge is paused mid-conflict and how many files are waiting.

Do not write a pause file. The conflicted tree is the saved state.

## Allowed options

Offer these for each conflict unless the caller already relayed exact instructions:

- Keep current branch version
- Keep incoming/source branch version
- Combine both
- User provides exact replacement text

When the answer is "combine both" or "exact replacement text" and the content is not explicit, that is another question — return it and stop again rather than filling the gap yourself.

## Pass two — apply what the caller relayed

Only when your prompt carries the user's resolutions:

1. Apply each resolution **verbatim** to its path. Infer nothing, extend nothing to a hunk the user did not answer.
2. Remove conflict markers.
3. Stage the resolved file.
4. Any conflict the prompt did not answer goes back as an `open_questions` entry. Stop again.

## Do not

- Do not infer or guess a resolution.
- Do not choose based on style, tests, or apparent intent without user input.
- Do not use `ours`, `theirs`, or broad strategy flags unless the user explicitly instructs that for the specific conflict.
- Do not run destructive commands such as `git reset --hard`, `git checkout --`, or `git merge --abort` without explicit user approval.
- Do not commit or push as part of this skill.

## Verification

After applying relayed resolutions:

- Check `git status --porcelain` for unmerged paths.
- Search changed files for conflict markers:
  - `<<<<<<<`
  - `=======`
  - `>>>>>>>`
- If any marker remains, return it as a question and stop — never edit past it.

## Record

Name the resolved paths and the resolution the user chose for each in your return `summary`. There is no conflict handoff file.
