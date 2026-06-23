# code-workspace-sync — nicki.code-workspace stays in sync with worktrees

## Feature: Multi-root workspace reflects active worktrees

As a Nicki operator
I want nicki.code-workspace regenerated when worktrees are added or removed
So that Cursor lists Shared plus every active task worktree without manual edits

### Background

```gherkin
Given the Nicki workspace root holds nicki.code-workspace and worktrees/
And scripts/generate-code-workspace.sh regenerates Shared plus one folder per git worktree under worktrees/
And actors are the user, Nicki, sheep-start (create-worktree.py), and sheep-close (close-scope)
And wiring runs after successful create-worktree.py on start and after worktree delete on close
And regen failure emits a warning and does not fail create or close
And regen is skipped when create-worktree.py runs with --dry-run
And constraints are no-commit and no-new-deps
And changing worktree naming layout, check-gate enforcement, and rewriting generate script output rules are out of scope
```

### Scenario: Start adds new worktree folder

```gherkin
Given create-worktree.py completes successfully without --dry-run
And a new git worktree exists at worktrees/<project>-<slug>
When the start flow finishes
Then scripts/generate-code-workspace.sh runs
And nicki.code-workspace includes a folder entry for that worktree
And the Shared folder entry at workspace root remains
```

### Scenario: Close removes deleted worktree folder

```gherkin
Given close-scope teardown has removed the worktree directory worktrees/<project>-<slug>
When the close flow finishes
Then scripts/generate-code-workspace.sh runs
And nicki.code-workspace no longer lists that worktree folder
And folder entries for remaining git worktrees are still present
```

### Scenario: Regen failure warns without failing create or close

```gherkin
Given create-worktree.py or close-scope completed its primary work successfully
When scripts/generate-code-workspace.sh fails
Then the operator receives a warning about workspace regeneration
And the start handoff still reports success when worktree creation succeeded
And close teardown is not rolled back because regeneration failed
```

### Scenario: Dry-run skips workspace regeneration

```gherkin
Given create-worktree.py is invoked with --dry-run
When validation completes without creating a worktree
Then scripts/generate-code-workspace.sh does not run
And nicki.code-workspace is unchanged
```
