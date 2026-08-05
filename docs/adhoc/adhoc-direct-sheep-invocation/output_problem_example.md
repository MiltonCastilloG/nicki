# Output shape problem — examples from ad-hoc archive

Date: 2026-08-05  
Source: first live ad-hoc `sheep-archive` run (`docs/adhoc/adhoc-direct-sheep-invocation/`).  
Related: [`2026-08-05-adhoc-direct-sheep-invocation-design.md`](../../superpowers/specs/2026-08-05-adhoc-direct-sheep-invocation-design.md), artifact ownership (Nicki owns **input/output paths**; sheep own **document bodies**).

## The broader problem

Nicki (or the ad-hoc caller) already owns **where** to write — the path goes in the prompt. Sheep still decide **what** the file contains: required fields, enums, default values, which companion files must exist. That is the mirror of the old input problem. Paths are caller-owned; output *shape* is still sheep-owned.

Follow-up work should make output contracts caller-driven the same way paths are. Until then, these friction points from the live archive run are the examples.

## Examples (do not fix in the ad-hoc path/input pass)

### 1. Unconditional `outcome.status: pending_integrate`

`task-archive` step 3 always sets `pending_integrate` ("integrate has not run yet"). That was false for a change landed on `main` with no integrate step. The sheep chose a pipeline-shaped outcome; the caller had no way to pass the real status.

### 2. `story.md` required when no story exists

Format/rules treat `story.md` as required before later sync/integrate. Ad-hoc (and any run without a describe step) has nothing to copy. "Required" is an output-set decision the sheep enforces, not something the caller can waive.

### 3. Process sourcing has no off-pipeline path

`archive-format.md` builds `process` only from status handoffs + `side_effects`, and bans inventing history. Ad-hoc has neither. The sheep had to improvise from the design doc and git log with no sanctioned shape for "caller-supplied process."

### 4. `meta.source_context` only documents `status.json`

Schema example pins `source_context` to `current-task/status.json`. Ad-hoc's real source was a design path. No first-class field for "what the caller said to archive from."

### 5. No field for who invoked the archive

Pipeline vs ad-hoc is invisible from `report.json` alone. The live run added a non-schema `adhoc_run` block. Invocation belongs in a caller-owned or contract-owned place, not sheep improvisation.

### 6. `suggestions.area` enum has no archive/tooling value

Allowed areas are pipeline steps (`spec | subtasking | execute | …`). Friction about the archive skill itself had no legal `area`. Enum is sheep/format-owned output vocabulary.

### 7. Return `completed_status` vocabulary

Sheep return contract is `complete` | `blocked`. The live archive returned `"success"`. Return JSON shape is still under-specified in `sheep-archive.md` and easy for the sheep to invent.

## What is *not* this problem (handled in the ad-hoc path/input pass)

- Delete of `artifacts.spec` / `artifacts.subtasks` (cleanup purpose of archive).
- Archive always writes under `<prefix>/docs/archive/<slug>/`; caller passes `prefix`.
- Dropping "No status.json → ask" — inputs and output path are enough.
- Inputs that assume a worktree / `close-scope` when the caller already packs paths.

## Desired direction (for the follow-up)

Caller packs path **and** enough of the output contract that the sheep does not invent defaults for status enums, required companion files, or process sources. Exact design TBD — this file is evidence, not the design.
