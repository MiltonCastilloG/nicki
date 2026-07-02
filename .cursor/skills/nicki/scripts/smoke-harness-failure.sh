#!/usr/bin/env bash
# smoke-harness-failure.sh — E2E: real check-gate contract failure → sheep-fallback record
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$ROOT"

GATE=".cursor/skills/nicki/scripts/check-gate.py"
VALIDATE=".cursor/skills/nicki/scripts/validate-harness-stdout.py"
APPEND=".cursor/skills/errors-recording/scripts/append-error.py"
WORKTREE="."
STEP="acceptance"
SCRIPT_ROUTE=".cursor/skills/nicki/scripts/check-gate.py"
ERRORS_YAML="$ROOT/current-task/specs/errors.yaml"

# 1. Run check-gate with smoke contract failure (real gate script, invalid stdout)
set +e
GATE_OUT=$(python3 "$GATE" --smoke-contract-fail --worktree "$WORKTREE" --step "$STEP" 2>&1)
GATE_EXIT=$?
set -e

test "$GATE_EXIT" -eq 1 || { echo "fail: expected check-gate exit 1"; exit 1; }
test -n "$GATE_OUT" || { echo "fail: empty stdout"; exit 1; }

# 2. Validate contract — must fail (missing sheep, reason)
set +e
VAL_OUT=$(python3 "$VALIDATE" --script check-gate.py --stdout "$GATE_OUT" --exit-code "$GATE_EXIT" 2>&1)
VAL_EXIT=$?
set -e
test "$VAL_EXIT" -eq 1 || { echo "fail: validator should reject contract"; exit 1; }

VAL_JSON=$(echo "$VAL_OUT" | tail -1)
echo "$VAL_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['valid'] is False and d['errors']; print('contract-invalid:', d['errors'])"

# 3. Normal gate deny must NOT be harness failure (valid contract, allowed false)
set +e
DENY_OUT=$(python3 "$GATE" --worktree /nonexistent-wt --step "$STEP" 2>&1)
DENY_EXIT=$?
set -e
test "$DENY_EXIT" -eq 1
DENY_VAL=$(python3 "$VALIDATE" --script check-gate.py --stdout "$DENY_OUT" --exit-code "$DENY_EXIT")
echo "$DENY_VAL" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['valid'] is True; print('gate-deny-valid-contract: ok')"

# 4. sheep-fallback path — append failure record (what sheep-fallback runs)
INPUT_JSON=$(python3 -c "import json; print(json.dumps({'argv':['--worktree','worktrees/nicki-sheep-fallback','--step','$STEP','--smoke-contract-fail']}))")
EXPECTED_JSON='{"required_fields":["allowed","sheep","reason"]}'
VALIDATION_JSON=$(echo "$VAL_JSON" | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)['errors']))")

python3 "$APPEND" \
  --worktree "$ROOT" \
  --script-route "$SCRIPT_ROUTE" \
  --input "$INPUT_JSON" \
  --expected-output "$EXPECTED_JSON" \
  --exit-code "$GATE_EXIT" \
  --stdout "$GATE_OUT" \
  --validation-errors "$VALIDATION_JSON"

test -f "$ERRORS_YAML"

python3 -c "
import yaml
from pathlib import Path
p = Path('$ERRORS_YAML')
d = yaml.safe_load(p.read_text())
assert d['meta']['schema'] == 'errors.v1'
assert len(d['failures']) >= 1
last = d['failures'][-1]
assert last['script_route'] == '$SCRIPT_ROUTE'
assert last['actual']['exit_code'] == 1
assert 'missing field' in ' '.join(last['actual']['validation_errors'] or [])
print('errors.yaml harness entry: ok')
"

echo "smoke-harness-failure: ok"
