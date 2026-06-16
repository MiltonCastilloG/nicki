---
worktree: gherkin-spec-mutual-understanding
generated_by: subtask-maker
spec: current-task/specs/gherkin-spec-mutual-understanding.yaml
context: current-task/status.json
title: Gherkin and spec mutual understanding
constraints:
  - no-commit
  - no-new-deps
---

# Subtasks

- [x] Update nicki.md Describe to ask organized chat questions when task.original lacks detail needed for testable Gherkin before showing any draft.
- [x] Update nicki.md Describe to keep Gherkin drafts in chat only until explicit user approval and persist story.md once via sheep-status after approval.
- [x] Update nicki.md Describe to support multi-round revision, scenario-by-scenario iteration, and no downstream transition while scope, actor, or acceptance gaps remain.
- [x] Update nicki.md Describe to pause without inventing specifics when the user is silent and to forbid reopening describe after the spec step begins.
- [x] Update nicki.md to relay sheep-spec open_questions in chat, allow multiple resolution rounds, and resend sheep-spec after user answers and permits persistence via sheep-status.
- [x] Update nicki.md to withhold sheep-subtask while spec open_questions remain non-empty with no user override to force advance.
- [x] Update sheep-spec.md so vague or forked approved stories block without writing spec YAML and return populated open_questions for Nicki to relay.
- [x] Update sheep-spec.md so the spec file is written only when all open_questions would be empty and requirement forks are listed as options awaiting user pick.
- [x] Update spec-maker/SKILL.md to enforce ask-first behavior and prohibit writing a spec file while open_questions remain unresolved.
- [x] Update spec-maker/SKILL.md to require written specs include open_questions as an empty list when the file is written.
- [x] Confirm no edits were made to check-gate.py, routing.yaml, status-read.md, status-format.md, current-task-update/SKILL.md, story-format.md, or spec gate smoke fixtures.
- [x] Manually verify the tetris ghost piece describe flow asks about unstated details before inventing them and persists story.md only after user approval.
- [x] Manually verify the tetris ghost piece spec flow blocks with open_questions for remaining ambiguities, writes spec only after resolution with open_questions empty, and reaches subtasks without execute.
- [x] Add story-maker/SKILL.md with ask-first Gherkin logic translated from former nicki.md Describe rules.
- [x] Add sheep-describe.md mirroring sheep-spec path-and-handoff pattern.
- [x] Collapse nicki.md Describe to Describe relay; restore pause-on-silence for Nicki orchestration context.
- [x] Wire routing.yaml describe step to sheep-describe (nicki_only false).
