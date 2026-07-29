# Harness alignment — four subagent briefs

> **Superseded (2026-07-29).** Historical Task briefs from the harness write-contract
> alignment. Do **not** follow these steps as current instructions.
>
> Current truth:
> - Position: `current_step` + `next_step` + artifacts — **`completed_steps` removed**
> - Modes: `--mode normal|adhoc|jump` — see [`flexibility.md`](flexibility.md)
> - Write / bootstrap contracts: [`status-format.md`](../.cursor/skills/current-task-update/status-format.md), `nicki.md`, `routing.json`
> - Gate bugs: [`harness-gate-bugs.md`](harness-gate-bugs.md)
> - Next optional work: [`flexibility_next_steps.md`](flexibility_next_steps.md)

Run **in order** (1 → 2 → 3 → 4). Each step is one fresh Task (`subagent_type: generalPurpose`). Do not commit unless the user asks.

**ADR:** [`superpowers/specs/2026-07-17-harness-read-write-types-design.md`](superpowers/specs/2026-07-17-harness-read-write-types-design.md)

---

## Step 1 — Contract: `next_step` only required

**Copy everything below the line into a new Task.**

```
Full Repository Path: /home/castlemill/repositories/nicki

## Goal

Align write contract: only `next_step` is required in sheep return YAML and in `update-status.py`. `completed_step` becomes optional everywhere in the write path.

## Scope.in (edit only these)

- `.cursor/skills/nicki/routing.yaml` — `sheep_return_contract` + `harness_failure.scripts.update-status.py` notes
- `.cursor/skills/current-task-update/scripts/update-status.py`
- `.claude/skills/nicki/routing.yaml` — keep in sync with `.cursor/` (symlink tree; edit canonical if only one copy is real)
- `.claude/skills/current-task-update/scripts/update-status.py` — same

## Scope.out

- Do not edit tests yet (step 2 repairs them).
- Do not trim nicki.md (step 4).
- Do not touch archive story.md files.

## routing.yaml — sheep_return_contract

Replace `required_fields` with **only**:

```yaml
required_fields:
  - next_step
```

Add a short `optional_fields` list (or extend `description`) documenting what sheep normally still send but the write script does not require:

- `worktree` — Nicki passes path separately; may appear in YAML
- `completed_step` — when present, drives `task.current_step`, `completed_steps` append, artifact pointer
- `completed_status` — default `complete`
- `artifact` — pointer when `completed_step` present
- `open_questions` — default `[]`
- `summary` — relay prose only

Update `harness_failure.scripts.update-status.py.notes` to say: required summary field is **`next_step` only**; missing `next_step` → `written: false`; missing `completed_step` is allowed.

## update-status.py — behavior

1. `REQUIRED_SUMMARY_FIELDS = ("next_step",)` only.

2. **Always write `task.current_step`** (flexibility: YAML may omit `completed_step`, but status.json must always have `current_step`):
   - If `completed_step` **present** (non-empty string): set `task.current_step` = `completed_step`; append to `task.completed_steps` when `completed_status == "complete"` (default); call `_set_artifact_pointer(status, completed_step, artifact)`
   - If `completed_step` **absent**: still write `task.current_step` — keep existing `task.current_step` when status already exists; on fresh init use `"start"`. Do **not** append `completed_steps`. Do **not** set artifact pointer.
   - Always set `task.next_step` from summary

3. Fresh init (`status.json` missing):
   - `task.next_step` = summary `next_step`
   - `task.current_step` = `completed_step` if provided, else `"start"`
   - `completed_steps`: if `completed_step` provided and complete, `[completed_step]`, else `[]`

5. Success stdout: include `"completed_step": <value or null>` and `"next_step"`.

6. Input error: only when `next_step` missing/empty/non-string.

7. Update module docstring to match.

## Verify

```bash
cd /home/castlemill/repositories/nicki
python3 .cursor/skills/current-task-update/scripts/update-status.py --help
# manual: tmp dir with only next_step in yaml → written true
# manual: yaml without next_step → written false, names next_step, exit 1
```

Report: files changed, behavior summary, any symlink duplication notes.
```

