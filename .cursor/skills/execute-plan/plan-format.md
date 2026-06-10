# Plan format

Plans drive `/execute-plan`. **YAML only** — both `/plan-maker` output and `/execute-plan` input use this schema.

Store plans in the worktree under `current-task/plans/` (e.g. `current-task/plans/hero-section.yaml`) or paste inline YAML in the command.

All agent YAML artifacts for the active task live under `current-task/`:

```
current-task/
  current-task-context.yaml # workflow context from /current-task-update
  specs/              # spec-maker output
  plans/              # plan-maker output
  executions/         # execute-plan handoff output
  reviews/            # review-execution output
  review-validations/ # review-triage output
  review-inputs/      # review guidance input for review-execution
  next-steps/         # follow-up specs consumable by plan-maker
  merges/             # merge-task output
  commits/            # commit-task output
  pushes/             # push-task output
```

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes for `/plan-maker` output | Machine-friendly metadata used for scope and traceability checks |
| `title` | No | Short name for the task |
| `constraints` | Yes for `/plan-maker` output | Rules for the agent (default `no-commit`, `no-new-deps`) |
| `steps` | Yes | Ordered list of work units |

### `meta` block

When `/plan-maker` writes the plan, include every field below. `/execute-plan` treats `worktree` as a cross-check against the worktree path passed in the command.

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug (e.g. `hero-section`) |
| `generated_by` | Yes | Agent that wrote the plan (`plan-maker`) |
| `task` | Yes | Original task description from the user |
| `spec` | Yes when a spec exists | Path to the spec file plan-maker read (e.g. `current-task/specs/hero-section.yaml`) |
| `context` | No | Path to task context (e.g. `current-task/current-task-context.yaml`) |

## Step fields

Each step:

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Recommended | Stable kebab-case label (`step-1`, `add-hero`) |
| `action` | Yes | `create`, `modify`, `delete`, `run`, or `verify` |
| `path` | For file actions | File path relative to the worktree root |
| `do` | For file actions; optional for `verify` | Exact instructions — be specific, not aspirational |
| `commands` | For shell `run` and `verify` steps | Shell commands to run from worktree root |
| `covers` | No | Spec requirement IDs this step satisfies (e.g. `[hero-cta]`) |

### Required fields by action

| Action | Required fields | Notes |
|--------|-----------------|-------|
| `create` | `id`, `action`, `path`, `do` | Create the file at `path` under the worktree root |
| `modify` | `id`, `action`, `path`, `do` | Edit only the named file unless the plan has another step |
| `delete` | `id`, `action`, `path`, `do` | Delete only the named file |
| `run` | `id`, `action`, `commands` or `do` | Use `commands` for shell work; use `do` for an explicit ask/decision step |
| `verify` | `id`, `action`, `commands` | `do` may briefly state what the checks prove |

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: plan-maker
  task: "redesign hero with headline, subcopy, CTA using semantic Tailwind tokens"
  spec: current-task/specs/hero-section.yaml
  context: current-task/current-task-context.yaml

title: Hero section redesign
constraints:
  - no-commit
  - no-new-deps

steps:
  - id: create-hero
    action: create
    path: src/components/Hero/Hero.tsx
    covers: [hero-headline, hero-subcopy, hero-cta, hero-tokens]
    do: >
      Create a Hero component with headline, subcopy, and CTA button.
      Follow LandingBanner patterns for layout. Use semantic Tailwind tokens
      (bg-primary, text-primary) — no raw palette classes.

  - id: wire-hero
    action: modify
    path: app/page.tsx
    covers: [hero-page-wiring]
    do: Replace the existing hero markup with <Hero /> from src/components/Hero.

  - id: verify
    action: verify
    commands:
      - npm run lint
      - npm test -- Hero
    do: Lint and Hero tests pass.
```

## Writing good steps

**Do:**

- Name exact files and symbols
- Describe the expected outcome, not just the motivation
- Add `covers` when mapping a step to spec `requirements[].id` is useful for review
- Group verification in final `verify` steps
- List constraints when the agent should avoid commits, new deps, or scope creep

**Don't:**

- "Improve performance" without measurable targets
- "Refactor as needed" without file list
- Reference paths outside the worktree
- Rely on the agent to choose architecture unless the plan includes a decision step

## Ambiguity → ask

The execute-plan agent should stop and ask when a step:

- Uses vague verbs (`clean up`, `modernize`, `fix issues`)
- Conflicts with another step
- Requires a design choice not specified in the plan
- References missing files without a prior `create` step
- References a path that escapes the worktree root
- Has `meta.worktree` that does not match the worktree path passed to `/execute-plan`
- Omits a final `verify` step and the user has not approved skipping verification

Add an explicit **decision** step when the plan author expects a fork:

```yaml
- id: decision-cta
  action: run
  do: >
    Ask the user whether the CTA should link to /contact or /demo.
    Do not implement until answered.
```

## Authoring for plan-maker

When `/plan-maker` writes a plan:

1. **Read spec first** — load `current-task/specs/<slug>.yaml` from `/spec-maker`; stop if `open_questions` is non-empty.
2. **Explore second** — grep/glob/search the worktree for relevant files, tests, and patterns; respect spec `scope.out`.
3. **5–12 steps typical** — split large features into create → wire → test → verify; cover every spec requirement.
4. **Carry constraints** — copy spec `constraints` into the plan (default `no-commit`, `no-new-deps`).
5. **Include `meta`** — set `worktree`, `generated_by: plan-maker`, `task`, `spec: current-task/specs/<slug>.yaml`, and `context: current-task/current-task-context.yaml` when present.
6. **Map coverage** — add `covers` to steps when spec requirement IDs are available.
7. **Verify last** — end with a `verify` step mapping spec `acceptance` to CONTRIBUTING.md checks.
8. **Write to `current-task/plans/<slug>.yaml`** — slug matches the worktree folder name.

The plan-maker agent must not edit application code — only the YAML plan file.

Spec schema (plan-maker input): [spec-format.md](../spec-maker/spec-format.md).
