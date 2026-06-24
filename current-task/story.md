# P1-5 — Wire sheep-start to create-worktree.py

## Feature: sheep-start uses create-worktree.py

As a Nicki operator
I want sheep-start to invoke create-worktree.py from the workspace root
So that new task worktrees follow the unified layout and Nicki handoff is mechanical

### Background

```gherkin
Given the Nicki workspace root is the only valid cwd for worktree creation
And actors are the user, Nicki, and sheep-start
And sheep-start follows start-task/SKILL.md for classification and one create-worktree.py run per work item
And worktrees live at worktrees/<project>-<slug> with a single hyphen
And create-worktree.py pulls main, scaffolds current-task/, copies registry locals, runs post_create, and registers global-status.json
And registration uses register-global-status.py (invoked by create-worktree.py on success)
And start-worktrees.sh is not referenced on the sheep-start agent path
And constraints are no-commit and no-new-deps
And deleting start-worktrees.sh from the repo, changing create-worktree.py behavior, permissions.json, and check-gate are out of scope
```

### Scenario: sheep-start creates a nicki self-task worktree

```gherkin
Given sheep-start has classified a work item with project "nicki" and slug "wire-sheep-start"
When sheep-start runs create-worktree.py from the workspace root with --project, --slug, --type, and --original as needed
Then a new git worktree exists at worktrees/nicki-wire-sheep-start
And current-task/status.json is scaffolded in that worktree
And global-status.json gains a per-project task entry with worktree_path and status_path
And sheep-start does not invoke start-worktrees.sh
And sheep-start reports structured handoff fields from create-worktree.py JSON stdout for sheep-status
```

### Scenario: sheep-start creates a managed-project worktree

```gherkin
Given nicki-workspace.yaml lists a managed project (e.g. tetris-clone-frp)
And sheep-start has a work item with that project and a kebab-case slug
When sheep-start runs create-worktree.py once for that item
Then the worktree is created at worktrees/<project>-<slug>
And global-status.json is updated for that project
And sheep-start does not invoke start-worktrees.sh
```

### Scenario: start-worktrees.sh retired from agent path

```gherkin
Given sheep-start.md and related agent instructions describe the start flow
When an operator or reviewer inspects the sheep-start agent path
Then instructions direct create-worktree.py per start-task/SKILL.md
And start-worktrees.sh is not listed as the worktree creation command
And register-global-status flow is preserved (via create-worktree.py registration, not a parallel legacy shell path)
```

### Scenario: existing worktree is not silently overwritten

```gherkin
Given a worktree already exists at worktrees/<project>-<slug>
When sheep-start runs create-worktree.py for that project and slug
Then the script fails without overwriting the existing worktree
And sheep-start surfaces the error and WORKFLOW.md recovery guidance
```