---

## Step 2 — Repair (docs + tests + agents after contract)

**Run after step 1 merges or lands in the working tree.**

```
Full Repository Path: /home/castlemill/repositories/nicki

## Goal

Repair all prose, tests, and agent instructions to match step-1 contract (`next_step` required; `completed_step` optional). Update the harness ADR.

## Prerequisite

Step 1 complete: `routing.yaml` and `update-status.py` already use `next_step`-only required set.

## Scope.in

- `docs/superpowers/specs/2026-07-17-harness-read-write-types-design.md`
- `.cursor/agents/sheep-status.md` and `.claude/agents/sheep-status.md`
- `.cursor/agents/nicki.md` and `.claude/agents/nicki.md` — harness table / `written: false` lines only (not full trim)
- `.cursor/skills/current-task-update/SKILL.md` and `.claude/skills/current-task-update/SKILL.md` — required vs optional fields
- `tests/smoke/status_update.py`
- `.cursor/skills/nicki/scripts/validate-harness-stdout.py` (if comments reference old required set)

## Scope.out

- No `nicki.md` line deletions (step 4).
- No fixture `errors.yaml` cleanup (step 3).
- No archive edits.

## Required edits

### ADR (`2026-07-17-harness-read-write-types-design.md`)

Under **Write required fields**, list only `next_step` (+ `worktree` CLI).

Under **Write optional**, add `completed_step` with behavior: when present, updates current_step / completed_steps / artifact pointer; when absent, only advances `next_step`.

### sheep-status.md

- Required summary: **`next_step` only**
- Optional: `completed_step`, `artifact`, `completed_status`, `open_questions`, `summary`
- Note: Nicki still forwards full YAML; write script ignores missing optional fields

### current-task-update/SKILL.md

- Example blocks: show minimal `next_step`-only write where valid
- Document optional `completed_step` semantics matching script

### tests/smoke/status_update.py

- Keep case: valid summary with both steps + artifact
- Keep case: acceptance with `completed_step` + `next_step`, no artifact
- Change `summary-bad.yaml` case: use yaml with **no `next_step`** (remove `completed_step` from bad fixture or use empty next_step)
- Add case: **next_step only** (no `completed_step`) → `written: true`, `task.next_step` updated, `completed_steps` unchanged
- Assert bad case errors name `next_step` only

### nicki.md (harness section only)

- `update-status.py` row: required input = `next_step`; `written: false` when `next_step` missing

## Verify

```bash
cd /home/castlemill/repositories/nicki
python3 -m tests.smoke.status_update 2>/dev/null || python3 tests/smoke/status_update.py
# or: ./test.sh if present
```

Report: files changed, smoke result.
```

---

## Step 3 — Clean stale `validate-sheep-return` references

**Run after step 2.**

```
Full Repository Path: /home/castlemill/repositories/nicki

## Goal

Remove or replace live references to deleted `validate-sheep-return.py`. Leave historical archives unchanged.

## Scope.in (grep hits — fix live/fixture paths only)

- `.cursor/skills/errors-recording/scripts/fixtures/smoke-worktree/current-task/specs/errors.yaml`
- `.cursor/skills/errors-recording/scripts/fixtures/smoke-worktree/docs/archive/sheep-fallback/errors.yaml`
- `.claude/skills/errors-recording/scripts/fixtures/smoke-worktree/current-task/specs/errors.yaml`
- `.claude/skills/errors-recording/scripts/fixtures/smoke-worktree/docs/archive/sheep-fallback/errors.yaml`

## Scope.out (do NOT edit)

- `docs/archive/sheep-fallback/story.md` — historical Gherkin
- `docs/archive/bootstrap-script/story.md` — historical
- `docs/tasks.md` defer row for #9 (intentional)
- `docs/tasks-done.md` / `docs/archive/sheep-fallback/report.md` — already say superseded

## Replacement rule

Where `script_route` was `validate-sheep-return.py`, use:

`script_route: .cursor/skills/current-task-update/scripts/update-status.py`

Update `expected_stdout` / `stdin` / `validation_errors` in that fixture entry to match **update-status** contract:

- Input error example: stdin missing `next_step` → `{"written": false, "errors": ["missing required field: next_step"]}`
- Do not reference `valid:` field (that was validate-sheep shape)

Keep sibling entries for `check-gate.py` unchanged unless broken.

## Verify

```bash
cd /home/castlemill/repositories/nicki
rg 'validate-sheep-return' --glob '!docs/archive/**' --glob '!docs/tasks.md' --glob '!docs/tasks-done.md' --glob '!docs/superpowers/**'
```

Expect **zero** hits outside intentional defer/history docs.

Report: files changed, rg output.
```

