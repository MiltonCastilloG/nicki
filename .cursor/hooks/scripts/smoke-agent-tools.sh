#!/usr/bin/env bash
set -euo pipefail

HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/enforce-agent-tools.sh"

result="$(printf '%s' '{"tool_name":"Shell","agent_type":"nicki"}' | "$HOOK")"
jq -e '.permission == "deny"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Read","agent_type":"nicki"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Shell"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

echo "smoke-agent-tools: ok"
