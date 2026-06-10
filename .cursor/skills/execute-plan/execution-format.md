# Execution format

Executions are the handoff from `/execute-plan` to `/review-execution`. **YAML only** — write one compact artifact after executing, partially executing, or blocking on a subtask list.

Store executions in the worktree under `current-task/executions/` (e.g. `current-task/executions/hero-section.yaml`).

All agent artifacts for the active task live under `current-task/`:

```
current-task/
  current-task-context.yaml              # workflow context from /current-task-update
  specs/<slug>.yaml                    # from /spec-maker
  subtasks/<slug>.md                   # from /subtask-maker; executor updates checkboxes
  executions/<slug>.yaml               # from /execute-plan
  reviews/<slug>.yaml                  # from /review-execution
  review-validations/rN-validation.yaml # from /review-triage
  review-inputs/rN-review.yaml         # optional guidance input for /review-execution
  next-steps/*.yaml                    # follow-up specs consumable by /subtask-maker
  merges/<slug>.yaml                   # from /merge-task
  commits/<slug>.yaml                  # from /commit-task
  pushes/<slug>.yaml                   # from /push-task
```

The execution file is a map for review, not an approval. `/review-execution` still reads the diff and reruns verification independently.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Routing, source subtask list, and execution status |
| `paths` | Yes | Touched paths grouped by change type |
| `subtasks` | Yes | One result entry per checklist line, in list order |
| `verify` | If verify ran | Command evidence from execution |
| `deviations` | No | Approved or blocked departures from the subtask list |
| `open_questions` | No | Questions left unresolved at handoff time |
| `hotspots` | No | Reviewer focus areas |
| `review_scope` | No | Hints for full, triage, or focused review |

## `meta`

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug (e.g. `hero-section`) |
| `generated_by` | Yes | Always `execute-plan` |
| `subtasks` | Yes | Subtask list path used (e.g. `current-task/subtasks/hero-section.md`) |
| `spec` | No | Spec path when known |
| `context` | No | Path to task context (e.g. `current-task/current-task-context.yaml`) |
| `status` | Yes | `complete`, `partial`, or `blocked` |
| `constraints` | No | Constraints honored from the subtask list frontmatter |

## `paths`

Use paths relative to the worktree root.

| Field | Required | Description |
|-------|----------|-------------|
| `created` | No | Files created during execution |
| `modified` | No | Files modified during execution |
| `deleted` | No | Files deleted during execution |
| `unplanned` | No | Files touched but not implied by any subtask |

At least one list should be non-empty unless execution blocked before edits.

## `subtasks`

Mirror checklist order. Do not copy the full subtask list; reference line index and summarize the result.

| Field | Required | Description |
|-------|----------|-------------|
| `index` | Yes | 1-based line number in the checklist (after frontmatter) |
| `text` | Yes | The one-sentence subtask text |
| `status` | Yes | `done`, `partial`, `skipped`, or `blocked` |
| `checked` | Yes | `true` if marked `- [x]` in the markdown file |
| `paths` | No | Paths touched by this subtask |
| `note` | No | One-line outcome, blocker, or user decision |

## `verify`

Include one entry per command run by `/execute-plan`.

| Field | Required | Description |
|-------|----------|-------------|
| `command` | Yes | Shell command |
| `exit` | Yes | Exit code |
| `passed` | Yes | `true` or `false` |
| `tail` | No | Last few relevant output lines for failures only |

## Optional detail blocks

### `deviations`

Use when execution differed from the subtask list.

| Field | Required | Description |
|-------|----------|-------------|
| `kind` | Yes | `user_approved`, `list_gap`, `blocked`, or `out_of_scope` |
| `subtask_index` | No | Related subtask index |
| `note` | Yes | What changed and why |

### `hotspots`

Use for focused review attention, not for full explanations.

| Field | Required | Description |
|-------|----------|-------------|
| `path` | Yes | File or area to review closely |
| `reason` | Yes | Short reason (e.g. `semantic-tokens`, `i18n-strings`, `new-deps-risk`) |

### `review_scope`

Use when review should be partial or focused.

| Field | Required | Description |
|-------|----------|-------------|
| `mode` | No | `full` (default), `triage`, or `verify_only` |
| `focus_paths` | No | Paths to prioritize |
| `skip_subtasks` | No | Subtask indices that are not reviewable yet |

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: execute-plan
  subtasks: current-task/subtasks/hero-section.md
  spec: current-task/specs/hero-section.yaml
  context: current-task/current-task-context.yaml
  status: complete
  constraints: [no-commit, no-new-deps]

paths:
  created: [src/components/Hero/Hero.tsx]
  modified: [app/page.tsx]
  deleted: []
  unplanned: []

subtasks:
  - index: 1
    text: Implement a Hero component with headline, subcopy, and a primary CTA using semantic Tailwind tokens only.
    status: done
    checked: true
    paths: [src/components/Hero/Hero.tsx]
    note: Hero with headline, subcopy, CTA, and semantic tokens.
  - index: 2
    text: Replace the home page hero with the new Hero component above the fold.
    status: done
    checked: true
    paths: [app/page.tsx]
    note: Replaced landing banner with Hero.
  - index: 6
    text: Run npm test for Hero and home page test suites.
    status: done
    checked: true
    note: All test commands passed.

verify:
  - command: npm run lint
    exit: 0
    passed: true
  - command: npm test -- Hero
    exit: 0
    passed: true

deviations: []
open_questions: []

hotspots:
  - path: src/components/Hero/Hero.tsx
    reason: semantic-tokens

review_scope:
  mode: full
```

## Writing good execution files

**Do:**

- Write the file even when execution blocks or stops partially.
- Keep notes short; reference subtask index instead of repeating full sentences.
- Record all changed paths, including unplanned paths.
- Include failure output only when a command fails, and keep it short.

**Don't:**

- Include diffs, transcripts, or long logs.
- Mark review approval here; that belongs only in `current-task/reviews/<slug>.yaml`.
- Hide scope changes. If an unplanned path changed, list it under `paths.unplanned`.
