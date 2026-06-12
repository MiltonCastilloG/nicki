#!/usr/bin/env bash
set -euo pipefail

# Create git worktrees from updated main.
# Usage: start-worktrees.sh "branch:slug" ["branch:slug" ...]
# Example: start-worktrees.sh "feature/hero-section:hero-section" "fix/footer-bug:footer-bug"

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 \"branch:slug\" [\"branch:slug\" ...]" >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Warning: working tree has uncommitted changes; continuing anyway." >&2
fi

before_sha="$(git rev-parse main 2>/dev/null || true)"

git checkout main
git pull origin main

after_sha="$(git rev-parse main)"
if [[ -n "$before_sha" && "$before_sha" != "$after_sha" ]]; then
  echo "Pulled main ($before_sha -> $after_sha)"
else
  echo "main is up to date ($after_sha)"
fi

# PROJECT env → projects/<project>/worktrees/<slug>; else legacy worktrees/<slug>
if [[ -n "${PROJECT:-}" ]]; then
  worktree_base="projects/${PROJECT}/worktrees"
else
  worktree_base="worktrees"
fi
mkdir -p "$worktree_base"

created=()
skipped=()

for pair in "$@"; do
  if [[ "$pair" != *:* ]]; then
    echo "Error: invalid pair '$pair' (expected branch:slug)" >&2
    exit 1
  fi

  branch="${pair%%:*}"
  slug="${pair#*:}"
  worktree_path="${worktree_base}/${slug}"

  if [[ -z "$branch" || -z "$slug" ]]; then
    echo "Error: invalid pair '$pair' (branch and slug must be non-empty)" >&2
    exit 1
  fi

  if [[ -d "$worktree_path" ]]; then
    echo "Skipped: $worktree_path already exists"
    skipped+=("$worktree_path ($branch)")
    continue
  fi

  if git show-ref --verify --quiet "refs/heads/$branch"; then
    if git worktree list --porcelain | grep -q "^branch refs/heads/$branch$"; then
      echo "Skipped: branch $branch is already checked out in another worktree"
      skipped+=("$worktree_path ($branch)")
      continue
    fi
    git worktree add "$worktree_path" "$branch"
  else
    git worktree add "$worktree_path" -b "$branch" main
  fi

  echo "Created: $worktree_path -> $branch"
  created+=("$worktree_path -> $branch")
done

echo ""
echo "Worktrees:"
git worktree list

if [[ ${#created[@]} -gt 0 ]]; then
  echo ""
  echo "Created:"
  printf '  %s\n' "${created[@]}"
fi

if [[ ${#skipped[@]} -gt 0 ]]; then
  echo ""
  echo "Skipped:"
  printf '  %s\n' "${skipped[@]}"
fi
