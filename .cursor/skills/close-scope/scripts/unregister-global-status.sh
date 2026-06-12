#!/usr/bin/env bash
# Unregister task from global-status.json. Only close-task should call this.
# Usage: unregister-global-status.sh <workspace_root> <task_id>
set -euo pipefail

ROOT="${1:?workspace root}"
TASK_ID="${2:?task id}"
GLOBAL="${ROOT}/global-status.json"

[[ -f "$GLOBAL" ]] || { echo "skip: no global-status.json"; exit 0; }

jq --arg id "$TASK_ID" 'del(.tasks[$id]) | if .active_task == $id then .active_task = ( .tasks | keys | .[0] // null) else . end' \
  "$GLOBAL" > "${GLOBAL}.tmp" && mv "${GLOBAL}.tmp" "$GLOBAL"

echo "unregistered: task $TASK_ID"
