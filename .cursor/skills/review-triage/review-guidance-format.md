# Review guidance format

Review guidance files are created when a prior review is not valid enough to act on. They are **input** for a later review run.

Default path: `current-task/review-inputs/rN-review.yaml` under the worktree scope root.

## Top-level fields

Review YAML shape plus one extra input-only key:

| Field | Required | Description |
|-------|----------|-------------|
| `approved` | Yes | Usually `false`; marks that the previous review should not be treated as approved |
| `content` | Yes | Short explanation of why review should be rerun |
| `important-considerations` | Yes | Context the next review must keep in mind |

`important-considerations` is **input-only**. Review output still has only `approved` and `content`.

## YAML example

```yaml
approved: false
content: |
  Previous review was discarded because its blocking findings were outside the hero task scope.
  Rerun review using the current task spec, subtask list, execution, and the considerations below.

important-considerations:
  - Do not block the hero task on footer redesign requests; footer work is outside spec.scope.in.
  - Still report build, lint, test, safety, or correctness issues even if they were not named in the subtasks.
  - Verify CTA, headline, subcopy, and semantic token requirements from the spec.
```

## Rules

- Use only when a review was `discarded` or mostly invalid and should be rerun.
- Keep considerations actionable and scoped to review behavior.
- Do not include implementation instructions or subtask edits.
- Do not use this to hide real in-scope blockers from the next review.
