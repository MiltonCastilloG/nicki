#!/usr/bin/env bash
# update-status.py write contract: success, input error, optional artifact
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
UPDATE="$ROOT/.cursor/skills/current-task-update/scripts/update-status.py"
VALIDATE="$ROOT/.cursor/skills/nicki/scripts/validate-harness-stdout.py"
FIXTURE=$(mktemp -d)
trap 'rm -rf "$FIXTURE"' EXIT

write_yaml() {
  local path="$1"
  shift
  printf '%s\n' "$@" >"$path"
}

# (a) valid summary
YAML_OK="$FIXTURE/summary-ok.yaml"
write_yaml "$YAML_OK" \
  "completed_step: spec" \
  "next_step: subtasks" \
  "artifact: current-task/specs/foo.yaml" \
  "open_questions: []"

OUT=$(python3 "$UPDATE" --worktree "$FIXTURE" --yaml-path "$YAML_OK")
echo "$OUT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d['written'] is True
assert d['completed_step'] == 'spec'
assert d['next_step'] == 'subtasks'
"
python3 "$VALIDATE" --script update-status.py --stdout "$OUT" --exit-code 0 >/dev/null
test -f "$FIXTURE/current-task/status.json"

# (c) acceptance without artifact
YAML_ACC="$FIXTURE/summary-acc.yaml"
write_yaml "$YAML_ACC" \
  "completed_step: acceptance" \
  "next_step: sync"

OUT=$(python3 "$UPDATE" --worktree "$FIXTURE" --yaml-path "$YAML_ACC")
echo "$OUT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d['written'] is True
"
STATUS_BEFORE=$(cat "$FIXTURE/current-task/status.json")

# (b) missing next_step — must not write
YAML_BAD="$FIXTURE/summary-bad.yaml"
write_yaml "$YAML_BAD" "completed_step: spec"

set +e
OUT=$(python3 "$UPDATE" --worktree "$FIXTURE" --yaml-path "$YAML_BAD" 2>&1)
EXIT=$?
set -e
test "$EXIT" -eq 1
echo "$OUT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d['written'] is False
assert any('next_step' in e for e in d['errors'])
"
test "$(cat "$FIXTURE/current-task/status.json")" = "$STATUS_BEFORE"

echo "smoke-status-update: ok"
