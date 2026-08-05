# Handoff: caller-owned output shape (all sheep)

Date: 2026-08-05  
Status: **ready for new session / brainstorm**  
Slug hint: `caller-owned-output-shape` (or similar)

## Task for the next session

**Make output shape controlled the same way input (and write path) already is — for every sheep, not only archive.**

Today the caller (Nicki on the pipeline, or the parent agent ad-hoc) packs **paths**: where to read, where to write. Sheep must not invent those. They still invent **what** goes in the file and in the return JSON: required fields, enums, defaults (`pending_integrate`), companion files (`story.md`), process sources, schema vocabulary. That is the remaining half of ownership.

| Already caller-owned | Still sheep-owned (this task) |
|---|---|
| Input paths / worktree / `source_document` | Document body *schema* and required fields |
| Output path (`prefix` + slug for archive; prompt path for describe/spec/subtasks) | Defaults when the caller did not say (e.g. always `pending_integrate`) |
| Ad-hoc vs pipeline dispatch | Return JSON extras beyond the thin contract; invented enums |

Sheep still **author content** (story prose, spec requirements, archive summary text). They must not **choose the contract** — which fields exist, which are required, which enum values are legal — unless the caller packed that contract or pointed at a format the caller selected.

Exact mechanism TBD in brainstorm (prompt section? routing fields? thin format pointer?). This file is evidence + scope, not the design.

## Scope

- **In:** all sheep that write documents or return structured JSON — at least describe, spec, subtasks, archive, review (summary/verdict), fallback/errors; and the shared return contract (`completed_status`, `open_questions`, `artifact`, `summary`).
- **Especially important evidence:** archive (`task-archive` + `archive-format.md`) — richest live friction.
- **Out / already done:** path ownership, ad-hoc direct invocation, archive `<prefix>/docs/archive/<slug>/`, delete of pointed `spec`/`subtasks`, no close-scope for archive inputs. Do not reopen those.

## How input works today (the pattern to mirror)

1. Caller packs concrete paths in the Task prompt (and Nicki shows them on the transition card).
2. Sheep/skill write or read **only** there; they do not resolve registry/close-scope when the caller already named paths.
3. Format files describe the artifact type; they must not override the caller's path.

Apply the same discipline to **shape**: caller packs (or points at) the output contract; sheep fill content into that shape; skills/formats stop shipping hard defaults that contradict the caller.

Baseline path ownership: [`2026-08-01-artifact-ownership-and-position-design.md`](../../superpowers/specs/2026-08-01-artifact-ownership-and-position-design.md).  
Ad-hoc dispatch: [`2026-08-05-adhoc-direct-sheep-invocation-design.md`](../../superpowers/specs/2026-08-05-adhoc-direct-sheep-invocation-design.md).  
Live rule: `.cursor/rules/nicki-default.mdc`. Nicki ownership blurb: `.cursor/agents/nicki.md`.

## Archive evidence (two live ad-hoc runs)

| Run | Location | Result |
|---|---|---|
| 1 (pre path fix) | `docs/adhoc/adhoc-direct-sheep-invocation/` (scratch; may be untracked) | Mechanism worked; skill assumed pipeline paths |
| 2 (post path fix, commit `3f4e757`) | `docs/archive/adhoc-direct-sheep-invocation/` | Paths correct; **output-shape** friction remained |

Design/implementation commits (local `main`): `52432f0` → `755616b` → `3f4e757`.

### Concrete archive friction (still open — shape, not path)

1. **`outcome.status: pending_integrate` hardcoded** in `task-archive` step 3 — false when work landed on `main` with no integrate.
2. **`story.md` treated as required** when no describe/`artifacts.story` exists.
3. **`process` only from status handoffs + `side_effects`** — empty for source-document ad-hoc; no caller-supplied process shape.
4. **`meta.source_context` exemplified only as `status.json`** — ad-hoc source was a design path.
5. **No caller field for invocation** (pipeline vs ad-hoc) — sheep improvised non-schema blocks.
6. **`suggestions.area` enum** is pipeline-step vocabulary only — no archive/tooling value.
7. **Return `completed_status`** — contract is `complete` \| `blocked`; first live run returned `"success"` (second run got `complete`). Under-specified in sheep prose; easy to invent.

Second-run note: path/input matched (`prefix`, no close-scope, no no-status ask, errors only if named). Remaining hits were exactly 1–3 and 4 above.

## Other sheep to check in the follow-up (not fully dogfooded)

Same class of problem — skills/formats decide shape:

| Sheep | Likely shape ownership leaks |
|---|---|
| `sheep-spec` | Spec JSON schema / required keys; block-without-write rules |
| `sheep-describe` | Story/Gherkin shape; whether path alone is enough |
| `sheep-subtask` | Checklist format; frontmatter |
| `sheep-review` | Verdict vocabulary in `summary` (`acceptance` / `execute` / `review`) — Nicki consumes it for `next_step` |
| `sheep-fallback` | `errors.v1` entry shape |
| All | Shared return contract in `routing.json` `sheep_return_contract` vs per-sheep prose drift |

## Files to open first

- This handoff
- `.cursor/skills/task-archive/SKILL.md` + `archive-format.md`
- `.cursor/agents/sheep-*.md` (caller-neutral path wording already; shape still skill-led)
- `.cursor/skills/nicki/routing.json` (`prompt` strings, `sheep_return_contract`)
- `docs/archive/adhoc-direct-sheep-invocation/report.json` (second live output)
- Specs linked above

## Non-goals for that session

- Reintroducing `--mode adhoc` or check-gate
- Changing ad-hoc = direct sheep spawn
- Moving archive off `<prefix>/docs/archive/<slug>/`
- Softening archive's delete of pointed `current-task` spec/subtasks

## Done when (acceptance sketch for the later design)

- Caller can determine output contract the same way they determine paths (precise mechanism in the design).
- Sheep/skills do not invent defaults that contradict a packed contract.
- Archive ad-hoc with `source_document` can produce a valid report without fake `pending_integrate` / empty forced process / required missing `story.md` — unless the caller asked for those.
- Pattern applies across sheep, not an archive-only special case.
- Documented in `docs/superpowers/specs/` and verified (prefer another ad-hoc archive dogfood).
