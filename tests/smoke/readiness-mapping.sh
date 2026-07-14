#!/usr/bin/env bash
# Validation skill — readiness enums, fixtures, fix-append semantics
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
FAIL=0
FIXTURE_DIR="${ROOT}/.cursor/skills/validation/scripts/fixtures"

check_enum() {
  local file="$1"
  for status in ready_for_acceptance fix_required blocked; do
    grep -q "$status" "$file" || { echo "fail: missing enum $status in $file"; FAIL=1; }
  done
}

check_enum "${ROOT}/.cursor/skills/validation/validation-format.md"
grep -q 'deferred_scope' "${ROOT}/.cursor/skills/validation/validation-format.md" || { echo "fail: deferred_scope"; FAIL=1; }
grep -q 'next-steps' "${ROOT}/.cursor/skills/validation/validation-format.md" || { echo "fail: validation next-steps"; FAIL=1; }
grep -q 'validation' "${ROOT}/.cursor/agents/sheep-review.md" || { echo "fail: sheep-review loads validation"; FAIL=1; }
! test -f "${ROOT}/.cursor/agents/out-of-scope.md" || { echo "fail: out-of-scope agent should be removed"; FAIL=1; }
! test -d "${ROOT}/.cursor/skills/readiness-from-review" || { echo "fail: readiness-from-review dir should be removed"; FAIL=1; }
grep -q 'review_validation' "${ROOT}/.cursor/skills/nicki/routing.yaml" || { echo "fail: review_validation artifact"; FAIL=1; }
! grep -q 'out_of_scope:' "${ROOT}/.cursor/skills/nicki/routing.yaml" || { echo "fail: out_of_scope step should be removed"; FAIL=1; }

FIXTURE=$(mktemp)
cat >"$FIXTURE" <<'EOF'
# Subtasks
- [x] Done line stays.
EOF
BEFORE_X=$(grep -c '\- \[x\]' "$FIXTURE" || true)
cat >>"$FIXTURE" <<'EOF'

## Fix
<!-- ref: current-task/review-validations/r1-validation.yaml -->
- [ ] Fix lint from review.
EOF
AFTER_X=$(grep -c '\- \[x\]' "$FIXTURE" || true)
if [[ "$BEFORE_X" != "$AFTER_X" ]] || [[ "$BEFORE_X" -lt 1 ]]; then
  echo "fail: fix append mutated prior [x] ($BEFORE_X -> $AFTER_X)"
  FAIL=1
else
  echo "ok: fix append keeps prior [x]"
fi
rm -f "$FIXTURE"

if [[ -f "${FIXTURE_DIR}/scope-only-validation.yaml" ]]; then
  grep -q 'ready_for_acceptance' "${FIXTURE_DIR}/scope-only-validation.yaml" || { echo "fail: scope-only fixture"; FAIL=1; }
  grep -q 'deferred_scope: true' "${FIXTURE_DIR}/scope-only-validation.yaml" || { echo "fail: scope-only deferred"; FAIL=1; }
  echo "ok: scope-only fixture present"
fi

if [[ -f "${FIXTURE_DIR}/verify-fail-validation.yaml" ]]; then
  grep -q 'fix_required' "${FIXTURE_DIR}/verify-fail-validation.yaml" || { echo "fail: verify fixture"; FAIL=1; }
  echo "ok: verify-fail fixture present"
fi

if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "smoke-readiness-mapping: ok"
