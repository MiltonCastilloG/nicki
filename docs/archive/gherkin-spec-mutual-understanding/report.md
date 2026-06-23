# Gherkin and spec mutual understanding

## Task

- **Slug:** gherkin-spec-mutual-understanding
- **Branch:** feature/gherkin-spec-mutual-understanding
- **Type:** feature

## Story

describe ask-first · chat-only drafts · spec block-without-write · open_questions gate · story-maker + sheep-describe refactor

## Outcome

Integrated on `main` at `d09b87a` (no-op merge — feature branch already an ancestor). Final handoff: `current-task/integrates/gherkin-spec-mutual-understanding.yaml`.

## Process

Describe captured two Gherkin Features: Nicki asks before inventing during describe; sheep-spec blocks without writing YAML when requirements fork or stay vague. User approved story meaning with "continue"; tetris ghost piece anchors acceptance scenarios. Spec defined seventeen requirements with empty open_questions and minimal touch surface. Subtasks produced a thirteen-item checklist. Execute updated nicki.md, sheep-spec.md, and spec-maker/SKILL.md, then trimmed redundant prose and refactored describe into story-maker + sheep-describe with routing.yaml wiring. Review approved with traceability PASS for ghost-piece flows; routing and README scope notes deferred. User accepted at ready_for_acceptance. Sync fast-forwarded main and pushed feature branch. Integrate confirmed main already contained feature commits.

## Decisions

Post-execute trim preserved guarantees while removing duplicate prose. Describe logic lives in story-maker and sheep-describe; Nicki keeps relay and pause-on-silence. routing.yaml describe → sheep-describe was intentional despite original out-of-scope listing.

## Suggestions

- Record post-execute refactors that touch out-of-scope paths as explicit sub-rounds before review.
- When push auth fails, verify remote SHA in integrate handoff (done here).
- Schedule P2 harness work for check-gate.py and full blocked-return contract.
