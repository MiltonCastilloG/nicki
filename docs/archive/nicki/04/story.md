# P1 create-worktree.py — worktree creation, layout, and registration

## Feature: Scripted worktree creation at workspace root

As a Nicki operator  
I want sheep-start to run a single Python script from the workspace root  
So that new task worktrees are created mechanically and Nicki only does creative work (Gherkin) by hand

### Background

```gherkin
Given the Nicki workspace root is the only valid cwd for worktree creation
And actors are limited to the user, Nicki, and sheep-start
And sheep-start invokes create-worktree.py as a subprocess (one slug per run, not batch)
And managed projects are discovered from nicki-workspace.yaml and the projects/ directory shape
And base branch is always main
And slug is kebab-case
And branch name defaults from task type when not supplied (e.g. chore/<slug>, feature/<slug>)
And all worktrees use workspace-root worktrees/<project>-<slug> with a single hyphen separator (gitignored, outside tracked repo content)
And for nicki self-tasks project is "nicki" (e.g. worktrees/nicki-create-worktree-py)
And for managed projects project is the registry project name (e.g. worktrees/tetris-clone-frp-hero-section)
And task ids are incremental per project starting at "00"
And global-status.json registration may be a separate script (not required inside create-worktree.py)
And P1-4 (migrate existing tetris worktree) and P1-5 (wire sheep-start) are out of scope for this story
And P1-2 (root worktrees/ layout) and P1-3 (post_create copy list / registry) are in scope
And no git commits until user approval
```

### Scenario: sheep-start creates a nicki self-task worktree

```gherkin
Given sheep-start has classified a single work item with slug "create-worktree-py"
And project is "nicki"
When sheep-start runs create-worktree.py from the workspace root
Then main is updated via pull
And a new git worktree exists at worktrees/nicki-create-worktree-py
And the worktree is on a new branch defaulting to chore/create-worktree-py unless overridden
And gitignored locals needed to work (.env, .env.*, node_modules, and other paths from nicki-workspace.yaml gitignore/copy list) are copied into worktrees/nicki-create-worktree-py
And current-task/ exists with what Nicki needs to continue the pipeline
And post_create commands from nicki-workspace.yaml for project "nicki" run after copy
And a companion registration step updates global-status.json with the next per-project task id
And the registry entry includes project, slug, worktree_path, and status_path
And active_task points to the new task id
And sheep-start reports created paths and branch to the user
And start-worktrees.sh is replaced by this flow (no backward-compat requirement)
```

### Scenario: sheep-start creates a managed-project worktree

```gherkin
Given nicki-workspace.yaml lists project "tetris-clone-frp" with path projects/tetris-clone-frp
And sheep-start has a work item with slug "hero-section" for that project
When sheep-start runs create-worktree.py from the workspace root
Then the worktree is created at worktrees/tetris-clone-frp-hero-section
And gitignored locals are copied from the project source into the new worktree
And post_create commands from nicki-workspace.yaml for "tetris-clone-frp" run in the worktree
And global-status.json gains a per-project incremental task id for tetris-clone-frp
And status_path resolves to worktrees/tetris-clone-frp-hero-section/current-task/status.json
```

### Scenario: Project discovery at Nicki startup

```gherkin
Given the workspace contains projects/ with managed clones
And nicki-workspace.yaml defines project entries
When Nicki or hooks resolve project context at startup
Then available projects are discoverable without hardcoding repo names
And create-worktree.py reads post_create and copy lists from nicki-workspace.yaml (P1-3)
And hooks documentation reflects the workspace-root worktrees/<project>-<slug> layout (P1-2)
```

### Scenario: Missing env file is non-fatal

```gherkin
Given create-worktree.py is creating worktree worktrees/nicki-foo
And source .env does not exist
When the copy step runs
Then the script skips the missing file without failing
And the worktree creation continues
And the user is informed
```

### Scenario: Recoverable failure manual recovery

```gherkin
Given create-worktree.py encounters uncommitted changes on main
Or the worktree path already exists
Or git pull fails
Or post_create fails
Or global-status registration fails
When the script cannot complete automatically
Then the worktree is left as-is when already created
And the agent reads the script's documented workflow and attempts to complete remaining steps manually
And no silent overwrite of existing worktrees or branches occurs
```

### Scenario: Acceptance via dogfood worktrees

```gherkin
Given create-worktree.py and registration are implemented
When review creates test worktrees for tetris-clone-frp and castlemill-landing
Then worktree paths follow worktrees/<project>-<slug> (e.g. worktrees/tetris-clone-frp-<slug>, worktrees/castlemill-landing-<slug>)
And branches, copied gitignored files, post_create, global-status entries, and current-task layout are verified correct
And the user explicitly approves before any commit
```

## Out of scope

- P1-4: migrate or recreate the existing tetris-clone-frp worktree at projects/tetris-clone-frp/worktrees/*
- P1-5: final sheep-start wiring (may follow immediately after; not part of this story's deliverable)
- check-gate.py, permissions.json, smoke fixtures (P2)
- bin/nicki CLI
