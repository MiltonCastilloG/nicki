#!/usr/bin/env bash
# Register task in global-status.json. Only start-task should call this.
# Usage: register-global-status.sh <workspace_root> <task_id> <project> <slug> <worktree_path>
set -euo pipefail

ROOT="${1:?workspace root}"
TASK_ID="${2:?task id}"
PROJECT="${3:?project}"
SLUG="${4:?slug}"
WORKTREE_PATH="${5:?worktree path}"

GLOBAL="${ROOT}/global-status.json"
STATUS_PATH="${WORKTREE_PATH}/current-task/status.json"

mkdir -p "$(dirname "$GLOBAL")"

if [[ -f "$GLOBAL" ]]; then
  EXISTING=$(jq -r --arg id "$TASK_ID" '.tasks[$id] // empty' "$GLOBAL")
  if [[ -n "$EXISTING" && "$EXISTING" != "null" ]]; then
    echo "skip: task $TASK_ID already registered"
    exit 0
  fi
  jq --arg id "$TASK_ID" \
     --arg project "$PROJECT" \
     --arg slug "$SLUG" \
     --arg wp "$WORKTREE_PATH" \
     --arg sp "$STATUS_PATH" \
     '.tasks[$id] = {project: $project, slug: $slug, worktree_path: $wp, status_path: $sp} | .active_task = $id' \
     "$GLOBAL" > "${GLOBAL}.tmp" && mv "${GLOBAL}.tmp" "$GLOBAL"
else
  jq -n \
     --arg id "$TASK_ID" \
     --arg project "$PROJECT" \
     --arg slug "$SLUG" \
     --arg wp "$WORKTREE_PATH" \
     --arg sp "$STATUS_PATH" \
     '{version: 1, active_task: $id, tasks: {($id): {project: $project, slug: $slug, worktree_path: $wp, status_path: $sp}}}' \
     > "$GLOBAL"
fi

echo "registered: task $TASK_ID -> $STATUS_PATH"
