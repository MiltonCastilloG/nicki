#!/usr/bin/env bash
set -euo pipefail

HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/enforce-agent-tools.sh"
INJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/inject-nicki-bootstrap.sh"

result="$(printf '%s' '{"tool_name":"Shell","agent_type":"nicki"}' | "$HOOK")"
jq -e '.permission == "deny"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Read","agent_type":"nicki"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Glob","agent_type":"nicki"}' | "$HOOK")"
jq -e '.permission == "deny"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Grep","agent_type":"nicki"}' | "$HOOK")"
jq -e '.permission == "deny"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Shell"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

# Hint must not resolve agent — parent work mentioning "nicki" must not block tools.
result="$(printf '%s' '{"tool_name":"Write","description":"Update nicki.md and routing.yaml"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Grep","description":"find references to nicki in README"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Write","subagent_type":"sheep-spec"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

result="$(printf '%s' '{"tool_name":"Write","subagent_type":"sheep-describe"}' | "$HOOK")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null

# sessionStart injects bootstrap context
result="$(printf '%s' '{"hook_event_name":"sessionStart","cwd":"'"$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"'"}' | bash "$INJECT")"
jq -e '.additional_context | length > 0' <<<"$result" >/dev/null
jq -e '.additional_context | contains("Nicki workspace bootstrap")' <<<"$result" >/dev/null

# preToolUse Task→nicki prepends bootstrap to prompt
result="$(printf '%s' '{"hook_event_name":"preToolUse","tool_name":"Task","cwd":"'"$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"'","tool_input":{"subagent_type":"nicki","prompt":"user message"}}' | bash "$INJECT")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null
jq -e '.updated_input.prompt | contains("Nicki workspace bootstrap")' <<<"$result" >/dev/null
jq -e '.updated_input.prompt | contains("user message")' <<<"$result" >/dev/null

# preToolUse Task→other agent passes through
result="$(printf '%s' '{"hook_event_name":"preToolUse","tool_name":"Task","tool_input":{"subagent_type":"explore","prompt":"find files"}}' | bash "$INJECT")"
jq -e '.permission == "allow"' <<<"$result" >/dev/null
jq -e 'has("updated_input") | not' <<<"$result" >/dev/null

echo "smoke-agent-tools: ok"
