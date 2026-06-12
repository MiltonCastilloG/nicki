---
name: conflict-resolution
description: "Protocol for resolving git merge conflicts by asking the user for every conflicted file or hunk."
disable-model-invocation: true
---

# Conflict Resolution

Use whenever a git merge encounters conflict markers.

This skill defines the **only** allowed conflict-resolution protocol. Agents may summarize conflicts, but they must not choose resolutions themselves.

## Required behavior

For every conflicted file or hunk:

1. Read the conflicted file.
2. Identify each conflict region with enough surrounding context for the user to decide.
3. Ask the user how to resolve it using `AskQuestion`.
4. Apply only the user-approved resolution.
5. Remove conflict markers.
6. Stage the resolved file.
7. Record the user prompt and answer in the agent's handoff artifact.

## Allowed options

Present these options for each conflict unless the user has already provided exact instructions:

- Keep current branch version
- Keep incoming/source branch version
- Combine both
- User provides exact replacement text

If the user chooses "combine both" or "exact replacement text" and the required content is not explicit, ask for the exact resulting text before editing.

## Do not

- Do not infer or guess a resolution.
- Do not choose based on style, tests, or apparent intent without user input.
- Do not use `ours`, `theirs`, or broad strategy flags unless the user explicitly instructs that for the specific conflict.
- Do not run destructive commands such as `git reset --hard`, `git checkout --`, or `git merge --abort` without explicit user approval.
- Do not commit or push as part of this skill.

## Verification

After applying user-approved resolutions:

- Check `git status --porcelain` for unmerged paths.
- Search changed files for conflict markers:
  - `<<<<<<<`
  - `=======`
  - `>>>>>>>`
- If any marker remains, ask again before editing.

## Handoff record

The calling agent should record:

```yaml
user_resolutions:
  - path: src/example.ts
    prompt: "Resolve conflict in src/example.ts around function buildHero."
    answer: "Keep current branch logic and incoming import order."
```

Use the calling agent's handoff schema for the rest of the artifact.
