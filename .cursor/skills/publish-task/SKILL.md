---
name: publish-task
description: "Push a target branch to remote after user confirmation; write publish handoff YAML in task worktree."
disable-model-invocation: true
metadata:
  type: subagent
  subagent: publish-task
---

# Publish Task

Push a **target branch** to remote after user confirmation. Task branch was already pushed separately.

Schema: [publish-format.md](publish-format.md).

## Inputs

| Input | Required | Notes |
|-------|----------|-------|
| Task worktree path | Yes | Handoff write location |
| Merge handoff | Yes | Confirms merge completed; supplies target branch |
| Target repo root | Yes | Git root containing target branch — agent resolves |
| Target branch | No | Default from merge handoff |
| Handoff output path | No | Default `current-task/publishes/<slug>.yaml` in task worktree |

## Procedure

```
- [ ] Resolve task worktree scope
- [ ] Load merge handoff
- [ ] Resolve target repo root + branch
- [ ] Inspect target branch state
- [ ] User confirm push
- [ ] Push target branch
- [ ] Write publish handoff in task worktree
- [ ] Report
```

### Scope

- **Task worktree** = handoff write location
- **Target repo** = git root for push commands
- Never modify app source except via git push side effects on target repo

### Load merge handoff

Stop and ask when:

- No merge handoff or `status: blocked`
- Merge handoff missing `merge.target_branch`
- Target repo ambiguous

### Push

1. Ask user: push `<target_branch>` to remote per project policy?
2. On yes: `git push origin <target_branch>` from target repo checkout (no force)
3. On no: write `status: blocked` handoff; report

### Handoff write

Always under task worktree: `current-task/publishes/<slug>.yaml`.

## Safety

- No force push
- No push without user confirm
- No push of task branch here
- When in doubt, ask
