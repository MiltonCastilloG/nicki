# Archive: review-write-nothing

## Task

- **slug:** `review-write-nothing`
- **title:** Review never mutates subtasks
- **branch:** `main`
- **type:** fix

## Story

review write-nothing · suggested fixes in return · Nicki asks approval · sheep-subtask appends ## Fix · preserve [x] · no checklist mutate from review

## Outcome

`pending_integrate` (skill default). Target `main`. No feature branch, no integrate handoff. Landed on local `main` as `8da7680`. Final artifact: `docs/archive/review-write-nothing/report.json`.

Ad-hoc archive from commit + landed prose. No `status.json`, no errors path — no `errors.json`. No task artifacts — deleted nothing. No `story.md` (no `artifacts.story`).

## Process

Empty. No handoff pointers, no `side_effects`. Source: commit `8da7680` plus review / Nicki / subtask / routing / README / knowable-outputs prose.

## Decisions

- Review writes nothing (no handoffs, no checklist mutate).
- Suggested fixes stay in the sheep return.
- Nicki relays fixes, waits for approval, then sends `sheep-subtask` to append `## Fix`.
- Subtask-maker apply-fixes mode does not regenerate from the spec; preserves `- [x]`.
- `fix_required` → approval → `sheep-subtask` → `execute`.

## Suggestions

1. **orchestration** — Smoke-test ad-hoc review → approved `sheep-subtask` `## Fix` append on a throwaway checklist.
