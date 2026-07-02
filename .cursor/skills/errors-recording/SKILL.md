---
name: errors-recording
description: "Append harness script failure records to current-task/specs/errors.yaml (errors.v1)."
disable-model-invocation: true
---

# Errors recording

Append one harness failure to `current-task/specs/errors.yaml`. Schema: [errors-format.md](errors-format.md).

## Inputs

| Input | Required |
|-------|----------|
| Worktree path | Yes |
| Failed script route | Yes |
| Script input | Yes |
| Expected output contract | Yes |
| Actual failure (`exit_code`, `stdout`, `stderr`, `validation_errors`) | Yes |

## Procedure

1. Resolve worktree to absolute path; derive slug from folder name.
2. Target: `current-task/specs/errors.yaml`.
3. Load existing YAML when present; else init `meta.schema: errors.v1` and `failures: []`.
4. Append one failure entry with unique `id` (ISO8601 UTC; add `-N` suffix on collision).
5. Write file back — preserve all prior entries.

Prefer: `python3 .cursor/skills/errors-recording/scripts/append-error.py` with JSON flags.

## Write boundary

- Write only `current-task/specs/errors.yaml`.
- Never write `status.json` or modify harness script source.
