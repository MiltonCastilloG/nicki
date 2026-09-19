#!/usr/bin/env bash
# Remove task worktree, prune git registration, delete local feature branch.
# Only sheep-close should call this (via close-scope §3).
# Usage: teardown-worktree.sh <workspace_root> <worktree_path>
set -euo pipefail

ROOT="${1:?workspace root}"
WT_INPUT="${2:?worktree path}"

resolve_abs() {
  local p="$1"
  if [[ "$p" = /* ]]; then
    printf '%s' "$p"
  else
    (cd "$ROOT" && cd "$p" && pwd)
  fi
}

WT_ABS="$(resolve_abs "$WT_INPUT")"

GIT_ROOT=""
if git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  GIT_ROOT="$(git -C "$ROOT" rev-parse --show-toplevel)"
fi

BRANCH=""
if [[ -n "$GIT_ROOT" ]]; then
  BRANCH="$(
    git -C "$GIT_ROOT" worktree list --porcelain | awk -v wt="$WT_ABS" '
      $1 == "worktree" { path = $2; branch = "" }
      $1 == "branch" && path == wt { sub("refs/heads/", "", $2); print $2; exit }
    '
  )"
fi

if [[ -d "$WT_ABS" ]]; then
  rm -rf -- "$WT_ABS"
  echo "removed: $WT_ABS"
else
  echo "skip: worktree path missing ($WT_ABS)"
fi

if [[ -z "$GIT_ROOT" ]]; then
  echo "warn: no git root; skipped prune and branch delete" >&2
  exit 0
fi

git -C "$GIT_ROOT" worktree prune
echo "pruned: worktree registrations"

if [[ -n "$BRANCH" ]]; then
  if git -C "$GIT_ROOT" worktree list --porcelain | grep -q "branch refs/heads/${BRANCH}"; then
    echo "skip branch delete: ${BRANCH} still checked out in another worktree"
  elif git -C "$GIT_ROOT" show-ref --verify --quiet "refs/heads/${BRANCH}"; then
    git -C "$GIT_ROOT" branch -D "$BRANCH"
    echo "deleted branch: ${BRANCH}"
  else
    echo "skip branch delete: ${BRANCH} not found locally"
  fi
fi
