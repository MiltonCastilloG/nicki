#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
HOOK="$ROOT/.cursor/hooks/enforce-agent-tools.sh"

result="$(printf '%s' '{"tool_name":"Shell","agent_type":"nicki"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Read","agent_type":"nicki"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Shell"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Write","description":"Update nicki.md and routing.yaml"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Grep","description":"find references to nicki in README"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Write","subagent_type":"sheep-spec"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

echo "smoke-agent-tools: ok"
