# Task archive format

`task-archive` writes under `docs/archive/<slug>/`.

## Outputs

```
docs/archive/<slug>/report.json
docs/archive/<slug>/report.md
docs/archive/<slug>/story.md      # copy from artifacts.story
docs/archive/<slug>/errors.json   # verbatim copy when current-task/specs/errors.json exists
```

Spec and subtask paths from status are **not** archived — delete from worktree after copy (see [task-archive/SKILL.md](SKILL.md) step 7).

## Load inputs

Read via `current-task/status.json` — [status-format.md](../current-task-update/status-format.md) `artifacts` + `open_questions`. Follow pointers; glob only if pointer missing.

**Process sourcing:** build `report.json` `process` in two passes. Do **not** invent history from `completed_steps`.

1. **Handoffs** — for each step with an artifact pointer, load the handoff and take a one-line summary from its `meta` or top-level summary fields.
2. **Side effects** — append one `process` row per `task.side_effects[]` entry (log order). Always include the row, even when `artifact` is null — a null still means the out-of-band run happened. Summary shape: `Ad-hoc <step> at <at> — <artifact|no artifact>`.

| Step | Artifact pointer | Summary source |
|------|------------------|----------------|
| `describe` | `artifacts.story` | story exists → brief line from story title or slug |
| `spec` | `artifacts.spec` | `meta.summary` or spec `title` |
| `subtasks` | `artifacts.subtasks` | subtask frontmatter `title` |
| `execute` | (none — execute omits artifact) | skip |
| `review` | `artifacts.review_validation` | validation `readiness.status` |
| `sync` | `artifacts.sync` | sync handoff `meta` |
| `integrate` | `artifacts.integrate` | integrate handoff `meta` |

```json
"process": [
  {"step": "execute", "summary": "Subtasks in progress."},
  {"step": "sync", "summary": "Feature branch pushed."},
  {"step": "sync", "summary": "Ad-hoc sync at 2026-07-29T08:14:02Z — current-task/syncs/foo.json"},
  {"step": "sync", "summary": "Ad-hoc sync at 2026-07-29T09:01:00Z — no artifact"}
]
```

No status.json → ask: archive from artifacts or stop.

Summarize handoffs — never paste full bodies, logs, diffs, transcripts, secrets.

## report.json

| Field | Req |
|-------|-----|
| `meta` | yes — `task-archive.v1`, `generated_by: task-archive`, `source_context` |
| `task` | yes — slug, title, original, type, branch |
| `story` | yes — keyword line of what shipped |
| `outcome` | yes — merge/push/commit final |
| `process` | yes — step + one-line summary |
| `decisions` | yes — `[]` OK |
| `open_questions` | yes — `[]` OK |
| `suggestions` | yes — see below |

```json
{
  "meta": {
    "schema": "task-archive.v1",
    "generated_by": "task-archive",
    "source_context": "current-task/status.json"
  },
  "task": {
    "slug": "hero-section",
    "title": "Hero section redesign",
    "original": "redesign hero section with headline, subcopy, CTA",
    "type": "feature",
    "branch": "feature/hero-section"
  },
  "story": "headline · subcopy · CTA · responsive layout",
  "outcome": {
    "status": "merged",
    "target": "main",
    "pushed_branch": "feature/hero-section",
    "final_artifact": "current-task/integrates/hero-section.json"
  },
  "process": [
    {
      "step": "spec",
      "summary": "Requirements captured."
    },
    {
      "step": "integrate",
      "summary": "Branch merged into main and pushed."
    }
  ],
  "decisions": [],
  "open_questions": [],
  "suggestions": [
    {
      "area": "subtasking",
      "suggestion": "Put CTA in spec before subtasks.",
      "evidence": "open_questions had CTA during spec."
    }
  ]
}
```

## suggestions

Scan: `open_questions`, blockers, triage, review inputs, push/merge conflicts, skipped subtasks.

```json
{
  "suggestions": [
    {
      "area": "spec | subtasking | execute | review | push | merge | orchestration",
      "suggestion": "One actionable next-time fix.",
      "evidence": "artifact path or short quote"
    }
  ]
}
```

Top items in `report.md` prose — may highlight 3–5.

## report.md

Terse prose per [caveman/SKILL.md](../caveman/SKILL.md) (lite default). Mirror `report.json`; `story` matches the story keyword line.

Sections:

1. Task — slug, title, branch
2. Story — same keyword line as `report.json`
3. Outcome — merged/pushed; final handoff path
4. Process — short paragraph per step
5. Decisions — omit when none
6. Open questions — omit when empty
7. Suggestions — top items only; omit when none

No raw diffs/logs. Clear prose for irreversible warnings.

## Harness errors reference

When `docs/archive/<slug>/errors.json` was copied, `report.json` or `report.md` may include a short note that harness errors were recorded and point to the archived errors file — never paste full failure bodies.

## Rules

- Compact — summarize, don't copy `current-task/` tree.
- `report.json`, `report.md`, and `story.md` required before second sync (commit/push) and integrate.
