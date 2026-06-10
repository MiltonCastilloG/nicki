# Review format

Reviews are the output of `/review-execution`. **YAML only** — output reviews have exactly two top-level keys: `approved` and `content`.

Store reviews in the worktree under `current-task/reviews/` (e.g. `current-task/reviews/hero-section.yaml`) or consume inline YAML from the subagent report.

All agent YAML artifacts for the active task live under `current-task/`:

```
current-task/
  current-task-context.yaml              # workflow context from /current-task-update
  specs/<slug>.yaml                    # from /spec-maker
  plans/<slug>.yaml                    # from /plan-maker
  executions/<slug>.yaml               # from /execute-plan
  reviews/<slug>.yaml                  # from /review-execution
  review-validations/rN-validation.yaml # from /review-triage
  review-inputs/rN-review.yaml         # optional guidance input for /review-execution
  next-steps/*.yaml                    # follow-up specs consumable by /plan-maker
  merges/<slug>.yaml                   # from /merge-task
  commits/<slug>.yaml                  # from /commit-task
  pushes/<slug>.yaml                   # from /push-task
```

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `approved` | Yes | `true` if the implementation passes review; `false` if blocking issues remain |
| `content` | Yes | Pass summary (`approved: true`) or actionable issue list (`approved: false`) |

**Output reviews have no other top-level keys.** Do not add `meta`, `title`, or routing hints to `current-task/reviews/<slug>.yaml` — downstream consumers read only `approved` and `content`.

## Optional review-execution input

When `/review-triage` discards an invalid review, it may write a guidance file under `current-task/review-inputs/rN-review.yaml`. That input uses review YAML plus one extra key:

| Field | Required | Description |
|-------|----------|-------------|
| `approved` | Yes | Usually `false`; explains that previous review should not be treated as approved |
| `content` | Yes | Why the previous review should be rerun |
| `important-considerations` | Yes | Scope or correctness notes `/review-execution` must keep in mind |

`important-considerations` is input-only. `/review-execution` must use it while reviewing, but must still write output with only `approved` and `content`.

```yaml
approved: false
content: |
  Previous review was discarded because it treated footer redesign as a hero-task blocker.
important-considerations:
  - Do not block the hero task on footer redesign; footer is outside spec.scope.in.
  - Still report build, lint, test, safety, or correctness issues.
```

## `approved`

- `true` — all spec requirements met, plan steps satisfied, verify commands passed, no scope creep, no blocking convention violations.
- `false` — one or more blocking issues; see `content` for details.

## `content`

Use a YAML block scalar (`|`). Write in plain language with consistent prefixes so issues are easy to scan and act on.

### When `approved: true`

Brief pass summary (2–5 lines). Mention requirements coverage, verify results, and scope.

```yaml
approved: true
content: |
  All spec requirements met (hero-headline, hero-subcopy, hero-cta, hero-tokens).
  Plan steps create-hero, wire-hero completed as described.
  Verify: npm run lint and npm test -- Hero passed.
  No files changed outside plan scope.
```

### When `approved: false`

List **blocking issues** only. Each bullet should be actionable — reference IDs, paths, and failures.

| Prefix | Use for |
|--------|---------|
| `[req-<id>]` | Spec requirement not met |
| `[plan:<step-id>]` | Plan step not done or done incorrectly |
| `[scope]` | Change outside spec `scope.out` or plan paths |
| `[verify]` | Lint, test, build, or other check failure |
| `[convention]` | CONTRIBUTING rule violation (tokens, i18n, deps) |

```yaml
approved: false
content: |
  [req-hero-cta] Hero component has no CTA button — only headline and subcopy rendered.
  [plan:wire-hero] app/page.tsx still imports LandingBanner; Hero not wired in.
  [verify] npm run lint failed: src/components/Hero/Hero.tsx — unused import 'Link'.
  [scope] src/components/Footer/Footer.tsx modified — outside spec scope.out.
```

## Writing good `content`

**Do:**

- Reference spec requirement IDs and plan step IDs when applicable
- Name exact file paths for code and scope issues
- Paste or summarize verify command failures with enough context to reproduce
- Keep bullets specific and testable

**Don't:**

- Suggest fixes or re-plan steps — only report what failed review
- Include non-blocking nits unless the user asked for strict review
- Add keys beyond `approved` and `content`
- Mention downstream agents or routing logic

## Ambiguity → ask

The review-execution agent should ask the user before writing the review when:

- Spec or plan is missing and partial review is insufficient
- A requirement is subjective and pass/fail is unclear
- Verify commands cannot run (missing deps, wrong branch base)
- Git history makes change discovery unreliable

Resolve or get user direction, then write `current-task/reviews/<slug>.yaml`.
