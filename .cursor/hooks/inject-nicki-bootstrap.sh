#!/usr/bin/env bash
# sessionStart + preToolUse(Task→nicki): inject workspace bootstrap for cold start.
set -euo pipefail

allow_only() { printf '%s\n' '{"permission":"allow"}'; }

build_bootstrap() {
  local root="$1"
  local errors=()
  local yaml=""
  local yaml_name=""

  if [[ -f "$root/nicki-workspace.yaml" ]]; then
    yaml="$root/nicki-workspace.yaml"
    yaml_name="nicki-workspace.yaml"
  elif [[ -f "$root/nicki-workspace.example.yaml" ]]; then
    yaml="$root/nicki-workspace.example.yaml"
    yaml_name="nicki-workspace.example.yaml"
  else
    errors+=("No nicki-workspace.yaml or nicki-workspace.example.yaml at workspace root.")
  fi

  {
    printf '%s\n' "## Nicki workspace bootstrap (hook-injected; do not re-discover)"
    printf '%s\n' ""
    printf 'workspace_root: %s\n' "$root"

    if [[ -n "$yaml" ]]; then
      printf 'registry: %s\n' "$yaml_name"
      printf '%s\n' ""
      printf '%s\n' "projects:"
      while IFS=$'\t' read -r name path; do
        [[ -n "$name" ]] || continue
        local backlog=""
        if [[ "$name" == "nicki" || "$path" == "." ]]; then
          backlog="docs/tasks.md"
        else
          backlog="${path}/docs/TASKS.md"
          backlog="${backlog#./}"
        fi
        printf '  - name: %s\n' "$name"
        printf '    path: %s\n' "$path"
        printf '    backlog: %s\n' "$backlog"
        if [[ -f "$root/$backlog" ]]; then
          printf '    backlog_tasks:\n'
          extract_backlog_tasks "$root/$backlog" | sed 's/^/      /'
        else
          printf '    backlog_tasks: (file missing)\n'
        fi
      done < <(parse_workspace_projects "$yaml")
    fi

    printf '%s\n' ""
    if [[ -f "$root/global-status.json" ]] && command -v jq >/dev/null 2>&1; then
      printf '%s\n' "active_tasks:"
      local active
      active="$(jq -r '.active_task // empty' "$root/global-status.json")"
      [[ -n "$active" ]] && printf '  active_task: %s\n' "$active"
      jq -r '.tasks // {} | to_entries[] | "  - id: \(.key)\n    project: \(.value.project)\n    slug: \(.value.slug)\n    worktree_path: \(.value.worktree_path)\n    status_path: \(.value.status_path)"' \
        "$root/global-status.json" 2>/dev/null || true
    else
      printf '%s\n' "active_tasks: (global-status.json missing or jq unavailable)"
    fi

    if ((${#errors[@]} > 0)); then
      printf '%s\n' ""
      printf '%s\n' "bootstrap_errors:"
      for e in "${errors[@]}"; do
        printf '  - %s\n' "$e"
      done
    fi
  }
}

parse_workspace_projects() {
  local yaml_file="$1"
  awk '
    /^  [a-zA-Z0-9_.-]+:$/ {
      if (project != "") print project "\t" (path == "" ? "." : path)
      project = $1
      sub(/:$/, "", project)
      path = ""
      next
    }
    /^    path:[[:space:]]*/ {
      path = $0
      sub(/^    path:[[:space:]]*/, "", path)
      next
    }
    END {
      if (project != "") print project "\t" (path == "" ? "." : path)
    }
  ' "$yaml_file"
}

extract_backlog_tasks() {
  local file="$1"
  awk '
    /^## P[0-9]/ { phase = $0; next }
    /^\| [0-9]/ {
      task = ""
      slug = ""
      if (match($0, /\| [0-9]+(\.[0-9]+)? \|/)) {
        task = substr($0, RSTART + 2, RLENGTH - 4)
        gsub(/^ +| +$/, "", task)
      }
      if (match($0, /`[^`]+`/)) {
        slug = substr($0, RSTART + 1, RLENGTH - 2)
      }
      if (task != "" && slug != "") {
        printf "      - phase: %s | %s | slug: %s\n", phase, task, slug
      }
      next
    }
    /^## / && phase != "" { phase = "" }
  ' "$file" | head -n 40
}

resolve_workspace_root() {
  local input="$1"
  local root
  root="$(printf '%s' "$input" | jq -r '.cwd // .workspace_roots[0] // empty')"
  if [[ -z "$root" || ! -d "$root" ]]; then
    root="$(pwd)"
  fi
  if [[ -f "$root/nicki-workspace.yaml" || -f "$root/nicki-workspace.example.yaml" ]]; then
    printf '%s' "$root"
    return 0
  fi
  if [[ -f "$root/../nicki-workspace.yaml" || -f "$root/../nicki-workspace.example.yaml" ]]; then
    printf '%s' "$(cd "$root/.." && pwd)"
    return 0
  fi
  printf '%s' "$root"
}

normalize_agent() {
  local raw="${1:-}"
  raw="${raw//_/-}"
  printf '%s' "$raw" | tr '[:upper:]' '[:lower:]'
}

input="$(cat)"

if ! command -v jq >/dev/null 2>&1; then
  event="$(printf '%s' "$input" | jq -r '.hook_event_name // empty' 2>/dev/null || true)"
  if [[ "$event" == "sessionStart" ]]; then
    printf '%s\n' '{"additional_context":"bootstrap_error: jq required"}'
  else
    allow_only
  fi
  exit 0
fi

event="$(printf '%s' "$input" | jq -r '.hook_event_name // empty')"

if [[ "$event" == "sessionStart" ]]; then
  root="$(resolve_workspace_root "$input")"
  bootstrap="$(build_bootstrap "$root")"
  jq -n --arg ctx "$bootstrap" '{additional_context: $ctx}'
  exit 0
fi

tool_name="$(printf '%s' "$input" | jq -r '.tool_name // empty')"
if [[ "$tool_name" != "Task" ]]; then
  allow_only
  exit 0
fi

subagent="$(normalize_agent "$(printf '%s' "$input" | jq -r '.tool_input.subagent_type // .subagent_type // empty')")"
if [[ "$subagent" != "nicki" ]]; then
  allow_only
  exit 0
fi

root="$(resolve_workspace_root "$input")"
bootstrap="$(build_bootstrap "$root")"
tool_input="$(printf '%s' "$input" | jq -c '.tool_input // {}')"
original_prompt="$(printf '%s' "$tool_input" | jq -r '.prompt // ""')"
merged_prompt="${bootstrap}"

if [[ -n "$original_prompt" ]]; then
  merged_prompt="${bootstrap}

---

${original_prompt}"
fi

printf '%s' "$tool_input" | jq -c \
  --arg prompt "$merged_prompt" \
  '{permission: "allow", updated_input: (. + {prompt: $prompt})}'
exit 0
