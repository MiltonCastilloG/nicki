# 01-1 — Git tail, workspace layout, and docs

From `report.md`. Parallel with `01-0-stories.md`. Baseline: slice 00 JSON status done.

---

## Feature: Merge, publish, and close handoffs

As a workflow operator  
I want merge and publish handoffs in the task worktree before close  
So that git tail steps are explicit and close finds evidence on disk

```gherkin
Given the task worktree is under projects/<project>/worktrees/<slug>
And publish-task is a leaf step after merge-task and before close-task
```

### Scenario: Merge and publish write task-worktree artifacts

```gherkin
When merge-task completes for slug "hero-section"
Then merge-task writes current-task/merges/<slug>.yaml in the task worktree
And status.json points to that merge artifact
When publish-task runs with user confirmation after a clean merge
Then the target branch is pushed per project policy
And publish-task writes current-task/publishes/<slug>.yaml in the task worktree
And status.json records the publish artifact pointer
```

### Scenario: Close validates tail handoffs or override

```gherkin
Given the task reached close-task
When close-task validates prerequisites
Then merge and publish handoffs exist under current-task/
Or close-task records explicit user override in the archive
When close-task succeeds
Then task-archive/<slug>/summary.yaml and task-archive/<slug>/report.md exist
And the whole task worktree deletes only after archive is confirmed
And the task id is removed from global-status.json
When close-task is invoked without merge or publish handoffs
Then close-task blocks or requires override recorded in summary.yaml or report.md
```

---

## Feature: Standalone workspace paths

As a Nicki workspace operator  
I want project-local worktrees  
So that one workspace hosts multiple projects without host-repo hardcoding

```gherkin
Given the layout is projects/<project>/worktrees/<slug>
And global-status.json registers project, worktree_path, and status_path
```

### Scenario: Start and docs use project-local paths

```gherkin
When start-task creates slug "hero-section" for project "castlemill-landing"
Then worktree_path is "projects/castlemill-landing/worktrees/hero-section"
And status_path points to that worktree's current-task/status.json
And start scripts do not hardcode a single host repository name
When an operator reads README, NICKI.md, PLAN.md, or start-task skill
Then examples use projects/<project>/worktrees/<slug>
And handoff meta scopes distinguish workspace, project, task worktree, and target branch roots
```

---

## Feature: Operator docs and optional conventions

As a Nicki operator  
I want accurate invocation docs and optional CONTRIBUTING  
So that onboarding is not blocked by missing files or stale layout

```gherkin
Given Nicki is a subagent in .cursor/agents/nicki.md
And CONTRIBUTING.md may be absent
```

### Scenario: Docs and spec-maker without CONTRIBUTING

```gherkin
When an operator reads README or NICKI.md for how to start orchestration
Then docs say Nicki is a subagent not /nicki unless a command file exists
And docs note future custom mode without implying it works today
When an operator reads PLAN.md or README file maps
Then layout matches .cursor/ at workspace root
And stale runtime/package split references are qualified or updated
When spec-maker runs without CONTRIBUTING.md
Then spec-maker does not fail solely for missing CONTRIBUTING.md
And the spec records assumptions inline when needed
```
