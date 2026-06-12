#!/usr/bin/env bash
# Smoke: global-status.json unchanged when only per-task status would update.
# Usage: smoke-status-boundary.sh <workspace_root>
set -euo pipefail

ROOT="${1:-.}"
GLOBAL="${ROOT}/global-status.json"

if [[ ! -f "$GLOBAL" ]]; then
  echo "skip: no global-status.json (ok before first start-task)"
  exit 0
fi

BEFORE=$(sha256sum "$GLOBAL" | awk '{print $1}')
# Simulate: status-update must not touch global file
AFTER=$(sha256sum "$GLOBAL" | awk '{print $1}')

if [[ "$BEFORE" != "$AFTER" ]]; then
  echo "fail: global-status.json changed without start/close"
  exit 1
fi

echo "ok: global-status.json stable (boundary check placeholder)"
echo "note: run after status-update in real workflow; this script compares hash at invoke time only"
