# Task archive format

Task archives are the compact root-level record written by `/close-task` after Nicki has completed merge and `/current-task-update` has recorded the merge result.

Archive path:

```
task-archive/<slug>/summary.yaml
```

The archive keeps only compact task context, task definition, process/iterations, decisions, open questions, and suggestions. It does not copy the full `current-task/` artifact tree.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Archive identity and source context |
| `task` | Yes | Compact task definition |
| `outcome` | Yes | Final merge/push/commit outcome |
| `process` | Yes | Compact step-by-step workflow summary |
| `decisions` | Yes | Important choices and user decisions |
| `open_questions` | Yes | Questions remaining at close time, usually empty |
| `suggestions` | Yes | Suggestions for smoother future task development |

## YAML example

```yaml
meta:
  schema: task-archive.v1
  generated_by: close-task
  source_context: current-task/current-task-context.yaml

task:
  slug: hero-section
  title: Hero section redesign
  original: "redesign hero section with headline, subcopy, CTA"
  type: feature
  branch: feature/hero-section

outcome:
  status: merged
  target: main
  pushed_branch: feature/hero-section
  final_artifact: current-task/merges/hero-section.yaml

process:
  - step: spec
    summary: Requirements and acceptance criteria captured.
  - step: subtasks
    summary: Subtask checklist mapped requirements to build, test, and verification items.
  - step: execute
    summary: Subtasks executed and verification evidence recorded.
  - step: review
    summary: Review completed with no blocking findings.
  - step: push
    summary: Branch pushed after pre-push base merge.
  - step: merge
    summary: Pushed branch merged into main.

decisions:
  - step: push
    decision: Resolved pre-push conflict by keeping task branch behavior and main import order.

open_questions: []

suggestions:
  - area: subtasking
    suggestion: Add CTA destination to the spec before writing subtasks to avoid a decision step.
    evidence: "open_questions included CTA destination during spec."
```

## Rules

- Keep the archive compact; summarize instead of copying full artifacts.
- Use source artifact paths in `evidence` when useful.
- Include suggestions based on task artifacts, open questions, blockers, failed steps, review triage, conflict resolutions, and close-task judgment.
- Do not include secrets, raw diffs, long logs, or full transcripts.
