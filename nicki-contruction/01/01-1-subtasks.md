---
worktree: git-tail-workspace
generated_by: subtask-maker
spec: 01-1-spec.yaml
title: Git tail, workspace layout, and docs
constraints:
  - no-new-deps
  - global-registry-start-close-only
  - nicki-read-only-orchestrator
  - leaf-agents-atomic
  - publish-after-merge-before-close
  - caveman-md-default-full
  - baseline-slice-00-done
---

# Subtasks

- [x] Add publish-task leaf agent, skill, command — slot after merge, before close; user confirm push.
- [x] publish-task push target branch per policy; write publish handoff in task worktree; set status publish pointer.
- [x] Align merge-task finish: merge handoff in task worktree + status merge pointer on complete.
- [x] Per-task status carry merge + publish artifact pointers; YAML/MD handoff bodies stay unchanged.
- [x] close-task gate: merge + publish handoffs exist or explicit archive override recorded.
- [x] Close sequence: archive summary + caveman report first, worktree delete, registry unregister last.
- [x] start-task register project-local worktree_path + status_path; no single host-repo hardcode.
- [x] Layout standard: projects per name, worktrees per slug under each project.
- [x] Handoff meta docs: workspace, project, task worktree, target branch roots clearly scoped.
- [x] README, NICKI, PLAN refresh: project-local examples, cursor layout match, Nicki = subagent not slash unless command file.
- [x] Docs note future custom mode possible; don't imply it works today.
- [x] spec-maker + agents OK without CONTRIBUTING; record inline assumptions when conventions needed.
- [x] Nicki tail route from status pointers: merge → publish → close; disk beats chat.
- [x] Caveman full on all new/changed MD handoffs this slice; schema keys stay normal.
- [x] Smoke: merge + publish handoffs + pointers set; close blocks or override without tail evidence.
- [x] Verify start paths + doc examples use project-local layout; new MD handoffs caveman full.
