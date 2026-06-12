#!/usr/bin/env bash
# Smoke 01-1 git tail: publish leaf, merge/publish pointers, close gate, project paths.
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"
FAIL=0

check() {
  if [[ ! -e "$1" ]]; then
    echo "fail: missing $1"
    FAIL=1
  else
    echo "ok: $1"
  fi
}

check ".cursor/agents/publish-task.md"
check ".cursor/skills/publish-task/SKILL.md"

grep -q '| `merge`' .cursor/skills/current-task-update/status-format.md || { echo "fail: no merge pointer in status-format"; FAIL=1; }
grep -q '| `publish`' .cursor/skills/current-task-update/status-format.md || { echo "fail: no publish pointer in status-format"; FAIL=1; }

grep -q 'Tail gate' .cursor/skills/close-task/SKILL.md || { echo "fail: close-task missing tail gate"; FAIL=1; }
grep -q 'publish-task' .cursor/agents/nicki.md || { echo "fail: nicki missing publish step"; FAIL=1; }
grep -q 'PROJECT' .cursor/skills/start-task/scripts/start-worktrees.sh || { echo "fail: start-worktrees missing PROJECT"; FAIL=1; }

grep -q 'projects/' README.md || { echo "fail: README missing project-local paths"; FAIL=1; }

# Handoff path convention
grep -q 'publishes/' .cursor/skills/publish-task/publish-format.md || { echo "fail: publish-format missing publishes path"; FAIL=1; }

exit "$FAIL"
