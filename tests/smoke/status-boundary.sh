#!/usr/bin/env bash
# global-status.json must not change from per-task status updates alone
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
GLOBAL="${ROOT}/global-status.json"

if [[ ! -f "$GLOBAL" ]]; then
  echo "skip: no global-status.json (ok before first start-task)"
  exit 0
fi

BEFORE=$(sha256sum "$GLOBAL" | awk '{print $1}')
AFTER=$(sha256sum "$GLOBAL" | awk '{print $1}')

if [[ "$BEFORE" != "$AFTER" ]]; then
  echo "fail: global-status.json changed without start/close"
  exit 1
fi

echo "smoke-status-boundary: ok"
