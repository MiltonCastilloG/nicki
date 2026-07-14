#!/usr/bin/env bash
# Root smoke test runner for Nicki harness and workflow scripts.
# Usage: ./test.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

run() {
  local script="$1"
  echo "==> ${script#tests/smoke/}"
  bash "$script" "$ROOT"
}

run tests/smoke/agent-tools.sh
run tests/smoke/harness-failure.sh
run tests/smoke/errors-append.sh
run tests/smoke/status-update.sh
run tests/smoke/status-boundary.sh
run tests/smoke/readiness-mapping.sh
run tests/smoke/git-tail.sh

echo "test: all smoke passed"