---

## Step 4 — Trim orchestrator prose (P3)

**Run after step 2 smoke passes. Step 3 may run in parallel with 4 if different agents; prefer 2 → 3 → 4.**

```
Full Repository Path: /home/castlemill/repositories/nicki

## Goal

P3 trim per `docs/investigation-complexity.md` and `docs/tasks.md` #12–#14. Scripts are authoritative for gates, readiness routing, and sheep mapping.

## Prerequisite

Steps 1–2 done; `check-gate.py` + `bootstrap-context.py` wired in `nicki.md` already.

## Scope.in

- `.cursor/agents/nicki.md` and `.claude/agents/nicki.md`
- `.cursor/skills/current-task-update/status-read.md` and `.claude/skills/current-task-update/status-read.md`
- `docs/NICKI.md`

## Scope.out

- Do not delete Bootstrap or Transitions blocks that invoke scripts.
- Do not delete Describe/Spec relay prose (not yet scripted).
- Do not edit `routing.yaml` or Python scripts.

## nicki.md — delete per investigation-complexity.md

Use current line numbers (may have shifted); delete **content equivalent** to:

| Delete | Content |
|--------|---------|
| Numbered workflow | Step list Nicki re-derives each turn |
| Context load-for-gates | Prose listing files to open for routing |
| Session bootstrap gates | Duplicate sync-block rules superseded by bootstrap stdout |
| Readiness table | Map readiness → route (bootstrap/check-gate own this) |
| Spec / partial review gates | Duplicated gate prose |
| Sheep map | step → subagent_type table |

**Add (~5 lines)** after Transitions: pointer — run `check-gate.py`; on deny show `reason`; on allow spawn `sheep` from stdout.

**Keep:** Harness failure block, Describe/Spec relay, Safety, disk bootstrap invoke lines.

## status-read.md

- Delete **Gates** and **Readiness** sections (L7–19 area) — field pointers + JSON example only per #13
- Keep bootstrap one-liner pointing at `bootstrap-context.py`

## NICKI.md (#14)

- Fix stale claims: Nicki **does** run shell for `bootstrap-context.py` and `check-gate.py` (not globally read-only for shell)
- Add short **Harness scripts** subsection (read / gate / write table) linking ADR
- Remove duplicated readiness/transition tables if they mirror deleted `nicki.md` content
- Optional: one paragraph bootstrap chain (session vs disk) if still missing

## Hard rule

If a deleted rule is **not** enforced by script yet, **keep** the prose. When unsure, keep.

## Verify

- Read trimmed `nicki.md` — Bootstrap, Transitions, relay, harness failure still present
- `wc -l` before/after for nicki.md and status-read.md
- No broken markdown links

Report: line counts removed, sections kept vs deleted, NICKI.md fixes made.
```

---

## After all four

| Check | Command |
|-------|---------|
| Contract | `rg 'REQUIRED_SUMMARY_FIELDS' .cursor/skills/current-task-update/scripts/update-status.py` → only `next_step` |
| Stale validator | `rg validate-sheep-return --glob '!docs/archive/**'` → only defer/history |
| Smokes | `./test.sh` or `python3 tests/smoke/status_update.py` |
| Backlog | Optionally add note to `tasks.md` #12–#14 when trim lands |

**Do not** re-open #9 `validate-sheep-return.py`.
