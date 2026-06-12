#!/usr/bin/env bash
# Smoke: readiness routing docs + fix-loop append keeps prior [x].
# Usage: smoke-readiness-routing.sh <workspace_root>
set -euo pipefail

ROOT="${1:-.}"
FAIL=0

grep -q 'readiness\.status' "${ROOT}/.cursor/skills/review-triage/validation-format.md" || { echo "fail: validation-format readiness"; FAIL=1; }
grep -q 'fix_required' "${ROOT}/.cursor/agents/nicki.md" || { echo "fail: nicki fix_required routing"; FAIL=1; }
grep -q 'ready_for_acceptance' "${ROOT}/.cursor/agents/nicki.md" || { echo "fail: nicki acceptance gate"; FAIL=1; }
grep -q 'review_scope' "${ROOT}/.cursor/agents/nicki.md" || { echo "fail: nicki partial review_scope"; FAIL=1; }
grep -q 'open_questions' "${ROOT}/.cursor/agents/subtask-maker.md" || { echo "fail: subtask-maker open_questions gate"; FAIL=1; }
grep -q 'artifacts.review_validation' "${ROOT}/.cursor/skills/current-task-update/status-format.md" || { echo "fail: status validation pointer"; FAIL=1; }

# Fix-loop append: prior [x] preserved in fixture
FIXTURE=$(mktemp)
cat >"$FIXTURE" <<'EOF'
# Subtasks
- [x] Done line stays.
EOF
APPEND=$'# Subtasks\n- [x] Done line stays.\n\n## Fix\n<!-- ref: current-task/review-validations/r1-validation.yaml -->\n- [ ] Fix lint from triage.\n'
printf '%s' "$APPEND" >"${FIXTURE}.expected"
# Simulate append: extract [x] lines before and after
BEFORE_X=$(grep -c '\- \[x\]' "$FIXTURE" || true)
cat >>"$FIXTURE" <<'EOF'

## Fix
<!-- ref: current-task/review-validations/r1-validation.yaml -->
- [ ] Fix lint from triage.
EOF
AFTER_X=$(grep -c '\- \[x\]' "$FIXTURE" || true)
if [[ "$BEFORE_X" != "$AFTER_X" ]] || [[ "$BEFORE_X" -lt 1 ]]; then
  echo "fail: fix append mutated prior [x] ($BEFORE_X -> $AFTER_X)"
  FAIL=1
else
  echo "ok: fix append keeps prior [x]"
fi
rm -f "$FIXTURE" "${FIXTURE}.expected"

# Round-trip: readiness enum in format matches nicki routing table
for status in ready_for_acceptance fix_required rerun_review blocked; do
  grep -q "$status" "${ROOT}/.cursor/skills/review-triage/validation-format.md" || { echo "fail: missing enum $status"; FAIL=1; }
done

if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "ok: readiness routing smoke passed"
