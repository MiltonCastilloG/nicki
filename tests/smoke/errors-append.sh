#!/usr/bin/env bash
# Verify errors.v1 append and archive copy semantics
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
APPEND="$ROOT/.cursor/skills/errors-recording/scripts/append-error.py"
FIXTURE="$ROOT/tests/fixtures/smoke-worktree"
ERRORS="$FIXTURE/current-task/specs/errors.yaml"
ARCHIVE_DIR="$FIXTURE/docs/archive/sheep-fallback"

rm -rf "$FIXTURE"
mkdir -p "$FIXTURE/current-task/specs"

python3 "$APPEND" \
  --worktree "$FIXTURE" \
  --script-route ".cursor/skills/nicki/scripts/check-gate.py" \
  --input '{"argv":["--worktree","worktrees/nicki-sheep-fallback","--step","execute"]}' \
  --expected-output '{"required_fields":["allowed","sheep","reason"]}' \
  --exit-code 1 \
  --stdout '{"allowed":false}' \
  --validation-errors '["missing field: reason"]'

test -f "$ERRORS"
COUNT1=$(python3 -c "import yaml; print(len(yaml.safe_load(open('$ERRORS'))['failures']))")
test "$COUNT1" -eq 1

python3 -c "
import yaml
d = yaml.safe_load(open('$ERRORS'))
assert d['meta']['schema'] == 'errors.v1'
f = d['failures'][0]
req = ['id','recorded_at','script_route','input','expected_output','actual']
assert all(k in f for k in req)
a = f['actual']
assert 'exit_code' in a and 'stdout' in a and 'stderr' in a and 'validation_errors' in a
print('ok')
"

python3 "$APPEND" \
  --worktree "$FIXTURE" \
  --script-route ".cursor/skills/current-task-update/scripts/update-status.py" \
  --input '{"argv":["--worktree","worktrees/foo"]}' \
  --expected-output '{"required_fields":["written"]}' \
  --exit-code 1 \
  --stdout 'not json' \
  --validation-errors '["stdout is not valid JSON"]'

COUNT2=$(python3 -c "import yaml; print(len(yaml.safe_load(open('$ERRORS'))['failures']))")
test "$COUNT2" -eq 2

IDS=$(python3 -c "import yaml; print(len({f['id'] for f in yaml.safe_load(open('$ERRORS'))['failures']}))")
test "$IDS" -eq 2

python3 -c "
contract = {
  'worktree': 'sheep-fallback',
  'completed_step': 'execute',
  'completed_status': 'blocked',
  'artifact': 'current-task/specs/errors.yaml',
  'next_step': 'execute',
  'open_questions': [],
  'summary': 'Recorded harness failure.',
}
req = ['worktree','completed_step','completed_status','artifact','next_step','open_questions','summary']
assert all(k in contract for k in req)
"

rm -rf "$ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR"
cp "$ERRORS" "$ARCHIVE_DIR/errors.yaml"
ARCHIVED=$(python3 -c "import yaml; print(len(yaml.safe_load(open('$ARCHIVE_DIR/errors.yaml'))['failures']))")
test "$ARCHIVED" -eq 2

NO_ERR_FIXTURE="$ROOT/tests/fixtures/no-errors-worktree"
rm -rf "$NO_ERR_FIXTURE"
mkdir -p "$NO_ERR_FIXTURE/current-task/specs"
test ! -f "$NO_ERR_FIXTURE/current-task/specs/errors.yaml"

echo "smoke-errors-append: ok"
