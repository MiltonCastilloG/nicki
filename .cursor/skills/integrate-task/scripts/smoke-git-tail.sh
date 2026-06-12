#!/usr/bin/env bash
# Smoke git tail: sync + integrate leaves, status pointers, close gate.
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

check ".cursor/agents/sheep-sync.md"
check ".cursor/skills/sync-task/SKILL.md"
check ".cursor/agents/sheep-integrate.md"
check ".cursor/skills/integrate-task/SKILL.md"

! test -f ".cursor/agents/commit-task.md" || { echo "fail: commit-task agent should be removed"; FAIL=1; }
! test -f ".cursor/agents/push-task.md" || { echo "fail: push-task agent should be removed"; FAIL=1; }
! test -f ".cursor/agents/merge-task.md" || { echo "fail: merge-task agent should be removed"; FAIL=1; }
! test -f ".cursor/agents/publish-task.md" || { echo "fail: publish-task agent should be removed"; FAIL=1; }

grep -q '| `sync`' .cursor/skills/current-task-update/status-format.md || { echo "fail: no sync pointer in status-format"; FAIL=1; }
grep -q '| `integrate`' .cursor/skills/current-task-update/status-format.md || { echo "fail: no integrate pointer in status-format"; FAIL=1; }

grep -q 'Tail gate' .cursor/skills/close-task/SKILL.md || { echo "fail: close-task missing tail gate"; FAIL=1; }
grep -q 'sheep-integrate' .cursor/agents/nicki.md || { echo "fail: nicki missing integrate step"; FAIL=1; }
grep -q 'sheep-sync' .cursor/skills/nicki/routing.yaml || { echo "fail: routing missing sheep-sync"; FAIL=1; }
grep -q 'PROJECT' .cursor/skills/start-task/scripts/start-worktrees.sh || { echo "fail: start-worktrees missing PROJECT"; FAIL=1; }

grep -q 'projects/' README.md || { echo "fail: README missing project-local paths"; FAIL=1; }

grep -q 'syncs/' .cursor/skills/sync-task/sync-format.md || { echo "fail: sync-format missing syncs path"; FAIL=1; }
grep -q 'integrates/' .cursor/skills/integrate-task/integrate-format.md || { echo "fail: integrate-format missing integrates path"; FAIL=1; }

exit "$FAIL"
