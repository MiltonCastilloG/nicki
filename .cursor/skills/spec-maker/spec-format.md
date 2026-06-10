# Spec format

Specs drive `/subtask-maker`. **YAML only** — both `/spec-maker` output and `/subtask-maker` input use this schema.

Store specs in the worktree under `current-task/specs/` (e.g. `current-task/specs/hero-section.yaml`) or paste inline YAML in the command.

All agent YAML artifacts for the active task live under `current-task/`:

```
current-task/
  current-task-context.yaml # workflow context from /current-task-update
  specs/              # spec-maker output
  subtasks/           # subtask-maker output
  executions/         # execute-plan handoff output
  reviews/            # review-execution output
  review-validations/ # review-triage output
  review-inputs/      # review guidance input for review-execution
  next-steps/         # follow-up specs consumable by subtask-maker
  merges/             # merge-task output
  commits/            # commit-task output
  pushes/             # push-task output
```

Specs define **what** to build (requirements, scope, acceptance). They do **not** name implementation subtasks or file paths — that is subtask-maker's job.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `meta` | Yes | Machine-friendly metadata |
| `title` | Yes | Short task name |
| `type` | Yes | Task type: `feature`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf` |
| `summary` | Yes | One-paragraph description of the goal |
| `requirements` | Yes | Ordered list of what must be delivered |
| `scope` | No | `in` and `out` lists bounding the work |
| `constraints` | No | Rules for downstream agents (e.g. `no-commit`, `no-new-deps`) |
| `acceptance` | Yes | Testable criteria for done |
| `assumptions` | No | Defaults spec-maker applied when the task was silent |
| `open_questions` | No | Unresolved decisions — subtask-maker must ask before writing subtasks |

## `meta` block

| Field | Required | Description |
|-------|----------|-------------|
| `worktree` | Yes | Worktree slug (e.g. `hero-section`) |
| `generated_by` | Yes | `spec-maker` for original task specs; `review-triage` for next-step specs |
| `task` | Yes | Original task description from the user — prefer the Gherkin `task.story` from context when orchestrated by Nicki |
| `branch` | No | Git branch (e.g. `feature/hero-section`) |
| `context` | No | Path to task context (e.g. `current-task/current-task-context.yaml`) |
| `source_review` | No | Review path when generated from review triage |
| `source_validation` | No | Validation path when generated from review triage |
| `source_finding` | No | Original review finding that triggered a next-step spec |

## Requirement fields

Each item in `requirements`:

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Stable label (`hero-cta`, `fix-link-href`) |
| `description` | Yes | Specific, testable requirement — not aspirational |

## YAML example

```yaml
meta:
  worktree: hero-section
  generated_by: spec-maker
  task: "redesign hero section with headline, subcopy, and CTA"
  branch: feature/hero-section
  context: current-task/current-task-context.yaml

title: Hero section redesign
type: feature

summary: >
  Replace the current home page hero with a new section featuring a prominent
  headline, supporting subcopy, and a primary call-to-action button.

requirements:
  - id: hero-headline
    description: Display a prominent headline in the hero area above the fold.
  - id: hero-subcopy
    description: Display supporting subcopy below the headline.
  - id: hero-cta
    description: Include a primary CTA button using existing link/button patterns.
  - id: hero-tokens
    description: Style using semantic Tailwind tokens only — no raw palette classes.

scope:
  in:
    - Home page hero area
    - New or refactored Hero component
  out:
    - Header, footer, and other pages
    - New npm dependencies
    - i18n changes unless required by the hero copy

constraints:
  - no-commit
  - no-new-deps

acceptance:
  - Home page hero shows headline, subcopy, and CTA
  - Styling uses semantic Tailwind tokens (bg-primary, text-primary, etc.)
  - npm run lint passes
  - npm test passes for affected components

assumptions:
  - Reuse layout patterns from the existing LandingBanner component
  - Hero copy is static English for this task

open_questions: []
```

## Writing good specs

**Do:**

- Make every requirement testable and specific
- Bound scope with explicit `in` / `out` lists
- List acceptance criteria the executor can verify
- Record assumptions when the user's task was implicit
- Put unresolved design forks in `open_questions` — do not guess

**Don't:**

- Name file paths or implementation subtasks (subtask-maker does that)
- Use vague verbs without measurable outcomes (`improve`, `modernize`, `clean up`)
- Duplicate subtask-level or execution detail (commands, step order, create/modify actions)
- Leave silent on constraints — default to `no-commit` and `no-new-deps` unless the task requires otherwise

## Ambiguity → ask

The spec-maker agent should ask the user before writing the spec when:

- The task has no measurable outcome
- Scope is unclear and cannot be reasonably bounded
- Multiple valid interpretations exist (e.g. which page, which component)
- A design fork affects requirements (CTA destination, copy tone, etc.)

Resolve questions first, then write `current-task/specs/<slug>.yaml` with `open_questions: []`.

## Authoring for spec-maker

When `/spec-maker` writes a spec:

1. **Analyze the task** — parse user intent; ask if vague before writing.
2. **Light context only** — read CONTRIBUTING.md and optionally skim project layout (app/, src/) to bound scope realistically. Do not explore file-by-file.
3. **Default constraints** — include `no-commit` and `no-new-deps` unless the task requires otherwise.
4. **Include `meta`** — set `worktree`, `generated_by: spec-maker`, `task`, `context: current-task/current-task-context.yaml` when present, and `branch` when known.
5. **Write to `current-task/specs/<slug>.yaml`** — slug matches the worktree folder name.
6. **Hand off to subtask-maker** — report the exact next command:

   ```
   /subtask-maker worktrees/<slug> @current-task/specs/<slug>.yaml
   ```

The spec-maker agent must not edit application code or write subtask files — only the YAML spec file.
