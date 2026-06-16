#!/usr/bin/env bash
# Register task in global-status.json. Only sheep-start should call this.
# Delegates to register-global-status.py for per-project task id auto-increment.
# Usage: register-global-status.sh <workspace_root> <project> <slug> <worktree_path> [task_id]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ROOT="${1:?workspace root}"
PROJECT="${2:?project}"
SLUG="${3:?slug}"
WORKTREE_PATH="${4:?worktree path}"
TASK_ID="${5:-}"

if [[ -n "$TASK_ID" ]]; then
  exec python3 "$SCRIPT_DIR/register-global-status.py" \
    "$ROOT" "$PROJECT" "$SLUG" "$WORKTREE_PATH" "$TASK_ID"
else
  exec python3 "$SCRIPT_DIR/register-global-status.py" \
    "$ROOT" "$PROJECT" "$SLUG" "$WORKTREE_PATH"
fi
